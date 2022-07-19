#############################
# ======== IMPORTS ======== #
#############################

import pickle
import time
from pathlib import Path as p
from typing import Dict, List

import praw
import praw.models

import _stdlib as std
from _plugin_loader import PluginLoader
from _threading_manager import BanQueue, Queue, ThreadManager, uuid

###########################
# ======== PATHS ======== #
###########################


ABSDIR = p(__file__).parent.absolute()
ban_cache_path = ABSDIR.joinpath("../cache/ban.queue")

###############################
# ======== INSTANCES ======== #
###############################


configs = std.Configs()
blacklist = std.Blacklist()
logger = std.Logger(ABSDIR.joinpath("../logs/submissions.log"), "Submissions")
moderating = std.Moderating()
plugins = PluginLoader(["on_bad_post"])
banned = std.Banned()


if ban_cache_path.exists():
    with open(ban_cache_path, "rb") as f:
        ban_queue = pickle.load(f)
else:
    ban_queue = BanQueue()


###############################
# ======== FUNCTIONS ======== #
###############################


def ban_user(subreddit: praw.models.Subreddit, user_name: str):
    """Ban user from a subreddit.

    Args:
        subreddit (praw.models.Subreddit): The subreddit to ban a user from.
        user_name (str): The reddit username of the user to ban.
    """
    options = configs.get_both("on_bad_post", "ban_opts", sub=str(subreddit)).unwrap()

    options["ban_message"] = options["ban_message"] % {"subreddit": subreddit}

    try:
        # https://praw.readthedocs.io/en/stable/code_overview/other/subredditrelationship.html#praw.models.reddit.subreddit.SubredditRelationship.add
        # https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html?highlight=banned.add#praw.models.Subreddit.banned
        # https://www.reddit.com/dev/api/#POST_api_friend
        # https://www.reddit.com/r/redditdev/comments/6vlvfb/comment/dm1i9a4/
        subreddit.banned.add(user_name, **options)
    except Exception as e:
        logger.error("Banning u/%s from r/%s failed : %s" % (user_name, subreddit, e))


def ban_user_in_moderating(user_name: str):
    """Ban a user from all subreddits the bot moderates if it has not been banned yet.

    Args:
        user_name (str): The reddit username of the user to ban.
    """
    if not configs.get("on_bad_post", "ban"):
        return

    reddit = std.gen_reddit_instance()

    subs_banned_in = []

    for subreddit in reddit.user.moderator_subreddits(limit=None):  # type: ignore
        if std.raw_str_comp(subreddit, f"u_{std.Secrets.username.lower()}"):
            continue

        if banned.is_in(user_name, str(subreddit).lower()):
            continue

        std.control_ratelimit(reddit)

        ban_user(subreddit, user_name)

        subs_banned_in.append(str(subreddit).lower())

        time.sleep(2)

    banned.add(user_name, subs_banned_in)


def remove_submission(submission: praw.models.Submission):
    """Remove a submission from their host sub.

    Args:
        submission (praw.models.Submission): The submission to remove.
    """
    options = configs.get_both("on_bad_post", sub=str(submission.subreddit)).unwrap()

    if not options["remove"]:
        return

    try:
        # https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.remove
        submission.mod.remove(**options["remove_opts"])
        # https://praw.readthedocs.io/en/stable/code_overview/other/submissionmoderation.html#praw.models.reddit.submission.SubmissionModeration.send_removal_message
        submission.mod.send_removal_message(**options["remove_message_content"])
    except Exception as e:
        logger.error("Removing submission %s failed: %s" % (submission, e))


def pickle_queue(queue: BanQueue):
    """Pickle a queue to a file.

    Args:
        queue (BanQueue): Queue to pickle.
    """
    with open(ban_cache_path, "wb") as f:
        pickle.dump(queue, f)


def check_submissions(  # sourcery no-metrics
    id_: uuid.UUID, subs_dict: Dict[uuid.UUID, List[str]], errors: Queue
):
    """Check for bad submissions given a list of subreddits to monitor.

    Args:
        subs_dict (Dict[uuid.UUID, List[str]]): Dictionary containing the list of subreddits to monitor.
        errors (Queue): Queue responsible for storing any unplanned exceptions.
    """
    reddit = std.gen_reddit_instance()

    while 1:
        try:

            modded = subs_dict[id_]

            submission_stream = reddit.subreddit("+".join(modded)).stream.submissions(
                skip_existing=True, pause_after=10
            )

            for submission in submission_stream:

                std.control_ratelimit(reddit)
                time.sleep(20)

                if submission is None:
                    time.sleep(60)
                    continue

                logger.debug("%s: found submission : %s" % (id_, submission))

                if hasattr(submission, "crosspost_parent"):

                    parent = reddit.submission(
                        submission.crosspost_parent.split("_")[1]
                    )

                    if str(parent.subreddit).lower() in blacklist.get():
                        logger.info(
                            "Bad submission found: %s : u/%s"
                            % (
                                submission,
                                submission.author,
                            )
                        )

                        if std.raw_str_comp(submission.author, parent.author):
                            ban_queue.put(str(submission.author).lower())
                            pickle_queue(ban_queue)

                        remove_submission(submission)

                        plugins.on(
                            "on_bad_post",
                            submission=str(submission),
                            parent=str(parent),
                        )

                if not len(subs_dict[id_]):
                    return

                if modded != subs_dict[id_]:
                    break

        except BaseException as e:
            code, call, msg = std.catch(e, logger)
            call(msg)

            if code:
                errors.put(e)
                break
            continue


def manage_threads(thread_manager: ThreadManager):
    """Manage all running threads given a manager.

    Args:
        thread_manager (ThreadManager): Any ThreadManager instance.

    Raises:
        SystemExit: Raised if an error occurred within the thread manager.
    """
    while 1:

        time.sleep(120)

        new_modded = moderating.get()

        thread_manager.update(new_modded)

        error = thread_manager.check_errors()

        if error is not None:
            raise SystemExit("Unplanned SystemExit: %s" % error)

        # ban users

        if ban_queue.is_empty():
            if ban_cache_path.exists():
                ban_cache_path.unlink(True)
            continue

        if user := ban_queue.get():
            ban_user_in_moderating(user)

        thread_manager.check_running()


##########################
# ======== MAIN ======== #
##########################


def main():
    """Main entry point."""
    thread_manager = ThreadManager(check_submissions)
    thread_manager.initialize(moderating.get())

    manage_threads(thread_manager)
    return


if __name__ == "__main__":
    main()
