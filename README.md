# Cat Clicker

A small Pygame game: click the cat, buy helpers, and purchase Golden Kitty before
four minutes of active play run out. Opening, win, and lose cutscenes use the
temporary artwork in `assets/`.

## Run

With Python 3.13+ and `uv` installed:

```sh
uv sync
uv run python main.py
```

Or use a regular virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pygame==2.6.1
python main.py
```

On Windows, activate with `.venv\Scripts\activate` instead. Assets resolve relative
to the project, so you can also launch `main.py` by its absolute path.

## How to play

- Click the visible cat to earn one point per click. Holding the button does not repeat clicks.
- Click a shop card or press **1–5** to purchase its upgrade. Hover over a card for its effect.
- Each Litter Box multiplies Cat Petter speed by **1.2**; each Yarn Ball multiplies their output by **2**.
- Cat House earns a separate **100 points/second**. Neither boost affects Cat House or manual clicks.
- Buy **Golden Kitty for 5,500 points** while time remains to win. Having enough points alone does not win.
- **P**, **Escape**, or the **Pause** button opens the pause menu. Time, automatic income, and purchases all stop.
- Switching away or minimizing pauses automatically. Return and explicitly resume when ready.
- In cutscenes, use **Left/Right**, **Space/Enter**, or the on-screen buttons. Left-click advances; right-click goes back.
- **Start game** skips the opening. **Play again** at the end starts a fresh round. The pause menu also offers a restart.
- Close the window or choose **Quit** to exit.

The window can be resized; artwork keeps its proportions, and clicks in the
surrounding bars are ignored. This first version is silent; music and sound
assets can be added later.

## Configuration and code

Edit **[cat_clicker/config.py](cat_clicker/config.py)** and restart to change the
title, duration, click value, upgrade prices, price increments, limits, income,
multipliers, pause behavior, controls, window size, colors, fonts, layout, and
animation settings. Prices are `base_cost + cost_increase * number_owned`.

Automatic income is calculated continuously, preserving fractional points:

```text
petters * petter_income * litter_speed_multiplier ** litter_boxes
    * yarn_points_multiplier ** yarn_balls
    + houses * house_income
```

The HUD displays whole spendable points and a rate rounded to one decimal place.
No progress is saved between runs.

- `main.py` — launcher.
- `cat_clicker/model.py` — points, purchases, production, timer, and outcomes; no Pygame dependency.
- `cat_clicker/game.py` — main loop, focus handling, scaling, and screen transitions.
- `cat_clicker/gameplay.py` — cat interaction, shop, HUD, and pause menu.
- `cat_clicker/cutscene.py` — shared opening/win/lose slideshow.
- `cat_clicker/resources.py` and `ui.py` — asset loading and small drawing helpers.
- `tests/` — rule and Pygame integration tests.

Keep the logical 1200 × 800 canvas for the supplied layout; use `WINDOW_SIZE`
to change the physical window size. Runtime layout settings live in `config.py`;
the layout block in the asset manifest is an art reference.

See the **[asset replacement guide](assets/README.md)** for PNG dimensions,
transparency, and filenames. `assets/manifest.json` lists asset paths and explicit
cutscene order. Put new caption text in `CUTSCENE_CAPTIONS` if adding frames.

## Validate

```sh
uv run python -m unittest discover -s tests -v
```

The integration tests default to SDL's dummy video driver, so they open no windows
and need no audio device. They exercise real Pygame input events and rendering,
including all 17 images, purchase limits, compounding boosts, fractional income,
deadline precedence, manual/focus pauses, cutscene navigation, replay, quit,
transparent cat hit testing, and input mapping after resizing.
