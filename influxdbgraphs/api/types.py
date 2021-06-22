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

import textwrap
from dataclasses import dataclass
from typing import List, Optional

import jsons
from grafanalib.core import (DAYS_FORMAT, HOURS_FORMAT, MINUTES_FORMAT,
                             SECONDS_FORMAT)

NONE_FORMAT = "none"

JOULE_FORMAT = "joule"

WATTHOUR_FORMAT = "watth"
WATT_FORMAT = "watt"
KWATT_FORMAT = "kwatt"
KWATTHOUR_FORMAT = "kwatth"

VOLT_FORMAT = "volt"

BAR_FORMAT = "pressurebar"
PSI_FORMAT = "pressurepsi"

CELSIUS_FORMAT = "celsius"
KELVIN_FORMAT = "kelvin"
GRAM_FORMAT = "massg"

EUR_FORMAT = "currencyEUR"
USD_FORMAT = "currencyUSD"

METER_FORMAT = "lengthm"
SQUARE_METER_FORMAT = "areaM2"
CUBIC_METER_FORMAT = "m3"

LITRE_FORMAT = "litre"

PERCENT_FORMAT = "percent"
VOLT_AMPERE_FORMAT = "voltamp"


YAXIS_TYPES = [
    NONE_FORMAT,
    JOULE_FORMAT,
    WATTHOUR_FORMAT,
    WATT_FORMAT,
    KWATTHOUR_FORMAT,
    KWATT_FORMAT,
    VOLT_FORMAT,
    BAR_FORMAT,
    PSI_FORMAT,
    CELSIUS_FORMAT,
    KELVIN_FORMAT,
    GRAM_FORMAT,
    EUR_FORMAT,
    USD_FORMAT,
    SECONDS_FORMAT,
    MINUTES_FORMAT,
    HOURS_FORMAT,
    DAYS_FORMAT,
    METER_FORMAT,
    SQUARE_METER_FORMAT,
    CUBIC_METER_FORMAT,
    LITRE_FORMAT,
    PERCENT_FORMAT,
    VOLT_AMPERE_FORMAT,
]

@dataclass
class RawInfluxDbQuery:
    """
    A representation of a raw InfluxDB query.
    """

    query: str
    alias: Optional[str]
    yaxis: Optional[str]

    @classmethod
    def argtype(cls, value):
        """
        Type to add as request argument in flask restplus.
        """
        return jsons.load(value, cls)


@dataclass
class InfluxDbQuery:
    """
    A representation of (some of the) components of an InfluxDB query.
    """

    field: str
    measurement: str
    alias: Optional[str]
    yaxis: Optional[str]
    filters: Optional[List[str]]
    group_by_time: Optional[str] = "$__interval"
    fill: Optional[str] = "null"
    function: Optional[str] = "mean"

    def build(self) -> RawInfluxDbQuery:
        filters = self.filters or []
        query = build_raw_influx_query(
            self.field, self.measurement, self.function, filters, self.group_by_time, self.fill
        )
        alias = self.alias if self.alias else f"{self.measurement}.{self.function}"
        return RawInfluxDbQuery(query=query, alias=alias, yaxis=self.yaxis)

    @classmethod
    def argtype(cls, value):
        """
        Type to add as request argument in flask restplus.
        """
        return jsons.load(value, cls)


def build_raw_influx_query(field, measurement, function, filters, group_by_time="$__interval", fill="null") -> str:
    """
    Build a raw InfluxDB query.
    """
    copied_filters = filters.copy()
    copied_filters.append("$timeFilter")
    string_filters = " AND ".join(copied_filters)
    query = f"""
    SELECT {function}("{field}")
    FROM "{measurement}"
    WHERE {string_filters} GROUP BY time({group_by_time}) fill({fill})
    """

    return textwrap.dedent(query).replace("\n", " ").strip()
