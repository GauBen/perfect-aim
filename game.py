"""Classes du jeu, sans interface."""

from __future__ import annotations

from copy import copy, deepcopy
from random import randrange
from time import perf_counter
from typing import Dict, List, Optional, Set, Type, Union

import entities
from gamegrid import Grid, Tile

Action = entities.Action


class CantMoveThereException(Exception):
    """Exception lancée quand un joueur ne peut pas se rendre sur une case."""


class Player:
    """Représente la stratégie d'une équipe."""

    NAME = "Donne-moi un nom !"

    def __init__(self):
        """Représente la stratégie d'une équipe."""
        self.game: Optional[Game] = None
        self.player_entity: Optional[entities.PlayerEntity] = None

    def next_action(self, game: Game, player_entity: entities.PlayerEntity):
        """Renvoie l'action suivante du joueur."""
        self.game = game
        self.player_entity = player_entity
        t = perf_counter()
        action = self.play(game)
        dt = perf_counter() - t
        if dt >= 0.010:
            print(f"/!\\ Temps de 10 ms dépassé pour {self.NAME} : {dt} s")
        return action

    def play(self, game: Game) -> Action:
        """Choisit la prochaine action du joueur, en renvoyant une constante d'action."""
        return Action.WAIT

    def is_action_valid(self, action: Action) -> bool:
        """Vérifie qu'une action est valide."""
        return self.game.is_action_valid(self, action)

    @property
    def x(self) -> int:
        """Coordonnée x du joueur."""
        return self.player_entity.x

    @property
    def y(self) -> int:
        """Coordonnée y du joueur."""
        return self.player_entity.y

    @property
    def speed(self) -> float:
        """Vitesse du joueur."""
        return self.player_entity.speed

    @property
    def coins(self) -> int:
        """Nombre de pièces du joueur."""
        return self.player_entity.coins

    @property
    def super_fireballs(self) -> int:
        """Nombre de super boules de feu."""
        return self.player_entity.super_fireballs

    @property
    def shield(self) -> bool:
        """Le joueur possède un bouclier."""
        return self.player_entity.shield

    @property
    def action(self) -> Action:
        """Action en cours."""
        return self.player_entity.action

    @property
    def action_progress(self) -> Action:
        """Avancement de l'action en cours."""
        return self.player_entity.action_progress

    @property
    def color(self) -> Tile:
        """Couleur du joueur."""
        return self.player_entity.color


