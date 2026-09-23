"""Load artwork and sound once, using paths relative to the project."""

import json
import logging

import pygame

from . import config


class Resources:
    def __init__(self):
        manifest = json.loads(config.ASSET_MANIFEST.read_text())
        self.images = {}
        self.scaled = {}
        for name, spec in manifest["images"].items():
            self.images[name] = self._load(spec["path"], spec["size"], spec["transparent"])
        self.cat_petter_variants = ["cat_petter"]
        petter_spec = manifest["images"]["cat_petter"]
        for path in sorted(config.ASSET_DIR.glob(config.CAT_PETTER_VARIANT_GLOB)):
            self.images[path.stem] = self._load(path.relative_to(config.ASSET_DIR),
                                               petter_spec["size"], petter_spec["transparent"])
            self.cat_petter_variants.append(path.stem)
        self.cutscenes = {
            name: [self._load(path, spec["size"], False) for path in spec["frames"]]
            for name, spec in manifest["cutscenes"].items()
        }
        for name, frames in self.cutscenes.items():
            if not frames:
                raise ValueError(f"Cutscene {name!r} needs at least one image")
        self.fonts = {name: pygame.font.Font(None, size) for name, size in config.FONT_SIZES.items()}
        self.cat_meow = self._load_cat_meow()

    @staticmethod
    def _load_cat_meow():
        if not config.SFX_ENABLED:
            return None
        try:
            pygame.mixer.init(buffer=config.SFX_BUFFER_SIZE)
            pygame.mixer.set_num_channels(config.SFX_CHANNELS)
            sound = pygame.mixer.Sound(str(config.CAT_MEOW_PATH))
            sound.set_volume(config.SFX_VOLUME)
            return sound
        except (OSError, pygame.error) as error:
            logging.getLogger(__name__).warning("Sound unavailable; continuing silently: %s", error)
            return None

    def play_cat_meow(self):
        if self.cat_meow is not None:
            pygame.mixer.find_channel(force=True).play(self.cat_meow)

    @staticmethod
    def _load(relative_path, expected_size, transparent):
        path = config.ASSET_DIR / relative_path
        try:
            image = pygame.image.load(str(path))
        except (OSError, pygame.error) as error:
            raise RuntimeError(f"Cannot load game image: {path}") from error
        if image.get_size() != tuple(expected_size):
            raise ValueError(f"{path}: expected {tuple(expected_size)}, got {image.get_size()}")
        return image.convert_alpha() if transparent else image.convert()

    def image(self, name, size=None):
        original = self.images[name]
        if size is None or original.get_size() == tuple(size):
            return original
        key = (name, tuple(size))
        if key not in self.scaled:
            self.scaled[key] = pygame.transform.smoothscale(original, size)
        return self.scaled[key]
