import unittest
import json
from exporter.exporter import Quota

quota_definition = '''
{
        "name": "default",
        "non_basic_services_allowed": true,
        "total_services": 100,
        "total_routes": 1000,
        "total_private_domains": -1,
        "memory_limit": 10240,
        "trial_db_allowed": false,
        "instance_memory_limit": -1,
        "app_instance_limit": -1,
        "app_task_limit": -1,
        "total_service_keys": -1,
        "total_reserved_route_ports": 0
      }
'''

class TestQuotaDefinition(unittest.TestCase):

  def test_quota_can_load_its_config(self):
    config = json.loads(quota_definition)
    quota = Quota(config)
    quota.load()
    qd = quota.asdict()
    self.assertEqual(qd["name"], "default")