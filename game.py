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
    CollectableEntity,
    Player,
    SpeedBoost,
    move,
    place_arrow,
    SpeedPenalty,
)
from map import (
    ARROW,
    EMPTY,
    PLAYER_BLUE,
    PLAYER_GREEN,
    PLAYER_RED,
    PLAYER_YELLOW,
    WALL,
    Map,
)

from random import randrange


class Game:
    """
    Représente une partie de Perfect Aim, commançant avec 2-4 joueurs, et se terminant quand il n'en reste qu'un.
    """

    def __init__(self, players):
        """
        Initialise une partie de 4 joueurs et crée une carte.
        """
        self.map = Map()
        self.players = set()
        coords = [
            (self.map.size - 2, 1),
            (1, self.map.size - 2),
            (self.map.size - 2, self.map.size - 2),
            (1, 1),
        ]
        colors = [PLAYER_GREEN, PLAYER_YELLOW, PLAYER_BLUE, PLAYER_RED]
        for player in players:
            x, y = coords.pop()
            self.players.add(player(x, y, 1.0, colors.pop()))
        self.arrows: set[Arrow] = set()
        self.collectibles: set[CollectableEntity] = {
            SpeedBoost(self.map.size // 2 - 1, self.map.size // 2 - 1)
        }
        self.t = 0
        self.over = False
        self.winner = None
        self.grid = deepcopy(self.map.grid)
        self.entity_grid = [
            [set() for x in range(self.map.size)] for y in range(self.map.size)
        ]
        for entity in self.collectibles | self.players | self.arrows:
            self.grid[entity.y][entity.x] = entity.grid_id
            self.entity_grid[entity.y][entity.x].add(entity)
        self.update(0.0)

    def update(self, elapsed_time: float):
        """
        Calcule toutes les updates du jeu qui ont eu lieu en `elapsed_time` secondes.
        """

        # Si la partie est finie, pas besoin d'update
        if self.over:
            return

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

            old_x, old_y = player.x, player.y
            player.update(self, dt)

            # Une mise à jour des coordonnées entraine une mise à jour de la grille
            if player.x != old_x or player.y != old_y:
                self.entity_grid[old_y][old_x].remove(player)
                self.entity_grid[player.y][player.x].add(player)

            # Un item à ramasser ?
            for entity in self.entity_grid[player.y][player.x].copy():
                if isinstance(entity, CollectableEntity):
                    entity.collect(self, player)
                    self.collectibles.remove(entity)
                    self.entity_grid[player.y][player.x].remove(entity)

            self.update_grid(player.x, player.y)
            if player.x != old_x or player.y != old_y:
                self.update_grid(old_x, old_y)

        # Mise à jour des flèches
        for arrow in self.arrows.copy():

            old_x, old_y = arrow.x, arrow.y
            arrow.update(self, dt)

            # Une mise à jour des coordonnées entraine une mise à jour de la grille
            if arrow.x != old_x or arrow.y != old_y:
                self.entity_grid[old_y][old_x].remove(arrow)
                self.entity_grid[arrow.y][arrow.x].add(arrow)

            # Suppression de la flèche si elle tape un mur
            if self.grid[arrow.y][arrow.x] == WALL:
                self.arrows.remove(arrow)
                self.entity_grid[arrow.y][arrow.x].remove(arrow)

            # Suppression des joueurs transpercés par la flèche
            for entity in self.entity_grid[arrow.y][arrow.x].copy():
                if isinstance(entity, Player):
                    print(f"Joueur {entity.color} éliminé par {arrow.player.color}")
                    self.players.remove(entity)
                    self.entity_grid[arrow.y][arrow.x].remove(entity)

            self.update_grid(arrow.x, arrow.y)
            if arrow.x != old_x or arrow.y != old_y:
                self.update_grid(old_x, old_y)

        # Il ne reste qu'un joueur en vie ?
        if len(self.players) == 1:
            winner = list(self.players)[0]
            print(f"Victoire du joueur {winner.color}")
            self.over = True
            self.winner = winner

        # Génération des items
        if (
            len(list(filter(lambda e: isinstance(e, SpeedBoost), self.collectibles)))
            == 0
        ):
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] == EMPTY:
                    collectible = SpeedBoost(x, y)
                    self.collectibles.add(collectible)
                    self.grid[y][x] = collectible.grid_id
                    self.entity_grid[y][x].add(collectible)
                    break
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] == EMPTY:
                    collectible = SpeedPenalty(x, y)
                    self.collectibles.add(collectible)
                    self.grid[y][x] = collectible.grid_id
                    self.entity_grid[y][x].add(collectible)
                    break

        # Si dt < elapsed_time, il reste des updates à traiter
        if elapsed_time - dt > 0:
            self.update(elapsed_time - dt)

    def update_grid(self, x, y):
        if len(self.entity_grid[y][x]) == 0:
            self.grid[y][x] = self.map.grid[y][x]
        else:
            self.grid[y][x] = max(entity.grid_id for entity in self.entity_grid[y][x])

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
            if not self.can_player_attack(player):
                return False
            x, y, _ = place_arrow((player.x, player.y), action)
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
        arrow = Arrow(x, y, direction, player)
        self.arrows.add(arrow)
        self.entity_grid[arrow.y][arrow.x].add(arrow)

    def can_player_attack(self, player):
        """
        Renvoie `True` si le joueur a une flèche disponible.
        """
        return not any(arrow.player == player for arrow in self.arrows)
