"""Stratégie d'exemple : un joueur qui gagne."""

from entities import Fireball
from fractions import Fraction
from gamegrid import Tile
from typing import List, Optional
from game import Action, Game, Player

ALL_MOVES = (
    Action.MOVE_UP,
    Action.MOVE_DOWN,
    Action.MOVE_LEFT,
    Action.MOVE_RIGHT,
)

FIREBALL_SPEED = Fraction(1, Fireball.INITIAL_SPEED)


class LePireJoueur(Player):
    """Stratégie qui gagne."""

    NAME = "1 - LePireJoueur"

    def play(self, game: Game) -> Action:
        """Choisit la meilleure action possible dans la situation donnée en paramètre."""
        attack_matrix = self.attack_matrix(game)

        if attack_matrix[self.y][self.x] is not None and self.is_action_valid(
            attack_matrix[self.y][self.x][0]
        ):
            return attack_matrix[self.y][self.x][0]

        interesting_paths = self.list_interesting_paths(game)

        if len(interesting_paths) == 0:
            return Action.WAIT

        best_t = interesting_paths[0][4]
        best_moves = interesting_paths[0][3]
        for (_, _, _, moves, t) in interesting_paths:
            if t < best_t:
                best_t = t
                best_moves = moves

        if self.is_action_valid(best_moves[0]):
            return best_moves[0]

        return Action.WAIT

    def attack_matrix(self, game: Game) -> List[List[Optional[Action]]]:
        """Renvoie une liste des directions d'attaque."""
        matrix = [[None for _ in range(game.size)] for _ in range(game.size)]

        for player in filter(
            lambda e: e.TILE.is_player() and e.color != self.color,
            game.entities,
        ):
            for a in ALL_MOVES:
                (x, y) = a.apply((player.x, player.y))
                t = FIREBALL_SPEED
                while game.background[y][x] != Tile.WALL:
                    if matrix[y][x] is None or matrix[y][x][1] > t:
                        matrix[y][x] = (a.swap().to_attack(), t)
                    (x, y) = a.apply((x, y))
                    t += FIREBALL_SPEED

        return matrix

    def list_interesting_paths(self, game: Game) -> list:
        """Renvoie la liste des chemins se terminant par un item."""
        time_matrix = [[None for _ in range(game.size)] for _ in range(game.size)]
        time_matrix[self.y][self.x] = Fraction(0)

        paths = [(self.x, self.y, [], Fraction(0))]
        interesting_paths = []

        def is_valid(x, y, a: Action):
            x, y = a.apply((x, y))
            return (
                game.background[y][x].is_floor()
                and not game.tile_grid[y][x].is_player()
            )

        # Tant que le parcours du graphe n'est pas fini
        while len(paths) > 0:

            # On défile un chemin
            x, y, moves, t = paths.pop()

            # Si la case est intéressante, on garde la liste des mouvements
            if game.tile_grid[y][x].is_bonus() or (
                game.tile_grid[y][x].is_player() and game.tile_grid[y][x] != self.color
            ):
                interesting_paths.append((game.tile_grid[y][x], x, y, moves, t))

            # On regarde les 4 noeuds adjacents pour savoir :
            #  - Si on peut s'y rendre
            #  - Si on a trouvé le chemin le plus court alors on remplace la valeur
            #    précédente
            for a in ALL_MOVES:

                # Le mouvement est valide
                if is_valid(x, y, a):

                    # Coordonnées, temps et liste des mouvements suivants
                    next_x, next_y = a.apply((x, y))
                    next_t = t + self.speed
                    next_moves = moves[:]
                    next_moves.append(a)

                    # On a trouvé plus court !
                    if (
                        time_matrix[next_y][next_x] is None
                        or time_matrix[next_y][next_x] > next_t
                    ):
                        time_matrix[next_y][next_x] = next_t
                        paths.append((next_x, next_y, next_moves, next_t))

        return interesting_paths
