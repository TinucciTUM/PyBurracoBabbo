"""
Module: Main
Author: Alessandro Tinucci
Version: 1.0
Description: Main Script to run PyBurraco.
"""

import sys
sys.path.append('/home/alessandro/Documents/Projects/Python/PyBurraco')  # Adjust the path accordingly

import numpy as np
import os

from pyburraco import Game
from pyburraco.players import PlayerCoded, PlayerNN, PlayerHuman
from pyburraco.genetic_algorithm import GeneticAlgorithm
from utils.plotter import plot_evolution


def test_model_match(ai_type="coded"):
    # Create game instance
    game = Game(save_stats=True, log=True)

    models_path = os.path.join(os.getcwd(), 'data', 'models')
    file_list = [f for f in os.listdir(models_path) if os.path.isfile(os.path.join(models_path, f))]

    # Create Players
    ai_0 = PlayerNN()
    if len(file_list) > 0:
        ai_0.load_model(os.path.join(models_path, file_list[0]))

    if ai_type == "human":
        ai_1 = PlayerHuman()
    elif ai_type == "nn":
        ai_1 = PlayerNN()
        ai_0.load_model(os.path.join(models_path, file_list[0]))
    else:
        ai_1 = PlayerCoded()

    # Add players
    game.add_player(ai_0)
    game.add_player(ai_1)

    # Start the game loop
    for _ in range(100):
        game.play_game()

    print(np.average([np.average(turns) for turns in game.stats.data['turns'][:-1]]))
    print(np.average(ai_0.score_history))
    print(np.average(ai_1.score_history))
    game.stats.plot_game_turns()


def play_game_against_nn():
    models_path = os.path.join(os.getcwd(), 'data', 'models')
    file_list = [f for f in os.listdir(models_path) if os.path.isfile(os.path.join(models_path, f))]

    game = Game(save_stats=True, log=True)

    ai_0 = PlayerHuman()
    ai_1 = PlayerNN()
    ai_1.load_model(os.path.join(models_path, file_list[0]))

    game.add_player(ai_0)
    game.add_player(ai_1)

    game.play_game()
    print(np.average(ai_1.score_history))
    print(np.average(ai_1.score_history))


if __name__ == "__main__":
    # TODO - n_games is not doing nothing now
    parameters = {
        'n_players': 100,
        'n_games': 1,
        'generations': 1000,
        'continue_training': True,
        'n_processors': 16,
        'propagate_percentage': 0.1,
        'mutation_probability': 0.03,
        'mutation_scale': 0.2
    }
    ga = GeneticAlgorithm(parameters)
    ga.evolve_generations()

    # test_model_match(ai_type='coded')

    # plot_evolution(save_plot=True)
