import numpy as np
import matplotlib.pyplot as plt
import os, sys, time
from torchviz import make_dot
import torch

from pyburraco.players.player_nn import PlayerNN

MODELS_PATH = os.path.join(os.getcwd(), 'data', 'models')
FILES_LIST = [f for f in os.listdir(MODELS_PATH) if os.path.isfile(os.path.join(MODELS_PATH, f))]

N_MELDS_ENCODED = 10
IN_LAYER_SIZE = 216 + N_MELDS_ENCODED * 16 + 1


def plot_saved_models():
    players = []
    plt1, ax1 = plt.subplots()
    for file in FILES_LIST:
        new_player = PlayerNN()
        new_player.load_model(os.path.join(MODELS_PATH, file))
        players.append(new_player)

    for player in players:
        player.model.weights_histogram(bins=100, alpha=0.25)

    plt1.legend([f'{player.name}' for player in players])
    plt.show()


def plot_random_models():
    players = []
    plt1, ax1 = plt.subplots()
    for _ in range(10):
        players.append(PlayerNN())

    for i, player in enumerate(players):
        for _ in range(1):
            player.model.mutate_weights(probability=0.05, scale=0.2)
        player.model.weights_histogram(bins=100, alpha=0.25)

    plt1.legend([f'{player.name}' for player in players])
    plt.show()


def plot_model_nn():
    player = PlayerNN()
    player.load_model(os.path.join(MODELS_PATH, FILES_LIST[0]))

    dummy_text = torch.randn(1, IN_LAYER_SIZE).to("cuda")  # Adjust the size based on your input size
    dataloader_train = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(dummy_text))

    batch = next(iter(dataloader_train))
    yhat = player.model(batch[0])  # Access the text from the batch

    make_dot(yhat, params=dict(list(player.model.named_parameters()))).view()


if __name__ == '__main__':
    plot_saved_models()
