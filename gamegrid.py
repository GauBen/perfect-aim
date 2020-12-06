"""Le générateur de cartes de Perfect Aim."""

import sys
from enum import IntEnum
from random import Random, randrange
from typing import List, Tuple


class Tile(IntEnum):
    """Tous les éléments présents sur le jeu."""

    GENERATING = -2
    INVALID = -1

    FLOOR = 0
    WALL = 1
    LAVA = 2
    DAMAGED_FLOOR = 3

    SPEEDBOOST = 21
    SPEEDPENALTY = 22
    COIN = 23
    SUPER_FIREBALL = 24
    SHIELD = 25

    PLAYER_RED = 31
    PLAYER_BLUE = 32
    PLAYER_YELLOW = 33
    PLAYER_GREEN = 34

    FIREBALL = 41

    def is_floor(self) -> bool:
        """Renvoie vrai si `self` correspond à du sol."""
        return self in (Tile.FLOOR, Tile.DAMAGED_FLOOR)

    def is_background(self) -> bool:
        """Renvoie vrai si `self` correspond au fond du plateau."""
        return self in (Tile.FLOOR, Tile.WALL, Tile.LAVA, Tile.DAMAGED_FLOOR)

    def is_collectible(self) -> bool:
        """Renvoie vrai si `self` correspond à un objet."""
        return self in (
            Tile.SPEEDBOOST,
            Tile.SPEEDPENALTY,
            Tile.COIN,
            Tile.SUPER_FIREBALL,
            Tile.SHIELD,
        )

    def is_bonus(self) -> bool:
        """Renvoie vrai si `self` correspond à un objet positif."""
        return self in (Tile.SPEEDBOOST, Tile.SUPER_FIREBALL, Tile.SHIELD)

    def is_player(self) -> bool:
        """Renvoie vrai si `self` correspond à un joueur."""
        return self in (
            Tile.PLAYER_RED,
            Tile.PLAYER_BLUE,
            Tile.PLAYER_YELLOW,
            Tile.PLAYER_GREEN,
        )

    def is_dangerous(self) -> bool:
        """Renvoie vrai si `self` représente un danger."""
        return self in (
            Tile.LAVA,
            Tile.DAMAGED_FLOOR,
            Tile.PLAYER_RED,
            Tile.PLAYER_BLUE,
            Tile.PLAYER_YELLOW,
            Tile.PLAYER_GREEN,
            Tile.FIREBALL,
        )

    def __repr__(self) -> str:
        """REMOVE."""
        return "Tile." + self.name


class Matrix:
    """Opérations matricielles basiques."""

    @staticmethod
    def rotate(m):
        """Rotation."""
        return [list(i) for i in zip(*m[::-1])]

    @staticmethod
    def rotate2(m):
        """Double rotation."""
        return [i[::-1] for i in m][::-1]

    @staticmethod
    def vmirror(m):
        """Reflet vertical d'une matrice."""
        return [i[:] for i in m[::-1]]

    @staticmethod
    def hmirror(m):
        """Reflet horizontal d'une matrice."""
        return [i[::-1] for i in m]

    @staticmethod
    def vstack(m, n):
        """Empile verticalement deux matrices, sans copie."""
        return m + n

    @staticmethod
    def hstack(m, n):
        """Concatène horizontalement deux matrices, sans copie."""
        return [m[i] + n[i] for i in range(len(m))]


