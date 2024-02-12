"""
Module: Human Player
Author: Alessandro Tinucci
Version: 1.0
Description: Human logic for the Burraco game.

This module implements the human interface for playing Burraco.
"""
from pyburraco.game_logic.card import Card
from pyburraco.players.player import Player


class PlayerHuman(Player):
    def __init__(self):
        # Initialize AI player state
        super().__init__()

    def draw_card(self, discard_deck) -> bool:
        print(discard_deck)
        while True:
            user_input = input("\nPick from deck [0]\nPick discard pile [1]\n")

            if user_input in ('0', '1'):
                bool_draw = bool(user_input)
                break
            else:
                print("Invalid choice. Please enter 0 or 1.")
        return bool_draw

    def add_card(self, card: Card) -> None:
        pass

    def play_melds(self) -> list:
        pass

    def discard_card(self) -> int:
        pass
