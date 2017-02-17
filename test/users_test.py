import unittest
import json
from exporter.exporter import User

user_definition = json.loads('''
{
    "admin": false,
    "active": false,
    "default_space_guid": "fc898723-2192-42d9-9567-c0b2e03a3169",
    "default_space_url": "/v2/spaces/fc898723-2192-42d9-9567-c0b2e03a3169",
    "spaces_url": "/v2/users/uaa-id-317/spaces",
    "organizations_url": "/v2/users/uaa-id-317/organizations",
    "managed_organizations_url": "/v2/users/uaa-id-317/managed_organizations",
    "billing_managed_organizations_url": "/v2/users/uaa-id-317/billing_managed_organizations",
    "audited_organizations_url": "/v2/users/uaa-id-317/audited_organizations",
    "managed_spaces_url": "/v2/users/uaa-id-317/managed_spaces",
    "audited_spaces_url": "/v2/users/uaa-id-317/audited_spaces"
}
''')

uaa_user_definition = json.loads('''
{
  "id" : "2dd424e5-f2ed-4bb7-b374-c347513915ca",
  "externalId" : "test-user",
  "meta" : {
    "version" : 0,
    "created" : "2017-02-02T19:05:45.685Z",
    "lastModified" : "2017-02-02T19:05:45.685Z"
  },
  "userName" : "Z5qRBj@test.org",
  "name" : {
    "familyName" : "family name",
    "givenName" : "given name"
  },
  "emails" : [ {
    "value" : "Z5qRBj@test.org",
    "primary" : false
  } ],
  "groups" : [ {
    "value" : "73339582-437f-4e46-86d4-977c31617c44",
    "display" : "cloud_controller.read",
    "type" : "DIRECT"
  }, {
    "value" : "41e0c28b-37a0-4be5-801a-0e1df301ace2",
    "display" : "cloud_controller_service_permissions.read",
    "type" : "DIRECT"
  } ],
  "approvals" : [ {
    "userId" : "2dd424e5-f2ed-4bb7-b374-c347513915ca",
    "clientId" : "client id",
    "scope" : "scim.read",
    "status" : "APPROVED",
    "lastUpdatedAt" : "2017-02-02T19:05:45.693Z",
    "expiresAt" : "2017-02-02T19:05:55.693Z"
  } ],
  "phoneNumbers" : [ {
    "value" : "5555555555"
  } ],
  "active" : true,
  "verified" : true,
  "origin" : "uaa",
  "zoneId" : "uaa",
  "passwordLastModified" : "2017-02-02T19:05:45.000Z",
  "previousLogonTime" : 1486062345696,
  "lastLogonTime" : 1486062345697,
  "schemas" : [ "urn:scim:schemas:core:1.0" ]
}
''')

default_space_response = json.loads('''
{ 
    "name": "name-2064",
    "organization_guid": "6e1ca5aa-55f1-4110-a97f-1f3473e771b9",
    "space_quota_definition_guid": null,
    "allow_ssh": true,
    "organization_url": "/v2/organizations/6e1ca5aa-55f1-4110-a97f-1f3473e771b9",
    "developers_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/developers",
    "managers_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/managers",
    "auditors_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/auditors",
    "apps_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/apps",
    "routes_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/routes",
    "domains_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/domains",
    "service_instances_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/service_instances",
    "app_events_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/app_events",
    "events_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/events",
    "security_groups_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/security_groups",
    "staging_security_groups_url": "/v2/spaces/bc8d3381-390d-4bd7-8c71-25309900a2e3/staging_security_groups"
}
''')


default_organization_response = json.loads('''
{
    "name": "name-1716",
    "billing_enabled": false,
    "quota_definition_guid": "769e777f-92b6-4ba0-9e48-5f77e6293670",
    "status": "active",
    "quota_definition_url": "/v2/quota_definitions/769e777f-92b6-4ba0-9e48-5f77e6293670",
    "spaces_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/spaces",
    "domains_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/domains",
    "private_domains_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/private_domains",
    "users_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/users",
    "managers_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/managers",
    "billing_managers_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/billing_managers",
    "auditors_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/auditors",
    "app_events_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/app_events",
    "space_quota_definitions_url": "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/space_quota_definitions"
}
''')

class MockResourceFetcher:
    def __init__(self, client):
        self._client = client

    def get_entities(self, resource_url):
        if resource_url == "/v2/spaces/fc898723-2192-42d9-9567-c0b2e03a3169":
            return default_space_response
        elif resource_url == "/v2/organizations/6e1ca5aa-55f1-4110-a97f-1f3473e771b9":
            return default_organization_response

class TestUserDefinition(unittest.TestCase):

  def test_quota_can_load_its_config(self):
    fetcher = MockResourceFetcher(None)
    user = User(user_definition, uaa_user_definition, fetcher=fetcher)
    user.load()
    u = user.asdict()
    self.assertEqual(u["name"], "Z5qRBj@test.org")

    self.assertEqual(u["email"], "Z5qRBj@test.org")

    self.assertEqual(u["given_name"], "given name")
    self.assertEqual(u["family_name"], "family name")

    self.assertEqual(u["default_space"], "name-2064")
    self.assertEqual(u["default_organization"], "name-1716")