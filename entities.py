from map import ARROW, SPEEDBOOST, SPEEDPENALTY, WALL, COIN

WAIT = 0
MOVE_UP = 1
MOVE_DOWN = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4
ATTACK_UP = 11
ATTACK_DOWN = 12
ATTACK_LEFT = 13
ATTACK_RIGHT = 14


def move(coords, action):
    """
    Applique le déplacement `action` à la paire de coordonnées `coords`.
    """
    x, y = coords
    if action == MOVE_UP:
        y -= 1
    elif action == MOVE_DOWN:
        y += 1
    elif action == MOVE_LEFT:
        x -= 1
    elif action == MOVE_RIGHT:
        x += 1
    return (x, y)


def place_arrow(coords, action):
    """
    Donne un triplet `(x, y, direction)` correspondant à une flèche placée depuis les coordonnées `coords`, par l'action `action`.
    """
    x, y = coords
    direction = MOVE_UP
    if action == ATTACK_UP:
        y -= 1
    elif action == ATTACK_DOWN:
        y += 1
        direction = MOVE_DOWN
    elif action == ATTACK_LEFT:
        x -= 1
        direction = MOVE_LEFT
    elif action == ATTACK_RIGHT:
        x += 1
        direction = MOVE_RIGHT
    return (x, y, direction)


def swap_direction(action):
    """
    Donne la direction opposée pour l'action `action`.
    """
    if action == MOVE_UP:
        return MOVE_DOWN
    elif action == MOVE_DOWN:
        return MOVE_UP
    elif action == MOVE_LEFT:
        return MOVE_RIGHT
    elif action == MOVE_RIGHT:
        return MOVE_LEFT
    elif action == ATTACK_UP:
        return ATTACK_DOWN
    elif action == ATTACK_DOWN:
        return ATTACK_UP
    elif action == ATTACK_LEFT:
        return ATTACK_RIGHT
    elif action == ATTACK_RIGHT:
        return ATTACK_LEFT
    return WAIT


def swap_type(action):
    if action == MOVE_UP:
        return ATTACK_UP
    elif action == MOVE_DOWN:
        return ATTACK_DOWN
    elif action == MOVE_LEFT:
        return ATTACK_LEFT
    elif action == MOVE_RIGHT:
        return ATTACK_RIGHT
    elif action == ATTACK_UP:
        return MOVE_UP
    elif action == ATTACK_DOWN:
        return MOVE_DOWN
    elif action == ATTACK_LEFT:
        return MOVE_LEFT
    elif action == ATTACK_RIGHT:
        return MOVE_RIGHT
    return WAIT


class CantMoveThereException(Exception):
    """
    Exception lancée quand un joueur ne peut pas se rendre sur un case car il y a un mur.
    """

    pass


class Entity:
    """
    Une entité de la zone de jeu.
    """

    grid_id = 0

    def __init__(self, x: int, y: int):
        """
        Entité placée initialement en `(x, y)`
        """
        self.x = x
        self.y = y

    def get_visual_x(self):
        """
        Position x affichée de l'entité, utilisée pour les animations.
        """
        return self.x

    def get_visual_y(self):
        """
        Position y affichée de l'entité, utilisée pour les animations.
        """
        return self.y

    def update(self, game, dt: float):
        pass

    def next_update_in(self, dt: float):
        return float("inf")


class MovingEntity(Entity):
    """
    Une entité mobile de la zone de jeu.
    """

    def __init__(self, x, y, speed: float):
        """
        L'entité réalise `speed` actions par seconde.
        """
        super().__init__(x, y)
        self.speed = speed
        self.action = WAIT
        self.action_progress = 0.0

    def next_update_in(self, dt):
        """
        Temps en seconde avant la prochaine update pour cette entité.
        """

        # Update à la moitié de l'action
        if self.action_progress < 0.5:
            return 0.5 / self.speed

        return 1 / self.speed

    def get_visual_x(self):
        """
        Position x affichée de l'entité, utilisée pour les animations.
        """
        if self.action == MOVE_LEFT:
            return self.x + int(self.action_progress >= 0.5) - self.action_progress
        elif self.action == MOVE_RIGHT:
            return self.x - int(self.action_progress >= 0.5) + self.action_progress
        return self.x

    def get_visual_y(self):
        """
        Position y affichée de l'entité, utilisée pour les animations.
        """
        if self.action == MOVE_UP:
            return self.y + int(self.action_progress >= 0.5) - self.action_progress
        elif self.action == MOVE_DOWN:
            return self.y - int(self.action_progress >= 0.5) + self.action_progress
        return self.y


