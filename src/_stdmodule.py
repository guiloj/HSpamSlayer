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

import praw.reddit
import time
import json
import datetime
import requests
import inspect

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
    return


def send_to_webhook(data: dict) -> bool:
    """Sends dict data as json to the discord webhook.

    Args:
        data (dict): Data to be sent to the webhook.

    Returns:
        bool: True if response is ok False if not.
    """
    with open("../data/secrets.json", "rt", encoding="utf-8") as f:
        webhook = json.loads(f.read())["webhook"]
    response = requests.post(
        webhook,
        json=data,
    )
    return response.ok

# NOTE: this function needs to be very robust, it keeps the bot from getting banned from the api
def check_ratelimit(reddit: "praw.reddit.Reddit", debug: bool = False ):
    """Checks for rate limiting, if `left` < 20 then sleep for `reset_timestamp` - now.

    Args:
        reddit (praw.reddit.Reddit): Reddit object from praw.
    """

    limit: dict[str, int] = reddit.auth.limits

    if debug:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)

        limit_left = limit
        limit_left["left"] = limit["reset_timestamp"] - time.time()
        print(f"{calframe[1][3]}()\n{limit_left}\n")

    if limit["remaining"] < 20:
        # ? (@guiloj) if time left until reset is smaller than 0 than it should not sleep.
        if (timesleep := limit["reset_timestamp"] - time.time()) > 0:
            # * (@guiloj) the `:=` opperator assigns the expression on the left to the
            # * identifier on the right if the `if` is `True`
            time.sleep(timesleep)
        return