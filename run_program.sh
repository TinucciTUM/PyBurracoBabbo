#!/bin/bash

# Open the first terminal tab and navigate to folder 1, then run Python script 1
gnome-terminal --tab --title="PyBurraco" --working-directory="/home/alessandro/Documents/Projects/Python/PyBurraco" -- bash -c "\
source venv/bin/activate && \
python3 -c '\
import sys; \
sys.path.append(\"/home/alessandro/Documents/Projects/Python/PyBurraco\"); \
from pyburraco.genetic_algorithm import GeneticAlgorithm; \
parameters = { \
    \"n_players\": 500, \
    \"n_games\": 1, \
    \"generations\": 1000, \
    \"continue_training\": True, \
    \"n_processors\": 16, \
    \"propagate_percentage\": 0.1, \
    \"mutation_probability\": 0.005, \
    \"mutation_scale\": 0.25 \
}; \
ga = GeneticAlgorithm(parameters); \
ga.evolve_generations()' && \
exec bash"

