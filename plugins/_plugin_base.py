#############################
# ======== IMPORTS ======== #
#############################

import os
import sys
from pathlib import Path as p

###########################
# ======== PATHS ======== #
###########################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))

sys.path.append(str(ABSDIR.joinpath("../src")))

##############################
# ======== INSTACES ======== #
##############################

from _stdlib import (
    Blacklist,
    Configs,
    Logger,
    Moderating,
    control_ratelimit,
    gen_reddit_instance,
)

sys.stderr = sys.stdout  # just to keep stderr clean for main.py
logger = Logger(ABSDIR.joinpath("../logs/plugin.name.log"), "NamePlugin")
configs = Configs(ABSDIR.joinpath("../config/plugins/plugin.name.json"))
blacklist = Blacklist()
moderating = Moderating()

##########################
# ======== MAIN ======== #
##########################


def main(type_: str, **kwargs):
    reddit = (
        gen_reddit_instance()
    )  # if you don't plan to use mod privleges pass an _stdlib.Secrets instance to another reddit account.
    #    if you don't plan to use praw at all remove the call to this function.

    # control_ratelimit(reddit) # use this function at least once inside every request heavy loop.

    # Your code here!

    return  # Should't return anything


# -=======================================================================================================================================-
#
# def main(type_, *args, **kwargs) -> None: ...
#   @param type_ : (str) ->
#       what type was called, useful for plugins that accept more then one type, name it "_" if your plugin accepts only one type.
#
#   @param *args : (tuple) ->
#       all positional arguments passed after type, never used by default, only include this if you run a modified version of the bot.
#
#   @param **kwargs : (Dict[str, Any]) ->
#       all non positional arguments passed after type and *args, used by default.
#
# -=======================================================================================================================================-
#
# Every plugin has its main function enclosed inside a thread, but praw is not thread safe!
#
# That's why one needs to use a different reddit instance. Visualize the given scenario.
#
# > # type: "on_invite"
# > def main(_, **kwargs):
# >     for post in kwargs["subreddit"].hot(limit=100):
# >         post.upvote()
#
# The example above will break the reddit instance of whatever thread passed `subreddit` to this plugin. Do something like this instead.
#
# > # type: "on_invite"
# > def main(_, **kwargs):
# >     reddit = gen_reddit_instance()
# >     sub = reddit.subreddit(str(kwargs["subreddit"]))
# >
# >     for post in sub.hot(limit=100):
# >         post.upvote()
#
# This will not interfere with the original reddit instance.
#
# -=======================================================================================================================================-
