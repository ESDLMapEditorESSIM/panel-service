#!/usr/bin/env python

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

import os
from time import strftime

from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from influxdbgraphs.api import api
from influxdbgraphs.api.settings import DevConfig
from influxdbgraphs.log import get_logger

logger = get_logger(__name__)


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. influxdbgraphs.api.settings.ProdConfig
    """
    logger.info("Setting up InfluxDB Graphs app.")

    app = Flask(__name__)
    CORS(app)
    app.config.from_object(object_name)
    if app.config["ENV"] == DevConfig.ENV:
        import ptvsd

        ptvsd.enable_attach()

    app.wsgi_app = ProxyFix(app.wsgi_app)

    api.init_app(app)

    logger.info("Finished setting up InfluxDB Graphs app.")

    return app


env = os.environ.get("ENV", "prod")
app = create_app("influxdbgraphs.api.settings.%sConfig" % env.capitalize())


@app.after_request
def after_request(response):
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    logger.error(
        "%s %s %s %s %s %s",
        timestamp,
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
    )
    return response
