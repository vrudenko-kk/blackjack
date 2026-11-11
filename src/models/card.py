"""Игральная карта стандартной колоды без джокеров."""

from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    """Четыре масти игральных карт."""

    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"


class Rank(Enum):
    """Тринадцать номиналов игральных карт."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


@dataclass(frozen=True)
class Card:
    """Неизменяемая карта с номиналом и мастью."""

    rank: Rank
    suit: Suit

    def __post_init__(self) -> None:
        """Проверить, что номинал и масть принадлежат колоде."""
        if not isinstance(self.rank, Rank):
            raise TypeError("Номинал должен быть элементом Rank.")
        if not isinstance(self.suit, Suit):
            raise TypeError("Масть должна быть элементом Suit.")

    @property
    def value(self) -> int:
        """Вернуть стоимость карты, считая туза за 11."""
        if self.rank is Rank.ACE:
            return 11
        if self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        return int(self.rank.value)

    def __str__(self) -> str:
        """Вернуть обозначение карты для вывода."""
        return f"{self.rank.value}{self.suit.value}"
