"""Проверки очков, тузов, blackjack и перебора."""

import unittest

from src.models import Card, Hand, Rank, Suit


class HandTests(unittest.TestCase):
    """Проверяет подсчёт очков независимо от интерфейса."""

    def test_scores(self):
        cases = [
            ([], 0, False, False),
            ([Rank.ACE], 11, False, False),
            ([Rank.ACE, Rank.SEVEN], 18, False, False),
            ([Rank.ACE, Rank.SEVEN, Rank.NINE], 17, False, False),
            ([Rank.ACE, Rank.ACE, Rank.NINE], 21, False, False),
            ([Rank.ACE] * 4, 14, False, False),
            ([Rank.ACE, Rank.ACE, Rank.KING, Rank.QUEEN], 22, False, True),
            ([Rank.TEN, Rank.SIX, Rank.FIVE], 21, False, False),
            ([Rank.KING, Rank.QUEEN, Rank.TWO], 22, False, True),
        ]
        for ranks, score, blackjack, bust in cases:
            with self.subTest(ranks=ranks):
                hand = Hand()
                for rank in ranks:
                    hand.add_card(Card(rank, Suit.HEARTS))
                self.assertEqual(hand.score, score)
                self.assertEqual(hand.is_blackjack, blackjack)
                self.assertEqual(hand.is_bust, bust)

    def test_blackjack_with_every_ten_point_rank(self):
        for rank in (Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING):
            with self.subTest(rank=rank):
                hand = Hand()
                hand.add_card(Card(Rank.ACE, Suit.SPADES))
                hand.add_card(Card(rank, Suit.HEARTS))
                self.assertTrue(hand.is_blackjack)
                self.assertFalse(hand.is_bust)

    def test_score_changes_when_ace_becomes_one(self):
        hand = Hand()
        hand.add_card(Card(Rank.ACE, Suit.SPADES))
        hand.add_card(Card(Rank.SIX, Suit.SPADES))
        self.assertEqual(hand.score, 17)
        hand.add_card(Card(Rank.TEN, Suit.SPADES))
        self.assertEqual(hand.score, 17)

    def test_clear_and_card_snapshot(self):
        hand = Hand()
        card = Card(Rank.TEN, Suit.CLUBS)
        hand.add_card(card)
        snapshot = hand.cards
        self.assertEqual(snapshot, (card,))
        hand.clear()
        self.assertEqual(hand.cards, ())
        self.assertEqual(snapshot, (card,))
        self.assertEqual(hand.score, 0)
        self.assertFalse(hand.is_blackjack)
        self.assertFalse(hand.is_bust)

    def test_invalid_card_does_not_change_hand(self):
        hand = Hand()
        with self.assertRaises(TypeError):
            hand.add_card("A♠")
        self.assertEqual(hand.cards, ())
