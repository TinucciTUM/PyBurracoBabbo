"""
Module: Burraco NN Player
Author: Alessandro Tinucci
Version: 1.0
Description: ML Player for the game Burraco.

This module implements the ML interface for playing Burraco.
"""

import torch
import random
import os

from pyburraco.players.player import Player
from pyburraco.game_logic.meld import Meld
from .player_nn_net import PlayerNNNet
from . import nn_helpers as nH

N_MELDS_ENCODED = 10
IN_LAYER_SIZE = 216 + N_MELDS_ENCODED * 16 + 1

# TODO - probably increase cards_play and length_melds
N_CARDS_PLAY = 5
N_MELDS_PLAY = 5
LENGTH_MELDS = 6
OUT_LAYER_SIZE = 1 + 10 * N_CARDS_PLAY + 6 * LENGTH_MELDS * N_MELDS_PLAY + 6


class PlayerNN(Player):
    device = "cuda"
    _initialized = False
    _id = 0

    def __init__(self):
        if not PlayerNN._initialized:
            # Run the initialization code only if not already initialized
            PlayerNN._initialize_class()
            PlayerNN._initialized = True

        super().__init__()
        self.nn = PlayerNNNet(IN_LAYER_SIZE, OUT_LAYER_SIZE)
        self.model = self.nn.to(self.device)

        self.name = "NN_" + str(PlayerNN._id)
        self.id = PlayerNN._id
        PlayerNN._id += 1

        self._discard_pile = []
        self._encoded_status = torch.zeros(IN_LAYER_SIZE)
        self._phase = 0b0
        self._ran_nn_bool = False
        self._output = []

    @classmethod
    def _initialize_class(cls):
        cls.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        print(f"Using {cls.device} device")

    def save_model(self, name=None):
        if name is not None:
            torch.save(self.model.state_dict(),
                       os.path.join(os.getcwd(), "data", "models", f"nn_weights_{name}.pth"))
        else:
            torch.save(self.model.state_dict(),
                       os.path.join(os.getcwd(), "data", "models", f"nn_weights_{self._id}.pth"))

    def load_model(self, filename):
        self.model.load_state_dict(torch.load(filename))

    def draw_card(self, discard_deck):
        # Returns true if picking from deck, false if taking discards pile
        self._phase = 0b0
        self._discard_pile = discard_deck

        output = self.model(self.encoded_game_status).tolist()
        draw_bool = round(output[0])

        if not draw_bool:
            self._discard_pile = []

        self._ran_nn_bool = False
        return draw_bool

    def play_melds(self):
        self.process_output()

        remove_idx = []
        index_start = 1 + 10 * N_CARDS_PLAY
        for i in range(N_MELDS_PLAY):
            possible_meld_idx = []

            for j in range(LENGTH_MELDS):
                # TODO - Verify this index
                idx = index_start + i * 6 * LENGTH_MELDS + j * 6
                card_list = self._output[idx:(idx + 6)]
                binary_card_index = ''.join(str(bit) for bit in card_list)
                card_index = int(binary_card_index, 2)

                # card_index == 0 used to signal no card
                if card_index == 0:
                    break

                elif (card_index-1 < len(self.hand)
                      and card_index not in remove_idx
                      and card_index not in possible_meld_idx):
                    possible_meld_idx.append(card_index)

            if len(possible_meld_idx) > 2:
                possible_meld = Meld([self.hand[card_idx-1] for card_idx in possible_meld_idx])

                if possible_meld.valid and self.can_play_card(len(possible_meld_idx) + len(remove_idx)):
                    self.melds.append(possible_meld)
                    remove_idx.extend(possible_meld_idx)

        remove_cards = [self.hand[idx-1] for idx in remove_idx]
        for card in remove_cards:
            self.hand.remove(card)

    def add_melds(self):
        self.process_output()

        idx_to_remove = []
        for i in range(N_CARDS_PLAY):
            card_list = self._output[(1 + i*10):(7 + i*10)]
            meld_list = self._output[(7 + i*10):(11 + i*10)]

            binary_card_index = ''.join(str(bit) for bit in card_list)
            binary_meld_index = ''.join(str(bit) for bit in meld_list)

            card_index = int(binary_card_index, 2)
            meld_index = int(binary_meld_index, 2)

            # meld_index == 0 used to indicate not to add anything
            if (meld_index != 0 and self.melds and card_index < len(self.hand) and meld_index < len(self.melds)
                    and self.can_play_card(len(idx_to_remove)) and card_index not in idx_to_remove):

                card = self.hand[card_index]
                self.melds[meld_index-1].cards = self.melds[meld_index-1].cards + [card]
                if self.melds[meld_index-1].valid:
                    idx_to_remove.append(card_index)

                else:
                    meld = self.melds[meld_index-1]
                    meld.cards.remove(card)
                    self.melds[meld_index-1].cards = meld.cards

        cards_to_remove = [self.hand[card_idx] for card_idx in idx_to_remove]
        for card in cards_to_remove:
            self.hand.remove(card)

    def discard_card(self):
        self.process_output()
        discard_pos_output = self._output[-7:-1]

        binary_string = ''.join(str(bit) for bit in discard_pos_output)
        discard_pos = int(binary_string, 2)

        if discard_pos >= len(self.hand):
            discard_pos = random.randint(0, len(self.hand) - 1)
        return self.hand.pop(discard_pos)

    def process_output(self):
        if not self._ran_nn_bool:
            self._process_output()

    def _process_output(self):
        self._phase = 0b1
        output = self.model(self.encoded_game_status).tolist()
        self._output = [round(val) for val in output]
        self._ran_nn_bool = True

    @property
    def encoded_game_status(self):
        encoded_status = nH.binary_to_tensor(PlayerNN.device, self._phase, 1)

        encoded_discard_pile = nH.encode_deck(PlayerNN.device, self._discard_pile)
        encoded_status = torch.cat((encoded_status, encoded_discard_pile), dim=0)

        encoded_hand = nH.encode_deck(PlayerNN.device, self.hand)
        encoded_status = torch.cat((encoded_status, encoded_hand), dim=0)

        encoded_melds = nH.encode_melds(PlayerNN.device, self.melds, N_MELDS_ENCODED)
        encoded_status = torch.cat((encoded_status, encoded_melds), dim=0)

        self._encoded_status = encoded_status
        return self._encoded_status

    def __repr__(self):
        return f'<Player {self.name}>'
