"""
# src/accept_invites.py

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
import time
import _stdmodule as std
from praw.models import SubredditMessage
import prawcore

###############################################
# FILE MANAGEMENT
###############################################

# ? correctly finds the path to the main.py file to
# ? manage the modules and libs

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

# * (@guiloj) get app secrets from the `../data/secrets.json` file
with open("../data/secrets.json") as f:
    cred = json.loads(f.read())

###############################################
# CLASSES
###############################################

###############################################
# FUNCTIONS
###############################################

def message_configs() -> dict:
    """Grabs the message configs for a dynamic configuration process.

    Returns:
        dict: All of the configs to be used in **kwargs
    """
    with open("../config/config.json", "rt", encoding="utf-8") as f:
        configs = json.loads(f.read())
    
    return configs["message"]

def send_message(redditor: praw.models.Redditor, subreddit: praw.models.Subreddit) -> None:
    """Sends a message to the mod that invited the bot as soon as a invite is accepted.

    Args:
        redditor (praw.models.Redditor): The redditor object for the mod.
        subreddit (praw.models.Subreddit): The subreddit to format into the message.
    """
    options = message_configs()

    try:
        options["message"] = options["message"].format("r/"+str(subreddit))
    except:
        pass

    try:
        redditor.message(**options)
    except Exception as e:
        std.add_to_traceback(str(e))

def auto_accept_invites(reddit: "praw.reddit.Reddit"):
    """Auto accepts all moderator invites.

    Args:
        reddit (praw.reddit.Reddit): The Reddit instance.
    """
    while True:
        for unread in reddit.inbox.unread(limit=None):
            std.check_ratelimit(reddit)

            if isinstance(unread, SubredditMessage):
                try:
                    reddit.subreddit(str(unread.subreddit)).mod.accept_invite()
                    send_message(unread.author, unread.subreddit)
                except (praw.exceptions.RedditAPIException, prawcore.exceptions.NotFound):
                    # ? (@guiloj) if the invite is invalid the bot does not break
                    unread.mark_read()
                    continue
                
                except Exception as e:
                    std.add_to_traceback(e)

                unread.mark_read()
        time.sleep(120)



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
    auto_accept_invites(reddit)



if __name__ == "__main__":
    main()
