"""Проверки правил раунда с заданным порядком выдачи карт."""

import unittest
from unittest.mock import Mock, patch

from src.models import Card, Deck, Game, Rank, RoundPhase, RoundResult, Suit


def start_game(*ranks: Rank) -> tuple[Game, Mock]:
    """Начать раунд с картами в указанном порядке раздачи."""
    suits = tuple(Suit)
    deck = Mock(spec=Deck)
    deck.draw.side_effect = [
        Card(rank, suits[index % len(suits)])
        for index, rank in enumerate(ranks)
    ]
    game = Game()
    with patch("src.models.game.Deck", return_value=deck):
        game.start_round()
    return game, deck


class GameTests(unittest.TestCase):
    """Проверяет раздачу, переходы между ходами и исходы раунда."""

    def test_deal_hides_dealer_card_until_player_stands(self):
        game, _ = start_game(
            Rank.TEN, Rank.ACE, Rank.SIX, Rank.SEVEN, Rank.TWO
        )

        self.assertEqual(game.phase, RoundPhase.PLAYER)
        self.assertIsNone(game.result)
        self.assertEqual(
            [card.rank for card in game.player_cards], [Rank.TEN, Rank.SIX]
        )
        self.assertEqual(game.player_score, 16)
        visible_card = Card(Rank.ACE, Suit.DIAMONDS)
        self.assertEqual(game.dealer_visible_cards, (visible_card,))
        self.assertEqual(game.dealer_visible_score, 11)

        game.hit()
        self.assertEqual(game.phase, RoundPhase.PLAYER)
        self.assertEqual(game.player_score, 18)
        self.assertEqual(game.dealer_visible_cards, (visible_card,))

        game.stand()

        self.assertEqual(game.phase, RoundPhase.DEALER)
        self.assertEqual(
            [card.rank for card in game.dealer_visible_cards],
            [Rank.ACE, Rank.SEVEN],
        )
        self.assertEqual(game.dealer_visible_score, 18)

    def test_initial_blackjacks(self):
        cases = [
            ((Rank.ACE, Rank.NINE, Rank.KING, Rank.SEVEN),
             RoundResult.PLAYER_BLACKJACK),
            ((Rank.NINE, Rank.ACE, Rank.SEVEN, Rank.QUEEN),
             RoundResult.DEALER_BLACKJACK),
            ((Rank.ACE, Rank.ACE, Rank.KING, Rank.TEN), RoundResult.PUSH),
        ]
        for ranks, result in cases:
            with self.subTest(result=result):
                game, deck = start_game(*ranks)
                self.assertEqual(game.phase, RoundPhase.FINISHED)
                self.assertEqual(game.result, result)
                self.assertEqual(len(game.dealer_visible_cards), 2)
                self.assertEqual(deck.draw.call_count, 4)

    def test_player_reaching_21_passes_turn_without_blackjack(self):
        game, _ = start_game(
            Rank.TEN, Rank.NINE, Rank.SIX, Rank.SEVEN, Rank.FIVE, Rank.TWO
        )

        game.hit()
        self.assertEqual(game.player_score, 21)
        self.assertEqual(game.phase, RoundPhase.DEALER)
        self.assertIsNone(game.result)

        game.dealer_step()
        self.assertEqual(game.phase, RoundPhase.FINISHED)
        self.assertEqual(game.result, RoundResult.WIN)

    def test_player_bust_reveals_dealer_cards_without_dealer_draw(self):
        game, deck = start_game(
            Rank.TEN, Rank.NINE, Rank.SIX, Rank.SEVEN, Rank.EIGHT
        )

        game.hit()
        game.dealer_step()

        self.assertEqual(game.player_score, 24)
        self.assertEqual(game.phase, RoundPhase.FINISHED)
        self.assertEqual(game.result, RoundResult.LOSS)
        self.assertEqual(len(game.dealer_visible_cards), 2)
        self.assertEqual(deck.draw.call_count, 5)

    def test_dealer_draws_one_card_per_step_until_reaching_17(self):
        game, deck = start_game(
            Rank.TEN, Rank.TWO, Rank.EIGHT, Rank.THREE, Rank.FOUR, Rank.NINE
        )
        game.stand()

        game.dealer_step()
        self.assertEqual(deck.draw.call_count, 5)
        self.assertEqual(game.dealer_visible_score, 9)
        self.assertEqual(game.phase, RoundPhase.DEALER)

        game.dealer_step()
        self.assertEqual(deck.draw.call_count, 6)
        self.assertEqual(game.dealer_visible_score, 18)
        self.assertEqual(game.phase, RoundPhase.FINISHED)
        self.assertEqual(game.result, RoundResult.PUSH)

    def test_dealer_stands_on_hard_and_soft_17(self):
        for first, second in [(Rank.NINE, Rank.EIGHT), (Rank.ACE, Rank.SIX)]:
            with self.subTest(dealer=(first, second)):
                game, deck = start_game(Rank.TEN, first, Rank.EIGHT, second)
                game.stand()
                game.dealer_step()

                self.assertEqual(game.dealer_visible_score, 17)
                self.assertEqual(game.result, RoundResult.WIN)
                self.assertEqual(deck.draw.call_count, 4)

    def test_dealer_wins_with_higher_score_and_loses_on_bust(self):
        cases = [
            ((Rank.TEN, Rank.KING, Rank.SIX, Rank.EIGHT), RoundResult.LOSS),
            ((Rank.TEN, Rank.KING, Rank.SIX, Rank.SIX, Rank.SEVEN),
             RoundResult.WIN),
        ]
        for ranks, result in cases:
            with self.subTest(result=result):
                game, _ = start_game(*ranks)
                game.stand()
                game.dealer_step()
                self.assertEqual(game.phase, RoundPhase.FINISHED)
                self.assertEqual(game.result, result)

    def test_invalid_actions_do_not_change_active_round(self):
        game = Game()
        game.hit()
        game.stand()
        game.dealer_step()
        self.assertEqual(game.phase, RoundPhase.READY)
        self.assertEqual(game.player_cards, ())
        self.assertEqual(game.dealer_visible_cards, ())

        game, deck = start_game(Rank.TEN, Rank.FOUR, Rank.SIX, Rank.SEVEN)
        player_cards = game.player_cards
        game.start_round()
        game.dealer_step()
        self.assertEqual(game.phase, RoundPhase.PLAYER)

        game.stand()
        game.start_round()
        game.hit()
        game.stand()
        self.assertEqual(game.phase, RoundPhase.DEALER)
        self.assertEqual(game.player_cards, player_cards)
        self.assertEqual(deck.draw.call_count, 4)
        self.assertIsNone(game.result)

    def test_next_round_resets_result_and_uses_new_deck(self):
        game, first_deck = start_game(Rank.ACE, Rank.NINE, Rank.KING, Rank.SIX)
        self.assertEqual(game.result, RoundResult.PLAYER_BLACKJACK)

        second_deck = Mock(spec=Deck)
        new_cards = (
            Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.THREE, Suit.HEARTS), Card(Rank.FOUR, Suit.SPADES),
        )
        second_deck.draw.side_effect = new_cards
        with patch("src.models.game.Deck", return_value=second_deck):
            game.start_round()

        self.assertEqual(game.phase, RoundPhase.PLAYER)
        self.assertIsNone(game.result)
        self.assertEqual(game.player_cards, (new_cards[0], new_cards[2]))
        self.assertEqual(game.dealer_visible_cards, (new_cards[1],))
        self.assertEqual(first_deck.draw.call_count, 4)
        self.assertEqual(second_deck.draw.call_count, 4)
