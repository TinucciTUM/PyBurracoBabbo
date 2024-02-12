"""
Module: Burraco NN Player
Author: Alessandro Tinucci
Version: 1.0
Description: ML Player for the game Burraco.

This module implements the ML interface for playing Burraco.
"""

import sys
import numpy as np
import random
import os
import time
import concurrent.futures
import multiprocessing
import pickle

from pyburraco import Game
from pyburraco.players import PlayerNN

SWISS_ROUNDS = 10


def play_2p_match(pair):
    player1, player2 = pair

    game = Game(save_stats=False, log=False)
    game.add_player(player1)
    game.add_player(player2)
    game.play_game()

    # TODO - Check if this is really necessary
    out_dict = dict()
    out_dict['winner'] = game.winner.name
    out_dict['score1'] = player1.score_history
    out_dict['score2'] = player2.score_history

    return out_dict


def crossover(parent1, parent2):
    """
    Perform crossover between two parent models
    """
    child_model = PlayerNN()

    for param_name, param in child_model.model.named_parameters():
        if random.random() < 0.5:  # 50% chance to inherit from each parent
            param.data.copy_(parent1.model.state_dict()[param_name])
        else:
            param.data.copy_(parent2.model.state_dict()[param_name])
    return child_model


def print_progress_bar(iteration, total, length=80):
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)

    # Add color codes for a more modern look
    color_start = '\033[32m'  # Green color
    color_end = '\033[0m'  # Reset color to default

    # Add some styling to the output using an f-string
    border = '─' * 3
    print(f'\r ╰{border} Swiss Round Progress: |{color_start}{bar}{color_end}| {percent}% Complete',
          end='', flush=True)

    if iteration == total:
        print('\r \n', flush=True)


