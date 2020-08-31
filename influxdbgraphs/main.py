"""
This module is for testing the creation of dashboards in Grafana directly.
"""
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

from grafana_api.grafana_face import GrafanaFace
from grafanalib.core import (
    SECONDS_FORMAT,
    Dashboard,  # YAxes,; YAxis,
    Graph,
    Row,
    Time,
    single_y_axis,
)

from influxdbgraphs.graphing.utils import GrafanalibDashboardEncoder, InfluxDBTarget
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)

GRAFANA_KEY = (
    "eyJrIjoiTU5UYWxHang5bWpSdGdEUmxQTHRNTmlpd1FMNkY5ZVMiLCJuIjoiZWRyIiwiaWQiOjF9"
)
grafana_api = GrafanaFace(auth=GRAFANA_KEY, host="localhost:3007")


dashboard = Dashboard(
    title="simple-test",
    time=Time("2015-01-01", "2019-01-01"),
    timezone="CET",
    rows=[
        Row(
            panels=[
                Graph(
                    title="NEDU Aardgas 2015-2018",
                    dataSource="InfluxDB",
                    targets=[
                        InfluxDBTarget(
                            query='SELECT mean("G1A") FROM "autogen"."nedu_aardgas_2015-2018" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
                            refId="A",
                        ),
                        InfluxDBTarget(
                            query='SELECT mean("G2A") FROM "autogen"."nedu_aardgas_2015-2018" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
                            refId="B",
                        ),
                        InfluxDBTarget(
                            query='SELECT mean("G2A") FROM "autogen"."nedu_aardgas_2015-2018" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
                            refId="C",
                        ),
                        InfluxDBTarget(
                            query='SELECT mean("SPT") FROM "autogen"."nedu_aardgas_2015-2018" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
                            refId="D",
                        ),
                    ],
                    yAxes=single_y_axis(format=SECONDS_FORMAT),
                    # yAxes=YAxes(
                    #     YAxis(format=SECONDS_FORMAT), YAxis(format=SECONDS_FORMAT),
                    # ),
                ),
            ],
        ),
    ],
).auto_panel_ids()


def main():
    # logger.debug(dashboard)
    logger.debug(dashboard.to_json_data())
    json_dashboard = json.dumps(
        dashboard.to_json_data(), indent=4, sort_keys=True, cls=GrafanalibDashboardEncoder
    )
    logger.debug(json_dashboard)
    dashboard_dict = json.loads(json_dashboard)

    dashboards = grafana_api.search.search_dashboards()
    logger.debug(dashboards)
    resp = grafana_api.dashboard.update_dashboard(
        dashboard=dict(dashboard=dashboard_dict, folderId=0, overwrite=True)
    )
    logger.debug(resp)


if __name__ == "__main__":
    main()
