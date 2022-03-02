#############################
# ======== IMPORTS ======== #
#############################

import os
import sys
import time
from subprocess import PIPE, Popen

from _plugin_loader import PluginLoader
from _stdlib import Configs, Logger, p

############################
# ======== PATHS ========= #
############################


ABSPATH = os.path.abspath(__file__)
ABSDIR = p(os.path.dirname(ABSPATH))


###############################
# ======== INSTANCES ======== #
###############################


configs = Configs()
logger = Logger(str(ABSDIR.joinpath("../logs/main.log")), "Main")
plugins = PluginLoader(["on_main_critical"])


##########################
# ======== MAIN ======== #
##########################


def main():
    processes = [
        Popen(
            [sys.executable, str(ABSDIR.joinpath(script))],
            stdout=sys.stdout,
            stderr=PIPE,
        )
        for script in configs.get("main.py", "scripts")
        if not script.startswith("_")
    ]

    try:

        while 1:
            time.sleep(120)

            for process in processes.copy():

                if (exit_code := process.poll()) is not None:

                    _, error = process.communicate()
                    file_name = process.args[1]  # type: ignore

                    error = error.decode("utf-8")

                    logger.critical(
                        "Process %s exited with code %d : %s"
                        % (file_name, exit_code, error)
                    )

                    processes.remove(process)

                    plugins.on(
                        "on_main_critical",
                        file_name=file_name,
                        exit_code=exit_code,
                        error=error,
                    )

            if not len(processes):
                break

    except (SystemExit, KeyboardInterrupt):
        logger.info("SystemExit: terminating processes and exiting with code 1...")

        for process in processes:
            process.kill()

        sys.stdout.flush()
        sys.stderr.flush()

        sys.exit(1)
    return


if __name__ == "__main__":
    main()
