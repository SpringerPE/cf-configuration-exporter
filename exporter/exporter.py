from cfconfigurator.cf import CFException
from cfconfigurator.uaa import UAAException
from .exceptions import ExporterException 

import re
import sys
import logging
import collections
import functools

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceParser(object):

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


class Memoize(object):

    def __init__(self, make_request):
        self.make_request = make_request
        self.memo = {}

    def __call__(self, o_self, resource_url):
        if resource_url not in self.memo:
            response = self.make_request(o_self, resource_url)

            if response[1] == 200:
                self.memo[resource_url] = response
            else:
                return response

        return self.memo[resource_url]

    def __get__(self, instance, owner):
        from functools import partial
        return partial(self.__call__, instance)

class ResourceFetcher(object):
    """
    @brief      Help fetching resources from Cloudfoundry
    """

    def __init__(self, client):
        self._client = client


    def get_raw(self, resource_url):
        response = self.response(resource_url)
        return response[0]

    def get_resources(self, resource_url):
        """
        @brief      Get the `resources` configuration from the response body
        """
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_resources(body)

    def get_entities(self, resource_url):
        """
        @brief      Get the `entities` configuration from the response body
        """
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_entities(body)

    def get_metadata(self, resource_url):
        """
        @brief      Get the `metadata` configuration from the response body
        """
        response = self.response(resource_url)
        body = response[0]
        return ResourceParser.extract_metadata(body)

    @Memoize
    def response(self, resource_url):
        try:
            return self._client.request("GET", resource_url)
        except CFException as cfe:
            logger.err(str(cfe))
            raise

class BaseResource(object):
    """
    @brief      Base Class for a generic CF Resource
    """

    def __init__(self, *config_dicts, **kwargs):
        """
        @brief      Constructs the Resource object.
        
        @param      self          The object
        @param      config_dicts  The configuration dicts
        @param      fetcher       The fetcher
        """
        self._prop_dict = collections.OrderedDict()
        self._fetcher  = kwargs.get('fetcher', None)
        self._config = config_dicts

    def lookup(self, name):
        """
        @brief         looks up the name variable

        Performs a look up for a variable named `name` against
        the list of dictionaries passed as argument to the constructor
        of this class
        
        @param      self  The object
        @param      name  The name of the variable to look-up
        """
        for config in self._config:
            if name in config:
                return config[name] 
        raise AttributeError("%s not found" % name)

    def __getattr__(self, name):
        """
        Try to find the variable in the list of dictionaries passed to this
        instance contructor begore raising a AttributeError
        """
        return self.lookup(name)

    def load(self):
        """
        Parse the configuration and load the variables into the
        self._prop_dict instance dictionary
        """
        for prop in self.properties:
            try:
                value = getattr(self, prop)
                self._prop_dict[prop] = value
            except AttributeError as ate:
                pass

    def asdict(self):
        """
        @return     self._prop_dict instance dictionary containing a map representing
        the configuration parameters for this resource
        """
        return self._prop_dict

class FeatureFlag(BaseResource):
    """
    @brief:     Describe a feature flag.

    https://docs.cloudfoundry.org/adminguide/listing-feature-flags.html
    """
    properties = [  "name", 
                            "value"
                        ]

    @property
    def value(self):
        return self.__getattr__("enabled")

    def __init__(self, *config_dicts):
        super(FeatureFlag, self).__init__(*config_dicts)

class Vars(BaseResource):
    """
    @brief:     Describe environment variables groups.

    This resource in represented as a dictionary of
    `name`: `value` pairs where name is the name of the variable
    and value its value
    """
    properties = []

    def __init__(self, *config_dicts, **kwargs):
        super(Vars, self).__init__(*config_dicts)
        self.exclude_vars = kwargs.get('exclude_vars', ())


    def var_excluded(self, name):
        if name.lower().startswith(self.exclude_vars):
            return True
        return False

    def asdict(self):
        #Differetly from other resources we do not need
        #to extract the properties here. This resource consists
        #on just a dictionary of key: value entries
        return self._config[0]

    def aslist(self):
        return [{'name': name, 'value': value} for name, value in self._config[0].items() if not self.var_excluded(name)]

    def load(self):
        #Nothing to load. The response body is already in the correct format
        pass

