import numpy as np
import torch

from pyburraco.game_logic.meld import Meld
from pyburraco.players.player_coded import PlayerCoded
from pyburraco.game_logic.card import Card
import pyburraco.players.player_nn.nn_helpers as nH

SUIT_MAPPING = {'C': 'Clubs', 'S': 'Spades', 'D': 'Diamonds', 'H': 'Hearts', 'Joker': 'Joker'}


def test_meld_validity_1():
    meld = Meld([Card("Hearts", "4"), Card("Hearts", "4"), Card("Hearts", "5")])
    assert meld.valid is False


def test_meld_validity_2():
    meld = Meld([Card("Hearts", "4"), Card("Hearts", "10"), Card("Hearts", "J")])
    assert meld.valid is False


def test_meld_validity_3():
    meld = Meld([Card("Joker", "Joker"), Card("Hearts", "2"), Card("Clubs", "5")])
    assert meld.valid is False


def test_meld_sorting_1():
    meld = Meld([Card("Joker", "Joker"), Card("Hearts", "K"), Card("Clubs", "K")])
    assert meld.cards[0].rank != 'Joker'


def test_add_melds_1():
    ai_player = PlayerCoded()
    ai_player.melds = [Meld([Card("Hearts", "3"), Card("Hearts", "4"), Card("Hearts", "5"),
                             Card("Hearts", "6")])]
    ai_player.hand = [Card("Hearts", "2"), Card("Hearts", "7"), Card("Spades", "10"),
                      Card("Spades", "10")]
    ai_player.add_melds()

    assert ai_player.melds == [Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                                     Card("Hearts", "5"), Card("Hearts", "6"),
                                     Card("Hearts", "7"), Card("Hearts", "2")])]
    assert ai_player.hand == [Card("Spades", "10"), Card("Spades", "10")]


def test_add_melds_2():
    ai_player = PlayerCoded()
    ai_player.melds = [Meld([Card("Hearts", "2"), Card("Hearts", "5"),
                             Card("Hearts", "6")])]
    ai_player.hand = [Card("Hearts", "4"), Card("Spades", "10"),
                      Card("Spades", "10")]
    ai_player.add_melds()

    assert ai_player.melds == [Meld([Card("Hearts", "4"),
                                     Card("Hearts", "5"), Card("Hearts", "6"),
                                     Card("Hearts", "2")])]
    assert ai_player.hand == [Card("Spades", "10"), Card("Spades", "10")]


def test_add_melds_3():
    ai_player = PlayerCoded()
    ai_player.melds = [Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                             Card("Hearts", "5"), Card("Hearts", "2")])]
    ai_player.hand = [Card("Hearts", "A"), Card("Spades", "10"),
                      Card("Spades", "10")]
    ai_player.add_melds()

    assert ai_player.melds == [Meld([Card("Hearts", "A"),
                                     Card("Hearts", "2"), Card("Hearts", "3"),
                                     Card("Hearts", "4"), Card("Hearts", "5")])]
    assert ai_player.hand == [Card("Spades", "10"), Card("Spades", "10")]


def test_add_melds_4():
    ai_player = PlayerCoded()
    ai_player.melds = [Meld([Card("Hearts", "10"), Card("Hearts", "J"),
                             Card("Hearts", "Q"), Card("Hearts", "2")])]
    ai_player.hand = [Card("Hearts", "A"), Card("Spades", "10"),
                      Card("Spades", "10")]
    ai_player.add_melds()

    assert ai_player.melds == [Meld([Card("Hearts", "10"),
                                     Card("Hearts", "J"), Card("Hearts", "Q"),
                                     Card("Hearts", "2"), Card("Hearts", "A")])]
    assert ai_player.hand == [Card("Spades", "10"), Card("Spades", "10")]


def test_add_melds_5():
    ai_player = PlayerCoded()
    ai_player.melds = [Meld([Card("Hearts", "4"), Card("Joker", "Joker"),
                             Card("Hearts", "5")])]

    player_hand = [card.split("-") for card in ("9-H, 9-S, 8-C, J-H, A-S, 10-C, K-D, 5-S, 7-D, 4-H, 9-D, A-D, 4-H, "
                                                "7-D, Q-D, K-S, Q-H, A-D, J-S, K-D, 7-H, 4-S, Q-C, Joker-Joker, "
                                                "Joker-Joker, 10-D, 7-S, 4-C, 2-H, 2-C, 9-D, 8-H, 4-D, 10-D").split(", ")]
    ai_player.hand = [Card(SUIT_MAPPING[card[1]] if card[1] else card[0], card[0])
                      for card in player_hand]

    ai_player.add_melds()
    assert ai_player.melds[0].cards[0].rank != 'Joker'


def test_encoding_1():
    encoded_deck = nH.encode_card_from_deck(Card(suit='Spades', rank='A'), 0b0)
    assert np.log2(float(encoded_deck)) == 102


def test_encoding_2():
    encoded_deck = nH.encode_card_from_deck(Card(suit='Spades', rank='A'), 0b0)
    encoded_deck = nH.encode_card_from_deck(Card(suit='Spades', rank='A'), encoded_deck) ^ encoded_deck
    assert np.log2(float(encoded_deck)) == 103


def test_encoding_3():
    encoded_deck = nH.encode_deck([Card("Joker", "Joker")] * 4)

    result = torch.tensor([1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                          dtype=torch.float32)

    assert all([a == b for a, b in zip(encoded_deck, result)])


def test_encoding_meld_1():
    encoded_meld = nH.encode_meld(Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                                        Card("Hearts", "5")]))
    result = torch.tensor([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.])
    assert all([a == b for a, b in zip(encoded_meld, result)])


def test_encoding_meld_2():
    encoded_meld = nH.encode_meld(Meld([Card("Hearts", "3"), Card("Hearts", "2"),
                                        Card("Hearts", "5")]))
    result = torch.tensor([0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.])
    assert all([a == b for a, b in zip(encoded_meld, result)])


def test_encoding_meld_3():
    encoded_meld = nH.encode_meld(Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                                        Card("Hearts", "5"), Card("Hearts", "2")]))
    result = torch.tensor([0., 0., 1., 1., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.])
    assert all([a == b for a, b in zip(encoded_meld, result)])


def test_encoding_meld_4():
    encoded_meld = nH.encode_meld(Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                                        Card("Hearts", "5"), Card("Joker", "Joker")]))
    result = torch.tensor([0., 0., 1., 1., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.])
    assert all([a == b for a, b in zip(encoded_meld, result)])


def test_encoding_melds_1():
    encoded_meld = nH.encode_melds([Meld([Card("Hearts", "3"), Card("Hearts", "4"),
                                          Card("Hearts", "5")]),
                                    Meld([Card("Spades", "3"), Card("Spades", "4"),
                                          Card("Spades", "5")])], 10)
    result = torch.tensor([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0.,
                           0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 0.])
    assert all([a == b for a, b in zip(encoded_meld[:32], result[:32])])
