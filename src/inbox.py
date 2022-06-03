#############################
# ======== IMPORTS ======== #
#############################

import os
import time
from pathlib import Path as p

import praw
import praw.exceptions
import praw.models
import prawcore

import _stdlib as std
from _plugin_loader import PluginLoader

############################
# ======== PATHS ========= #
############################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))


###############################
# ======== INSTANCES ======== #
###############################


configs = std.Configs()
logger = std.Logger(ABSDIR.joinpath("../logs/inbox.log"), "Inbox")
moderating = std.Moderating()
blacklist = std.Blacklist()
plugins = PluginLoader(["on_invite"])


###############################
# ======== FUNCTIONS ======== #
###############################


def send_message_to_subreddit(subreddit: praw.models.Subreddit) -> None:
    """Send message to a given subreddit.

    Args:
        subreddit (praw.models.Subreddit)
    """
    options = configs.get("on_invite").unwrap()

    if not options["send_message"]:
        return

    message = options["message_content"]

    message["message"] = message["message"] % {"subreddit": subreddit}

    try:
        # https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html?highlight=Subreddit.message#praw.models.Subreddit.message
        subreddit.message(**message)
    except Exception as e:
        logger.error("Sending message to r/%s failed: %s" % (subreddit, e))


def can_make_sticky_post(subreddit: praw.models.Subreddit) -> bool:
    """Check if the sticky pool is full for a given subreddit.

    Args:
        subreddit (praw.models.Subreddit)

    Returns: bool
    """
    # check if the first two posts in hot are sticky or not
    return sum(1 for post in subreddit.hot(limit=2) if post.stickied) < 2


def make_sticky_announcement(subreddit: praw.models.Subreddit) -> None:
    """Make a sticky announcement to a given subreddit.

    Args:
        subreddit (praw.models.Subreddit)
    """

    options = configs.get("on_invite").unwrap()

    if (not options["make_announcement"]) or (not can_make_sticky_post(subreddit)):
        return

    content = options["announcement_content"]

    try:
        submission = subreddit.submit(
            **content
        )  # https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit

        # https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.approve
        submission.mod.approve()

        # https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.distinguish
        submission.mod.distinguish(how="yes")

        # https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.sticky
        submission.mod.sticky(state=True)
    except Exception as e:
        logger.error("Making announcement to r/%s failed: %s" % (subreddit, e))


def check_inbox(reddit: praw.reddit.Reddit) -> None:
    """Check for messages in the bot's inbox.

    Args:
        reddit (praw.reddit.Reddit)
    """

    inbox = reddit.inbox.unread(limit=None)  # type: ignore

    for unread in inbox:
        std.control_ratelimit(reddit)

        if isinstance(unread, praw.models.SubredditMessage):

            if str(unread.subreddit).lower() in (
                [
                    x.lower()
                    for x in configs.get("on_invite", "ignore").unwrap_or_default([])
                ]
                + blacklist.get()
            ):
                continue

            try:
                # https://praw.readthedocs.io/en/stable/code_overview/other/subredditmoderation.html?highlight=accept_invite#praw.models.reddit.subreddit.SubredditModeration.accept_invite
                reddit.subreddit(str(unread.subreddit)).mod.accept_invite()

                plugins.on("on_invite", subreddit=str(unread.subreddit))

                time.sleep(1)  # sleep just to be 100% sure <- probably stupid

                send_message_to_subreddit(unread.subreddit)
                make_sticky_announcement(unread.subreddit)
            except (
                praw.exceptions.RedditAPIException,
                prawcore.exceptions.NotFound,
            ) as e:
                logger.warning(
                    "Accepting invite from r/%s failed: %s" % (unread.subreddit, e)
                )

        unread.mark_read()

    moderating.update(reddit)
    plugins.check()
    time.sleep(120)


##########################
# ======== MAIN ======== #
##########################


def main():
    """Main entry point.

    Raises:
        e: Unhandled exception.
    """

    error = BaseException("Exception was not registered!")

    reddit = std.gen_reddit_instance()

    while 1:
        try:
            check_inbox(reddit)
        except KeyboardInterrupt:
            break
        except BaseException as e:
            if std.catch(e, logger):
                error = e
                break
            continue

    raise error


if __name__ == "__main__":
    main()
