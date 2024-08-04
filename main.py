import asyncio
import random
import settings
import pygame
from pygame.locals import *
from gamestate import GameState
from debug import *

import sys, platform

if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"


def update(gs: GameState):
    x, y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        for widget in gs.widgets.values():
            widget.handle_event(event, gs, x, y)

        if event.type == QUIT:
            gs.playing = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
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
                gs.nav.record_turn(gs.pieces)
                continue

            # check if we've clicked a piece
            for piece in gs.pieces:
                if piece.coord_collides(x, y):
                    piece.selected = not piece.selected
                    if piece.selected:
                        gs.widgets["cancel_rot"].reveal()
                        gs.widgets["movesel"].reveal()
                        gs.selected_pieces.append(piece)
                        if gs.widgets["movesel"].get_selected_point() is not None:
                            piece.set_preview_angle(gs.widgets["movesel"].selected_angle())
                    else:
                        gs.selected_pieces.remove(piece)
                        piece.stop_previewing()
                        if len(gs.selected_pieces) == 0:
                            gs.widgets["movesel"].hide(gs)

                    if (
                        not settings.CAN_SELECT_MULTIPLE
                        and len(gs.selected_pieces) == 2
                    ):
                        gs.selected_pieces[0].selected = False
                        gs.selected_pieces[0].stop_previewing()
                        gs.selected_pieces.pop(0)
                        gs.selected_pieces[0].stop_previewing()
                        gs.widgets["movesel"].hide(gs)
                        gs.widgets["cancel_rot"].reveal()
                        gs.widgets["movesel"].reveal()

                    # if len(gs.selected_pieces) != 0:
                    #     gs.widgets["movesel"].reveal()
                    # else:
                    #     gs.widgets["movesel"].hide(gs)

    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()

        for widget in gs.widgets.values():
            widget.handle_mouse_hold(gs, x, y)


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

    # draw widgets
    for widget in gs.widgets.values():
        widget.draw(screen, gs)

    pygame.display.update()


async def main():
    pygame.init()

    # screen = pygame.display.set_mode((600, 400), flags=0, vsync=1)
    screen = pygame.display.set_mode((600, 400), flags=pygame.SCALED, vsync=1)

    gs: GameState = GameState()
    clock = pygame.time.Clock()

    while gs.playing:
        update(gs)
        draw(screen, gs)

        clock.tick(60)
        await asyncio.sleep(0)  # Let other tasks run


# async code such that pygbag can compile to wasm
asyncio.run(main())
