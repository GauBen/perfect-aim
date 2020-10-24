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
    Arrow,
    CantMoveThereException,
    Player,
    move,
    place_arrow,
)
from map import ARROW, PLAYER_BLUE, PLAYER_GREEN, PLAYER_RED, PLAYER_YELLOW, WALL, Map


class Game:
    """
    Représente une partie de Perfect Aim, commançant avec 2-4 joueurs, et se terminant quand il n'en reste qu'un.
    """

    def __init__(self):
        """
        Initialise une partie de 4 joueurs et crée une carte.
        """
        self.map = Map()
        self.players = {
            Player(1, 1, 1.0, PLAYER_RED),
            Player(self.map.size - 2, self.map.size - 2, 1.5, PLAYER_BLUE),
            Player(1, self.map.size - 2, 1, PLAYER_GREEN),
            Player(self.map.size - 2, 1, 1, PLAYER_YELLOW),
        }
        self.arrows: set[Arrow] = set()
        self.t = 0
        self.update_grid()

    def update(self, elapsed_time: float):
        """
        Calcule toutes les updates du jeu qui ont eu lieu en `elapsed_time` secondes.
        """
        # Temps jusqu'à la prochaine update
        dt = min(
            [player.next_update_in(elapsed_time) for player in self.players]
            + [arrow.next_update_in(elapsed_time) for arrow in self.arrows]
            + [elapsed_time]
        )
        # dt vaut la plus petite durée avant un évènement (changement de case par exemple)
        self.t += dt

        # Mise à jour des joueurs
        for player in self.players:
            player.update(self, dt)
            self.update_grid()

            # Un item à ramasser ?

        for arrow in self.arrows.copy():
            arrow.update(self, dt)

            # Suppression de la flèche si elle tape un mur
            if self.grid[arrow.y][arrow.x] == WALL:
                self.arrows.remove(arrow)

            # Suppression des joueurs contre la flèche
            for player in self.players.copy():
                if player.x == arrow.x and player.y == arrow.y:
                    self.players.remove(player)

            self.update_grid()

        # Si dt < elapsed_time, il reste des updates à traiter
        if elapsed_time - dt > 0:
            self.update(elapsed_time - dt)

    def update_grid(self):
        """
        Crée une grille avec les murs, les joueurs, les flèches et les items.
        """
        self.grid = deepcopy(self.map.grid)

        for a in self.players:
            self.grid[a.y][a.x] = a.color

        for a in self.arrows.copy():
            self.grid[a.y][a.x] = ARROW

    def is_valid_action(self, player, action):
        """
        Renvoie `True` si l'action `action` est jouable par le joueur `player`.
        """
        if action == WAIT:
            return True

        # Un déplacement est possible s'il n'y a ni mur ni joueur
        elif action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
            x, y = move((player.x, player.y), action)
            try:
                if self.grid[y][x] in (
                    WALL,
                    PLAYER_RED,
                    PLAYER_BLUE,
                    PLAYER_YELLOW,
                    PLAYER_GREEN,
                ):
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True

        # Un tir d'arc est possible s'il n'est pas fait contre un mur
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

        # Dans le doute c'est pas possible
        return False

    def player_attacks(self, player, action):
        """
        Lance une flèche pour le joueur `player`.
        """
        x, y, direction = place_arrow((player.x, player.y), action)
        arrow = Arrow(x, y, direction)
        self.arrows.add(arrow)
