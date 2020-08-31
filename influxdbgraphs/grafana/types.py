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
from typing import List

from grafana_api.grafana_face import GrafanaFace


@dataclass
class GrafanaCreateDashboardResponse:
    """Response class for Grafana's create dashboard call."""

    id: int
    slug: str
    status: str  # success
    uid: str
    url: str
    version: int


@dataclass
class GrafanaCreateDatasourceResponse:
    """Response class for Grafana's create datasource call."""

    id: int
    message: str
    name: str


@dataclass
class GrafanaDatasource:
    """Grafana API data source representation."""

    name: str
    url: str
    database: str
    type: str


@dataclass
class GrafanaTarget:
    """
    The grafana API representation of a target.
    """

    query: str


@dataclass
class GrafanaDashboardPanel:
    """
    The grafana API representation of a dashboard panel.
    """

    id: str
    datasource: str
    targets: List[GrafanaTarget]


@dataclass
class GrafanaDashboardRow:
    """
    The grafana API representation of a dashboard row.
    """

    panels: List[GrafanaDashboardPanel]


@dataclass
class GrafanaDashboard:
    """
    The grafana API representation of a dashboard.
    """

    uid: str
    rows: List[GrafanaDashboardRow]


@dataclass
class GrafanaMeta:
    slug: str
    url: str


@dataclass
class GrafanaGetDashboardResponse:
    """
    Response class for Grafana's get dashboard call. Only contains those fields
    that we need.
    """

    meta: GrafanaMeta
    dashboard: GrafanaDashboard
