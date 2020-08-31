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

import logging


def get_logger(name):
    logger = logging.getLogger(name)

    # if is_production():
    #     logger.setLevel(logging.INFO)
    # else:
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(levelname).3s/%(asctime)s/%(name)s - %(message)s")
    )
    logger.addHandler(handler)

    return logger
