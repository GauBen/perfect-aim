from random import choice

EMPTY = 0
WALL = 1
UNEXPLORED = -1

PLAYER_RED = 10
PLAYER_BLUE = 11


class Map:
    def __init__(self):
        self.size = 11
        self.grid = self.create_map(self.size)
        # self.grid = [[WALL] * self.size]
        # for i in range(self.size - 2):
        #     self.grid.append([WALL] + [EMPTY] * (self.size - 2) + [WALL])
        # self.grid.append([WALL] * self.size)

    @staticmethod
    def create_map(size):
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
                (new_x, new_y) = choice(possible_directions)
                grid[(y + new_y) // 2][(x + new_x) // 2] = EMPTY
                backtrack.append((new_x, new_y))

        return grid


if __name__ == "__main__":
    from pprint import pprint

    pprint(Map().grid)
