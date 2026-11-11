"""Проверки номиналов и неизменяемости карт."""

from dataclasses import FrozenInstanceError
import unittest

from src.models import Card, Rank, Suit


class CardTests(unittest.TestCase):
    """Проверяет стоимость и допустимость карт."""

    def test_values_for_all_ranks_and_suits(self):
        expected = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
        for suit in Suit:
            for rank, value in zip(Rank, expected):
                with self.subTest(rank=rank, suit=suit):
                    self.assertEqual(Card(rank, suit).value, value)

    def test_card_is_immutable(self):
        card = Card(Rank.ACE, Suit.SPADES)
        with self.assertRaises(FrozenInstanceError):
            card.rank = Rank.TWO

    def test_invalid_rank_or_suit(self):
        with self.assertRaises(TypeError):
            Card("A", Suit.SPADES)
        with self.assertRaises(TypeError):
            Card(Rank.ACE, "spades")

    def test_display(self):
        self.assertEqual(str(Card(Rank.ACE, Suit.SPADES)), "A♠")
