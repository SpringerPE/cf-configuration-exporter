from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException
import collections
import yaml
import pyaml
import os

class GUIDHelper:

    def __init__(self, config):
        self._config = config

    def get_guids(self):
        guids = [resource['metadata']['guid'] for resource in self._config[0]['resources']]
        return guid

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

class Quota:

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
        self._prop_dict = collections.OrderedDict()
        self._config = config
        self._quotas = []

    def load(self):
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        return self._prop_dict

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)

class Space:

    properties = ["name", "allow_ssh", "developers", "managers", "auditors", "security_groups"]
    
    def __init__(self, config, fetcher):
        self._prop_dict = collections.OrderedDict()
        self._config = config
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
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        return self._prop_dict

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)

class Organization:

    properties = ["name", "spaces", "users", "managers", "billing_managers", "auditors"]

    def __init__(self, config, fetcher):
        self._prop_dict = collections.OrderedDict()
        self._config = config
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
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        return self._prop_dict

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)

class SecurityGroup:

    properties = ["name", "context", "rules"]

    def __init__(self, config):
        self._prop_dict = collections.OrderedDict()
        self._config = config
        self._rules = []

    def load(self):
        rules = self._config['rules']
        for rule in rules:
            self.add_rule(rule)
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[str(prop)] = value
            except AttributeError:
                pass

    def asdict(self):
        return self._prop_dict

    @property
    def rules(self):
        return self._rules

    def add_rule(self, rule):
        new_rule = SecurityRule(rule)
        new_rule.load()
        self._rules.append(new_rule.asdict())

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)

class SecurityRule:

    properties = ["name", "protocol", "destination", "ports", "logs", "code", "type"]

    def __init__(self, config):
        self._config = config
        self._prop_dict = collections.OrderedDict()

    def asdict(self):
        return self._prop_dict

    def load(self):
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError:
                pass

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("%s not found" % name)


class User:

    properties = ["name", "active", "email", "given_name", "family_name",
                  "default_organization", "default_space", "origin", "external_id"]

    def __init__(self, user_cf, user_uaa):
        self._user_cf = user_cf
        self._user_uaa = user_uaa
        self._prop_dict = collections.OrderedDict()

    def asdict(self):
        return self._prop_dict

    @property
    def given_name(self):
        response = None
        name = self.__getattr__('name')
        if 'givenName' in name:
            response = name['givenName']
        return response

    @property
    def family_name(self):
        response = None
        name = self.__getattr__('name')
        if 'familyName' in name:
            response = name['familyName']
        return response

    @property
    def name(self):
        return getattr(self, 'userName')

    def load(self):
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as atbe:
                pass

    def __getattr__(self, name):
        if name in self._user_cf:
            return self._user_cf[name]
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


    def get_variable_group(self):
        response = self.client.request("GET", "/v2/config/environment_variable_groups/running")
        return response

    def get_user_default_org(self, guid):
        pass

    def get_user_default_space(self, guid):
        response = self.client.request("GET", "/v2/spaces")
        pass

    def get_users_list(self):
        response = self.client.request("GET", "/v2/users")
        resources = response[0]['resources']
        user_ids = [user['metadata']['guid'] for user in resources]
        return user_ids

    def get_user_details(self, guid):
        user = None
        user_dict = collections.OrderedDict()
        try:
            user = self.client.uaa.user_get(user_id)
            user_dict['name'] = user['userName']
            user_dict['email'] = [email["value"] for email in user['emails'] if email['primary']]
            user_dict['familyName'] = user['name']['familyName']
            user_dict['givenName'] = user['name']['givenName']
            user_dict['active'] = user['active']
        except UAAException as uaaexp:
            print(uaaexp)

        return user_dict

    def transform_in_valid_yaml(self, obj):
        yaml_string = pyaml.dump(obj)
        print(yaml_string)
