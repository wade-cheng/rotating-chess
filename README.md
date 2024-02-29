# Rotating Chess

A very normal game of chess.

![normally set up chess board except rotated pawn](dist_assets/cover_image.png)

Check out example games in `/dist_assets/example_game*`.

### play
https://wade-cheng.is-a.dev/rotating-chess/

### attributions

Chess pieces from https://opengameart.org/content/chess-pieces-and-a-board

and https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces.

As required from wikimedia, this work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

### rules

The program allows the movement and rotation of any piece at any time.

The following ruleset is currently recommended:
- alternating player turns, starting with white
- on each turn, the player must move a piece and may rotate a piece, in that order
- pawns, knights, and kings may "jump" over other pieces. all other pieces may be "blocked"
- pawns always have access to their two-forward movement

### technical details

This pygame game is developed on Python 3.10.12. There is a `__future__` import for type checking in `moveselector.py`. 

Locally start the game by calling `python3 main.py`. See the `Makefile` for build options.

Colors and some other settings may be edited with a text editor via `settings.py`.
