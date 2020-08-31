#  This work is based on original code developed and copyrighted by TNO 2020.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO
#

import os

from grafana_api.grafana_face import GrafanaFace

INTERNAL_GRAFANA_HOST = os.getenv("INTERNAL_GRAFANA_HOST")
INTERNAL_GRAFANA_PORT = os.getenv("INTERNAL_GRAFANA_PORT")
EXTERNAL_GRAFANA_URL = os.getenv("EXTERNAL_GRAFANA_URL")

GRAFANA_KEY = os.getenv("GRAFANA_API_KEY")
"""The Grafana API key. To be able to manage all resources, the role needs to be Admin."""

GRAFANA_API = GrafanaFace(
    auth=GRAFANA_KEY, host=INTERNAL_GRAFANA_HOST, port=INTERNAL_GRAFANA_PORT
)
