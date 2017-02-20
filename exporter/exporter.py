from cfconfigurator.cf import CF, CFException
from cfconfigurator.uaa import UAA, UAAException
import collections
import yaml
import pyaml
import os
import logging

logger = logging.getLogger(__name__)

class ResourceParser:

    @classmethod
    def extract_entities(cls, body):
        if 'resources' in body:
            return [obj['entity'] for obj in body['resources']]
        else:
            return body['entity']

    @classmethod
    def extract_resources(cls, body):
        if 'resources' in body:
            return [obj for obj in body['resources']]

    @classmethod
    def extract_metadata(cls, body):
        return [obj['metadata'] for obj in body['resources']]


class ResourceFetcher:

    def __init__(self, client):
        self._client = client

    def get_raw(self, resource_url):
        response = self.response(resource_url)
        return response[0]

    def get_resources(self, resource_url):
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_resources(body)

    def get_entities(self, resource_url):
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_entities(body)

    def get_metadata(self, resource_url):
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_metadata(body)

    def response(self, resource_url):
        try:
            return self._client.request("GET", resource_url)
        except CFException as cfe:
            logger.err(str(cfe))
            raise

class BaseEntity:

    def __init__(self, *config_dicts, fetcher=None):
        self._prop_dict = collections.OrderedDict()
        self._fetcher  = fetcher
        self._config = config_dicts

    def lookup(self, name):
        for config in self._config:
            if name in config:
                return config[name] 
        raise AttributeError("%s not found" % name)

    def __getattr__(self, name):
        return self.lookup(name)

    def load(self):
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        return self._prop_dict

class FeatureFlag(BaseEntity):

    properties = [  "name", 
                            "value"
                        ]

    @property
    def value(self):
        return self.__getattr__("enabled")

    def __init__(self, *config_dicts):
        super(FeatureFlag, self).__init__(*config_dicts)

class Vars(BaseEntity):

    properties = []

    def __init__(self, *config_dicts):
        super(Vars, self).__init__(*config_dicts)

    def load(self):
        for config in self._config:
            for key, value in config.items():
                self.properties[key] = value

class Quota(BaseEntity):

    properties = [  "name", 
                            "total_services", 
                            "total_routes", 
                            "memory_limit", 
                            "non_basic_services_allowed",
                            "instance_memory_limit", 
                            "total_service_keys",
                            "total_reserved_route_ports", 
                            "total_private_domains",
                            "app_instance_limit"
                        ]

    def __init__(self, *config_dicts):
        super(Quota, self).__init__(*config_dicts)

class Space(BaseEntity):

    user_types = [
                            "developers", 
                            "managers", 
                            "auditors"
                        ]

    properties = [
                            "name", 
                            "allow_ssh", 
                            "developers", 
                            "managers", 
                            "auditors", 
                            "security_groups"
                        ]
    
    def __init__(self, *config_dicts, fetcher=None):
        super(Space, self).__init__(*config_dicts, fetcher=fetcher)
        self._security_groups = []

    @property
    def security_groups(self):
        return self._security_groups

    def load_security_groups(self):
        url = self.lookup("security_groups_url")
        groups = self._fetcher.get_entities(url)
        if groups is None:
            return
        for group in groups:
            if 'name' in group:
                self._security_groups.append(group['name'])

    def load_users(self):
        for user_type in self.user_types:
            url = "%s_url" % user_type
            try:
                users = self.lookup(url)
            except AttributeError as ate:
                continue
            user_list = []
            for user in users:
                if 'username' in user:
                    user_list.append(user['username'])
            if len(user_list) > 0:
                setattr(self, user_type, user_list)

    def load(self):
        self.load_users()
        self.load_security_groups()
        BaseEntity.load(self)


class Organization(BaseEntity):

    user_types = [
                            "users", 
                            "managers", 
                            "billing_managers", 
                            "auditors"
                        ]

    properties = [
                            "name", 
                            "quota",
                            "spaces", 
                            "users", 
                            "managers", 
                            "billing_managers", 
                            "auditors"
                        ]

    def __init__(self, *config_dicts, fetcher=None):
        super(Organization, self).__init__(*config_dicts, fetcher=fetcher)
        self._spaces = []

    @property
    def spaces(self):
        return self._spaces

    @property
    def quota(self):
        return self._quota

    def load_quota_definitions(self):
        url = self.lookup("quota_definition_url")
        quota = self._fetcher.get_entities(url)
        if 'name' in quota:
            self._quota = quota['name']

    def load_spaces(self):
        url = self.lookup("spaces_url")
        spaces = self._fetcher.get_entities(url)
        for space in spaces:
            new_space = Space(space, fetcher=self._fetcher)
            new_space.load()
            self._spaces.append(new_space.asdict())
    
    def load_users(self):
        for user_type in self.user_types:
            url = "%s_url" % user_type
            try:
                self.lookup(url)
            except AttributeError:
                continue 
            users = self._fetcher.get_entities(self.lookup(url))
            user_list = []
            for user in users:
                if 'username' in user:
                    user_list.append(user['username'])
            if len(user_list) > 0:
                setattr(self, user_type, user_list)


    def load(self):
        self.load_quota_definitions()
        self.load_spaces()
        self.load_users()
        BaseEntity.load(self)

