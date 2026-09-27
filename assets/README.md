# Cat Clicker Simulator assets

The artwork uses the **1200 × 800 (3:2)** canvas of the concept drawings. The game uses 24 opening drawings, 22 win drawings, and 6 lose drawings. A clean alternate of win frame 9 is also included.

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
| Opening frames 1–24 | `cutscenes/opening/open_cutscene_1.png` through `open_cutscene_24.png` | 1200 × 800 each | Opaque |
| Win frames 1–22 | `cutscenes/win/win_cutscene_1.png` through `win_cutscene_22.png` | 1200 × 800 each | Opaque |
| Lose frames 1–6 | `cutscenes/lose/lose_cutscene_1.png` through `lose_cutscene_6.png` | 1200 × 800 each | Opaque |
| Win frame 9 alternate | `cutscenes/win/win_cutscene_9 (No Pixels).png` | 1200 × 800 | Opaque |

There are **69 image files**: eight base gameplay images, eight extra Cat Petter variants,
52 cutscene frames in playback, and one alternate. Cat Petters use the base image and every variant once
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
- Cutscenes keep their 3:2 proportions and fit completely above the bottom 90-pixel control panel. Titles, navigation, and optional captions stay in that panel so they cannot cover the artwork or its dialogue.
- Prices, counts, timer, labels, and buttons belong in game code. The cutscene drawings include their own story text; the old placeholder captions have been removed from all sequences.
- Load sprites with Pygame's `convert_alpha()` after creating the display. Load opaque backgrounds/cutscenes with `convert()`.

## Sound and music

`audio/sfx/729031__redjamie7__cat-smokey-meow-1.mp3` plays when the player clicks
the cat. It is loaded once and reused for subsequent clicks. Change
`CAT_MEOW_PATH`, `SFX_VOLUME`, or `SFX_ENABLED` in `cat_clicker/config.py` to replace,
adjust, or mute it.

`audio/music/Curious_Cat_Quest_1.mp3` loops during opening, win, and lose
cutscenes. `audio/music/Curious_Cat_Quest_2.mp3` loops during gameplay.
Music pauses with the game and while the window is unfocused, then resumes
from the same position. Switching between cutscenes and gameplay starts the
new track from the beginning. `MUSIC_ENABLED`, `MUSIC_VOLUME`,
`CUTSCENE_MUSIC_PATH`, and `GAMEPLAY_MUSIC_PATH` configure music independently
of the meow effect. A missing audio device or track does not prevent play.

## Storyboard order

Every numbered frame plays once, in numeric order:

| Sequence | Frames | Trigger | After the last frame |
| --- | --- | --- | --- |
| Opening | 1–24 | Launch the game | Start a new round |
| Win | 1–22 | Buy Golden Kitty before the deadline | Offer to play again |
| Lose | 1–6 | Run out of time | Offer to play again |

Win frame 9 uses the numbered file with its pixel effect. `win_cutscene_9 (No Pixels).png` is alternate artwork, recorded under `alternates` in the manifest and shown separately in the preview. It is not an extra story frame.

[manifest.json](manifest.json) records exact sizes, transparency, proposed placement, cursor hotspot, and the cutscene playback order. When adding frames, update its `frames` list and the preview. Run the tests from the project root with `uv run python -m unittest discover -s tests -v`; they check that every cutscene image is either in playback or explicitly listed as an alternate, and that numbered frames play in order.

[GENERATION_PROMPTS.md](GENERATION_PROMPTS.md) records the original placeholder prompts and generation method. The placeholder artwork was made using the built-in image generation tool and resized to its final dimensions with macOS `sips`; the supplied cutscene drawings replace those sequences.
