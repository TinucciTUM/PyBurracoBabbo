"""
Module: Game
Author: Alessandro Tinucci
Version: 1.0
Description: Main game logic for Burraco.

This module handles the game flow, rules, and interactions between different components of the game.
"""


from .deck import Deck
from .game_analytics import GameAnalytics
from utils.logger_config import setup_logger


class Game:
    NUMBER_OF_INITIAL_CARDS = 11
    TURN_LIMIT = 1e2
    GAME_LIMIT = 5

    def __init__(self, save_stats=False, log=False):
        self.deck = Deck()
        self.deck_secondary = []
        self.players = []

        self.initial_player_index = 0
        self.current_player_index = self.initial_player_index
        self.turn = 0
        self.round = 0
        self.game_over = False
        self.winner = None
        self.stats = GameAnalytics(save_data=save_stats)
        self._debug = log
        if self._debug:
            self._logger = setup_logger()

    def reset(self):
        self.deck = Deck()
        self.deck_secondary = []
        for i, _ in enumerate(self.players):
            self.deck_secondary.append([])
        self.initial_player_index = (self.initial_player_index + 1) % len(self.players)
        self.current_player_index = self.initial_player_index
        self.turn = 0
        self.game_over = False

        for i, player in enumerate(self.players):
            player.hand = []
            player.melds = []
            player.turn_history.append(player.turn)
            player.turn = 0
            player.round += 1
            self.deck_secondary[i] = []

    def reset_game(self):
        self.reset()
        for player in self.players:
            player.score_history.append(player.score_evaluation)
            player.score = 0
            player.round = 0
            player.secondary_deck = False

    def add_player(self, player):
        self.players.append(player)

    def setup_game(self):
        # Shuffle the deck
        self.deck.shuffle()
        self.deck_secondary = []

        for i, _ in enumerate(self.players):
            self.deck_secondary.append([])

        # Deal initial cards to each player
        for _ in range(self.NUMBER_OF_INITIAL_CARDS):
            for player in self.players:
                player.hand.append(self.deck.draw_card())

            for deck in self.deck_secondary:
                deck.append(self.deck.draw_card())

    def setup_match(self):
        self.winner = None
        self.round = 0
        for player in self.players:
            player.turn_history = []
        self.setup_game()

    def play_game(self):
        self.setup_match()
        while not self.winner:
            self.setup_game()

            while not self.game_over:
                self.play_round()

            self.stats.add_turn(self.turn + 1)

            if self._debug:
                self._logger.info(f"Round Over. Turns: {self.turn}")

            if self.players[self.current_player_index].score >= 1000:
                self.winner = self.players[self.current_player_index]
                self.stats.add_round(self.round)

                if self._debug:
                    self._logger.info(f"Games: {self.round + 1}. Winner: {self.winner.name}. Score: {self.winner.score}\n")

            elif self.round >= self.GAME_LIMIT:
                self.winner = max(self.players, key=lambda player: player.score)
                self.stats.add_round(self.round)

                if self._debug:
                    self._logger.info(f"Reached Limit of Games. Winner: {self.winner.name}. Score: {self.winner.score}\n")

            else:
                self.round += 1
                self.reset()

        self.reset_game()

    def play_round(self):
        # Basic structure of a player's turn
        player = self.players[self.current_player_index]

        # 1. Drawing Phase: Draw from deck or pick discard pile
        if player.draw_card(discard_deck=self.deck.discard_pile):
            player.hand.append(self.deck.draw_card())
        else:
            for _ in range(len(self.deck.discard_pile)):
                player.hand.append(self.deck.discard_pile.pop())

        if self._debug:
            self._logger.debug(f'Player: {player.name}. Hand: {player.hand}')
            self._logger.debug(f'Melds: {[meld.cards for meld in player.melds]}\n')

        # 2. Additional Cards Phase: Add cards to existing melds
        player.add_melds()

        if self._debug:
            self._logger.debug(f'Player: {player.name}. Hand: {player.hand}')
            self._logger.debug(f'Melds: {[meld.cards for meld in player.melds]}\n')

        # 3. Melding Phase: Player lays down valid melds if any
        player.play_melds()

        if self._debug:
            self._logger.debug(f'Player: {player.name}. Hand: {player.hand}')
            self._logger.debug(f'Melds: {[meld.cards for meld in player.melds]}\n')

        # 4. Discarding Phase: Discard a card to end the turn
        if (len(player.hand) > 1 or
                (len(player.hand) == 1 and (player.burraco or not player.secondary_deck))):
            self.deck.discard_pile.append(player.discard_card())

            # 5. Check for win condition
            if len(player.hand) == 0 and player.burraco and player.secondary_deck:
                self.game_over = True
                self.count_score(player, True)

            elif self.turn >= self.TURN_LIMIT:
                self.game_over = True
                self.count_score(player, False)

            else:
                # 4.1 Pick secondary deck and pass
                if len(player.hand) == 0 and not player.secondary_deck:
                    while self.deck_secondary[self.current_player_index]:
                        player.hand.append(self.deck_secondary[self.current_player_index].pop())
                    player.secondary_deck = True

                # 4.2 Move to next player
                self.next_player()
                if self.current_player_index == 0:
                    for player in self.players:
                        player.turn += 1
                    self.turn += 1

        # 4.3 Pick secondary deck and continue playing
        elif len(player.hand) == 0 and not player.secondary_deck:
            while self.deck_secondary[self.current_player_index]:
                player.hand.append(self.deck_secondary[self.current_player_index].pop())
            player.secondary_deck = True

        else:
            raise ValueError("No cards to discard. Program will terminate.")

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def count_score(self, end_player, closed):
        for i, player in enumerate(self.players):
            # TODO: Calculate Burraco Bonuses
            if player is end_player and closed:
                player.score += 100

            elif len(self.deck_secondary[i]) > 0:
                player.score -= 100

            player.score += player.points
