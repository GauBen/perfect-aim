"""Stratégie d'exemple : un joueur qui joue au hasard."""

from random import choice

from game import Action, Game, Player


class RandomPlayer(Player):
    """Joueur qui joue au hasard."""

    NAME = "1 - Joueur aléatoire"

    def play(self, game: Game) -> Action:
        """Choisit une action aléatoirement parmi toutes les actions possibles."""
        c = choice(list(Action))
        while not self.is_action_valid(c):
            c = choice(list(Action))
        return c
