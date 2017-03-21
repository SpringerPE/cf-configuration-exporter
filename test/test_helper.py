from jinja2 import Environment, PackageLoader, select_autoescape
from exporter.exporter import ResourceParser
import json

env = Environment(
    loader=PackageLoader('test', 'templates'),
)


class MockResourceFetcher:

    def __init__(self, client):
        self._client = client
        self.responses = {}

    def register_response(self, url, response):
        self.responses[url] = response

    def get_entities(self, resource_url):
        body = self.responses[resource_url]
        return ResourceParser.extract_entities(body)

class BasicMock:

  def get_response(self, resource):
    return self.template.render(resource=resource)


class UserUAAAPIMock(BasicMock):

  def __init__(self):
    self.template = env.get_template('user_uaa.j2')

class UserAPIMock(BasicMock):

  def __init__(self):
    self.template = env.get_template('user_cf.j2')


class OrgUsersAPIMock(BasicMock):

  def __init__(self):
    self.template = env.get_template('org_users.j2')

class FeatureFlagsAPIMock(BasicMock):

  def __init__(self):
    self.template = env.get_template('feature_flags.j2')

class SpaceAPIMock(BasicMock):

  def __init__(self, config, fetcher):
    self.template = env.get_template('space.j2')
    self._fetcher = fetcher
    self._config = config
    self._security_groups = list()

  @property
  def config(self):
      return self._config
  
  def get_guid(self):
    return self._config['guid']

  def dump(self):
      self.dump_sec_groups()
      space = json.loads(self.get_response(self._config))
      self._fetcher.register_response("/v2/spaces/%s" % self.get_guid(), space)
      return space

  def add_sec_group(self, sec_group):
    self._security_groups.append(sec_group.config)

  def dump_sec_groups(self):
    mock_sec_groups = SecGroupsAPIMock()
    sec_groups_definition = json.loads(mock_sec_groups.get_response(self._security_groups))
    self._fetcher.register_response("/v2/spaces/%s/security_groups" % self.get_guid(), 
        sec_groups_definition)


class OrganizationAPIMock(BasicMock):

  def __init__(self, config, fetcher):
    self.template = env.get_template('organization.j2')
    self._fetcher = fetcher
    self._config = config
    self._spaces = list()
    self._domains = list()

  @property
  def spaces(self):
      return self._spaces

  def get_guid(self):
    return self._config['guid']

  def dump(self):
      self.dump_spaces()
      self.dump_domains()

      org = json.loads(self.get_response(self._config))
      self._fetcher.register_response("/v2/organizations/%s" % self.get_guid(), org)
      return org

  def dump_spaces(self):
    mock_spaces = OrgSpacesAPIMock()
    spaces_definition = json.loads(mock_spaces.get_response(self._spaces))
    self._fetcher.register_response("/v2/organizations/%s/spaces" % self.get_guid(), 
                                      spaces_definition)

  def dump_domains(self):
    mock_domains = PrivateDomainsAPIMock()
    domains_definition = json.loads(mock_domains.get_response(self._domains))

    self._fetcher.register_response("/v2/organizations/%s/private_domains" % self.get_guid(), 
                                      domains_definition)

  def add_space(self, space):
    self._spaces.append(space.config)

  def add_domain(self, domain):
    self._domains.append(domain.config)

  def add_private_domains(self, private_domains):
    mock_private_domains = PrivateDomainsAPIMock()
    pd_definition = json.loads(mock_private_domains.get_response(private_domains))
    self._fetcher.register_response("/v2/organizations/%s/private_domains" % self.get_guid(), pd_definition)

  def _add_users(self, users, kind):

    mock_users = OrgUsersAPIMock()
    users_definition = json.loads(mock_users.get_response(users))
    self._fetcher.register_response("/v2/organizations/%s/%s" % (self.get_guid(), kind), 
                                          users_definition
                                      )

  def add_auditors(self, auditors):
    self._add_users(auditors, "auditors")

  def add_managers(self, managers):
    self._add_users(managers, "managers")

  def add_billing_managers(self, billing_managers):
    self._add_users(billing_managers, "billing_managers")

  def add_users(self, users):
    self._add_users(users, "users")


class QuotaAPIMock(BasicMock):

  def __init__(self, config, fetcher):
    self.template = env.get_template('quota.j2')
    self._config = config
    self._fetcher = fetcher

  def get_guid(self):
    return self._config['guid']

  def dump(self):
    quota = json.loads(self.get_response(self._config))
    self._fetcher.register_response("/v2/quota_definitions/%s" % self.get_guid(), quota)
    return quota


class SecGroupAPIMock(BasicMock):

  def __init__(self, config, fetcher):
    self.template = env.get_template('security_group.j2')
    self._config = config
    self._fetcher = fetcher

  @property
  def config(self):
      return self._config

class PrivateDomainAPIMock(BasicMock):

  def __init__(self, config, fetcher):
    self.template = env.get_template('domain.j2')
    self._config = config
    self._fetcher = fetcher

  @property
  def config(self):
      return self._config


class SecGroupsAPIMock:

  def __init__(self):
    self.template = env.get_template('security_groups.j2')

  def get_response(self, resource):
    return self.template.render(resource=resource)


class OrgSpacesAPIMock:

  def __init__(self):
    self.template = env.get_template('org_spaces.j2')

  def get_response(self, resource):
    return self.template.render(resource=resource)

class PrivateDomainsAPIMock:

  def __init__(self):
    self.template = env.get_template('private_domains.j2')

  def get_response(self, resource):
    return self.template.render(resource=resource)

