#############################
# ======== IMPORTS ======== #
#############################

import inspect
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path as p  # normalize paths between every OS
from typing import Any, Dict, List, Tuple, Type

import praw
import prawcore

############################
# ======== PATHS ========= #
############################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))
# os.chdir(str(ABSDIR))  # changing directory to file path to use relative paths

_secrets_path = str(ABSDIR.joinpath("../keys/secrets.json"))
_config_path = str(ABSDIR.joinpath("../config/config.json"))
_subs_config_path = str(ABSDIR.joinpath("../config/subs"))
_blacklist_path = str(ABSDIR.joinpath("../data/blacklist.json"))
_mod_cache_path = str(ABSDIR.joinpath("../cache/moderating_subreddits.cache.json"))
_banned_cache_path = str(ABSDIR.joinpath("../cache/banned_users.cache.json"))

with open(_secrets_path, "rt", encoding="utf-8") as f:
    _secrets = json.load(f)


##########################
# ======== DATA ======== #
##########################


@dataclass
class Secrets:
    client_id: str = _secrets["client_id"]
    client_secret: str = _secrets["client_secret"]
    password: str = _secrets["password"]
    user_agent: str = _secrets["user_agent"]
    username: str = _secrets["username"]


@dataclass
class PrawErrors:
    Critical: Tuple[Type[BaseException], ...] = (
        prawcore.exceptions.Forbidden,
        prawcore.exceptions.NotFound,
    )
    NonCritical: Tuple[Type[BaseException], ...] = (
        prawcore.exceptions.ServerError,
        prawcore.exceptions.RequestException,
    )
    SysExit: Tuple[Type[BaseException], ...] = (BaseException,)


class Configs:
    def __init__(
        self,
        config_path: str = _config_path,
        subs_path: str = _subs_config_path,
    ):
        self.config_path = p(config_path).absolute()

        self.subs_path = p(subs_path)

    def _get(self, path: "str | p", *keys):
        with open(path, "rt", encoding="utf-8") as f:
            configs: Dict[str, Any] = json.load(f)

        try:
            for key in keys:
                configs = configs[key]
        except (KeyError, IndexError) as e:
            _logger.error("Invalid path for dictionary object!")
            return None
        return configs

    def get(self, *keys) -> Any:
        return self._get(self.config_path, *keys)

    def get_sub(self, sub: str, *keys) -> Any:
        config_path = self.config_path

        for config in self.subs_path.iterdir():
            if config.name.replace(".json", "").lower() == sub.lower():
                config_path = config
                break

        return self._get(config_path, *keys)


class Banned:
    def __init__(
        self,
        banned_cache_path: str = _banned_cache_path,
    ):
        self.banned_cache_path = p(banned_cache_path)

    def get(self, user: str):
        with open(self.banned_cache_path, "rt", encoding="utf-8") as f:
            banned: Dict[str, List[str]] = json.load(f)

        for key, value in banned.items():
            if key.lower() == user.lower():
                return value

    def is_in(self, user: str, subreddit: str):

        banned_in = self.get(user)

        if banned_in is None:
            return False

        if subreddit.lower() in banned_in:
            return True

        return False

    def add(self, user: str, new_subs: List[str]):
        # sourcery skip: use-dict-items
        with open(self.banned_cache_path, "rt", encoding="utf-8") as f:
            banned: Dict[str, List[str]] = json.load(f)

        for key in banned:
            if key.lower() == user.lower():

                banned[key] += new_subs
                banned[key] = list(set(banned[key]))
                break
        else:
            banned[user.lower()] = [x.lower() for x in new_subs]

        with open(self.banned_cache_path, "wt", encoding="utf-8") as f:
            json.dump(banned, f)


class Blacklist:
    def __init__(self, blacklist_path: str = _blacklist_path):
        self.blacklist_path = blacklist_path

    def get(self) -> List[str]:
        with open(self.blacklist_path, "rt", encoding="utf-8") as f:
            blacklist: List[str] = json.load(f)

        return [sub.lower() for sub in blacklist]


