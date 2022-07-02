#############################
# ======== IMPORTS ======== #
#############################

from typing import Any

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
                    "properties": {
                        "spam": {"type": "boolean"},
                        "mod_note": {"type": "string"},
                        "reason_id": {"type": "string"},
                    },
                },
                "remove_message_content": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "message": {"type": "string"},
                        "type": {"type": "string"},
                    },
                    "required": ["message", "type", "title"],
                },
                "ban": {"type": "boolean"},
                "ban_opts": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ban_message": {"type": "string"},
                        "ban_reason": {"type": "string"},
                        "duration": {"type": ["integer", "null"]},
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
        "extra": {
            "type": "object",
            "additionalProperties": False,
            "required": ["opt_in_image_recognition", "opt_out_manual_moderation"],
            "properties": {
                "opt_in_image_recognition": {
                    "type": "boolean",
                },
                "opt_out_manual_moderation": {
                    "type": "boolean",
                },
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
        "extra",
    ],
}

SUB_CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["on_bad_post", "extra"],
    "properties": {
        "on_bad_post": {
            "type": "object",
            "additionalProperties": False,
            "required": ["remove_opts", "remove_message_content", "ban_opts"],
            "properties": {
                "remove_opts": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["spam", "mod_note"],
                    "properties": {
                        "spam": {
                            "type": "boolean",
                        },
                        "mod_note": {
                            "type": "string",
                        },
                    },
                },
                "remove_message_content": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["public", "private", "private_exposed"],
                        },
                    },
                },
                "ban_opts": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["ban_reason", "duration", "note"],
                    "properties": {
                        "ban_reason": {
                            "type": "string",
                            "minLength": 0,
                            "maxLength": 100,
                        },
                        "duration": {
                            "type": ["integer", "null"],
                            "minimum": 1,
                            "maximum": 999,
                        },
                        "note": {
                            "type": "string",
                            "minLength": 0,
                            "maxLength": 300,
                        },
                    },
                },
            },
        },
        "extra": {
            "type": "object",
            "additionalProperties": False,
            "required": ["opt_in_image_recognition", "opt_out_manual_moderation"],
            "properties": {
                "opt_in_image_recognition": {
                    "type": "boolean",
                },
                "opt_out_manual_moderation": {
                    "type": "boolean",
                },
            },
        },
    },
}

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


def validate(
    instance: object, schema: Any
) -> "jsonschema.exceptions.ValidationError | None":
    """Validate json object with a schema.

    Args:
        instance (object): The json object to validate.
        schema (Any): The schema to validate against.

    Returns:
        BaseException | None: The exception if the validation fails, None otherwise.
    """
    try:
        _validate(instance, schema)
    except jsonschema.exceptions.ValidationError as e:
        return e
    return None
