from __future__ import annotations

import pygame
from pygame.locals import *
import math
import settings
from pieces import Piece

# gamestate is a circular import
# this block and __future__'s annotations fixes type checking
from typing import TYPE_CHECKING

# from gamestate import GameState

if TYPE_CHECKING:
    from gamestate import GameState


class Widget:
    """
    anything that might possibly need to handle events. 
    should probably eventually extend pygame's Sprite so we can use LayeredUpdates
    """
    def __init__(self) -> None:
        self._visible: bool = True
        
    def reveal(self):
        self._visible = True

    def hide(self, gs: GameState):
        self._visible = False

    def is_visible(self) -> bool:
        return self._visible
        
    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        pass

    def handle_mouse_hold(self, gs: GameState, x: int, y: int) -> None:
        pass

    def draw(self, screen: pygame.Surface, gs: GameState):
        pass
    
class Pieces(Widget):
    def __init__(self) -> None:
        self.skin = settings.SKIN
        self.pieces: list[Piece] = []
        # invariant: forall Piece in selected_pieces, Piece.selected
        # invariant: forall Piece not in selected_pieces, not Piece.selected
        self.selected_pieces: list[Piece] = []

    def draw(self, screen: pygame.Surface, gs: GameState):
        # draw pieces
        for piece in self.pieces:
            piece.draw(screen)
            if len(self.selected_pieces) == 1:
                piece.draw_hitcircle(screen)

        if len(self.selected_pieces) == 1:
            self.selected_pieces[0].draw_move_points(screen)
            self.selected_pieces[0].draw_capture_points(screen)

class MoveSelector(Widget):
    def __init__(self, center: tuple[int, int], radius: int):
        # center [x, y]
        super().__init__()
        self.__center: tuple[int, int] = center
        self.__radius: int = radius
        self.__selected_point: tuple[int, int] | None = None
        self.selecting: bool = False

        self._visible = False

    def reveal(self):
        self._visible = True

    def hide(self, gs: GameState):
        self._visible = False
        self.__selected_point = None
        gs.widgets["cancel_rot"].hide(gs)
        gs.widgets["confirm_rot"].hide(gs)

    def is_visible(self) -> bool:
        return self._visible
    
    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONUP:
            self.selecting = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            # check if we've started to move the rotation move selector
            if self.is_visible() and self.coord_collides(x, y):
                self.selecting = True
                self.select_rotcircle(x, y, gs)

    def handle_mouse_hold(self, gs: GameState, x: int, y: int) -> None:
        if not self.selecting:
            return
        
        self.select_rotcircle(x, y, gs)
        for piece in gs.selected_pieces:
            piece.update_capture_points()
            piece.update_move_points()

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not self._visible:
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

    def coord_collides(self, x: int, y: int) -> bool:
        return (
            (x - self.__center[0]) ** 2 + (y - self.__center[1]) ** 2
        ) < self.__radius ** 2

    def select_rotcircle(self, x: int, y: int, gs: GameState):
        gs.widgets["confirm_rot"].reveal()

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


class Button(Widget):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__()
        self._surface = surface
        self.__x = x
        self.__y = y
        self._rect = surface.get_rect(left=x, top=y)
        self.hovered: bool = False

    def clicked(self, x: int, y: int) -> bool:
        """returns whether a click at x, y has clicked this button"""
        return self._rect.collidepoint(x, y)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if self.is_visible():
            screen.blit(self._surface, self._rect)

        if self.hovered:
            pygame.draw.rect(screen, color=(255, 255, 255), rect=self._rect, width=1)


class CancelRot(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)
        self._visible = False

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not gs.widgets["cancel_rot"].is_visible():
                return
            
            if not self.clicked(x, y):
                return

            gs.widgets["movesel"].hide(gs)
            for piece in gs.selected_pieces:
                # according to invariant, this should set all to false.
                # setting not piece.selected is sorta like verifying invariant
                piece.selected = not piece.selected
                piece.stop_previewing()
            gs.selected_pieces.clear()

class ConfirmRot(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)
        self._visible = False

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not gs.widgets["confirm_rot"].is_visible():
                return 
            
            if not self.clicked(x, y):
                return

            gs.widgets["movesel"].hide(gs)
            for piece in gs.selected_pieces:
                # according to invariant, this should set all to false.
                # setting not piece.selected is sorta like verifying invariant
                piece.selected = not piece.selected
                piece.confirm_preview()
            gs.selected_pieces.clear()

            gs.nav.record_turn(gs.pieces)

class NavFirst(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets["cancel_rot"].is_visible():
                return
            
            if not self.clicked(x, y):
                return
            
            gs.nav.first()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets["cancel_rot"].is_visible():
            super().draw(screen, gs)

class NavPrev(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets["cancel_rot"].is_visible():
                return
            
            if not self.clicked(x, y):
                return
            
            gs.nav.prev()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets["cancel_rot"].is_visible():
            super().draw(screen, gs)

class NavNext(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets["cancel_rot"].is_visible():
                return
            
            if not self.clicked(x, y):
                return
            
            gs.nav.next()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets["cancel_rot"].is_visible():
            super().draw(screen, gs)

class NavLast(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets["cancel_rot"].is_visible():
                return
            
            if not self.clicked(x, y):
                return
            
            gs.nav.last()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets["cancel_rot"].is_visible():
            super().draw(screen, gs)