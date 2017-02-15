from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException
import collections
import yaml
import pyaml
import os

class ResourceFetcher:

    def __init__(self, client):
        self._client = client

    def get_resources(self, resource_url):
        response = self._client.request("GET", resource_url)
        return [obj for obj in response[0]['resources']]

    def get_entities(self, resource_url):
        response = self._client.request("GET", resource_url)
        return [obj['entity'] for obj in response[0]['resources']]

    def get_metadata(self, resource_url):
        response = self._client.request("GET", resource_url)
        return [obj['metadata'] for obj in response[0]['resources']]

class BaseEntity:

    def __init__(self, config):
        self._prop_dict = collections.OrderedDict()
        self._config = config

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)

    def load(self):
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        return self._prop_dict

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

    def __init__(self, config):
        super(Quota, self).__init__(config)

class Space(BaseEntity):

    properties = [
                            "name", 
                            "allow_ssh", 
                            "developers", 
                            "managers", 
                            "auditors", 
                            "security_groups"
                        ]
    
    def __init__(self, config, fetcher):
        super(Space, self).__init__(config)
        self._fetcher = fetcher
        self._security_groups = []

    @property
    def security_groups(self):
        return self._security_groups

    def load_security_groups(self):
        url = self._config["security_groups_url"]
        groups = self._fetcher.get_entities(url)
        for group in groups:
            self._security_groups.append(group['name'])

    def load_users(self):
        user_types = ["developers", "managers", "auditors"]
        for user_type in user_types:
            url = "%s_url" % user_type
            if not url in self._config:
                continue 
            setattr(self, user_type, [])
            users = self._fetcher.get_entities(self._config[url])
            for user in users:
                user_list =  getattr(self, user_type)
                if 'username' in user:
                    user_list.append(user['username'])

    def load(self):
        self.load_users()
        self.load_security_groups()
        BaseEntity.load(self)


class Organization(BaseEntity):

    properties = [
                            "name", 
                            "spaces", 
                            "users", 
                            "managers", 
                            "billing_managers", 
                            "auditors"
                        ]

    def __init__(self, config, fetcher):
        super(Organization, self).__init__(config)
        self._fetcher = fetcher
        self._spaces = []

    @property
    def spaces(self):
        return self._spaces
    
    def load_spaces(self):
        url = self._config["spaces_url"]
        spaces = self._fetcher.get_entities(url)
        for space in spaces:
            new_space = Space(space, self._fetcher)
            new_space.load()
            self._spaces.append(new_space.asdict())
    
    def load_users(self):
        user_types = ["users", "managers", "billing_managers", "auditors"]
        for user_type in user_types:
            url = "%s_url" % user_type
            if not url in self._config:
                continue 
            setattr(self, user_type, [])
            users = self._fetcher.get_entities(self._config[url])
            for user in users:
                user_list =  getattr(self, user_type)
                if 'username' in user:
                    user_list.append(user['username'])

    def load(self):
        self.load_spaces()
        self.load_users()
        BaseEntity.load(self)

class SecurityGroup(BaseEntity):

    properties = [
                            "name", 
                            "context", 
                            "rules"
                        ]

    def __init__(self, config):
        super(SecurityGroup, self).__init__(config)
        self._rules = []

    @property
    def rules(self):
        return self._rules

    def load(self):
        self.load_rules()
        BaseEntity.load(self)

    def load_rules(self):
        rules = self._config['rules']
        for rule in rules:
            new_rule = SecurityRule(rule)
            new_rule.load()
            self._rules.append(new_rule.asdict())

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

    def __init__(self, config):
        super(SecurityRule, self).__init__(config)


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

    def __init__(self, config, user_uaa):
        super(User, self).__init__(config)
        self._user_uaa = user_uaa

    @property
    def given_name(self):
        name = self.__getattr__('name')
        if 'givenName' in name:
            return name['givenName']
        raise AttributeError("given_name not found")

    @property
    def family_name(self):
        name = self.__getattr__('name')
        if 'familyName' in name:
            return name['familyName']
        raise AttributeError("family_name not found")

    @property
    def name(self):
        return getattr(self, 'userName')

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        elif name in self._user_uaa:
            return self._user_uaa[name]
        raise AttributeError("%s not found" % name)


class Exporter:

    def __init__(self, api_url=""):
        api_url = os.environ.get("EXPORTER_API_URL")
        self.client = CF(api_url)
        self.fetcher = ResourceFetcher(self.client)
        self.manifest = collections.OrderedDict()

    def login(self, admin_user='admin', admin_password=''):
        admin_user = os.environ.get("EXPORTER_ADMIN_USER")
        admin_password = os.environ.get("EXPORTER_ADMIN_PASSWORD")
        self.client.login(admin_user, admin_password)

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
        return []

    def add_staging_environment_variables(self):
        return []

    def add_running_environment_variables(self):
        return []

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
                user_uaa = self.client.uaa.user_get(user['metadata']['guid'])
            except UAAException as uaaexp:
                continue
            user_cf = user['entity']
            u = User(user_cf, user_uaa)
            u.load()
            user_list.append(u.asdict())
        return user_list

    def add_orgs(self):
        response = self.fetcher.get_entities("/v2/organizations")
        org_list = []
        for org in response:
            o = Organization(org, self.fetcher)
            o.load()
            org_list.append(o.asdict())
        return org_list

