import unittest
import json
from exporter.exporter import FeatureFlag

feature_flags = '''{
    "name": "user_org_creation",
    "enabled": false,
    "error_message": null,
    "url": "/v2/config/feature_flags/user_org_creation"
  }'''

class TestFeatureFlag(unittest.TestCase):

	def test_feature_flag_can_load_its_config(self):
		config = json.loads(feature_flags)
		feature = FeatureFlag(config)
		feature.load()
		self.assertEquals(feature.asdict()['name'], 'user_org_creation')
		self.assertEquals(feature.asdict()['value'], False)

