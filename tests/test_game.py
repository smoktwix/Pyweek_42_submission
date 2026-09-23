"""Exercise the actual Pygame event, asset-loading, and rendering paths."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from cat_clicker import config
from cat_clicker.cutscene import CutsceneScreen
from cat_clicker.game import Game
from cat_clicker.ui import points_text, time_text


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code)


def click(pos, button=1):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button)


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        pygame.event.clear()

    def tearDown(self):
        self.game.close()

    def start(self):
        self.game.step(0, [click(self.game.screen.skip_button.rect.center)])
        self.assertEqual(self.game.mode, "playing")

    def test_opening_has_no_running_timer(self):
        self.game.step(1000, [])
        self.assertEqual(self.game.mode, "opening")
        self.assertIsNone(self.game.state)

    def test_opening_forward_back_and_start(self):
        self.game.step(0, [key(pygame.K_RIGHT)])
        self.assertEqual(self.game.screen.index, 1)
        self.game.step(0, [key(pygame.K_LEFT)])
        self.assertEqual(self.game.screen.index, 0)
        for _ in range(3):
            self.game.step(0, [key(pygame.K_SPACE)])
        self.assertEqual(self.game.mode, "playing")
        self.assertEqual(self.game.state.remaining, 240)

    def test_right_click_browses_back_and_first_frame_is_bounded(self):
        self.game.step(0, [click((600, 400))])
        self.game.step(0, [click((600, 400), button=3)])
        self.game.step(0, [click(self.game.screen.back_button.rect.center)])
        self.assertEqual(self.game.screen.index, 0)

    def test_start_click_does_not_also_click_cat(self):
        self.game.screen.index = 2
        self.game.step(0, [click((400, 380)), click((400, 380))])
        self.assertEqual(self.game.mode, "playing")
        self.assertEqual(self.game.state.points, 0)

    def test_clicks_only_count_on_visible_cat(self):
        self.start()
        self.game.step(0, [click((130, 110)), click((20, 200)), click((400, 380), button=3)])
        self.assertEqual(self.game.state.points, 0)
        self.game.step(0, [click((400, 380))])
        self.assertEqual(self.game.state.points, 1)
        self.assertEqual(len(self.game.screen.popups), 1)
        self.game.step(1, [pygame.event.Event(pygame.MOUSEMOTION, pos=(400, 380), buttons=(1, 0, 0)),
                           pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(400, 380), button=1)])
        self.assertEqual(self.game.state.points, 1)
        self.assertEqual(len(self.game.screen.popups), 0)

    def test_mouse_and_keyboard_shop_purchases(self):
        self.start()
        self.game.step(0, [click((400, 380)) for _ in range(10)])
        self.game.step(0, [click(self.game.screen.cards["cat_petter"].center)])
        self.assertEqual((self.game.state.points, self.game.state.owned["cat_petter"]), (0, 1))
        self.game.step(12, [key(pygame.K_1)])
        self.assertEqual((self.game.state.points, self.game.state.owned["cat_petter"]), (0, 2))

    def test_meow_plays_only_for_manual_cat_clicks(self):
        sound = self.game.resources.cat_meow
        self.assertIsNotNone(sound)
        self.assertGreater(sound.get_length(), 0)
        self.assertAlmostEqual(sound.get_volume(), config.SFX_VOLUME, delta=1 / 128)
        self.start()
        self.assertEqual(sound.get_num_channels(), 0)
        self.game.step(0, [click((400, 380))])
        self.assertEqual(sound.get_num_channels(), 1)
        self.game.step(0, [click((400, 380)) for _ in range(config.SFX_CHANNELS * 2)])
        self.assertEqual(sound.get_num_channels(), config.SFX_CHANNELS)
        sound.stop()
        self.game.state.points = 100
        self.game.step(0, [click((130, 110)), click((20, 200)), click((400, 380), button=3),
                           click(self.game.screen.cards["cat_petter"].center)])
        self.game.step(1, [])  # Automatic income does not meow.
        self.assertEqual(sound.get_num_channels(), 0)
        self.game.step(0, [key(pygame.K_p)])
        self.game.step(0, [click((400, 380))])
        self.assertEqual(sound.get_num_channels(), 0)
        self.game.step(0, [key(pygame.K_p)])
        self.game.step(config.GAME_DURATION, [click((400, 380))])
        self.assertEqual(sound.get_num_channels(), 0)

    def test_missing_audio_device_does_not_prevent_play(self):
        self.game.close()
        with patch("pygame.mixer.init", side_effect=pygame.error("No audio device")):
            with self.assertLogs("cat_clicker.resources", level="WARNING"):
                self.game = Game()
        self.assertIsNone(self.game.resources.cat_meow)
        self.start()
        self.game.step(0, [click((400, 380))])
        self.assertEqual(self.game.state.points, 1)

    def test_sound_can_be_disabled(self):
        self.game.close()
        with patch.object(config, "SFX_ENABLED", False):
            self.game = Game()
        self.assertIsNone(pygame.mixer.get_init())
        self.assertIsNone(self.game.resources.cat_meow)
        self.start()
        self.game.step(0, [click((400, 380))])
        self.assertEqual(self.game.state.points, 1)

    def test_pause_blocks_shop_and_cat_input_then_resumes(self):
        self.start()
        self.game.state.points = 100
        self.game.step(0, [key(pygame.K_p)])
        self.game.step(1000, [key(pygame.K_1), click((400, 380))])
        self.assertEqual((self.game.state.points, self.game.state.remaining), (100, 240))
        self.assertEqual(self.game.state.owned["cat_petter"], 0)
        self.game.step(10, [key(pygame.K_ESCAPE)])
        self.assertFalse(self.game.state.paused)
        self.assertEqual(self.game.state.remaining, 240)
        self.game.step(1, [])
        self.assertEqual(self.game.state.remaining, 239)

    def test_focus_loss_and_minimizing_pause_without_auto_resume(self):
        for event_type in (pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED):
            with self.subTest(event_type=event_type):
                self.game.start_round()
                self.game.focused = True
                self.game.state.paused = False
                self.game.step(1000, [pygame.event.Event(event_type)])
                self.assertEqual(self.game.state.remaining, 240)
                self.assertTrue(self.game.state.paused)
                self.game.step(10, [key(pygame.K_p)])
                self.assertTrue(self.game.state.paused)
                self.game.step(10, [pygame.event.Event(pygame.WINDOWFOCUSGAINED)])
                self.assertTrue(self.game.state.paused)
                self.game.step(0, [click(self.game.screen.menu["resume"].rect.center)])
                self.assertFalse(self.game.state.paused)

    def test_pause_button_and_restart_reset_round(self):
        self.start()
        self.game.state.points = 100
        self.game.state.buy("cat_petter")
        self.game.step(20, [click(self.game.screen.pause_button.rect.center)])
        self.assertTrue(self.game.state.paused)
        self.game.step(0, [click(self.game.screen.menu["restart"].rect.center)])
        self.assertEqual((self.game.state.points, self.game.state.remaining), (0, 240))
        self.assertFalse(self.game.state.paused)
        self.assertTrue(all(value == 0 for value in self.game.state.owned.values()))

    def test_golden_purchase_shows_win_and_consumes_event_batch(self):
        self.start()
        self.game.state.points = 5500
        self.game.step(239.99, [click(self.game.screen.cards["golden_kitty"].center), key(pygame.K_SPACE)])
        self.assertEqual(self.game.mode, "win")
        self.assertEqual(self.game.screen.index, 0)
        self.assertEqual(self.game.state.points, 0)

    def test_deadline_wins_over_late_purchase_input(self):
        self.start()
        self.game.state.points = 5500
        self.game.step(240, [key(pygame.K_5)])
        self.assertEqual(self.game.mode, "lose")
        self.assertEqual(self.game.state.owned["golden_kitty"], 0)
        self.assertEqual(self.game.screen.index, 0)

    def test_both_endings_can_go_back_and_replay(self):
        for outcome in ("win", "lose"):
            with self.subTest(outcome=outcome):
                self.game.start_round()
                if outcome == "win":
                    self.game.state.points = 5500
                    self.game.step(1, [key(pygame.K_5)])
                else:
                    self.game.step(240, [])
                self.game.step(0, [key(pygame.K_RIGHT)])
                self.game.step(0, [key(pygame.K_LEFT)])
                self.assertEqual(self.game.screen.index, 0)
                for _ in range(3):
                    self.game.step(0, [key(pygame.K_RETURN)])
                self.assertEqual(self.game.mode, "playing")
                self.assertEqual((self.game.state.points, self.game.state.remaining), (0, 240))

    def test_resize_preserves_hit_testing_and_ignores_letterbox(self):
        self.start()
        for size in ((900, 900), (1600, 800), (600, 400)):
            with self.subTest(size=size):
                self.game.window = pygame.display.set_mode(size)
                viewport = self.game.viewport
                self.assertAlmostEqual(viewport.width / viewport.height, 1.5, places=2)
                pos = (viewport.x + round(400 * viewport.width / 1200),
                       viewport.y + round(380 * viewport.height / 800))
                before = self.game.state.points
                self.game.step(0, [click(pos)])
                self.assertEqual(self.game.state.points, before + 1)
                self.game.draw(mouse_pos=pos)
                if viewport.topleft != (0, 0):
                    self.assertIsNone(self.game.to_canvas((0, 0)))
                    self.game.step(0, [click((0, 0))])
                    self.assertEqual(self.game.state.points, before + 1)

    def test_all_art_and_cutscene_frames_render(self):
        self.assertEqual(len(self.game.resources.images),
                         7 + len(self.game.resources.cat_petter_variants))
        self.assertEqual(sum(map(len, self.game.resources.cutscenes.values())), 9)
        for sequence, frames in self.game.resources.cutscenes.items():
            screen = CutsceneScreen(self.game.resources, sequence)
            for index in range(len(frames)):
                with self.subTest(sequence=sequence, frame=index):
                    screen.index = index
                    screen.draw(self.game.canvas, None)
                    self.assertEqual(self.game.canvas.get_size(), (1200, 800))
        for name in config.PROP_AREAS:
            self.assertTrue(self.game.resources.image(name).get_flags() & pygame.SRCALPHA)

    def test_gameplay_all_upgrades_and_pause_render(self):
        self.start()
        self.game.state.points = 10000
        for name in config.PROP_AREAS:
            while not self.game.state.at_limit(name):
                self.assertTrue(self.game.state.buy(name))
        self.game.step(0.1, [click((400, 380))])
        self.game.draw((400, 380))
        self.game.step(0, [key(pygame.K_p)])
        self.game.draw((-1, -1))
        self.assertTrue(self.game.state.paused)

    def test_key_repeat_does_not_skip_story_or_toggle_pause(self):
        self.game.step(0, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, repeat=True)])
        self.assertEqual(self.game.screen.index, 0)
        self.start()
        self.game.step(0, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p, repeat=True)])
        self.assertFalse(self.game.state.paused)

    def test_focus_pause_can_be_configured(self):
        self.start()
        with patch.object(config, "PAUSE_ON_FOCUS_LOSS", False):
            self.game.step(3, [pygame.event.Event(pygame.WINDOWFOCUSLOST)])
            self.assertEqual(self.game.state.remaining, 237)
            self.assertFalse(self.game.state.paused)

    def test_quit_buttons_work_in_cutscene_and_pause(self):
        self.game.step(0, [click(self.game.screen.quit_button.rect.center)])
        self.assertFalse(self.game.running)
        self.game.running = True
        self.game.start_round()
        self.game.step(0, [key(pygame.K_p)])
        self.game.step(0, [click(self.game.screen.menu["quit"].rect.center)])
        self.assertFalse(self.game.running)

    def test_window_close_is_processed_by_real_loop(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game.run()
        self.assertFalse(self.game.running)

    def test_readable_number_and_time_formatting(self):
        self.assertEqual(points_text(5499.9), "5,499")
        self.assertEqual(time_text(240), "4:00")
        self.assertEqual(time_text(59.1), "1:00")
        self.assertEqual(time_text(60 + 1e-12), "1:00")
        self.assertEqual(time_text(0), "0:00")


if __name__ == "__main__":
    unittest.main()
