"""Правила и состояния раунда blackjack."""

from enum import Enum, auto
from random import Random

from .card import Card
from .deck import Deck
from .hand import Hand


class RoundPhase(Enum):
    """Состояния раунда, доступные интерфейсу."""

    READY = auto()
    PLAYER = auto()
    DEALER = auto()
    FINISHED = auto()


class RoundResult(Enum):
    """Результаты раунда с точки зрения игрока."""

    WIN = auto()
    LOSS = auto()
    PUSH = auto()
    PLAYER_BLACKJACK = auto()
    DEALER_BLACKJACK = auto()


class Game:
    """Управляет раздачей, ходами и результатом раунда."""

    def __init__(self, rng: Random | None = None) -> None:
        """Подготовить игру с необязательным генератором для колод."""
        self._rng = rng
        self._deck: Deck
        self._player = Hand()
        self._dealer = Hand()
        self._phase = RoundPhase.READY
        self._result: RoundResult | None = None

    @property
    def phase(self) -> RoundPhase:
        """Вернуть текущее состояние раунда."""
        return self._phase

    @property
    def result(self) -> RoundResult | None:
        """Вернуть результат завершённого раунда."""
        return self._result

    @property
    def player_cards(self) -> tuple[Card, ...]:
        """Вернуть карты игрока в порядке раздачи."""
        return self._player.cards

    @property
    def dealer_visible_cards(self) -> tuple[Card, ...]:
        """Вернуть только открытые карты дилера."""
        if self._phase is RoundPhase.PLAYER:
            return self._dealer.cards[:1]
        return self._dealer.cards

    @property
    def player_score(self) -> int:
        """Вернуть очки игрока."""
        return self._player.score

    @property
    def dealer_visible_score(self) -> int:
        """Вернуть очки по открытым картам дилера."""
        if self._phase is RoundPhase.PLAYER:
            return self._dealer.cards[0].value
        return self._dealer.score

    def start_round(self) -> None:
        """Раздать начальные карты, если нет активного раунда."""
        if self._phase in (RoundPhase.PLAYER, RoundPhase.DEALER):
            return

        self._deck = Deck(self._rng)
        self._player.clear()
        self._dealer.clear()
        self._result = None
        for _ in range(2):
            self._player.add_card(self._deck.draw())
            self._dealer.add_card(self._deck.draw())

        player_blackjack = self._player.is_blackjack
        dealer_blackjack = self._dealer.is_blackjack
        if player_blackjack and dealer_blackjack:
            self._finish(RoundResult.PUSH)
        elif player_blackjack:
            self._finish(RoundResult.PLAYER_BLACKJACK)
        elif dealer_blackjack:
            self._finish(RoundResult.DEALER_BLACKJACK)
        else:
            self._phase = RoundPhase.PLAYER

    def hit(self) -> None:
        """Выдать карту на ходу игрока и проверить его очки."""
        if self._phase is not RoundPhase.PLAYER:
            return

        self._player.add_card(self._deck.draw())
        if self._player.is_bust:
            self._finish(RoundResult.LOSS)
        elif self._player.score == 21:
            self.stand()

    def stand(self) -> None:
        """Передать ход дилеру и раскрыть его вторую карту."""
        if self._phase is RoundPhase.PLAYER:
            self._phase = RoundPhase.DEALER

    def dealer_step(self) -> None:
        """Взять до одной карты и завершить раунд при остановке дилера."""
        if self._phase is not RoundPhase.DEALER:
            return

        dealer_score = self._dealer.score
        if dealer_score < 17:
            self._dealer.add_card(self._deck.draw())
            dealer_score = self._dealer.score

        if dealer_score < 17:
            return

        player_score = self._player.score
        if self._dealer.is_bust or player_score > dealer_score:
            self._finish(RoundResult.WIN)
        elif player_score < dealer_score:
            self._finish(RoundResult.LOSS)
        else:
            self._finish(RoundResult.PUSH)

    def _finish(self, result: RoundResult) -> None:
        """Сохранить результат и завершить раунд."""
        self._result = result
        self._phase = RoundPhase.FINISHED
