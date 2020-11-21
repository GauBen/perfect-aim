"""Les entités du jeu."""
from enum import Enum
from typing import Tuple

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


def move(coords: Tuple[int, int], action: Action) -> Tuple[int, int]:
    """Applique le déplacement `action` à la paire de coordonnées `coords`."""
    x, y = coords
    if action == Action.MOVE_UP:
        y -= 1
    elif action == Action.MOVE_DOWN:
        y += 1
    elif action == Action.MOVE_LEFT:
        x -= 1
    elif action == Action.MOVE_RIGHT:
        x += 1
    return (x, y)


def place_fireball(coords: Tuple[int, int], action: Action) -> Tuple[int, int, Action]:
    """
    Donne les infos sur le placement d'une boule de feu.

    Donne un triplet `(x, y, direction)` correspondant à une boule de feu placée depuis
    les coordonnées `coords`, par l'action `action`.
    """
    x, y = coords
    direction = Action.WAIT
    if action == Action.ATTACK_UP:
        direction = Action.MOVE_UP
    elif action == Action.ATTACK_DOWN:
        direction = Action.MOVE_DOWN
    elif action == Action.ATTACK_LEFT:
        direction = Action.MOVE_LEFT
    elif action == Action.ATTACK_RIGHT:
        direction = Action.MOVE_RIGHT
    return (x, y, direction)


def swap_direction(action):
    """Donne la direction opposée pour l'action `action`."""
    if action == Action.MOVE_UP:
        return Action.MOVE_DOWN
    if action == Action.MOVE_DOWN:
        return Action.MOVE_UP
    if action == Action.MOVE_LEFT:
        return Action.MOVE_RIGHT
    if action == Action.MOVE_RIGHT:
        return Action.MOVE_LEFT
    if action == Action.ATTACK_UP:
        return Action.ATTACK_DOWN
    if action == Action.ATTACK_DOWN:
        return Action.ATTACK_UP
    if action == Action.ATTACK_LEFT:
        return Action.ATTACK_RIGHT
    if action == Action.ATTACK_RIGHT:
        return Action.ATTACK_LEFT
    return Action.WAIT


def swap_type(action):
    """Echange les attaques et les déplacements."""
    if action == Action.MOVE_UP:
        return Action.ATTACK_UP
    if action == Action.MOVE_DOWN:
        return Action.ATTACK_DOWN
    if action == Action.MOVE_LEFT:
        return Action.ATTACK_LEFT
    if action == Action.MOVE_RIGHT:
        return Action.ATTACK_RIGHT
    if action == Action.ATTACK_UP:
        return Action.Action.MOVE_UP
    if action == Action.ATTACK_DOWN:
        return Action.MOVE_DOWN
    if action == Action.ATTACK_LEFT:
        return Action.MOVE_LEFT
    if action == Action.ATTACK_RIGHT:
        return Action.MOVE_RIGHT
    return Action.WAIT


class CantMoveThereException(Exception):
    """Exception lancée quand un joueur ne peut pas se rendre sur une case."""


class Entity:
    """Une entité de la zone de jeu."""

    grid_id = 0

    def __init__(self, x: int, y: int):
        """Entité placée initialement en `(x, y)`."""
        self.x = x
        self.y = y

    def get_visual_x(self) -> float:
        """Position x affichée de l'entité, utilisée pour les animations."""
        return self.x

    def get_visual_y(self) -> float:
        """Position y affichée de l'entité, utilisée pour les animations."""
        return self.y

    def update(self, game, dt: float):
        """Met à jour l'entité."""
        pass

    def next_update_in(self, dt: float):
        """Temps avant la prochaine mise à jour de l'entité."""
        return float("inf")


class MovingEntity(Entity):
    """Une entité mobile de la zone de jeu."""

    def __init__(self, x, y, speed: float):
        """L'entité réalise `speed` actions par seconde."""
        super().__init__(x, y)
        self.speed = speed
        self.action = Action.WAIT
        self.action_progress = 0.0

    def next_update_in(self, dt):
        """Temps en seconde avant la prochaine update pour cette entité."""
        # Update à la moitié de l'action
        if self.action_progress < 0.5:
            return 0.5 / self.speed

        return 1 / self.speed

    def get_visual_x(self):
        """Position x affichée de l'entité, utilisée pour les animations."""
        if self.action == Action.MOVE_LEFT:
            return self.x + int(self.action_progress >= 0.5) - self.action_progress
        if self.action == Action.MOVE_RIGHT:
            return self.x - int(self.action_progress >= 0.5) + self.action_progress
        return self.x

    def get_visual_y(self):
        """Position y affichée de l'entité, utilisée pour les animations."""
        if self.action == Action.MOVE_UP:
            return self.y + int(self.action_progress >= 0.5) - self.action_progress
        if self.action == Action.MOVE_DOWN:
            return self.y - int(self.action_progress >= 0.5) + self.action_progress
        return self.y


