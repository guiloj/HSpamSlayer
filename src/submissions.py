#############################
# ======== IMPORTS ======== #
#############################

import os
import pickle
import threading
import time
from typing import Dict, List

import praw
import praw.models

from _plugin_loader import PluginLoader
from _stdlib import (
    Banned,
    Blacklist,
    Configs,
    Logger,
    Moderating,
    Secrets,
    catch,
    control_ratelimit,
    gen_reddit_instance,
    p,
)
from _threading_manager import BanQueue, Queue, ThreadManager, uuid

###########################
# ======== PATHS ======== #
###########################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))
ban_cache_path = ABSDIR.joinpath("../cache/ban.queue")

###############################
# ======== INSTANCES ======== #
###############################


configs = Configs()
blacklist = Blacklist()
logger = Logger(str(ABSDIR.joinpath("../logs/submissions.log")), "Submissions")
moderating = Moderating()
plugins = PluginLoader(["on_bad_post"])
banned = Banned()


if ban_cache_path.exists():
    with open(ban_cache_path, "rb") as f:
        ban_queue = pickle.load(f)
else:
    ban_queue = BanQueue()


###############################
# ======== FUNCTIONS ======== #
###############################


def ban_user(subreddit: praw.models.Subreddit, user_name: str):
    options = configs.get("on_bad_post", "ban_opts")

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

    if not configs.get("on_bad_post", "ban"):
        return

    reddit = gen_reddit_instance()

    subs_banned_in = []

    for subreddit in reddit.user.moderator_subreddits(limit=None):  # type: ignore
        if str(subreddit).lower() == "u_" + Secrets.username.lower():
            continue

        if banned.is_in(user_name, str(subreddit).lower()):
            continue

        control_ratelimit(reddit)

        ban_user(subreddit, user_name)

        subs_banned_in.append(str(subreddit).lower())

        time.sleep(2)

    banned.add(user_name, subs_banned_in)


def remove_submission(submission: praw.models.Submission):

    options = configs.get("on_bad_post")

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
    with open(ban_cache_path, "wb") as f:
        pickle.dump(queue, f)


def check_submissions(  # sourcery no-metrics
    id_: uuid.UUID, subs_dict: Dict[uuid.UUID, List[str]], errors: Queue
):
    reddit = gen_reddit_instance()

    while 1:
        try:

            modded = subs_dict[id_]

            submission_stream = reddit.subreddit("+".join(modded)).stream.submissions(
                skip_existing=True, pause_after=10
            )

            for submission in submission_stream:

                control_ratelimit(reddit)

                if submission is None:
                    time.sleep(10)
                    continue

                if hasattr(submission, "crosspost_parent"):

                    parent = reddit.submission(
                        submission.crosspost_parent.split("_")[1]
                    )

                    if str(parent.subreddit).lower() in blacklist.get():
                        logger.debug(
                            "Bad submission found: %s : u/%s",
                            submission,
                            submission.author,
                        )

                        if str(submission.author).lower() == str(parent.author).lower():
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
            if catch(e, logger):
                errors.put(e)
                break
            continue


def manage_bans(thread_manager: ThreadManager):
    while 1:
        try:
            time.sleep(60)

            if ban_queue.is_empty():
                if ban_cache_path.exists():
                    ban_cache_path.unlink(True)
                continue

            if user := ban_queue.get():
                ban_user_in_moderating(user)

        except BaseException as e:
            if catch(e, logger):
                thread_manager.errors.put(e)
                break
            continue


def manage_threads(thread_manager: ThreadManager):
    while 1:
        time.sleep(120)

        new_modded = moderating.get()

        thread_manager.update(new_modded)

        error = thread_manager.check_errors()

        if error is not None:
            raise SystemExit("Unplanned SystemExit: %s" % error)

        thread_manager.check_running()


##########################
# ======== MAIN ======== #
##########################


def main():
    thread_manager = ThreadManager(check_submissions)
    thread_manager.initialize(moderating.get())

    threading.Thread(target=manage_bans, args=(thread_manager,)).start()

    manage_threads(thread_manager)
    return


if __name__ == "__main__":
    main()
