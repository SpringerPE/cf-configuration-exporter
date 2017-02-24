import unittest
import json
from exporter.exporter import ResourceParser, Organization, ResourceParser
from test.test_helper import OrgUsersAPIMock, SpaceAPIMock, OrganizationAPIMock, QuotaAPIMock, SecGroupAPIMock, PrivateDomainAPIMock

organization = {
  'guid': '1c0e6074-777f-450e-9abc-c42f39d9b75b',
  'name': 'name-1716'
}
mock_organization = OrganizationAPIMock()
organization_definition = ResourceParser.extract_entities(
                                            json.loads(mock_organization.get_cf_response(organization))
                                        )

users = [
{
    'userName': "user@example.com",
    'email': 'user@example.com',
    'guid': "uaa-id-1",
    'space_guid': "fc898723-2192-42d9-9567-c0b2e03a3169"
},
{
    'userName': "user2@example.com",
    'email': 'user2@example.com',
    'guid': "uaa-id-2",
    'space_guid': "fc898723-2192-42d9-9567-c0b2e03a3169"
}
]

mock_user = OrgUsersAPIMock()
users_definition = json.loads(mock_user.get_cf_response(users))
auditors_definition = json.loads(mock_user.get_cf_response(users))
managers_definition = json.loads(mock_user.get_cf_response(users))
billing_managers_definition = json.loads(mock_user.get_cf_response(users))
billing_managers_definition = json.loads(mock_user.get_cf_response(users))


space1 = {
    'guid': '5489e195-c42b-4e61-bf30-323c331ecc01',
    'name': 'space-1'
}

mock_space = SpaceAPIMock()
spaces_definition = json.loads(mock_space.get_cf_org_spaces_response(space1))

quota = {
  'guid': '80f3e539-a8c0-4c43-9c72-649df53da8cb',
  'name': 'default'
}

mock_quota = QuotaAPIMock()
quota_definition = json.loads(mock_quota.get_cf_response(quota))

mock_sec_groups = SecGroupAPIMock()
space_sec_groups_response = json.loads(mock_sec_groups.get_cf_space_sg_response({}))

domain = {
    'guid': ""
}

mock_private_domains = PrivateDomainAPIMock()
private_domains_definition = json.loads(mock_private_domains.get_cf_org_private_domains_response({}))

class MockResourceFetcher:

    def __init__(self, client):
        self._client = client
        self.entities = {}

    def register_entity(self, url, response):
        self.entities[url] = response

    def get_entities(self, resource_url):
        return ResourceParser.extract_entities(self.entities[resource_url])

class TestOrgDefinition(unittest.TestCase):

  def test_org_can_load_its_config(self):
    fetcher = MockResourceFetcher(None)

    fetcher.register_entity("/v2/quota_definitions/769e777f-92b6-4ba0-9e48-5f77e6293670", quota_definition)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/spaces", spaces_definition)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/users", users_definition)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/managers", managers_definition)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/billing_managers", billing_managers_definition)
    fetcher.register_entity("/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/security_groups", space_sec_groups_response)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/auditors", users_definition)
    fetcher.register_entity("/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/private_domains", private_domains_definition)

    org = Organization(organization_definition, fetcher=fetcher)
    org.load()
    o = org.asdict()
    self.assertEqual(o['spaces'][0]['name'], 'space-1')
    self.assertEqual(o['users'][0], {'name': 'user@example.com'})
    self.assertEqual(o['managers'][0], {'name': 'user@example.com'})
    self.assertEqual(o['billing_managers'][0], {'name': 'user@example.com'})

