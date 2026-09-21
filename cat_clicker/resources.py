"""Load artwork once, using paths relative to the project rather than cwd."""

import json

import pygame

from . import config


class Resources:
    def __init__(self):
        manifest = json.loads(config.ASSET_MANIFEST.read_text())
        self.images = {}
        self.scaled = {}
        for name, spec in manifest["images"].items():
            self.images[name] = self._load(spec["path"], spec["size"], spec["transparent"])
        self.cutscenes = {
            name: [self._load(path, spec["size"], False) for path in spec["frames"]]
            for name, spec in manifest["cutscenes"].items()
        }
        for name, frames in self.cutscenes.items():
            if not frames:
                raise ValueError(f"Cutscene {name!r} needs at least one image")
        self.fonts = {name: pygame.font.Font(None, size) for name, size in config.FONT_SIZES.items()}

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
