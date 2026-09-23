"""Pygame lifecycle, time accounting, and transitions between screens."""

import pygame

from . import config
from .cutscene import CutsceneScreen
from .gameplay import GameplayScreen
from .model import GameState
from .resources import Resources


class Game:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        flags = pygame.RESIZABLE if config.RESIZABLE else 0
        self.window = pygame.display.set_mode(config.WINDOW_SIZE, flags)
        pygame.display.set_caption(config.TITLE)
        self.canvas = pygame.Surface(config.CANVAS_SIZE).convert()
        self.resources = Resources()
        pygame.display.set_icon(self.resources.image("golden_kitty"))
        self.clock = pygame.time.Clock()
        self.running = True
        self.focused = True
        self.state = None
        self.mode = "opening"
        self.screen = CutsceneScreen(self.resources, self.mode)

    def start_round(self):
        self.state = GameState()
        self.state.paused = config.PAUSE_ON_FOCUS_LOSS and not self.focused
        self.mode = "playing"
        self.screen = GameplayScreen(self.resources, self.state)

    def _show_outcome(self):
        self.mode = self.state.outcome
        self.screen = CutsceneScreen(self.resources, self.mode)

    @property
    def viewport(self):
        return pygame.Rect((0, 0), config.CANVAS_SIZE).fit(self.window.get_rect())

    def to_canvas(self, pos):
        """Map window input through letterboxing; ignore clicks in the bars."""
        rect = self.viewport
        if not rect.collidepoint(pos):
            return None
        return (int((pos[0] - rect.x) * config.CANVAS_SIZE[0] / rect.width),
                int((pos[1] - rect.y) * config.CANVAS_SIZE[1] / rect.height))

    def step(self, seconds, events):
        """Advance one frame. Public so tests can drive the real event paths."""
        events = list(events)
        self.window = pygame.display.get_surface()
        # Handle focus before charging elapsed time: a stalled/minimized window
        # must not spend a player's remaining time on its first returning frame.
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type in (pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED):
                self.focused = False
                if config.PAUSE_ON_FOCUS_LOSS and self.mode == "playing":
                    self.state.paused = True
            elif event.type == pygame.WINDOWFOCUSGAINED:
                self.focused = True
        if not self.running:
            return
        if self.mode == "playing":
            self.state.advance(seconds)
            self.screen.update(seconds)
            if self.state.outcome:
                self._show_outcome()
                return  # A click at/after the deadline cannot buy a win.
        for event in events:
            if not self.focused:
                continue
            pos = self.to_canvas(event.pos) if hasattr(event, "pos") else None
            action = self.screen.handle_event(event, pos)
            if self.mode == "playing" and self.state.outcome:
                self._show_outcome()
                break
            if action in ("start", "replay", "restart"):
                self.start_round()
            elif action == "quit":
                self.running = False
            elif action == "pause":
                self.state.paused = True
            elif action == "resume":
                self.state.paused = False
            if action:
                # Do not let queued clicks spill into a new frame/screen/round.
                break

    def draw(self, mouse_pos=None):
        self.window = pygame.display.get_surface()
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)
        pos = self.to_canvas(mouse_pos)
        self.screen.draw(self.canvas, pos)
        pygame.mouse.set_visible(pos is None)
        if pos is not None:
            cursor_pos = (pos[0] - config.CURSOR_HOTSPOT[0], pos[1] - config.CURSOR_HOTSPOT[1])
            self.canvas.blit(self.resources.image("mouse_cursor", config.CURSOR_SIZE), cursor_pos)
        viewport = self.viewport
        self.window.fill(config.COLORS["letterbox"])
        if viewport.size == config.CANVAS_SIZE:
            self.window.blit(self.canvas, viewport)
        else:
            self.window.blit(pygame.transform.smoothscale(self.canvas, viewport.size), viewport)
        pygame.display.flip()

    def run(self):
        while self.running:
            seconds = self.clock.tick(config.FPS) / 1000.0
            self.step(seconds, pygame.event.get())
            if self.running:
                self.draw()

    @staticmethod
    def close():
        if pygame.display.get_init():
            pygame.mouse.set_visible(True)
        pygame.quit()


def main():
    try:
        Game().run()
    finally:
        Game.close()
