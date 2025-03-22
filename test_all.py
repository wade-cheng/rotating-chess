import doctest
import unittest
import compressjson as cj
import widgets
from math import isclose
from pieces import Piece


# class Pieces(Widget):
#     def __init__(self) -> None:
#         self.skin = settings.SKIN
#         self.pieces: list[Piece] = []
#         # invariant: forall Piece in selected_pieces, Piece.selected
#         # invariant: forall Piece not in selected_pieces, not Piece.selected
#         # checked every time we MOUSEBUTTONDOWN
#         self.selected_pieces: list[Piece] = []


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(cj))
    return tests


class TestSaveFiles(unittest.TestCase):
    def test_compression(self):
        msg = """{"instructions": "this ENTIRE alert is your game save.", "save": [[{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175.0, "y": 225.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 175.0, "y": 125.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}], [{"x": 25, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 25, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 75, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 75, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 125, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 125, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 175, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 225.0, "y": 75.0, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 225, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 275, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 275, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 325, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 325, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 375, "y": 75, "angle": 3.141592653589793, "side": 1, "piece_name": "pawn"}, {"x": 375, "y": 325, "angle": 0, "side": 2, "piece_name": "pawn"}, {"x": 25, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 25, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}, {"x": 75, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 75, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 125, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 125, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 175, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "queen"}, {"x": 175, "y": 375, "angle": 0, "side": 2, "piece_name": "queen"}, {"x": 225, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "king"}, {"x": 225, "y": 375, "angle": 0, "side": 2, "piece_name": "king"}, {"x": 275, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "bishop"}, {"x": 275, "y": 375, "angle": 0, "side": 2, "piece_name": "bishop"}, {"x": 325, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "knight"}, {"x": 325, "y": 375, "angle": 0, "side": 2, "piece_name": "knight"}, {"x": 375, "y": 25, "angle": 3.141592653589793, "side": 1, "piece_name": "rook"}, {"x": 375, "y": 375, "angle": 0, "side": 2, "piece_name": "rook"}]]}"""
        self.assertEqual(cj.json_decompress(cj.json_compress(msg)), msg)

def find_piece(ps: widgets.Pieces, x: float, y: float) -> Piece:
    """returns the piece in ps at x,y or throws an error if not exactly 1 was found."""
    selected_ps = [
        p
        for p in ps.pieces
        if isclose(p.get_x(), x, abs_tol=0.001)
        and isclose(p.get_y(), y, abs_tol=0.001)
    ]
    assert len(selected_ps) == 1
    return selected_ps[0]


def can_move(
    ps: widgets.Pieces, start: tuple[float, float], end: tuple[float, float]
) -> bool:
    """
    returns whether the piece at start within ps can move to end.
    """
    s_x, s_y = start
    e_x, e_y = end
    
    p =  find_piece(ps, s_x, s_y)
    p.selected = True
    ps.selected_pieces.append(p)
    return ps.canmove(p, e_x, e_y)


class TestPieceMovementFromStandard(unittest.TestCase):
    def setUp(self):
        self.standard_begin = widgets.Pieces()
        self.standard_begin.load_normal_board(None, None)

    def test_Nc3(self):
        self.assertTrue(can_move(self.standard_begin, (75, 375), (125, 275)))

    def test_Nxd2(self):
        self.assertFalse(can_move(self.standard_begin, (75, 375), (175.0, 325.0)))

    def test_Rh5(self):
        self.assertFalse(can_move(self.standard_begin, (375, 375), (375.0, 175.0)))

    def test_pawn_jump(self):
        # non-infinitely jumping pieces like pawns should be able to hop like standard knights.
        
        # find_piece(self.standard_begin, 225, 325).__angle = 1.183126748420898 we should not need this
        # Piece.can_move doesn't check for compilance with DistsAngles.
        self.assertTrue(can_move(self.standard_begin, (225, 325), (133.42074531670488, 287.1968043376545)))

    def test_phase(self):
        # infinitely jumping pieces should be not able to hop/phase through pieces to their destination.
        # rotchess save eJzt1uFOwjAUBeBXWfobm/Z2XVtehRAydYEF3RAUNYR3t1MQmYuOrZAYzy+bLp7cHLabb8NW6TqbrLPlKi8LNoyY5IILNojeH/iL0WjDXvxf0v7u1R9MdUiL6V31VHEZS+0o0UpbZ5yq/jG/rR5Jf1zk2U02KdL76oIt0ueCbQdRLVDR10RxSKBfEkzokUzvkWTwmmT/nmTwomT/pij8C9W/KQreFPVvSgVvSvVvSgVvSgV4p/YJ1HmmZVnOm3aUaT3ScYLpP9K8yKezx6Yt1X6oeoYMUNV1vpqVi8ZN1X6wbyEBCnt4yrLmZdV+rloGBehrnhfTxm11ws94HBGgq3r/1KWseogK0VbtjVWd+qqHBGjs+PtWXfr6iBgPItgKtvortuJi/+nszvAVfAVfwVfwFXwFX8FXPyXCV/DV+X11JbgWZGNFUjgyNhEW4oK4IK6GDIgL4oK4IC6IC+JqQRmhOVktYxI6NkbHyefWMVw4RYkR/lo7m8Bj8BiDx+AxeAweg8fgMXgMHoPH4LHLecx/soddYk7YJTAZTAaTBRwJJoPJ/ovJvMe4NpWvvK60Fm6XL63j0vpAH6yldIZAMpCMgWQgGUgGkoFkIBlIBpKBZCDZRUmmuq4SkAwkOzfJxts3GM1Nuw==
        find_piece(self.standard_begin, 225, 325).move(225.0, 225.0) # move aside e-pawn
        find_piece(self.standard_begin, 325, 325).move(305.28514205477546, 257.09326707755986) # block queen with g pawn
        self.assertFalse(can_move(self.standard_begin, (175, 375), (325.0, 225.0))) # test cannot phase


# TODO: can add another key to game save dict, d["forward_moves"] : list[moves] of one less length than list["save", the boards] where
# d["forward_moves"][i] describes the move from d["save"][i] to [i+1]
# this would be helpful for testing because we could just read in an old save file and be sure we're backwards compatible.

if __name__ == "__main__":
    unittest.main()
