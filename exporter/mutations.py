import re

from .exceptions import FieldNotOptionalException

class TerraformMutation(object):

	user_fmt = '${{cf_user.user_{}.id}}'

	def __init__(self, cf_dict):
		self.cf_dict = cf_dict

	def manifest_to_terraform(self):
		tf_manifest = {}

		print("Mutating users...")
		tf_manifest["cf_users"] = self.cf_users_to_terraform(self.cf_dict)
		print("Mutating orgs...")
		tf_manifest["cf_orgs"] = self.cf_orgs_to_terraform(self.cf_dict)
		print("Mutating quotas...")
		tf_manifest["cf_quotas"] = self.cf_quotas_to_terraform(self.cf_dict)
		print("Mutating security_groups...")
		tf_manifest["cf_security_groups"] = self.cf_security_groups_to_terraform(self.cf_dict)
		print("Mutating flags...")
		tf_manifest["cf_feature_flags"] = self.cf_feature_flags_to_terraform(self.cf_dict)
		return tf_manifest

	def to_terraform_resource_name(self, name):
		return re.sub(r"[@\.]", "_", name)

	def map_field(self, tf_field, tf_dict, cf_field, cf_dict, optional=False, mapping={}, default=None):
		if optional == False:
			if not cf_field in cf_dict:
				raise FieldNotOptionalException("Field {} is not optional".format(tf_field))

		if cf_field in cf_dict:
			if cf_dict[cf_field] in mapping:
				tf_dict[tf_field] = mapping[cf_dict[cf_field]]
			else:
				mapped_field = cf_dict[cf_field]
				if mapped_field != None:
					tf_dict[tf_field] = mapped_field
		elif default:
			tf_dict[tf_field] = default

	def map_list_field(self, tf_field, tf_dict, cf_field, cf_dict, cf_key=None, fmt='{}'):
		tf_dict[tf_field] = []
		if cf_field in cf_dict:
			for elem in cf_dict[cf_field]:
				if cf_key:
					tf_dict[tf_field].append(fmt.format(elem[cf_key]))
				else:
					tf_dict[tf_field].append(fmt.format(elem))


	def cf_feature_flags_to_terraform(self, cf_dict):
		cf_flags = cf_dict["cf_feature_flags"]
		tf_flags = []

		supported_flags = {
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

		flags_to_port = [flag for flag in cf_flags if flag['name'] in supported_flags]

		for flag in flags_to_port:
			flag_name = flag['name'] if supported_flags[flag['name']] == None else supported_flags[flag['name']]
			flag_value = "enabled" if flag['value'] else "disabled"

			tf_flags.append({'name': flag_name, 'value': flag_value})
		
		return tf_flags

	def cf_security_groups_to_terraform(self, cf_dict):
		cf_asgs = cf_dict["cf_security_groups"]
		tf_asgs = []

		for cf_asg in cf_asgs:
			tf_asg = {}
			self.map_field("name", tf_asg, "name", cf_asg)
			self.map_field("guid", tf_asg, "guid", cf_asg)

			tf_asg["rules"] = self.cf_security_rules_to_terraform(cf_asg["rules"])

			tf_asgs.append(tf_asg)

		return tf_asgs

	def cf_security_rules_to_terraform(self, rules):
		tf_rules = []

		for cf_rule in rules:
			tf_rule = {}
			self.map_field("protocol", tf_rule, "protocol", cf_rule)
			self.map_field("destination", tf_rule, "destination", cf_rule)
			self.map_field("ports", tf_rule, "ports", cf_rule, optional=True)
			self.map_field("description", tf_rule, "description", cf_rule, optional=True)
			self.map_field("type", tf_rule, "type", cf_rule, optional=True, default=0)
			self.map_field("code", tf_rule, "code", cf_rule, optional=True, default=0)
			self.map_field("log", tf_rule, "log", cf_rule, optional=True, default="false")

			tf_rules.append(tf_rule)

		return tf_rules

	def cf_quotas_to_terraform(self, cf_dict):
		cf_quotas = cf_dict["cf_quotas"]
		tf_quotas = []

		for cf_quota in cf_quotas:
			tf_quota  = {}
			self.map_field("guid", tf_quota, "guid", cf_quota)
			self.map_field("name", tf_quota, "name", cf_quota)
			self.map_field("allow_paid_service_plans", tf_quota, "non_basic_services_allowed", cf_quota, mapping={True: "true", False: "false"})
			self.map_field("total_memory", tf_quota, "memory_limit", cf_quota)
			self.map_field("total_routes", tf_quota, "total_routes", cf_quota)
			self.map_field("total_services", tf_quota, "total_services", cf_quota)
			self.map_field("instance_memory", tf_quota, "instance_memory_limit", cf_quota, optional=True, default=-1)
			self.map_field("total_app_instances", tf_quota, "app_instance_limit", cf_quota, optional=True, default=-1)
			self.map_field("total_route_ports", tf_quota, "total_reserved_route_ports", cf_quota, optional=True, default=-1)
			self.map_field("total_private_domains", tf_quota, "total_private_domains", cf_quota, optional=True, default=0)
			tf_quotas.append(tf_quota)

		return tf_quotas

	def cf_spaces_to_terraform(self, cf_org):
		spaces = cf_org["spaces"]
		org = cf_org["name"]
		tf_spaces = []

		for cf_space in spaces:
			tf_space = {}			
			tf_space["resource_name"] = self.to_terraform_resource_name(cf_space["name"])

			tf_space["org"] = org
			self.map_field("guid", tf_space, "guid", cf_space)
			self.map_field("name", tf_space, "name", cf_space)
			self.map_field("quota", tf_space, "quota", cf_space, optional=True)
			self.map_field("allow_ssh", tf_space, "allow_ssh", cf_space, mapping={True: "true", False: "false"})

			self.map_list_field("asgs", tf_space, "security_groups", cf_space)
			self.map_list_field("managers", tf_space, "managers", cf_space, cf_key="name", fmt=self.user_fmt)
			self.map_list_field("developers", tf_space, "developers", cf_space, cf_key="name", fmt=self.user_fmt)
			self.map_list_field("auditors", tf_space, "auditors", cf_space, cf_key="name", fmt=self.user_fmt)

			tf_spaces.append(tf_space)

		return tf_spaces

	def cf_orgs_to_terraform(self, cf_dict):
		cf_orgs = cf_dict["cf_orgs"]
		tf_orgs = []

		for cf_org in cf_orgs:
			tf_org = {}
			tf_org["resource_name"] = self.to_terraform_resource_name(cf_org["name"])
			
			self.map_field("guid", tf_org, "guid", cf_org)
			self.map_field("name", tf_org, "name", cf_org)
			self.map_field("quota", tf_org, "quota", cf_org)
			self.map_list_field("managers", tf_org, "managers", cf_org, cf_key="name", fmt=self.user_fmt)
			self.map_list_field("billing_managers", tf_org, "billing_managers", cf_org, cf_key="name", fmt=self.user_fmt)
			self.map_list_field("auditors", tf_org, "auditors", cf_org, cf_key="name", fmt=self.user_fmt)

			tf_org["spaces"] = self.cf_spaces_to_terraform(cf_org)
			tf_orgs.append(tf_org)

		return tf_orgs

	def cf_users_to_terraform(self, cf_dict):
		cf_users = cf_dict["cf_users"]
		tf_users = []

		for cf_user in cf_users:
			tf_user = {}


			tf_user["resource_name"] = self.to_terraform_resource_name(cf_user["name"])
			self.map_field("guid", tf_user, "guid", cf_user)
			self.map_field("name", tf_user, "name", cf_user)
			self.map_field("password", tf_user, "password", cf_user, optional=True, mapping={"None": None})
			self.map_field("origin", tf_user, "origin", cf_user, optional=True)
			self.map_field("given_name", tf_user, "given_name", cf_user, optional=True)
			self.map_field("family_name", tf_user, "family_name", cf_user, optional=True)
			self.map_field("email", tf_user, "email", cf_user, optional=True)

			tf_users.append(tf_user)

		return tf_users
