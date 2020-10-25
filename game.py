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
    MovingEntity,
)
from map import (
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
        self.t = 0
        self.over = False
        self.winner = None

        coords = [
            (self.map.size - 2, 1),
            (1, self.map.size - 2),
            (self.map.size - 2, self.map.size - 2),
            (1, 1),
        ]
        colors = [PLAYER_GREEN, PLAYER_YELLOW, PLAYER_BLUE, PLAYER_RED]
        self.grid = deepcopy(self.map.grid)
        self.entity_grid = [
            [set() for x in range(self.map.size)] for y in range(self.map.size)
        ]

        for player in players:
            x, y = coords.pop()
            self.players.add(player(x, y, 1.0, colors.pop()))

        self.arrows: set[Arrow] = set()
        self.collectibles: set[CollectableEntity] = {
            SpeedBoost(self.map.size // 2 - 1, self.map.size // 2 - 1)
        }

        for entity in self.collectibles | self.players | self.arrows:
            self.entity_grid[entity.y][entity.x].add(entity)
            self.update_grid(entity.x, entity.y)

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

        # Mise à jour des entités mobiles
        for entity in self.players | self.arrows:
            entity.update(self, dt)
            self.update_grid(entity.x, entity.y)

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
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] == EMPTY:
                    collectible = SpeedPenalty(x, y)
                    self.collectibles.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
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

        arrow.update(self, 0.0)

        self.update_grid(arrow.x, arrow.y)

    def can_player_attack(self, player: Player):
        """
        Renvoie `True` si le joueur a une flèche disponible.
        """
        return not any(arrow.player == player for arrow in self.arrows)

    def collect(self, player: Player, collectible: CollectableEntity):
        """
        Ramasse l'object `collectible` pour le joueur `player`.
        """
        collectible.collect(self, player)
        self.collectibles.remove(collectible)
        self.entity_grid[collectible.y][collectible.x].remove(collectible)

    def remove_arrow(self, arrow: Arrow):
        """
        Supprime une flèche.
        """
        self.arrows.remove(arrow)
        self.entity_grid[arrow.y][arrow.x].remove(arrow)

    def remove_player(self, player: Player):
        """
        Supprime un joueur.
        """
        self.players.remove(player)
        self.entity_grid[player.y][player.x].remove(player)

    def move_entity(self, entity: MovingEntity, old_x: int, old_y: int):
        """
        Déplace l'entité sur la grille des entités `entity_grid`.
        """
        self.entity_grid[old_y][old_x].remove(entity)
        self.entity_grid[entity.y][entity.x].add(entity)
        self.update_grid(old_x, old_y)
