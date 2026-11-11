"""Проверки состава колоды и выдачи без повторений."""

import random
import unittest

from src.models import Card, Deck, Rank, Suit


class DeckTests(unittest.TestCase):
    """Проверяет полный жизненный цикл колоды."""

    def test_draw_all_cards_and_exhaust_deck(self):
        deck = Deck()
        self.assertEqual(len(deck), 52)
        cards = []
        for remaining in range(51, -1, -1):
            cards.append(deck.draw())
            self.assertEqual(len(deck), remaining)
        expected = {Card(rank, suit) for rank in Rank for suit in Suit}
        self.assertEqual(set(cards), expected)
        with self.assertRaises(IndexError):
            deck.draw()
        self.assertEqual(len(deck), 0)

    def test_shuffle_preserves_only_remaining_cards(self):
        deck = Deck()
        drawn = {deck.draw() for _ in range(10)}
        deck.shuffle()
        remaining = {deck.draw() for _ in range(len(deck))}
        self.assertEqual(len(remaining), 42)
        self.assertTrue(drawn.isdisjoint(remaining))

    def test_shuffle_is_reproducible_with_seed(self):
        first = Deck(random.Random(42))
        second = Deck(random.Random(42))
        actual = [first.draw() for _ in range(52)]
        self.assertEqual(actual, [second.draw() for _ in range(52)])
        ordered = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.assertNotEqual(actual, list(reversed(ordered)))
