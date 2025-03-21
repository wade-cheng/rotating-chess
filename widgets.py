from __future__ import annotations

import pygame
from pygame.locals import *
import math
import random
import settings
from pieces import Piece, Side
import sys, platform
from pathlib import Path
from datetime import datetime

# gamestate is a circular import
# this block and __future__'s annotations fixes type checking
from typing import TYPE_CHECKING

# from gamestate import GameState

if TYPE_CHECKING:
    from gamestate import GameState

MOUSE_HELD = pygame.USEREVENT + 1


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

    def draw(self, screen: pygame.Surface, gs: GameState):
        pass


def max_hit_distance(start_x: float, start_y: float, end_x: float, end_y: float) -> float:
    """simple distance formula + hitcirclerad"""
    return math.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2) + settings.HITCIRCLE_RADIUS


def distance(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    point_x: float,
    point_y: float,
) -> float:
    """finds the distance from a point to a line, where the line is given by two points"""
    return abs((end_x - start_x) * (point_y - start_y) - (point_x - start_x) * (end_y - start_y)) / math.sqrt(
        (end_x - start_x) ** 2 + (end_y - start_y) ** 2
    )


def scalar_comp(
    start_x: float,
    start_y: float,
    point_x: float,
    point_y: float,
    dir_x: float,
    dir_y: float,
) -> float:
    """finds the scalar composition of vectors point in the direction of dir where the vectors have starting point start"""
    # scalar comp of v in the direction of u: we find u dot v / magn(u)
    u = [dir_x - start_x, dir_y - start_y]
    v = [point_x - start_x, point_y - start_y]

    return (u[0] * v[0] + u[1] * v[1]) / math.sqrt(u[0] ** 2 + u[1] ** 2)


