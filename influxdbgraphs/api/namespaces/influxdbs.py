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
from typing import List, Optional

import jsons
from flask import request
from flask_accepts import accepts
from flask_restplus import Namespace, Resource
from grafana_api.grafana_api import GrafanaClientError
from marshmallow import Schema, fields

from influxdbgraphs.api.hal import HALLink, HALModel
from influxdbgraphs.grafana.config import GRAFANA_API
from influxdbgraphs.grafana.queries import get_datasources_by_url_and_database
from influxdbgraphs.grafana.types import GrafanaCreateDatasourceResponse
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)

influxdbs = Namespace("influxdbs", path="/influxdbs")


@dataclass
class InfluxDbSource:
    """
    Our (limited) representation of an InfluxDB datasource.
    """

    name: str
    url: str
    database: str


@dataclass
class GetInfluxDbResponse(HALModel):
    influxdbs: List[InfluxDbSource]


@dataclass
class CreateInfluxDbResponse(HALModel):
    message: str
    name: Optional[str]


class CreateInfluxDbSchema(Schema):
    name = fields.String(required=True)
    database_name = fields.String(required=True)
    url = fields.String(required=True)
    basic_auth_user = fields.String(required=True)
    basic_auth_password = fields.String(required=True)


@influxdbs.route("/")
class InfluxDbs(Resource):
    @accepts(dict(name="url", type=str), dict(name="database", type=str), api=influxdbs)
    def get(self):
        url: str = request.parsed_args["url"]
        database: str = request.parsed_args["database"]

        sources = get_datasources_by_url_and_database(url, database)

        return jsons.dump(
            # Only include fields from the GetInfluxDbResponse.
            GetInfluxDbResponse(
                _links=dict(self=HALLink("/influxdbs", "List InfluxDBs"),),
                influxdbs=sources,
            ),
            strict=True,
        )

    @accepts(schema=CreateInfluxDbSchema, api=influxdbs)
    def post(self):
        args = request.parsed_obj

        try:
            raw_grafana_resp = GRAFANA_API.datasource.create_datasource(
                datasource=dict(
                    type="influxdb",
                    name=args["name"],
                    database=args["database_name"],
                    url=args["url"],
                    access="proxy",
                    basicAuth=True,
                    basicAuthUser=args["basic_auth_user"],
                    basicAuthPassword=args["basic_auth_password"],
                )
            )
        except GrafanaClientError as e:
            return e.response, e.status_code

        try:
            grafana_resp = jsons.load(raw_grafana_resp, GrafanaCreateDatasourceResponse)
        except jsons.exceptions.JsonsError:
            logger.exception(f"Error parsing response from Grafana: {raw_grafana_resp}")
            raise

        if grafana_resp.message.lower() != "datasource added":
            return {}, 500

        resp = CreateInfluxDbResponse(
            _links=dict(
                self=HALLink("/influxdbs", "Create InfluxDB"), graphs=HALLink("/graphs")
            ),
            message=grafana_resp.message,
            name=grafana_resp.name,
        )
        return jsons.dump(resp), 201


@influxdbs.route("/<string:name>")
class Influxdb(Resource):
    def delete(self, name):

        try:
            raw_grafana_resp = GRAFANA_API.datasource.delete_datasource_by_name(name)
        except GrafanaClientError as e:
            return e.response, e.status_code

        return raw_grafana_resp
