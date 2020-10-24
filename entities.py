from random import choice

WAIT = 0
MOVE_UP = 1
MOVE_DOWN = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4
ATTACK_UP = 11
ATTACK_DOWN = 12
ATTACK_LEFT = 13
ATTACK_RIGHT = 14


class CantMoveThereException(Exception):
    pass


class Entity:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class MovingEntity(Entity):
    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.speed = speed
        self.action = WAIT
        self.in_action_for = 0.0

    def next_update_in(self, dt):
        if (
            self.action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT)
            and self.in_action_for < 0.5 / self.speed
            and self.in_action_for + dt >= 0.5 / self.speed
        ):
            return 0.5 / self.speed - self.in_action_for
        else:
            return 1 / self.speed - self.in_action_for

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


class Player(MovingEntity):
    name = "PlayerOne"

    def __init__(self, x, y, speed, color):
        super(Player, self).__init__(x, y, speed)
        self.color = color

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
                    WAIT,
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

    def update(self, game, dt: float):
        if (
            self.action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT)
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
                # me am smart
                self.action = self.action + (self.action % 2) - ((self.action + 1) % 2)
            self.in_action_for = 0.5 / self.speed

        elif self.in_action_for + dt >= 1 / self.speed:
            self.in_action_for = 0
            # Choix de la prochaine action
            action = self.play(game)
            if game.is_valid_action(self, action):
                self.action = action
                if self.action in (ATTACK_UP, ATTACK_DOWN, ATTACK_LEFT, ATTACK_RIGHT):
                    game.player_attacks(self, self.action)
            else:
                self.action = WAIT
                print("Action invalide pour le joueur " + self.name)

        else:
            self.in_action_for += dt


class Arrow(MovingEntity):
    def __init__(self, x, y, direction):
        super().__init__(x, y, 4.0)
        self.action = direction

    def update(self, game, dt: float):
        if (
            self.in_action_for < 0.5 / self.speed
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
            self.x = new_x
            self.y = new_y
            self.in_action_for = 0.5 / self.speed

        elif self.in_action_for + dt >= 1 / self.speed:
            self.in_action_for = 0

        else:
            self.in_action_for += dt
