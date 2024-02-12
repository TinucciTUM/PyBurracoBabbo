"""
Module: Random AI
Author: Alessandro Tinucci
Version: 1.0
Description: AI logic for the Burraco game.

This module implements the Random AI strategy for playing Burraco.
"""

import random
from pyburraco.players.player import Player


class PlayerRandom(Player):
    def __init__(self):
        # Initialize AI player state
        super().__init__()

    def draw_card(self):
        return True

    def play_melds(self):
        if len(self.hand) < 3:
            return  # Not enough cards to form a meld

        meld = []
        # Ensure the upper bound for the range is valid
        upper_bound = min(len(self.hand), 6)  # Adjust 6 to your game's maximum meld size if needed
        meld_size = random.randint(3, upper_bound)

        for _ in range(meld_size):
            if self.hand:  # Check if there are still cards in the hand
                meld.append(self.hand.pop(random.randint(0, len(self.hand) - 1)))

        if is_valid_meld(meld):
            self.melds.append(meld)
        else:
            # Extend the hand with the cards in meld, not as a nested list
            self.hand.extend(meld)

    def discard_card(self):
        return self.hand.pop(random.randint(0, len(self.hand) - 1))
