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
    def play(self, game):
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
