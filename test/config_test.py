import unittest
import json
from exporter.exporter import FeatureFlag
from test.test_helper import FeatureFlagsAPIMock


feature_flags =[
{
    "name": "user_org_creation",
    "enabled": False,
  },
  {
    "name": "diego_enabled",
    "enabled": False,
  }
 ]


class TestFeatureFlag(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.mock_flags = FeatureFlagsAPIMock()


	def test_feature_flag_can_load_its_config(self):
		config = json.loads(TestFeatureFlag.mock_flags.get_response(feature_flags))
		feature = FeatureFlag(config[0])
		feature.load()
		self.assertEquals(feature.asdict()['name'], 'user_org_creation')
		self.assertEquals(feature.asdict()['value'], False)

