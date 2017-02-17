from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('test', 'templates'),
)


class UserAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('user_cf.j2')
    self.uaa_template = env.get_template('user_uaa.j2')
    self.org_users_template = env.get_template('org_users.j2')

  def get_cf_response(self, user):
    return self.cf_template.render(user=user)

  def get_uaa_response(self, user):
    return self.uaa_template.render(user=user)

  def get_org_users_response(self, user):
    return self.org_users_template.render(user=user)

class SpaceAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('space.j2')
    self.cf_org_template = env.get_template('org_spaces.j2')

  def get_cf_response(self, space):
    return self.cf_template.render(space=space)

  def get_cf_org_spaces_response(self, space):
    return self.cf_org_template.render(space=space)

class OrganizationAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('organization.j2')

  def get_cf_response(self, organization):
    return self.cf_template.render(organization=organization)

class QuotaAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('quota.j2')

  def get_cf_response(self, quota):
    return self.cf_template.render(quota=quota)


class SecGroupAPIMock:

  def __init__(self):
    self.cf_template = env.get_template('security_groups.j2')

  def get_cf_space_sg_response(self, sg):
    return self.cf_template.render(sg=sg)