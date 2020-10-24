from random import choice

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


class CantMoveThereException(Exception):
    """
    Exception lancée quand un joueur ne peut pas se rendre sur un case car il y a un mur.
    """

    pass


class Entity:
    """
    Une entité de la zone de jeu.
    """

    def __init__(self, x: int, y: int):
        """
        Entité placée initialement en `(x, y)`
        """
        self.x = x
        self.y = y


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
        self.in_action_for = 0.0

    def next_update_in(self, dt):
        """
        Temps en seconde avant la prochaine update pour cette entité.
        """

        # Update à la moitié de l'action
        if 0.5 / self.speed > self.in_action_for:
            return 0.5 / self.speed - self.in_action_for

        return 1 / self.speed - self.in_action_for

    def get_visual_x(self):
        """
        Position x affichée de l'entité, utilisée pour les animations.
        """
        if self.action == MOVE_LEFT:
            return (
                self.x
                + int(self.in_action_for >= 0.5 / self.speed)
                - self.in_action_for * self.speed
            )
        elif self.action == MOVE_RIGHT:
            return (
                self.x
                - int(self.in_action_for >= 0.5 / self.speed)
                + self.in_action_for * self.speed
            )
        return self.x

    def get_visual_y(self):
        """
        Position y affichée de l'entité, utilisée pour les animations.
        """
        if self.action == MOVE_UP:
            return (
                self.y
                + int(self.in_action_for >= 0.5 / self.speed)
                - self.in_action_for * self.speed
            )
        elif self.action == MOVE_DOWN:
            return (
                self.y
                - int(self.in_action_for >= 0.5 / self.speed)
                + self.in_action_for * self.speed
            )
        return self.y

    def action_progress(self):
        """
        Valeur entre 0 et 1 correspondant à l'avancement de l'action.
        """
        return self.in_action_for * self.speed


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

    def play(self, game):
        """
        Choisit la prochaine action du joueur, en renvoyant une constante d'action.
        """

        c = choice(
            [
                MOVE_UP,
                MOVE_DOWN,
                MOVE_LEFT,
                MOVE_RIGHT,
                ATTACK_UP,
                ATTACK_DOWN,
                ATTACK_LEFT,
                ATTACK_RIGHT,
            ]
        )
        while not game.is_valid_action(self, c):
            c = choice(
                [
                    WAIT,
                    MOVE_UP,
                    MOVE_DOWN,
                    MOVE_LEFT,
                    MOVE_RIGHT,
                    ATTACK_UP,
                    ATTACK_DOWN,
                    ATTACK_LEFT,
                    ATTACK_RIGHT,
                ]
            )
        return c

    def update(self, game, dt: float):
        """
        Met à jour la position du joueur et choisit sa prochaine action.
        """

        # Fin d'une action, choix de la prochaine action
        if (
            self.in_action_for < 1.0 / self.speed
            and self.in_action_for + dt >= 1.0 / self.speed
        ):

            # Choix de la prochaine action
            action = self.play(game)
            self.in_action_for = 0

            # Si l'action est valide, on la joue
            if game.is_valid_action(self, action):
                self.action = action
                if self.action in (ATTACK_UP, ATTACK_DOWN, ATTACK_LEFT, ATTACK_RIGHT):
                    game.player_attacks(self, self.action)
            else:
                self.action = WAIT
                print("Action invalide pour le joueur " + self.color)

        # À la moitié du déplacement on met à jour les coordonnées du joueur
        elif (
            self.action in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT)
            and self.in_action_for < 0.5 / self.speed
            and self.in_action_for + dt >= 0.5 / self.speed
        ):
            # Si le déplacement est toujours valide, il est effectué
            if game.is_valid_action(self, self.action):
                self.x, self.y = move((self.x, self.y), self.action)

            # Sinon, on fait demi-tour
            else:
                self.action = swap_direction(self.action)

            self.in_action_for = 0.5 / self.speed

        # Rien de spécial, on avance dans l'action
        else:
            self.in_action_for += dt


class Arrow(MovingEntity):
    """
    Une flèche, qui tue les joueurs qu'elle traverse.
    """

    def __init__(self, x, y, direction):
        """
        Initialise une flèche, qui se déplace à 4.0 case / seconde.
        """
        super().__init__(x, y, 4.0)
        self.action = direction

    def update(self, game, dt: float):
        """
        Met à jour les coordonnées de la flèche.
        """

        # On recommence la même action
        if (
            self.in_action_for < 1.0 / self.speed
            and self.in_action_for + dt >= 1.0 / self.speed
        ):
            self.in_action_for = 0

        # À la moitié de l'action on déplace la flèche
        elif (
            self.in_action_for < 0.5 / self.speed
            and self.in_action_for + dt >= 0.5 / self.speed
        ):
            self.x, self.y = move((self.x, self.y), self.action)
            self.in_action_for = 0.5 / self.speed

        # Rien de spécial
        else:
            self.in_action_for += dt
