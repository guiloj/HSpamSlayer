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
import queue
from typing import Any, Callable, Dict, List, Tuple
import praw
import praw.models
import prawcore
import _stdmodule as std
import time
import threading
import uuid

###############################################
# FILE MANAGEMENT
###############################################

# ? (@guiloj) correctly finds the path to the main.py file to
# ? manage the modules and libs

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

###############################################
# CLASSES
###############################################
class StreamThread(threading.Thread):
    def __init__(
        self, target: Callable[[Any], Any], args: "List | Tuple", id_: uuid.UUID
    ):
        super().__init__(target=target, args=args)
        self.id = id_


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

    return configs


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
    return [x.lower() for x in subs]


def get_modded_subs() -> List[str]:
    with open("../cache/moderated_subreddits.cache.json") as f:
        subs = json.loads(f.read())
    try:
        return [
            x.lower()
            for x in subs["subreddits"]
            if str(x).lower() != "u_" + std.username.lower()
        ]
    except KeyError:
        std.update_modded_subreddits()
        return get_modded_subs()


def remove_config() -> dict:
    with open("../config/config.json", "rt", encoding="utf-8") as f:
        configs = json.loads(f.read())["remove"]

    return configs


def remove_submission(submission: praw.reddit.Submission) -> None:
    """Removes a submission and sends a removal message.

    Args:
        submission (praw.reddit.Submission): The submission to be removed.
    """
    configs = remove_config()
    try:
        submission.mod.remove()
        submission.mod.send_removal_message(**configs)
    except Exception as e:
        std.add_to_traceback(e)


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
        subreddit: praw.models.Subreddit
        if str(subreddit).lower() == "u_" + std.username.lower():
            continue

        if user_banned.get(str(subreddit), False):
            continue

        std.check_ratelimit(reddit, True)

        try:
            ban_user(subreddit, user_name)
            std.logger.info(
                f"User https://www.reddit.com/u/{user_name} banned in https://www.reddit.com/r/{subreddit}"
            )
            subs_banned_in.append(subreddit)
        except Exception as e:
            std.add_to_traceback(str(e))

        time.sleep(2)

    if len(subs_banned_in):
        add_to_banned_users(subs_banned_in, user_name)


def check_moderated_subs(
    id_: uuid.UUID, subs_dict: Dict[uuid.UUID, List[str]], errors_queue: queue.Queue
):
    """Checks all blacklisted subs for new posts and bans the authors.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance.
    """
    try:
        reddit = std.gen_reddit_instance()
        while 1:
            modded = subs_dict[id_]
            post_stream = reddit.subreddit("+".join(modded)).stream.submissions(
                skip_existing=True, pause_after=10  # skip_existing=True
            )

            for post in post_stream:
                std.check_ratelimit(reddit, True)
                if post is None:
                    time.sleep(10)
                    continue

                if hasattr(post, "crosspost_parent"):
                    parent = reddit.submission(post.crosspost_parent.split("_")[1])
                    if str(parent.subreddit).lower() in get_banned_subs():
                        std.logger.info(f"Bad crosspost found: {post.permalink}")
                        if post.author == parent.author:
                            threading.Thread(
                                target=flexible_ban,
                                args=(std.gen_reddit_instance(), str(post.author)),
                            ).start()

                        remove_submission(post)

                    continue

                if modded != subs_dict[id_]:
                    break

    except prawcore.exceptions.ServerError as e:
        std.add_to_traceback("Reddit API is down: " + str(e))
        time.sleep(60)
    except prawcore.exceptions.Forbidden as e:
        std.logger.critical(str(e))
        time.sleep(60)
    except Exception as e:
        errors_queue.put(e)
        return


def generate_safe_id(is_in) -> uuid.UUID:
    _id = uuid.uuid4()
    while _id in is_in:
        _id = uuid.uuid4()
    return _id


def list_diff(list_: list, other: list):
    """Difference between two lists.

    Args:
        list_ (list): list number 1
        other (list): list number 2

    Returns:
        Tuple[list]: Difference between the two lists. `[0]` == `list_` - `other`, `[1]` == `other` - `list_`
    """
    return ([x for x in list_ if x not in other], [x for x in other if x not in list_])


def mk_mod_stream(
    subs: list, threads_dict: Dict[str, List[str]], errors_queue: queue.Queue
) -> StreamThread:
    id_ = generate_safe_id(threads_dict)
    stream = StreamThread(check_moderated_subs, (id_, threads_dict, errors_queue), id_)
    threads_dict[id_] = subs
    stream.start()
    return stream


def fill_thread(new: list, filled: int):
    return (
        [x for idx, x in enumerate(new) if idx < std.LIMIT - filled],
        [x for idx, x in enumerate(new) if idx >= std.LIMIT - filled],
    )


def split_sub_list(subs: list):
    return [subs[x : x + std.LIMIT] for x in range(0, len(subs), std.LIMIT)]


def gen_mod_streams():  # sourcery no-metrics
    modded_subs = get_modded_subs()
    errors_queue = queue.Queue()
    threads_dict = {}

    running_threads = [
        mk_mod_stream(sub_list, threads_dict, errors_queue)
        for sub_list in split_sub_list(modded_subs)
    ]
    std.logger.info(f"Threads created: {len(running_threads)}")

    while 1:
        time.sleep(120)
        updated_modded_subs = get_modded_subs()
        std.logger.debug(
            f"Updated modded list: [{len(modded_subs)} => {len(updated_modded_subs)}]"
        )

        modded_diff = list_diff(modded_subs, updated_modded_subs)

        if len(modded_diff[0]):  # subs we stopped modding
            std.logger.info(f"Stopped modding: {modded_diff[0]}")
            for thread in running_threads:
                for idx, sub in enumerate(modded_diff[0]):
                    if sub in threads_dict[thread.id]:
                        threads_dict[thread.id].pop(idx)

        if len(modded_diff[1]):  # subs we started modding
            std.logger.info(f"Started modding: {modded_diff[1]}")
            to_add = modded_diff[1]

            for thread in running_threads:
                if (length := len(threads_dict[thread.id])) < std.LIMIT:
                    fill_add = fill_thread(to_add, length)
                    threads_dict[thread.id] += fill_add[0]
                    to_add = fill_add[1]
                if not len(to_add):
                    break

            if len(to_add):
                for sub_list in split_sub_list(to_add):
                    running_threads.append(
                        mk_mod_stream(sub_list, threads_dict, errors_queue)
                    )
                std.logger.info(f"Threads created: {len(to_add)}")

        if not errors_queue.empty:
            error = errors_queue.get()
            std.logger.critical(error)
            raise error

        killed = 0
        for idx, thread in enumerate(running_threads):
            if not thread.is_alive():
                killed += 1
                running_threads.pop(idx)

        if killed:
            std.logger.info(f"Threads killed: {killed}")
            killed = 0

        modded_subs = updated_modded_subs


###############################################
# MAIN
###############################################


def main():
    gen_mod_streams()


if __name__ == "__main__":
    main()
