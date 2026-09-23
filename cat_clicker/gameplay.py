"""The cat, shop, HUD, and pause menu for a single round."""

import math
import random

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
        self.next_popup_color = 0
        self.prop_random = random.Random()
        self.props = {name: [] for name in config.PROP_AREAS}
        self.prop_variants = {name: (name,) for name in config.PROP_AREAS}
        self.prop_variants["cat_petter"] = resources.cat_petter_variants
        self.prop_variant_bags = {name: [] for name in config.PROP_AREAS}
        self.prop_images = {}
        self.prop_bounds = {}
        for name, variants in self.prop_variants.items():
            for image_name in variants:
                original = resources.image(image_name)
                size = tuple(round(dimension * config.PROP_SCALES[name])
                             for dimension in original.get_size())
                image = resources.image(image_name, size)
                self.prop_images[image_name] = image
                self.prop_bounds[image_name] = image.get_bounding_rect(min_alpha=config.CAT_HIT_ALPHA)

    def update(self, seconds):
        if self.state.paused:
            return
        self.animation_time += seconds
        self.popups = [(pos, age + seconds, color) for pos, age, color in self.popups
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
            self.resources.play_cat_meow()
            self.popups.append((pos, 0.0, self.next_popup_color))
            self.next_popup_color = (self.next_popup_color + 1) % len(config.CLICK_POPUP_COLORS)
            self.popups = self.popups[-config.MAX_CLICK_POPUPS:]
        return None

    def draw(self, surface, pos):
        surface.blit(self.resources.image("background", config.CANVAS_SIZE), (0, 0))
        surface.blit(self.cat_image, self.cat_rect)
        self._draw_props(surface)
        for (x, y), age, color_index in self.popups:
            progress = age / config.CLICK_POPUP_SECONDS
            rise = round(config.CLICK_POPUP_RISE * progress)
            palette = config.CLICK_POPUP_COLORS
            start, end = palette[color_index], palette[(color_index + 1) % len(palette)]
            color = tuple(round(a + (b - a) * progress) for a, b in zip(start, end))
            text(surface, self.resources, f"+{config.POINTS_PER_CLICK}", (x, y - rise),
                 "stat", color, "center")
        self._draw_hud(surface, pos)
        self._draw_shop(surface, pos)
        if self.state.paused:
            self._draw_pause(surface, pos)

    def _draw_props(self, surface):
        drawings = []
        for name in config.PROP_AREAS:
            props = self.props[name]
            del props[self.state.owned[name]:]
            while len(props) < self.state.owned[name]:
                # Use every variant once per shuffled cycle; redraws keep each choice.
                bag = self.prop_variant_bags[name]
                if not bag:
                    bag.extend(self.prop_variants[name])
                    self.prop_random.shuffle(bag)
                image_name = bag.pop()
                position = self._place_prop(name, self.prop_bounds[image_name])
                props.append((image_name, position))
            for index, (image_name, position) in enumerate(props):
                image = self.prop_images[image_name]
                visible = self.prop_bounds[image_name]
                rect = image.get_rect(topleft=position)
                if name == "cat_petter":
                    phase = (self.animation_time * math.tau * config.PETTER_BOB_HZ
                             + index * config.PETTER_PHASE_STEP)
                    rect.y += round(math.sin(phase) * config.PETTER_BOB_PIXELS)
                drawings.append((rect.y + visible.bottom, image, rect))
        # Draw farther objects first so overlapping ground objects form a natural pile.
        drawings.sort(key=lambda drawing: drawing[0])
        for _, image, rect in drawings:
            surface.blit(image, rect)

    def _place_prop(self, name, visible):
        """Place scaled artwork without moving previously bought copies."""
        area = pygame.Rect(config.PROP_AREAS[name])
        if name == "cat_petter":
            area.inflate_ip(0, -config.PETTER_BOB_PIXELS * 2)
        min_y, max_y = area.top, area.bottom - visible.height
        if name in config.GROUNDED_PROPS:
            min_y = max(min_y, config.PROP_GROUND_Y_RANGE[0] - visible.height)
            max_y = min(max_y, config.PROP_GROUND_Y_RANGE[1] - visible.height)
        max_x = area.right - visible.width
        if max_x < area.left or max_y < min_y:
            raise ValueError(f"PROP_AREAS[{name!r}] must fit the scaled asset's visible size")

        if name == "cat_house":
            return (area.centerx - visible.width // 2 - visible.x,
                    (min_y + max_y) // 2 - visible.y)

        occupied = [self.prop_bounds[image_name].move(position)
                    for props in self.props.values() for image_name, position in props]
        best, best_score = None, float("inf")
        for _ in range(config.PROP_PLACEMENT_ATTEMPTS):
            candidate = pygame.Rect(self.prop_random.randint(area.left, max_x),
                                    self.prop_random.randint(min_y, max_y), *visible.size)
            score = 0
            for other in occupied:
                overlap = candidate.clip(other)
                score = max(score, overlap.width * overlap.height)
            if name == "cat_petter" and not self.cat_contains(candidate.center):
                score += visible.width * visible.height * config.PETTER_OFF_CAT_PENALTY
            if score < best_score:
                best, best_score = candidate, score
        return (best.x - visible.x, best.y - visible.y)

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
