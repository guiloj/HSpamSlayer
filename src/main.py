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

import os
import time
import sys
from subprocess import Popen, PIPE
import _stdmodule as std

###############################################
# FILE MANAGEMENT
###############################################

# ? correctly finds the path to the main.py file to
# ? manage the modules and libs

ABSPATH = os.path.abspath(__file__)
os.chdir(os.path.dirname(ABSPATH))

###############################################
# MAIN
###############################################

# TODO: (@guiloj) add tests for all scripts


def main():
    # * (@guiloj) starts all bot scripts simultaneously
    processes = [
        Popen([sys.executable, script], stdout=sys.stdout, stderr=PIPE)
        for script in ["accept_invites.py", "mod_posts.py"]
    ]
    try:
        while 1:

            time.sleep(100)

            # * (@guiloj) checks if any of the scripts stopped unexpectedly
            for idx, process in enumerate(processes):
                if (code := process.poll()) != None:
                    _, err = process.communicate()
                    err = str(err)
                    name = process.args[1]

                    std.add_to_traceback(f"{name}: {code}\n{err}")

                    processes.pop(idx)

                    # ? (@guiloj) to alert owner that one of the scripts have stopped, is on `../config/config.json`
                    if std.config("webhooks")["use"]:
                        message = std.format_webhook(
                            std.config("webhooks")["main_critical"],
                            filename=name,
                            exitcode=code,
                            error=err,
                        )
                        std.send_to_webhook(message)

            if not len(processes):
                break

    except KeyboardInterrupt:
        std.logger.info(
            "KeyboardInterrupt: terminating processes and exiting with code 1..."
        )
        for process in processes:
            process.kill()
        quit(1)


if __name__ == "__main__":
    main()
