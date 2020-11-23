"""Classes du jeu, sans interface."""

from copy import deepcopy
from typing import List, Optional, Set, Type, Union

import entities
from gamegrid import Grid, Tile

from random import randrange

Action = entities.Action


class CantMoveThereException(Exception):
    """Exception lancée quand un joueur ne peut pas se rendre sur une case."""


class Player:
    """Représente la stratégie d'une équipe."""

    NAME = "Donne-moi un nom !"

    def __init__(self, entity: entities.PlayerEntity):
        """Représente la stratégie d'une équipe."""
        self._player_entity = entity

    def play(self, game) -> Action:
        """Choisit la prochaine action du joueur, en renvoyant une constante d'action."""
        return Action.WAIT

    @property
    def x(self) -> int:
        """Coordonnée x du joueur."""
        return self._player_entity.x

    @property
    def y(self) -> int:
        """Coordonnée y du joueur."""
        return self._player_entity.y

    @property
    def speed(self) -> float:
        """Vitesse du joueur."""
        return self._player_entity.speed

    @property
    def coins(self) -> int:
        """Nombre de pièces du joueur."""
        return self._player_entity.coins

    @property
    def super_fireballs(self) -> int:
        """Nombre de super boules de feu."""
        return self._player_entity.super_fireballs

    @property
    def shield(self) -> bool:
        """Le joueur possède un bouclier."""
        return self._player_entity.shield

    @property
    def action(self) -> Action:
        """Action en cours."""
        return self._player_entity.action

    @property
    def action_progress(self) -> Action:
        """Avancement de l'action en cours."""
        return self._player_entity.action_progress

    @property
    def color(self) -> Tile:
        """Couleur du joueur."""
        return self._player_entity.TILE


