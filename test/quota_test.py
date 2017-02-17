import unittest
import json
from exporter.exporter import Quota, ResourceParser
from test.test_helper import QuotaAPIMock

quota = {
  'guid': '80f3e539-a8c0-4c43-9c72-649df53da8cb',
  'name': 'default'
}

mock_quota = QuotaAPIMock()
quota_definition = ResourceParser.extract_entities(
                                  json.loads(mock_quota.get_cf_response(quota))
                              )

class TestQuotaDefinition(unittest.TestCase):

  def test_quota_can_load_its_config(self):
    quota = Quota(quota_definition)
    quota.load()
    qd = quota.asdict()
    self.assertEqual(qd["name"], "default")