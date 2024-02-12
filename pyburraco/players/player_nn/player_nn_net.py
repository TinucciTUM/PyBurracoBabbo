"""
Module: Burraco NN Net
Author: Alessandro Tinucci
Version: 1.0
Description: NN Net for the burraco_net.

This module implements the ML Network for playing Burraco.
"""

import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt


class PlayerNNNet(nn.Module):
    def __init__(self, in_layer_size, out_layer_size):
        super().__init__()

        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(in_layer_size, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, out_layer_size),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

    def mutate_weights(self, probability=0.01, scale=0.1):
        for param in self.parameters():
            with torch.no_grad():
                mutation_mask = torch.abs(torch.randn_like(param.data)) < probability
                mutation_values = scale * torch.randn_like(param.data)
                param.data[mutation_mask] += mutation_values[mutation_mask]
                param.data.clamp_(-1.0, 1.0)

    def weights_histogram(self, bins=10, alpha=0.5):
        weights = [param.data.flatten().cpu().numpy() for param in self.parameters() if param.requires_grad]
        flattened_weights = np.concatenate(weights)

        # Plot histogram
        plt.hist(flattened_weights, bins=bins, range=(-1.0, 1.0), alpha=alpha)
        plt.xlim((-1.0, 1.0))
        plt.title('Weights Histogram')
        plt.xlabel('Weight Values')
        plt.ylabel('Frequency')
