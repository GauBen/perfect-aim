"""
Stratégie de l'équipe Bob Morane.

MIT License

Copyright (c) 2020 Quentin VERDIER

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import entities
from game import Action, Game, Player, Tile


class BobMorane(Player):
    """Le Véritable aventurier."""

    NAME = "Bob Morane"

    def play(self, game: Game) -> Action:
        """Cherche les autres joueurs pour attaquer et les boules de feu à éviter."""
        # Coordonnées de la case voisine en haut
        x, y = Action.MOVE_UP.apply((self.x, self.y))

        # On regarde en haut jusqu'au prochain mur
        while game.background[y][x] != Tile.WALL:

            # On regarde l'ensemble des entités sur la case
            for entity in game.entity_grid[y][x]:

                # Si on Trouve un Joueur ou une Boule de feu
                if isinstance(entity, entities.PlayerEntity) and self.is_action_valid(
                    Action.ATTACK_UP
                ):
                    # On attaque un joueur vers le haut
                    return Action.ATTACK_UP
                elif isinstance(entity, entities.Fireball):
                    # On fuit dans une autre direction que la Boule de feu
                    if self.is_action_valid(Action.MOVE_RIGHT):
                        return Action.MOVE_RIGHT
                    elif self.is_action_valid(Action.MOVE_LEFT):
                        return Action.MOVE_LEFT
                    elif self.is_action_valid(Action.MOVE_DOWN):
                        return Action.MOVE_DOWN
            # On va sur la case haute suivante
            x, y = Action.MOVE_UP.apply((x, y))

        # Coordonnées de la case voisine en bas
        x, y = Action.MOVE_DOWN.apply((self.x, self.y))

        # On regarde en bas jusqu'au prochain mur
        while game.background[y][x] != Tile.WALL:

            # On regarde l'ensemble des entités sur la case
            for entity in game.entity_grid[y][x]:

                # Si on Trouve un Joueur ou une Boule de feu
                if isinstance(entity, entities.PlayerEntity) and self.is_action_valid(
                    Action.ATTACK_DOWN
                ):
                    # On attaque un joueur vers le bas
                    return Action.ATTACK_DOWN
                elif isinstance(entity, entities.Fireball):
                    # On fuit dans une autre direction que la Boule de feu
                    if self.is_action_valid(Action.MOVE_RIGHT):
                        return Action.MOVE_RIGHT
                    elif self.is_action_valid(Action.MOVE_LEFT):
                        return Action.MOVE_LEFT
                    elif self.is_action_valid(Action.MOVE_UP):
                        return Action.MOVE_UP
            # On va sur la case basse suivante
            x, y = Action.MOVE_DOWN.apply((x, y))

        # Coordonnées de la case gauche voisine
        x, y = Action.MOVE_LEFT.apply((self.x, self.y))

        # On regarde à gauche jusqu'au prochain mur
        while game.background[y][x] != Tile.WALL:

            # On regarde l'ensemble des entités sur la case
            for entity in game.entity_grid[y][x]:

                if isinstance(entity, entities.PlayerEntity) and self.is_action_valid(
                    Action.ATTACK_LEFT
                ):
                    # On attaque un joueur vers la gauche
                    return Action.ATTACK_LEFT
                elif isinstance(entity, entities.Fireball):
                    # On fuit dans une autre direction que la Boule de feu
                    if self.is_action_valid(Action.MOVE_UP):
                        return Action.MOVE_UP
                    elif self.is_action_valid(Action.MOVE_DOWN):
                        return Action.MOVE_DOWN
                    elif self.is_action_valid(Action.MOVE_RIGHT):
                        return Action.MOVE_RIGHT
            # On va sur la case gauche suivante
            x, y = Action.MOVE_LEFT.apply((x, y))

        # Coordonnées de la case droite voisine
        x, y = Action.MOVE_RIGHT.apply((self.x, self.y))

        # On regarde à droite jusqu'au prochain mur
        while game.background[y][x] != Tile.WALL:

            # On regarde l'ensemble des entités sur la case
            for entity in game.entity_grid[y][x]:

                if isinstance(entity, entities.PlayerEntity) and self.is_action_valid(
                    Action.ATTACK_RIGHT
                ):
                    # On attaque un joueur vers la droite
                    return Action.ATTACK_RIGHT
                elif isinstance(entity, entities.Fireball):
                    # On fuit dans une autre direction que la Boule de feu
                    if self.is_action_valid(Action.MOVE_UP):
                        return Action.MOVE_UP
                    elif self.is_action_valid(Action.MOVE_DOWN):
                        return Action.MOVE_DOWN
                    elif self.is_action_valid(Action.MOVE_LEFT):
                        return Action.MOVE_LEFT
            # On va sur la case droite suivante
            x, y = Action.MOVE_RIGHT.apply((x, y))

        """Cherche les objets les plus proches et se mettre en sécurité."""
        # Renvoie `True` si la destination est acceptable
        accept_target = (
            lambda x, y: game.background[y][x] == Tile.FLOOR
            and game.tile_grid[y][x].is_bonus()
        )

        # Renvoie `True` si le chemin est sûr
        is_safe = (
            lambda x, y: game.background[y][x] == Tile.FLOOR
            and not game.tile_grid[y][x].is_dangerous()
        )

        # Si on est en danger, on cherche un endroit sûr
        if game.background[self.y][self.x] == Tile.DAMAGED_FLOOR:
            accept_target = is_safe

            # N'importe quel endroit où on peut marcher est sûr
            is_safe = lambda x, y: game.background[y][x].is_floor()

        # Matrice des cases explorées par la recherche de chemin
        explored = [[False for x in range(game.size)] for y in range(game.size)]
        explored[self.y][self.x] = True

        # Tous les chemins possibles sans demi-tour depuis la case actuelle
        paths = []

        # On regarde quelles sont les cases atteignables depuis la case actuelle
        for direction in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            # Coordonnées de la case voisine
            x, y = direction.apply((self.x, self.y))

            # Si on peut aller dans cette direction, on explore les possibilités offertes
            if self.is_action_valid(direction):
                # On retient quelle est la direction de départ
                paths.append((x, y, direction))
                explored[y][x] = True

        # Tant qu'il existe des chemins possibles
        while len(paths) > 0:

            # On regarde un chemin envisageable
            x, y, direction = paths.pop(0)

            # Si sa destination est acceptable, on va dans la direction de départ
            # pour s'y rendre
            if accept_target(x, y):
                return direction

            # On regarde les 4 cases potentiellement atteignable depuis le bout du
            # chemin considéré
            for d in (
                Action.MOVE_UP,
                Action.MOVE_DOWN,
                Action.MOVE_LEFT,
                Action.MOVE_RIGHT,
            ):
                # On regarde la case voisine
                new_x, new_y = d.apply((x, y))

                # Si le chemin est sécurisé, on envisage d'y aller
                if is_safe(new_x, new_y) and not explored[new_y][new_x]:
                    paths.append((new_x, new_y, direction))  # Direction d'origine
                    explored[new_y][new_x] = True
        return Action.WAIT
