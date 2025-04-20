from collections.abc import Callable
import os


def dprint(s: str | Callable[[], str]):
    if not isinstance(s, str):
        s = s()

    debug = os.getenv("DEBUG_ROTCHESS", "False")
    if debug == "True":
        print(s)


def dassert(s: Callable[[], bool]):
    debug = os.getenv("DEBUG_ROTCHESS", "False")
    if debug == "True":
        assert s()
