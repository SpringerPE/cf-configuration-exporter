import os
import pyaml
from exporter.exporter import Exporter
from cfconfigurator.cf import CF
from cfconfigurator.uaa import UAA, UAAException


if __name__ == "__main__":
	api_url = os.environ.get("EXPORTER_API_URL")
	admin_user = os.environ.get("EXPORTER_ADMIN_USER")
	admin_password = os.environ.get("EXPORTER_ADMIN_PASSWORD")

	cf_client = CF(api_url)
	cf_client.login(admin_user, admin_password)

	exp = Exporter(cf_client)
	exp.generate_manifest()
	print(pyaml.dump(exp.manifest))