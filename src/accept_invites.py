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


def send_message(subreddit: praw.models.Subreddit) -> None:
    """Sends a message to the mods of the invited subreddit as soon as a invite is accepted.

    Args:
        subreddit (praw.models.Subreddit): The subreddit in question, can also be formated into the message.
    """
    options = std.config("message")

    try:
        options["message"] = options["message"].format("r/" + str(subreddit))
    except:
        pass

    try:
        subreddit.message(**options)
    except Exception as e:
        std.add_to_traceback(str(e))


def can_sticky(subreddit: praw.models.Subreddit) -> bool:
    """If the limit of sticky posts for a subreddit is reached.

    Args:
        subreddit (praw.models.Subreddit): The given subreddit.

    Returns:
        bool: If the limit was reached or not.
    """
    return sum(1 for post in subreddit.hot(limit=2) if post.stickied) < 2


def make_announcement(subreddit: praw.models.Subreddit):
    """Make an announcement to a given subreddit

    Args:
        subreddit (praw.models.Subreddit): The subreddit to make an announcement to.
    """
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
                    if (
                        str(unread.subreddit).lower()
                        in [x.lower() for x in std.config("no_invite")]
                        + std.banned_subs()
                    ):
                        unread.mark_read()
                        continue

                    try:
                        reddit.subreddit(str(unread.subreddit)).mod.accept_invite()
                        time.sleep(1)  # sleep just to be 100% sure
                        send_message(unread.subreddit)
                        make_announcement(unread.subreddit)

                        if std.config("webhooks")["use"]:
                            message = std.format_webhook(
                                std.config("webhooks")["invite_accept"],
                                sub=str(unread.subreddit),
                            )
                            std.send_to_webhook(message)

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
