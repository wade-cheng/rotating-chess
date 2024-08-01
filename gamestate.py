from moveselector import MoveSelector
from pieces import *
import os
import random
import math
import settings
from settings import PieceSkins
import copy


def max_hit_distance(
    start_x: float, start_y: float, end_x: float, end_y: float
) -> float:
    """simple distance formula + hitcirclerad"""
    return (
        math.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2)
        + settings.HITCIRCLE_RADIUS
    )


def distance(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    point_x: float,
    point_y: float,
) -> float:
    """finds the distance from a point to a line, where the line is given by two points"""
    return abs(
        (end_x - start_x) * (point_y - start_y)
        - (point_x - start_x) * (end_y - start_y)
    ) / math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)


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


class GameState:
    def __init__(self) -> None:
        self.playing: bool = True
        self.movesel: MoveSelector = MoveSelector((500, 200), 80)

        # loading assets
        self.assets: dict[str, pygame.Surface] = dict()
        for file in os.listdir("assets"):
            self.assets[
                file.removesuffix(".png").removesuffix(".svg")
            ] = pygame.image.load(f"assets/{file}")
        print(f"loaded assets:\n{self.assets.keys()}")

        self.piece_skin: str = settings.SKIN
        self.pieces: list[Piece] = []
        # invariant: forall Piece in selected_pieces, Piece.selected
        # invariant: forall Piece not in selected_pieces, not Piece.selected
        self.selected_pieces: list[Piece] = []

        self.cross_showing = False
        self.check_showing = False

        # self.load_chess_960()
        self.load_normal_board()

        self.nav: TurnNavigation = TurnNavigation(self.pieces)

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
                < max_hit_distance(
                    only_selected.get_x(), only_selected.get_y(), point_x, point_y
                )
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
        self.movesel.hide(self)

    def promote(self, piece: Piece):
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
        self.pieces.append(
            Piece(
                x,
                y,
                rad,
                side,
                self.assets[f"piece_queen{side_str}{self.piece_skin}"],
                "queen",
            )
        )

    # fmt: off
    def load_normal_board(self):
        self.pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.pieces.append(Piece(x_pos, 75, math.radians(180), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin}"], "pawn"))
            self.pieces.append(Piece(x_pos, 75 + 250, 0, Side.WHITE, self.assets[f"piece_pawnW{self.piece_skin}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.pieces.append(Piece(x_pos, 25, math.radians(180), Side.BLACK, self.assets[f"piece_{order[orderidx]}B{self.piece_skin}"], order[orderidx]))
            self.pieces.append(Piece(x_pos, 25 + 350, 0, Side.WHITE, self.assets[f"piece_{order[orderidx]}W{self.piece_skin}"], order[orderidx]))
    # fmt: on

    # fmt: off
    def load_chess_960(self):
        self.pieces.clear()
        for x_pos in range(25, 50*8, 50):
            self.pieces.append(Piece(x_pos, 75, math.radians(random.randint(-180, 180)), Side.BLACK, self.assets[f"piece_pawnB{self.piece_skin}"], "pawn"))
            self.pieces.append(Piece(x_pos, 75 + 250, math.radians(random.randint(-180, 180)), Side.WHITE, self.assets[f"piece_pawnW{self.piece_skin}"], "pawn"))

        order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        random.shuffle(order)
        for orderidx, x_pos in enumerate(range(25, 50*8, 50)):
            self.pieces.append(Piece(x_pos, 25, math.radians(random.randint(-180, 180)), Side.BLACK, self.assets[f"piece_{order[orderidx]}B{self.piece_skin}"], order[orderidx]))
            self.pieces.append(Piece(x_pos, 25 + 350, math.radians(random.randint(-180, 180)), Side.WHITE, self.assets[f"piece_{order[orderidx]}W{self.piece_skin}"], order[orderidx]))
    # fmt: on


class TurnNavigation:
    def __init__(self, pieces: list[Piece]) -> None:
        self.__turns = [copy.deepcopy(pieces)]
        self.__curr_turn = 0

    def __len__(self) -> int:
        return len(self.__turns)

    def record_turn(self, pieces: list[Piece]) -> None:
        self.__turns = self.__turns[0 : self.__curr_turn + 1]
        self.__turns.append(copy.deepcopy(pieces))
        self.__curr_turn += 1

    def update_state(self, gs: GameState):
        gs.pieces = copy.deepcopy(self.__turns[self.__curr_turn])

    def first(self) -> None:
        """presses first button. may or may not be a noop"""
        pass

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
