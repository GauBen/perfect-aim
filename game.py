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
    move,
    place_arrow,
)
from map import WALL, PLAYER_BLUE, PLAYER_RED, ARROW, Map


class Game:
    def __init__(self):
        self.map = Map()
        self.players = {
            Player(1, 1, 1.0, PLAYER_RED),
            Player(self.map.size - 2, self.map.size - 2, 1.5, PLAYER_BLUE),
        }
        self.arrows: set[Arrow] = set()
        self.t = 0
        self.grid = deepcopy(self.map.grid)

    def update(self, remaining: float):
        dt = min(
            [p.next_update_in(remaining) for p in self.players]
            + [a.next_update_in(remaining) for a in self.arrows]
            + [remaining]
        )
        self.t += dt

        for p in self.players:
            p.update(self, dt)
            self.update_grid()

        for a in self.arrows.copy():
            a.update(self, dt)
            if self.grid[a.y][a.x] == WALL:
                self.arrows.remove(a)
                continue
            for p in self.players.copy():
                if p.x == a.x and p.y == a.y:
                    self.players.remove(p)
            self.update_grid()

        if remaining - dt > 0:
            self.update(remaining - dt)

    def update_grid(self):
        self.grid = deepcopy(self.map.grid)

        for a in self.players:
            self.grid[a.y][a.x] = a.color

        for a in self.arrows.copy():
            self.grid[a.y][a.x] = ARROW

    def is_valid_action(self, player, action):
        if action == WAIT:
            return True
        elif action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
            x, y = move((player.x, player.y), action)
            try:
                if self.grid[y][x] in (WALL, PLAYER_RED, PLAYER_BLUE):
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True
        elif action in (ATTACK_UP, ATTACK_DOWN, ATTACK_LEFT, ATTACK_RIGHT):
            (x, y, _) = place_arrow((player.x, player.y), action)
            try:
                if self.grid[y][x] == WALL:
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True
        return False

    def player_attacks(self, player, action):
        x, y, direction = place_arrow((player.x, player.y), action)
        arrow = Arrow(x, y, direction)
        self.arrows.add(arrow)
