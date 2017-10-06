import unittest

from exporter.mutations import TerraformMutation, ManifestMutation
from exporter.exceptions import FieldNotOptionalException

cf_dict = {
"cf_orgs":[{
  "name": "first_org",
  "spaces": [
  {
	  "name": "first_space", 
	  "org": "first_org", 
	  "quota": "m", 
	  "allow_ssh": True,
	  "asgs": [],
	  "managers": [{"name": "manager"}],
	  "developers": [{"name": "developer"}],
	  "auditors": [{"name": "auditor"}] 
  },
  {
	  "name": "second_space", 
	  "org": "second_org", 
	  "quota": "m", 
	  "allow_ssh": False,
	  "asgs": [],
	  "managers": [{"name": "manager"}],
	  "developers": [{"name": "developer"}],
	  "auditors": [{"name": "auditor"}] 
  }]
}]
}

class TestMutations(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		pass

	def test_map_field(self):
		source_dict = {"name": "resource_name", "property": "value", "none_property": None}
		dest_dict = {}

		tm = ManifestMutation(source_dict)
		tm.map_field("name", dest_dict, source_dict)

		self.assertIn("name", dest_dict)
		self.assertEqual(dest_dict["name"], "resource_name")

		# Test renaming cf field
		tm.map_field("mutated_name", dest_dict, source_dict, cf_field="name")
		self.assertIn("mutated_name", dest_dict)
		self.assertEqual(dest_dict["mutated_name"], "resource_name")

		#Test optionality
		with self.assertRaises(FieldNotOptionalException):
			tm.map_field("not_existent", dest_dict, source_dict, optional=False)

		tm.map_field("not_existent", dest_dict, source_dict, optional=True)
		self.assertNotIn("not_existent", dest_dict)


		#Test default
		tm.map_field("not_existent_w_default", dest_dict,
			source_dict, cf_field="not_existent", optional=True, default="default")
		self.assertIn("not_existent_w_default", dest_dict)
		self.assertEqual(dest_dict["not_existent_w_default"], "default")

		#Test mapping
		tm.map_field("mapped_property", dest_dict, source_dict,
			cf_field="property", mapping={"value": "mapped_value"})
		self.assertIn("mapped_property", dest_dict)
		self.assertEqual(dest_dict["mapped_property"], "mapped_value")

		#Test mapping when source value is None
		tm.map_field("none_property", dest_dict, source_dict)
		self.assertNotIn("none_property", dest_dict)

	def test_map_list_field(self):
		source_dict = {"name": "resource_name", "list_item": ["value1", "value2"]}
		dest_dict = {}

		tm = ManifestMutation(source_dict)
		tm.map_list_field("list_item", dest_dict, source_dict)

		self.assertIn("list_item", dest_dict)
		self.assertEqual(["value1", "value2"], dest_dict["list_item"])

		# Test that key formatting works
		tm.map_list_field("list_item", dest_dict, source_dict, fmt='fmt_{}')

		self.assertIn("list_item", dest_dict)
		self.assertEqual(["fmt_value1", "fmt_value2"], dest_dict["list_item"])

		# Test that key mapping works
		tm.map_list_field("list_item", dest_dict, source_dict, key_fn=lambda x: "mapped")

		self.assertIn("list_item", dest_dict)
		self.assertEqual(["mapped", "mapped"], dest_dict["list_item"])
