from entities import (
    Player,
    WAIT,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    ATTACK_UP,
    ATTACK_DOWN,
    ATTACK_LEFT,
    ATTACK_RIGHT,
    move,
)
from game import Game
from map import WALL, SPEEDBOOST


class IndianaJones(Player):
    def play(self, game: Game):
        explored = [[False for x in range(game.map.size)] for y in range(game.map.size)]
        explored[self.y][self.x] = True
        tracks = []
        for direction in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
            if game.is_valid_action(self, direction):
                x, y = move((self.x, self.y), direction)
                tracks.append((x, y, direction))
                explored[y][x] = True

        while len(tracks) > 0:
            x, y, direction = tracks.pop(0)
            if game.grid[y][x] in (SPEEDBOOST,):
                return direction

            for d in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
                new_x, new_y = move((x, y), d)
                if game.grid[new_y][new_x] != WALL and not explored[new_y][new_x]:
                    tracks.append((new_x, new_y, direction))  # Direction d'origine
                    explored[new_y][new_x] = True

        return WAIT
