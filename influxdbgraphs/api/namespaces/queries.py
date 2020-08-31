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
from flask_restplus import Namespace, Resource, reqparse

from influxdbgraphs.api.hal import HALLink, HALModel
from influxdbgraphs.api.types import build_raw_influx_query
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)

queries = Namespace("queries", path="/queries")


@dataclass
class QueryResponse(HALModel):
    influxql_query: str


get_parser = reqparse.RequestParser()
get_parser.add_argument(
    "measurement", required=True, type=str, help="Name of the measurement."
)
get_parser.add_argument("field", required=True, type=str, help="Name of the field.")
get_parser.add_argument(
    "function",
    required=False,
    default="mean",
    type=str,
    help="Name of the function to execute on the field (mean, sum, etc).",
)


@queries.route("/")
class Queries(Resource):
    @queries.expect(get_parser)
    def get(self):
        """
        Build a InfluxDB query based on a number of parameters.

        These queries are not stored, and are only a convenience method to
        generate a query from some parameters commonly found in an ESDL InfluxDB
        Profile. The resulting query should be used when creating a graph.
        """
        args = get_parser.parse_args()

        query = build_raw_influx_query(args.field, args.measurement, args.function, [])

        resp = QueryResponse(
            _links=dict(self=HALLink("/queries", "Build InfluxQL queries.")),
            influxql_query=query,
        )
        return jsons.dump(resp)
