EMPTY = 0
WALL = 1


class Map:
    def __init__(self):
        self.size = 20
        self.grid = [[WALL] * self.size]
        for i in range(self.size - 2):
            self.grid.append([WALL] + [EMPTY] * (self.size - 2) + [WALL])
        self.grid.append([WALL] * self.size)
