"""Classes du jeu, sans interface."""

from copy import deepcopy
from typing import Callable, List, Optional, Set

import entities
from entities import (
    Action,
    Fireball,
    CantMoveThereException,
    CollectableEntity,
    Player,
    SpeedBoost,
    move,
    place_fireball,
    SpeedPenalty,
    MovingEntity,
    Coin,
    SuperFireball,
    Shield,
    Entity,
)
from gamegrid import Grid, Tile

from random import randrange


class Game:
    """
    Représente une partie de Perfect Aim.

    Elle commence avec 2-4 joueurs, et se termine quand il n'en reste qu'un.
    """

    MIN_PLAYERS = 2
    MAX_PLAYERS = 4

    def __init__(
        self, player_constructors: List[Optional[Callable[[], entities.Player]]]
    ):
        """Initialise une partie et crée une carte."""
        self.map = Grid()
        self.players: list[Player] = []
        self.t = 0.0
        self.over = False
        self.winner: Optional[Player] = None

        coords = [
            (self.map.size - 2, 1),
            (1, self.map.size - 2),
            (self.map.size - 2, self.map.size - 2),
            (1, 1),
        ]
        colors = [
            Tile.PLAYER_GREEN,
            Tile.PLAYER_YELLOW,
            Tile.PLAYER_BLUE,
            Tile.PLAYER_RED,
        ]
        self.background = deepcopy(self.map.grid)
        self.grid = deepcopy(self.map.grid)
        self.entities: Set[Entity] = set()
        self.entity_grid = [
            [set() for x in range(self.map.size)] for y in range(self.map.size)
        ]

        for player in player_constructors:
            x, y = coords.pop()
            p = player(x, y, 1.0, colors.pop())
            self.entities.add(p)
            self.players.append(p)

        for y in range(self.map.size):
            for x in range(self.map.size):
                if self.grid[y][x] == Tile.COIN:
                    self.entities.add(Coin(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.grid[y][x] == Tile.SPEEDBOOST:
                    self.entities.add(SpeedBoost(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.grid[y][x] == Tile.SPEEDPENALTY:
                    self.entities.add(SpeedPenalty(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.grid[y][x] == Tile.SUPER_FIREBALL:
                    self.entities.add(SuperFireball(x, y))
                    self.background[y][x] = Tile.FLOOR
                elif self.grid[y][x] == Tile.SHIELD:
                    self.entities.add(Shield(x, y))
                    self.background[y][x] = Tile.FLOOR

        for entity in self.entities:
            self.entity_grid[entity.y][entity.x].add(entity)
            self.update_grid(entity.x, entity.y)
            self.entities.add(entity)

        self.update(0.0)

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

            players = list(filter(lambda e: isinstance(e, Player), self.entities))

            # Il ne reste qu'un joueur en vie ?
            if len(players) == 1:
                winner = players[0]
                print(f"Victoire du joueur {winner.color}")
                self.over = True
                self.winner = winner
            elif len(players) == 0:
                print("Match nul")
                self.over = True
                # pass

            # Si dt < elapsed_time, il reste des updates à traiter
            elapsed_time -= dt

    def add_collectibles(self):
        """Ajoute des objets s'il n'y en a plus."""
        if len(list(filter(lambda e: isinstance(e, SpeedBoost), self.entities))) == 0:
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = SpeedBoost(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = Shield(x, y)
                    self.entities.add(collectible)
                    self.entity_grid[y][x].add(collectible)
                    self.update_grid(collectible.x, collectible.y)
                    break
            for _ in range(10):
                x, y = randrange(self.map.size), randrange(self.map.size)
                if self.grid[y][x] in (Tile.FLOOR, Tile.DAMAGED_FLOOR):
                    collectible = Coin(x, y)
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
                for y in range(self.map.size):
                    for x in range(self.map.size):
                        if (
                            x == coords
                            or y == coords
                            or x == self.map.size - coords - 1
                            or y == self.map.size - coords - 1
                        ) and self.background[y][x] == from_:
                            if to == Tile.LAVA:
                                self.turn_to_lava(x, y)
                            else:
                                self.background[y][x] = to
                                self.update_grid(x, y)

    def update_grid(self, x, y):
        """Met à jour la grille aux coordonnées données."""
        if len(self.entity_grid[y][x]) == 0:
            self.grid[y][x] = self.background[y][x]
        else:
            self.grid[y][x] = max(entity.grid_id for entity in self.entity_grid[y][x])

    def is_valid_action(self, player: Player, action):
        """Renvoie `True` si l'action `action` est jouable."""
        if action == Action.WAIT:
            return True

        # Un déplacement est possible s'il n'y a ni mur ni joueur
        elif action in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        ):
            x, y = move((player.x, player.y), action)
            try:
                if self.grid[y][x] in (
                    Tile.WALL,
                    Tile.PLAYER_RED,
                    Tile.PLAYER_BLUE,
                    Tile.PLAYER_YELLOW,
                    Tile.PLAYER_GREEN,
                ):
                    raise CantMoveThereException()
            except IndexError:
                return False
            except CantMoveThereException:
                return False
            return True

        # Un tir d'arc est possible s'il n'est pas fait contre un mur
        elif action in (
            Action.ATTACK_UP,
            Action.ATTACK_DOWN,
            Action.ATTACK_LEFT,
            Action.ATTACK_RIGHT,
        ):
            if not self.can_player_attack(player):
                return False
            if player.super_fireball > 0:
                return True
            return self.can_place_fireball(player, action)

        # Dans le doute c'est pas possible
        return False

    def can_place_fireball(self, player: Player, action):
        """Renvoie `True` si le joueur peut placer une boule de feu."""
        x, y, _ = place_fireball((player.x, player.y), action)
        try:
            if self.grid[y][x] == Tile.WALL:
                raise CantMoveThereException()
        except IndexError:
            return False
        except CantMoveThereException:
            return False
        return True

    def player_attacks(self, player: Player, action):
        """Lance une boule de feu pour le joueur `player`."""

        def throw_fireball(action):
            x, y, direction = place_fireball((player.x, player.y), action)
            fireball = Fireball(x, y, direction, player)
            self.entities.add(fireball)
            self.entity_grid[fireball.y][fireball.x].add(fireball)
            self.update_grid(fireball.x, fireball.y)

        if player.super_fireball > 0:
            for action in (
                Action.ATTACK_UP,
                Action.ATTACK_DOWN,
                Action.ATTACK_LEFT,
                Action.ATTACK_RIGHT,
            ):
                if self.can_place_fireball(player, action):
                    throw_fireball(action)
            player.super_fireball -= 1

        else:
            throw_fireball(action)

    def can_player_attack(self, player: Player):
        """Renvoie `True` si le joueur a une boule de feu disponible."""
        for entity in self.entities:
            if isinstance(entity, Fireball) and entity.player == player:
                return False
        return True

    def collect(self, player: Player, collectible: CollectableEntity):
        """Ramasse l'object `collectible` pour le joueur `player`."""
        collectible.collect(self, player)
        self.entities.remove(collectible)
        self.entity_grid[collectible.y][collectible.x].remove(collectible)
        self.update_grid(collectible.x, collectible.y)

    def hit_player(self, fireball: Fireball, player: Player):
        """Inflige un point de dégât."""
        if player.shield:
            player.shield = False
            self.remove_entity(fireball)
            self.update_grid(player.x, player.y)
        else:
            self.remove_entity(player)

    def remove_entity(self, entity: Entity):
        """Supprime l'entité du jeu."""
        if entity in self.entities:
            self.entities.remove(entity)
            self.entity_grid[entity.y][entity.x].remove(entity)
        self.update_grid(entity.x, entity.y)

    def move_entity(self, entity: MovingEntity, old_x: int, old_y: int):
        """Déplace l'entité sur la grille des entités `entity_grid`."""
        self.entity_grid[old_y][old_x].remove(entity)
        self.entity_grid[entity.y][entity.x].add(entity)
        self.update_grid(old_x, old_y)

    def turn_to_lava(self, x, y):
        """Transforme une case en lave."""
        self.background[y][x] = Tile.LAVA
        for entity in self.entity_grid[y][x].copy():
            if not isinstance(entity, Fireball):
                self.remove_entity(entity)
        self.update_grid(x, y)
