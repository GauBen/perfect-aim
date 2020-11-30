"""Stratégie d'exemple : un joueur très offensif."""

from entities import PlayerEntity

from game import Action, Game, Player, Tile


class Zidane(Player):
    """Parfois appelé Numéro 10."""

    NAME = "Zidane"

    def play(self, game: Game) -> Action:
        """Cherche le joueur le plus proche pour l'attaquer."""
        # On cherche à attaquer un joueur tout droit dans une direction
        action = self.attack(game)

        # S'il n'y a personne à attaquer, on va vers le joueur le plus proche
        if action == Action.WAIT:
            action = self.chase(game)

        if self.is_action_valid(action):
            return action

        # Si l'action n'est pas valide, on attend
        return Action.WAIT

    def attack(self, game: Game) -> Action:
        """Attaque le joueur le plus proche s'il est visible."""
        # On regarde si un joueur est en ligne de mire
        for action in (
            Action.ATTACK_UP,
            Action.ATTACK_DOWN,
            Action.ATTACK_LEFT,
            Action.ATTACK_RIGHT,
        ):
            x, y = action.to_movement().apply((self.x, self.y))

            # On regarde jusqu'au prochain mur dans la direction de l'attaque
            while game.background[y][x] != Tile.WALL:

                # On a trouvé un joueur : on attaque dans sa direction
                if any(
                    isinstance(entity, PlayerEntity)
                    for entity in game.entity_grid[y][x]
                ):
                    # Si on a des boules de feu disponibles, on attaque
                    if self.can_attack():
                        return action

                    # Sinon on le chasse
                    return action.to_movement()

                x, y = action.to_movement().apply((x, y))

        # On a rien trouvé
        return Action.WAIT

    def chase(self, game: Game) -> Action:
        """Se rend vers le joueur le plus proche."""
        # Aucun joueur en vue, on va vers le joueur le plus proche
        # (Voir IndianaJones pour le détail)
        explored = [[False for x in range(game.size)] for y in range(game.size)]
        explored[self.y][self.x] = True
        paths = []

        for direction in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            x, y = direction.apply((self.x, self.y))
            if self.is_action_valid(direction):
                paths.append((x, y, direction))
                explored[y][x] = True

        while len(paths) > 0:

            x, y, direction = paths.pop(0)
            if any(
                isinstance(entity, PlayerEntity) for entity in game.entity_grid[y][x]
            ):
                return direction

            for d in (
                Action.MOVE_UP,
                Action.MOVE_DOWN,
                Action.MOVE_LEFT,
                Action.MOVE_RIGHT,
            ):
                new_x, new_y = d.apply((x, y))
                if game.background[y][x].is_floor() and not explored[new_y][new_x]:
                    paths.append((new_x, new_y, direction))
                    explored[new_y][new_x] = True

        # On a toujours rien trouvé (on est piégé par la lave !)
        return Action.WAIT
