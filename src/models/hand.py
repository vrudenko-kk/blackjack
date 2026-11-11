"""Карты участника и подсчёт очков в blackjack."""

from .card import Card, Rank


class Hand:
    """Рука игрока или дилера с автоматическим подсчётом очков."""

    def __init__(self) -> None:
        """Создать пустую руку."""
        self._cards: list[Card] = []

    @property
    def cards(self) -> tuple[Card, ...]:
        """Вернуть неизменяемый снимок карт в порядке получения."""
        return tuple(self._cards)

    def add_card(self, card: Card) -> None:
        """Добавить карту в руку."""
        if not isinstance(card, Card):
            raise TypeError("В руку можно добавить только Card.")
        self._cards.append(card)

    def clear(self) -> None:
        """Убрать все карты перед новым раундом."""
        self._cards.clear()

    @property
    def score(self) -> int:
        """Посчитать очки с учётом стоимости туза 1 или 11."""
        total = sum(card.value for card in self._cards)
        aces = sum(card.rank is Rank.ACE for card in self._cards)
        # Каждый перевод туза с 11 на 1 уменьшает сумму на 10.
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_blackjack(self) -> bool:
        """Проверить наличие 21 очка ровно на двух картах."""
        return len(self._cards) == 2 and self.score == 21

    @property
    def is_bust(self) -> bool:
        """Проверить перебор даже с учётом тузов за 1."""
        return self.score > 21