class Pieces(Widget):
    def __init__(self) -> None:
        self.skin = settings.SKIN
        self.pieces: list[Piece] = []
        # invariant: forall Piece in selected_pieces, Piece.selected
        # invariant: forall Piece not in selected_pieces, not Piece.selected
        # checked every time we MOUSEBUTTONDOWN
        self.selected_pieces: list[Piece] = []

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            assert all(p.selected for p in self.selected_pieces)
            assert all(not p.selected for p in set(self.pieces) - set(self.selected_pieces))
            # check and update if we've moved a piece, promoting as needed
            moved_piece = False
            if len(self.selected_pieces) == 1:
                only_selected = self.selected_pieces[0]
                for point_x, point_y in only_selected.get_movable_points():
                    if (((x - point_x) ** 2 + (y - point_y) ** 2) < settings.HITCIRCLE_RADIUS**2) and self.canmove(
                        only_selected, point_x, point_y
                    ):
                        self.move(only_selected, point_x, point_y, gs)
                        # note: self.move() already removes the piece from selected, but we still have the pointer.
                        if only_selected.should_promote():
                            self.promote(only_selected)

                        moved_piece = True
                        break

            if moved_piece:
                gs.nav.record_turn(gs.widgets.pieces.pieces)
                return

            # check if we've clicked a piece
            for piece in self.pieces:
                if piece.coord_collides(x, y):
                    piece.selected = not piece.selected
                    if piece.selected:
                        gs.widgets.cancel_rot.reveal()
                        gs.widgets.movesel.reveal()
                        gs.widgets.pieces.selected_pieces.append(piece)
                        if gs.widgets.movesel.get_selected_point() is not None:
                            piece.set_preview_angle(gs.widgets.movesel.selected_angle())
                    else:
                        self.selected_pieces.remove(piece)
                        piece.stop_previewing()
                        if len(self.selected_pieces) == 0:
                            gs.widgets.movesel.hide(gs)

                    if not settings.CAN_SELECT_MULTIPLE and len(self.selected_pieces) == 2:
                        self.selected_pieces[0].selected = False
                        self.selected_pieces[0].stop_previewing()
                        self.selected_pieces.pop(0)
                        self.selected_pieces[0].stop_previewing()
                        gs.widgets.movesel.hide(gs)
                        gs.widgets.cancel_rot.reveal()
                        gs.widgets.movesel.reveal()

                    # if len(self.selected_pieces) != 0:
                    #     gs.widgets.movesel.reveal()
                    # else:
                    #     gs.widgets.movesel.hide(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        # draw pieces
        for piece in self.pieces:
            piece.draw(screen)
            if len(self.selected_pieces) == 1:
                piece.draw_hitcircle(screen)

        if len(self.selected_pieces) == 1:
            self.selected_pieces[0].draw_move_points(screen)
            self.selected_pieces[0].draw_capture_points(screen)
            self.selected_pieces[0].draw_guide_lines(screen)

    def canmove(self, only_selected: Piece, point_x: float, point_y: float) -> bool:
        """checks if we can move the only selected piece to point_x, point_y"""
        assert len(self.selected_pieces) == 1

        pieces_overlapping_endpoint = 0

        # disallow capturing own side. also update how many pieces overlap the endpoint
        for piece in self.pieces:
            if piece == only_selected:
                continue

            if piece.piece_collides(point_x, point_y):
                pieces_overlapping_endpoint += 1

                if piece.get_side() == only_selected.get_side():
                    return False

        if only_selected.can_jump:
            return True

        in_the_way: int = 0
        for piece in self.pieces:
            if piece == only_selected:
                continue

            if (
                0
                < scalar_comp(
                    only_selected.get_x(),
                    only_selected.get_y(),
                    piece.get_x(),
                    piece.get_y(),
                    point_x,
                    point_y,
                )
                < max_hit_distance(only_selected.get_x(), only_selected.get_y(), point_x, point_y)
            ):
                # piece is within correct distance to block. now check:
                if (
                    distance(
                        only_selected.get_x(),
                        only_selected.get_y(),
                        point_x,
                        point_y,
                        piece.get_x(),
                        piece.get_y(),
                    )
                    < 2 * settings.HITCIRCLE_RADIUS
                ):
                    # piece is within correct point to line distance to block. we may be blocked unless we can capture this piece.
                    in_the_way += 1
        #     if piece in the scalar projection direction is >= 0 but < the max hit distance
        #     and if piece is less than 2*hitcirclerad away from line:
        #         in_the_way.append(piece)

        print(f"inway: {in_the_way}, overlaps: {pieces_overlapping_endpoint}")
        if in_the_way > pieces_overlapping_endpoint:
            return False
        # if len(in_the_way) > len(pieces overlapping endpoint):
        #     return False

        return True

    def move(self, only_selected: Piece, point_x: float, point_y: float, gs: GameState | None):
        """
        moves only_selected to x,y, capturing any overlapping pieces.
        use with gs=None in testing when we create a board without visualization.
        """
        assert len(self.selected_pieces) == 1

        only_selected.move(point_x, point_y)

        for piece in self.pieces:
            if piece == only_selected:
                continue

            if only_selected.piece_collides(piece.get_x(), piece.get_y()):
                self.pieces.remove(piece)

        # after moving, automatically deselect the piece and spinner
        only_selected.selected = False
        self.selected_pieces.pop()
        if gs is not None:
            gs.widgets.movesel.hide(gs)

    def promote(self, piece: Piece, assets: dict[str, pygame.Surface], piece_skin: settings.PieceSkin):
        x, y, rad, side = (
            piece.get_x(),
            piece.get_y(),
            piece.get_angle(),
            piece.get_side(),
        )
        self.pieces.remove(piece)
        if side == Side.BLACK:
            side_str = "B"
        elif side == Side.WHITE:
            side_str = "W"
        self.pieces.append(Piece(x, y, rad, side, assets[f"piece_queen{side_str}{piece_skin.value}"], "queen"))  # fmt: skip

    # fmt: off
    def load_normal_board(self, assets: dict[str, pygame.Surface], piece_skin: settings.PieceSkin):
        self.pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.pieces.append(Piece(x_pos, 75, math.radians(180), Side.BLACK, assets[f"piece_pawnB{piece_skin.value}"], "pawn"))
            self.pieces.append(Piece(x_pos, 75 + 250, 0, Side.WHITE, assets[f"piece_pawnW{piece_skin.value}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.pieces.append(Piece(x_pos, 25, math.radians(180), Side.BLACK, assets[f"piece_{order[orderidx]}B{piece_skin.value}"], order[orderidx]))
            self.pieces.append(Piece(x_pos, 25 + 350, 0, Side.WHITE, assets[f"piece_{order[orderidx]}W{piece_skin.value}"], order[orderidx]))
    # fmt: on

    # fmt: off
    def load_chess_960(self, assets: dict[str, pygame.Surface], piece_skin: settings.PieceSkin):
        self.pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.pieces.append(Piece(x_pos, 75, math.radians(random.randint(-180, 180)), Side.BLACK, assets[f"piece_pawnB{piece_skin.value}"], "pawn"))
            self.pieces.append(Piece(x_pos, 75 + 250, math.radians(random.randint(-180, 180)), Side.WHITE, assets[f"piece_pawnW{piece_skin.value}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        random.shuffle(order)
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.pieces.append(Piece(x_pos, 25, math.radians(random.randint(-180, 180)), Side.BLACK, assets[f"piece_{order[orderidx]}B{piece_skin.value}"], order[orderidx]))
            self.pieces.append(Piece(x_pos, 25 + 350, math.radians(random.randint(-180, 180)), Side.WHITE, assets[f"piece_{order[orderidx]}W{piece_skin.value}"], order[orderidx]))
    # fmt: on


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
        gs.widgets.cancel_rot.hide(gs)
        gs.widgets.confirm_rot.hide(gs)

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
        elif e.type == MOUSE_HELD:
            if not self.selecting:
                return

            self.select_rotcircle(x, y, gs)
            for piece in gs.widgets.pieces.selected_pieces:
                piece.update_capture_points()
                piece.update_move_points()

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not self._visible:
            return

        pygame.draw.circle(screen, (255, 255, 255), self.__center, self.__radius, width=1)
        if self.__selected_point is not None:
            pygame.draw.line(screen, (255, 255, 255), self.__selected_point, self.__center, width=1)
            pygame.draw.circle(screen, (255, 0, 0), self.__selected_point, radius=5, width=1)

    def coord_collides(self, x: int, y: int) -> bool:
        return ((x - self.__center[0]) ** 2 + (y - self.__center[1]) ** 2) < self.__radius**2

    def select_rotcircle(self, x: int, y: int, gs: GameState):
        gs.widgets.confirm_rot.reveal()

        self.__selected_point = (x, y)

        theta: float = self.selected_angle()
        for piece in gs.widgets.pieces.selected_pieces:
            piece.set_preview_angle(theta)

    def selected_angle(self) -> float:
        """requires a point to be selected. returns the selected angle in radians in the range (-pi, pi).
        uses `-1 * math.atan2(y, x)` to invert the 'upside-downnedness' of topleft (0,0) coordinate system positioning.
        """
        assert self.__selected_point is not None

        y = self.__selected_point[1] - self.__center[1]
        x = self.__selected_point[0] - self.__center[0]
        # not sure why this is opposite of the convention that I know of but whatever, I can just invert it
        # NOTE: it was because I forgot pygame considers positive x to be facing "down." whoops.
        return -1 * math.atan2(y, x)

    def get_selected_point(self) -> tuple[int, int] | None:
        return self.__selected_point


class Button(Widget):
    # if one button is clicked, we should prevent buttons "under" it from being clicked.
    one_clicked: bool = False

    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__()
        self._surface = surface
        self.__x = x
        self.__y = y
        self._rect = surface.get_rect(left=x, top=y)
        self.hovered: bool = False

    def check_clicked(self, x: int, y: int) -> bool:
        """
        should be run whenever we check if a button is clicked.
        this lets us manipulate Button.one_clicked.
        returns whether a click at x, y has clicked this button
        """
        if Button.one_clicked:
            return False

        if self.check_hovered(x, y):
            Button.one_clicked = True
            return True

        return False

    def check_hovered(self, x: int, y: int) -> bool:
        """
        should be run whenever we check if a button is hovered over.
        """
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
            if not gs.widgets.cancel_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.widgets.movesel.hide(gs)
            for piece in gs.widgets.pieces.selected_pieces:
                # according to invariant, this should set all to false.
                # setting not piece.selected is sorta like verifying invariant
                piece.selected = not piece.selected
                piece.stop_previewing()
            gs.widgets.pieces.selected_pieces.clear()


class ConfirmRot(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)
        self._visible = False

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not gs.widgets.confirm_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.widgets.movesel.hide(gs)
            for piece in gs.widgets.pieces.selected_pieces:
                # according to invariant, this should set all to false.
                # setting not piece.selected is sorta like verifying invariant
                piece.selected = not piece.selected
                piece.confirm_preview()
            gs.widgets.pieces.selected_pieces.clear()

            gs.nav.record_turn(gs.widgets.pieces.pieces)


class NavFirst(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets.cancel_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.nav.first()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets.cancel_rot.is_visible():
            super().draw(screen, gs)


class NavPrev(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets.cancel_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.nav.prev()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets.cancel_rot.is_visible():
            super().draw(screen, gs)


class NavNext(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets.cancel_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.nav.next()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets.cancel_rot.is_visible():
            super().draw(screen, gs)


class NavLast(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__(surface, x, y)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if gs.widgets.cancel_rot.is_visible():
                return

            if not self.check_clicked(x, y):
                return

            gs.nav.last()
            gs.nav.update_state(gs)

    def draw(self, screen: pygame.Surface, gs: GameState):
        if not gs.widgets.cancel_rot.is_visible():
            super().draw(screen, gs)


class ExportSave(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int, font: pygame.font.Font) -> None:
        super().__init__(surface, x, y)
        self.hover_text = font.render(
            "export save",
            antialias=False,
            color=(255, 255, 255),
            bgcolor=(181, 136, 99),
        )
        self.hover_rect = self.hover_text.get_rect()
        self.hover_text_visible = False
        self.hover_x = 0
        self.hover_y = 0

    def download_save(self, s: str):
        savedir = Path("game_saves")
        savedir.mkdir(parents=True, exist_ok=True)

        savepath = f"game_saves/rotchess_save_{datetime.now().isoformat().replace(':', '').split('.')[0]}"

        with open(savepath, "w") as f:
            f.write(s)
        if sys.platform == "emscripten":
            print("got here")
            platform.window.MM.download(savepath)
        else:
            with open(savedir / savepath, "w") as f:
                f.write(s)

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not self.check_clicked(x, y):
                return

            save = gs.nav.get_game_save()
            print("save:")
            print(save)
            self.download_save(save)
        elif e.type == pygame.MOUSEMOTION:
            if self.check_hovered(x, y):
                self.hover_text_visible = True
                self.hover_x, self.hover_y = x, y
            else:
                self.hover_text_visible = False

    def draw(self, screen: pygame.Surface, gs: GameState):
        super().draw(screen, gs)
        if self.hover_text_visible:
            screen.blit(self.hover_text, (self.hover_x - self.hover_rect.width, self.hover_y))


class ImportSave(Button):
    def __init__(self, surface: pygame.Surface, x: int, y: int, font: pygame.font.Font) -> None:
        super().__init__(surface, x, y)
        self.hover_text = font.render(
            "import save",
            antialias=False,
            color=(255, 255, 255),
            bgcolor=(181, 136, 99),
        )
        self.hover_rect = self.hover_text.get_rect()
        self.hover_text_visible = False
        self.hover_x = 0
        self.hover_y = 0

    def handle_event(self, e: pygame.Event, gs: GameState, x: int, y: int) -> None:
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not self.check_clicked(x, y):
                return

            if sys.platform == "emscripten":
                save = platform.window.prompt("paste game save")
                if save is not None and not gs.nav.load_game_save(save, gs):
                    platform.window.alert("invalid save")
            else:
                if not gs.nav.load_game_save(input("paste game save > "), gs):
                    print("invalid save")

        elif e.type == pygame.MOUSEMOTION:
            if self.check_hovered(x, y):
                self.hover_text_visible = True
                self.hover_x, self.hover_y = x, y
            else:
                self.hover_text_visible = False

    def draw(self, screen: pygame.Surface, gs: GameState):
        super().draw(screen, gs)
        if self.hover_text_visible:
            screen.blit(self.hover_text, (self.hover_x - self.hover_rect.width, self.hover_y))

if __name__ == "__main__":
    print(f"d={distance(0,0, 10,0, 4,3)}")
    print(f"d={distance(2,0, 0,2, 0,0)}")

    print(f"comp={scalar_comp(1,1, 5,5, 5,1)}")
