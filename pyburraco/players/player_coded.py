"""
Module: My AI
Author: Alessandro Tinucci
Version: 1.0
Description: AI logic for the Burraco game.

This module implements the AI strategies for playing Burraco, including decision-making algorithms.
"""

import random
from pyburraco.players.player import Player
from .player_coded_helpers import find_best_meld
from pyburraco.game_logic.meld import Meld


class PlayerCoded(Player):
    _id = 0

    def __init__(self):
        # Initialize AI player state
        super().__init__()
        self.name = "AI_" + str(PlayerCoded._id)
        PlayerCoded._id += 1

    def draw_card(self, discard_deck):
        if ((not self.burraco and (len(self.hand) == 1 or len(discard_deck) > 3)) or
                (self.burraco and len(self.hand) == 2) and len(discard_deck) > 1):
            return False
        else:
            return True

    def play_melds(self):
        if len(self.hand) < 3:
            pass  # Not enough cards to form a meld

        # Find the best possible meld based on the current hand
        best_meld = Meld(find_best_meld(self.hand, self.burraco))

        # If a valid meld is found, play it
        if best_meld.cards:
            self.melds.append(best_meld)
            for card in best_meld.cards:
                self.hand.remove(card)
        # Handle the case where no valid meld is found, if necessary

    def add_melds(self):
        cards_to_remove = []
        if ((len(self.hand) > 2) or
                (len(self.hand) == 2 and (not self.secondary_deck or self.burraco))):
            for card in self.hand:
                for meld in self.melds:
                    meld.cards = meld.cards + [card]
                    if meld.valid:
                        cards_to_remove.append(card)
                        break
                    else:
                        meld.cards.remove(card)
                if (((len(self.hand) - len(cards_to_remove)) == 2 and self.secondary_deck and not self.burraco) or
                        (len(self.hand) - len(cards_to_remove) == 1)):
                    break
            # Remove cards from hand after iteration
            for card in cards_to_remove:
                if card in self.hand:
                    self.hand.remove(card)

    def discard_card(self):
        return self.hand.pop(random.randint(0, len(self.hand) - 1))
