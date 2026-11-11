"""Кнопки действий и сообщение о состоянии раунда."""

from collections.abc import Callable
from tkinter import ttk

from src.models import Game, RoundPhase, RoundResult


class Controls(ttk.Frame):
    """Панель управления с доступностью кнопок по состоянию игры."""

    def __init__(
        self, parent: ttk.Frame, on_start: Callable[[], None],
        on_hit: Callable[[], None], on_stand: Callable[[], None],
    ) -> None:
        """Создать кнопки и подпись состояния."""
        super().__init__(parent, padding=(0, 12, 0, 0))
        self.start = ttk.Button(self, text="Новый раунд", command=on_start)
        self.hit = ttk.Button(self, text="Взять карту", command=on_hit)
        self.stand = ttk.Button(self, text="Остановиться", command=on_stand)
        for column, button in enumerate((self.start, self.hit, self.stand)):
            button.grid(row=0, column=column, padx=4, sticky="ew")
            self.columnconfigure(column, weight=1)
        self.status = ttk.Label(self, anchor="center")
        self.status.grid(row=1, column=0, columnspan=3, pady=(10, 0))

    def update_state(
        self, game: Game, animation_message: str | None = None,
    ) -> None:
        """Обновить доступность действий и сообщение игроку."""
        if animation_message is not None:
            for button in (self.start, self.hit, self.stand):
                button.state(["disabled"])
            self.status.configure(text=animation_message)
            return

        player_turn = game.phase is RoundPhase.PLAYER
        can_start = game.phase in (RoundPhase.READY, RoundPhase.FINISHED)
        self.start.state(["!disabled" if can_start else "disabled"])
        for button in (self.hit, self.stand):
            button.state(["!disabled" if player_turn else "disabled"])
        messages = {
            RoundPhase.READY: "Нажмите «Новый раунд», чтобы начать",
            RoundPhase.PLAYER: "Ваш ход",
            RoundPhase.DEALER: "Ход дилера",
            RoundPhase.FINISHED: "Раунд завершён",
        }
        results = {
            RoundResult.WIN: "Вы победили!",
            RoundResult.LOSS: "Победил дилер",
            RoundResult.PUSH: "Ничья",
            RoundResult.PLAYER_BLACKJACK: "Blackjack! Вы победили!",
            RoundResult.DEALER_BLACKJACK: "У дилера blackjack",
        }
        self.status.configure(
            text=results.get(game.result, messages[game.phase]),
        )
