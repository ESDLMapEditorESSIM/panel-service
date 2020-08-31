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

from datetime import datetime
from typing import Dict, List

import attr
from grafanalib.core import Dashboard, Graph, Row, Time, YAxes, YAxis

from influxdbgraphs.api.types import RawInfluxDbQuery
from influxdbgraphs.grafana.grafanalib_types import (
    InfluxDBTarget,
    SeriesOverride,
    Threshold,
)
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)


@attr.s
class CustomGraph(Graph):
    """
    Our own Graph class, that extends the grafanalib Graph to add fields we need.
    """

    thresholds = attr.ib(attr.Factory(list))

    def to_json_data(self):
        data = super().to_json_data()
        data["thresholds"] = self.thresholds
        return data


def create_dashboard(
    title: str,
    datasource_name: str,
    queries: List[RawInfluxDbQuery],
    start: datetime,
    end: datetime,
    timezone: str,
    yaxe_types: List[YAxis],
    thresholds: List[Threshold],
    grafana_graph_params: Dict[str, any],
) -> Dashboard:
    """
    Create a dashboard object that can be serialized to JSON and sent to Grafana.
    """
    targets = []
    series_overrides = []
    for query in queries:
        targets.append(InfluxDBTarget(query=query.query, alias=query.alias))
        if query.yaxis == "right":
            series_overrides.append(SeriesOverride(alias=query.alias, yaxis=2))

    left = yaxe_types[0]
    right = yaxe_types[1] if len(yaxe_types) > 1 else None
    yaxes = YAxes(left, right) if right else YAxes(left=left)

    return Dashboard(
        title=title,
        time=Time(start.isoformat(), end.isoformat()),
        timezone=timezone,
        rows=[
            Row(
                panels=[
                    CustomGraph(
                        title=title,
                        dataSource=datasource_name,
                        targets=targets,
                        thresholds=thresholds,
                        seriesOverrides=series_overrides,
                        yAxes=yaxes,
                        transparent=True,
                        **grafana_graph_params,
                    ),
                ],
            ),
        ],
    ).auto_panel_ids()