class Game:
    """
    Représente une partie de Perfect Aim.

    Elle commence avec 2-4 joueurs, et se termine quand il n'en reste qu'un.
    """

    MIN_PLAYERS = 2
    MAX_PLAYERS = 4

    DEFAULT_GRID_SIZE = 21
    LAVA_FLOOD_START_TIME = 65.0
    LAVA_STEP_DURATION = 5.0

    def __init__(
        self, player_constructors: List[Optional[Type[entities.PlayerEntity]]]
    ):
        """Initialise une partie et crée une carte."""
        # Initialisation de la grille
        self.size = self.DEFAULT_GRID_SIZE
        self.tile_grid = Grid.create_grid(self.size)

        # L'état du jeu
        self.t = 0.0
        self.over = False
        self.winner: Optional[entities.PlayerEntity] = None

        # Les entités du jeu
        self.entities: Set[entities.Entity] = set()
        self.players: Dict[Tile, Player] = {}

        # Les matrices du jeu
        self.background = deepcopy(self.tile_grid)
        self.entity_grid: List[List[Set[entities.Entity]]] = [
            [set() for x in range(self.size)] for y in range(self.size)
        ]

        # Crée les joueurs et des objets
        self.create_entities(player_constructors)

    def __deepcopy__(self, memo: Dict[int, object]):
        """Assure une copie profonde efficace de l'objet."""
        clone: Game = self.__class__.__new__(self.__class__)

        # Propriétés simples
        clone.over = self.over
        clone.size = self.size
        clone.t = self.t
        clone.winner = None

        # Objets profonds
        clone.players = self.players
        clone.background = [[tile for tile in row] for row in self.background]
        clone.tile_grid = [[tile for tile in row] for row in self.tile_grid]
        clone.entity_grid = [
            [set() for _ in range(clone.size)] for _ in range(clone.size)
        ]
        clone.entities = set()
        for entity in self.entities:
            e = copy(entity)
            clone.entities.add(e)
            clone.entity_grid[e.y][e.x].add(e)
            if entity == self.winner:
                clone.winner = e

        return clone

    @property
    def player_entities(self) -> List[entities.PlayerEntity]:
        """Les `PlayerEntities` encore en vie."""
        return sorted(
            filter(lambda e: isinstance(e, entities.PlayerEntity), self.entities),
            key=lambda player: player.color,
        )

    def create_entities(self, player_constructors: List[Optional[Type[Player]]]):
        """Ajoute les joueurs et les entitiés sur les grilles."""
        # Les joueurs
        for player_constructor, entity_constructor, coords in zip(
            player_constructors,
            entities.players,
            [
                (1, 1),
                (self.size - 2, self.size - 2),
                (self.size - 2, 1),
                (1, self.size - 2),
            ],
        ):
            x, y = coords
            if player_constructor is not None:
                p = entity_constructor(x, y)
                self.entities.add(p)
                self.players[p.color] = player_constructor()
                # On initialise le joueur, mais on ignore son action
                self.next_action(p)

        d = {
            Tile.COIN: entities.Coin,
            Tile.SPEEDBOOST: entities.SpeedBoost,
            Tile.SPEEDPENALTY: entities.SpeedPenalty,
            Tile.SUPER_FIREBALL: entities.SuperFireball,
            Tile.SHIELD: entities.Shield,
        }
        for y in range(self.size):
            for x in range(self.size):
                if self.tile_grid[y][x] in d:
                    self.entities.add(d[self.tile_grid[y][x]](x, y))
                    self.background[y][x] = Tile.FLOOR

        for entity in self.entities:
            self.entity_grid[entity.y][entity.x].add(entity)
            self.update_grid(entity.x, entity.y)

    def update(self, elapsed_time: float):
        """Calcule toutes les updates qui ont eu lieu en `elapsed_time` secondes."""
        # On applique les updates itérativement, car on a discrétisé le temps
        while elapsed_time > 0.0:

            # Si la partie est finie, pas besoin d'update
            if self.over:
                return

            # Temps jusqu'à la prochaine update
            dt = min(
                [
                    entity.time_before_next_update
                    for entity in self.entities
                    if isinstance(entity, entities.MovingEntity)
                ]
                + [elapsed_time, int(self.t + 1.0) - self.t]
            )
            # dt vaut la plus petite durée avant un évènement
            # (changement de case par exemple)

            # Mise à jour du terrain
            self.add_lava(dt)
            self.add_collectibles()

            self.t += dt

            # Mise à jour des entités
            for entity in self.entities.copy():
                if entity in self.entities and isinstance(
                    entity, entities.MovingEntity
                ):
                    entity.update(self, dt)
                self.update_grid(entity.x, entity.y)

            # Il ne reste qu'un joueur en vie ?
            player_entities = list(self.player_entities)
            if len(player_entities) == 1:
                winner = player_entities[0]
                self.over = True
                self.winner = winner
            elif len(player_entities) == 0:
                self.over = True

            # Si dt < elapsed_time, il reste des updates à traiter
            elapsed_time -= dt

    def update_grid(self, x: int, y: int):
        """Met à jour la grille aux coordonnées données."""
        if len(self.entity_grid[y][x]) == 0:
            self.tile_grid[y][x] = self.background[y][x]
        else:
            self.tile_grid[y][x] = max(entity.TILE for entity in self.entity_grid[y][x])

    def add_lava(self, dt: float):
        """Ajoute de la lave après un certain temps."""
        if self.t + dt >= self.LAVA_FLOOD_START_TIME and int(
            self.t / self.LAVA_STEP_DURATION
        ) < int((self.t + dt) / self.LAVA_STEP_DURATION):
            # Étape de l'inondation
            step = int(
                (self.t + dt - self.LAVA_FLOOD_START_TIME) / self.LAVA_STEP_DURATION
            )
            lava = step % 2 == 1
            ring = 1 + step // 2
            if ring >= self.size // 2:
                return

            for y in range(ring, self.size - ring):
                for x in range(ring, self.size - ring):
                    if (
                        ring < x < self.size - ring - 1
                        and ring < y < self.size - ring - 1
                    ):
                        continue
                    if lava and self.background[y][x] == Tile.DAMAGED_FLOOR:
                        self.background[y][x] = Tile.LAVA
                        for entity in self.entity_grid[y][x].copy():
                            if not isinstance(entity, entities.Fireball):
                                self.remove_entity(entity)
                        self.update_grid(x, y)
                    elif not lava and self.background[y][x] == Tile.FLOOR:
                        self.background[y][x] = Tile.DAMAGED_FLOOR
                        self.update_grid(x, y)

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
                x, y = randrange(self.size), randrange(self.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.SpeedBoost(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.size), randrange(self.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.Shield(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.size), randrange(self.size)
                if self.tile_grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = entities.Coin(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break

    def move_entity(self, entity: entities.MovingEntity, old_x: int, old_y: int):
        """Déplace l'entité sur la grille des entités `entity_grid`."""
        self.entity_grid[old_y][old_x].remove(entity)
        self.entity_grid[entity.y][entity.x].add(entity)
        self.update_grid(old_x, old_y)

    def remove_entity(self, entity: entities.Entity):
        """Supprime l'entité du jeu."""
        if entity in self.entities:
            self.entities.remove(entity)
            self.entity_grid[entity.y][entity.x].remove(entity)
        self.update_grid(entity.x, entity.y)

    def next_action(self, entity: entities.PlayerEntity) -> Action:
        """Renvoie la prochaine action du joueur."""
        clone = deepcopy(self)
        return self.players[entity.color].next_action(
            clone, clone.player_entity_from_color(entity.color)
        )

    def collect(self, player: Player, collectible: entities.CollectableEntity):
        """Ramasse l'object `collectible` pour le joueur `player`."""
        collectible.collect(player)
        self.entities.remove(collectible)
        self.entity_grid[collectible.y][collectible.x].remove(collectible)
        self.update_grid(collectible.x, collectible.y)

    def player_attacks(self, player: entities.PlayerEntity, action: Action):
        """Lance une boule de feu pour le joueur `player`."""

        def throw_fireball(action: entities.Action):
            fireball = entities.Fireball(
                player.x, player.y, action.to_movement(), player.color
            )
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

    def hit_player(
        self, fireball: entities.Fireball, player_entity: entities.PlayerEntity
    ):
        """Inflige un point de dégât."""
        if player_entity.shield:
            player_entity.shield = False
            self.remove_entity(fireball)
            self.update_grid(player_entity.x, player_entity.y)
        else:
            self.remove_entity(player_entity)

    def can_player_attack(self, player: Union[entities.PlayerEntity, Player]) -> bool:
        """Renvoie `True` si le joueur a une boule de feu disponible."""
        for entity in self.entities:
            if isinstance(entity, entities.Fireball) and entity.sender == player.color:
                return False
        return True

    def is_action_valid(
        self, player: Union[entities.PlayerEntity, Player], action: entities.Action
    ) -> bool:
        """Renvoie `True` si l'action `action` est jouable."""
        if isinstance(player, Player):
            return self.is_action_valid(player.player_entity, action)

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
            return player.super_fireballs > 0 or self.can_player_attack(player)

        # Dans le doute c'est pas possible
        return False

    def player_entity_from_color(self, color: Tile) -> entities.PlayerEntity:
        """Cherche l'entité associée à la couleur d'une joueur."""
        if not color.is_player():
            raise ValueError("L'argument n'est pas un joueur.")
        try:
            return next(
                entity
                for entity in self.entities
                if isinstance(entity, entities.PlayerEntity) and entity.color == color
            )
        except StopIteration:
            raise KeyError("Le joueur n'est plus dans le jeu.")


if __name__ == "__main__":
    print("Le lanceur du jeu est le fichier ./main.py")
