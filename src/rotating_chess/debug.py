DEBUG: bool = True


def d_print(s: str):
    if DEBUG:
        print(s)


# NOTE: this doesn't actually prevent evaluation of any costly asserts if debug mode is off.
# NOTE: this also doesn't help mypy with type checking.
def d_assert(b: bool):
    if DEBUG:
        assert b
