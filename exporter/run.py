import os
import sys
import pyaml
import logging
import sys

from jinja2 import Environment, PackageLoader, select_autoescape
from .exporter import Exporter
from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(
    loader=PackageLoader('exporter', 'templates'),
)

api_url = os.environ.get("EXPORTER_API_URL", None)
admin_user = os.environ.get("EXPORTER_ADMIN_USER", None)
admin_password = os.environ.get("EXPORTER_ADMIN_PASSWORD", None)
output_file = os.environ.get("EXPORTER_OUTPUT_FILE", "output")

def main():

	if api_url is None:
		logger.critical("Please set EXPORTER_API_URL env variable")
		sys.exit(1)
	if admin_user is None:
		logger.critical("Please set EXPORTER_ADMIN_USER env variable")
		sys.exit(1)
	if admin_password is None:
		logger.critical("Please set EXPORTER_ADMIN_PASSWORD env variable")
		sys.exit(1)

	logger.info("Start exporting configuration...")

	cf_client = CF(api_url)
	cf_client.login(admin_user, admin_password)

	exp = Exporter(cf_client)
	exp.generate_manifest()

	manifest = {key: pyaml.dump({key:value}) for key, value in exp.manifest.items()}

	template = env.get_template('manifest.j2')
	rendered = template.render(manifest=manifest)


	with open(output_file ,"w") as stream:
		stream.write(rendered)