class Game:
    """
    Représente une partie de Perfect Aim.

    Elle commence avec 2-4 joueurs, et se termine quand il n'en reste qu'un.
    """

    MIN_PLAYERS = 2
    MAX_PLAYERS = 4

    def __init__(
        self, player_constructors: List[Optional[Type[entities.PlayerEntity]]]
    ):
        """Initialise une partie et crée une carte."""
        # Initialisation de la grille
        self.grid = Grid()

        # Les entités du jeu
        self.entities: Set[entities.Entity] = set()
        self.players: list[Player] = []

        # Les matrices du jeu
        self.background = deepcopy(self.grid.grid)
        self.tile_grid = deepcopy(self.grid.grid)
        self.entity_grid: List[List[Set[entities.Entity]]] = [
            [set() for x in range(self.grid.size)] for y in range(self.grid.size)
        ]

        # L'état du jeu
        self.t = 0.0
        self.over = False
        self.winner: Optional[Player] = None

        # Crée les joueurs et des objets
        self.create_entities(player_constructors)

    def create_entities(
        self, player_constructors: List[Optional[Type[entities.PlayerEntity]]]
    ):
        """Ajoute les joueurs et les entitiés sur les grilles."""
        # Les joueurs
        for player_constructor, entity_constructor, coords in zip(
            player_constructors,
            entities.players,
            [
                (1, 1),
                (self.grid.size - 2, self.grid.size - 2),
                (1, self.grid.size - 2),
                (self.grid.size - 2, 1),
            ],
        ):
            x, y = coords
            if player_constructor is not None:
                p = entity_constructor(x, y)
                self.entities.add(p)
                self.players.append(player_constructor(p))

        for y in range(self.grid.size):
            for x in range(self.grid.size):
                if self.tile_grid[y][x] == Tile.COIN:
                    self.entities.add(entities.Coin(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.tile_grid[y][x] == Tile.SPEEDBOOST:
                    self.entities.add(entities.SpeedBoost(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.tile_grid[y][x] == Tile.SPEEDPENALTY:
                    self.entities.add(entities.SpeedPenalty(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.tile_grid[y][x] == Tile.SUPER_FIREBALL:
                    self.entities.add(entities.SuperFireball(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.tile_grid[y][x] == Tile.SHIELD:
                    self.entities.add(entities.Shield(x, y))
                    self.background[y][x] = Tile.FLOOR

        for entity in self.entities:
            self.entity_grid[entity.y][entity.x].add(entity)
            self.update_grid(entity.x, entity.y)
            self.entities.add(entity)

    def update(self, elapsed_time: float):
        """Calcule toutes les updates qui ont eu lieu en `elapsed_time` secondes."""
        # On applique les updates itérativement, car on a discrétisé le temps
        while elapsed_time > 0.0:

            # Si la partie est finie, pas besoin d'update
            if self.over:
                return

            # Génération du terrain
            self.add_lava()
            self.add_collectibles()

            # Temps jusqu'à la prochaine update
            dt = min(
                [entity.next_update_in(elapsed_time) for entity in self.entities]
                + [elapsed_time]
            )
            # dt vaut la plus petite durée avant un évènement
            # (changement de case par exemple)
            self.t += dt

            # Mise à jour des entités
            for entity in self.entities.copy():
                if entity in self.entities:
                    entity.update(self, dt)
                self.update_grid(entity.x, entity.y)

            # Il ne reste qu'un joueur en vie ?
            player_entities = list(self.player_entities)
            if len(player_entities) == 1:
                winner = player_entities[0]
                print(f"Victoire du joueur {winner.TILE.name}")
                self.over = True
                self.winner = winner
            elif len(player_entities) == 0:
                print("Match nul")
                self.over = True

            # Si dt < elapsed_time, il reste des updates à traiter
            elapsed_time -= dt

    def add_collectibles(self):
        """Ajoute des objets s'il n'y en a plus."""
        if (
            len(
                list(
                    filter(lambda e: isinstance(e, entities.SpeedBoost), self.entities)
                )
            )
            == 0
        ):
            for _ in range(10):
                x, y = randrange(self.grid.size), randrange(self.grid.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.SpeedBoost(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.grid.size), randrange(self.grid.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.Shield(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.grid.size), randrange(self.grid.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.Coin(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break

    def add_lava(self):
        """Ajoute de la lave après un certain temps."""
        if self.t >= 65.0:
            step = int((self.t - 65.0) / 10.0)
            halfstep = (self.t - 65.0 - step * 10.0) > 5.0
            coords = 1 + step
            from_ = Tile.DAMAGED_FLOOR if halfstep else Tile.FLOOR
            to = Tile.LAVA if halfstep else Tile.DAMAGED_FLOOR
            if self.background[coords][coords] != to:
                for y in range(self.grid.size):
                    for x in range(self.grid.size):
                        if (
                            x == coords
                            or y == coords
                            or x == self.grid.size - coords - 1
                            or y == self.grid.size - coords - 1
                        ) and self.background[y][x] == from_:
                            if to == Tile.LAVA:
                                self.turn_to_lava(x, y)
                            else:
                                self.background[y][x] = to
                                self.update_grid(x, y)

    def update_grid(self, x, y):
        """Met à jour la grille aux coordonnées données."""
        if len(self.entity_grid[y][x]) == 0:
            self.tile_grid[y][x] = self.background[y][x]
        else:
            self.tile_grid[y][x] = max(entity.TILE for entity in self.entity_grid[y][x])

    def is_valid_action(
        self, player: Union[entities.PlayerEntity, Player], action: entities.Action
    ):
        """Renvoie `True` si l'action `action` est jouable."""
        if isinstance(player, Player):
            return self.is_valid_action(player._player_entity, action)

        if action == Action.WAIT:
            return True

        # Un déplacement est possible s'il n'y a ni mur ni joueur
        elif action.is_movement():
            x, y = action.apply((player.x, player.y))
            try:
                if self.background[y][x] == Tile.WALL or any(
                    isinstance(e, entities.PlayerEntity) for e in self.entity_grid[y][x]
                ):
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True

        # Un tir d'arc est possible s'il n'est pas fait contre un mur
        elif action.is_attack():
            if player.super_fireballs > 0:
                return True
            if not self.can_player_attack(player):
                return False
            return True

        # Dans le doute c'est pas possible
        return False

    def player_attacks(self, player: entities.PlayerEntity, action):
        """Lance une boule de feu pour le joueur `player`."""

        def throw_fireball(action: entities.Action):
            fireball = entities.Fireball(player.x, player.y, action.attack, player)
            self.entities.add(fireball)
            self.entity_grid[fireball.y][fireball.x].add(fireball)
            self.update_grid(fireball.x, fireball.y)

        if player.super_fireballs > 0:
            for action in (
                Action.ATTACK_UP,
                Action.ATTACK_DOWN,
                Action.ATTACK_LEFT,
                Action.ATTACK_RIGHT,
            ):
                throw_fireball(action)
            player.super_fireballs -= 1

        else:
            throw_fireball(action)

    def can_player_attack(self, player: Player):
        """Renvoie `True` si le joueur a une boule de feu disponible."""
        for entity in self.entities:
            if isinstance(entity, entities.Fireball) and entity.player == player:
                return False
        return True

    def collect(self, player: Player, collectible: entities.CollectableEntity):
        """Ramasse l'object `collectible` pour le joueur `player`."""
        collectible.collect(player)
        self.entities.remove(collectible)
        self.entity_grid[collectible.y][collectible.x].remove(collectible)
        self.update_grid(collectible.x, collectible.y)

    def hit_player(self, fireball: entities.Fireball, player: Player):
        """Inflige un point de dégât."""
        if player.shield:
            player.shield = False
            self.remove_entity(fireball)
            self.update_grid(player.x, player.y)
        else:
            self.remove_entity(player)

    def remove_entity(self, entity: entities.Entity):
        """Supprime l'entité du jeu."""
        if entity in self.entities:
            self.entities.remove(entity)
            self.entity_grid[entity.y][entity.x].remove(entity)
        self.update_grid(entity.x, entity.y)

    def move_entity(self, entity: entities.MovingEntity, old_x: int, old_y: int):
        """Déplace l'entité sur la grille des entités `entity_grid`."""
        self.entity_grid[old_y][old_x].remove(entity)
        self.entity_grid[entity.y][entity.x].add(entity)
        self.update_grid(old_x, old_y)

    def turn_to_lava(self, x, y):
        """Transforme une case en lave."""
        self.background[y][x] = Tile.LAVA
        for entity in self.entity_grid[y][x].copy():
            if not isinstance(entity, entities.Fireball):
                self.remove_entity(entity)
        self.update_grid(x, y)

    def next_action(self, entity: entities.PlayerEntity) -> Action:
        """La prochaine action de l'entité."""
        for player in self.players:
            if player._player_entity is entity:
                return player.play(self)
        raise KeyError("Le joueur n'existe plus")

    @property
    def player_entities(self) -> List[entities.PlayerEntity]:
        """Les `PlayerEntities` encore en vie."""
        return filter(lambda e: isinstance(e, entities.PlayerEntity), self.entities)
