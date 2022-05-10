#############################
# ======== IMPORTS ======== #
#############################

import ctypes
import inspect
import threading
import uuid
from queue import Queue
from typing import Any, Callable, Dict, List, Tuple

from _stdlib import Configs, Logger, p

############################
# ======== PATHS ========= #
############################


ABSDIR = p(__file__).parent.absolute()


#######################################
# ======== PRIVATE INSTANCES ======== #
#######################################

_configs = Configs()
_logger = Logger(ABSDIR.joinpath("../logs/threading.manager.log"), "ThreadingManager")

#############################
# ======== CLASSES ======== #
#############################


# http://tomerfiliba.com/recipes/Thread2/
class StreamThread(threading.Thread):
    def __init__(
        self, target: Callable[[Any], Any], args: "List | Tuple", id_: uuid.UUID
    ):
        super().__init__(target=target, args=args)
        self.id = id_

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.is_alive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():  # type: ignore - Pylance hides "private" members
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)


class ThreadManager:
    def __init__(
        self, target: Callable[[uuid.UUID, Dict[uuid.UUID, List[str]], Queue], None]
    ):
        self.thread_dict = {}
        self.errors = Queue()
        self.target = target
        self.alive = True
        self.running: List[StreamThread] = []
        self.last_running_len: int
        self.modding: List[str] = []

    def initialize(self, subs: List[str]):
        """Initializes the thread manager with the given subs.

        Args:
            subs (List[str]): List of subs to be distributed across all running threads.
        """
        self.modding = subs
        split = self._split_sub_list(subs)

        for sub_list in split:
            self._make_thread(sub_list)

        self.last_running_len = len(self.running)

        _logger.debug(
            "Created %d threads for %d sets of subs" % (len(self.running), len(split))
        )

    def update(self, new_subs: List[str]):
        """Updates all threads with the new given subs, creates new ones if necessary.

        Args:
            new_subs (List[str]): List of subs to add to threads.
        """
        difference = _list_diff(self.modding, new_subs)

        if len(difference[0]):  # stopped modding.
            _logger.info(f"Stopped modding: {difference[0]}")
            for thread in self.running:
                for sub in difference[0]:
                    if sub in self.thread_dict[thread.id]:
                        try:
                            self.thread_dict[thread.id].remove(sub)
                        except BaseException:
                            continue

        if len(difference[1]):  # subs we started modding
            _logger.info(f"Started modding: {difference[1]}")
            to_add = difference[1]

            limit = _configs.get("threading", "max_subs_per_thread")

            for thread in self.running:
                if (length := len(self.thread_dict[thread.id])) < limit:
                    fill_add = self._fill_thread(to_add, length)
                    self.thread_dict[thread.id] += fill_add[0]
                    to_add = fill_add[1]
                if not len(to_add):
                    break

            if len(to_add):
                for sub_list in self._split_sub_list(to_add):
                    self._make_thread(sub_list)
                _logger.info(f"Threads created: {len(to_add)}")

        self.modding = new_subs
        _logger.debug(
            "Running Threads [%d => %d] %d are alive."
            % (
                self.last_running_len,
                len(self.running),
                len([t for t in self.running if t.is_alive()]),
            )
        )

        self.last_running_len = len(self.running)

    def check_errors(self):
        """Checks all running threads for errors, returns the first error it finds.

        Returns:
            Type[BaseException]
        """
        if self.errors.empty():
            return None

        error = self.errors.get()

        _logger.critical("An exception went unhandled: %s" % error)

        self._end()

        return error

    def check_running(self):
        """Checks all running threads and removes dead ones from the running list."""
        killed = 0

        for thread in self.running.copy():
            if not thread.is_alive():
                killed += 1
                self.running.remove(thread)

        if killed:
            _logger.info("Popped %d dead thread(s)" % killed)

    def _end(self):
        """Kill all threads"""

        for thread in self.running.copy():
            if thread.is_alive():
                thread.terminate()
                thread.join()

            self.running.remove(thread)

        self.alive = False

        _logger.info("Threads were terminated!")

    def _generate_safe_id(self) -> uuid.UUID:
        """Generates an ID for a thread that is not already present (unlikely).

        Returns:
            uuid.UUID: The ID
        """
        _id = uuid.uuid4()
        while _id in self.thread_dict.keys():
            _id = uuid.uuid4()
        return _id

    def _make_thread(self, subs: List[str]):
        """Creates and adds a thread to the running list and dict given the subs it should mod.

        Args:
            subs (List[str])
        """
        id_ = self._generate_safe_id()
        thread = StreamThread(self.target, (id_, self.thread_dict, self.errors), id_)  # type: ignore - Pylance thinks generic type `Any` should match with static types for some reason
        self.thread_dict[id_] = subs
        self.running.append(thread)
        thread.start()
        return

    def _fill_thread(self, new: list, filled: int):
        """Fills a list based on the limit defined as std.LIMIT and returns the remainder.

        Args:
            new (list): The list to be filled.
            filled (int): How much of the other list is filled.

        Returns:
            Tuple[List[str], List[str]]: The list of elements that can fit in a list already filled by `filled` items and limited by `std.LIMIT`, the remainder.
        """
        limit = _configs.get("threading", "max_subs_per_thread")
        return (
            [x for idx, x in enumerate(new) if idx < limit - filled],
            [x for idx, x in enumerate(new) if idx >= limit - filled],
        )

    def _split_sub_list(self, subs: List[str]):
        """Splits a list into a list of lists with a maximum amount of items determined by std.LIMIT

        Args:
            subs (list): The list.

        Returns:
            List[List[str]]: The now splitted list.
        """
        limit = _configs.get("threading", "max_subs_per_thread")
        return [subs[x : x + limit] for x in range(0, len(subs), limit)]


class BanQueue:
    def __init__(self):
        self._queue: List[str] = []

    def put(self, obj: Any):
        self._queue.append(obj)

    def get(self) -> "str | None":
        return self._queue.pop(0) if len(self._queue) else None

    def is_empty(self):
        return not len(self._queue)

    def is_full(self):
        return len(self._queue)


###############################
# ======== FUNCTIONS ======== #
###############################


def _list_diff(list_: list, other: list) -> Tuple[List[Any], List[Any]]:
    """Difference between two lists.

    Args:
        list_ (list): list number 1
        other (list): list number 2

    Returns:
        Tuple[list]: Difference between the two lists. `[0]` == `list_` - `other`, `[1]` == `other` - `list_`
    """
    return ([x for x in list_ if x not in other], [x for x in other if x not in list_])


def _async_raise(tid, exctype):
    """Raises the exception, performs cleanup if needed."""
    # cspell: disable-next-line
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), ctypes.py_object(exctype)
    )
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
        #                                                   ^  needs to be c_long to work, I'm not sure about `0`.
        raise SystemError("PyThreadState_SetAsyncExc failed")