class Player(MovingEntity):
    """
    Un joueur, qui fait `speed` actions par seconde.

    L'action du joueur est choisie par la fonction `play`, qui renvoie une constante d'action.
    """

    def __init__(self, x, y, speed, color):
        """
        Initialise un joueur avec sa couleur.
        """
        super(Player, self).__init__(x, y, speed)
        self.color = color
        self.grid_id = self.color
        self.shield = False
        self.coins = 0

    def play(self, game):
        """
        Choisit la prochaine action du joueur, en renvoyant une constante d'action.
        """
        return WAIT

    def update(self, game, dt: float):
        """
        Met à jour la position du joueur et choisit sa prochaine action.
        """

        # Fin d'une action, choix de la prochaine action
        if self.action_progress < 1.0 and self.action_progress + dt * self.speed >= 1.0:

            # Choix de la prochaine action
            action = self.play(game)
            self.action_progress = 0

            # Si l'action est valide, on la joue
            if game.is_valid_action(self, action):
                self.action = action

                if self.action in (ATTACK_UP, ATTACK_DOWN, ATTACK_LEFT, ATTACK_RIGHT):
                    game.player_attacks(self, self.action)

            else:
                self.action = WAIT
                print("Action invalide pour le joueur " + str(self.color))

        # À la moitié du déplacement on met à jour les coordonnées du joueur
        elif (
            self.action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT)
            and self.action_progress < 0.5
            and self.action_progress + dt * self.speed >= 0.5
        ):
            # Si le déplacement est toujours valide, il est effectué
            if game.is_valid_action(self, self.action):
                old_x, old_y = self.x, self.y
                self.x, self.y = move((self.x, self.y), self.action)
                game.move_entity(self, old_x, old_y)

            # Sinon, on fait demi-tour
            else:
                self.action = swap_direction(self.action)

            self.action_progress = 0.5

        # Rien de spécial, on avance dans l'action
        else:
            self.action_progress += dt * self.speed

        # Un item à ramasser ?
        for entity in game.entity_grid[self.y][self.x].copy():
            if isinstance(entity, CollectableEntity):
                game.collect(self, entity)


class Arrow(MovingEntity):
    """
    Une flèche, qui tue les joueurs qu'elle traverse.
    """

    grid_id = ARROW

    def __init__(self, x, y, direction, player: Player):
        """
        Initialise une flèche, qui se déplace à 4.0 case / seconde.
        """
        super().__init__(x, y, 4.0)
        self.action = direction
        self.player = player

    def update(self, game, dt: float):
        """
        Met à jour les coordonnées de la flèche.
        """

        # On recommence la même action
        if self.action_progress < 1.0 and self.action_progress + dt * self.speed >= 1.0:
            self.action_progress = 0

        # À la moitié de l'action on déplace la flèche
        elif (
            self.action_progress < 0.5 and self.action_progress + dt * self.speed >= 0.5
        ):
            old_x, old_y = self.x, self.y
            self.x, self.y = move((self.x, self.y), self.action)
            self.action_progress = 0.5

            game.move_entity(self, old_x, old_y)

            # Suppression de la flèche si elle tape un mur
            if game.grid[self.y][self.x] == WALL:
                game.remove_arrow(self)

        # Rien de spécial
        else:
            self.action_progress += dt * self.speed

        # Suppression des joueurs transpercés par la flèche
        for entity in game.entity_grid[self.y][self.x].copy():
            if isinstance(entity, Player):
                print(f"Joueur {entity.color} éliminé par {self.player.color}")
                game.remove_player(entity)


class CollectableEntity(Entity):
    """
    Une entité ramassable de la zone de jeu.
    """

    def collect(self, game, player):
        """
        Le joueur `player` ramasse l'entité.
        """
        pass


class Coin(CollectableEntity):
    grid_id = COIN

    def collect(self, game, player):
        player.coins += 1


class SpeedBoost(CollectableEntity):
    grid_id = SPEEDBOOST

    def collect(self, game, player):
        player.speed += 0.25


class SpeedPenalty(CollectableEntity):
    grid_id = SPEEDPENALTY

    def collect(self, game, player):
        if player.speed >= 0.75:
            player.speed -= 0.25


class Shield(CollectableEntity):
    def collect(self, game, player):
        player.shield = True
