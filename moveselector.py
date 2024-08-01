from __future__ import annotations

import pygame
from pygame.locals import *
import math

# gamestate is a circular import
# this block and __future__'s annotations fixes type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gamestate import GameState


class MoveSelector:
    def __init__(self, center: tuple[int, int], radius: int):
        # center [x, y]
        self.__center: tuple[int, int] = center
        self.__radius: int = radius
        self.__selected_point: tuple[int, int] | None = None
        self.__visible: bool = False
        self.selecting: bool = False

    def draw(self, screen: pygame.Surface):
        if not self.__visible:
            return

        pygame.draw.circle(
            screen, (255, 255, 255), self.__center, self.__radius, width=1
        )
        if self.__selected_point is not None:
            pygame.draw.line(
                screen, (255, 255, 255), self.__selected_point, self.__center, width=1
            )
            pygame.draw.circle(
                screen, (255, 0, 0), self.__selected_point, radius=5, width=1
            )

    def reveal(self):
        self.__visible = True

    def hide(self, gs: GameState):
        self.__visible = False
        self.__selected_point = None
        gs.cross_showing = False
        gs.check_showing = False

    def is_visible(self) -> bool:
        return self.__visible

    def coord_collides(self, x: int, y: int) -> bool:
        return (
            (x - self.__center[0]) ** 2 + (y - self.__center[1]) ** 2
        ) < self.__radius ** 2

    def select_rotcircle(self, x: int, y: int, gs: GameState):
        gs.check_showing = True

        self.__selected_point = (x, y)

        theta: float = self.selected_angle()
        for piece in gs.selected_pieces:
            piece.set_preview_angle(theta)

    def selected_angle(self) -> float:
        """requires a point to be selected. returns the selected angle in radians in the range (-pi, pi).
        uses `-1 * math.atan2(y, x)` to invert the 'upside-downnedness' of topleft (0,0) coordinate system positioning."""
        assert self.__selected_point is not None

        y = self.__selected_point[1] - self.__center[1]
        x = self.__selected_point[0] - self.__center[0]
        # not sure why this is opposite of the convention that I know of but whatever, I can just invert it
        # NOTE: it was because I forgot pygame considers positive x to be facing "down." whoops.
        return -1 * math.atan2(y, x)

    def get_selected_point(self) -> tuple[int, int] | None:
        return self.__selected_point
