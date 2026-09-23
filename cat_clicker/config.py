"""Edit this file to tune the game. Restart the game to apply changes.

Pixels use a logical 1200 x 800 canvas; the window scales it proportionally.
Asset filenames and source dimensions are recorded in assets/manifest.json.
"""

from dataclasses import dataclass
from pathlib import Path

# Game rules (seconds, points, and multipliers).
TITLE = "Cat Clicker"
GAME_DURATION = 240.0
STARTING_POINTS = 0.0
POINTS_PER_CLICK = 1
POINT_EPSILON = 1e-9  # Tolerance for fractional automatic income.
TIME_EPSILON = 1e-9  # Ignore sub-nanosecond subtraction noise at the deadline.
PAUSE_ON_FOCUS_LOSS = True


@dataclass(frozen=True)
class Upgrade:
    name: str
    base_cost: int
    cost_increase: int
    limit: int
    income: float = 0.0
    speed_multiplier: float = 1.0
    points_multiplier: float = 1.0


# Dict order is also the shop order and the order of number-key shortcuts.
UPGRADES = {
    "cat_petter": Upgrade("Cat Petter", 10, 2, 15, income=1.0),
    "litter_box": Upgrade("Litter Box", 30, 10, 5, speed_multiplier=1.2),
    "yarn_ball": Upgrade("Yarn Ball", 80, 80, 6, points_multiplier=2.0),
    "cat_house": Upgrade("Cat House", 1000, 0, 1, income=100.0),
    "golden_kitty": Upgrade("Golden Kitty", 5500, 0, 1),
}

# Display and assets.
ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSET_MANIFEST = ASSET_DIR / "manifest.json"
CAT_PETTER_VARIANT_GLOB = "images/upgrades/cat_petter_*.png"
CANVAS_SIZE = (1200, 800)
WINDOW_SIZE = (1200, 800)
FPS = 60
RESIZABLE = True
CURSOR_HOTSPOT = (12, 12)
CURSOR_SIZE = (48, 48)
CAT_RECT = (120, 100, 960, 560)
CAT_HIT_ALPHA = 128

# Sound effects. Volume ranges from 0.0 (silent) to 1.0 (full volume).
SFX_ENABLED = True
SFX_VOLUME = 0.5
SFX_CHANNELS = 4  # Maximum overlapping meows; rapid clicks replace the oldest.
SFX_BUFFER_SIZE = 512
CAT_MEOW_PATH = ASSET_DIR / "audio/sfx/729031__redjamie7__cat-smokey-meow-1.mp3"

# Controls use pygame.key.name spellings; change these to rebind keys.
PAUSE_KEYS = ("p", "escape")
NEXT_KEYS = ("right", "space", "return")
BACK_KEYS = ("left", "backspace")
SHOP_KEYS = ("1", "2", "3", "4", "5")
PRIMARY_MOUSE_BUTTON = 1
BACK_MOUSE_BUTTON = 3

# Colors, font sizes, and shared drawing details.
COLORS = {
    "ink": (49, 43, 39),
    "muted": (110, 100, 91),
    "paper": (255, 248, 235),
    "panel": (255, 253, 247),
    "border": (207, 189, 166),
    "accent": (97, 137, 106),
    "hover": (232, 242, 224),
    "disabled": (235, 229, 219),
    "gold": (170, 112, 15),
    "gold_pale": (255, 237, 169),
    "warning": (173, 56, 51),
    "white": (255, 255, 255),
    "letterbox": (34, 31, 29),
}
FONT_SIZES = {"small": 20, "body": 24, "button": 26, "stat": 36, "title": 44, "hero": 60}
BORDER_WIDTH = 2
CORNER_RADIUS = 12
BUTTON_TEXT_PADDING = 12
LINE_GAP = 4
OVERLAY_ALPHA = 175
TITLE_OVERLAY_ALPHA = 155

# HUD: coordinates are top-left unless the name says CENTER.
HUD_RECT = (0, 0, 1200, 80)
HUD_COLUMNS = (28, 260, 510)
HUD_LABEL_Y = 12
HUD_VALUE_Y = 34
GOAL_LABEL_POS = (762, 14)
GOAL_BAR_RECT = (762, 44, 276, 16)
GOAL_BAR_RADIUS = 8
TIME_WARNING_SECONDS = 30
PAUSE_BUTTON_RECT = (1064, 20, 112, 42)

