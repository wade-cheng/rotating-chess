import asyncio
import random  # TEMP
import settings
import pygame
from pygame.locals import *
from gamestate import GameState
from debug import *
import pieces

import sys, platform

if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"


def try_nav_first(gs):
    print("clicked try_nav_first")


def try_nav_prev(gs):
    print("clicked try_nav_prev")


def try_nav_next(gs):
    print("clicked try_nav_next")


def try_nav_last(gs):
    print("clicked try_nav_last")


# TODO: maybe these try button should be a MoveSelector function? or not.
def try_cancelbutton(gs: GameState) -> bool:
    """tries to cancel, returning whether it succeeded"""
    if not gs.cross_showing:
        return False

    gs.movesel.hide(gs)
    for piece in gs.selected_pieces:
        # according to invariant, this should set all to false.
        # setting not piece.selected is sorta like verifying invariant
        piece.selected = not piece.selected
        piece.stop_previewing()
    gs.selected_pieces.clear()

    return True


def try_confirmbutton(gs: GameState) -> bool:
    """tries to confirm, returning whether it succeeded"""
    if not gs.check_showing:
        return False

    gs.movesel.hide(gs)
    for piece in gs.selected_pieces:
        # according to invariant, this should set all to false.
        # setting not piece.selected is sorta like verifying invariant
        piece.selected = not piece.selected
        piece.confirm_preview()
    gs.selected_pieces.clear()

    return True


def update(gs: GameState):
    for event in pygame.event.get():
        if event.type == QUIT:
            gs.playing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # TEMP
                # lost two endgame games in playtesting accidentally because of this 💀
                # leaving the history here for posterity
                # d_print(f"{gs.movesel.selected_angle() / 3.1415}pi rad")
                pass
            elif event.key == pygame.K_d:
                debug_str = input("entered debug mode: ")
                split_debug: list[str] = debug_str.strip().split()
                if len(split_debug) == 3 and split_debug[0].lower() == "move":
                    if len(gs.selected_pieces) != 1:
                        print("need to have only one selected piece to move it")
                        continue
                    try:
                        x = float(split_debug[1])
                        y = float(split_debug[2])
                    except:
                        print("debug string not formatted as a move")
                        continue

                    gs.move(gs.selected_pieces[0], x, y)
                elif len(split_debug) == 1 and (
                    split_debug[0].lower() == "r" or split_debug[0].lower() == "rand"
                ):
                    p = random.choice(gs.pieces)
                    while p.get_side() == 2:
                        p = random.choice(gs.pieces)
                    p.selected = True
                    gs.selected_pieces.append(p)
                elif len(split_debug) == 2 and (
                    split_debug[0].lower() == "rot"
                    or split_debug[0].lower() == "rotate"
                ):
                    try:
                        rads = float(split_debug[1])
                    except:
                        print("debug string not formatted as a rotate")
                        continue

                    for piece in gs.selected_pieces:
                        piece.set_preview_angle(rads)
                        piece.confirm_preview()
                        piece.update_capture_points()
                        piece.update_move_points()
            elif event.key == pygame.K_EQUALS:
                # fmt: off
                order = ["rook", "knight", "bishop", "queen", "pawn", "king"]
                for orderidx, x_pos in enumerate(range(25, 50*len(order), 50)):
                    gs.pieces.append(pieces.Piece(x_pos, 0, 0, pieces.Side.BLACK, gs.assets[f"piece_{order[orderidx]}B{gs.piece_skin}"], order[orderidx]))
                    gs.pieces.append(pieces.Piece(x_pos, 400, 0, pieces.Side.WHITE, gs.assets[f"piece_{order[orderidx]}W{gs.piece_skin}"], order[orderidx]))
                # fmt: on
            elif event.key == pygame.K_DELETE:
                if len(gs.selected_pieces) != 1:
                    continue

                d_print("using keybind to try to delete current selected piece")
                gs.pieces.remove(gs.selected_pieces[0])
                gs.selected_pieces.clear()
            elif event.key == pygame.K_BACKSPACE:
                # KEYBIND FOR CANCEL BUTTON
                cancelled = try_cancelbutton(gs)
                if cancelled:
                    continue
            elif event.key == pygame.K_RETURN:
                # KEYBIND FOR CONFIRM BUTTON
                confirmed = try_confirmbutton(gs)
                if confirmed:
                    continue
        elif event.type == pygame.MOUSEBUTTONUP:
            gs.movesel.selecting = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # check if we've clicked on the move navigation
            """
            # draw move navigation
            offset = 3 # make sure the hitboxes dont overlap
            f_width, p_width, n_width, l_width = 58, 37, 41, 54
            screen.blit(gs.assets["nav_first"], (400 + offset, 300))
            offset += 1
            screen.blit(gs.assets["nav_prev"], (400 + offset + f_width, 300))
            offset += 1
            screen.blit(gs.assets["nav_next"], (400 + offset + f_width + p_width, 300))
            offset += 1
            screen.blit(gs.assets["nav_last"], (400 + offset + f_width + p_width + n_width, 300))
            """
            if not gs.cross_showing:
                offset = 3
                f_width, p_width, n_width, l_width = 58, 37, 41, 54
                nav_height = 53

                if pygame.Rect(400 + offset, 300, nav_height, f_width).collidepoint(x, y):
                    try_nav_first(gs)
                    continue

                if pygame.Rect(400 + offset + f_width, 300, nav_height, p_width).collidepoint(x, y):
                    try_nav_prev(gs)
                    continue

                if pygame.Rect(
                    400 + offset + f_width + p_width, 300, nav_height, n_width
                ).collidepoint(x, y):
                    try_nav_next(gs)
                    continue

                if pygame.Rect(
                    400 + offset + f_width + p_width + n_width, 300, nav_height, n_width
                ).collidepoint(x, y):
                    try_nav_last(gs)
                    continue

            # check if we've clicked the cross or check
            if pygame.Rect(500 - 28, 50, 56, 53).collidepoint(x, y):
                try_confirmbutton(gs)
                continue

            if pygame.Rect(500 - 28, 300, 56, 53).collidepoint(x, y):
                try_cancelbutton(gs)
                continue

            # check if we've started to move the rotation move selector
            if gs.movesel.is_visible() and gs.movesel.coord_collides(x, y):
                gs.movesel.selecting = True
                gs.movesel.select_rotcircle(x, y, gs)
                continue

            # check and update if we've moved a piece, promoting as needed
            moved_piece = False
            if len(gs.selected_pieces) == 1:
                only_selected = gs.selected_pieces[0]
                for point_x, point_y in only_selected.get_movable_points():
                    if (
                        ((x - point_x) ** 2 + (y - point_y) ** 2)
                        < settings.HITCIRCLE_RADIUS ** 2
                    ) and gs.canmove(only_selected, point_x, point_y):
                        gs.move(only_selected, point_x, point_y)
                        # note: gs.move() already removes the piece from selected, but we still have the pointer.
                        if only_selected.should_promote():
                            gs.promote(only_selected)

                        moved_piece = True
                        break

            if moved_piece:
                continue

            # check if we've clicked a piece
            for piece in gs.pieces:
                if piece.coord_collides(x, y):
                    piece.selected = not piece.selected
                    if piece.selected:
                        gs.cross_showing = True
                        gs.movesel.reveal()
                        gs.selected_pieces.append(piece)
                        if gs.movesel.get_selected_point() is not None:
                            piece.set_preview_angle(gs.movesel.selected_angle())
                    else:
                        gs.selected_pieces.remove(piece)
                        piece.stop_previewing()
                        if len(gs.selected_pieces) == 0:
                            gs.movesel.hide(gs)

                    if (
                        not settings.CAN_SELECT_MULTIPLE
                        and len(gs.selected_pieces) == 2
                    ):
                        gs.selected_pieces[0].selected = False
                        gs.selected_pieces[0].stop_previewing()
                        gs.selected_pieces.pop(0)
                        gs.selected_pieces[0].stop_previewing()
                        gs.movesel.hide(gs)
                        gs.cross_showing = True
                        gs.movesel.reveal()

                    # if len(gs.selected_pieces) != 0:
                    #     gs.movesel.reveal()
                    # else:
                    #     gs.movesel.hide(gs)

    # if pygame.mouse.get_pressed()[0]:
    if pygame.mouse.get_pressed()[0] and gs.movesel.selecting:
        x, y = pygame.mouse.get_pos()
        # if gs.movesel.is_visible() and gs.movesel.coord_collides(x, y):
        gs.movesel.select_rotcircle(x, y, gs)
        for piece in gs.selected_pieces:
            piece.update_capture_points()
            piece.update_move_points()


