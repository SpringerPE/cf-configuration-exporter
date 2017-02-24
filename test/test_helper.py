from jinja2 import Environment, PackageLoader, select_autoescape
from exporter.exporter import ResourceParser
import json

env = Environment(
    loader=PackageLoader('test', 'templates'),
)


class MockResourceFetcher:

    def __init__(self, client):
        self._client = client
        self.entities = {}

    def register_entity(self, url, response):
        entities = ResourceParser.extract_entities(response)
        self.entities[url] = entities

    def get_entities(self, resource_url):
        return self.entities[resource_url]


class UserAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('user_cf.j2')
    self.uaa_template = env.get_template('user_uaa.j2')

  def get_cf_response(self, user):
    return self.cf_template.render(user=user)

  def get_uaa_response(self, user):
    return self.uaa_template.render(user=user)

class OrgUsersAPIMock:

  def __init__(self):
    self.org_users_template = env.get_template('org_users.j2')

  def get_cf_response(self, users):
    return self.org_users_template.render(users=users)


class SpaceAPIMock:

  def __init__(self, config, fetcher):
    self.cf_template = env.get_template('space.j2')
    self._fetcher = fetcher
    self._config = config
    self._security_groups = list()

  @property
  def config(self):
      return self._config
  
  def get_cf_response(self, space):
    return self.cf_template.render(space=space)

  def get_guid(self):
    return self._config['guid']

  def dump(self):

      self.dump_sec_groups()

      space = json.loads(self.get_cf_response(self._config))
      self._fetcher.register_entity("/v2/spaces/%s" % self.get_guid(), 
            space
      )
      return ResourceParser.extract_entities(space)

  def add_sec_group(self, sec_group):
    self._security_groups.append(sec_group.config)

  def dump_sec_groups(self):
    mock_sec_groups = SecGroupsAPIMock(self._security_groups, self._fetcher)
    sec_groups_definition = json.loads(mock_sec_groups.get_cf_response(self._security_groups))
    self._fetcher.register_entity("/v2/spaces/%s/security_groups" % self.get_guid(), 
        sec_groups_definition)



class OrgSpacesAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('org_spaces.j2')

  def get_cf_response(self, spaces):
    return self.cf_template.render(spaces=spaces)


class OrganizationAPIMock:

  def __init__(self, config, fetcher):
    self.cf_template = env.get_template('organization.j2')
    self._fetcher = fetcher
    self._config = config
    self._spaces = list()
    self._domains = list()

  @property
  def spaces(self):
      return self._spaces

  def get_cf_response(self, organization):
    return self.cf_template.render(organization=organization)

  def get_guid(self):
    return self._config['guid']

  def dump(self):
      self.dump_domains()

      self.dump_spaces()

      org = json.loads(self.get_cf_response(self._config))
      self._fetcher.register_entity("/v2/organizations/%s" % self.get_guid(), 
            org
      )
      return ResourceParser.extract_entities(org)

  def dump_spaces(self):
    mock_spaces = OrgSpacesAPIMock()
    spaces_definition = json.loads(mock_spaces.get_cf_response(self._spaces))
    self._fetcher.register_entity("/v2/organizations/%s/spaces" % self.get_guid(), 
                                      spaces_definition)

  def dump_domains(self):
    mock_domains = PrivateDomainsAPIMock()
    domains_definition = json.loads(mock_domains.get_cf_response(self._domains))

    self._fetcher.register_entity("/v2/organizations/%s/private_domains" % self.get_guid(), 
                                      domains_definition)

  def add_space(self, space):
    self._spaces.append(space.config)

  def add_domain(self, domain):
    self._domains.append(domain.config)

  def add_private_domains(self, private_domains):
    mock_private_domains = PrivateDomainsAPIMock()
    pd_definition = json.loads(mock_private_domains.get_cf_response(private_domains))
    self._fetcher.register_entity("/v2/organizations/%s/private_domains" % self.get_guid(), pd_definition)

  def _add_users(self, users, kind):

    mock_users = OrgUsersAPIMock()
    users_definition = json.loads(mock_users.get_cf_response(users))
    self._fetcher.register_entity("/v2/organizations/%s/%s" % (self.get_guid(), kind), 
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


class QuotaAPIMock:

  def __init__(self, config, fetcher):
    self.cf_template = env.get_template('quota.j2')
    self._config = config
    self._fetcher = fetcher

  def get_cf_response(self, quota):
    return self.cf_template.render(quota=quota)

  def get_guid(self):
    return self._config['guid']

  def dump(self):

    quota_definition = json.loads(self.get_cf_response(self._config))

    self._fetcher.register_entity("/v2/quota_definitions/%s" % self.get_guid(), quota_definition)
    return ResourceParser.extract_entities(quota_definition)


class SecGroupsAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('security_groups.j2')

  @property
  def config(self):
      return self._config

  def get_cf_response(self, sgs):
    return self.cf_template.render(sgs=sgs)


class SecGroupsAPIMock:

  def __init__(self, config, fetcher):
    self.cf_template = env.get_template('security_groups.j2')
    self._config = config
    self._fetcher = fetcher

  @property
  def config(self):
      return self._config

  def get_cf_response(self, sgs):
    return self.cf_template.render(sgs=sgs)


class PrivateDomainAPIMock:

  def __init__(self, config, fetcher):
    self.cf_template = env.get_template('private_domains.j2')
    self._config = config
    self._fetcher = fetcher

  def config(self):
      return self._config

  def get_cf_response(self, domains):
    return self.cf_template.render(domains=domains)


class PrivateDomainsAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('private_domains.j2')

  def get_cf_response(self, domains):
    return self.cf_template.render(domains=domains)

