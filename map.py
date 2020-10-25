from random import shuffle, random

EMPTY = 0
WALL = 1
UNEXPLORED = 19

SPEEDBOOST = 21
SPEEDPENALTY = 22

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

        grid.pop()
        wall = [
            [WALL, EMPTY]
            + [WALL if i % 2 == 0 or random() < 0.5 else EMPTY for i in range(size - 3)]
        ]
        wallr = rotate(wall)
        for row in grid:
            row.pop()

        top = hstack(grid, hstack(wallr, rotate(grid)))

        return vstack(
            top,
            vstack(
                hstack(
                    wall,
                    hstack([[WALL]], rotate(wallr)),
                ),
                rotate(rotate(top)),
            ),
        )


if __name__ == "__main__":
    from pprint import pprint

    pprint(Map().grid)
