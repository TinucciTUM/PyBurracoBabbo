"""
Module: Game Analytics
Author: Alessandro Tinucci
Version: 1.0
Description: Analytics management for Burraco.

This module provides functionalities for managing the stats of the game.
"""

import matplotlib.pyplot as plt
import numpy as np


class GameAnalytics:
    def __init__(self, save_data=False):
        self._save_data = save_data
        self.data = dict()
        self.data['turns'] = [[]]
        self.data['rounds'] = []

    def add_turn(self, turns):
        if self._save_data:
            self.data['turns'][-1].append(turns)

    def add_round(self, rounds):
        if self._save_data:
            self.data['rounds'].append(rounds)
            self.data['turns'].append([])

    def plot_game_turns(self):
        if not self._save_data:
            print("No data to plot. Enable data saving to use this feature.")
            return

        turn_averages = [np.average(turns) for turns in self.data['turns'][:-1]]

        plt.figure()
        plt.plot(turn_averages, marker='o', linestyle='-')
        plt.plot(self.data['rounds'], marker='o', linestyle='-')
        plt.xlabel("Game")
        plt.ylabel("Number of Turns")
        plt.title("Number of Turns per round")
        plt.grid(True)
        plt.show()

