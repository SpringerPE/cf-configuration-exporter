import unittest
import json
from exporter.exporter import ResourceParser, Organization
from test.test_helper import (
                        OrgUsersAPIMock, OrgSpacesAPIMock, 
                        OrganizationAPIMock, QuotaAPIMock, 
                        SecGroupAPIMock, PrivateDomainsAPIMock,
                        PrivateDomainAPIMock,
                        MockResourceFetcher, SpaceAPIMock
            )

organization = {
  'guid': '1c0e6074-777f-450e-9abc-c42f39d9b75b',
  'name': 'name-1716',
  'quota_guid': '80f3e539-a8c0-4c43-9c72-649df53da8cb'
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

    mock_organization = OrganizationAPIMock(organization, fetcher)

    mock_organization.add_users(users)
    mock_organization.add_managers(users)
    mock_organization.add_auditors(users)
    mock_organization.add_billing_managers(users)

    mock_space1 =  SpaceAPIMock(spaces[0], fetcher)

    mock_organization.add_space(mock_space1)

    mock_quota = QuotaAPIMock(quota, fetcher)
    mock_quota.dump()

    mock_sec_group1 = SecGroupAPIMock(sgs[0], fetcher)
    mock_space1.add_sec_group(mock_sec_group1)

    mock_domain = PrivateDomainAPIMock(domains[0], fetcher)
    mock_organization.add_domain(mock_domain)
  
    mock_space1.dump()
    cls.organization_definition = ResourceParser.extract_entities(mock_organization.dump())

  def test_org_can_load_its_config(self):

    org = Organization(self.organization_definition, fetcher=self.fetcher)
    org.load()
    o = org.asdict()
    print(o)
    self.assertEqual(o['spaces'][0]['name'], 'space-1')
    self.assertEqual(o['users'][0], {'name': 'user@example.com'})
    self.assertEqual(o['managers'][0], {'name': 'user@example.com'})
    self.assertEqual(o['billing_managers'][0], {'name': 'user@example.com'})

