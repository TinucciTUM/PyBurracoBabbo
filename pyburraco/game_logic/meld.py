"""
Module: Meld
Author: Alessandro Tinucci
Version: 1.0
Description: Meld management for Burraco.

This module provides functionalities for creating and managing a deck of cards.
"""

from .card import Card
from .helpers import all_same_rank, all_same_suit, is_consecutive_run, card_rank_difference

RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


class Meld:
    def __init__(self, cards=None):
        self._valid = False
        self._meld_type = None
        self._regular_cards = None
        self._wildcards = None
        if cards is None:
            self._cards = []
        self.cards = cards

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, new_cards):
        if new_cards is not None:
            self._cards = new_cards
            self._update_meld_properties()

    @property
    def meld_type(self):
        return self._meld_type

    @property
    def wildcards(self):
        return self._wildcards

    @property
    def regular_cards(self):
        return self._regular_cards

    @property
    def valid(self):
        return self._valid

    def _update_meld_properties(self):
        # TODO - speedup possible by not recalculating wildcards and regular cards
        wildcards = [card for card in self._cards if card.rank in ['2', 'Joker']]
        self._wildcards = wildcards.copy()

        regular_cards = sorted([card for card in self._cards if card.rank not in ['2', 'Joker']],
                               key=lambda card: RANK_ORDER.index(card.rank))
        self._regular_cards = regular_cards.copy()

        if not self._cards or len(self._cards) < 3 or len(wildcards) > 1:
            self._meld_type = None
            self._valid = False

        else:
            if all_same_rank(regular_cards):
                self._meld_type = 'Set'
                self._cards = regular_cards + wildcards
                self._valid = True

            elif all_same_suit(regular_cards) and is_consecutive_run(regular_cards, wildcards):
                ordered_cards = [regular_cards[0]]
                for i in range(1, len(regular_cards)):
                    if card_rank_difference(regular_cards[i], regular_cards[i - 1]) == 1:
                        ordered_cards.append(regular_cards[i])
                    else:
                        ordered_cards.append(wildcards.pop())
                        ordered_cards.append(regular_cards[i])
                if wildcards:
                    ordered_cards.append(wildcards.pop())
                self._cards = ordered_cards

                self._meld_type = 'Run'
                self._valid = True
            else:
                self._meld_type = None
                self._valid = False

    def __str__(self):
        return f"Meld Type: {self._meld_type}, Cards: {self._cards}"

    def __repr__(self):
        return f"Meld Type: {self._meld_type}, Cards: {self._cards}"

    def __eq__(self, other):
        regular_cards = sorted([card for card in self._cards if card.rank not in ['2', 'Joker']],
                               key=lambda card: RANK_ORDER.index(card.rank))
        regular_cards.append([card for card in self._cards if card.rank in ['2', 'Joker']])

        regular_cards_other = sorted([card for card in other.cards if card.rank not in ['2', 'Joker']],
                                     key=lambda card: RANK_ORDER.index(card.rank))
        regular_cards_other.append([card for card in other.cards if card.rank in ['2', 'Joker']])

        return regular_cards == regular_cards_other
