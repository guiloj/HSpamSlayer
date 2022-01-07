import sys

print(
    " _   _ ____                        ____  _                       \n| | | / ___| _ __   __ _ _ __ ___ / ___|| | __ _ _   _  ___ _ __ \n| |_| \\___ \\| '_ \\ / _` | '_ ` _ \\\\___ \\| |/ _` | | | |/ _ \\ '__|\n|  _  |___) | |_) | (_| | | | | | |___) | | (_| | |_| |  __/ |   \n|_| |_|____/| .__/ \\__,_|_| |_| |_|____/|_|\\__,_|\\__, |\\___|_|   \n            |_|                                  |___/\n"
)

if sys.version_info.major != 3 or sys.version_info.minor < 6:
    print(
        "Please upgrade your python version to Python ≥ 3.6"
        + "\n"
        + "Refer to https://www.python.org/downloads/"
    )
    quit(1)

import os
from typing import NoReturn
import subprocess
from pathlib import Path

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

dir_paths = ["cache", "config", "data"]
file_paths = {
    "cache/banned_users.cache.json": '{"banned_users":{}}',
    "cache/moderated_subreddits.cache.json": '{"subreddits":{}}',
    "config/config.json": '{\n    "webhooks": {\n        "use": false,\n        "main_critical": {},\n        "invite_accept": {}\n    },\n    "no_invite": [],\n    "action": {\n        "ban_message": "",\n        "ban_reason": "",\n        "duration": null,\n        "note": ""\n    },\n    "message": {\n        "subject": "",\n        "message": ""\n    },\n    "announcement": {\n        "title": "",\n        "selftext": ""\n    },\n    "remove": {\n        "message": "",\n        "type": "public"\n    }\n}',
    "data/secrets.json": '{\n    "username": "",\n    "password": "",\n    "secret": "",\n    "id": "",\n    "agent": "",\n    "webhook": ""\n}',
    "data/subs.json": '{\n    "banned_subs": []\n}',
}


def normalize_size(string: str, max_size: int):
    for _ in range(max_size - len(string)):
        string += " "
    return string


def progress_bar(current: int, total: int, message: str = ""):
    percent = ("{0:." + str(1) + "f}").format(100 * (current / float(total)))
    filled = int(100 * current // total)
    bar = "█" * filled + " " * (100 - filled)
    print(f"\r{message} |{bar}| {percent}%", end="\r")

    if current == total:
        print()


def confirm(string: str) -> "None | NoReturn":
    yn = input(string + " [Y/n] ")
    if yn.lower() != "y":
        print("Abort.")
        quit(1)


confirm(
    "This script will use/clear any existing directory/file with conflicting names, do wou wish to proceed?"
)


try:
    print("Creating directories...")
    for path in dir_paths:
        Path(path).mkdir(parents=True, exist_ok=True)

    print("Creating files...")

    for path in file_paths:
        with open(Path(path), "wt", encoding="utf-8") as f:
            f.write(file_paths[path])

    confirm(
        "This script will now install all the required dependencies from requirements.txt, do you wish to proceed?"
    )
    with open("requirements.txt", "rt", encoding="utf-8") as f:
        content = [x.replace("\n", "") for x in f.readlines()]

    for idx, package in enumerate(content):
        progress_bar(
            idx + 1,
            len(content),
            normalize_size(package, max(len(x) for x in content)),
        )
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.PIPE,
            )
        except subprocess.CalledProcessError:
            print("A critical error occurred during the installation process!")
            quit(1)

    print(
        "This script has been ran successfully, now auto destroying to avoid any future accidents."
    )
    Path(ABSPATH).unlink()  # this comes from trauma
except PermissionError:
    print("PermissionError: Script can't write in this location!")
    quit(1)
except FileExistsError:
    print(
        f"FileExistsError: There is already a file or directory with one of the following names: {dir_paths}"
    )
    quit(1)
quit(0)
