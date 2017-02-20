import os
import sys
import pyaml
import logging
import sys

from exporter import Exporter
from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_url = os.environ.get("EXPORTER_API_URL", None)
admin_user = os.environ.get("EXPORTER_ADMIN_USER", None)
admin_password = os.environ.get("EXPORTER_ADMIN_PASSWORD", None)

def main():

	if api_url is None:
		logger.critical("Please set EXPORTER_API_URL env variable")
	if admin_user is None:
		logger.critical("Please set EXPORTER_ADMIN_USER env variable")
	if admin_password is None:
		logger.critical("Please set EXPORTER_ADMIN_PASSWORD env variable")

	logger.info("Start exporting configuration...")

	cf_client = CF(api_url)
	cf_client.login(admin_user, admin_password)

	exp = Exporter(cf_client)
	exp.generate_manifest()
	print(pyaml.dump(exp.manifest))	

if __name__ == "__main__":
	main()
