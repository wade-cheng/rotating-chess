import settings
import pygame
from pygame.locals import *
from gamestate import GameState
from debug import *


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
            elif event.key == pygame.K_DELETE:
                if len(gs.selected_pieces) != 1:
                    continue

                d_print("using keybind to try to delete current selected piece")
                gs.pieces.remove(gs.selected_pieces[0])
                gs.selected_pieces.clear()
            elif event.key == pygame.K_BACKSPACE:
                # TEMP KEYBIND FOR CANCEL BUTTON
                if not gs.cross_showing:
                    continue

                d_print("using keybind to try to click cancel button")
                gs.movesel.hide(gs)
                for piece in gs.selected_pieces:
                    # according to invariant, this should set all to false.
                    # setting not piece.selected is sorta like verifying invariant
                    piece.selected = not piece.selected
                    piece.stop_previewing()
                gs.selected_pieces.clear()
            elif event.key == pygame.K_RETURN:
                # TEMP KEYBIND FOR CONFIRM BUTTON
                if not gs.check_showing:
                    continue

                gs.movesel.hide(gs)
                for piece in gs.selected_pieces:
                    # according to invariant, this should set all to false.
                    # setting not piece.selected is sorta like verifying invariant
                    piece.selected = not piece.selected
                    piece.confirm_preview()
                gs.selected_pieces.clear()
                d_print("using keybind to try to click confirm button")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            moved_piece = False
            if len(gs.selected_pieces) == 1:
                only_selected = gs.selected_pieces[0]
                for point_x, point_y in only_selected.get_movable_points():
                    if (
                        ((x - point_x) ** 2 + (y - point_y) ** 2)
                        < settings.HITCIRCLE_RADIUS ** 2
                    ) and gs.canmove(only_selected, point_x, point_y):
                        gs.move(only_selected, point_x, point_y)

                        moved_piece = True
                        break

            if moved_piece:
                continue

            for piece in gs.pieces:
                if piece.coord_collides(x, y):
                    piece.selected = not piece.selected
                    if piece.selected:
                        gs.cross_showing = True
                        gs.selected_pieces.append(piece)
                        if gs.movesel.get_selected_point() is not None:
                            piece.set_preview_angle(gs.movesel.selected_angle())
                    else:
                        gs.selected_pieces.remove(piece)
                        piece.stop_previewing()

                    if len(gs.selected_pieces) != 0:
                        gs.movesel.reveal()
                    else:
                        gs.movesel.hide(gs)

    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        if gs.movesel.is_visible() and gs.movesel.coord_collides(x, y):
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

    pygame.display.update()


def main():

    pygame.init()

    fps = 60.0
    fpsClock = pygame.time.Clock()

    screen = pygame.display.set_mode((600, 400), flags=0, vsync=1)
    # screen = pygame.display.set_mode((600, 400), flags=pygame.SCALED, vsync=1)

    gs: GameState = GameState()

    while gs.playing:
        update(gs)
        draw(screen, gs)

        fpsClock.tick(fps)


if __name__ == "__main__":
    main()
