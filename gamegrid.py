"""Le générateur de cartes de Perfect Aim."""

from enum import IntEnum
from random import shuffle, random
from typing import List


class Tile(IntEnum):
    """Tous les éléments présents sur le jeu."""

    INVALID = -2
    GENERATING = -1

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

    @classmethod
    def is_background(cls, tile):
        """Renvoie vrai si `tile` correspond au fond du plateau."""
        return tile in (
            cls.FLOOR,
            cls.WALL,
            cls.LAVA,
            cls.DAMAGED_FLOOR,
        )

    @classmethod
    def is_collectible(cls, tile):
        """Renvoie vrai si `tile` correspond à un objet."""
        return tile in (
            cls.SPEEDBOOST,
            cls.SPEEDPENALTY,
            cls.COIN,
            cls.SUPER_FIREBALL,
            cls.SHIELD,
        )

    @classmethod
    def is_bonus(cls, tile):
        """Renvoie vrai si `tile` correspond à un objet positif."""
        return tile in (
            cls.SPEEDBOOST,
            cls.SUPER_FIREBALL,
            cls.SHIELD,
        )

    @classmethod
    def is_player(cls, tile):
        """Renvoie vrai si `tile` correspond à un joueur."""
        return tile in (
            cls.PLAYER_RED,
            cls.PLAYER_BLUE,
            cls.PLAYER_YELLOW,
            cls.PLAYER_GREEN,
        )

    @classmethod
    def is_dangerous(cls, tile):
        """Renvoie vrai si `tile` représente un danger."""
        return tile in (
            cls.LAVA,
            cls.DAMAGED_FLOOR,
            cls.PLAYER_RED,
            cls.PLAYER_BLUE,
            cls.PLAYER_YELLOW,
            cls.PLAYER_GREEN,
            cls.FIREBALL,
        )


class Matrix:
    """
    Opérations matricielles.

    Sans vérification de taille et sans copie, au développeur de faire attention.
    """

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
        """Empile verticalement deux matrices."""
        return m + n

    @staticmethod
    def hstack(m, n):
        """Concatène horizontalement deux matrices."""
        return [m[i] + n[i] for i in range(len(m))]


class Grid:
    """Représente une carte du jeu."""

    DEFAULT_SIZE = 21

    def __init__(self, size: int = DEFAULT_SIZE):
        """Génère une carte."""
        assert size % 4 == 1, "La grille doit respecter un critère de taille."
        self.size = size
        self.grid = self.create_map(self.size)

    @staticmethod
    def create_map(size: int) -> List[List[Tile]]:
        """Génération d'une carte labyrinthe."""
        size = (size - 1) // 2 + 1

        # == Génération du labyrinthe ==

        # Au début c'est un gruyère, un truc un peu comme ça :
        # ##########
        # ##  ##  ##
        # ##########
        # ##  ##  ##
        # ##########
        grid: List[List[Tile]] = [
            [Tile.GENERATING if x % 2 == y % 2 == 1 else Tile.WALL for x in range(size)]
            for y in range(size)
        ]

        # On va générer des chemins
        path = [(1, 1)]
        while len(path) > 0:
            # Tête d'exploration
            (x, y) = path[-1]

            # On remplace GENERATING par FLOOR
            grid[y][x] = Tile.FLOOR

            # On fait la liste des directions possibles pour continuer l'exploration
            possible_directions = []
            if y >= 3 and grid[y - 2][x] == Tile.GENERATING:
                possible_directions.append((x, y - 2))
            if y <= size - 3 and grid[y + 2][x] == Tile.GENERATING:
                possible_directions.append((x, y + 2))
            if x >= 3 and grid[y][x - 2] == Tile.GENERATING:
                possible_directions.append((x - 2, y))
            if x <= size - 3 and grid[y][x + 2] == Tile.GENERATING:
                possible_directions.append((x + 2, y))

            # Si on est dans un cul de sac, on dépile
            if len(possible_directions) == 0:
                path.pop()
                continue

            # Sinon on va dans une des directions possible
            shuffle(possible_directions)
            new_x, new_y = possible_directions.pop()
            path.append((new_x, new_y))

            # On perce le mur entre ici et la prochaine case
            grid[(y + new_y) // 2][(x + new_x) // 2] = Tile.FLOOR

            # On ajoute quelques chemins de traverse
            if len(possible_directions) > 0 and random() < 0.2:
                other_x, other_y = possible_directions.pop()
                grid[(y + other_y) // 2][(x + other_x) // 2] = Tile.FLOOR

        # == Génération d'une grille symétrique avec des objets ==

        # On ajoute des items
        Grid.add_collectibles(grid, size)

        # On fait une belle grille symétrique
        return Grid.add_symetry(grid, size)

    @staticmethod
    def add_collectibles(grid: List[List[Tile]], size: int):
        """Ajoute tous les objets possibles sur la grille."""
        coords = [
            (x, y)
            for x in range(1, size, 2)
            for y in range(1, size, 2)
            if (x, y) != (1, 1)
        ]
        shuffle(coords)
        items = [
            Tile.SPEEDBOOST,
            Tile.SPEEDPENALTY,
            Tile.COIN,
            Tile.SUPER_FIREBALL,
            Tile.SHIELD,
        ]
        while len(coords) > 0:
            x, y = coords.pop()
            if grid[y][x] == Tile.FLOOR:
                grid[y][x] = items.pop()
            if len(items) == 0:
                break

    @staticmethod
    def add_symetry(grid: List[List[Tile]], size: int) -> List[List[Tile]]:
        """Rend la grille symétrique en la répétant 3 fois."""
        # On enlève les murs bas et droit
        grid.pop()
        for row in grid:
            row.pop()

        # On va mettre ce mur percé à la place
        wall = [
            [
                Tile.FLOOR if i % 2 == 1 and random() < 0.5 else Tile.WALL
                for i in range(size - 3)
            ]
            + [Tile.WALL, Tile.FLOOR]
        ]
        wallr = Matrix.rotate(wall)

        # Une chance sur deux que la symétrie soit centrale
        op1 = Matrix.rotate
        op2 = Matrix.rotate2

        # Et l'autre qu'elle soit axiale
        if random() < 0.5:
            op1 = Matrix.hmirror
            op2 = Matrix.vmirror

        # Assemblage du haut (laby + mur + laby symétrique)
        top = Matrix.hstack(grid, Matrix.hstack(wallr, op1(grid)))

        # Assemblage final
        return Matrix.vstack(
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
    for row in Grid(21).grid:
        for cell in row:
            print(
                {
                    Tile.WALL: "###",
                    Tile.FLOOR: "   ",
                    Tile.COIN: " o ",
                    Tile.SPEEDBOOST: " ^ ",
                    Tile.SHIELD: " D ",
                    Tile.SUPER_FIREBALL: " X ",
                    Tile.SPEEDPENALTY: " v ",
                }[cell],
                end="",
            )
        print()
    print("o Coin          D Shield          X Super fireball")
    print("^ Speed boost   v Speed penalty")
