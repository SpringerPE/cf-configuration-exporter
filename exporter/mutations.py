import re
import logging
import collections
import sys

from .exceptions import FieldNotOptionalException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class ManifestMutation(object):

	def __init__(self, cf_dict):
		self.cf_dict = cf_dict

	def mutate_manifest(self):
		return self.cf_dict

	def map_flags(self, flags, source_flags):
		dest_flags = []

		for flag in source_flags:
			flag_name = flag['name']
			flag_value = flag['value']

			if flags[flag_name] is not None:
				flag_name = flags[flag_name]

			flag_value = "enabled" if flag_value else "disabled"

			dest_flags.append({'name': flag_name, 'value': flag_value})

		return dest_flags

	def map_fields(self, dest_dict, source_dict, fields):
		for field, options in fields.items():
			self.map_field(field, dest_dict, source_dict, **options)

	def map_list_fields(self, dest_dict, source_dict, fields):
		for field, options in fields.items():
			self.map_list_field(field, dest_dict, source_dict, **options)

	def map_field(self, dest_field, dest_dict, source_dict,
		source_field=None, optional=False,
		mapping={}, default=None):

		if not source_field:
			source_field = dest_field
		# the field is present and needs to be mapped
		if source_field in source_dict and source_dict[source_field] in mapping:
			dest_dict[dest_field] = mapping[source_dict[source_field]]
		# the field is present and doesn't need to be mapped
		elif source_field in source_dict:
			if source_dict[source_field] != None:
				dest_dict[dest_field] = source_dict[source_field]
		# the field is not present but it was given a default
		elif default:
			dest_dict[dest_field] = default
		# the field is not present and is not optional
		elif not optional:
			raise FieldNotOptionalException(
				"Field {} is not optional".format(dest_field))

	def map_list_field(self, dest_field, dest_dict, source_dict,
		source_field=None, key_fn=lambda x: x, fmt=None):

		if not source_field:
			source_field=dest_field

		dest_dict[dest_field] = []
		if not source_field in source_dict:
			return

		for elem in source_dict[source_field]:
			elem = fmt.format(key_fn(elem)) if fmt else key_fn(elem)
			dest_dict[dest_field].append(elem)

