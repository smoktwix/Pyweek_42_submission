# Temporary Cat Clicker assets

The artwork uses the **1200 × 800 (3:2)** canvas of the concept drawings. These are temporary AI-generated PNGs with simple outlines and soft colors, ready to replace with your own drawings.

Open [preview.html](preview.html) in a browser to review the gameplay composition, toggle purchased objects, try the cursor, and browse all cutscenes. It works directly from disk without installing anything or starting a server.

## Image sizes

All paths below are relative to this directory.

| Asset | Path | Canvas size | Background |
| --- | --- | --- | --- |
| Room | `images/backgrounds/room.png` | 1200 × 800 | Opaque |
| Clickable cat | `images/cats/cat.png` | 960 × 560 | Transparent |
| Golden Kitty | `images/cats/golden_kitty.png` | 256 × 256 | Transparent |
| Cat Petter | `images/upgrades/cat_petter.png` | 256 × 256 | Transparent |
| Cat Petter variants | `images/upgrades/cat_petter_2.png` through `cat_petter_9.png` | 256 × 256 each | Transparent |
| Litter Box | `images/upgrades/litter_box.png` | 256 × 256 | Transparent |
| Yarn Ball | `images/upgrades/yarn_ball.png` | 256 × 256 | Transparent |
| Cat House | `images/upgrades/cat_house.png` | 256 × 256 | Transparent |
| Animal mouse cursor | `images/ui/mouse_cursor.png` | 48 × 48 | Transparent |
| Opening frames 1–3 | `cutscenes/opening/open_cutscene_1.png` through `open_cutscene_3.png` | 1200 × 800 each | Opaque |
| Win frames 1–3 | `cutscenes/win/win_cutscene_1.png` through `win_cutscene_3.png` | 1200 × 800 each | Opaque |
| Lose frames 1–3 | `cutscenes/lose/lose_cutscene_1.png` through `lose_cutscene_3.png` | 1200 × 800 each | Opaque |

There are **25 PNGs**: eight base gameplay images, eight extra Cat Petter variants,
and nine cutscene frames. Cat Petters use the base image and every variant once
in a shuffled order before repeating with a new shuffled cycle. Each keeps its
choice throughout the round. Add more
`images/upgrades/cat_petter_*.png` files at 256 × 256 with transparency and restart
the game to include them automatically.

## Placement and replacement guide

- Keep each replacement's **filename, full canvas dimensions, and transparency**. Do not trim away the transparent padding; it keeps the object positioned consistently.
- Treat 1200 × 800 as the game's logical drawing surface. If the window changes size later, scale the complete surface uniformly and letterbox it rather than stretching individual drawings.
- Place the background at `(0, 0)` and the main cat at `(120, 100)`. Reserve the top 80 pixels for timer/points and the bottom 140 pixels for the shop, following the concept art.
- The five 256 × 256 sprites are reusable source images. A suggested shop display size is **80 × 80**. Purchased objects can use larger, uniform scales in the play area.
- The cursor's click hotspot is **(12, 12)**, at the mouse's nose. Draw its 48 × 48 canvas at mouse position minus this offset. Keep the nose at this point when replacing the artwork.
- Cutscenes fill the screen. Keep important action above the bottom 90 pixels so navigation and optional captions can be drawn over that area.
- Prices, counts, timer, labels, buttons, and captions belong in game code; none are baked into these assets.
- Load sprites with Pygame's `convert_alpha()` after creating the display. Load opaque backgrounds/cutscenes with `convert()`.

## Sound effects

`audio/sfx/729031__redjamie7__cat-smokey-meow-1.mp3` plays when the player clicks
the cat. It is loaded once and reused for subsequent clicks. Change
`CAT_MEOW_PATH`, `SFX_VOLUME`, or `SFX_ENABLED` in `cat_clicker/config.py` to replace,
adjust, or mute it.

## Storyboard order

| Sequence | Frame 1 | Frame 2 | Frame 3 |
| --- | --- | --- | --- |
| Opening | Girl arrives at her computer | She sees the cat and Golden Kitty goal | She begins clicking |
| Win | Golden Kitty purchase succeeds | The monitor pulls her into the game | She is inside the game with the cats |
| Lose | Time runs out | She leaves the computer and steps outside | She touches grass |

The frames use the same character description: dark brown bob, lavender hoodie, blue jeans, and white sneakers. Small drawing differences between generated frames are expected in this temporary set.

[manifest.json](manifest.json) records exact sizes, transparency, proposed placement, cursor hotspot, and explicit cutscene order for future game code.

[GENERATION_PROMPTS.md](GENERATION_PROMPTS.md) records the prompts and generation method. Artwork was made using the built-in image generation tool and resized to its final dimensions with macOS `sips`.
