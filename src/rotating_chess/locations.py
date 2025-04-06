from pygame.math import Vector2
import string


def rank_to_pos(rank: str) -> float:
    try:
        rank = int(rank)
    except ValueError:
        raise ValueError("rank must be coercable to int")

    return (8 * 50) - (
        rank * 50 - 25
    )  # the rank pos, with flip because pygame y is top-down


def file_to_pos(file: str) -> float:
    try:
        assert len(file) == 1
        assert file in string.ascii_lowercase
    except AssertionError:
        raise ValueError("file must be a valid string value")

    return (ord(file) - ord("a")) * 50 + 25


def at(location: str) -> Vector2:
    """
    Gets the pygame location of an algebraic notation location.

    If notations are split by a `/`, returns the average of their locations.

    >>> at("e4")
    Vector2(225, 225)
    >>> at("d5")
    Vector2(175, 175)
    >>> at("e4/d5")
    Vector2(200, 200)
    >>> at("e3/e4/e5") == at("e4")
    True
    """
    try:
        locations = location.split("/")
        assert all(len(l) == 2 for l in locations)
    except AssertionError:
        raise ValueError("must use a valid string value like a1, e4")
    locations = [Vector2(file_to_pos(l[0]), rank_to_pos(l[1])) for l in locations]
    return sum(locations, start=Vector2(0, 0)) / len(locations)
