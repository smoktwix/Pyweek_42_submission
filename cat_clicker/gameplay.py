"""The cat, shop, HUD, and pause menu for a single round."""

import math

import pygame

from . import config
from .ui import Button, points_text, text, time_text


class GameplayScreen:
    def __init__(self, resources, state):
        self.resources = resources
        self.state = state
        self.cat_rect = pygame.Rect(config.CAT_RECT)
        self.cat_image = resources.image("cat", self.cat_rect.size)
        self.cat_mask = pygame.mask.from_surface(self.cat_image, config.CAT_HIT_ALPHA)
        self.pause_button = Button(config.PAUSE_BUTTON_RECT, "Pause")
        self.menu = {
            "resume": Button(config.RESUME_BUTTON_RECT, "Resume"),
            "restart": Button(config.RESTART_BUTTON_RECT, "Restart round"),
            "quit": Button(config.QUIT_BUTTON_RECT, "Quit"),
        }
        shop = pygame.Rect(config.SHOP_RECT)
        count = len(config.UPGRADES)
        width = (shop.width - config.SHOP_MARGIN * 2 - config.SHOP_GAP * (count - 1)) // count
        self.cards = {
            name: pygame.Rect(shop.x + config.SHOP_MARGIN + index * (width + config.SHOP_GAP),
                              config.SHOP_CARD_Y, width, config.SHOP_CARD_HEIGHT)
            for index, name in enumerate(config.UPGRADES)
        }
        self.animation_time = 0.0
        self.popups = []

    def update(self, seconds):
        if self.state.paused:
            return
        self.animation_time += seconds
        self.popups = [(pos, age + seconds) for pos, age in self.popups
                       if age + seconds < config.CLICK_POPUP_SECONDS]

    def cat_contains(self, pos):
        if pos is None or not self.cat_rect.collidepoint(pos):
            return False
        local = (pos[0] - self.cat_rect.x, pos[1] - self.cat_rect.y)
        return bool(self.cat_mask.get_at(local))

    def handle_event(self, event, pos):
        if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            key = pygame.key.name(event.key)
            if key in config.PAUSE_KEYS:
                return "resume" if self.state.paused else "pause"
            if not self.state.paused and key in config.SHOP_KEYS:
                index = config.SHOP_KEYS.index(key)
                if index < len(self.cards):
                    self.state.buy(tuple(self.cards)[index])
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != config.PRIMARY_MOUSE_BUTTON:
            return None
        if self.state.paused:
            for action, button in self.menu.items():
                if button.contains(pos):
                    return action
            return None
        if self.pause_button.contains(pos):
            return "pause"
        for name, rect in self.cards.items():
            if pos is not None and rect.collidepoint(pos):
                self.state.buy(name)
                return None
        if self.cat_contains(pos) and self.state.click():
            self.popups.append((pos, 0.0))
            self.popups = self.popups[-config.MAX_CLICK_POPUPS:]
        return None

    def draw(self, surface, pos):
        surface.blit(self.resources.image("background", config.CANVAS_SIZE), (0, 0))
        surface.blit(self.cat_image, self.cat_rect)
        self._draw_props(surface)
        for (x, y), age in self.popups:
            rise = round(config.CLICK_POPUP_RISE * age / config.CLICK_POPUP_SECONDS)
            text(surface, self.resources, f"+{config.POINTS_PER_CLICK}", (x, y - rise),
                 "stat", "gold", "center")
        self._draw_hud(surface, pos)
        self._draw_shop(surface, pos)
        if self.state.paused:
            self._draw_pause(surface, pos)

    def _draw_props(self, surface):
        for name, placement in config.PROP_RECTS.items():
            count = self.state.owned[name]
            if not count:
                continue
            rect = pygame.Rect(placement)
            if name == "cat_petter":
                rect.y += round(math.sin(self.animation_time * math.tau * config.PETTER_BOB_HZ)
                                * config.PETTER_BOB_PIXELS)
            image = self.resources.image(name, rect.size)
            surface.blit(image, rect)
            visible = image.get_bounding_rect(min_alpha=config.CAT_HIT_ALPHA).move(rect.topleft)
            badge = pygame.Rect((0, 0), config.PROP_BADGE_SIZE)
            badge.midtop = (visible.centerx, visible.bottom + config.PROP_BADGE_OFFSET_Y)
            pygame.draw.rect(surface, config.COLORS["paper"], badge, border_radius=config.CORNER_RADIUS)
            text(surface, self.resources, f"x{count}", badge.center, "small", anchor="center")

    def _draw_hud(self, surface, pos):
        pygame.draw.rect(surface, config.COLORS["paper"], config.HUD_RECT)
        stats = (
            ("TIME", time_text(self.state.remaining), "warning" if self.state.remaining <= config.TIME_WARNING_SECONDS else "ink"),
            ("POINTS", points_text(self.state.points), "ink"),
            ("POINTS / SECOND", f"{self.state.points_per_second:,.1f}", "ink"),
        )
        for x, (label, value, color) in zip(config.HUD_COLUMNS, stats):
            text(surface, self.resources, label, (x, config.HUD_LABEL_Y), "small", "muted")
            text(surface, self.resources, value, (x, config.HUD_VALUE_Y), "stat", color)
        goal = self.state.price("golden_kitty")
        text(surface, self.resources, f"Golden Kitty: {points_text(goal)} points",
             config.GOAL_LABEL_POS, "small", "gold")
        bar = pygame.Rect(config.GOAL_BAR_RECT)
        pygame.draw.rect(surface, config.COLORS["disabled"], bar, border_radius=config.GOAL_BAR_RADIUS)
        fill = bar.copy()
        fill.width = round(bar.width * min(1.0, self.state.points / goal)) if goal else bar.width
        if fill.width:
            pygame.draw.rect(surface, config.COLORS["gold"], fill, border_radius=config.GOAL_BAR_RADIUS)
        self.pause_button.draw(surface, self.resources, pos)

    def _description(self, name):
        spec = config.UPGRADES[name]
        if name == "cat_petter":
            return f"Each Cat Petter earns {spec.income:g} point/s before boosts."
        if name == "litter_box":
            return f"Multiply all Cat Petters' speed by {spec.speed_multiplier:g}. Stacks with every purchase."
        if name == "yarn_ball":
            return f"Multiply all Cat Petters' output by {spec.points_multiplier:g}. Stacks with every purchase."
        if name == "cat_house":
            return f"Earn {spec.income:g} points/s. Litter Boxes and Yarn Balls boost Cat Petters only."
        return f"Buy {spec.name} before time runs out to win!"

    def _draw_shop(self, surface, pos):
        pygame.draw.rect(surface, config.COLORS["paper"], config.SHOP_RECT)
        hint = (f"Click the cat: +{config.POINTS_PER_CLICK} point  |  Shop: {' / '.join(config.SHOP_KEYS)}"
                f"  |  Pause: {' / '.join(config.PAUSE_KEYS)}")
        for index, (name, rect) in enumerate(self.cards.items()):
            spec = config.UPGRADES[name]
            maximum = self.state.at_limit(name)
            affordable = self.state.can_buy(name)
            hovered = pos is not None and rect.collidepoint(pos)
            fill = "panel" if affordable else "disabled"
            border = "accent" if affordable else "border"
            if name == "golden_kitty" and affordable:
                fill, border = "gold_pale", "gold"
            if hovered:
                fill = "hover" if affordable else fill
                hint = self._description(name)
            pygame.draw.rect(surface, config.COLORS[fill], rect, border_radius=config.CORNER_RADIUS)
            pygame.draw.rect(surface, config.COLORS[border], rect,
                             config.BORDER_WIDTH, border_radius=config.CORNER_RADIUS)
            image_pos = (rect.x + config.SHOP_ICON_OFFSET[0], rect.y + config.SHOP_ICON_OFFSET[1])
            surface.blit(self.resources.image(name, config.SHOP_ICON_SIZE), image_pos)
            x = rect.x + config.SHOP_TEXT_X
            available_width = rect.right - x - config.BUTTON_TEXT_PADDING
            text(surface, self.resources, spec.name, (x, rect.y + config.SHOP_NAME_Y),
                 "body", max_width=available_width)
            price = "MAX" if maximum else points_text(self.state.price(name))
            text(surface, self.resources, price, (x, rect.y + config.SHOP_PRICE_Y),
                 "button", "gold" if name == "golden_kitty" else "ink", max_width=available_width)
            text(surface, self.resources, f"Owned {self.state.owned[name]}/{spec.limit}",
                 (x, rect.y + config.SHOP_COUNT_Y), "small", "muted", max_width=available_width)
            action = "Sold out" if maximum else "Buy" if affordable else "Save up"
            if index < len(config.SHOP_KEYS):
                action = f"[{config.SHOP_KEYS[index]}] {action}"
            text(surface, self.resources, action, (x, rect.y + config.SHOP_ACTION_Y),
                 "small", "accent" if affordable else "muted", max_width=available_width)
        panel = pygame.Rect(config.TOOLTIP_RECT)
        pygame.draw.rect(surface, config.COLORS["paper"], panel, border_radius=config.CORNER_RADIUS)
        text(surface, self.resources, hint,
             (panel.x + config.TOOLTIP_TEXT_OFFSET[0], panel.y + config.TOOLTIP_TEXT_OFFSET[1]),
             "small", max_width=panel.width - config.TOOLTIP_TEXT_OFFSET[0] * 2)

    def _draw_pause(self, surface, pos):
        shade = pygame.Surface(config.CANVAS_SIZE, pygame.SRCALPHA)
        shade.fill((*config.COLORS["letterbox"], config.OVERLAY_ALPHA))
        surface.blit(shade, (0, 0))
        pygame.draw.rect(surface, config.COLORS["paper"], config.PAUSE_PANEL_RECT,
                         border_radius=config.CORNER_RADIUS)
        text(surface, self.resources, "Paused", config.PAUSE_TITLE_CENTER, "hero", anchor="center")
        text(surface, self.resources, "Time and points are on hold.",
             config.PAUSE_DETAIL_CENTER, anchor="center")
        text(surface, self.resources, f"Press {' / '.join(config.PAUSE_KEYS)} or choose Resume.",
             config.PAUSE_HINT_CENTER, "small", "muted", "center")
        for button in self.menu.values():
            button.draw(surface, self.resources, pos)
