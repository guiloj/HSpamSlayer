#############################
# ======== IMPORTS ======== #
#############################

import json
import typing as tp
from pathlib import Path as p

import _rust_types as rt
import _stdlib as std
import _validators as val

############################
# ======== PATHS ========= #
############################

ABSDIR = p(__file__).parent.absolute()

###############################
# ======== INSTANCES ======== #
###############################

logger = std.Logger(ABSDIR.joinpath("../logs/sub.configs.log"), "SubConfigs")

###############################
# ======== FUNCTIONS ======== #
###############################


def list_as_arrows(array: list):
    return f"[{' => '.join(array)}]"


def json_parsing_error(err: json.JSONDecodeError):
    message = f"It looks like your configuration data is not valid json data!\n\n    {err.lineno} | "

    len_num = len(str(err.lineno))

    line = err.doc.splitlines(True)[err.lineno - 1]
    temp = line[max(err.colno - 1 - 20, 0) : min(err.colno - 1 + 20, len(line) - 1)]

    displacement = 0

    if not line.startswith(temp):
        message += "... "
        displacement += 4

    index = line.find(temp) or 0

    if not line.endswith(temp):
        temp += " ..."

    # XXX: just pretend this makes sense
    message += "    ".join(
        f"{temp}\n{' ' * len_num} |_{'_' * displacement}{'_'*(err.colno-1-index)}^\n{' ' * len_num} |\n{' ' * len_num} | error: {str(err)}".splitlines(
            True
        )
    )

    return message


def json_schema_validation_error(err: val.jsonschema.exceptions.ValidationError):
    msg = "    ".join(
        f'\n{err.message}\nAt instance {list_as_arrows(list(err.path))}:\n    {"    ".join(json.dumps(err.instance, indent=4).splitlines(True))}\n\nFailed to validate against validator "{err.validator}" that was set to "{err.validator_value}"\n'.splitlines(
            True
        )
    )
    return (
        f"It looks like your json data does not match our verification schema!\n\n{msg}"
    )


###############################
# ======== FUNCTIONS ======== #
###############################


def set_sub_config(data: str, subreddit: str) -> rt.Option[str]:
    try:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError as e:
            return rt.Some(json_parsing_error(e))

        exception = val.validate(json_data, val.SUB_CONFIG_SCHEMA)

        if exception is not None:
            return rt.Some(json_schema_validation_error(exception))

        ABSDIR.joinpath(f"../config/subs/{subreddit.lower()}.json").write_text(
            json.dumps(json_data, indent=4)
        )

        logger.info("Set config file for r/%s" % subreddit)

        return rt.Nothing()
    except Exception as e:
        logger.critical("Something went wrong with setting a sub config: %s" % e)
        return rt.Some(
            "Something internal went wrong! Our team should be working on it!"
        )
