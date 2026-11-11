"""Проверки интерфейса, требующие графической среды Tkinter."""

import tkinter as tk
import unittest
from random import Random
from time import monotonic, sleep
from unittest.mock import patch

from src.app import App
from src.models import Game, RoundPhase, RoundResult


class AppTests(unittest.TestCase):
    """Проверяет учёт результатов и действия во время анимации."""

    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Нет графической среды: {error}")
        self.addCleanup(self.root.destroy)
        self.app = App(self.root)
        self.app.game = Game(Random(42))
        self.root.update()
        for name, value in (
            ("CARD_FLIGHT_SECONDS", 0.001),
            ("FRAME_INTERVAL_MS", 1),
            ("DEALER_PAUSE_MS", 1),
        ):
            patcher = patch(f"src.app.{name}", value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def settle(self):
        deadline = monotonic() + 3
        while self.app._animation_message is not None:
            self.root.update()
            self.assertLess(monotonic(), deadline, "Анимация не завершилась")
            sleep(0.002)

    def test_statistics_count_each_round_once(self):
        expected = [0, 0, 0]
        for _ in range(40):
            self.app.start_round()
            self.settle()
            if self.app.game.phase is RoundPhase.PLAYER:
                self.app.hit()
                self.settle()
                self.app.stand()
                self.settle()
            result = self.app.game.result
            if result in (RoundResult.WIN, RoundResult.PLAYER_BLACKJACK):
                expected[0] += 1
            elif result is RoundResult.PUSH:
                expected[2] += 1
            else:
                expected[1] += 1
            self.app._advance_round()
            self.app._refresh()
            self.assertEqual(
                [self.app.wins, self.app.losses, self.app.pushes], expected,
            )
        self.app.reset_statistics()
        self.app._advance_round()
        self.assertEqual(self.app.wins + self.app.losses + self.app.pushes, 0)

    def test_reset_during_deal_and_repeated_actions(self):
        self.app.start_round()
        cards = self.app.game.player_cards
        self.app.hit()
        self.app.stand()
        self.app.start_round()
        self.assertEqual(self.app.game.player_cards, cards)
        self.assertTrue(self.app.controls.hit.instate(["disabled"]))
        self.app.reset_statistics()
        self.settle()
        self.app.stand()
        self.settle()
        self.assertEqual(self.app.wins + self.app.losses + self.app.pushes, 1)

    def test_rules_and_shortcuts(self):
        with patch("src.app.messagebox.showinfo") as show:
            self.app.show_rules()
            show.assert_called_once()
        for key in ("n", "N", "h", "H", "s", "S", "F1"):
            self.assertTrue(self.root.bind(f"<KeyPress-{key}>"))
