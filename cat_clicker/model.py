"""Gameplay rules with no Pygame dependency."""

from dataclasses import dataclass, field
from math import isfinite

from . import config


@dataclass
class GameState:
    duration: float = field(default_factory=lambda: config.GAME_DURATION)
    points: float = field(default_factory=lambda: float(config.STARTING_POINTS))
    remaining: float = field(init=False)
    owned: dict[str, int] = field(default_factory=lambda: dict.fromkeys(config.UPGRADES, 0))
    paused: bool = False
    outcome: str | None = None

    def __post_init__(self):
        if not isfinite(self.duration) or self.duration <= 0:
            raise ValueError("GAME_DURATION must be a positive number of seconds")
        self.remaining = self.duration

    @property
    def active(self):
        return not self.paused and self.outcome is None and self.remaining > 0

    @property
    def points_per_second(self):
        upgrades = config.UPGRADES
        petters = self.owned["cat_petter"] * upgrades["cat_petter"].income
        speed = upgrades["litter_box"].speed_multiplier ** self.owned["litter_box"]
        power = upgrades["yarn_ball"].points_multiplier ** self.owned["yarn_ball"]
        houses = self.owned["cat_house"] * upgrades["cat_house"].income
        return petters * speed * power + houses

    def price(self, upgrade_id):
        spec = config.UPGRADES[upgrade_id]
        return spec.base_cost + spec.cost_increase * self.owned[upgrade_id]

    def at_limit(self, upgrade_id):
        return self.owned[upgrade_id] >= config.UPGRADES[upgrade_id].limit

    def can_buy(self, upgrade_id):
        return (self.active and not self.at_limit(upgrade_id)
                and self.points + config.POINT_EPSILON >= self.price(upgrade_id))

    def buy(self, upgrade_id):
        if not self.can_buy(upgrade_id):
            return False
        self.points = max(0.0, self.points - self.price(upgrade_id))
        self.owned[upgrade_id] += 1
        if upgrade_id == "golden_kitty":
            self.outcome = "win"
        return True

    def click(self):
        if not self.active:
            return False
        self.points += config.POINTS_PER_CLICK
        return True

    def advance(self, seconds):
        """Accrue fractional income, stopping exactly at the deadline.

        Reaching the price alone never wins: Golden Kitty must be purchased
        while time remains. Pauses freeze income as well as the countdown.
        """
        if not isfinite(seconds) or seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative")
        if not self.active:
            return
        elapsed = min(seconds, self.remaining)
        self.points += self.points_per_second * elapsed
        self.remaining = max(0.0, self.remaining - elapsed)
        if self.remaining <= config.TIME_EPSILON:
            self.remaining = 0.0
            self.outcome = "lose"
