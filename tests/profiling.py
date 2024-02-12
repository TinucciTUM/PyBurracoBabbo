import cProfile
import os
import pstats

from pyburraco.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


def profile_main():
    ga = GeneticAlgorithm(n_players=10, n_games=2, generations=1, continue_training=True)
    ga.evolve_generations()


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()

    profile_main()

    pr.disable()

    # Create a Stats object
    stats = pstats.Stats(pr)
    stats.strip_dirs()
    stats.sort_stats('calls')
    stats.print_stats()