class SecurityGroup(BaseEntity):

    properties = [
                            "name", 
                            "context", 
                            "rules"
                        ]

    def __init__(self, *config_dicts, fetcher=None):
        super(SecurityGroup, self).__init__(*config_dicts, fetcher=fetcher)
        self._rules = []

    @property
    def rules(self):
        return self._rules

    def load(self):
        self.load_rules()
        BaseEntity.load(self)

    def load_rules(self):
        rules = self.lookup('rules')
        for rule in rules:
            new_rule = SecurityRule(rule)
            new_rule.load()
            self._rules.append(new_rule.asdict())

#TODO add name to security rules
class SecurityRule(BaseEntity):

    properties = [
                            "name", 
                            "protocol", 
                            "destination", 
                            "ports", 
                            "logs", 
                            "code", 
                            "type"
                        ]

    def __init__(self, *config_dicts, fetcher=None):
        super(SecurityRule, self).__init__(*config_dicts, fetcher=fetcher)


class User(BaseEntity):

    properties = [
                            "name", 
                            "active", 
                            "email", 
                            "given_name", 
                            "family_name",
                            "default_organization", 
                            "default_space", 
                            "origin", 
                            "external_id"
                        ]

    def __init__(self, *config_dicts, fetcher=None):
        super(User, self).__init__(*config_dicts, fetcher=fetcher)

    @property
    def given_name(self):
        name = self.lookup('name')
        if 'givenName' in name:
            return name['givenName']
        raise AttributeError("given_name not found")

    @property
    def family_name(self):
        name = self.lookup('name')
        if 'familyName' in name:
            return name['familyName']
        raise AttributeError("family_name not found")

    @property
    def email(self):
        emails = self.lookup('emails')
        if len(emails) > 0:
            if 'value' in emails[0]:
                return emails[0]['value']
        raise AttributeError("email not found")
    
    @property
    def name(self):
        return self.lookup('userName')

    @property
    def default_space(self):
        return self._default_space

    @property
    def default_organization(self):
        return self._default_organization

    def load(self):
        self.load_default_space_and_org()
        BaseEntity.load(self)

    def load_default_space_and_org(self):
        try:
            space_url = self.lookup("default_space_url")
        except AttributeError:
            return
        space = self._fetcher.get_entities(space_url)
        if 'organization_url' in space:
            org_url = space['organization_url']
            org = self._fetcher.get_entities(org_url)

            if ('name' in space) and ('name' in org):
                self._default_organization = org['name']
                self._default_space = space['name']




class Exporter:

    def __init__(self, client):
        self._client = client
        self._uaa_client = client.uaa
        self.fetcher = ResourceFetcher(client)
        self.manifest = collections.OrderedDict()

    def generate_manifest(self):
        self.manifest["cf_feature_flags"] = self.add_feature_flags()
        self.manifest["cf_staging_environment_variables"] = self.add_staging_environment_variables()
        self.manifest["cf_running_environment_variables"] = self.add_running_environment_variables()
        self.manifest["cf_shared_domains"] = self.add_shared_domains()
        self.manifest["cf_security_groups"] = self.add_security_groups()
        self.manifest["cf_quotas"] = self.add_quotas()
        self.manifest["cf_users"] = self.add_users()
        self.manifest["cf_orgs"] = self.add_orgs()

    def add_feature_flags(self):
        response = self.fetcher.get_raw("/v2/config/feature_flags")
        flag_list = []
        for flag in response:
            f = FeatureFlag(flag)
            f.load()
            flag_list.append(f.asdict())
        return flag_list

    def add_staging_environment_variables(self):
        var_list = []
        response = self.fetcher.get_raw("/v2/config/environment_variable_groups/running")
        
        v = Vars(response)
        return v.asdict()

    def add_running_environment_variables(self):
        var_list = []
        response = self.fetcher.get_raw("/v2/config/environment_variable_groups/staging")
        
        v = Vars(response)
        return v.asdict()

    def add_shared_domains(self):
        response = self.fetcher.get_entities("/v2/shared_domains")
        domain_list = []
        for domain in response:
            domain_list.append({'name': domain['name']})
        return domain_list

    def add_security_groups(self):
            response = self.fetcher.get_entities("/v2/security_groups")
            group_list = []
            for group in response:
                g = SecurityGroup(group)
                g.load()
                group_list.append(g.asdict())
            return group_list

    def add_quotas(self):
        response = self.fetcher.get_entities("/v2/quota_definitions")
        quota_list = []
        for quota in response:
            q = Quota(quota)
            q.load()
            quota_list.append(q.asdict())
        return quota_list

    def add_users(self):
        response = self.fetcher.get_resources("/v2/users")
        user_list = []
        for user in response:
            try:
                user_uaa = self._uaa_client.user_get(user['metadata']['guid'])
            except UAAException as uaaexp:
                continue
            user_cf = user['entity']
            u = User(user_cf, user_uaa, fetcher=self.fetcher)
            u.load()
            user_list.append(u.asdict())
        return user_list

    def add_orgs(self):
        response = self.fetcher.get_entities("/v2/organizations")
        org_list = []
        for org in response:
            o = Organization(org, fetcher=self.fetcher)
            o.load()
            org_list.append(o.asdict())
        return org_list

