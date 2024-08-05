import asyncio
import random
import settings
import pygame
from pygame.event import Event
from pygame.locals import *
from gamestate import GameState
import widgets
from widgets import MOUSE_HELD
from debug import *

import sys, platform

if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"


def update(gs: GameState):
    widgets.Button.one_clicked = False
    x, y = pygame.mouse.get_pos()

    if pygame.mouse.get_pressed()[0]:
        pygame.event.post(Event(MOUSE_HELD))

    for event in pygame.event.get():
        for widget in gs.widgets.values():
            widget.handle_event(event, gs, x, y)

        if event.type == QUIT:
            gs.playing = False


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

    # draw "cover" for pieces in case they leak over to the selection panel
    # TODO: this doesn't actually do anything anymore. need to get
    # LayeredUpdates working and make all these widgets.
    # ie only thing in this function should be screen.fill board color and draw all widgets
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