def draw(screen: pygame.Surface, gs: GameState):
    """
    Draw things to the window. Called once per frame.
    """
    # draw board tiles
    screen.fill(settings.BOARD_COLOR)

    for i in range(0, 400, 100):
        for j in range(0, 400, 100):
            pygame.draw.rect(screen, settings.BACKGROUND_COLOR, (i, j, 50, 50))

    for i in range(50, 450, 100):
        for j in range(50, 450, 100):
            pygame.draw.rect(screen, settings.BACKGROUND_COLOR, (i, j, 50, 50))

    # draw pieces
    for piece in gs.pieces:
        piece.draw(screen)
        if len(gs.selected_pieces) == 1:
            piece.draw_hitcircle(screen)

    if len(gs.selected_pieces) == 1:
        gs.selected_pieces[0].draw_move_points(screen)
        gs.selected_pieces[0].draw_capture_points(screen)

    # draw "cover" for pieces in case they leak over to the selection panel
    pygame.draw.rect(screen, settings.BOARD_COLOR, (8 * 50, 0, 4 * 50, 8 * 50))

    # draw rotation selector
    gs.movesel.draw(screen)

    # draw check and cross if applicable
    if gs.check_showing:
        screen.blit(gs.assets["check_white"], (500 - 28, 50))

    if gs.cross_showing:
        screen.blit(gs.assets["cross_white"], (500 - 28, 300))

    # draw move navigation if applicable
    if not gs.cross_showing:
        offset = 3  # make sure the hitboxes dont overlap
        f_width, p_width, n_width, l_width = 58, 37, 41, 54
        screen.blit(gs.assets["nav_first"], (400 + offset, 300))
        offset += 1
        screen.blit(gs.assets["nav_prev"], (400 + offset + f_width, 300))
        offset += 1
        screen.blit(gs.assets["nav_next"], (400 + offset + f_width + p_width, 300))
        offset += 1
        screen.blit(
            gs.assets["nav_last"], (400 + offset + f_width + p_width + n_width, 300)
        )

    pygame.draw.circle(screen, (255, 255, 255), (400, 300), radius=3, width=1)

    pygame.display.update()


async def main():
    pygame.init()

    screen = pygame.display.set_mode((600, 400), flags=0, vsync=1)
    # screen = pygame.display.set_mode((600, 400), flags=pygame.SCALED, vsync=1)

    gs: GameState = GameState()
    clock = pygame.time.Clock()

    while gs.playing:
        update(gs)
        draw(screen, gs)

        clock.tick(60)
        await asyncio.sleep(0)  # Let other tasks run


# async code such that pygbag can compile to wasm
asyncio.run(main())