class Moderating:
    def __init__(self, mod_cache_path: str = _mod_cache_path):
        self.mod_cache_path = mod_cache_path

    def get(self) -> List[str]:
        with open(self.mod_cache_path, "rt", encoding="utf-8") as f:
            subs = json.load(f)

        result = [
            x.lower() for x in subs if str(x).lower() != "u_" + Secrets.username.lower()
        ]
        if not len(result):
            with gen_reddit_instance() as r:  # it's ok to create a reddit instance here because this should only be called when the cache is empty
                self.update(r)
            return (
                self.get()
            )  # will create a recursion loop if the bot does not moderate any subreddits
        return result

    def update(self, reddit: praw.reddit.Reddit) -> None:

        modded_subs = [str(x) for x in reddit.user.moderator_subreddits(limit=None)]  # type: ignore

        with open(self.mod_cache_path, "wt", encoding="utf-8") as f:
            json.dump(modded_subs, f, indent=4)

        return


#############################
# ======== LOGGING ======== #
#############################


_loggers: Dict[str, logging.Logger] = {}

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("prawcore").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

# https://stackoverflow.com/a/56944256 <= (@guiloj) credit is important kids
class _CustomFormatter(logging.Formatter):
    def __init__(self, file: bool = False):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format_ = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        self.OS = os.name if not file else "nt"

        self.FORMATS = {
            logging.DEBUG: grey + format_ + reset,
            logging.INFO: grey + format_ + reset,
            logging.WARNING: yellow + format_ + reset,
            logging.ERROR: red + format_ + reset,
            logging.CRITICAL: bold_red + format_ + reset,
            "NORMAL": format_,
        }

    def format(self, record):
        log_fmt = (
            self.FORMATS.get(record.levelno)
            if self.OS != "nt"
            else self.FORMATS.get("NORMAL")
        )
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def Logger(file_path: str, name: str) -> logging.Logger:

    if _loggers.get(name):
        return _loggers.get(name)  # type: ignore

    # create logger with 'spam_application'
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    _ch = logging.StreamHandler(sys.stdout)
    _ch.setLevel(_configs.get("logging", "stdout_level"))
    _ch.setFormatter(_CustomFormatter())

    _fh = logging.FileHandler(file_path)
    _fh.setLevel(_configs.get("logging", "file_level"))
    _fh.setFormatter(_CustomFormatter(True))

    logger.addHandler(_fh)
    logger.addHandler(_ch)

    _loggers[file_path] = logger

    return logger


#######################################
# ======== PRIVATE INSTANCES ======== #
#######################################

_configs = Configs()
_logger = Logger(str(ABSDIR.joinpath("../logs/std.lib.log")), "StdLib")

###############################
# ======== FUNCTIONS ======== #
###############################


def catch(error: BaseException, logger: logging.Logger) -> int:

    if isinstance(error, PrawErrors.Critical):
        logger.critical(
            "Critical error ocurred: %s : %s" % (type(error).__name__, error)
        )
        time.sleep(60)
    elif isinstance(error, PrawErrors.NonCritical):
        logger.warning("Reddit API is down: %s : %s" % (type(error).__name__, error))
        time.sleep(120)
    elif isinstance(error, PrawErrors.SysExit):
        logger.critical(
            "An exception went unhandled: %s : %s" % (type(error).__name__, error)
        )
        return 1
    else:
        logger.critical(
            "Something went very wrong: %s : %s" % (type(error).__name__, error)
        )
        return 1
    return 0


def _as_dict(obj: object):
    _vars = vars(obj)
    return {k: v for k, v in zip(_vars.keys(), _vars.values()) if not k.startswith("_")}


def control_ratelimit(reddit: praw.reddit.Reddit):
    limit = reddit.auth.limits

    requests_left = (
        int(limit["remaining"]) if isinstance(limit["remaining"], (int, float)) else 0
    )
    time_left = (
        limit["reset_timestamp"]
        if isinstance(limit["reset_timestamp"], (int, float))
        else 0
    ) - time.time()

    if _logger.level == logging.DEBUG:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        _logger.debug(f"{calframe[1][3]}() => {requests_left}, {int(time_left)}s")

    if requests_left < 20:
        if time_left > 0:
            time.sleep(time_left)
        return


def gen_reddit_instance(secrets: Type[Secrets] = Secrets) -> praw.reddit.Reddit:
    reddit = praw.Reddit(**_as_dict(secrets))
    reddit._validate_on_submit = True
    # _logger.debug("Created reddit instance: %s" % reddit)
    # I'm not sure about this debug call
    return reddit
