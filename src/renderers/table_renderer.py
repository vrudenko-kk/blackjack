"""Отрисовка карт и очков средствами Tkinter Canvas."""

import tkinter as tk
from dataclasses import dataclass

from src.models import Card, Hand, Suit


@dataclass(frozen=True)
class CardFlight:
    """Карта в движении, её рука назначения и доля пройденного пути."""

    card: Card | None
    to_dealer: bool
    progress: float


class TableRenderer:
    """Рисует текущее состояние игры с учётом размера поля."""

    def __init__(self, canvas: tk.Canvas) -> None:
        """Сохранить холст для отрисовки."""
        self.canvas = canvas

    def render(
        self,
        player: tuple[Card | None, ...],
        dealer: tuple[Card | None, ...],
        flight: CardFlight | None = None,
    ) -> None:
        """Нарисовать выложенные карты и текущий кадр движения."""
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 480)
        height = max(self.canvas.winfo_height(), 280)
        dealer_slot = self._hand(
            "Дилер", dealer, 20, width,
            flight is not None and flight.to_dealer,
        )
        player_slot = self._hand(
            "Игрок", player, height / 2 + 10, width,
            flight is not None and not flight.to_dealer,
        )
        deck_x, deck_y = width - 90, height / 2 - 45
        self._card(None, deck_x, deck_y)
        self.canvas.create_text(
            width - 55, height / 2 + 60, text="Колода", fill="white",
            font=("Arial", 11),
        )
        if flight is not None:
            target_x, target_y = (
                dealer_slot if flight.to_dealer else player_slot
            )
            progress = 1 - (1 - flight.progress) ** 2
            self._card(
                flight.card,
                deck_x + (target_x - deck_x) * progress,
                deck_y + (target_y - deck_y) * progress,
            )

    def _hand(
        self, title: str, cards: tuple[Card | None, ...],
        y: float, width: int, incoming: bool,
    ) -> tuple[float, float]:
        """Разместить карты и вернуть координаты следующего места."""
        visible = Hand()
        for card in cards:
            if card is not None:
                visible.add_card(card)
        suffix = " (открытые)" if None in cards else ""
        self.canvas.create_text(
            24, y, anchor="nw", text=f"{title}: {visible.score}{suffix}",
            fill="white", font=("Arial", 15, "bold"),
        )
        count = len(cards) + int(incoming)
        step = min(86, (width - 170) / max(count - 1, 1))
        for index, card in enumerate(cards):
            self._card(card, 24 + index * step, y + 32)
        return 24 + len(cards) * step, y + 32

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
