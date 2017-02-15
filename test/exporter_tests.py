import unittest
import json
import fixtures
from exporter.exporter import SecurityGroup, SecurityRule

class TestExporter(unittest.TestCase):

	def test_security_rule(self):
		sec_rule_obj = json.loads(fixtures.security_group_response)
		sec_rule = SecurityRule(sec_rule_obj['entity']['rules'][0])
		sec_rule.load()
		self.assertEquals(sec_rule.asdict()['protocol'], 'udp')
		self.assertEquals(sec_rule.asdict()['ports'], '8080')
		self.assertEquals(sec_rule.asdict()['destination'], '198.41.191.47/1')