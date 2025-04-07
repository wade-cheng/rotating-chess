import pytest

from pygame.math import Vector2

import rotating_chess.compressjson as cj
from rotating_chess import widgets
from rotating_chess.pieces import Piece, Side
from rotating_chess.locations import at


class TestSaveFiles:
    def test_compression(self):
        msg = """{"instructions": "this ENTIRE alert is your game save.", "save": [[{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175.0, "y": 225.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175.0, "y": 125.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225.0, "y": 75.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}]]}"""
        assert cj.json_decompress(cj.json_compress(msg)) == msg


def find_piece(ps: widgets.Pieces, x: float, y: float) -> Piece:
    """returns the piece in ps at x,y or throws an error if not exactly 1 was found."""
    selected_ps = [
        p
        for p in ps.pieces
        if p.get_x() == pytest.approx(x) and p.get_y() == pytest.approx(y)
    ]

    assert len(selected_ps) == 1
    return selected_ps[0]


def can_move(
    ps: widgets.Pieces,
    start: tuple[float, float],
    end: tuple[float, float],
) -> bool:
    """
    returns whether the piece at start within ps can move to end.
    """
    s_x, s_y = start
    e_x, e_y = end

    p = find_piece(ps, s_x, s_y)
    p.selected = True
    ps.selected_pieces.append(p)
    return ps.canmove(p, e_x, e_y)


@pytest.fixture
def standard_begin():
    pieces = widgets.Pieces()
    pieces.load_normal_board(None, None)
    return pieces


@pytest.fixture
def e4() -> Piece:
    return Piece(*at("e4"), 0, Side.WHITE, None, "pawn")


class TestPromotion:
    def test_simple1(self, e4: Piece):
        """e4 -> e8"""
        ps = widgets.Pieces([e4])
        ps.selected_pieces.append(e4)
        e4.selected = True
        ps.move(e4, *at("e8"), None)
        assert len(ps.pieces) == 1
        assert ps.pieces[0].get_piece_name() == "queen"

    def test_simple2(self, e4: Piece):
        """e4 -> g8"""
        ps = widgets.Pieces([e4])
        ps.selected_pieces.append(e4)
        e4.selected = True
        ps.move(e4, *at("g8"), None)
        assert len(ps.pieces) == 1
        assert ps.pieces[0].get_piece_name() == "queen"

    def test_simple3(self, e4: Piece):
        """e4 -> partial"""
        ps = widgets.Pieces([e4])
        ps.selected_pieces.append(e4)
        e4.selected = True
        ps.move(e4, *at("e8/e7"), None)
        assert len(ps.pieces) == 1
        assert ps.pieces[0].get_piece_name() == "queen"


class TestPieceMovement:
    def test_Nc3(self, standard_begin):
        assert can_move(standard_begin, at("b1"), at("c3"))

    def test_Nxd2(self, standard_begin):
        assert not can_move(standard_begin, at("b1"), at("d2"))

    def test_Rh5(self, standard_begin):
        assert not can_move(standard_begin, at("h1"), at("h5"))

    def test_pawn_jump(self, standard_begin):
        """non-infinitely jumping pieces like pawns should be able to hop like standard knights."""

        # find_piece(standard_begin, 225, 325).__angle = 1.183126748420898 we should not need this
        # Piece.can_move doesn't check for compilance with DistsAngles.
        assert can_move(
            standard_begin,
            at("e2"),
            (133.42074531670488, 287.1968043376545),
        )

    def test_doublecapture(self, standard_begin):
        find_piece(standard_begin, *at("e2")).move(*at("e6"))  # e->e6
        find_piece(standard_begin, *at("d2")).move(*at("d4"))  # d4
        assert can_move(
            standard_begin,
            at("d1"),
            at("g7/h7"),
        )  # Qx(g7,h7)

    def test_triplecapture(self):
        board = widgets.Pieces(
            [
                Piece(*at("a7/b8"), 0, Side.BLACK, None, "pawn"),
                Piece(*at("a8"), 0, Side.BLACK, None, "rook"),
                Piece(*at("b8"), 0, Side.BLACK, None, "knight"),
                Piece(*at("b6"), 0.25, Side.WHITE, None, "queen"),
            ]
        )
        assert can_move(
            board,
            at("b6"),
            at("a8/b8"),
        )  # can capture all three

        board.move(find_piece(board, *at("b6")), *at("a8/b8"), None)  # do so

        # only the queen should remain
        assert len(board.pieces) == 1
        assert board.pieces[0].get_piece_name() == "queen"

    def test_quadcapture(self):
        board = widgets.Pieces(
            [
                Piece(*at("a7") - Vector2(0, 10), 0, Side.BLACK, None, "pawn"),
                Piece(*at("b7") - Vector2(10, 10), 0, Side.BLACK, None, "pawn"),
                Piece(*at("a8") - Vector2(0, 0), 0, Side.BLACK, None, "rook"),
                Piece(*at("b8") - Vector2(10, 0), 0, Side.BLACK, None, "knight"),
                Piece(*at("a1/b2") - Vector2(5, 5), 0, Side.WHITE, None, "queen"),
            ]
        )
        assert can_move(
            board,
            at("a1/b2") - Vector2(5, 5),
            at("a7/b8") - Vector2(5, 5),
        )  # can capture all four

        board.move(
            find_piece(board, *at("a1/b2") - Vector2(5, 5)),
            *at("a7/b8") - Vector2(5, 5),
            None,
        )  # do so

        # only the queen should remain
        assert len(board.pieces) == 1
        assert board.pieces[0].get_piece_name() == "queen"

    def test_phase(self, standard_begin):
        """
        infinitely jumping pieces should be not able to hop/phase through pieces to their destination.
        """
        assert not can_move(
            standard_begin,
            at("d1"),
            at("d5"),
        )

    def test_phase2(self, standard_begin):
        """
        infinitely jumping pieces should be not able to hop/phase through pieces to their destination.
        currently bugged.
        """
        find_piece(standard_begin, *at("e2")).move(*at("e6"))  # e->e6
        find_piece(standard_begin, *at("d2")).move(*at("d4"))  # d4
        assert not can_move(
            standard_begin,
            at("d1"),
            (315.9709686086502, 50.76677220010447),
        )  # Qx(g7,g8), but should NOT be possible


# TODO: can add another key to game save dict, d["forward_moves"] : list[moves] of one less length than list["save", the boards] where
# d["forward_moves"][i] describes the move from d["save"][i] to [i+1]
# this would be helpful for testing because we could just read in an old save file and be sure we're backwards compatible.

# TODO: test save files up/download. start refactoring into more test files?
