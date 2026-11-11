"""Главное окно приложения Blackjack."""

import tkinter as tk
from tkinter import ttk

from src.models import Game, RoundPhase
from src.renderers.table_renderer import TableRenderer
from src.widgets.controls import Controls


class App:
    """Связывает модель раунда, игровой стол и кнопки действий."""

    def __init__(self, root: tk.Tk) -> None:
        """Настроить окно и разместить игровое поле."""
        root.title("Blackjack")
        root.minsize(560, 440)
        self.game = Game()

        content = ttk.Frame(root, padding=16)
        content.pack(fill="both", expand=True)
        self.table = tk.Canvas(
            content, width=720, height=400, background="#17543a",
            highlightthickness=0,
        )
        self.table.pack(fill="both", expand=True)
        self.renderer = TableRenderer(self.table)
        self.controls = Controls(
            content, self.start_round, self.hit, self.stand,
        )
        self.controls.pack(fill="x")
        self.table.bind("<Configure>", lambda event: self._refresh())
        self._refresh()

    def start_round(self) -> None:
        """Начать раунд и отобразить начальную раздачу."""
        self.game.start_round()
        self._refresh()

    def hit(self) -> None:
        """Выдать карту игроку и при необходимости выполнить ход дилера."""
        self.game.hit()
        self._finish_dealer_turn()
        self._refresh()

    def stand(self) -> None:
        """Завершить ход игрока и выполнить ход дилера."""
        self.game.stand()
        self._finish_dealer_turn()
        self._refresh()

    def _finish_dealer_turn(self) -> None:
        """Выполнить шаги дилера до завершения раунда."""
        while self.game.phase is RoundPhase.DEALER:
            self.game.dealer_step()

    def _refresh(self) -> None:
        """Обновить стол и панель управления."""
        self.renderer.render(self.game)
        self.controls.update_state(self.game)
