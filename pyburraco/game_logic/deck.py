"""
Module: Deck
Author: Alessandro Tinucci
Version: 1.0
Description: Deck management for Burraco.

This module provides functionalities for creating, shuffling, and managing a deck of cards.
"""


from .card import Card
import random


class Deck:
    def __init__(self):
        """
        Initialize the Deck with two sets of standard playing cards and four Jokers.

        The deck consists of two complete sets of cards (each set has 52 cards)
        and four Jokers, making a total of 108 cards.
        """
        self.draw_pile = [Card(suit, rank) for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]
                      for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]] * 2

        self.draw_pile.extend([Card('Joker', 'Joker') for _ in range(4)])
        self.shuffle()

        self.discard_pile = []

    def shuffle(self):
        """
        Shuffle the deck of cards.

        This method randomizes the order of the cards in the deck.
        """
        random.shuffle(self.draw_pile)

    def draw_card(self):
        """
        Draw the top card from the draw pile.

        Returns:
            Card: The top card from the draw pile. If the draw pile is empty, reshuffle the discard pile.
        """
        if self.draw_empty():
            self.reshuffle_discard_pile()
        return self.draw_pile.pop() if self.draw_pile else None

    def draw_discard_pile(self):
        """
        Draw the discard pile.
        """
        draw_cards = [card for card in self.discard_pile]
        return draw_cards if self.discard_pile else None

    def discard_card(self, card):
        """
        Add a card to the discard pile.

        Args:
            card (Card): The card to be added to the discard pile.
        """
        self.discard_pile.append(card)

    def reshuffle_discard_pile(self):
        """
        Reshuffle the discard pile back into the draw pile.
        """
        self.draw_pile = self.discard_pile
        self.discard_pile = []
        self.shuffle()

    def draw_empty(self):
        """
        Check if the draw pile is empty.

        Returns:
            bool: True if the draw pile is empty, False otherwise.
        """
        return len(self.draw_pile) == 0

    def discard_empty(self):
        """
        Check if the discard pile is empty.

        Returns:
            bool: True if the discard pile is empty, False otherwise.
        """
        return len(self.discard_pile) == 0