class Quota(BaseResource):
    """
    @brief:     Describe a quota configuration

    Docs: https://docs.cloudfoundry.org/adminguide/quota-plans.html
     """

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

class Space(BaseResource):
    """
    @brief:     Describe a space configuration

    Docs: https://docs.cloudfoundry.org/concepts/roles.html#spaces
    """
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
    
    def __init__(self, *config_dicts,  **kwargs):
        super(Space, self).__init__(*config_dicts, **kwargs)
        self._security_groups = []


    @property
    def security_groups(self):
        return self._security_groups

    def load_security_groups(self):
        """
        @brief      extract and parse the security groups
        """
        url = self.lookup("security_groups_url")
        groups = self._fetcher.get_entities(url)
        if groups is None:
            return

        group_names = [group['name'] for group in groups if group['running_default'] is False]
        #at this point the group_names contain all the running groups in addition
        #to the groups assigned to this space.
        #That's why we need to remove the duplicates
        group_names = list(set(group_names))

        for name in group_names:
            self._security_groups.append({'name': name})

    def load_users(self):
        """
        @brief      extract and parse the users for this space
        """
        for user_type in self.user_types:
            url_string = "%s_url" % user_type
            try:
                url = self.lookup(url_string)
                users = self._fetcher.get_entities(url)
            except AttributeError as ate:
                logger.err(str(ate))
                continue
            user_list = []
            for user in users:
                if 'username' in user:
                    user_list.append({'name': user['username']})
            if len(user_list) > 0:
                setattr(self, user_type, user_list)

    def load(self):
        self.load_users()
        self.load_security_groups()
        BaseResource.load(self)


class Organization(BaseResource):
    """
    @brief      Describe a CF organization
    """
    user_types = [
                            "users", 
                            "managers", 
                            "billing_managers", 
                            "auditors"
                        ]

    properties = [
                            "name", 
                            "quota",
                            "domains_private",
                            "spaces", 
                            "users", 
                            "managers", 
                            "billing_managers", 
                            "auditors"
                        ]

    def __init__(self, *config_dicts, **kwargs):
        super(Organization, self).__init__(*config_dicts, **kwargs)
        self._spaces = []

    @property
    def spaces(self):
        return self._spaces

    @property
    def quota(self):
        return self._quota

    @property
    def domains_private(self):
        return self._domains_private

    def load_private_domains(self):
        """
        @brief  Loads private domains list for this org
        """
        url = self.lookup("private_domains_url")
        p_domains = self._fetcher.get_entities(url)
        domains = []
        for domain in p_domains:
            if 'name' in domain:
                domains.append({'name': domain['name']})
        self._domains_private = domains

    def load_quota_definitions(self):
        """
        @brief      Loads quota definitions for this org.
        """
        url = self.lookup("quota_definition_url")
        quota = self._fetcher.get_entities(url)
        if 'name' in quota:
            self._quota = quota['name']

    def load_spaces(self):
        """
        @brief      Loads all the spaces for this org.
        """
        url = self.lookup("spaces_url")
        spaces = self._fetcher.get_entities(url)
        for space in spaces:
            new_space = Space(space, fetcher=self._fetcher)
            new_space.load()
            self._spaces.append(new_space.asdict())
    
    def load_users(self):
        """
        @brief      Loads all the users for this org.
        """
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
                    user_list.append({'name': user['username']})
            if len(user_list) > 0:
                setattr(self, user_type, user_list)


    def load(self):
        self.load_private_domains()
        self.load_quota_definitions()
        self.load_spaces()
        self.load_users()
        BaseResource.load(self)

