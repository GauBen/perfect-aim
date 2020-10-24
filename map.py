EMPTY = 0
WALL = 1

PLAYER_RED = 10
PLAYER_BLUE = 11


class Map:
    def __init__(self):
        self.size = 4
        self.grid = [[WALL] * self.size]
        for i in range(self.size - 2):
            self.grid.append([WALL] + [EMPTY] * (self.size - 2) + [WALL])
        self.grid.append([WALL] * self.size)
