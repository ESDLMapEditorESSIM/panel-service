"""
Custom queries for Grafana. Because the Grafana API is a bit limited, we usually
extend them through postprocessing in Python.
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

from typing import List, Optional

import jsons

from influxdbgraphs.grafana.config import GRAFANA_API
from influxdbgraphs.grafana.types import GrafanaDatasource


def get_datasources_by_url_and_database(
    url: Optional[str], database: Optional[str]
) -> List[GrafanaDatasource]:
    """
    Get all datasources and optionally filter on URL and database name.
    """
    raw_sources: List = GRAFANA_API.datasource.list_datasources()
    # Parse the source as a GrafanaDataSource, to allow easier handling of the data.
    sources: List[GrafanaDatasource] = [
        jsons.load(raw_source, GrafanaDatasource)
        for raw_source in raw_sources
        if raw_source["type"] == "influxdb"
    ]

    # Filter out datasources based on input parameters.
    if url:
        sources = [source for source in sources if source.url == url]
    if database:
        sources = [source for source in sources if source.database == database]

    return sources
