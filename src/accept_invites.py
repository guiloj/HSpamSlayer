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
import praw.exceptions
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


def send_message(subreddit: praw.models.Subreddit) -> None:
    """Sends a message to the mods of the invited subreddit as soon as a invite is accepted.

    Args:
        subreddit (praw.models.Subreddit): The subreddit in question, can also be formated into the message.
    """
    options = message_configs()

    try:
        options["message"] = options["message"].format("r/" + str(subreddit))
    except:
        pass

    try:
        subreddit.message(**options)
    except Exception as e:
        std.add_to_traceback(str(e))


def can_sticky(subreddit: praw.models.Subreddit) -> bool:
    return sum(1 for post in subreddit.hot(limit=2) if post.stickied) < 2


def make_announcement(subreddit: praw.models.Subreddit):
    try:
        if can_sticky(subreddit):
            submission: praw.models.Submission = subreddit.submit(
                **std.config("announcement")
            )
            submission.mod.approve()
            submission.mod.distinguish(how="yes")
            submission.mod.sticky(state=True)
    except Exception as e:
        std.add_to_traceback(str(e))


def auto_accept_invites(reddit: "praw.reddit.Reddit"):
    """Auto accepts all moderator invites.

    Args:
        reddit (praw.reddit.Reddit): The Reddit instance.
    """
    while True:
        try:
            for unread in reddit.inbox.unread(limit=None):
                std.check_ratelimit(reddit, True)

                if isinstance(unread, SubredditMessage):
                    try:
                        reddit.subreddit(str(unread.subreddit)).mod.accept_invite()
                        if std.config("webhook"):
                            std.send_to_webhook(
                                {
                                    "content": "<@235950285569130496>",
                                    "embeds": [
                                        {
                                            "author": {
                                                "name": "HSpamSlayer",
                                                "url": "https://www.reddit.com/user/HSpamSlayer",
                                                "icon_url": "https://styles.redditmedia.com/t5_5czm0s/styles/profileIcon_aaqhxf65yj081.jpeg?width=256&height=256&crop=256:256,smart&s=0709aa35f8ca40351ed717448529deba63cec82e",
                                            },
                                            "title": f"Invite from {unread.subreddit} accepted!",
                                            "url": f"https://www.reddit.com/r/{unread.subreddit}",
                                        }
                                    ],
                                },
                                "2",
                            )
                        make_announcement(unread.subreddit)
                        send_message(unread.subreddit)
                    except (
                        praw.exceptions.RedditAPIException,
                        prawcore.exceptions.NotFound,
                    ) as e:
                        # ? (@guiloj) if the invite is invalid the bot does not break
                        unread.mark_read()
                        std.add_to_traceback(str(e))
                        continue

                    except Exception as e:
                        std.add_to_traceback(str(e))
                unread.mark_read()

            # ? (@guiloj) update the modded subreddits every two minutes and after any invite accept.
            std.update_modded_subreddits(reddit)
            time.sleep(120)
        except prawcore.exceptions.ServerError as e:
            std.add_to_traceback("Reddit API is down: " + str(e))
            time.sleep(60)
        except prawcore.exceptions.Forbidden as e:
            std.logger.critical(str(e))
            time.sleep(60)


###############################################
# MAIN
###############################################


def main():
    reddit = std.gen_reddit_instance()
    auto_accept_invites(reddit)


if __name__ == "__main__":
    main()
