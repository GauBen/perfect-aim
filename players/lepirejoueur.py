"""Stratégie d'exemple : un joueur qui gagne."""

from entities import Fireball
from fractions import Fraction
from gamegrid import Tile
from typing import List, Optional, Tuple
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
        time_grid = self.time_grid(game)
        attack_grid = self.attack_grid(game)
        danger_grid = self.danger_grid(game)

        best_action = Action.WAIT
        best_value = self.compute_value(
            Action.WAIT, time_grid, attack_grid, danger_grid
        )
        for a in list(Action):
            if a == Action.WAIT:
                continue
            if self.is_action_valid(a):
                value = self.compute_value(a, time_grid, attack_grid, danger_grid)
                if value > best_value:
                    best_value = value
                    best_action = a

        return best_action

    def compute_value(
        self,
        a: Action,
        time_grid: List[List[Optional[Tuple[Fraction, List[Action]]]]],
        attack_grid: List[List[Optional[Tuple[Action, Fraction]]]],
        danger_grid: List[List[Optional[Fraction]]],
    ) -> float:
        """Calcule la valeur d'une action."""
        value = 1.0
        if a.is_attack():
            if attack_grid[self.y][self.x] is not None:
                value *= 100 * 1 / attack_grid[self.y][self.x]
        return value

    def nothing(self, game):
        """Todo."""
        attack_matrix = self.attack_grid(game)
        danger_matrix = self.danger_grid(game)

        if danger_matrix[self.y][self.x] is not None:
            danger = danger_matrix[self.y][self.x]
            best_action = Action.WAIT
            for a in ALL_MOVES:
                if self.is_action_valid(a):
                    (x, y) = a.apply((self.x, self.y))
                    if danger_matrix[y][x] is None or danger_matrix[y][x] < danger:
                        best_action = a
                        danger = danger_matrix[y][x]
                        if danger_matrix[y][x] is None:
                            break
            if best_action != Action.WAIT:
                return best_action

        if attack_matrix[self.y][self.x] is not None and self.is_action_valid(
            attack_matrix[self.y][self.x][0]
        ):
            return attack_matrix[self.y][self.x][0]

        interesting_paths = self.time_grid(game)

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

    def attack_grid(self, game: Game) -> List[List[Optional[Tuple[Action, Fraction]]]]:
        """Renvoie une liste des directions d'attaque."""
        matrix = [[None for _ in range(game.size)] for _ in range(game.size)]

        for player in filter(
            lambda e: e.TILE.is_player() and e.color != self.color, game.entities
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

    def danger_grid(self, game: Game) -> List[List[Optional[Fraction]]]:
        """Renvoie une liste des directions d'attaque."""
        matrix = [[None for _ in range(game.size)] for _ in range(game.size)]

        for fireball in filter(lambda e: e.TILE == Tile.FIREBALL, game.entities):
            (x, y) = (fireball.x, fireball.y)
            matrix[y][x] = Fraction(0)
            t = FIREBALL_SPEED
            (x, y) = fireball.action.apply((x, y))
            while game.background[y][x] != Tile.WALL:
                if matrix[y][x] is None or matrix[y][x] > t:
                    matrix[y][x] = t
                (x, y) = fireball.action.apply((x, y))
                t += FIREBALL_SPEED

        return matrix

    def time_grid(
        self, game: Game
    ) -> List[List[Optional[Tuple[Fraction, List[Action]]]]]:
        """Renvoie la liste des chemins se terminant par un item."""
        time_grid = [[None for _ in range(game.size)] for _ in range(game.size)]
        time_grid[self.y][self.x] = (Fraction(0), [])

        paths = [(self.x, self.y, [], Fraction(0), self.speed)]

        def is_valid(x, y, a: Action):
            x, y = a.apply((x, y))
            return (
                game.background[y][x].is_floor()
                and not game.tile_grid[y][x].is_player()
            )

        # Tant que le parcours du graphe n'est pas fini
        while len(paths) > 0:

            # On défile un chemin
            x, y, moves, t, speed = paths.pop()

            if any(e.TILE == Tile.SPEEDBOOST for e in game.entity_grid[y][x]):
                speed = Fraction(speed) + Fraction(1, 4)
            elif any(
                e.TILE == Tile.SPEEDPENALTY for e in game.entity_grid[y][x]
            ) and speed >= Fraction(3, 4):
                speed = Fraction(speed) - Fraction(1, 4)

            # On regarde les 4 noeuds adjacents pour savoir :
            #  - Si on peut s'y rendre
            #  - Si on a trouvé le chemin le plus court alors on remplace la valeur
            #    précédente
            for a in ALL_MOVES:

                # Le mouvement est valide
                if is_valid(x, y, a):

                    # Coordonnées, temps et liste des mouvements suivants
                    next_x, next_y = a.apply((x, y))
                    next_t = t + Fraction(1, speed)
                    next_moves = moves[:]
                    next_moves.append(a)

                    # On a trouvé plus court !
                    if (
                        time_grid[next_y][next_x] is None
                        or time_grid[next_y][next_x][0] > next_t
                    ):
                        time_grid[next_y][next_x] = (next_t, next_moves)
                        paths.append((next_x, next_y, next_moves, next_t, speed))

        return time_grid
