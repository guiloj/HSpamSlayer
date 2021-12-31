"""
# src/_stdmodule.py

Standard module for all functions that are reused by multiple scripts.

    @comments
    '?': why is this code here?
    '*': what is the code doing 
    '!': warning!
    'NOTE': a note

    @dev
    'TODO': todo notes
    'FIXME': needs fixing
    'XXX': makes no sense but works
"""

###############################################
# IMPORTS
###############################################

from typing import Any, List
import praw
import time
import json
import datetime
import requests
import inspect
import os
import logging

###############################################
# FILE MANAGEMENT
###############################################

# ? (@guiloj) correctly finds the path to the main.py file to
# ? manage the modules and libs

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

# * (@guiloj) get app secrets from the `../data/secrets.json` file
with open("../data/secrets.json") as f:
    cred = json.loads(f.read())

###############################################
# GLOBALS
##############################################

client_id: str = cred["id"]
client_secret: str = cred["secret"]
password: str = cred["password"]
user_agent: str = cred["agent"]
username: str = cred["username"]
logger: logging.Logger
LIMIT = 10

###############################################
# CLASSES
##############################################

# https://stackoverflow.com/a/56944256 < (@guiloj) credit is important kids
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
        "NORMAL": format,
    }

    def format(self, record):
        log_fmt = (
            self.FORMATS.get(record.levelno)
            if os.name != "nt"
            else self.FORMATS.get("NORMAL")
        )
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create logger with 'spam_application'
logger = logging.getLogger(username)
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

###############################################
# FUNCTIONS
###############################################


def add_to_traceback(message: str) -> None:
    """Adds a message to `traceback.txt`.

    Args:
        message (str): Message to be displayed.

    e.g.
    ```txt
    in: [function]()
    time: 2020-07-15 14:30:26.159446
    message: [message]

    ```
    """

    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)

    with open("../traceback.txt", "at", encoding="utf-8") as f:
        f.write(
            f"in: {calframe[1][3]}()\ntime: {datetime.datetime.now()}\nmessage: "
            + message
            + "\n\n"
        )
    logger.error(message)
    return


def config(config: str) -> Any:
    with open("../config/config.json", "rt", encoding="utf-8") as f:
        configs = json.loads(f.read())[config]
    return configs


def send_to_webhook(data: dict, use_alt: str = "") -> bool:
    """Sends dict data as json to the discord webhook.

    Args:
        data (dict): Data to be sent to the webhook.

    Returns:
        bool: True if response is ok False if not.
    """
    with open("../data/secrets.json", "rt", encoding="utf-8") as f:
        webhook = json.loads(f.read())["webhook" + use_alt]
    response = requests.post(
        webhook,
        json=data,
    )
    return response.ok


# NOTE: this function needs to be very robust, it keeps the bot from getting banned from the api
def check_ratelimit(reddit: "praw.reddit.Reddit", debug: bool = False):
    """Checks for rate limiting, if `left` < 20 then sleep for `reset_timestamp` - now.

    Args:
        reddit (praw.reddit.Reddit): Reddit object from praw.
    """

    limit: dict[str, int] = reddit.auth.limits

    if debug:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        requests_left = limit["remaining"]
        time_left = limit["reset_timestamp"] - time.time()
        logger.debug(f"{calframe[1][3]}() => {requests_left}, {int(time_left)}s")

    if limit["remaining"] < 20:
        # ? (@guiloj) if time left until reset is smaller than 0 than it should not sleep.
        if (timesleep := limit["reset_timestamp"] - time.time()) > 0:
            # * (@guiloj) the `:=` opperator assigns the expression on the left to the
            # * identifier on the right if the `if` is `True`
            time.sleep(timesleep)
        return


def gen_reddit_instance() -> praw.Reddit:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        user_agent=user_agent,
        username=username,
    )
    reddit.validate_on_submit = True
    return reddit


def update_modded_subreddits(reddit: praw.reddit.Reddit) -> None:
    """Updates the cache of modded subreddits to avoid unnecessary requests.

    Args:
        reddit (praw.reddit.Reddit): The Reddit instance.
    """
    mod_dict = [str(x) for x in reddit.user.moderator_subreddits(limit=None)]
    with open("../cache/moderated_subreddits.cache.json") as f:
        mod_subs = json.loads(f.read())

    mod_subs["subreddits"] = mod_dict

    with open("../cache/moderated_subreddits.cache.json", "wt") as f:
        f.write(json.dumps(mod_subs, indent=4))
