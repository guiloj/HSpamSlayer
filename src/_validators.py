#############################
# ======== IMPORTS ======== #
#############################

from typing import Any, Callable, Tuple

import jsonschema.exceptions
from jsonschema import validate as _validate

###############################
# ======== CONSTANTS ======== #
###############################


CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "logging": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "file_level": {"type": "integer"},
                "stdout_level": {"type": "integer"},
            },
            "required": ["file_level", "stdout_level"],
        },
        "threading": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"max_subs_per_thread": {"type": "integer"}},
            "required": ["max_subs_per_thread"],
        },
        "on_invite": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "send_message": {"type": "boolean"},
                "message_content": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "subject": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["subject", "message"],
                },
                "make_announcement": {"type": "boolean"},
                "announcement_content": {
                    "type": "object",
                    "additionalProperties": False,
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
            "additionalProperties": False,
            "properties": {
                "remove": {"type": "boolean"},
                "remove_opts": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"spam": {"type": "boolean"}},
                    "required": ["spam"],
                },
                "remove_message_content": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "message": {"type": "string"},
                        "type": {"type": "string"},
                    },
                    "required": ["message", "type"],
                },
                "ban": {"type": "boolean"},
                "ban_opts": {
                    "type": "object",
                    "additionalProperties": False,
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
            "additionalProperties": False,
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
                "additionalProperties": False,
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
        "experimental": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "opt_in": {"type": "boolean"},
                "image_recognition": {"type": "boolean"},
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

BANNED_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "additionalProperties": False,
}

BLACKLIST_SCHEMA = {"type": "array", "items": {"type": "string"}}

MODERATING_SCHEMA = BLACKLIST_SCHEMA

ANY_SCHEMA = {}


###############################
# ======== FUNCTIONS ======== #
###############################


def validate(instance: object, schema: Any) -> "BaseException | None":
    try:
        _validate(instance, schema)
    except jsonschema.exceptions.ValidationError as e:
        return e
    return None
