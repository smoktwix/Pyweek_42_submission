"""One slideshow implementation for all three story sequences."""

import pygame

from . import config
from .ui import Button, paragraph, text


class CutsceneScreen:
    def __init__(self, resources, sequence):
        self.resources = resources
        self.sequence = sequence
        self.frames = resources.cutscenes[sequence]
        self.index = 0
        self.back_button = Button(config.CUTSCENE_BACK_RECT, "Back")
        self.next_button = Button(config.CUTSCENE_NEXT_RECT, "Next")
        self.skip_button = Button(config.CUTSCENE_SKIP_RECT, "Start game")
        self.quit_button = Button(config.CUTSCENE_QUIT_RECT, "Quit")

    def advance(self):
        if self.index < len(self.frames) - 1:
            self.index += 1
            return "navigated"
        return "start" if self.sequence == "opening" else "replay"

    def back(self):
        self.index = max(0, self.index - 1)
        return "navigated"

    def handle_event(self, event, pos):
        if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            key = pygame.key.name(event.key)
            if key in config.NEXT_KEYS:
                return self.advance()
            if key in config.BACK_KEYS:
                return self.back()
        if event.type == pygame.MOUSEBUTTONDOWN and pos is not None:
            if event.button == config.BACK_MOUSE_BUTTON:
                return self.back()
            if event.button != config.PRIMARY_MOUSE_BUTTON:
                return None
            if self.quit_button.contains(pos):
                return "quit"
            if self.sequence == "opening" and self.skip_button.contains(pos):
                return "start"
            if self.back_button.contains(pos):
                return self.back()
            return self.advance()
        return None

    def draw(self, surface, pos):
        frame = self.frames[self.index]
        if frame.get_size() != config.CANVAS_SIZE:
            frame = pygame.transform.smoothscale(frame, config.CANVAS_SIZE)
        surface.blit(frame, (0, 0))
        title_rect = pygame.Rect(config.CUTSCENE_TITLE_RECT)
        shade = pygame.Surface(title_rect.size, pygame.SRCALPHA)
        shade.fill((*config.COLORS["letterbox"], config.TITLE_OVERLAY_ALPHA))
        surface.blit(shade, title_rect)
        title = {"opening": config.TITLE, "win": "You won!", "lose": "Time is up"}[self.sequence]
        text(surface, self.resources, title, config.CUTSCENE_TITLE_POS, "title", "white")
        text(surface, self.resources, f"{self.index + 1} / {len(self.frames)}   |   Left / Right to browse",
             config.CUTSCENE_COUNTER_POS, "small", "white")
        pygame.draw.rect(surface, config.COLORS["paper"], config.CUTSCENE_PANEL_RECT)
        captions = config.CUTSCENE_CAPTIONS[self.sequence]
        caption = captions[self.index] if self.index < len(captions) else ""
        paragraph(surface, self.resources, caption, config.CUTSCENE_CAPTION_RECT)
        self.back_button.draw(surface, self.resources, pos, enabled=self.index > 0)
        self.next_button.label = "Next"
        if self.index == len(self.frames) - 1:
            self.next_button.label = "Play" if self.sequence == "opening" else "Play again"
        self.next_button.draw(surface, self.resources, pos, gold=True)
        self.quit_button.draw(surface, self.resources, pos)
        if self.sequence == "opening":
            self.skip_button.draw(surface, self.resources, pos)