# Shop and the shared hint/tooltip area.
SHOP_RECT = (0, 660, 1200, 140)
SHOP_MARGIN = 16
SHOP_GAP = 12
SHOP_CARD_Y = 669
SHOP_CARD_HEIGHT = 122
SHOP_ICON_SIZE = (80, 80)
SHOP_ICON_OFFSET = (8, 22)
SHOP_TEXT_X = 96
SHOP_NAME_Y = 12
SHOP_PRICE_Y = 40
SHOP_COUNT_Y = 69
SHOP_ACTION_Y = 95
TOOLTIP_RECT = (18, 624, 1164, 32)
TOOLTIP_TEXT_OFFSET = (12, 6)

# Purchased pictures scale proportionally from their original PNG dimensions.
PROP_SCALES = {
    "cat_petter": 0.85,
    "litter_box": 0.85,
    "yarn_ball": 0.70,
    "cat_house": 0.85,
}
# Areas are (x, y, width, height) and contain the visible artwork, not its padding.
# Random positions are kept for the round; crowded areas can contain overlapping copies.
PROP_AREAS = {
    "cat_petter": (140, 90, 920, 420),  # Across the cat, in the top and middle.
    "litter_box": (24, 400, 456, 220),  # Bottom left, leaving room for the house.
    "yarn_ball": (720, 380, 456, 240),  # Bottom right, leaving room for the house.
    "cat_house": (480, 360, 240, 260),  # Centered in this area, resting on the floor.
}
GROUNDED_PROPS = ("litter_box", "yarn_ball", "cat_house")
PROP_GROUND_Y_RANGE = (584, 616)  # Visible bases sit on the floor above the help strip.
PROP_PLACEMENT_ATTEMPTS = 48     # Choose the least crowded of these random positions.
PETTER_OFF_CAT_PENALTY = 0.35    # Prefer positions touching the cat's visible silhouette.
PETTER_BOB_PIXELS = 5
PETTER_BOB_HZ = 1.5
PETTER_PHASE_STEP = 0.45  # Radians between hands so they pat at different times.
CLICK_POPUP_SECONDS = 0.65
CLICK_POPUP_RISE = 52
CLICK_POPUP_COLORS = (
    (255, 100, 110),  # Red
    (255, 169, 85),   # Orange
    (255, 225, 100),  # Yellow
    (125, 230, 135),  # Green
    (90, 215, 240),   # Cyan
    (125, 155, 255),  # Blue
    (205, 130, 255),  # Violet, then smoothly back to red.
)
MAX_CLICK_POPUPS = 32

# Pause menu.
PAUSE_PANEL_RECT = (330, 195, 540, 402)
PAUSE_TITLE_CENTER = (600, 249)
PAUSE_DETAIL_CENTER = (600, 299)
PAUSE_HINT_CENTER = (600, 328)
RESUME_BUTTON_RECT = (430, 364, 340, 52)
RESTART_BUTTON_RECT = (430, 426, 340, 52)
QUIT_BUTTON_RECT = (430, 488, 340, 52)

# Shared cutscene screen. Sequences and PNG order come from the manifest.
CUTSCENE_PANEL_RECT = (0, 710, 1200, 90)
CUTSCENE_TITLE_RECT = (16, 16, 450, 84)
CUTSCENE_TITLE_POS = (30, 24)
CUTSCENE_COUNTER_POS = (32, 68)
CUTSCENE_BACK_RECT = (24, 734, 116, 42)
CUTSCENE_NEXT_RECT = (1008, 734, 168, 42)
CUTSCENE_SKIP_RECT = (1016, 20, 160, 42)
CUTSCENE_QUIT_RECT = (1064, 72, 112, 36)
CUTSCENE_CAPTION_RECT = (164, 723, 820, 62)
CUTSCENE_CAPTIONS = {
    "opening": (
        "Just one little game before heading outside...",
        "Meet the cat. The Golden Kitty is waiting in the shop.",
        "Click the cat, buy helpers, and get Golden Kitty before the clock runs out!",
    ),
    "win": (
        "Golden Kitty is yours! Wait... why is the screen glowing?",
        "One last click pulls you straight into the game!",
        "Welcome to a world of cats. Make yourself at home.",
    ),
    "lose": (
        "Time is up. Golden Kitty will have to wait.",
        "Maybe it is time for a different kind of adventure.",
        "Fresh air. Sunshine. You finally touch grass.",
    ),
}
