from random import choice

WAIT = 0
MOVE_UP = 1
MOVE_DOWN = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4


class Player:
    name = "PlayerOne"

    def __init__(self, x=5, y=5, speed=1.0):
        self.x = x
        self.y = y

        self.speed = speed
        self.action = WAIT
        self.in_action_for = 0

    def play(self):
        return choice([WAIT, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT])

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
            if self.action == MOVE_UP:
                self.y -= 1
            elif self.action == MOVE_DOWN:
                self.y += 1
            elif self.action == MOVE_LEFT:
                self.x -= 1
            elif self.action == MOVE_RIGHT:
                self.x += 1
            self.in_action_for = 0.5 / self.speed
        elif self.in_action_for + dt >= 1 / self.speed:
            dt -= 1 / self.speed - self.in_action_for
            self.in_action_for = 0
            self.action = self.play()
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
