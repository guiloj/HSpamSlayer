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
from typing import Dict, List
import praw
import praw.models
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

###############################################
# FUNCTIONS
###############################################


def ban_configs() -> dict:
    """Grabs the ban configs for a dynamic configuration process.

    Returns:
        dict: All of the configs to be used in **kwargs.
    """
    with open("../config/config.json", "rt", encoding="utf-8") as f:
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


def get_banned_user_subs(user_name: str) -> Dict[str, str]:
    with open("../cache/banned_users.cache.json") as f:
        users = json.loads(f.read())["banned_users"]

    return users.get(user_name, {})


def add_to_banned_users(
    subreddits: List[praw.models.Subreddit], user_name: str
) -> None:
    with open("../cache/banned_users.cache.json") as f:
        current = json.loads(f.read())

    if not current["banned_users"].get(user_name, False):
        current["banned_users"][user_name] = {}

    for sub in subreddits:
        current["banned_users"][user_name][str(sub)] = str(sub)

    with open("../cache/banned_users.cache.json", "wt") as f:
        f.write(json.dumps(current, indent=4))


def ban_user(subreddit: praw.models.Subreddit, user_name: str) -> None:
    """Bans a user from a subreddit, adds any error to `traceback.txt`.

    Args:
        subreddit (praw.models.Subreddit): The subreddit a user should be banned from.
        user_name (str): The userss name.
    """

    options = ban_configs()

    try:
        options["ban_message"] = options["ban_message"].format("r/" + str(subreddit))
    except:
        pass

    subreddit.banned.add(user_name, **options)


def get_banned_subs() -> List[str]:
    with open("../data/subs.json") as f:
        subs = json.loads(f.read())["banned_subs"]
    return subs


def get_modded_subs() -> List[str]:
    with open("../cache/moderated_subreddits.cache.json") as f:
        subs = json.loads(f.read())
    try:
        return [x for x in subs["subreddits"] if str(x) != "u_" + cred["username"]]
    except KeyError:
        std.update_modded_subreddits()
        return get_modded_subs()


def flexible_ban(reddit: praw.reddit.Reddit, user_name: str) -> None:
    """Bans a user only if it was not banned beforehand.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance.
        user_name (str): The user's name.
    """

    user_banned = get_banned_user_subs(user_name)

    subs_banned_in = []

    # ? (@guiloj) we don't use the cache here because creating subs out of strings would be basically the same requests wise
    for subreddit in reddit.user.moderator_subreddits(limit=None):
        if str(subreddit) == "u_" + cred["username"]:
            continue

        if user_banned.get(str(subreddit), False):
            continue

        std.check_ratelimit(reddit, True)

        try:
            ban_user(subreddit, user_name)
            subs_banned_in.append(subreddit)
        except Exception as e:
            std.add_to_traceback(str(e))

    if len(subs_banned_in):
        add_to_banned_users(subs_banned_in, user_name)


def check_moderated_subs(reddit: praw.reddit.Reddit):
    """Checks all blacklisted subs for new posts and bans the authors.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance.
    """
    while 1:
        modded = get_modded_subs()
        for post in reddit.subreddit("+".join(modded)).stream.submissions(
            skip_existing=True, pause_after=10  # skip_existing=True
        ):
            std.check_ratelimit(reddit, True)
            if post is None:
                time.sleep(10)
                continue

            if hasattr(post, "crosspost_parent"):
                if (
                    str(
                        reddit.submission(post.crosspost_parent.split("_")[1]).subreddit
                    )
                    in get_banned_subs()
                ):

                    flexible_ban(reddit, str(post.author))
                    try:
                        post.mod.remove()
                    except Exception as e:
                        std.add_to_traceback(e)

                continue

            if modded != get_modded_subs():
                break


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

    check_moderated_subs(reddit)


if __name__ == "__main__":
    main()
