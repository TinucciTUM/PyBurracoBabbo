"""
Module: Player
Author: Alessandro Tinucci
Version: 1.0
Description: Player representation in Burraco.

Defines the base Player class, with basic methods and attributes.
"""


from pyburraco.game_logic.helpers import calculate_meld_points
from pyburraco.game_logic.game import Game


class Player:
    def __init__(self):
        self.name = None
        self.secondary_deck = False
        self.hand = []
        self.melds = []
        self.turn_history = []
        self.score_history = []

        # Used to track progress in the game and train NN
        self.score = 0
        self.turn = 0
        self.round = 0

    def draw_card(self, discard_deck) -> bool:
        # Returns true if picking from deck, false if taking discards pile
        pass

    def play_melds(self) -> list:
        # returns a list of lists containing the melds that i want to play.
        # This is checked outside if they can be played
        pass

    def add_melds(self) -> dict:
        # Returns a dictionary of the cards that i want to play where the key is the card to play and
        # what it contains is a list of the cards in the meld to be added to
        pass

    def discard_card(self) -> int:
        # returns index of the card that it wants to discard from the hand
        pass

    @property
    def points(self):
        return sum(calculate_meld_points(meld.cards) for meld in self.melds) - calculate_meld_points(self.hand)

    @property
    def burraco(self):
        return True if self.melds and max(len(meld.cards) for meld in self.melds) >= 7 \
            else False

    @property
    def score_evaluation(self):
        # This is equal to points per turn
        return self.score / sum(self.turn_history)

    def can_play_card(self, played_cards):
        hand_length = len(self.hand) - played_cards
        return (hand_length > 2
                or (hand_length == 2 and (self.burraco or not self.secondary_deck))
                or (hand_length == 1 and not self.secondary_deck))