class SecurityGroup(BaseResource):
    """
    @brief      Describe a global security group
    """

    properties = [
                            "name", 
                            "running_default",
                            "staging_default", 
                            "rules"
                        ]

    def __init__(self, *config_dicts, **kwargs):
        super(SecurityGroup, self).__init__(*config_dicts, **kwargs)
        self._rules = []

    @property
    def rules(self):
        return self._rules 

    def generate_rule_name(self):
        num = 0
        while True:
            yield "Unnamed rule %i" % num
            num += 1

    def load(self):
        self.load_rules()
        BaseResource.load(self)

    def load_rules(self):
        rules = self.lookup('rules')
        name_generator = self.generate_rule_name()
        for index, rule in enumerate(rules):
            new_rule = SecurityRule(rule)
            new_rule.name_generator = name_generator
            if new_rule.has_name():
                new_rule.load()
                self._rules.append(new_rule.asdict())

class SecurityRule(BaseResource):
    """
    @brief:     Describe a security rule.
    """

    properties = [
                            "name", 
                            "protocol", 
                            "destination", 
                            "ports", 
                            "logs", 
                            "code", 
                            "type"
                        ]


    def __init__(self, *config_dicts, **kwargs):
        super(SecurityRule, self).__init__(*config_dicts, **kwargs)
        self._name_generator = None

    def has_name(self):
        try:
            self.lookup("description")
        except AttributeError:
            return False
        return True
    
    @property
    def name(self):
        return self.lookup("description")

    @property
    def name_generator(self):
        return self._name_generator

    @name_generator.setter
    def name_generator(self, value):
        self._name_generator = value


class User(BaseResource):
    """
    @brief      Describe a CF user.
    """

    properties = [
                            "name",
                            "password",
                            "active", 
                            "email", 
                            "given_name", 
                            "family_name",
                            "default_organization", 
                            "default_space", 
                            "origin", 
                            "external_id"
                        ]

    def __init__(self, *config_dicts, **kwargs):
        cf_response = kwargs.get('cf_response', None)
        fetcher  = kwargs.get('fetcher', None)

        if cf_response is None:
            raise ExporterException("Please provide the CF configuration for this user resource")
        if fetcher is None:
            raise ExporterException("Please provide a valid resource fetcher")

        super(User, self).__init__(*config_dicts, **kwargs)
        self._cf_response = cf_response

    def lookup_cf_response(self, name):
        config = self._cf_response
        if name in config:
                return config[name] 
        raise AttributeError("%s not found" % name)

    @property
    def external_id(self):
        return self.lookup("externalId")

    @property
    def given_name(self):
        name = self.lookup('name')
        if 'givenName' in name:
            return name['givenName']
        return None

    @property
    def family_name(self):
        name = self.lookup('name')
        if 'familyName' in name:
            return name['familyName']
        return None

    @property
    def password(self):
        return None
    
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
        BaseResource.load(self)

    def load_default_space_and_org(self):
        """
        @brief      Loads a default space and organization.
        """
        try:
            space_url = self.lookup_cf_response("default_space_url")
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

    def __init__(self, client, exclude_vars=""):
        self._client = client
        self._uaa_client = client.uaa
        self.fetcher = ResourceFetcher(client)
        self.manifest = collections.OrderedDict()
        exprs = re.split(';|,', exclude_vars)
        self.exclude_vars = tuple(expr.strip().lower() for expr in exprs if len(expr) > 0)

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
        response = self.fetcher.get_raw("/v2/config/environment_variable_groups/staging")
        
        v = Vars(response, exclude_vars=self.exclude_vars)
        return v.aslist()

    def add_running_environment_variables(self):
        response = self.fetcher.get_raw("/v2/config/environment_variable_groups/running")
        
        v = Vars(response, exclude_vars=self.exclude_vars)
        return v.aslist()

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
            u = User(user_uaa, cf_response=user_cf, fetcher=self.fetcher)
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

