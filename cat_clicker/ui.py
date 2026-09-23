"""A small set of shared drawing helpers."""

from math import ceil, floor

import pygame

from . import config


def points_text(value):
    return f"{floor(value + config.POINT_EPSILON):,}"


def time_text(seconds):
    minutes, seconds = divmod(max(0, ceil(seconds - config.TIME_EPSILON)), 60)
    return f"{minutes}:{seconds:02d}"


def text(surface, resources, value, pos, style="body", color="ink", anchor="topleft", max_width=None):
    color = config.COLORS[color] if isinstance(color, str) else color
    image = resources.fonts[style].render(str(value), True, color)
    if max_width and image.get_width() > max_width:
        height = max(1, round(image.get_height() * max_width / image.get_width()))
        image = pygame.transform.smoothscale(image, (max_width, height))
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def paragraph(surface, resources, value, rect, style="body"):
    """Wrap captions to their panel, respecting the configured font."""
    rect = pygame.Rect(rect)
    font = resources.fonts[style]
    lines = []
    line = ""
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if line and font.size(candidate)[0] > rect.width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    line_height = font.get_height() + config.LINE_GAP
    top = rect.centery - (len(lines) * line_height - config.LINE_GAP) // 2
    for index, line in enumerate(lines):
        text(surface, resources, line, (rect.centerx, top + index * line_height),
             style, anchor="midtop", max_width=rect.width)


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def contains(self, pos):
        return pos is not None and self.rect.collidepoint(pos)

    def draw(self, surface, resources, pos, enabled=True, gold=False):
        fill = "gold_pale" if gold else "panel"
        if not enabled:
            fill = "disabled"
        elif self.contains(pos):
            fill = "hover"
        border = "gold" if gold else "border"
        pygame.draw.rect(surface, config.COLORS[fill], self.rect, border_radius=config.CORNER_RADIUS)
        pygame.draw.rect(surface, config.COLORS[border], self.rect,
                         config.BORDER_WIDTH, border_radius=config.CORNER_RADIUS)
        text(surface, resources, self.label, self.rect.center, "button",
             "ink" if enabled else "muted", "center",
             self.rect.width - config.BUTTON_TEXT_PADDING * 2)
