#############################
# ======== IMPORTS ======== #
#############################

import sys
import time
from pathlib import Path as p
from subprocess import PIPE, Popen

import _stdlib as std
from _plugin_loader import PluginLoader

############################
# ======== PATHS ========= #
############################


ABSDIR = p(__file__).parent.absolute()


###############################
# ======== INSTANCES ======== #
###############################


configs = std.Configs()
logger = std.Logger(ABSDIR.joinpath("../logs/main.log"), "Main")
plugins = PluginLoader(["on_main_critical"])


##########################
# ======== MAIN ======== #
##########################


def main():
    """Main entry point."""
    processes = [
        Popen(
            [sys.executable, str(ABSDIR.joinpath(script))],
            stdout=sys.stdout,
            stderr=PIPE,
        )
        for script in configs.get("main.py", "scripts").unwrap()
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
                        file_name=std.json_escape_string(file_name).split("/")[-1],
                        exit_code=exit_code,
                        error=std.json_escape_string(error),
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
