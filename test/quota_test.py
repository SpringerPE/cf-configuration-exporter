import unittest
import json
from exporter.exporter import Quota, ResourceParser
from test.test_helper import QuotaAPIMock, MockResourceFetcher

quota = {
  'guid': '80f3e539-a8c0-4c43-9c72-649df53da8cb',
  'name': 'default'
}

class TestQuotaDefinition(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    fetcher = MockResourceFetcher(None)

    mock_quota = QuotaAPIMock(quota, fetcher)
    cls.quota_definition = mock_quota.dump()


  def test_quota_can_load_its_config(self):
    quota = Quota(self.quota_definition)
    quota.load()
    qd = quota.asdict()
    self.assertEqual(qd["name"], "default")