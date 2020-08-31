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

class Config(object):
    """Generic config for all environments."""

    BUNDLE_ERRORS = True
    """Bundle all data validation errors from flask-restplus."""


class ProdConfig(Config):
    ENV = "prod"


class DevConfig(Config):
    ENV = "dev"
    DEBUG = True


class TestConfig(Config):
    ENV = "test"
    DEBUG = True
