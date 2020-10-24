from copy import deepcopy

from entities import (
    ATTACK_DOWN,
    ATTACK_LEFT,
    ATTACK_RIGHT,
    ATTACK_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    WAIT,
    CantMoveThereException,
    Player,
    Arrow,
)
from map import EMPTY, PLAYER_BLUE, PLAYER_RED, Map


class Game:
    def __init__(self):
        self.map = Map()
        self.players = [
            Player(1, 1, 1.0, PLAYER_RED),
            Player(self.map.size - 2, self.map.size - 2, 1.5, PLAYER_BLUE),
        ]
        self.arrows = []
        self.t = 0
        self.grid = deepcopy(self.map.grid)

    def update(self, remaining: float):
        dt = min([p.next_update_in(remaining) for p in self.players] + [remaining])
        self.t += dt
        for p in self.players:
            p.update(self, dt)
            self.update_grid()
        for a in self.arrows:
            a.update(self, dt)
            self.update_grid()
        if remaining - dt > 0:
            self.update(remaining - dt)

    def update_grid(self):
        self.grid = deepcopy(self.map.grid)
        for p in self.players:
            self.grid[p.y][p.x] = p.color

    def is_valid_action(self, player, action):
        if action == WAIT:
            return True
        elif action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
            new_x = player.x
            new_y = player.y
            if action == MOVE_UP:
                new_y -= 1
            elif action == MOVE_DOWN:
                new_y += 1
            elif action == MOVE_LEFT:
                new_x -= 1
            elif action == MOVE_RIGHT:
                new_x += 1
            try:
                if self.grid[new_y][new_x] != EMPTY:
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True
        elif action in (ATTACK_UP, ATTACK_DOWN, ATTACK_LEFT, ATTACK_RIGHT):
            return True
        return False

    def player_attacks(self, player, action):
        x = player.x
        y = player.y
        direction = MOVE_UP
        if action == ATTACK_UP:
            y -= 1
        elif action == ATTACK_DOWN:
            y += 1
            direction = MOVE_DOWN
        elif action == ATTACK_LEFT:
            x -= 1
            direction = MOVE_LEFT
        elif action == ATTACK_RIGHT:
            x += 1
            direction = MOVE_RIGHT
        arrow = Arrow(x, y, direction)
        self.arrows.append(arrow)
