"""Отрисовка карт и очков средствами Tkinter Canvas."""

import tkinter as tk

from src.models import Card, Game, RoundPhase, Suit


class TableRenderer:
    """Рисует текущее состояние игры с учётом размера поля."""

    def __init__(self, canvas: tk.Canvas) -> None:
        """Сохранить холст для отрисовки."""
        self.canvas = canvas

    def render(self, game: Game) -> None:
        """Перерисовать стол, показывая только доступные игроку карты."""
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 480)
        height = max(self.canvas.winfo_height(), 280)
        self._hand(
            "Дилер", game.dealer_visible_cards, game.dealer_visible_score,
            20, width, game.phase is RoundPhase.PLAYER,
        )
        self._hand(
            "Игрок", game.player_cards, game.player_score,
            height / 2 + 10, width,
        )
        self._card(None, width - 90, height / 2 - 45)
        self.canvas.create_text(
            width - 55, height / 2 + 60, text="Колода", fill="white",
            font=("Arial", 11),
        )

    def _hand(
        self, title: str, cards: tuple[Card, ...], score: int,
        y: float, width: int, hidden: bool = False,
    ) -> None:
        """Разместить руку, уменьшая шаг между картами при необходимости."""
        suffix = " (открытые)" if hidden else ""
        self.canvas.create_text(
            24, y, anchor="nw", text=f"{title}: {score}{suffix}",
            fill="white", font=("Arial", 15, "bold"),
        )
        count = len(cards) + int(hidden)
        step = min(86, (width - 170) / max(count - 1, 1))
        for index, card in enumerate(cards):
            self._card(card, 24 + index * step, y + 32)
        if hidden:
            self._card(None, 24 + len(cards) * step, y + 32)

    def _card(self, card: Card | None, x: float, y: float) -> None:
        """Нарисовать лицевую сторону карты или рубашку."""
        self.canvas.create_rectangle(
            x, y, x + 70, y + 96, fill="#fffaf0" if card else "#234c80",
            outline="#d4cfbd", width=2,
        )
        if card is None:
            self.canvas.create_rectangle(
                x + 7, y + 7, x + 63, y + 89, outline="#91b2dd", width=2,
            )
            self.canvas.create_text(
                x + 35, y + 48, text="◆", fill="#d6e4fa",
                font=("Arial", 24),
            )
            return
        color = "#bb283b" if card.suit in (
            Suit.HEARTS, Suit.DIAMONDS
        ) else "#202830"
        self.canvas.create_text(
            x + 6, y + 6, anchor="nw", text=str(card), fill=color,
            font=("Arial", 13, "bold"),
        )
        self.canvas.create_text(
            x + 35, y + 58, text=card.suit.value, fill=color,
            font=("Arial", 26),
        )
