from pygame import Surface
from pieces import *
from widgets import *
import os
import random
import math
import settings
import copy
from enum import Enum
from compressjson import json_compress, json_decompress
import json


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


class Screen(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    GAME = 3


class GameState:
    def __init__(self) -> None:
        self.playing: bool = True

        # loading assets
        self.assets: dict[str, pygame.Surface] = dict()
        self.load_img_assets()

        pygame.font.init()
        self.font = pygame.font.Font("assets/hero-speak.ttf", 14)
        # text = font.render('the creator of this game said they wanted to show you something cool.', True, (0,0,0), wraplength=MAP_WIDTH - 20)

        self.piece_skin: settings.PieceSkin = settings.SKIN
        # invariant: forall Piece in selected_pieces, Piece.selected
        # invariant: forall Piece not in selected_pieces, not Piece.selected

        # fmt: off
        f_width, p_width, n_width, l_width = 58, 37, 41, 54
        class Widgets:
            def __init__(wself):
                wself.pieces = Pieces()
                wself.movesel = MoveSelector(center=(500, 200), radius=80)
                wself.cancel_rot = CancelRot(self.assets["cross_white"], 500 - 28, 300)
                wself.confirm_rot = ConfirmRot(self.assets["check_white"], 500 - 28, 50)
                wself.nav_first_btn = NavFirst(self.assets["nav_first"], 400 + 3, 300)
                wself.nav_prev_btn = NavPrev(self.assets["nav_prev"], 400 + 4 + f_width, 300)
                wself.nav_next_btn = NavNext(self.assets["nav_next"], 400 + 5 + f_width + p_width, 300)
                wself.nav_last_btn = NavLast(self.assets["nav_last"], 400 + 6 + f_width + p_width + n_width, 300)
                wself.exp_save = ExportSave(self.assets["download"], 415, 10, self.font)
                wself.imp_save = ImportSave(self.assets["upload"], 540, 10, self.font)
        self.widgets = Widgets()
        {
            "pieces": Pieces(),
            "movesel": MoveSelector(center=(500, 200), radius=80),
            "cancel_rot": CancelRot(self.assets["cross_white"], 500 - 28, 300),
            "confirm_rot": ConfirmRot(self.assets["check_white"], 500 - 28, 50),
            "nav_first_btn": NavFirst(self.assets["nav_first"], 400 + 3, 300),
            "nav_prev_btn": NavPrev(self.assets["nav_prev"], 400 + 4 + f_width, 300),
            "nav_next_btn": NavNext(self.assets["nav_next"], 400 + 5 + f_width + p_width, 300),
            "nav_last_btn": NavLast(self.assets["nav_last"], 400 + 6 + f_width + p_width + n_width, 300),
            "exp_save": ExportSave(self.assets["download"], 415, 10, self.font),
            "imp_save": ImportSave(self.assets["upload"], 540, 10, self.font),
        }
        # fmt: on

        # self.load_chess_960()
        self.load_normal_board()

        self.nav: TurnNavigation = TurnNavigation(self.widgets["pieces"].pieces)

    def load_img_assets(self):
        """
        loads every file in assets dir to self.assets.
        strips .png and .svg suffixes, so the surface for a file named 'queen.png'
        can be accessed with self.assets['queen']
        """
        # TODO this sorely needs refactoring if we ever want to have more image extensions
        # we might not want more though, to be honest. this works so it's fine.
        for file in os.listdir("assets"):
            if not file.endswith(".png") and not file.endswith(".svg"):
                print(f"not loading {file} with load_img_assets()")
                continue
            self.assets[file.removesuffix(".png").removesuffix(".svg")] = pygame.image.load(f"assets/{file}")
        print(f"loaded assets:\n{self.assets.keys()}")

    def canmove(self, only_selected: Piece, point_x: float, point_y: float) -> bool:
        """checks if we can move the only selected piece to point_x, point_y"""
        assert len(self.widgets["pieces"].selected_pieces) == 1

        pieces_overlapping_endpoint = 0

        # disallow capturing own side. also update how many pieces overlap the endpoint
        for piece in self.widgets["pieces"].pieces:
            if piece == only_selected:
                continue

            if piece.piece_collides(point_x, point_y):
                pieces_overlapping_endpoint += 1

                if piece.get_side() == only_selected.get_side():
                    return False

        if only_selected.can_jump:
            return True

        in_the_way: int = 0
        for piece in self.widgets["pieces"].pieces:
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

    def move(self, only_selected: Piece, point_x: float, point_y: float):
        """moves only_selected to x,y, capturing any overlapping pieces"""
        assert len(self.widgets["pieces"].selected_pieces) == 1

        only_selected.move(point_x, point_y)

        for piece in self.widgets["pieces"].pieces:
            if piece == only_selected:
                continue

            if only_selected.piece_collides(piece.get_x(), piece.get_y()):
                self.widgets["pieces"].pieces.remove(piece)

        # after moving, automatically deselect the piece and spinner
        only_selected.selected = False
        self.widgets["pieces"].selected_pieces.pop()
        self.widgets["movesel"].hide(self)

    def promote(self, piece: Piece):
        x, y, rad, side = (
            piece.get_x(),
            piece.get_y(),
            piece.get_angle(),
            piece.get_side(),
        )
        self.widgets["pieces"].pieces.remove(piece)
        if side == Side.BLACK:
            side_str = "B"
        elif side == Side.WHITE:
            side_str = "W"
        self.widgets["pieces"].pieces.append(Piece(x, y, rad, side, self.assets[f"piece_queen{side_str}{self.piece_skin.value}"], "queen"))  # fmt: skip

    # fmt: off
    def load_normal_board(self):
        self.widgets["pieces"].pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.widgets["pieces"].pieces.append(Piece(x_pos, 75, math.radians(180), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin.value}"], "pawn"))
            self.widgets["pieces"].pieces.append(Piece(x_pos, 75 + 250, 0, Side.WHITE, self.assets[f"piece_pawnW{self.piece_skin.value}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.widgets["pieces"].pieces.append(Piece(x_pos, 25, math.radians(180), Side.BLACK, self.assets[f"piece_{order[orderidx]}B{self.piece_skin.value}"], order[orderidx]))
            self.widgets["pieces"].pieces.append(Piece(x_pos, 25 + 350, 0, Side.WHITE, self.assets[f"piece_{order[orderidx]}W{self.piece_skin.value}"], order[orderidx]))
    # fmt: on

    # fmt: off
    def load_chess_960(self):
        self.widgets["pieces"].pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.widgets["pieces"].pieces.append(Piece(x_pos, 75, math.radians(random.randint(-180, 180)), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin.value}"], "pawn"))
            self.widgets["pieces"].pieces.append(Piece(x_pos, 75 + 250, math.radians(random.randint(-180, 180)), Side.WHITE, self.assets[f"piece_pawnW{self.piece_skin.value}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        random.shuffle(order)
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.widgets["pieces"].pieces.append(Piece(x_pos, 25, math.radians(random.randint(-180, 180)), Side.BLACK, self.assets[f"piece_{order[orderidx]}B{self.piece_skin.value}"], order[orderidx]))
            self.widgets["pieces"].pieces.append(Piece(x_pos, 25 + 350, math.radians(random.randint(-180, 180)), Side.WHITE, self.assets[f"piece_{order[orderidx]}W{self.piece_skin.value}"], order[orderidx]))
    # fmt: on


class TurnNavigation:
    """used to keep track of previous turns and has an API to navigate the board through them"""

    def __init__(self, pieces: list[Piece]) -> None:
        self.__turns: list[list[Piece]] = [copy.deepcopy(pieces)]
        self.__curr_turn = 0

    def __len__(self) -> int:
        return len(self.__turns)

    def get_game_save(self) -> str:
        return json_compress(
            {
                "save_version": "1.0.0",
                "save": [[piece.to_JSON_dict() for piece in turn] for turn in self.__turns],
            }
        )

    def load_game_save(self, s: str, gs: GameState) -> bool:
        """
        tries to load a game save, returning whether this succeeded
        """
        try:
            s = s.strip()
            j = json_decompress(s)

            reconstructed_save: list[list[Piece]] = []
            save = j["save"]
            for move in save:
                reconstructed_save.append([])
                for piece_dict in move:
                    side: Side = Side(piece_dict["side"])
                    reconstructed_save[-1].append(
                        Piece(
                            piece_dict["x"],
                            piece_dict["y"],
                            piece_dict["angle"],
                            side,
                            gs.assets[f"piece_{piece_dict['piece_name']}{'B' if side == Side.BLACK else 'W'}{gs.piece_skin.value}"],
                            piece_dict["piece_name"],
                        )
                    )
            self.__turns = reconstructed_save
            self.__curr_turn = len(self) - 1
            self.update_state(gs)
            return True
        except:
            return False

    def record_turn(self, pieces: list[Piece]) -> None:
        self.__turns = self.__turns[0 : self.__curr_turn + 1]
        self.__turns.append(copy.deepcopy(pieces))
        self.__curr_turn += 1

    def update_state(self, gs: GameState):
        gs.widgets["pieces"].pieces = copy.deepcopy(self.__turns[self.__curr_turn])

    def first(self) -> None:
        """presses first button. may or may not be a noop"""
        self.__curr_turn = 0

    def first_noop(self) -> bool:
        """returns True if first is a noop"""
        return self.__curr_turn == 0

    def prev(self) -> None:
        """presses prev button. may or may not be a noop"""
        if not self.prev_noop():
            self.__curr_turn -= 1

    def prev_noop(self) -> bool:
        """returns True if prev is a noop"""
        return self.__curr_turn == 0

    def next(self) -> None:
        """presses next button. may or may not be a noop"""
        if not self.next_noop():
            self.__curr_turn += 1

    def next_noop(self) -> bool:
        """returns True if next is a noop"""
        return self.__curr_turn == self.__len__() - 1

    def last(self) -> None:
        """presses last button. may or may not be a noop"""
        self.__curr_turn = self.__len__() - 1

    def last_noop(self) -> bool:
        """returns True if last is a noop"""
        return self.__curr_turn == self.__len__() - 1

    def go_to(self, turn: int):
        assert 0 <= turn < self.__len__()
        self.__curr_turn = turn

    def get_curr_turn(self) -> list[Piece]:
        return copy.deepcopy(self.__turns[self.__curr_turn])


if __name__ == "__main__":
    print(f"d={distance(0,0, 10,0, 4,3)}")
    print(f"d={distance(2,0, 0,2, 0,0)}")

    print(f"comp={scalar_comp(1,1, 5,5, 5,1)}")
