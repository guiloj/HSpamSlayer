#############################
# ======== IMPORTS ======== #
#############################

import time
from pathlib import Path as p

import praw
import praw.exceptions
import praw.models
import prawcore

import _rust_types as rt
import _stdlib as std
import _sub_configs as sconf
from _plugin_loader import PluginLoader

############################
# ======== PATHS ========= #
############################


ABSDIR = p(__file__).parent.absolute()


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


def reply_to(message: praw.models.ModmailConversation, body: str) -> int:
    """Reply to a subreddit message, return 1 if anything went wrong.

    Args:
        message (praw.models.SubredditMessage): Message to reply to.
        body (str): Reply body.

    Returns:
        int: Exit code like.
    """
    try:
        message.reply(body=body)
        return 0
    except prawcore.exceptions.Forbidden as e:
        logger.critical(
            "Replying to %s from r/%s failed: %s" % (message, message.subreddit, e)
        )
        return 1


def check_inbox(reddit: praw.reddit.Reddit) -> None:
    # sourcery skip: low-code-quality, merge-nested-ifs
    """Check for messages in the bot's inbox.

    Args:
        reddit (praw.reddit.Reddit)
    """

    discussions = reddit.subreddit("all").mod.stream.modmail_conversations(
        state="mod", skip_existing=True, pause_after=-1
    )

    while 1:

        for unread in reddit.inbox.unread(limit=None):
            std.control_ratelimit(reddit)

            if isinstance(unread, praw.models.SubredditMessage):

                if str(unread.subreddit).lower() not in (
                    [
                        x.lower()
                        for x in configs.get("on_invite", "ignore").unwrap_or([])
                    ]
                    + blacklist.get()
                ):
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
                            "Accepting invite from r/%s failed: %s"
                            % (unread.subreddit, e)
                        )

            unread.mark_read()

        for discussion in discussions:
            if discussion is None:
                break

            if isinstance(discussion, praw.models.ModmailConversation):
                if str(discussion.subject).lower().strip() == "set config":

                    if not isinstance(discussion.owner, praw.models.Subreddit):
                        reply_to(
                            discussion,
                            "It seems like you have sent this message from your account instead of from a subreddit, please try again!",
                        )
                    elif not discussion.is_internal:
                        reply_to(
                            discussion,
                            "It seems like you're not part of our sub network yet! Please send the bot an invite and wait until you receive a confirmation message.",
                        )
                    else:
                        err = sconf.set_sub_config(
                            str(discussion.messages[0].body_markdown),
                            str(discussion.owner),
                        )

                        if isinstance(err, rt.Some):
                            reply_to(discussion, err.unwrap())
                        else:
                            reply_to(discussion, "Your sub configs are now set!")

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
            code, call, msg = std.catch(e, logger)
            call(msg)
            if code:
                error = e
                break
            continue

    raise error


if __name__ == "__main__":
    main()
