# Cat Clicker Simulator

A small Pygame game: click the cat, buy helpers, and purchase Golden Kitty before
four minutes of active play run out. Cutscenes use the artwork in `assets/`:
24 opening frames, 22 win frames, and 6 lose frames, played in numeric order.

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

- Click the visible cat to earn one point and play a meow. Holding the button does not repeat clicks. Automatic income and shop purchases stay silent.
- Background music loops: **Curious Cat Quest 1** during all cutscenes and **Curious Cat Quest 2** during gameplay. Music pauses with the game or when the window loses focus.
- Successive +1 popups follow rainbow colors, each blending into the next color as it floats upward.
- Click a shop card or press **1–5** to purchase its upgrade. Hover over a card for its effect.
- Each purchased helper gets its own picture in the play area: up to 15 Cat Petters, 5 Litter Boxes, 6 Yarn Balls, and 1 Cat House. The shop also shows how many you own.
- Cat Petters use every available paw color once in a shuffled order before starting a new shuffled cycle. Each purchased Cat Petter keeps its image for the round.
- Cat Petters scatter around the cat's top and middle, Litter Boxes sit on the bottom-left ground, Yarn Balls sit on the bottom-right ground, and Cat House stands in the center on the ground. Pictures are slightly reduced for space, with smaller Yarn Balls. Positions stay fixed after purchase; crowded groups can overlap.
- Each Litter Box multiplies Cat Petter speed by **1.2**; each Yarn Ball multiplies their output by **2**.
- Cat Petters start at **10 points** and cost **10 more** after each purchase. Litter Boxes start at **30 points** and Yarn Balls at **80 points**; both prices **double** after each purchase.
- Cat House costs **5,999 points** and earns a separate **100 points/second**. Neither boost affects Cat House or manual clicks.
- Buy **Golden Kitty for 50,500 points** while time remains to win. Having enough points alone does not win.
- **P**, **Escape**, or the **Pause** button opens the pause menu. Time, automatic income, and purchases all stop.
- Switching away or minimizing pauses automatically. Return and explicitly resume when ready.
- In cutscenes, use **Left/Right**, **Space/Enter**, or the on-screen buttons. Left-click advances; right-click goes back.
- Cutscene artwork fits above the controls so the full drawing and its dialogue stay visible.
- **Start game** skips the opening. **Play again** at the end starts a fresh round. The pause menu also offers a restart.
- Close the window or choose **Quit** to exit.

The window can be resized; artwork keeps its proportions, and clicks in the
surrounding bars are ignored.

## Configuration and code

Edit **[cat_clicker/config.py](cat_clicker/config.py)** and restart to change the
title, duration, click value, upgrade prices, price increments and multipliers, limits, income,
multipliers, pause behavior, controls, window size, colors, fonts, layout, and
animation settings. Prices are `base_cost * cost_multiplier ** number_owned + cost_increase * number_owned`.
Use `cost_multiplier=1` for additive prices or `cost_increase=0` for multiplicative prices.

`PROP_SCALES` controls the play-area sizes relative to the original PNGs: 85% for
Cat Petters, Litter Boxes, and Cat House; 70% for Yarn Balls. `PROP_AREAS` controls
placement regions, leaving a clear space for Cat House in the center.
`PROP_GROUND_Y_RANGE` controls where the visible bases meet the floor. Cat House
is centered in its region at the midpoint of that ground range. Other helpers
try several random positions to reduce overlap and keep existing copies in
place. Scaled pictures and their visible bounds are cached when a round starts.
Shop thumbnails use `SHOP_ICON_SIZE`. Resizing the window still scales the whole
logical canvas uniformly.

Cat Petter artwork includes `cat_petter.png` and all files matching
`CAT_PETTER_VARIANT_GLOB` (by default, `images/upgrades/cat_petter_*.png` inside
`assets/`). Add matching transparent 256 × 256 PNGs and restart to include more
variants. All variants use the same `PROP_SCALES["cat_petter"]` setting.

`SFX_VOLUME` controls meow volume (0.0–1.0), and `SFX_ENABLED` turns meows on or
off. `CAT_MEOW_PATH` selects the sound file. `SFX_CHANNELS` limits overlapping
meows; rapid clicks replace the oldest when all channels are busy. If audio is
unavailable, the game logs the problem and continues silently.

`MUSIC_ENABLED` and `MUSIC_VOLUME` control background music independently.
`CUTSCENE_MUSIC_PATH` selects `Curious_Cat_Quest_1.mp3` for opening, win, and lose
cutscenes; `GAMEPLAY_MUSIC_PATH` selects `Curious_Cat_Quest_2.mp3` for play.
Both files live in `assets/audio/music/` and loop continuously. Browsing cutscene
frames and pausing/resuming preserve the current track's position; switching
between cutscenes and gameplay starts the appropriate track from the beginning.

`CLICK_POPUP_COLORS` sets the rainbow sequence. Each click starts with the next
color and blends into the following one over `CLICK_POPUP_SECONDS`, rising by
`CLICK_POPUP_RISE` pixels. Pausing freezes the popup animation.

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
cutscene order. The old placeholder captions are removed; `CUTSCENE_CAPTIONS`
can supply optional captions in frame order.

## Validate

```sh
uv run python -m unittest discover -s tests -v
```

The integration tests default to SDL's dummy video and audio drivers, so they
open no windows and need no audio device. They exercise real Pygame input events
and rendering,
including gameplay images, Cat Petter variants, cutscene frames, purchase limits,
compounding boosts, fractional income,
deadline precedence, manual/focus pauses, cutscene navigation, replay, quit,
transparent cat hit testing, input mapping after resizing, meow playback, and
operation with sound disabled or an unavailable audio device.
