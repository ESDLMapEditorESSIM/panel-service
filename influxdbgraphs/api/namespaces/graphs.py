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

import json
from dataclasses import dataclass
from typing import List

import jsons
import marshmallow_dataclass
import pytz
from flask import request
from flask_accepts import accepts
from flask_restplus import Namespace, Resource
from grafana_api.grafana_api import GrafanaClientError
from grafanalib.core import SECONDS_FORMAT, YAxis
from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from influxdbgraphs.api.hal import HALLink, HALModel
from influxdbgraphs.api.types import YAXIS_TYPES, InfluxDbQuery, RawInfluxDbQuery
from influxdbgraphs.grafana.config import EXTERNAL_GRAFANA_URL, GRAFANA_API
from influxdbgraphs.grafana.grafanalib_types import (
    GrafanalibDashboardEncoder,
    Threshold,
)
from influxdbgraphs.grafana.queries import get_datasources_by_url_and_database
from influxdbgraphs.grafana.types import (
    GrafanaCreateDashboardResponse,
    GrafanaGetDashboardResponse,
)
from influxdbgraphs.graphing.dashboard import create_dashboard
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)

graphs = Namespace("graphs", path="/graphs")


@dataclass
class GraphResponse(HALModel):
    """The response after creating or requesting a graph."""

    dashboard_uid: str
    slug: str
    panel_id: int
    embed_url: str


RawInfluxQuerySchema = marshmallow_dataclass.class_schema(RawInfluxDbQuery)
InfluxQuerySchema = marshmallow_dataclass.class_schema(InfluxDbQuery)


class ThresholdSchema(Schema):
    value = fields.Number()
    op = fields.String(default="gt")
    yaxis = fields.String(default="left", validate=validate.OneOf(("left", "right")))
    color_mode = fields.String(default="warning")


class YAxisSchema(Schema):
    format = fields.String(validate=validate.OneOf(YAXIS_TYPES))
    min = fields.Number(default=0, allow_none=True)
    max = fields.Number(default=None, allow_none=True)


class InfluxDbSchema(Schema):
    url = fields.String(required=True)
    database = fields.String(required=True)


class CreateGraphSchema(Schema):
    title = fields.String(required=True)
    start = fields.DateTime(required=True)
    end = fields.DateTime(required=True)
    timezone = fields.String(
        required=False, default="CET", validate=validate.OneOf(pytz.all_timezones)
    )
    influxdb_name = fields.String(required=False)
    influxdb = fields.Nested(InfluxDbSchema, required=False)
    raw_influx_queries = fields.List(fields.Nested(RawInfluxQuerySchema))
    influx_queries = fields.List(fields.Nested(InfluxQuerySchema))
    yaxes = fields.List(fields.Nested(YAxisSchema()))
    thresholds = fields.List(fields.Nested(ThresholdSchema))
    grafana_graph_params = fields.Dict(required=False)
    theme = fields.String(required=False, validate=validate.OneOf(("dark", "light")))

    @validates_schema
    def validate_influxdb(self, data, **kwargs):
        no_db_provided = not (data.get("influxdb_name") or data.get("influxdb"))
        both_dbs_provided = data.get("influxdb_name") and data.get("influxdb")
        if no_db_provided or both_dbs_provided:
            raise ValidationError(
                "Either provide an influxdb_name or an influxdb object."
            )

    @validates_schema
    def validate_queries(self, data, **kwargs):
        if not data.get("raw_influx_queries") and not data.get("influx_queries"):
            raise ValidationError("Please provide at least one InfluxDB query.")