class TerraformMutation(ManifestMutation):

	user_fmt = '${{cf_user.user_{}.id}}'

	def __init__(self, cf_dict):
		self.cf_dict = cf_dict

	def mutate_manifest(self):
		tf_manifest = {}

		logging.info("Mutating users...")
		tf_manifest["cf_users"] = self.mutate_users(self.cf_dict)

		logging.info("Mutating orgs...")
		tf_manifest["cf_orgs"] = self.mutate_orgs(self.cf_dict)

		logging.info("Mutating quotas...")
		tf_manifest["cf_quotas"] = self.mutate_quotas(self.cf_dict)

		logging.info("Mutating security_groups...")
		tf_manifest["cf_security_groups"] = self.mutate_security_groups(self.cf_dict)

		logging.info("Mutating flags...")
		tf_manifest["cf_feature_flags"] = self.mutate_feature_flags(self.cf_dict)

		return tf_manifest

	def to_terraform_resource_name(self, name):
		return re.sub(r"[@\.]", "_", name)

	def mutate_feature_flags(self, cf_dict):
		cf_flags = cf_dict["cf_feature_flags"]

		flags = {
			"user_org_creation": None,
			"private_domain_creation": None,
			"app_bits_upload": None,
			"app_scaling": None,
			"route_creation": None,
			"service_instance_creation": None,
			"diego_docker": None,
			"set_roles_by_username": None,
			"unset_roles_by_username": None,
			"task_creation": None
		}

		supported_flags = [flag for flag in cf_flags if flag['name'] in flags]
		
		return self.map_flags(flags, supported_flags)

	def mutate_security_groups(self, cf_dict):
		cf_asgs = cf_dict["cf_security_groups"]
		tf_asgs = []

		fields = collections.OrderedDict()
		fields = {
			"guid": {},
			"name": {}
		}

		for cf_asg in cf_asgs:
			tf_asg = collections.OrderedDict()
			self.map_fields(tf_asg, cf_asg, fields)
			tf_asg["rules"] = self.mutate_security_rules(cf_asg["rules"])

			tf_asgs.append(tf_asg)

		return tf_asgs

	def mutate_security_rules(self, rules):
		tf_rules = []

		fields = collections.OrderedDict()
		fields = {
			"protocol": {},
			"destination": {},
			"ports": {"optional": True},
			"description": {"optional": True},
			"type": {"optional": True, "default": 0},
			"code": {"optional": True, "default": 0},
			"log": {"optional": True, "default": "false"}
		}

		for cf_rule in rules:
			tf_rule = collections.OrderedDict()
			self.map_fields(tf_rule, cf_rule, fields)

			tf_rules.append(tf_rule)

		return tf_rules

	def mutate_quotas(self, cf_dict):
		cf_quotas = cf_dict["cf_quotas"]
		tf_quotas = []

		fields = collections.OrderedDict()
		fields = {
			"guid": {},
			"name": {},
			"allow_paid_service_plans": {
				"source_field": "non_basic_services_allowed",
				"mapping": {True: "true", False: "false"}
			},
			"total_memory": {"source_field": "memory_limit"},
			"total_routes": {},
			"total_services": {},
			"instance_memory": {
				"source_field":"instance_memory_limit",
				"optional": True,
				"default": -1
			},
			"total_app_instances": {
				"source_field": "app_instance_limit",
				"optional": True,
				"default": -1
			},
			"total_route_ports":{
				"source_field": "total_reserved_route_ports",
				"optional": True,
				"default": -1
			},
			"total_private_domains": {
				"optional": True,
				"default": 0
			}
		}

		for cf_quota in cf_quotas:
			tf_quota  = collections.OrderedDict()
			self.map_fields(tf_quota, cf_quota, fields)
			tf_quotas.append(tf_quota)

		return tf_quotas

	def mutate_spaces(self, cf_org):
		spaces = cf_org["spaces"]
		org = cf_org["name"]
		tf_spaces = []

		fields = collections.OrderedDict()
		list_fields = collections.OrderedDict()

		fields = {
			"guid": {},
			"name": {},
			"quota": {"optional": True},
			"allow_ssh": {"mapping": {True: "true", False: "false"}}
		}

		list_fields = {
			"asgs": {"source_field": "security_groups"},
			"managers": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			},
			"developers": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			},			
			"auditors": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			}
		}
		for cf_space in spaces:
			tf_space = collections.OrderedDict()
			tf_space["org"] = org
			tf_space["resource_name"] = '{}_{}'.format(org,
				self.to_terraform_resource_name(cf_space["name"]))

			self.map_fields(tf_space, cf_space, fields)
			self.map_list_fields(tf_space, cf_space, list_fields)

			tf_spaces.append(tf_space)

		return tf_spaces

	def mutate_orgs(self, cf_dict):
		cf_orgs = cf_dict["cf_orgs"]
		tf_orgs = []

		fields = collections.OrderedDict()
		list_fields = collections.OrderedDict()

		fields = {
			"guid": {},
			"name": {},
			"quota": {}
		}

		list_fields = {
			"managers": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			},
			"billing_managers": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			},			
			"auditors": {
				"key_fn": lambda x: self.to_terraform_resource_name(x["name"]),
				"fmt": self.user_fmt
			}
		}

		for cf_org in cf_orgs:
			tf_org = collections.OrderedDict()
			tf_org["resource_name"] = self.to_terraform_resource_name(
				cf_org["name"])
			
			self.map_fields(tf_org, cf_org, fields)
			self.map_list_fields(tf_org, cf_org, list_fields)

			tf_org["spaces"] = self.mutate_spaces(cf_org)
			tf_orgs.append(tf_org)

		return tf_orgs

	def mutate_users(self, cf_dict):
		cf_users = cf_dict["cf_users"]
		tf_users = []

		fields = collections.OrderedDict()
		fields = {
			"guid": {},
			"name": {},
			"password": {"optional": True, "mapping": {"None": None}},
			"origin": {"optional": True},
			"given_name": {"optional": True},
			"family_name": {"optional": True},
			"email": {"optional": True}
		}

		for cf_user in cf_users:
			tf_user = collections.OrderedDict()
			tf_user["resource_name"] = self.to_terraform_resource_name(
				cf_user["name"])
			self.map_fields(tf_user, cf_user, fields)

			tf_users.append(tf_user)

		return tf_users

