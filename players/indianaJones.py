from entities import (
    Player,
    WAIT,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    move,
    swap_type,
)
from game import Game
from map import WALL, SUPER_FIREBALL, SPEEDBOOST


class IndianaJones(Player):
    def play(self, game: Game):

        explored = [[False for x in range(game.map.size)] for y in range(game.map.size)]
        explored[self.y][self.x] = True
        tracks = []

        for direction in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
            x, y = move((self.x, self.y), direction)
            attack = swap_type(direction)

            # Si on a un joueur sur la case d'à côté, on l'attaque
            if any(
                isinstance(e, Player) for e in game.entity_grid[y][x]
            ) and game.is_valid_action(self, attack):
                return attack

            # Sinon, on cherche les items
            elif game.is_valid_action(self, direction):
                tracks.append((x, y, direction))
                explored[y][x] = True

        while len(tracks) > 0:
            x, y, direction = tracks.pop(0)
            if game.grid[y][x] in (SPEEDBOOST, SUPER_FIREBALL):
                return direction

            for d in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
                new_x, new_y = move((x, y), d)
                if game.grid[new_y][new_x] != WALL and not explored[new_y][new_x]:
                    tracks.append((new_x, new_y, direction))  # Direction d'origine
                    explored[new_y][new_x] = True

        return WAIT
