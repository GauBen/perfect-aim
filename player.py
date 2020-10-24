from random import choice
from map import EMPTY

WAIT = 0
MOVE_UP = 1
MOVE_DOWN = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4


class CantMoveThereException(Exception):
    pass


class Player:
    name = "PlayerOne"

    def __init__(self, color, x=1, y=1, speed=1.0):
        self.x = x
        self.y = y

        self.color = color
        self.speed = speed
        self.action = WAIT
        self.in_action_for = 0

    def play(self, game):
        c = choice([MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT])
        while not game.is_valid_action(self, c):
            c = choice([WAIT, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT])
        return c

    def next_update_in(self, dt):
        if (
            self.action > 0
            and self.in_action_for < 0.5 / self.speed
            and self.in_action_for + dt >= 0.5 / self.speed
        ):
            return 0.5 / self.speed - self.in_action_for
        else:
            return 1 / self.speed - self.in_action_for

    def update(self, game, dt: float):
        if (
            self.action > 0
            and self.in_action_for < 0.5 / self.speed
            and self.in_action_for + dt >= 0.5 / self.speed
        ):
            new_x = self.x
            new_y = self.y
            if self.action == MOVE_UP:
                new_y -= 1
            elif self.action == MOVE_DOWN:
                new_y += 1
            elif self.action == MOVE_LEFT:
                new_x -= 1
            elif self.action == MOVE_RIGHT:
                new_x += 1
            if game.is_valid_action(self, self.action):
                self.x = new_x
                self.y = new_y
            else:
                self.action = self.action + (self.action % 2) - ((self.action + 1) % 2)
            self.in_action_for = 0.5 / self.speed
        elif self.in_action_for + dt >= 1 / self.speed:
            dt -= 1 / self.speed - self.in_action_for
            self.in_action_for = 0
            # ****************
            action = self.play(game)
            if game.is_valid_action(self, action):
                self.action = action
            else:
                self.action = WAIT
                print("Action invalide pour le joueur " + self.name)
        else:
            self.in_action_for += dt

    def get_visual_x(self):
        if self.action == MOVE_LEFT:
            return (
                self.x
                + int(self.in_action_for >= 0.5 / self.speed)
                - self.in_action_for * self.speed
            )
        elif self.action == MOVE_RIGHT:
            return (
                self.x
                - int(self.in_action_for >= 0.5 / self.speed)
                + self.in_action_for * self.speed
            )
        return self.x

    def get_visual_y(self):
        if self.action == MOVE_UP:
            return (
                self.y
                + int(self.in_action_for >= 0.5 / self.speed)
                - self.in_action_for * self.speed
            )
        elif self.action == MOVE_DOWN:
            return (
                self.y
                - int(self.in_action_for >= 0.5 / self.speed)
                + self.in_action_for * self.speed
            )
        return self.y

    def action_progress(self):
        return self.in_action_for * self.speed
