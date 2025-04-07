import os
import copy
from enum import Enum

from pygame.math import Vector2

from rotating_chess.pieces import *
from rotating_chess.widgets import *
from rotating_chess import settings
from rotating_chess.compressjson import json_compress, json_decompress
from rotating_chess.locations import at


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
            """
            we essentially create a typed dict. 
            this is just to make stuff more explicit.
            e.g. `gs.widgets.pieces` instead of `gs.pieces`.
            """
            def __init__(wself):
                wself.pieces = Pieces()
                wself.movesel = MoveSelector(center=(500, 200), radius=80)
                wself.cancel_rot = CancelRot(self.assets["cross_white"], 500 - 28, 300)
                wself.confirm_rot = ConfirmRot(self.assets["check_white"], 500 - 28, 50)
                wself.nav_first_btn = NavFirst(self.assets["nav_first"], 400 + 3, 300)
                wself.nav_prev_btn = NavPrev(self.assets["nav_prev"], 400 + 4 + f_width, 300)
                wself.nav_next_btn = NavNext(self.assets["nav_next"], 400 + 5 + f_width + p_width, 300)
                wself.nav_last_btn = NavLast(self.assets["nav_last"], 400 + 6 + f_width + p_width + n_width, 300)
                wself.nav_prog = NavProgressBar(400, 600, 200)
                wself.exp_save = ExportSave(self.assets["download"], 415, 10, self.font)
                wself.imp_save = ImportSave(self.assets["upload"], 540, 10, self.font)
            __dict__: dict[str, Widget]
        self.widgets = Widgets()

        # self.widgets.pieces.load_chess_960(self.assets, self.piece_skin)
        self.widgets.pieces.load_normal_board(self.assets, self.piece_skin)

        # for testing: (remember to comment out load_normal above)
        # self.widgets.pieces = Pieces([
        #     Piece(*at("a7")-Vector2(0,10), math.radians(180), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin.value}"], "pawn"),
        #     Piece(*at("b7")-Vector2(10,10), math.radians(180), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin.value}"], "pawn"),
        #     Piece(*at("a8")-Vector2(0,0), math.radians(180), Side.BLACK, self.assets[f"piece_rookB{self.piece_skin.value}"], "rook"),
        #     Piece(*at("b8")-Vector2(10,0), math.radians(180), Side.BLACK, self.assets[f"piece_knightB{self.piece_skin.value}"], "knight"),
        #     Piece(*at("a1/b2")-Vector2(5,5), 0, Side.WHITE, self.assets[f"piece_queenW{self.piece_skin.value}"], "queen"),
        # ])
        # fmt: on

        self.nav: TurnNavigation = TurnNavigation(self.widgets.pieces.pieces)

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
            self.assets[file.removesuffix(".png").removesuffix(".svg")] = (
                pygame.image.load(f"assets/{file}")
            )
        print(f"loaded assets:\n{self.assets.keys()}")


class TurnNavigation:
    """used to keep track of previous turns and has an API to navigate the board through them"""

    # TODO: hmm. this can be a Widget maybe? because a NavProgbar depends on this now? or not.

    def __init__(self, pieces: list[Piece]) -> None:
        self.__turns: list[list[Piece]] = [copy.deepcopy(pieces)]
        self.__curr_turn = 0

    def __len__(self) -> int:
        return len(self.__turns)

    def get_game_save(self) -> str:
        return json_compress(
            {
                "save_version": "1.0.0",
                "save": [
                    [piece.to_JSON_dict() for piece in turn] for turn in self.__turns
                ],
            }
        )

    def load_game_save(self, s: str, gs: GameState) -> list[list[Piece]] | None:
        """
        tries to load a game save, returning Some reconstructed list of list of pieces,
        or None if there was an error.

        if let Some ps, then ps is not an alias to any other ps. i.e., mutate as much as you'd like.
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
                            gs.assets[
                                f"piece_{piece_dict['piece_name']}{'B' if side == Side.BLACK else 'W'}{gs.piece_skin.value}"
                            ],
                            piece_dict["piece_name"],
                        )
                    )
            self.__turns = reconstructed_save
            self.__curr_turn = len(self) - 1
            self.update_state(gs)
            return copy.deepcopy(reconstructed_save)
        except:
            return None

    def record_turn(self, pieces: list[Piece]) -> None:
        self.__turns = self.__turns[0 : self.__curr_turn + 1]
        self.__turns.append(copy.deepcopy(pieces))
        self.__curr_turn += 1

    def update_state(self, gs: GameState):
        gs.widgets.pieces.pieces = copy.deepcopy(self.__turns[self.__curr_turn])

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

    def get_curr_turn_idx(self) -> int:
        return self.__curr_turn
