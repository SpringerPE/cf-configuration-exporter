import unittest
import json
from test.test_helper import (
    MockResourceFetcher, UserAPIMock, UserUAAAPIMock,
    SpaceAPIMock, OrganizationAPIMock
)
from exporter.exporter import User, ResourceParser

user = {
    'userName': "Z5qRBj@test.org",
    'email': 'Z5qRBj@test.org',
    'externalId': 'test-user',
    'guid': "2dd424e5-f2ed-4bb7-b374-c347513915ca",
    'space_guid': "fc898723-2192-42d9-9567-c0b2e03a3169"
}

space = {
    'guid': 'fc898723-2192-42d9-9567-c0b2e03a3169',
    'name': 'name-2064',
    'org_guid': '6e1ca5aa-55f1-4110-a97f-1f3473e771b9'
}

organization = {
    'guid': "6e1ca5aa-55f1-4110-a97f-1f3473e771b9",
    'name': 'name-1716'
}


class TestUserDefinition(unittest.TestCase):

  @classmethod
  def setUpClass(cls):

    fetcher = MockResourceFetcher(None)
    cls.fetcher = fetcher

    mock_user = UserAPIMock()
    mock_uaa_user = UserUAAAPIMock()
    cls.user_definition = ResourceParser.extract_entities(json.loads(mock_user.get_response(user)))
    cls.uaa_user_definition = json.loads(mock_uaa_user.get_response(user))

    mock_space = SpaceAPIMock(space, fetcher)
    default_space_response = mock_space.dump()

    mock_organization = OrganizationAPIMock(organization, fetcher)
    default_organization_response = mock_organization.dump()


  def test_user_can_load_its_config(self):

    user = User(
        self.uaa_user_definition, 
        cf_response=self.user_definition,
        fetcher=self.fetcher)

    user.load()
    u = user.asdict()
    self.assertEqual(u["name"], "Z5qRBj@test.org")

    self.assertEqual(u["email"], "Z5qRBj@test.org")

    self.assertEqual(u["given_name"], "given name")
    self.assertEqual(u["family_name"], "family name")

    self.assertEqual(u["default_space"], "name-2064")
    self.assertEqual(u["default_organization"], "name-1716")