class GeneticAlgorithm:
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}
        self._name = str(parameters.get('name', 'Test'))
        self._n_processors = int(parameters.get('n_processors', 1))
        self._n_players = int(parameters.get('n_players', 2))
        self._n_games = int(parameters.get('n_games', 1))
        self._generations = int(parameters.get('generations', 5))
        self._continue_training = bool(parameters.get('continue_training', True))
        self._tournament_type = str(parameters.get('tournament_type', 'swiss'))
        self._propagate_percentage = float(parameters.get('propagate_percentage', 0.1))
        self._mutation_probability = float(parameters.get('mutation_probability', 0.01))
        self._mutation_scale = float(parameters.get('mutation_scale', 0.1))

        if self._tournament_type == "swiss":
            self._swiss_rounds = SWISS_ROUNDS

        self._data_path = os.path.join(os.getcwd(), 'data')
        self._models_path = os.path.join(self._data_path, 'models')
        self._players = []
        self._generation_scores = []
        self._time_steps = []

        self._setup_simulation()

    def run_generation(self):
        # TODO - change this swiss ruleset to dutch-swiss tournament style
        if self._tournament_type == "swiss":
            swiss_points = dict()
            for player in self._players:
                swiss_points[player.name] = 0

            multiprocessing.set_start_method('spawn', force=True)
            for iteration in range(self._swiss_rounds):
                print_progress_bar(iteration=iteration, total=self._swiss_rounds)

                with concurrent.futures.ProcessPoolExecutor(max_workers=self._n_processors) as executor:

                    player_pairs = [(self._players[i], self._players[i + 1]) for i in range(0, self._n_players, 2)]
                    parallel_output = list(executor.map(play_2p_match, player_pairs))

                winners = [output['winner'] for output in parallel_output]
                for i, player in enumerate(self._players):
                    if i % 2 == 0:
                        player.score_history.append(parallel_output[int(np.ceil((i - 1) / 2))]['score1'][-1])
                    else:
                        player.score_history.append(parallel_output[int(np.ceil((i - 1) / 2))]['score2'][-1])

                for winner in winners:
                    swiss_points[winner] += 1

                self._players = sorted(self._players, key=lambda p: (swiss_points[p.name],
                                                                     np.mean(p.score_history)), reverse=True)

        elif self._tournament_type == "round_robin":
            for i in range(self._n_players - 1):
                for j in range(self._n_players - i - 1):
                    game = Game(save_stats=False, log=False)
                    game.add_player(self._players[i])
                    game.add_player(self._players[i + j + 1])

                    for _ in range(self._n_games):
                        game.play_game()
            self._players = sorted(self._players, key=lambda p: np.mean(p.score_history), reverse=True)

        self._generation_scores.append([np.mean(player.score_history) for player in self._players])

        for player in self._players:
            player.score_history = []

    def _setup_simulation(self):
        """
        Sets up self._n_players and self._players and load file
        """

        if not os.path.exists(self._models_path):
            os.mkdir(self._models_path)
        file_list = [f for f in os.listdir(self._models_path) if os.path.isfile(os.path.join(self._models_path, f))]

        if self._continue_training:
            self._players = []
            self._n_players = max(int(np.floor(len(file_list) / self._propagate_percentage)), self._n_players)
            if self._tournament_type == "swiss":
                self._n_players = self._n_players if self._n_players % 2 == 0 else self._n_players + 1
            for file in file_list:
                load_player = PlayerNN()
                load_player.load_model(os.path.join(self._models_path, file))
                self._players.append(load_player)

            # Fill the rest with child
            self.create_child_model(self._n_players - len(file_list))
            self._load_status()

        else:
            if len(file_list) > 0:
                user_inp = input("Are you sure you want to delete the saved models? (y/n) ")
                if user_inp.lower() not in ['y', 'yes', 'y ', 'yes ']:
                    print("Exiting...")
                    sys.exit()

            for file_name in file_list:
                file_path = os.path.join(self._models_path, file_name)
                os.remove(file_path)

            self._n_players = max(self._n_players, 4)
            self._players = [PlayerNN() for _ in range(self._n_players)]
            print(f'Simulating with {self._n_players} players.')

    def create_child_model(self, n_children):
        """
        Create a child Player based on the saved ones
        """
        if n_children > 0:
            file_list = [f for f in os.listdir(self._models_path) if os.path.isfile(os.path.join(self._models_path, f))]
            num_existing_models = len(file_list)

            for i in range(n_children):
                if num_existing_models > 1:
                    parent1_idx = random.randint(0, num_existing_models - 1)
                    parent2_idx = random.randint(0, num_existing_models - 1)

                    # Ensure parents are different
                    while parent2_idx == parent1_idx:
                        parent2_idx = random.randint(0, num_existing_models - 1)

                    parent1_name = os.path.join(self._models_path, f"nn_weights_{parent1_idx}.pth")
                    parent2_name = os.path.join(self._models_path, f"nn_weights_{parent2_idx}.pth")

                    parent1 = PlayerNN()
                    parent2 = PlayerNN()

                    parent1.load_model(filename=parent1_name)
                    parent2.load_model(filename=parent2_name)

                    child = crossover(parent1, parent2)
                    child.model.mutate_weights(probability=self._mutation_probability, scale=self._mutation_scale)
                else:
                    child = PlayerNN()
                    child.load_model(filename=os.path.join(self._models_path, file_list[0]))
                    child.model.mutate_weights(probability=self._mutation_probability, scale=self._mutation_scale)

                self._players.append(child)

    def evolve_generations(self):
        # Start evolution
        generation = len(self._time_steps)
        while generation < self._generations:
            start_time = time.time()

            # Run generation
            self.run_generation()

            # Print Status
            self._print_evolution(start_time=start_time, generation=generation)

            # Save status of iteration
            self._save_status()

            # Save top of current generation
            players_to_remove = []
            players_to_add = 0
            for i in range(len(self._players)):
                if i < self._n_players * self._propagate_percentage:
                    self._players[i].save_model(name=i)
                else:
                    players_to_remove.append(self._players[i])
                    players_to_add += 1

            # Remove last players
            for player in players_to_remove:
                self._players.remove(player)
            self.create_child_model(players_to_add)

            generation += 1

    def _print_evolution(self, start_time, generation):
        self._time_steps.append(time.time() - start_time)
        total_seconds = (self._generations - generation) * np.mean(self._time_steps)
        days, remainder = divmod(total_seconds, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = "{:>2} days, {:>2} hours, {:>2} minutes".format(int(days), int(hours), int(minutes))

        print("\r Generation {:>3}. Max Score: {:>.2f}. time/generation: {:>.2f}. Time remaining: {}. "
              "iterations/hour: {:>.2f}.".format(generation, max(self._generation_scores[-1]),
                                                 np.mean(self._time_steps),
                                                 formatted_time,
                                                 60 * 60 / np.mean(self._time_steps)))

    def _save_status(self):
        file_path = os.path.join(self._data_path, f'genetic_algorithm_status_{self._name}.pkl')
        parameters = {
            'time_steps': self._time_steps,
            'generation_scores': self._generation_scores
        }

        with open(file_path, 'wb') as file:
            pickle.dump(parameters, file)

    def _load_status(self):
        file_path = os.path.join(self._data_path, f'genetic_algorithm_status_{self._name}.pkl')

        try:
            with open(file_path, 'rb') as file:
                loaded_parameters = pickle.load(file)

            self._time_steps = loaded_parameters['time_steps']
            self._generation_scores = loaded_parameters['generation_scores']
            self._generations += len(loaded_parameters['time_steps'])

            total_seconds = np.sum(self._time_steps)
            days, remainder = divmod(total_seconds, 24 * 60 * 60)
            hours, remainder = divmod(remainder, 60 * 60)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = "{:>2} days, {:>2} hours, {:>2} minutes".format(int(days), int(hours), int(minutes))

            print(f"Summary:\n\tGenerations simulated: {len(loaded_parameters['time_steps']):>4}"
                  f"\n\tPlayers: {self._n_players:>4}"
                  f"\n\tTotal time: {formatted_time}"
                  f"\n\tImprovement: {np.max(self._generation_scores[0]):>.2f} - "
                  f"{np.max(self._generation_scores[-1]):>.2f}\n")

        except FileNotFoundError:
            print(f"File '{self._name}'.pkl does not exist. Creating new one.")

    @property
    def generation_scores(self):
        return self._generation_scores

    @property
    def players(self):
        return self._players

    @property
    def time_steps(self):
        return self._time_steps

    @property
    def name(self):
        return self._name

    @property
    def data_path(self):
        return self._data_path
