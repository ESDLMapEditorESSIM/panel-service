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

from dataclasses import dataclass

import jsons
from flask_restplus import Namespace, Resource

from influxdbgraphs.api.hal import HALLink, HALModel
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)

root = Namespace("root", path="/")


@dataclass
class WelcomeResponse(HALModel):
    message: str


@root.route("/welcome")
class Welcome(Resource):
    def get(self):
        return jsons.dump(
            WelcomeResponse(
                _links=dict(
                    self=HALLink("/welcome"),
                    influxdbs=HALLink("/influxdbs", "Create InfluxDB datasources."),
                    graphs=HALLink("/graphs", "Create graphs."),
                    queries=HALLink("/queries", "Build InfluxQL queries."),
                ),
                message="Welcome to the InfluxDB Graphs API.",
            )
        )


@root.route("/status")
class Status(Resource):
    def get(self):
        return {}, 200
