from map import EMPTY, PLAYER_RED, PLAYER_BLUE, Map
from entities import (
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    WAIT,
    CantMoveThereException,
    Player,
)
from copy import deepcopy


class Game:
    def __init__(self):
        self.map = Map()
        self.players = [
            Player(1, 1, 1.0, PLAYER_RED),
            Player(self.map.size - 2, self.map.size - 2, 1.5, PLAYER_BLUE),
        ]
        self.t = 0
        self.grid = deepcopy(self.map.grid)

    def update(self, remaining: float):
        dt = min([p.next_update_in(remaining) for p in self.players] + [remaining])
        self.t += dt
        for p in self.players:
            p.update(self, dt)
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