@graphs.route("/")
class Graphs(Resource):
    """
    Resource for all graphs, as well as creating graphs.
    """

    @accepts(schema=CreateGraphSchema, api=graphs)
    def post(self):
        """
        Create a new dashboard with a panel, that executes the query on the specified datasource.
        """
        args = request.parsed_obj

        if args.get("influxdb_name"):
            influx_db_name = args["influxdb_name"]
            # Verify that the datasource exists.
            try:
                GRAFANA_API.datasource.get_datasource_by_name(args["influxdb_name"])
            except GrafanaClientError as e:
                if e.status_code == 404:
                    return (
                        {
                            "message": "InfluxDB not found. Please add it first through the /influxdbs endpoint."
                        },
                        404,
                    )
                return e.response, e.status_code
        else:
            # We must have an influxdb object.
            influxdb = args["influxdb"]
            sources = get_datasources_by_url_and_database(
                influxdb["url"], influxdb["database"]
            )
            if not sources:
                return (
                    {
                        "message": "InfluxDB not found. Please add it first through the /influxdbs endpoint."
                    },
                    404,
                )
            influx_db_name = sources[0].name

        # Merge the raw InfluxDB queries with the constructed ones.
        raw_influx_queries: List[RawInfluxDbQuery] = args.get("raw_influx_queries", [])
        if args.get("influx_queries"):
            for query in args["influx_queries"]:
                query: InfluxDbQuery
                raw_influx_queries.append(query.build())

        # Perform some input validation.
        thresholds: List[Threshold] = []
        for threshold in args.get("thresholds", []):
            thresholds.append(jsons.load(threshold, Threshold))

        yaxes: List[YAxis] = []
        for yaxis in args.get("yaxes", [SECONDS_FORMAT]):
            yaxes.append(jsons.load(yaxis, YAxis))

        start = args["start"]
        end = args["end"]
        grafana_graph_params = args.get("grafana_graph_params", {})
        dashboard = create_dashboard(
            args["title"],
            influx_db_name,
            raw_influx_queries,
            start,
            end,
            args.get("timezone"),
            yaxes[:2],
            thresholds,
            grafana_graph_params,
        )

        # Dump to JSON to force a pass through the DashboardEncoder.
        json_dashboard: str = json.dumps(
            dashboard.to_json_data(),
            indent=2,
            sort_keys=True,
            cls=GrafanalibDashboardEncoder,
        )
        # logger.debug(json_dashboard)
        # This we can send to Grafana.
        dashboard_dict = json.loads(json_dashboard)

        try:
            raw_grafana_resp = GRAFANA_API.dashboard.update_dashboard(
                dashboard=dict(dashboard=dashboard_dict, folderId=0, overwrite=True)
            )
        except GrafanaClientError as e:
            return e.response, e.status_code

        try:
            grafana_resp = jsons.load(raw_grafana_resp, GrafanaCreateDashboardResponse)
        except jsons.exceptions.JsonsError:
            logger.exception(f"Error parsing response from Grafana: {raw_grafana_resp}")
            raise

        if grafana_resp.status != "success":
            return {}, 500

        # Example dashboard URL that we get: "/d/IOz7Y0-Wz/testapi"
        # What we want and can embed: "/d-solo/IOz7Y0-Wz/testapi"
        dashboard_embed_url = grafana_resp.url.replace("/d/", "/d-solo/")

        # Build the embed URL for the panel.
        embed_url = f"{EXTERNAL_GRAFANA_URL}{dashboard_embed_url}?panelId={1}"

        # Issue with subpath on production.
        if "grafana/grafana" in embed_url:
            embed_url = embed_url.replace("grafana/grafana", "grafana")

        # Add from and to date, to guarantee the link stays the same even if the dashboard is changed.
        embed_url = f"{embed_url}&from={int(start.timestamp() * 1000)}&to={int(end.timestamp() * 1000)}"
        if args.get("theme"):
            # Add theme.
            embed_url = f"{embed_url}&theme={args['theme']}"

        resp = GraphResponse(
            _links=dict(self=HALLink("/graphs", "Create graph")),
            dashboard_uid=grafana_resp.uid,
            slug=grafana_resp.slug,
            panel_id=1,
            embed_url=embed_url,
        )
        return jsons.dump(resp), 201


@graphs.route("/<string:dashboard_uid>")
class Graph(Resource):
    """
    Resource for approaching a single graph.
    """

    @accepts(dict(name="panel_id", type=int), api=graphs)
    def get(self, dashboard_uid):
        """
        Find the graph to embed based on dashboard UID and panel ID.

        Panel ID could be made optional, if we decide to just return the first panel always.
        """
        args = request.parsed_args

        try:
            raw_grafana_resp = GRAFANA_API.dashboard.get_dashboard(dashboard_uid)
        except GrafanaClientError as e:
            return e.response, e.status_code

        try:
            grafana_resp: GrafanaGetDashboardResponse = jsons.load(
                raw_grafana_resp, GrafanaGetDashboardResponse
            )
        except jsons.exceptions.JsonsError:
            logger.exception(f"Error parsing response from Grafana: {raw_grafana_resp}")
            raise

        meta = grafana_resp.meta
        dashboard = grafana_resp.dashboard
        found_panel = None
        for row in dashboard.rows:
            for panel in row.panels:
                if int(panel.id) == args["panel_id"]:
                    found_panel = panel
                    break

        if found_panel is None:
            return {}, 404

        # Example dashboard URL that we get: "/d/IOz7Y0-Wz/testapi"
        # What we want and can embed: "/d-solo/IOz7Y0-Wz/testapi"
        dashboard_embed_url = meta.url.replace("/d/", "/d-solo/")

        resp = GraphResponse(
            _links=dict(self=HALLink(f"/graphs/{dashboard_uid}")),
            dashboard_uid=grafana_resp.dashboard.uid,
            slug=meta.slug,
            panel_id=int(found_panel.id),
            embed_url=f"{EXTERNAL_GRAFANA_URL}{dashboard_embed_url}?panelId={found_panel.id}",
        )
        return jsons.dump(resp)

    def delete(self, dashboard_uid):
        """
        Delete the dashboard with the specified UID.
        """
        try:
            raw_grafana_resp = GRAFANA_API.dashboard.delete_dashboard(dashboard_uid)
        except GrafanaClientError as e:
            return e.response, e.status_code

        return raw_grafana_resp
