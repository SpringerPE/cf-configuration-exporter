import unittest
import json
from exporter.exporter import Organization

organization_definition = json.loads('''
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

users_definition = json.loads('''
[{
        "admin": false,
        "active": false,
        "default_space_guid": null,
        "username": "user@example.com",
        "spaces_url": "/v2/users/uaa-id-231/spaces",
        "organizations_url": "/v2/users/uaa-id-231/organizations",
        "managed_organizations_url": "/v2/users/uaa-id-231/managed_organizations",
        "billing_managed_organizations_url": "/v2/users/uaa-id-231/billing_managed_organizations",
        "audited_organizations_url": "/v2/users/uaa-id-231/audited_organizations",
        "managed_spaces_url": "/v2/users/uaa-id-231/managed_spaces",
        "audited_spaces_url": "/v2/users/uaa-id-231/audited_spaces"
}]
''')

auditors_definition = json.loads('''
[{
        "admin": false,
        "active": false,
        "default_space_guid": null,
        "username": "auditor@example.com",
        "spaces_url": "/v2/users/uaa-id-231/spaces",
        "organizations_url": "/v2/users/uaa-id-231/organizations",
        "managed_organizations_url": "/v2/users/uaa-id-231/managed_organizations",
        "billing_managed_organizations_url": "/v2/users/uaa-id-231/billing_managed_organizations",
        "audited_organizations_url": "/v2/users/uaa-id-231/audited_organizations",
        "managed_spaces_url": "/v2/users/uaa-id-231/managed_spaces",
        "audited_spaces_url": "/v2/users/uaa-id-231/audited_spaces"
}]
''')

managers_definition = json.loads('''
[{
        "admin": false,
        "active": false,
        "default_space_guid": null,
        "username": "manager@example.com",
        "spaces_url": "/v2/users/uaa-id-231/spaces",
        "organizations_url": "/v2/users/uaa-id-231/organizations",
        "managed_organizations_url": "/v2/users/uaa-id-231/managed_organizations",
        "billing_managed_organizations_url": "/v2/users/uaa-id-231/billing_managed_organizations",
        "audited_organizations_url": "/v2/users/uaa-id-231/audited_organizations",
        "managed_spaces_url": "/v2/users/uaa-id-231/managed_spaces",
        "audited_spaces_url": "/v2/users/uaa-id-231/audited_spaces"
}]
''')

billing_managers_definition = json.loads('''
[{
        "admin": false,
        "active": false,
        "default_space_guid": null,
        "username": "billing_manager@example.com",
        "spaces_url": "/v2/users/uaa-id-231/spaces",
        "organizations_url": "/v2/users/uaa-id-231/organizations",
        "managed_organizations_url": "/v2/users/uaa-id-231/managed_organizations",
        "billing_managed_organizations_url": "/v2/users/uaa-id-231/billing_managed_organizations",
        "audited_organizations_url": "/v2/users/uaa-id-231/audited_organizations",
        "managed_spaces_url": "/v2/users/uaa-id-231/managed_spaces",
        "audited_spaces_url": "/v2/users/uaa-id-231/audited_spaces"
}]
''')

spaces_definition = json.loads('''
[{
        "name": "space-1",
        "organization_guid": "3deb9f04-b449-4f94-b3dd-c73cefe5b275",
        "space_quota_definition_guid": null,
        "allow_ssh": true,
        "organization_url": "/v2/organizations/3deb9f04-b449-4f94-b3dd-c73cefe5b275",
        "developers_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/developers",
        "managers_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/managers",
        "auditors_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/auditors",
        "apps_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/apps",
        "routes_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/routes",
        "domains_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/domains",
        "service_instances_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/service_instances",
        "app_events_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/app_events",
        "events_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/events",
        "security_groups_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/security_groups",
        "staging_security_groups_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/staging_security_groups"
},
{
        "name": "space-2",
        "organization_guid": "3deb9f04-b449-4f94-b3dd-c73cefe5b275",
        "space_quota_definition_guid": null,
        "allow_ssh": true,
        "organization_url": "/v2/organizations/3deb9f04-b449-4f94-b3dd-c73cefe5b275",
        "developers_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/developers",
        "managers_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/managers",
        "auditors_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/auditors",
        "apps_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/apps",
        "routes_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/routes",
        "domains_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/domains",
        "service_instances_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/service_instances",
        "app_events_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/app_events",
        "events_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/events",
        "security_groups_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/security_groups",
        "staging_security_groups_url": "/v2/spaces/5489e195-c42b-4e61-bf30-323c331ecc01/staging_security_groups"
}]
''')

quota_definition = json.loads('''
{
        "name": "name-1759",
        "organization_guid": "9d3a1be7-d504-42bc-987d-90298dcb6b69",
        "non_basic_services_allowed": true,
        "total_services": 60,
        "total_routes": 1000,
        "memory_limit": 20480,
        "instance_memory_limit": -1,
        "app_instance_limit": -1,
        "app_task_limit": 5,
        "total_service_keys": 600,
        "total_reserved_route_ports": -1,
        "organization_url": "/v2/organizations/9d3a1be7-d504-42bc-987d-90298dcb6b69",
        "spaces_url": "/v2/space_quota_definitions/2203db56-bf87-4ffe-91b9-d46c810fb1b5/spaces"
}
''')

class MockResourceFetcher:
    def __init__(self, client):
        self._client = client

    def get_entities(self, resource_url):
        if resource_url == "/v2/quota_definitions/769e777f-92b6-4ba0-9e48-5f77e6293670":
            return quota_definition
        elif resource_url == "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/spaces":
            return spaces_definition
        elif resource_url == "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/users":
            return users_definition
        elif resource_url == "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/auditors":
            return auditors_definition
        elif resource_url == "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/managers":
            return managers_definition
        elif resource_url == "/v2/organizations/1c0e6074-777f-450e-9abc-c42f39d9b75b/billing_managers":
            return billing_managers_definition

class TestOrgDefinition(unittest.TestCase):

  def test_quota_can_load_its_config(self):
    fetcher = MockResourceFetcher(None)
    org = Organization(organization_definition, fetcher=fetcher)
    org.load()
    o = org.asdict()
    self.assertEqual(o['spaces'][0]['name'], 'space-1')
    self.assertEqual(o['spaces'][1]['name'], 'space-2')
    self.assertEqual(o['users'][0], 'user@example.com')
    self.assertEqual(o['managers'][0], 'manager@example.com')
    self.assertEqual(o['billing_managers'][0], 'billing_manager@example.com')

