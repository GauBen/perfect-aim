from random import shuffle, random

EMPTY = 0
WALL = 1
UNEXPLORED = 19

SPEEDBOOST = 21
SPEEDPENALTY = 22
COIN = 23
SUPER_FIREBALL = 24

PLAYER_RED = 31
PLAYER_BLUE = 32
PLAYER_YELLOW = 33
PLAYER_GREEN = 34

ARROW = 41


def rotate(m):
    """
    Solution trouvée ici https://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python.
    """
    return [list(i) for i in zip(*m[::-1])]


def rotate2(m):
    """
    Double rotation.
    """
    return [i[::-1] for i in m][::-1]


def vmirror(m):
    """
    Reflet vertical d'une matrice.
    """
    return [i[:] for i in m[::-1]]


def hmirror(m):
    """
    Reflet horizontal d'une matrice.
    """
    return [i[::-1] for i in m]


def vstack(m, n):
    """
    Empile verticalement deux matrices.
    """
    return m + n


def hstack(m, n):
    """
    Concatène horizontalement deux matrices.
    """
    return [m[i] + n[i] for i in range(len(m))]


class Map:
    """
    Représente une carte du jeu.
    """

    def __init__(self):
        """
        Génère une carte.
        """
        self.size = 21
        self.grid = self.create_map(self.size)
        # self.grid = [[WALL] * self.size]
        # for i in range(self.size - 2):
        #     self.grid.append([WALL] + [EMPTY] * (self.size - 2) + [WALL])
        # self.grid.append([WALL] * self.size)

    @staticmethod
    def create_map(size):
        """
        Génération d'une carte labyrinthe.
        """
        size = size // 2 + 1
        grid = [[WALL] * size]
        for i in range(size - 2):
            grid.append(
                [WALL]
                + [UNEXPLORED if j % 2 == i % 2 == 0 else WALL for j in range(size - 2)]
                + [WALL]
            )
        grid.append([WALL] * size)
        backtrack = [(1, 1)]
        while len(backtrack) > 0:
            (x, y) = backtrack[-1]
            grid[y][x] = EMPTY
            possible_directions = []
            if y >= 3 and grid[y - 2][x] == UNEXPLORED:
                possible_directions.append((x, y - 2))
            if y <= size - 3 and grid[y + 2][x] == UNEXPLORED:
                possible_directions.append((x, y + 2))
            if x >= 3 and grid[y][x - 2] == UNEXPLORED:
                possible_directions.append((x - 2, y))
            if x <= size - 3 and grid[y][x + 2] == UNEXPLORED:
                possible_directions.append((x + 2, y))
            if len(possible_directions) == 0:
                backtrack.pop()
            else:
                shuffle(possible_directions)
                new_x, new_y = possible_directions.pop()
                grid[(y + new_y) // 2][(x + new_x) // 2] = EMPTY

                # On ajoute quelques chemins de traverse
                if len(possible_directions) > 0 and random() < 0.2:
                    other_x, other_y = possible_directions.pop()
                    grid[(y + other_y) // 2][(x + other_x) // 2] = EMPTY

                backtrack.append((new_x, new_y))

        # On ajoute des items
        coords = [
            (x, y) for x in range(1, size) for y in range(1, size) if x != 1 and y != 1
        ]
        shuffle(coords)
        items = [SPEEDBOOST, SPEEDPENALTY, COIN, SUPER_FIREBALL]
        while len(coords) > 0:
            x, y = coords.pop()
            if grid[y][x] == EMPTY:
                grid[y][x] = items.pop()
            if len(items) == 0:
                break

        # On fait une belle grille symétrique
        grid.pop()
        for row in grid:
            row.pop()

        wall = [
            [WALL if i % 2 == 0 or random() < 0.5 else EMPTY for i in range(size - 3)]
            + [WALL, EMPTY]
        ]
        wallr = rotate(wall)

        op1 = rotate
        op2 = rotate2

        if random() < 0.5:
            op1 = hmirror
            op2 = vmirror

        top = hstack(grid, hstack(wallr, op1(grid)))

        return vstack(
            top,
            vstack(
                hstack(
                    wall,
                    hstack([[WALL]], rotate(wallr)),
                ),
                op2(top),
            ),
        )


if __name__ == "__main__":
    from pprint import pprint

    pprint(Map().grid)
