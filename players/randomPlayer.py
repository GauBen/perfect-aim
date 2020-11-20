"""Stratégie d'exemple: joueur qui joue au hasard."""
from entities import Player, Action
from random import choice


class RandomPlayer(Player):
    """Joueur qui joue au hasard."""

    name = "Je joue au hasard"

    def play(self, game):
        """Choisit une action aléatoirement parmi toutes les actions possibles."""
        c = choice(list(Action))
        while not game.is_valid_action(self, c):
            c = choice(list(Action))
        return c
