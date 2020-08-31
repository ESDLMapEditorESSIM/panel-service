"""
Types for the Grafana API, compatible with grafanalib. Should be contributed back to grafanalib.
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

import attr
import jsons
from attr.validators import instance_of
from grafanalib.core import TIME_SERIES_TARGET_FORMAT


@attr.s
class InfluxDBTarget(object):
    """
    Metric to show.
    :param target: Graphite way to select data
    """

    query = attr.ib()
    format = attr.ib(default=TIME_SERIES_TARGET_FORMAT)
    alias = attr.ib(default="")
    measurement = attr.ib(default="")
    rawQuery = True

    def to_json_data(self):
        return {
            "query": self.query,
            "resultFormat": self.format,
            "alias": self.alias,
            "measurement": self.measurement,
            "rawQuery": self.rawQuery,
        }


@attr.s
class Threshold(object):
    value = attr.ib()
    op = attr.ib(default="gt")
    yaxis = attr.ib(default="left")
    color_mode = attr.ib(default="warning")
    line = attr.ib(default=True, validator=instance_of(bool))

    @classmethod
    def argtype(cls, value):
        return jsons.load(value, cls)

    def to_json_data(self):
        return {
            "value": self.value,
            "op": self.op,
            "yaxis": self.yaxis,
            "colorMode": self.color_mode,
            "line": self.line,
        }


@attr.s
class SeriesOverride(object):
    alias = attr.ib()
    bars = attr.ib(default=False)
    lines = attr.ib(default=True)
    yaxis = attr.ib(default=1)
    color = attr.ib(default=None)

    def to_json_data(self):
        return {
            "alias": self.alias,
            "bars": self.bars,
            "lines": self.lines,
            "yaxis": self.yaxis,
            "color": self.color,
        }


class GrafanalibDashboardEncoder(json.JSONEncoder):
    """
    Encode grafanalib dashboard objects, as they do not all encode properly
    through the standard encoder. This uses the custom to_json_data method if they
    have it.
    """

    def default(self, obj):
        to_json_data = getattr(obj, "to_json_data", None)
        if to_json_data:
            return to_json_data()
        return json.JSONEncoder.default(self, obj)
