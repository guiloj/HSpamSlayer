#############################
# ======== IMPORTS ======== #
#############################

import importlib
import sys
import threading
import time
from pathlib import Path as p
from types import ModuleType
from typing import Dict, List, Tuple

import _stdlib as std

############################
# ======== PATHS ========= #
############################


ABSDIR = p(__file__).parent.absolute()

sys.path.append(str(ABSDIR.joinpath("../plugins")))


#######################################
# ======== PRIVATE INSTANCES ======== #
#######################################


_configs = std.Configs()

_logger = std.Logger(ABSDIR.joinpath("../logs/plugin.loader.log"), "PluginLoader")

_plugins = _configs.get("plugins").unwrap()


###########################
# ======== DATA ========= #
###########################


class PluginLoader:
    def __init__(self, types: List[str]):
        self.plugins = self._load_plugins(types)
        self._running: List[Tuple[threading.Thread, float]] = []

    def _load(self, plugin: Dict[str, str]) -> ModuleType:
        return importlib.import_module(plugin["script"].replace(".py", ""))

    def _load_plugins(self, types: List[str]) -> List[Tuple[ModuleType, List[str]]]:
        result = []
        for plugin in _plugins:
            if any(t in plugin["types"] for t in types):
                result.append((self._load(plugin), plugin["types"]))

                _logger.debug("%s was loaded!" % plugin["script"])
        return result

    def _detach(self, plugin: Tuple[ModuleType, List[str]], *args, **kwargs):
        detached = threading.Thread(
            target=plugin[0].main, args=args, kwargs=kwargs
        )  # maybe use killable threads here.
        self._running.append((detached, time.time()))
        detached.start()

    def on(self, type_: str, *args, **kwargs):
        args_ = [type_] + list(args)

        for plugin in self.plugins:
            if type_ in plugin[1]:
                self._detach(plugin, *args_, **kwargs)

    def check(self):
        for thr_obj in self._running.copy():
            thread, start = thr_obj

            if not thread.is_alive:
                self._running.remove(thr_obj)

            elif start > (time.time() + 600):
                _logger.error(
                    "Plugin thread %s has been running for more then 10 minutes!"
                    % thread.name
                )
            elif start > (time.time() + 60 * 5):
                _logger.warning(
                    "Plugin thread %s has been running for more then 5 minutes!"
                    % thread.name
                )
