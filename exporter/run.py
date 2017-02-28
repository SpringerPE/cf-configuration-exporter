import sys
import pyaml
import logging

from jinja2 import Environment, PackageLoader
from . import config as cfg
from .exporter import Exporter
from cfconfigurator.cf import CF

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(
    loader=PackageLoader('exporter', 'templates'),
)


def main():

	if cfg.api_url is None:
		logger.critical("Please set EXPORTER_API_URL env variable")
		sys.exit(1)
	if cfg.admin_user is None:
		logger.critical("Please set EXPORTER_ADMIN_USER env variable")
		sys.exit(1)
	if cfg.admin_password is None:
		logger.critical("Please set EXPORTER_ADMIN_PASSWORD env variable")
		sys.exit(1)

	logger.info("Start exporting configuration...")
	logger.info("CF api endpoint set to %s" % cfg.api_url)
	logger.info("Excluding the following env variables from the manifest: %s" % cfg.exclude_env_vars)

	cf_client = CF(cfg.api_url)
	cf_client.login(cfg.admin_user, cfg.admin_password)

	exp = Exporter(cf_client, exclude_vars=cfg.exclude_env_vars)
	exp.generate_manifest()

	manifest = {key: pyaml.dump({key:value}) for key, value in exp.manifest.items()}

	template = env.get_template('manifest.j2')
	rendered = template.render(manifest=manifest)


	with open(cfg.output_file ,"w") as stream:
		stream.write(rendered)

	logger.info("Manifest exported to '%s' file..." % (cfg.output_file))


