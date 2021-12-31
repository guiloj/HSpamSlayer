"""
# src/main.py

Starts the bot.

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

import json
import os
import time
from subprocess import Popen
import _stdmodule as std

###############################################
# FILE MANAGEMENT
###############################################

# ? correctly finds the path to the main.py file to
# ? manage the modules and libs

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

with open("../config/config.json", "rt", encoding="utf-8") as f:
    configs = json.loads(f.read())

###############################################
# MAIN
###############################################

# TODO: (@guiloj) add tests for all scripts
# TODO: (@guiloj) clean code of static data, use config for webhook messages
# TODO: (@guiloj) just fucking clean up the code: \
# 1 - make a setup wizard for configs, no one is going to read the docs. \
# 2 - update the docs :( \
# 3 - make main only send one webhook message, with the exception. \
# 4 - use the std.config() function instead of all of the useless *_config functions. \
# 5 - make things more customizable, it'll be better for everyone. \
# 6 - use sys.executable instead of defaulting to python3. \
# 7 - encrypt passwords and prompt the user for a encryption password on startup. \
# 8 - make a exclude list for subreddits, don't want the spam subs inviting the bot. \
# 9 - seriously make webhook messages useful and not being in the middle of the fucking code you fucking buffoon. \
# 10 - like ffs you need to release this you bitch.
def main():
    # * (@guiloj) starts both bot scripts simultaneously
    invites = Popen(["python3", "accept_invites.py"])
    posts = Popen(["python3", "mod_posts.py"])
    try:
        while 1:
            fail = 0
            time.sleep(100)

            # * (@guiloj) checks if any of the scripts stopped unexpectedly
            if (code := invites.poll()) != None:
                std.add_to_traceback(f"({code}) an error occurred in accept_invites.py")
                fail += 1
            if (code := posts.poll()) != None:
                std.add_to_traceback(f"({code}) an error occurred in mod_posts.py")
                fail += 1

            # ? (@guiloj) to alert owner that one of the scripts have stopped, is on `../config/config.json`
            if fail > 0 & configs["webhook"]:
                std.send_to_webhook(
                    {
                        "embeds": [
                            {
                                "author": {
                                    "name": "Doctor_Sex_tf2",
                                    "url": "https://www.reddit.com/user/Doctor_Sex_tf2",
                                    "icon_url": "https://styles.redditmedia.com/t5_39x1ek/styles/profileIcon_o9u59ceglna61.jpg?width=256&height=256&crop=256:256,smart&s=948c8d54cfe94a97f7d8bc120ef4ac77eb27dbb7",
                                },
                                "fields": [
                                    {
                                        "name": "SCRIPT ERROR!",
                                        "value": f"<@515591638295379968> {fail} of the scripts stopped! check traceback.txt",
                                    },
                                ],
                            }
                        ],
                    }
                )
                fail -= 1
    except KeyboardInterrupt:
        invites.kill()
        posts.kill()
        quit(1)


if __name__ == "__main__":
    main()
