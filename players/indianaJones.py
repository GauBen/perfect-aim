"""Stratégie d'exemple: un joueur qui cherche des items."""

from entities import (
    Player,
    Action,
    move,
    swap_type,
    SHIELD,
)
from game import Game
from map import WALL, SUPER_FIREBALL, SPEEDBOOST, LAVA, DAMAGED_FLOOR


class IndianaJones(Player):
    """Le célèbre aventurier."""

    name = "Indiana Jones"

    def play(self, game: Game):
        """Cherche un joueur adjacent ou un item atteignable."""
        explored = [[False for x in range(game.map.size)] for y in range(game.map.size)]
        explored[self.y][self.x] = True
        tracks = []

        for direction in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            x, y = move((self.x, self.y), direction)
            attack = swap_type(direction)

            # Si on a un joueur sur la case d'à côté, on l'attaque
            if any(
                isinstance(e, Player) for e in game.entity_grid[y][x]
            ) and game.is_valid_action(self, attack):
                return attack

            # Sinon, on cherche les items
            if game.is_valid_action(self, direction):
                tracks.append((x, y, direction, game.background[y][x] == DAMAGED_FLOOR))
                explored[y][x] = True

        while len(tracks) > 0:
            x, y, direction, dangerous = tracks.pop(0)
            if game.grid[y][x] in (SHIELD, SPEEDBOOST, SUPER_FIREBALL):
                return direction

            for d in (
                Action.MOVE_UP,
                Action.MOVE_DOWN,
                Action.MOVE_LEFT,
                Action.MOVE_RIGHT,
            ):
                new_x, new_y = move((x, y), d)
                if (
                    game.grid[new_y][new_x] not in (WALL, LAVA)
                    and not explored[new_y][new_x]
                    and dangerous >= (game.background[new_y][new_x] == DAMAGED_FLOOR)
                ):
                    tracks.append(
                        (
                            new_x,
                            new_y,
                            direction,
                            game.background[new_y][new_x] == DAMAGED_FLOOR,
                        )
                    )  # Direction d'origine
                    explored[new_y][new_x] = True

        return Action.WAIT
