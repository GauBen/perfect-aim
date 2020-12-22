"""
Stratégie de l'équipe Les Gangsters.

MIT License

Copyright (c) 2020 Tiziano Maisonhaute
Copyright (c) 2020 Enzo Petit

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

from game import Action, Game, Player, Tile
from entities import Fireball, PlayerEntity
import random

DEPTH_MAX = 10
COEFF_REGR = 0.9


class Gangsterino(Player):
    """Stratégie de l'équipe Les Gangsters."""

    NAME = "Gangsterino"

    def __init__(self):
        """Initialise le joueur."""
        Player.__init__(self)
        self.nb_visits = [[1 for i in range(21)] for j in range(21)]

    def play(self, game: Game) -> Action:
        """Choisit la meilleure action possible dans la situation donnée en paramètre."""
        all_directions = (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        )
        is_walkable = (
            lambda x, y: game.background[y][x] == Tile.FLOOR
            and not game.tile_grid[y][x] == Tile.LAVA
        )
        has_collectible = lambda x, y: game.tile_grid[y][x].is_collectible()

        if self.can_attack():
            for d in all_directions:
                x, y = d.apply((self.x, self.y))
                for ent in game.entity_grid[y][x]:
                    if isinstance(ent, PlayerEntity):
                        return d.to_attack()
            if random.randint(1, 10) <= 1:
                directionPossible = []
                for d in all_directions:
                    x, y = d.apply((self.x, self.y))
                    if game.tile_grid[y][x] != Tile.WALL:
                        directionPossible.append(d)
                if len(directionPossible) > 0:
                    return random.choice(directionPossible).to_attack()
            joueurCibleDir = []
            otherPlayers = (
                Tile.PLAYER_BLUE,
                Tile.PLAYER_GREEN,
                Tile.PLAYER_RED,
                Tile.PLAYER_YELLOW,
            )

            x = self.x

            for y in range(self.y + 1, 21):
                if game.tile_grid[y][x] == Tile.WALL:
                    break
                if game.tile_grid[y][x] in otherPlayers:
                    joueurCibleDir += [(Action.ATTACK_DOWN, y - self.y)]
                    break

            for y in range(0, self.y - 1):
                if game.tile_grid[y][x] == Tile.WALL:
                    break
                if game.tile_grid[y][x] in otherPlayers:
                    joueurCibleDir += [(Action.ATTACK_UP, self.y - y)]
                    break

            y = self.y
            for x in range(self.x + 1, 21):
                if game.tile_grid[y][x] == Tile.WALL:
                    break
                if game.tile_grid[y][x] in otherPlayers:
                    joueurCibleDir += [(Action.ATTACK_RIGHT, x - self.x)]
                    break

            for x in range(0, self.x - 1):
                if game.tile_grid[y][x] == Tile.WALL:
                    break
                if game.tile_grid[y][x] in otherPlayers:
                    joueurCibleDir += [(Action.ATTACK_LEFT, self.x - x)]
                    break

            if joueurCibleDir:
                return min(joueurCibleDir, key=lambda x: x[1])[0]

        visited = [[False for x in range(game.size)] for y in range(game.size)]

        visited[self.y][self.x] = True
        a_explorer = [
            [self.x, self.y, Action.WAIT, [], 0]
        ]  # c'est une liste de coordonnées sur lequel le joueur peut se déplacer

        self.score_objets = {
            Tile.COIN: 5,
            Tile.SUPER_FIREBALL: 10,
            Tile.SHIELD: 30,
            Tile.SPEEDBOOST: 20,
            Tile.SPEEDPENALTY: -1,
        }
        self.nb_visits[self.y][self.x] += 1
        for direction in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            # Coordonnées de la case voisine
            x, y = direction.apply((self.x, self.y))

            if not visited[y][x] and is_walkable(x, y):
                a_explorer.append([x, y, direction, [direction], 0])

        chemins_finis = []

        # Tant qu'il existe des chemins possibles
        while len(a_explorer) > 0:

            # On regarde un chemin envisageable
            x, y, direction, chemin, score = a_explorer.pop(0)
            depth = len(chemin)

            # Si sa destination est acceptable, on va dans la direction de départ
            # pour s'y rendre
            if has_collectible(x, y):
                score += self.score_objets[game.tile_grid[y][x]] * (COEFF_REGR ** depth)

            score += self.on_meurt(game, depth * self.speed) + max(
                15 - self.nb_visits[y][x], 1
            )
            score -= 30 * (game.tile_grid[self.y][self.x] == Tile.DAMAGED_FLOOR)

            if depth == DEPTH_MAX:
                chemins_finis.append([x, y, direction, chemin, score])
                continue

            # On regarde les 4 cases potentiellement atteignable depuis le bout du
            # chemin considéré

            CANTMOVE = all(
                [
                    not is_walkable(x, y) or visited[y][x]
                    for x, y in [d.apply((self.x, self.y)) for d in all_directions]
                ]
            )
            if CANTMOVE:
                chemins_finis.append([x, y, direction, chemin, score])
            for d in all_directions:
                # On regarde la case voisine
                new_x, new_y = d.apply((x, y))
                # Si le chemin est sécurisé, on envisage d'y aller
                if is_walkable(new_x, new_y) and not visited[new_y][new_x]:
                    chemin = chemin[:] + [d]
                    a_explorer.append(
                        [new_x, new_y, direction, chemin, score]
                    )  # Direction d'origine
                    visited[new_y][new_x] = True

        # meilleurChemin = max(chemins_finis, key = lambda x: x[4]/(len(x[3])+1))[3]

        scoreMax = -6e3
        meilleurChemin = None
        for k in range(len(chemins_finis)):
            score = chemins_finis[k][4]
            if score > scoreMax:
                scoreMax = score
                meilleurChemin = chemins_finis[k][3]

        return (
            (
                meilleurChemin[0]
                if self.is_action_valid(meilleurChemin[0])
                else Action.WAIT
            )
            if meilleurChemin
            else Action.WAIT
        )

    def on_meurt(self, game: Game, rnd: float) -> float:
        """Détermine le malus lié à la collision avec une boule de feu."""
        for ent in game.entities:
            if ent.TILE == Tile.FIREBALL:
                if abs(self.dist_boule_feu(ent) - 1) < 1:
                    if self.shield:
                        return -self.score_objets[Tile.SHIELD] * 0.75  # Random
                    else:
                        return -5e3
        return 0

    def dist_boule_feu(self, bdf: Fireball) -> float:
        """Distance avec la boule de feu."""
        BDFSPEED = bdf.speed
        direction = bdf.action
        if direction == Action.MOVE_DOWN or direction == Action.MOVE_UP:
            if self.x != bdf.x:
                return 50  # Approximativement l'infini

            if direction == Action.MOVE_DOWN:
                if bdf.y > self.y:
                    return 50
                else:
                    return (self.y - bdf.y) / BDFSPEED
            else:
                if bdf.y < self.y:
                    return 50
                else:
                    return -(self.y - bdf.y) / BDFSPEED

        if direction == Action.MOVE_LEFT or direction == Action.MOVE_RIGHT:
            if self.x != bdf.x:
                return 50  # Approximativement l'infini

            if direction == Action.MOVE_RIGHT:
                if bdf.x > self.x:
                    return 50
                else:
                    return (self.x - bdf.x) // BDFSPEED
            else:
                if bdf.y < self.y:
                    return 50
                else:
                    return -(self.y - bdf.y) // BDFSPEED
