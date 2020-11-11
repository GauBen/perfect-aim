"""Stratégie d'exemple: joueur qui joue au hasard."""
from entities import (
    Player,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    ATTACK_UP,
    ATTACK_DOWN,
    ATTACK_LEFT,
    ATTACK_RIGHT,
)
from random import choice


class RandomPlayer(Player):
    """Joueur qui joue au hasard."""

    name = "Je joue au hasard"

    def play(self, game):
        """Choisit une action aléatoirement parmi toutes les actions possibles."""
        c = choice(
            [
                MOVE_UP,
                MOVE_DOWN,
                MOVE_LEFT,
                MOVE_RIGHT,
                ATTACK_UP,
                ATTACK_DOWN,
                ATTACK_LEFT,
                ATTACK_RIGHT,
            ]
        )
        while not game.is_valid_action(self, c):
            c = choice(
                [
                    MOVE_UP,
                    MOVE_DOWN,
                    MOVE_LEFT,
                    MOVE_RIGHT,
                    ATTACK_UP,
                    ATTACK_DOWN,
                    ATTACK_LEFT,
                    ATTACK_RIGHT,
                ]
            )
        return c
