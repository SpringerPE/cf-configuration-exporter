#Configuration variables
import logging
import os

logger = logging.getLogger(__file__)

api_url = os.environ.get("EXPORTER_API_URL", None)
admin_user = os.environ.get("EXPORTER_ADMIN_USER", None)
admin_password = os.environ.get("EXPORTER_ADMIN_PASSWORD", None)
output_file = os.environ.get("EXPORTER_OUTPUT_FILE", "output")
exclude_env_vars = os.environ.get("EXPORTER_EXCLUDE_ENV_VARS", "")