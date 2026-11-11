"""Создание, перемешивание и выдача карт из колоды."""

import random

from .card import Card, Rank, Suit


class Deck:
    """Колода из 52 уникальных карт, перемешанная при создании."""

    def __init__(self, rng: random.Random | None = None) -> None:
        """Создать колоду с необязательным генератором для тестов."""
        self._rng = rng if rng is not None else random.Random()
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()

    def __len__(self) -> int:
        """Вернуть число оставшихся карт."""
        return len(self._cards)

    def shuffle(self) -> None:
        """Перемешать оставшиеся карты, не возвращая выданные."""
        self._rng.shuffle(self._cards)

    def draw(self) -> Card:
        """Выдать карту или вызвать IndexError, если колода пуста."""
        if not self._cards:
            raise IndexError("В колоде не осталось карт.")
        return self._cards.pop()
