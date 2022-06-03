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

import _rust_types as rt
import _validators as val

############################
# ======== PATHS ========= #
############################


ABSDIR = p(__file__).parent.absolute()

_secrets_path = ABSDIR.joinpath("../keys/secrets.json")
_config_path = ABSDIR.joinpath("../config/config.json")
_subs_config_path = ABSDIR.joinpath("../config/subs")
_blacklist_path = ABSDIR.joinpath("../data/blacklist.json")
_mod_cache_path = ABSDIR.joinpath("../cache/moderating_subreddits.cache.json")
_banned_cache_path = ABSDIR.joinpath("../cache/banned_users.cache.json")

with open(_secrets_path, "rt", encoding="utf-8") as f:
    _secrets = json.load(f)


##########################
# ======== DATA ======== #
##########################


@dataclass(frozen=True)
class Secrets:
    """A frozen and typed representation for praw's Reddit secrets."""

    client_id: str = _secrets["client_id"]
    client_secret: str = _secrets["client_secret"]
    password: str = _secrets["password"]
    user_agent: str = _secrets["user_agent"]
    username: str = _secrets["username"]


@dataclass(frozen=True)
class PrawErrors:
    """A frozen and typed representation for praw's errors with criticality layers."""

    Critical: Tuple[Type[BaseException], ...] = (
        prawcore.exceptions.Forbidden,
        prawcore.exceptions.NotFound,
    )
    NonCritical: Tuple[Type[BaseException], ...] = (
        prawcore.exceptions.ServerError,
        prawcore.exceptions.RequestException,
    )
    SysExit: Tuple[Type[BaseException], ...] = (BaseException,)


class Result:
    pass


#############################
# ======== CLASSES ======== #
#############################


class Configs:
    def __init__(
        self,
        config_path: p = _config_path,
        subs_path: p = _subs_config_path,
        schema: object = val.CONFIG_SCHEMA,
    ):
        """Creates a helper object to easily manage json style config files.

        Args:
            config_path (Path, optional): Path to the config file. Defaults to _config_path.
            subs_path (Path, optional): Path to the sub specific config files. Defaults to _subs_config_path.
            schema (object, optional): Json schema for the config file (Use ANY_SCHEMA to accept any json configuration). Defaults to CONFIG_SCHEMA.
        """
        self.config_path = config_path.absolute()

        self.subs_path = subs_path

        self.schema = schema

    def _get(self, path: "str | p", *keys, schema=None) -> rt.Option[Any]:
        with open(path, "rt", encoding="utf-8") as f:
            configs: Dict[str, Any] = json.load(f)

        if error := val.validate(configs, self.schema if schema is None else schema):
            raise error

        try:
            for key in keys:
                configs = configs[key]
        except (KeyError, IndexError) as e:
            _logger.error("Invalid path for dictionary object!")
            return rt.Nothing()
        return rt.Some(configs)

    def get(self, *keys):
        """Gets a config value from the config file."""
        return self._get(self.config_path, *keys)

    def get_sub(self, sub: str, *keys):
        """Gets a config value from a sub specific config file.

        Args:
            sub (str): Subreddit's name.

        Returns:
            Any: Config value. Defaults to normal config file.
        """
        config_path = self.config_path

        for config in self.subs_path.iterdir():
            if raw_str_comp(config.name.replace(".json", ""), sub):
                config_path = config
                break

        return self._get(config_path, *keys, val.SUB_CONFIG_SCHEMA)


class Banned:  # TODO: use rust_types
    def __init__(
        self,
        banned_cache_path: p = _banned_cache_path,
        schema: object = val.BANNED_SCHEMA,
    ):
        """Create a helper object for managing banned users.

        Args:
            banned_cache_path (p, optional): The path to the banned users cache file. Defaults to _banned_cache_path.
            schema (object, optional): A schema object to validate against. Defaults to val.BANNED_SCHEMA.
        """
        self.banned_cache_path = banned_cache_path

        self.schema = schema

    def _get(self, user: str, schema=None):
        with open(self.banned_cache_path, "rt", encoding="utf-8") as f:
            banned: Dict[str, List[str]] = json.load(f)

        if error := val.validate(banned, self.schema if schema is None else schema):
            raise error

        for key, value in banned.items():
            if raw_str_comp(key, user):
                return value

    def get(self, user: str):
        """Gets a user's banned subreddits."""
        return self._get(user)

    def is_in(self, user: str, subreddit: str):
        """If a user is banned in a subreddit

        Args:
            user (str): The user to check.
            subreddit (str): The subreddit to check.

        Returns:
            _type_: _description_
        """
        banned_in = self._get(user)

        if banned_in is None:
            return False

        if subreddit.lower() in banned_in:
            return True

        return False

    def add(self, user: str, new_subs: List[str], schema=None):
        """Adds the subreddits a user was banned in to the banned cache file.

        Args:
            user (str): User that was banned.
            new_subs (List[str]): List of subreddits that the user was banned in.
            schema (_type_, optional): A schema object to validate against. Defaults to None.

        Raises:
            error: A validation error if the schema is not valid.
        """
        # sourcery skip: use-dict-items
        with open(self.banned_cache_path, "rt", encoding="utf-8") as f:
            banned: Dict[str, List[str]] = json.load(f)

        if error := val.validate(banned, self.schema if schema is None else schema):
            raise error

        for key in banned:
            if raw_str_comp(key, user):

                banned[key] += new_subs
                banned[key] = list(set(banned[key]))
                break
        else:
            banned[user.lower()] = [x.lower() for x in new_subs]

        with open(self.banned_cache_path, "wt", encoding="utf-8") as f:
            json.dump(banned, f)


