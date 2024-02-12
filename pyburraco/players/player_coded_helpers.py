"""
Module: Player Helpers
Author: Alessandro Tinucci
Version: 1.0
Description: Helper functions for PyBurraco Players.
"""

from collections import defaultdict
from pyburraco.game_logic.helpers import card_rank_difference

RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def find_best_meld(hand, burraco):
    """
    Find the best possible meld in the hand.
    """
    all_melds = find_all_possible_melds(hand)
    if not all_melds:
        return None

    # Filter melds to those that are one card shorter than the hand
    if burraco:
        filtered_melds = [meld for meld in all_melds if len(meld) <= len(hand) - 1]
    else:
        filtered_melds = [meld for meld in all_melds if len(meld) < len(hand) - 1]

    if not filtered_melds:
        return None

    best_meld = max(filtered_melds, key=len, default=None)

    return best_meld


def find_all_possible_melds(hand):
    """
    Find all possible melds in the given hand.
    """
    possible_melds = []

    for suit in {'Hearts', 'Diamonds', 'Clubs', 'Spades'}:
        suited_cards = sorted([card for card in hand if card.suit == suit or card.rank == "2" or card.rank == "Joker"],
                              key=lambda c: c.rank)
        possible_melds.extend(find_all_runs(suited_cards))

    possible_melds.extend(find_all_sets(hand))

    return possible_melds


def find_all_sets(hand):
    """
    Find all sets in the given hand.

    Args:
        hand (list): The player's hand, a list of Card objects.

    Returns:
        list: A list of all sets (three or more cards of the same rank).
    """
    rank_groups = defaultdict(list)
    for card in hand:
        if card.rank not in ['2', 'Joker']:
            rank_groups[card.rank].append(card)

    wildcards = [card for card in hand if card.rank in ['2', 'Joker']]
    for rank in rank_groups:
        if not any(card.rank in ['2', 'Joker'] for card in rank_groups[rank]):
            # Add a wildcard to the group, if available
            if wildcards:
                rank_groups[rank].append(wildcards[0])

    sets = [group for group in rank_groups.values() if len(group) >= 3]
    return sets


def find_all_runs(suited_cards):
    """
    Find all runs among cards of the same suit.

    Args:
        suited_cards (list): Cards of the same suit, sorted by rank.

    Returns:
        list: A list of all runs (three or more consecutive cards of the same suit).
    """
    if not suited_cards or len(suited_cards) < 3:
        return []

    runs = []
    wildcards = [card for card in suited_cards if card.rank in ['2', 'Joker']]
    if wildcards:
        wildcards = [wildcards[0]]
    regular_cards = sorted([card for card in suited_cards if card.rank not in ['2', 'Joker']],
                           key=lambda c: RANK_ORDER.index(c.rank))

    run = []
    for i in range(len(regular_cards)):
        if not run or card_rank_difference(run[-1], regular_cards[i]) == -1:
            # Directly consecutive card
            run.append(regular_cards[i])
        elif wildcards and (not run or card_rank_difference(run[-1], regular_cards[i]) == -2):
            # Use a wildcard to bridge a single rank gap
            run.append(wildcards.pop())  # Use the wildcard
            run.append(regular_cards[i])
        else:
            # Not consecutive, check if run is valid to add to runs list
            if len(run) >= 3:
                runs.append(run)
            run = [regular_cards[i]]

    if len(run) >= 3:
        runs.append(run)

    return runs
