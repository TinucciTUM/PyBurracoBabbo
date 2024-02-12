import matplotlib.pyplot as plt
import numpy as np
import os

from pyburraco.genetic_algorithm.genetic_algorithm import GeneticAlgorithm

BOXPLOT_LIM = 50
VIOLINPLOT_LIM = 5

plt.rcParams['text.usetex'] = True


def plot_evolution(save_plot=False):
    genetic_algorithm = GeneticAlgorithm()
    
    player_generation_scores = []
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 16))

    # Boxplot of the previous generations
    axs[0, 0].boxplot(genetic_algorithm.generation_scores[-BOXPLOT_LIM:])
    axs[0, 0].set_xticks([y + 1 for y in range(len(genetic_algorithm.generation_scores[-BOXPLOT_LIM:]))])
    axs[0, 0].set_xticklabels([str(y) for y in range(1, len(genetic_algorithm.generation_scores[-BOXPLOT_LIM:]) + 1)])
    axs[0, 0].set_title('Score distribution')
    axs[0, 0].set_xlabel('Generation')
    axs[0, 0].set_ylabel('Score per turn')
    axs[0, 0].yaxis.grid(True)

    # Line plot of the scores of the different players
    window_size = 5
    mean_scores_per_generation = [np.mean(generation) for generation in genetic_algorithm.generation_scores]
    moving_avg_of_means = np.convolve(mean_scores_per_generation, np.ones(window_size)/window_size, mode='valid')
    for i, player in enumerate(genetic_algorithm.players):
        player_generation_scores.append([generation_score[i]
                                         for generation_score in genetic_algorithm.generation_scores])
        axs[1, 0].plot(range(1, len(genetic_algorithm.generation_scores) + 1), player_generation_scores[-1], alpha=0.5)
    axs[1, 0].plot(range(window_size, len(genetic_algorithm.generation_scores) + 1), moving_avg_of_means,
                   label='Moving Avg of Means', color='black')
    axs[1, 0].grid(True)
    axs[1, 0].set_title('Players score')
    axs[1, 0].set_xlabel('Generation')
    axs[1, 0].set_ylabel('Score per turn')

    # Violin plot of the distribution of scores for the top players
    violin = axs[0, 1].violinplot(player_generation_scores[:VIOLINPLOT_LIM], showmedians=True)
    for partname in ('cbars', 'cmins', 'cmaxes', 'cmedians'):
        vp = violin[partname]
        vp.set_edgecolor('black')
        vp.set_facecolor('black')

    for pc in violin['bodies']:
        pc.set_facecolor('black')
        pc.set_edgecolor('black')

    for partname in ('cmedians',):
        vp = violin[partname]
        vp.set_alpha(0)
        for line in vp.get_paths():
            x, y = line.vertices.mean(axis=0)  # Calculate the median position
            axs[0, 1].scatter(x, y, marker='o', color='black', edgecolors='black', s=50)

    axs[0, 1].set_xticks([y + 1 for y in range(len(genetic_algorithm.players[:VIOLINPLOT_LIM]))])
    axs[0, 1].set_xticklabels([player.name for player in genetic_algorithm.players[:VIOLINPLOT_LIM]])
    axs[0, 1].set_title('Best players score distribution')
    axs[0, 1].set_xlabel('Player')
    axs[0, 1].set_ylabel('Score per turn')
    axs[0, 1].yaxis.grid(True)

    # Line plot of the time taken per generation
    axs[1, 1].plot(100 * np.array(genetic_algorithm.time_steps) / np.average(genetic_algorithm.time_steps), 'k')
    axs[1, 1].set_title('Time taken per generation. '
                        'Mean: {:>.1f} seconds'.format(np.mean(genetic_algorithm.time_steps)))
    axs[1, 1].set_xlabel('Generation')
    axs[1, 1].set_ylabel('Time [s]')
    axs[1, 1].grid()

    # Save the plot
    if save_plot:
        plt.savefig(os.path.join(genetic_algorithm.data_path, f'genetic_algorithm_{genetic_algorithm.name}.png'),
                    dpi=300, bbox_inches='tight')

    # Show it
    plt.show()
