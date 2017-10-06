import sys
import pyaml
import logging
import os
import re
import json
import uuid

from jinja2 import Environment, PackageLoader
from . import config as cfg
from .exporter import Exporter
from cfconfigurator.cf import CF
from .mutations import TerraformMutation, CFConfiguratorMutation

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(
    loader=PackageLoader('exporter', 'templates'),
    trim_blocks=True,
    lstrip_blocks=True
)


def main():

    valid_config = True

    logger_message = """
			Please set:
			EXPORTER_API_URL env variable ie. https://api.test.example.com
			EXPORTER_ADMIN_USER env variable ie. admin
			EXPORTER_ADMIN_PASSWORD env variable

			Optional env variables are:
			EXPORTER_OUTPUT_FILE env variable to set the name of the output file (default is output)
			EXPORTER_EXCLUDE_ENV_VARS env variable to exclude env variables."""

    if (cfg.api_url is None) or (cfg.admin_user is None) or (cfg.admin_password is None):
        logger.critical(logger_message)
        valid_config = False
    if not valid_config:
        sys.exit(1)

    logger.info("Start exporting configuration...")
    logger.info("CF api endpoint set to %s" % cfg.api_url)
    logger.info("Excluding the following env variables from the manifest: %s" %
                cfg.exclude_env_vars)

    cf_client = CF(cfg.api_url)
    cf_client.login(cfg.admin_user, cfg.admin_password)

    exp = Exporter(cf_client, exclude_vars=cfg.exclude_env_vars)
    exp.generate_manifest()

    tm = TerraformMutation(exp.manifest)
    terraform_manifest = tm.mutate_manifest()
    export_cf_terraform_config(terraform_manifest)

    cc = CFConfiguratorMutation(exp.manifest)
    cc_manifest = cc.mutate_manifest()
    export_cf_configurator_config(cc_manifest)


def export_cf_terraform_config(manifest, output_folder="output_terraform"):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for template_name in ["user", "org", "quota", "security_group", "config"]:
        with open(os.path.join(output_folder, template_name + ".tf"), "w") as stream:
            template = env.get_template('terraform/' + template_name + ".j2")
            rendered = template.render(manifest=manifest)
            stream.write(rendered)

    with open(os.path.join(output_folder, "terraform.tfstate"), "w") as tf_state_file:
        template = env.get_template('tfstate/tfstate.j2')
        lineage = str(uuid.uuid4())
        tf_state = template.render(manifest=manifest, lineage=lineage)
        tf_state_file.write(tf_state)

    logger.info("Terraform config exported to '%s' folder..." %
                (output_folder))


def export_cf_configurator_config(manifest, output_file="output"):
    manifest = {key: pyaml.dump({key: value})
                for key, value in manifest.items()}

    template = env.get_template('manifest.j2')
    rendered = template.render(manifest=manifest)

    with open(output_file, "w") as stream:
        stream.write(rendered)

    logger.info("Manifest exported to '%s' file..." % (output_file))
