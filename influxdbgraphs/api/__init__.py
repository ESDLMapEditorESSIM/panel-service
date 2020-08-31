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

from flask_restplus import Api

from influxdbgraphs.api.namespaces.graphs import graphs
from influxdbgraphs.api.namespaces.influxdbs import influxdbs
from influxdbgraphs.api.namespaces.queries import queries
from influxdbgraphs.api.namespaces.root import root

api = Api(
    title="InfluxDB Panel Service",
    version="1.0",
    description="Panel service for ESDL-related tools.",
    # All API metadatas
)
api.add_namespace(root)
api.add_namespace(queries)
api.add_namespace(graphs)
api.add_namespace(influxdbs)
