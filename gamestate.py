from moveselector import MoveSelector
from pieces import *
import os
import random
import math
import settings
from settings import PieceSkins



class GameState:
    def __init__(self) -> None:
        self.playing: bool = True
        self.movesel: MoveSelector = MoveSelector((500, 200), 80)

        # loading assets
        self.assets: dict[str, pygame.Surface] = dict()
        for file in os.listdir("assets"):
            self.assets[file.removesuffix(".png").removesuffix(".svg")] = pygame.image.load(f"assets/{file}")
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

    def canmove(self, only_selected: Piece, point_x: float, point_y: float) -> bool:
        """checks if we can move the only selected piece to point_x, point_y"""
        assert len(self.selected_pieces) == 1

        if only_selected.can_jump:
            return True
        
        # in_the_way: list[Piece] = []
        # for piece in self.pieces:
        #     if piece == only_selected:
        #         continue

        #     if piece in the scalar projection direction is >= 0 but < the max hit distance
        #     and if piece is less than 2*hitcirclerad away from line:
        #         in_the_way.append(piece)
            
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
        x, y, rad, side = piece.get_x(), piece.get_y(), piece.get_angle(), piece.get_side()
        self.pieces.remove(piece)
        if side == Side.BLACK:
            side_str = "B"
        elif side == Side.WHITE:
            side_str = "W"
        self.pieces.append(Piece(x, y, rad, side, self.assets[f"piece_queen{side_str}{self.piece_skin}"], "queen"))

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
