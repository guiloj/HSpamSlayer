"""
# src/mod_posts.py

Accepts all mod invites.

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

import os
import json
import praw
import praw.models
from praw.models.reddit.subreddit import SubredditRedditorFlairTemplates 
import _stdmodule as std
import time 

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

with open("../data/subs.json") as f:
    subs = json.loads(f.read())

###############################################
# FUNCTIONS
###############################################

def ban_configs() -> dict:
    """Grabs the ban configs for a dynamic configuration process.

    Returns:
        dict: All of the configs to be used in **kwargs.
    """
    with open("../config/config.json") as f:
        configs = json.loads(f.read())["action"]

    options = {}

    for conf in ("ban_message", "ban_reason", "note", "duration"):

        try:
            if configs[conf] in ("", None):
                continue
        except KeyError:
            continue

        options[conf] = configs[conf]

    return options

def ban_user(subreddit: praw.models.Subreddit, user_name: str) -> None:
    """Bans a user from a subreddit, adds any error to `traceback.txt`.

    Args:
        subreddit (praw.models.Subreddit): The subreddit a user should be banned from.
        user_name (str): The userss name.
    """

    options = ban_configs()

    try:
        options["ban_message"].format("r/"+str(subreddit))
    except:
        pass

    try:
        subreddit.banned.add("NAME", **ban_configs())
    except Exception as err:
        std.add_to_traceback(str(err))

def sub_banned(subreddit: praw.models.Subreddit, user_name: str) -> bool:
    """Checks if a given user was already banned from a subreddit, adds any error to `traceback.txt`.

    Args:
        subreddit (praw.models.Subreddit): The subreddit to be checked.
        user_name (str): The user's name.

    Returns:
        bool: If the user was already banned or not.
    """
    try:
        return any(str(banned) == user_name for banned in subreddit.banned())
    except Exception as err:
        std.add_to_traceback(str(err))
        return False

def flexible_ban(reddit: praw.reddit.Reddit, user_name: str) -> None:
    """Bans a user only if it was not banned beforehand.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance.
        user_name (str): The user's name.
    """
    for subreddit in reddit.user.moderator_subreddits(limit=None):
        if str(subreddit) == "u_" + cred["username"]:
            continue

        std.check_ratelimit(reddit)

        if not sub_banned(subreddit, user_name):
            ban_user(subreddit, user_name)


def check_blacklisted_subs(reddit: praw.reddit.Reddit):
    """Checks all blacklisted subs for new posts and bans the authors.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance.
    """
    for post in reddit.subreddit("+".join(subs["banned_subs"])).stream.submissions(skip_existing=True, pause_after=10):
        std.check_ratelimit(reddit)
        
        if post is None:
            time.sleep(10)

        flexible_ban(reddit, str(post.author))

###############################################
# MAIN
###############################################

def main():
    reddit = praw.Reddit(
        client_id=cred["id"],
        client_secret=cred["secret"],
        password=cred["password"],
        user_agent=cred["agent"],
        username=cred["username"],
    )
    check_blacklisted_subs(reddit)


if __name__ == "__main__":
    main()