class CFConfiguratorMutation(ManifestMutation):

	def __init__(self, cf_dict):
		self.cf_dict = cf_dict

	def mutate_manifest(self):
		cc_manifest = collections.OrderedDict()

		logging.info("Mutating users...")
		cc_manifest["cf_users"] = self.mutate_users(self.cf_dict)

		logging.info("Mutating orgs...")
		cc_manifest["cf_orgs"] = self.mutate_orgs(self.cf_dict)

		logging.info("Mutating quotas...")
		cc_manifest["cf_quotas"] = self.mutate_quotas(self.cf_dict)

		logging.info("Mutating security_groups...")
		cc_manifest["cf_security_groups"] = self.mutate_security_groups(self.cf_dict)

		logging.info("Mutating flags...")
		cc_manifest["cf_feature_flags"] = self.mutate_feature_flags(self.cf_dict)

		return cc_manifest

	def mutate_feature_flags(self, cf_dict):
		cf_flags = cf_dict["cf_feature_flags"]
		cc_flags = []

		flags = {
			"user_org_creation": None,
			"private_domain_creation": None,
			"app_bits_upload": None,
			"app_scaling": None,
			"route_creation": None,
			"service_instance_creation": None,
			"diego_docker": None,
			"set_roles_by_username": None,
			"unset_roles_by_username": None,
			"task_creation": None
		}

		supported_flags = [flag for flag in cf_flags if flag['name'] in flags]

		return self.map_flags(flags, supported_flags)

	def mutate_security_groups(self, cf_dict):
		cf_asgs = cf_dict["cf_security_groups"]
		cc_asgs = []

		fields = collections.OrderedDict()
		fields = {
			"name": {}
		}

		for cf_asg in cf_asgs:
			cc_asg = collections.OrderedDict()
			self.map_fields(cc_asg, cf_asg, fields)
			cc_asg["rules"] = self.mutate_security_rules(cf_asg["rules"])

			cc_asgs.append(cc_asg)

		return cc_asgs

	def mutate_security_rules(self, rules):
		cc_rules = []
		fields = collections.OrderedDict()
		fields = {
			"protocol": {},
			"destination": {},
			"ports": {"optional": True},
			"description": {"optional": True},
			"type": {"optional": True, "default": 0},
			"code": {"optional": True, "default": 0},
			"log": {"optional": True, "default": "false"}
		}

		for cf_rule in rules:
			cc_rule = collections.OrderedDict()
			self.map_fields(cc_rule, cf_rule, fields)
			cc_rules.append(cc_rule)

		return cc_rules

	def mutate_quotas(self, cf_dict):
		cf_quotas = cf_dict["cf_quotas"]
		cc_quotas = []

		fields = collections.OrderedDict()
		fields = {
			"name": {},
			"non_basic_services_allowed": {},
			"memory_limit": {},
			"total_routes": {},
			"total_services": {},
			"instance_memory_limit":{"optional": True, "default": -1},
			"app_instance_limit": {"optional": True, "default": -1},
			"total_reserved_route_ports": {"optional": True, "default": -1},
			"total_private_domains": {"optional": True, "default": 0}
		}

		for cf_quota in cf_quotas:
			cc_quota  = collections.OrderedDict()
			self.map_fields(cc_quota, cf_quota, fields)
			cc_quotas.append(cc_quota)

		return cc_quotas

	def mutate_spaces(self, cf_org):
		spaces = cf_org["spaces"]
		org = cf_org["name"]
		cc_spaces = []

		fields = collections.OrderedDict()
		fields = {
			"name": {},
			"quota": {"optional": True},
			"allow_ssh": {}
		}

		list_fields = collections.OrderedDict()
		list_fields = {
			"security_groups": {},
			"managers": {},
			"developers": {},			
			"auditors": {}
		}

		for cf_space in spaces:
			cc_space = collections.OrderedDict()
			cc_space["org"] = org

			self.map_fields(cc_space, cf_space, fields)
			self.map_list_fields(cc_space, cf_space, list_fields)

			cc_spaces.append(cc_space)

		return cc_spaces

	def mutate_orgs(self, cf_dict):
		cf_orgs = cf_dict["cf_orgs"]
		cc_orgs = []

		fields = collections.OrderedDict()
		fields = {
			"name": {},
			"quota": {}
		}

		list_fields = collections.OrderedDict()
		list_fields = {
			"managers": {},
			"billing_managers": {},			
			"auditors": {}
		}

		for cf_org in cf_orgs:
			cc_org = collections.OrderedDict()

			self.map_fields(cc_org, cf_org, fields)
			self.map_list_fields(cc_org, cf_org, list_fields)

			cc_org["spaces"] = self.mutate_spaces(cf_org)
			cc_orgs.append(cc_org)

		return cc_orgs

	def mutate_users(self, cf_dict):
		cf_users = cf_dict["cf_users"]
		cc_users = []

		fields = collections.OrderedDict()
		fields = {
			"name": {},
			"password": {"optional": True},
			"origin": {"optional": True},
			"given_name": {"optional": True},
			"family_name": {"optional": True},
			"email": {"optional": True}
		}

		for cf_user in cf_users:
			cc_user = collections.OrderedDict()
			self.map_fields(cc_user, cf_user, fields)
			cc_users.append(cc_user)

		return cc_users