class Grid:
    """Générateur des cartes du jeu."""

    def __init__(self, size, seed=None):
        """Génère une carte à partir de sa taille et d'une graine."""
        assert size % 4 == 1, "La grille doit respecter un critère de taille."
        self.size = size
        if seed is None:
            seed = randrange(sys.maxsize)
        self.seed = seed
        self.random = Random(seed)
        self._create_grid()

    def _create_grid(self) -> List[List[Tile]]:
        """Génération d'une carte labyrinthe."""
        size = (self.size - 1) // 2 + 1

        # == Génération du labyrinthe ==

        # Au début c'est un gruyère, un truc un peu comme ça :
        # ##########
        # ##  ##  ##
        # ##########
        # ##  ##  ##
        # ##########
        self.grid: List[List[Tile]] = [
            [Tile.GENERATING if x % 2 == y % 2 == 1 else Tile.WALL for x in range(size)]
            for y in range(size)
        ]

        # On va générer des chemins
        path: List[Tuple[int, int]] = [(1, 1)]
        while len(path) > 0:
            # Tête d'exploration
            (x, y) = path[-1]

            # On remplace GENERATING par FLOOR
            self.grid[y][x] = Tile.FLOOR

            # On fait la liste des directions possibles pour continuer l'exploration
            possible_directions = []
            if y >= 3 and self.grid[y - 2][x] == Tile.GENERATING:
                possible_directions.append((x, y - 2))
            if y <= size - 3 and self.grid[y + 2][x] == Tile.GENERATING:
                possible_directions.append((x, y + 2))
            if x >= 3 and self.grid[y][x - 2] == Tile.GENERATING:
                possible_directions.append((x - 2, y))
            if x <= size - 3 and self.grid[y][x + 2] == Tile.GENERATING:
                possible_directions.append((x + 2, y))

            # Si on est dans un cul de sac, on dépile
            if len(possible_directions) == 0:
                path.pop()
                continue

            # Sinon on va dans une des directions possible
            self.random.shuffle(possible_directions)
            new_x, new_y = possible_directions.pop()
            path.append((new_x, new_y))

            # On perce le mur entre ici et la prochaine case
            self.grid[(y + new_y) // 2][(x + new_x) // 2] = Tile.FLOOR

            # On ajoute quelques chemins de traverse
            if len(possible_directions) > 0 and self.random.random() < 0.2:
                other_x, other_y = possible_directions.pop()
                self.grid[(y + other_y) // 2][(x + other_x) // 2] = Tile.FLOOR

        # == Génération d'une grille symétrique avec des objets ==

        # On ajoute des items
        self._add_collectibles()

        # On fait une belle grille symétrique
        self._add_symetry()

    def _add_collectibles(self):
        """Ajoute tous les objets possibles sur la grille."""
        size = (self.size - 1) // 2 + 1
        coords = [
            (x, y)
            for x in range(1, size, 2)
            for y in range(1, size, 2)
            if (x, y) != (1, 1)
        ]
        self.random.shuffle(coords)
        items = [
            Tile.SPEEDBOOST,
            Tile.SPEEDPENALTY,
            Tile.COIN,
            Tile.SUPER_FIREBALL,
            Tile.SHIELD,
        ]
        while len(coords) > 0:
            x, y = coords.pop()
            if self.grid[y][x] == Tile.FLOOR:
                self.grid[y][x] = items.pop()
            if len(items) == 0:
                break

    def _add_symetry(self):
        """Rend la grille symétrique en la répétant 3 fois."""
        size = (self.size - 1) // 2 + 1
        # On enlève les murs bas et droit
        self.grid.pop()
        for row in self.grid:
            row.pop()

        # On va mettre ce mur percé à la place
        wall = [
            [
                Tile.FLOOR if i % 2 == 1 and self.random.random() < 0.5 else Tile.WALL
                for i in range(size - 3)
            ]
            + [Tile.WALL, Tile.FLOOR]
        ]
        wallr = Matrix.rotate(wall)

        # Une chance sur deux que la symétrie soit centrale
        op1 = Matrix.rotate
        op2 = Matrix.rotate2

        # Et l'autre qu'elle soit axiale
        if self.random.random() < 0.5:
            op1 = Matrix.hmirror
            op2 = Matrix.vmirror

        # Assemblage du haut (laby + mur + laby symétrique)
        top = Matrix.hstack(self.grid, Matrix.hstack(wallr, op1(self.grid)))

        # Assemblage final
        self.grid = Matrix.vstack(
            top,
            Matrix.vstack(
                Matrix.hstack(
                    wall,
                    Matrix.hstack([[Tile.WALL]], Matrix.rotate(wallr)),
                ),
                op2(top),
            ),
        )


# Si on lance ce fichier, un petit easter egg
if __name__ == "__main__":
    g = Grid(21, seed=None)
    for row in g.grid:
        for cell in row:
            print(
                {
                    Tile.WALL: "###",
                    Tile.FLOOR: "   ",
                    Tile.COIN: " o ",
                    Tile.SPEEDBOOST: " ^ ",
                    Tile.SHIELD: " D ",
                    Tile.SUPER_FIREBALL: " + ",
                    Tile.SPEEDPENALTY: " v ",
                }[cell],
                end="",
            )
        print()
    print("o Coin          D Shield          + Super fireball")
    print(f"^ Speed boost   v Speed penalty     (seed: {g.seed})")