class Player(MovingEntity):
    """
    Un joueur, qui fait `speed` actions par seconde.

    L'action du joueur est choisie par la fonction `play`, qui renvoie une constante
    d'action.
    """

    name = "Donne-moi un nom !"

    def __init__(self, x, y, speed, color):
        """Initialise un joueur avec sa couleur."""
        super(Player, self).__init__(x, y, speed)
        self.color = color
        self.grid_id = self.color
        self.shield = False
        self.coins = 0
        self.super_fireball = 0

    def play(self, game):
        """Choisit la prochaine action du joueur, en renvoyant une constante d'action."""
        return Action.WAIT

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

                if self.action in (
                    Action.ATTACK_UP,
                    Action.ATTACK_DOWN,
                    Action.ATTACK_LEFT,
                    Action.ATTACK_RIGHT,
                ):
                    game.player_attacks(self, self.action)

            else:
                self.action = Action.WAIT
                print("Action invalide pour le joueur " + str(self.color))

        # À la moitié du déplacement on met à jour les coordonnées du joueur
        elif (
            self.action
            in (Action.MOVE_UP, Action.MOVE_DOWN, Action.MOVE_LEFT, Action.MOVE_RIGHT)
            and self.action_progress < 0.5 <= self.action_progress + dt * self.speed
        ):
            self.action_progress = 0.5

            # Si le déplacement est toujours valide, il est effectué
            if game.is_valid_action(self, self.action):
                old_x, old_y = self.x, self.y
                self.x, self.y = move((self.x, self.y), self.action)
                game.move_entity(self, old_x, old_y)

                if game.background[self.y][self.x] == Tile.LAVA:
                    game.remove_entity(self)
                    return

                for entity in game.entity_grid[self.y][self.x].copy():
                    # Suppression du joueur s'il est transpercé par une boule de feu
                    if isinstance(entity, Fireball):
                        print(f"Joueur {self.color} touché par {entity.player.color}")
                        game.hit_player(entity, self)

                    # Un item à ramasser ?
                    elif isinstance(entity, CollectableEntity):
                        game.collect(self, entity)

            # Sinon, on fait demi-tour
            else:
                self.action = swap_direction(self.action)

        # Rien de spécial, on avance dans l'action
        else:
            self.action_progress += dt * self.speed

    def get_name(self):
        """Renvoie le nom du joueur et sa couleur."""
        name = self.name
        if self.color == Tile.PLAYER_RED:
            name += " (rouge)"
        elif self.color == Tile.PLAYER_BLUE:
            name += " (bleu)"
        elif self.color == Tile.PLAYER_YELLOW:
            name += " (jaune)"
        elif self.color == Tile.PLAYER_GREEN:
            name += " (vert)"
        return name


class Fireball(MovingEntity):
    """Une boule de feu, qui tue les joueurs qu'elle traverse."""

    grid_id = Tile.FIREBALL

    def __init__(self, x, y, direction, player: Player):
        """Initialise une boule de feu, qui se déplace à 4.0 case / seconde."""
        super().__init__(x, y, 4.0)
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
            self.x, self.y = move((self.x, self.y), self.action)
            self.action_progress = 0.5

            game.move_entity(self, old_x, old_y)

            # Suppression de la boule de feu si elle tape un mur
            if game.grid[self.y][self.x] == Tile.WALL:
                game.remove_entity(self)

            self.hit_players(game)

        # Rien de spécial
        else:
            self.action_progress += dt * self.speed

    def hit_players(self, game):
        """Inflige un point de dégât à tous les joueurs de la case."""
        # Suppression des joueurs transpercés par la boule de feu
        for entity in game.entity_grid[self.y][self.x].copy():
            if isinstance(entity, Player):
                print(f"Joueur {entity.color} touché par {self.player.color}")
                game.hit_player(self, entity)


class CollectableEntity(Entity):
    """Une entité ramassable de la zone de jeu."""

    def collect(self, game, player: Player):
        """Le joueur `player` ramasse l'entité."""


class Coin(CollectableEntity):
    """Une pièce à ramasser."""

    grid_id = Tile.COIN

    def collect(self, game, player):
        """Ajoute une pièce au joueur."""
        player.coins += 1


class SpeedBoost(CollectableEntity):
    """Un bonus de vitesse."""

    grid_id = Tile.SPEEDBOOST

    def collect(self, game, player):
        """Ajoute 25pts% de vitesse au joueur."""
        player.speed += 0.25


class SpeedPenalty(CollectableEntity):
    """Un malus de vitesse."""

    grid_id = Tile.SPEEDPENALTY

    def collect(self, game, player):
        """Retire 25pts% de vitesse au joueur."""
        if player.speed >= 0.75:
            player.speed -= 0.25


class SuperFireball(CollectableEntity):
    """Un sort qui lance une boule de feu dans toutes les directions."""

    grid_id = Tile.SUPER_FIREBALL

    def collect(self, game, player):
        """Ajoute un sort au joueur."""
        player.super_fireball += 1


class Shield(CollectableEntity):
    """Un bouclier qui protège d'une boule de feu."""

    grid_id = Tile.SHIELD

    def collect(self, game, player):
        """Protège le joueur jusqu'au prochain coup."""
        player.shield = True
