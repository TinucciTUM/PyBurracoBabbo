"""
Module: Helpers
Author: Alessandro Tinucci
Version: 1.0
Description: Helper functions for PyBurraco.
"""

RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def get_card_point_value(card):
    """
    Get the point value of a single card.

    Args:
        card (Card): The card object.

    Returns:
        int: The point value of the card.
    """
    card_point_values = {
        '2': 20, '3': 5, '4': 5, '5': 5, '6': 5, '7': 5,
        '8': 10, '9': 10, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 15,
        'Joker': 30
    }
    return card_point_values.get(card.rank, 0)


def calculate_meld_points(cards):
    """
    Calculate the points for a single meld.

    Args:
        cards (list): A list of Card objects representing a meld.

    Returns:
        int: The point value of the meld.
    """
    return sum(get_card_point_value(card) for card in cards)


def all_same_rank(cards):
    """
    Check if all cards have the same rank.

    Args:
        cards (list): A list of Card objects.

    Returns:
        bool: True if all cards have the same rank, False otherwise.
    """
    first_rank = cards[0].rank
    return all(card.rank == first_rank for card in cards)


def all_same_suit(cards):
    """
    Check if all cards have the same suit.

    Args:
        cards (list): A list of Card objects.

    Returns:
        bool: True if all cards have the same suit, False otherwise.
    """
    first_suit = cards[0].suit
    return all(card.suit == first_suit for card in cards)


def is_consecutive_run(regular_cards, wildcards):
    """
    Check if the cards can form a consecutive run of the same suit, allowing only one wildcard.

    Args:
        wildcards:
        regular_cards:

    Returns:
        bool: True if the cards can form a consecutive run with at most one wildcard, False otherwise.
    """
    if (regular_cards[-1].rank == 'A' and regular_cards[-2].rank != 'K' and
            (not wildcards or regular_cards[-2].rank != 'Q')):
        regular_cards.insert(0, regular_cards.pop())

    gap_filled = False if wildcards else True
    for i in range(1, len(regular_cards)):
        rank_gap = card_rank_difference(regular_cards[i], regular_cards[i - 1])
        if rank_gap != 1:
            if gap_filled or rank_gap != 2:  # A gap has already been filled by a wildcard
                return False
            elif rank_gap == 2:
                gap_filled = True
    return True


def card_rank_difference(card1, card2):
    """
    Calculate the difference in rank between two cards.

    Args:
        card1, card2 (Card): The card objects to compare.

    Returns:
        int: The difference in rank.
    """
    if card2.rank == 'A':
        return RANK_ORDER.index(card1.rank) + 1
    else:
        return RANK_ORDER.index(card1.rank) - RANK_ORDER.index(card2.rank)

