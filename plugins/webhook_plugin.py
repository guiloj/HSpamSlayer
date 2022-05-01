#############################
# ======== IMPORTS ======== #
#############################

import json
import os
import sys
from pathlib import Path as p
from typing import Dict

import requests

###########################
# ======== PATHS ======== #
###########################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))

sys.path.append(str(ABSDIR.joinpath("../src")))

##############################
# ======== INSTACES ======== #
##############################

from _stdlib import Configs, Logger

sys.stderr = sys.stdout  # just to keep stderr clean for main.py
logger = Logger(ABSDIR.joinpath("../logs/webhook.log"), "WebhookPlugin")
configs = Configs(ABSDIR.joinpath("../config/plugins/webhook.json"))

###############################
# ======== FUNCTIONS ======== #
###############################


def format_webhook(webhook: Dict[str, "str | bool | list"], **kwargs) -> dict:
    """Format every string inside a webhook dict.

    Args:
        webhook (Dict[str, "str | bool | list"]): The webhook dict.

    Returns:
        dict: Formatted dict.
    """
    # XXX: I'm so sorry
    return json.loads(json.dumps(webhook) % kwargs)
    # so so sorry


def send_to_webhook(data: dict) -> int:
    """Send json data to a webhook.

    Args:
        data (dict): Json data in a dict format.

    Returns:
        int: Status code.
    """
    webhook = configs.get("webhook")
    response = requests.post(
        webhook,
        json=data,
    )

    return response.status_code


##########################
# ======== MAIN ======== #
##########################


def main(type_: str, **kwargs):
    message = format_webhook(configs.get("messages", type_), **kwargs)
    response = send_to_webhook(message)

    # 204 is the default response for a discord webhook - https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204
    if response != 204:
        logger.error("Webhook for type %s got status code %d!" % (type_, response))

    return
