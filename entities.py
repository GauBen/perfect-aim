"""Les entités du jeu."""
from enum import Enum
from typing import List, Tuple, Type

from gamegrid import Tile


class Action(Enum):
    """Toutes les actions possibles d'un joueur."""

    WAIT = "Attente"
    MOVE_UP = "Mvt haut"
    MOVE_DOWN = "Mvt bas"
    MOVE_LEFT = "Mvt gauche"
    MOVE_RIGHT = "Mvt droit"
    ATTACK_UP = "Atk haut"
    ATTACK_DOWN = "Atk bas"
    ATTACK_LEFT = "Atk gauche"
    ATTACK_RIGHT = "Atk droite"

    def apply(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        """Applique le déplacement à la paire de coordonnées."""
        x, y = coords
        if self == Action.MOVE_UP:
            return x, y - 1
        if self == Action.MOVE_DOWN:
            return x, y + 1
        if self == Action.MOVE_LEFT:
            return x - 1, y
        if self == Action.MOVE_RIGHT:
            return x + 1, y
        return x, y

    def swap(self):
        """Donne la direction opposée de l'action."""
        if self == Action.MOVE_UP:
            return Action.MOVE_DOWN
        if self == Action.MOVE_DOWN:
            return Action.MOVE_UP
        if self == Action.MOVE_LEFT:
            return Action.MOVE_RIGHT
        if self == Action.MOVE_RIGHT:
            return Action.MOVE_LEFT
        if self == Action.ATTACK_UP:
            return Action.ATTACK_DOWN
        if self == Action.ATTACK_DOWN:
            return Action.ATTACK_UP
        if self == Action.ATTACK_LEFT:
            return Action.ATTACK_RIGHT
        if self == Action.ATTACK_RIGHT:
            return Action.ATTACK_LEFT
        return Action.WAIT

    def attack(self):
        """Attaque dans la direction."""
        if self == Action.MOVE_UP:
            return Action.ATTACK_UP
        if self == Action.MOVE_DOWN:
            return Action.ATTACK_DOWN
        if self == Action.MOVE_LEFT:
            return Action.ATTACK_LEFT
        if self == Action.MOVE_RIGHT:
            return Action.ATTACK_RIGHT
        return self

    def is_movement(self) -> bool:
        """Renvoie vrai si l'action est un déplacement."""
        return self in (
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
        )

    def is_attack(self) -> bool:
        """Renvoie vrai si l'action est une attaque."""
        return self in (
            Action.ATTACK_UP,
            Action.ATTACK_DOWN,
            Action.ATTACK_LEFT,
            Action.ATTACK_RIGHT,
        )


class Entity:
    """Une entité de la zone de jeu."""

    TILE = Tile.INVALID

    def __init__(self, x: int, y: int):
        """Entité placée initialement en `(x, y)`."""
        self.x = x
        self.y = y

    @property
    def visual_x(self) -> float:
        """Position x affichée de l'entité, utilisée pour les animations."""
        return float(self.x)

    @property
    def visual_y(self) -> float:
        """Position y affichée de l'entité, utilisée pour les animations."""
        return float(self.y)

    def update(self, game, dt: float):
        """Met à jour l'entité."""

    def next_update_in(self, dt: float) -> float:
        """Temps avant la prochaine mise à jour de l'entité."""
        return float("inf")


class MovingEntity(Entity):
    """Une entité mobile de la zone de jeu."""

    def __init__(self, x: int, y: int, speed: float):
        """L'entité réalise `speed` actions par seconde."""
        super().__init__(x, y)
        self.speed = speed
        self.action = Action.WAIT
        self.action_progress = 0.0

    def next_update_in(self, dt: float) -> float:
        """Temps en seconde avant la prochaine update pour cette entité."""
        # Update à la moitié de l'action
        if self.action_progress < 0.5:
            return 0.5 / self.speed

        return 1 / self.speed

    @property
    def visual_x(self) -> float:
        """Position x affichée de l'entité, utilisée pour les animations."""
        if self.action == Action.MOVE_LEFT:
            return self.x + int(self.action_progress >= 0.5) - self.action_progress
        if self.action == Action.MOVE_RIGHT:
            return self.x - int(self.action_progress >= 0.5) + self.action_progress
        return float(self.x)

    @property
    def visual_y(self) -> float:
        """Position y affichée de l'entité, utilisée pour les animations."""
        if self.action == Action.MOVE_UP:
            return self.y + int(self.action_progress >= 0.5) - self.action_progress
        if self.action == Action.MOVE_DOWN:
            return self.y - int(self.action_progress >= 0.5) + self.action_progress
        return float(self.y)


class PlayerEntity(MovingEntity):
    """
    Un joueur, qui fait `speed` actions par seconde.

    L'action du joueur est choisie par la fonction `play`, qui renvoie une constante
    d'action.
    """

    INITIAL_SPEED = 1.0

    def __init__(self, x: int, y: int):
        """Initialise un joueur."""
        super().__init__(x, y, self.INITIAL_SPEED)
        self.shield = False
        self.coins = 0
        self.super_fireball = 0

        self.play = lambda game: Action.WAIT

    def update(self, game, dt: float):
        """Met à jour la position du joueur et choisit sa prochaine action."""
        # Fin d'une action, choix de la prochaine action
        if self.action_progress < 1.0 <= self.action_progress + dt * self.speed:

            # Choix de la prochaine action
            action = self.play(game)
            self.action_progress = 0

            # Si l'action est valide, on la joue
            if game.is_valid_action(self, action):
                self.action = action

                if self.action.is_attack():
                    game.player_attacks(self, self.action)

            else:
                self.action = Action.WAIT
                print(f"Action invalide pour le joueur {self.TILE.name}")

        # À la moitié du déplacement on met à jour les coordonnées du joueur
        elif (
            self.action.is_movement()
            and self.action_progress < 0.5 <= self.action_progress + dt * self.speed
        ):
            self.action_progress = 0.5

            # Si le déplacement est toujours valide, il est effectué
            if game.is_valid_action(self, self.action):
                old_x, old_y = self.x, self.y
                self.x, self.y = self.action.apply((self.x, self.y))
                game.move_entity(self, old_x, old_y)

                if game.background[self.y][self.x] == Tile.LAVA:
                    game.remove_entity(self)
                    return

                for entity in game.entity_grid[self.y][self.x].copy():
                    # Suppression du joueur s'il est transpercé par une boule de feu
                    if isinstance(entity, Fireball):
                        print(f"{self.TILE.name} touché par {entity.player.TILE.name}")
                        game.hit_player(entity, self)

                    # Un item à ramasser ?
                    elif isinstance(entity, CollectableEntity):
                        game.collect(self, entity)

            # Sinon, on fait demi-tour
            else:
                self.action = self.action.swap()

        # Rien de spécial, on avance dans l'action
        else:
            self.action_progress += dt * self.speed


class RedPlayer(PlayerEntity):
    """Le joueur rouge."""

    TILE = Tile.PLAYER_RED


class BluePlayer(PlayerEntity):
    """Le joueur bleu."""

    TILE = Tile.PLAYER_BLUE


class YellowPlayer(PlayerEntity):
    """Le joueur jaune."""

    TILE = Tile.PLAYER_YELLOW


class GreenPlayer(PlayerEntity):
    """Le joueur vert."""

    TILE = Tile.PLAYER_GREEN


players: List[Type[PlayerEntity]] = [
    RedPlayer,
    BluePlayer,
    YellowPlayer,
    GreenPlayer,
]


class Fireball(MovingEntity):
    """Une boule de feu, qui tue les joueurs qu'elle traverse."""

    TILE = Tile.FIREBALL
    INITIAL_SPEED = 4.0

    def __init__(self, x, y, direction, player: PlayerEntity):
        """Initialise une boule de feu."""
        super().__init__(x, y, self.INITIAL_SPEED)
        self.action = direction
        self.player = player

    def update(self, game, dt: float):
        """Met à jour les coordonnées de la boule de feu."""
        # On recommence la même action
        if self.action_progress < 1.0 <= self.action_progress + dt * self.speed:
            self.action_progress = 0

        # À la moitié de l'action on déplace la boule de feu
        elif self.action_progress < 0.5 <= self.action_progress + dt * self.speed:
            old_x, old_y = self.x, self.y
            self.x, self.y = self.action.apply((self.x, self.y))
            self.action_progress = 0.5

            game.move_entity(self, old_x, old_y)

            # Suppression de la boule de feu si elle tape un mur
            if game.background[self.y][self.x] == Tile.WALL:
                game.remove_entity(self)

            self.hit_players(game)

        # Rien de spécial
        else:
            self.action_progress += dt * self.speed

    def hit_players(self, game):
        """Inflige un point de dégât à tous les joueurs de la case."""
        # Suppression des joueurs transpercés par la boule de feu
        for entity in game.entity_grid[self.y][self.x].copy():
            if isinstance(entity, PlayerEntity):
                print(f"{entity.TILE.name} touché par {self.player.TILE.name}")
                game.hit_player(self, entity)


class CollectableEntity(Entity):
    """Une entité ramassable de la zone de jeu."""

    def collect(self, player: PlayerEntity):
        """Le joueur `player` ramasse l'entité."""


class Coin(CollectableEntity):
    """Une pièce à ramasser."""

    TILE = Tile.COIN

    def collect(self, player: PlayerEntity):
        """Ajoute une pièce au joueur."""
        player.coins += 1


class SpeedBoost(CollectableEntity):
    """Un bonus de vitesse."""

    TILE = Tile.SPEEDBOOST

    def collect(self, player: PlayerEntity):
        """Ajoute 25pts% de vitesse au joueur."""
        player.speed += 0.25


class SpeedPenalty(CollectableEntity):
    """Un malus de vitesse."""

    TILE = Tile.SPEEDPENALTY

    def collect(self, player: PlayerEntity):
        """Retire 25pts% de vitesse au joueur."""
        if player.speed >= 0.75:
            player.speed -= 0.25


class SuperFireball(CollectableEntity):
    """Un sort qui lance une boule de feu dans toutes les directions."""

    TILE = Tile.SUPER_FIREBALL

    def collect(self, player: PlayerEntity):
        """Ajoute un sort au joueur."""
        player.super_fireball += 1


class Shield(CollectableEntity):
    """Un bouclier qui protège d'une boule de feu."""

    TILE = Tile.SHIELD

    def collect(self, player: PlayerEntity):
        """Protège le joueur jusqu'au prochain coup."""
        player.shield = True
