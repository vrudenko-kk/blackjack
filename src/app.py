"""Главное окно приложения Blackjack."""

import tkinter as tk
from collections.abc import Callable
from time import monotonic
from tkinter import messagebox, ttk

from src.models import Card, Game, RoundPhase, RoundResult
from src.renderers.table_renderer import CardFlight, TableRenderer
from src.widgets.controls import Controls


CARD_FLIGHT_SECONDS = 0.25
FRAME_INTERVAL_MS = 16
DEALER_PAUSE_MS = 350


class App:
    """Связывает модель раунда, игровой стол и кнопки действий."""

    def __init__(self, root: tk.Tk) -> None:
        """Настроить окно и разместить игровое поле."""
        root.title("Blackjack")
        root.minsize(560, 500)
        self.root = root
        self.game = Game()
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self._result_counted = False
        self._player_cards: tuple[Card | None, ...] = ()
        self._dealer_cards: tuple[Card | None, ...] = ()
        self._flight: CardFlight | None = None
        self._animation_message: str | None = None
        self._timer: str | None = None

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
            self.reset_statistics, self.show_rules,
        )
        self.controls.pack(fill="x")
        self.table.bind("<Configure>", lambda event: self._render())
        root.bind("<Destroy>", self._cancel_timer, add="+")
        for key in ("n", "N"):
            root.bind(f"<KeyPress-{key}>", lambda event: self.start_round())
        for key in ("h", "H"):
            root.bind(f"<KeyPress-{key}>", lambda event: self.hit())
        for key in ("s", "S"):
            root.bind(f"<KeyPress-{key}>", lambda event: self.stand())
        root.bind("<F1>", lambda event: self.show_rules())
        self._refresh()

    def reset_statistics(self) -> None:
        """Обнулить счётчики, сохранив учёт текущего раунда."""
        self.wins = self.losses = self.pushes = 0
        self._refresh()

    def show_rules(self) -> None:
        """Показать правила принятого варианта blackjack."""
        messagebox.showinfo(
            "Правила Blackjack",
            "Наберите больше очков, чем дилер, не превышая 21.\n\n"
            "Карты 2–10 стоят по номиналу, J/Q/K — 10, туз — 11 или 1.\n"
            "Blackjack — 21 на первых двух картах. Он побеждает обычные 21.\n"
            "Blackjack у обоих участников означает ничью.\n\n"
            "H — взять карту, S — остановиться, N — новый раунд.\n"
            "При 21 ход автоматически переходит к дилеру.\n"
            "Перебор игрока сразу завершает раунд поражением.\n"
            "Дилер берёт до 17 и останавливается на мягких 17.\n"
            "Равные суммы дают ничью. Ставки и разделение пар отсутствуют.\n\n"
            "Статистика хранится до закрытия окна или её сброса.",
            parent=self.root,
        )

    def start_round(self) -> None:
        """Начать раунд и по очереди раздать четыре карты."""
        if (
            self._animation_message is not None
            or self.game.phase not in (RoundPhase.READY, RoundPhase.FINISHED)
        ):
            return

        self.game.start_round()
        self._result_counted = False
        self._player_cards = ()
        self._dealer_cards = ()
        self._animation_message = "Раздача карт…"
        opening = (
            (self.game.player_cards[0], False),
            (self.game.dealer_visible_cards[0], True),
            (self.game.player_cards[1], False),
            (None, True),
        )

        def deal_next(index: int) -> None:
            if index == len(opening):
                self._advance_round()
                return
            card, to_dealer = opening[index]
            self._animate_card(card, to_dealer, lambda: deal_next(index + 1))

        self._refresh()
        deal_next(0)

    def hit(self) -> None:
        """Выдать и показать карту игрока."""
        if (
            self._animation_message is not None
            or self.game.phase is not RoundPhase.PLAYER
        ):
            return

        self.game.hit()
        self._animation_message = "Карта игроку…"
        self._refresh()
        self._animate_card(
            self.game.player_cards[-1], False, self._advance_round,
        )

    def stand(self) -> None:
        """Завершить ход игрока и показать открытую карту дилера."""
        if (
            self._animation_message is not None
            or self.game.phase is not RoundPhase.PLAYER
        ):
            return

        self.game.stand()
        self._advance_round()

    def _advance_round(self) -> None:
        """Показать состояние модели и запланировать следующий шаг дилера."""
        self._player_cards = self.game.player_cards
        self._dealer_cards = self.game.dealer_visible_cards
        if self.game.phase is RoundPhase.PLAYER:
            self._dealer_cards += (None,)

        if (
            self.game.phase is RoundPhase.FINISHED
            and not self._result_counted
        ):
            if self.game.result in (RoundResult.WIN, RoundResult.PLAYER_BLACKJACK):
                self.wins += 1
            elif self.game.result is RoundResult.PUSH:
                self.pushes += 1
            else:
                self.losses += 1
            self._result_counted = True

        self._animation_message = None
        if self.game.phase is RoundPhase.DEALER:
            self._animation_message = "Ход дилера"
            self._schedule(DEALER_PAUSE_MS, self._dealer_step)
        self._refresh()

    def _dealer_step(self) -> None:
        """Выполнить один шаг дилера и показать полученную карту."""
        self.game.dealer_step()
        cards = self.game.dealer_visible_cards
        if len(cards) > len(self._dealer_cards):
            self._animate_card(cards[-1], True, self._advance_round)
        else:
            self._advance_round()

    def _animate_card(
        self,
        card: Card | None,
        to_dealer: bool,
        on_complete: Callable[[], None],
    ) -> None:
        """Переместить карту от колоды к руке и продолжить раунд."""
        started = monotonic()

        def frame() -> None:
            progress = (monotonic() - started) / CARD_FLIGHT_SECONDS
            if progress < 1:
                self._flight = CardFlight(card, to_dealer, progress)
                self._render()
                self._schedule(FRAME_INTERVAL_MS, frame)
                return

            self._flight = None
            if to_dealer:
                self._dealer_cards += (card,)
            else:
                self._player_cards += (card,)
            on_complete()

        frame()

    def _schedule(self, delay: int, action: Callable[[], None]) -> None:
        """Запланировать следующий кадр или шаг раунда."""
        def run() -> None:
            self._timer = None
            action()

        self._timer = self.root.after(delay, run)

    def _cancel_timer(self, event: tk.Event) -> None:
        """Отменить запланированное действие при закрытии окна."""
        if event.widget is self.root and self._timer is not None:
            self.root.after_cancel(self._timer)
            self._timer = None

    def _render(self) -> None:
        """Перерисовать карты с учётом текущего размера стола."""
        self.renderer.render(
            self._player_cards, self._dealer_cards, self._flight,
        )

    def _refresh(self) -> None:
        """Обновить стол и панель управления."""
        self._render()
        self.controls.update_state(self.game, self._animation_message)
        self.controls.statistics.configure(
            text=f"Победы: {self.wins}   Поражения: {self.losses}   "
                 f"Ничьи: {self.pushes}",
        )
