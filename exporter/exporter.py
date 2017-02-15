from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException
import collections
import yaml
import pyaml

class LastUpdatedOrderedDict(collections.OrderedDict):
    'Store items in the order the keys were last added'
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        collections.OrderedDict.__setitem__(self, key, value)

class Space:

    def __init__(self):
        pass

class SecurityGroup:

    properties = ["name", "context", "rules"]

    def __init__(self, group):
        self._prop_dict = LastUpdatedOrderedDict()
        self._group = group
        self._rules = []

    def load(self):
        rules = self._group['rules']
        for rule in rules:
            self.add_rule(rule)
        for prop in self.properties:
            value = getattr(self, prop)
            if value:
                self._prop_dict[str(prop)] = value

    @property
    def sec_group(self):
        return self._prop_dict

    @property
    def rules(self):
        return self._rules

    def add_rule(self, rule):
        new_rule = SecurityRule(rule)
        new_rule.load()
        self._rules.append(new_rule.sec_rule)

    def __getattr__(self, name):
        response = None
        if name in self._group:
            response = self._group[name]
        return response

class SecurityRule:

    properties = ["name", "protocol", "destination", "ports", "logs", "code", "type"]

    def __init__(self, rule):
        self._rule = rule
        self._prop_dict = LastUpdatedOrderedDict()

    @property
    def sec_rule(self):
        return self._prop_dict

    def load(self):
        for prop in self.properties:
            value = getattr(self, prop)
            if value:
                self._prop_dict[prop] = value

    def __getattr__(self, name):
        response = None
        if name in self._rule:
            response = self._rule[name]
        return response

class User:

    properties = ["name", "active", "email", "given_name", "family_name",
                  "default_organization", "default_space", "origin", "external_id"]

    def __init__(self, user_cf, user_uaa):
        self._user_cf = user_cf
        self._user_uaa = user_uaa
        self._prop_dict = LastUpdatedOrderedDict()

    @property
    def user(self):
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
        self.client = CF(api_url)

    def login(self, admin_user='admin', admin_password=''):
        self.client.login(admin_user, admin_password)

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
