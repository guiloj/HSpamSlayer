#############################
# ======== IMPORTS ======== #
#############################

from typing import Callable, Tuple

import jsonschema.exceptions
from jsonschema import validate

###############################
# ======== CONSTANTS ======== #
###############################


CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "logging": {
            "type": "object",
            "properties": {
                "file_level": {"type": "integer"},
                "stdout_level": {"type": "integer"},
            },
            "required": ["file_level", "stdout_level"],
        },
        "threading": {
            "type": "object",
            "properties": {"max_subs_per_thread": {"type": "integer"}},
            "required": ["max_subs_per_thread"],
        },
        "on_invite": {
            "type": "object",
            "properties": {
                "send_message": {"type": "boolean"},
                "message_content": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["subject", "message"],
                },
                "make_announcement": {"type": "boolean"},
                "announcement_content": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "selftext": {"type": "string"},
                    },
                    "required": ["title", "selftext"],
                },
                "ignore": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "send_message",
                "message_content",
                "make_announcement",
                "announcement_content",
                "ignore",
            ],
        },
        "on_bad_post": {
            "type": "object",
            "properties": {
                "remove": {"type": "boolean"},
                "remove_opts": {
                    "type": "object",
                    "properties": {"spam": {"type": "boolean"}},
                    "required": ["spam"],
                },
                "remove_message_content": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "type": {"type": "string"},
                    },
                    "required": ["message", "type"],
                },
                "ban": {"type": "boolean"},
                "ban_opts": {
                    "type": "object",
                    "properties": {
                        "ban_message": {"type": "string"},
                        "ban_reason": {"type": "string"},
                        "duration": {"type": "null"},
                        "note": {"type": "string"},
                    },
                    "required": ["ban_message", "ban_reason", "duration", "note"],
                },
            },
            "required": [
                "remove",
                "remove_opts",
                "remove_message_content",
                "ban",
                "ban_opts",
            ],
        },
        "main.py": {
            "type": "object",
            "properties": {
                "scripts": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["scripts"],
        },
        "plugins": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "types": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "script": {"type": "string"},
                },
                "required": ["types", "script"],
            },
        },
    },
    "required": [
        "logging",
        "threading",
        "on_invite",
        "on_bad_post",
        "main.py",
        "plugins",
    ],
}

SUB_CONFIG_SCHEMA = {}

BLACKLIST_SCHEMA = {"type": "array", "items": {"type": "string"}}


###############################
# ======== FUNCTIONS ======== #
###############################


def _validate(instance: object, schema: object) -> Tuple[bool, "BaseException | None"]:
    try:
        validate(instance, schema)
    except jsonschema.exceptions.ValidationError as e:
        return (False, e)
    return (True, None)


def validate_blacklist(instance: object) -> Tuple[bool, "BaseException | None"]:
    return _validate(instance, BLACKLIST_SCHEMA)


def validate_config(instance: object):
    return _validate(instance, CONFIG_SCHEMA)


def validate_sub_config(instance: object):
    return _validate(instance, SUB_CONFIG_SCHEMA)


def create_validator(
    schema: object,
) -> Callable[[object], Tuple[bool, "BaseException | None"]]:
    def result(instance: object) -> Tuple[bool, "BaseException | None"]:
        return _validate(instance, schema)

    return result
