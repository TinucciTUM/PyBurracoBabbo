"""
Module: Card
Author: Alessandro Tinucci
Version: 1.0
Description: Card representation for Burraco.

This module defines the Card class, used to represent a playing card in Burraco.
"""


class Card:
    def __init__(self, suit, rank):
        """
        Initialize a card with the given suit and rank.
        Jokers have suit and rank both set to 'Joker'.
        """
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        """
        Return the official string representation of the card.
        """
        if self.is_joker():
            return "Joker"
        # return f"{self.rank} of {self.suit}"
        return f"{self.rank}-{self.suit[0]}"

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def is_joker(self):
        """
        Check if the card is a Joker.
        """
        return self.suit == 'Joker' and self.rank == 'Joker'
