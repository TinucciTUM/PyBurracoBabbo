"""
Module: NN Helpers
Author: Alessandro Tinucci
Version: 1.0
Description: Helper functions for Neural Networks of PyBurraco.
"""

import torch

RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUIT_ORDER = ['Hearts', 'Diamonds', 'Clubs', 'Spades']


def encode_card_from_deck(card, deck):
    if card.rank == 'Joker':
        card_bin = 1 << 104
    else:
        rank_pos = RANK_ORDER.index(card.rank)
        suit_pos = SUIT_ORDER.index(card.suit)
        position = (suit_pos * 13 + rank_pos) * 2
        card_bin = 1 << position

    return (deck + card_bin) | deck


def encode_deck(device, cards, n_cards=108):
    encoded_deck = 0b0
    for card in cards:
        encoded_deck = encode_card_from_deck(card, encoded_deck)
    return binary_to_tensor(device, encoded_deck, n_cards)


def encode_melds(device, melds, n_melds):
    encoded_melds = torch.tensor([], device=device)
    for i in range(n_melds):
        if i < len(melds):
            encoded_meld = encode_meld(device, melds[i])
            encoded_melds = torch.cat((encoded_melds, encoded_meld.to(device)), dim=0)
        else:
            encoded_melds = torch.cat((encoded_melds, torch.zeros(16, device=device)), dim=0)

    return encoded_melds


def encode_meld(device, meld):
    # Encode type bit 1
    if meld.meld_type == 'Set':
        encoded_meld = 1
    else:
        encoded_meld = 0

    # Encode first card suit (bits 2-3) and rank (bits 4-7)
    rank_pos = RANK_ORDER.index(meld.cards[0].rank)
    suit_pos = SUIT_ORDER.index(meld.cards[0].suit)
    encoded_meld += suit_pos * 2 + rank_pos * 8

    # Encode number of cards
    encoded_meld += (len(meld.cards) - 3) * 128

    # Encode if there is a joker
    # TODO - 2s are virtually the same as jokers and cannot function as 2s
    if meld.wildcards:
        encoded_meld += 2048

        wildcard_position = [i for i, card in enumerate(meld.cards) if card in meld.wildcards]
        encoded_meld += wildcard_position[0] * 4096

    return binary_to_tensor(device, encoded_meld, 16)


def binary_to_tensor(device, binary_data, array_size):
    binary_list = [(binary_data >> i) & 1 for i in range(array_size - 1, -1, -1)]
    return torch.tensor(binary_list, dtype=torch.float32, device=device)
