import unittest
import json
from exporter.exporter import ResourceParser, Organization
from test.test_helper import (
                        OrgUsersAPIMock, OrgSpacesAPIMock, 
                        OrganizationAPIMock, QuotaAPIMock, 
                        SecGroupsAPIMock, PrivateDomainsAPIMock,
                        MockResourceFetcher
            )

organization = {
  'guid': '1c0e6074-777f-450e-9abc-c42f39d9b75b',
  'name': 'name-1716'
}

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

spaces = [
{
    'guid': 'fc898723-2192-42d9-9567-c0b2e03a3169',
    'name': 'space-1',
    'org_guid': '1c0e6074-777f-450e-9abc-c42f39d9b75b'
}
]

quota = {
  'guid': '80f3e539-a8c0-4c43-9c72-649df53da8cb',
  'name': 'default'
}

sgs =[
    {
    'guid': '38f5bb47-e7c2-4931-8046-ea491757332e',
    'name': 'secg-1'
    }
]

domains = [{
    'guid': "a3987aba-fa92-11e6-964b-8fa64aff3eda",
    'name': "test.domain",
    'org_guid': '1c0e6074-777f-450e-9abc-c42f39d9b75b'
}]

class TestOrgDefinition(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    fetcher = MockResourceFetcher(None)
    cls.fetcher = fetcher

    mock_organization = OrganizationAPIMock()
    cls.organization_definition = ResourceParser.extract_entities(
                                            json.loads(
                                            mock_organization.get_cf_response(organization)
                                          )
                                      )
    org_guid = organization['guid']

    mock_user = OrgUsersAPIMock()
    users_definition =json.loads(mock_user.get_cf_response(users))
    auditors_definition = json.loads(mock_user.get_cf_response(users))
    managers_definition = json.loads(mock_user.get_cf_response(users))
    billing_managers_definition = json.loads(mock_user.get_cf_response(users))


    fetcher.register_entity("/v2/organizations/%s/auditors" % org_guid, auditors_definition)
    fetcher.register_entity("/v2/organizations/%s/users" % org_guid, users_definition)
    fetcher.register_entity("/v2/organizations/%s/managers" % org_guid, managers_definition)
    fetcher.register_entity("/v2/organizations/%s/billing_managers" % org_guid, billing_managers_definition)

    mock_quota = QuotaAPIMock()
    quota_definition = json.loads(mock_quota.get_cf_response(quota))

    fetcher.register_entity("/v2/quota_definitions/769e777f-92b6-4ba0-9e48-5f77e6293670", quota_definition)

    mock_space = OrgSpacesAPIMock()
    spaces_definition = json.loads(mock_space.get_cf_response(spaces))


    fetcher.register_entity("/v2/organizations/%s/spaces" % org_guid, spaces_definition)

    mock_sec_groups = SecGroupsAPIMock()
    space_sec_groups_response = json.loads(mock_sec_groups.get_cf_response(sgs))

    fetcher.register_entity("/v2/spaces/fc898723-2192-42d9-9567-c0b2e03a3169/security_groups", space_sec_groups_response)
    fetcher.register_entity("/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc02/security_groups", space_sec_groups_response)

    mock_private_domains = PrivateDomainsAPIMock()
    private_domains_definition = json.loads(mock_private_domains.get_cf_response(domains))

    fetcher.register_entity("/v2/organizations/%s/private_domains" % org_guid, private_domains_definition)

  def test_org_can_load_its_config(self):

    org = Organization(self.organization_definition, fetcher=self.fetcher)
    org.load()
    o = org.asdict()
    self.assertEqual(o['spaces'][0]['name'], 'space-1')
    self.assertEqual(o['users'][0], {'name': 'user@example.com'})
    self.assertEqual(o['managers'][0], {'name': 'user@example.com'})
    self.assertEqual(o['billing_managers'][0], {'name': 'user@example.com'})

