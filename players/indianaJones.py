"""Stratégie d'exemple: un joueur qui cherche des items."""

from entities import PlayerEntity
from game import Action, Game, Player, Tile


class IndianaJones(Player):
    """Le célèbre aventurier."""

    name = "Indiana Jones"

    def play(self, game: Game):
        """Cherche un joueur adjacent ou un item atteignable."""
        explored = [
            [False for x in range(game.grid.size)] for y in range(game.grid.size)
        ]
        explored[self.y][self.x] = True
        tracks = []

        for direction in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            x, y = direction.apply((self.x, self.y))
            attack = direction.attack()

            # Si on a un joueur sur la case d'à côté, on l'attaque
            if any(
                isinstance(e, PlayerEntity) for e in game.entity_grid[y][x]
            ) and game.is_valid_action(self, attack):
                return attack

            # Sinon, on cherche les items
            if game.is_valid_action(self, direction):
                tracks.append(
                    (x, y, direction, game.background[y][x] == Tile.DAMAGED_FLOOR)
                )
                explored[y][x] = True

        while len(tracks) > 0:
            x, y, direction, dangerous = tracks.pop(0)
            if game.tile_grid[y][x] in (
                Tile.SHIELD,
                Tile.SPEEDBOOST,
                Tile.SUPER_FIREBALL,
            ):
                return direction

            for d in (
                Action.MOVE_UP,
                Action.MOVE_DOWN,
                Action.MOVE_LEFT,
                Action.MOVE_RIGHT,
            ):
                new_x, new_y = d.apply((x, y))
                if (
                    game.tile_grid[new_y][new_x] not in (Tile.WALL, Tile.LAVA)
                    and not explored[new_y][new_x]
                    and dangerous
                    >= (game.background[new_y][new_x] == Tile.DAMAGED_FLOOR)
                ):
                    tracks.append(
                        (
                            new_x,
                            new_y,
                            direction,
                            game.background[new_y][new_x] == Tile.DAMAGED_FLOOR,
                        )
                    )  # Direction d'origine
                    explored[new_y][new_x] = True

        return Action.WAIT