class Blacklist:
    def __init__(
        self, blacklist_path: p = _blacklist_path, schema=val.BLACKLIST_SCHEMA
    ):
        """Create a helper object for managing blacklisted subreddits.

        Args:
            blacklist_path (p, optional): The path to the blacklist file. Defaults to _blacklist_path.
            schema (object, optional): A schema object to validate against. Defaults to val.BLACKLIST_SCHEMA.
        """
        self.blacklist_path = blacklist_path
        self.schema = schema

    def get(self, schema=None) -> List[str]:
        """Get a list of all blacklisted subreddits.

        Args:
            schema (object, optional): A schema object to validate against. Defaults to None.

        Raises:
            error: A validation error if the schema is not valid.

        Returns:
            List[str]: A list of all blacklisted subreddits.
        """
        with open(self.blacklist_path, "rt", encoding="utf-8") as f:
            blacklist: List[str] = json.load(f)

        if error := val.validate(blacklist, self.schema if schema is None else schema):
            raise error

        return [sub.lower() for sub in blacklist]


class Moderating:
    def __init__(
        self,
        mod_cache_path: p = _mod_cache_path,
        schema: object = val.MODERATING_SCHEMA,
    ):
        """Create a helper object for managing moderated subreddits.

        Args:
            mod_cache_path (p, optional): The path to the moderation cache file. Defaults to _mod_cache_path.
            schema (object, optional): A schema object to validate against. Defaults to val.MODERATING_SCHEMA.
        """
        self.mod_cache_path = mod_cache_path
        self.schema = schema

    def get(self, schema=None) -> List[str]:
        """Get a list of all subreddits that the bot moderates.

        Args:
            schema (object, optional): A schema object to validate against. Defaults to None.

        Raises:
            error: A validation error if the schema is not valid.

        Returns:
            List[str]: A list of all moderated subreddits.
        """
        with open(self.mod_cache_path, "rt", encoding="utf-8") as f:
            subs = json.load(f)

        if error := val.validate(subs, self.schema if schema is None else schema):
            raise error

        result = [
            x.lower() for x in subs if str(x).lower() != f"u_{Secrets.username.lower()}"
        ]

        if not len(result):
            with gen_reddit_instance() as r:  # it's ok to create a reddit instance here because this should only be called when the cache is empty
                self.update(r)
            return (
                self.get()
            )  # will create a recursion loop if the bot does not moderate any subreddits
        return result

    def update(self, reddit: praw.reddit.Reddit) -> None:
        """Updates the cache of subreddits the bot moderates."""
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
# no I don't want to know about every single detail about every single request

# https://stackoverflow.com/a/56944256 <= (@guiloj) credit is important kids
class _CustomFormatter(logging.Formatter):
    def __init__(self, file: bool = False):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format_ = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        self.OS = "nt" if file else os.name

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


def Logger(file_path: p, name: str) -> logging.Logger:
    """Create a new logger instance.

    Args:
        file_path (p): The path to the log file.
        name (str): The name of the logger.

    Returns:
        logging.Logger: Resulting logger instance.
    """

    if _loggers.get(name):
        return _loggers.get(name)  # type: ignore

    # create logger with 'spam_application'
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    _ch = logging.StreamHandler(sys.stdout)
    _ch.setLevel(_configs.get("logging", "stdout_level").unwrap())
    _ch.setFormatter(_CustomFormatter())

    _fh = logging.FileHandler(str(file_path))
    _fh.setLevel(_configs.get("logging", "file_level").unwrap())
    _fh.setFormatter(_CustomFormatter(True))

    logger.addHandler(_fh)
    logger.addHandler(_ch)

    _loggers[str(file_path)] = logger

    return logger


#######################################
# ======== PRIVATE INSTANCES ======== #
#######################################

_configs = Configs()
_logger = Logger(ABSDIR.joinpath("../logs/std.lib.log"), "StdLib")

###############################
# ======== FUNCTIONS ======== #
###############################


def catch(error: BaseException, logger: logging.Logger) -> int:
    """Catch common errors derived from praw and return 1 if the error was critical and 0 if not.

    Args:
        error (BaseException): The exception that occurred.
        logger (logging.Logger): A logger to log the error to.

    Returns:
        int: 1 if the error was critical and 0 if not.
    """
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
    """Control the ratelimit of a reddit instance.

    Args:
        reddit (praw.reddit.Reddit): The reddit instance to control.
    """
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


def json_escape_string(object_: Any) -> str:
    """Escape a string for JSON serialization.

    Args:
        object_ (Any): Any object that can be turned into a string.

    Returns:
        str: The formatted string.
    """
    return str(object_).replace('"', "").replace("\n", "\\n")


def gen_reddit_instance(secrets: Type[Secrets] = Secrets) -> praw.reddit.Reddit:
    """Generate a new reddit instance.

    Args:
        secrets (Type[Secrets], optional): Secrets object used to login. Defaults to Secrets.

    Returns:
        praw.reddit.Reddit: A new reddit instance.
    """
    reddit = praw.Reddit(**_as_dict(secrets))
    reddit._validate_on_submit = True
    # _logger.debug("Created reddit instance: %s" % reddit)
    # I'm not sure about this debug call
    return reddit


def raw_str_comp(str1: object, str2: object) -> bool:
    """Compare two strings without caring about case.

    Args:
        str1 (object): First string to compare.
        str2 (object): Second string to compare.

    Returns:
        bool: True if the strings are equal, False otherwise.
    """
    return str(str1).lower() == str(str2).lower()
