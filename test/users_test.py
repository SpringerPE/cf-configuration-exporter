import unittest
import json
from test.test_helper import UserAPIMock, SpaceAPIMock, OrganizationAPIMock
from exporter.exporter import User, ResourceParser

user = {
    'userName': "Z5qRBj@test.org",
    'email': 'Z5qRBj@test.org',
    'externalId': 'test-user',
    'guid': "2dd424e5-f2ed-4bb7-b374-c347513915ca",
    'space_guid': "fc898723-2192-42d9-9567-c0b2e03a3169"
}

mock_user = UserAPIMock()
user_definition = ResourceParser.extract_entities(json.loads(mock_user.get_cf_response(user)))
uaa_user_definition = json.loads(mock_user.get_uaa_response(user))

space = {
    'guid': 'fc898723-2192-42d9-9567-c0b2e03a3169',
    'name': 'name-2064'
}
mock_space = SpaceAPIMock()
default_space_response = ResourceParser.extract_entities(json.loads(mock_space.get_cf_response(space)))

organization = {
    'guid': "6e1ca5aa-55f1-4110-a97f-1f3473e771b9",
    'name': 'name-1716'
}
mock_organization = OrganizationAPIMock()
default_organization_response = ResourceParser.extract_entities(
                                                        json.loads(mock_organization.get_cf_response(organization)))


class MockResourceFetcher:
    def __init__(self, client):
        self._client = client
        self.entities = {}

    def register_entity(self, url, response):
        self.entities[url] = response

    def get_entities(self, resource_url):
        return self.entities[resource_url]

class TestUserDefinition(unittest.TestCase):

  def test_user_can_load_its_config(self):

    fetcher = MockResourceFetcher(None)
    fetcher.register_entity("/v2/spaces/%s" % space['guid'], default_space_response)
    fetcher.register_entity("/v2/organizations/%s" % organization['guid'], default_organization_response)

    user = User(
        uaa_user_definition, 
        cf_response=user_definition,
        fetcher=fetcher)

    user.load()
    u = user.asdict()
    self.assertEqual(u["name"], "Z5qRBj@test.org")

    self.assertEqual(u["email"], "Z5qRBj@test.org")

    self.assertEqual(u["given_name"], "given name")
    self.assertEqual(u["family_name"], "family name")

    self.assertEqual(u["default_space"], "name-2064")
    self.assertEqual(u["default_organization"], "name-1716")