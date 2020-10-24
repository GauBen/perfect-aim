from tkinter import Canvas as tkCanvas, PhotoImage, DoubleVar, NW, HORIZONTAL

from tkinter.ttk import Scale, Label

from map import WALL


class Gui:
    def __init__(self, master):
        self.TILE_SIZE = 32

        self.master = master
        master.title("Perfect Aim")

        self.canvas = tkCanvas(master, background="#eee")
        self.canvas.pack()

        self.slider_var = DoubleVar(value=1.0)
        self.label = Label(text="x 1.0")
        self.slider = Scale(
            master,
            from_=0.0,
            to=10.0,
            orient=HORIZONTAL,
            variable=self.slider_var,
            command=lambda x: self.label.config(
                text="Paused"
                if self.slider_var.get() == 0
                else "x " + str(round(self.slider_var.get(), 1))
            ),
        )
        self.slider.pack()
        self.label.pack()

        self.arrows = {}
        self.arrow_hitboxes = {}

        self.assets = {}
        self.assets["empty"] = PhotoImage(file="./assets/empty.png")
        self.assets["wall"] = PhotoImage(file="./assets/wall.png")
        self.assets["player_red"] = PhotoImage(file="./assets/player_red.png")
        self.assets["player_blue"] = PhotoImage(file="./assets/player_blue.png")
        self.assets["hitbox_red"] = PhotoImage(file="./assets/hitbox_red.png")
        self.assets["hitbox_blue"] = PhotoImage(file="./assets/hitbox_blue.png")
        self.assets["arrow"] = PhotoImage(file="./assets/arrow.png")
        self.assets["hitbox_arrow"] = PhotoImage(file="./assets/hitbox_arrow.png")

    def draw_map(self, map):
        size = self.TILE_SIZE * map.size
        self.canvas.config(width=size, height=size)
        for y in range(map.size):
            for x in range(map.size):
                image = (
                    self.assets["wall"]
                    if map.grid[y][x] == WALL
                    else self.assets["empty"]
                )
                self.canvas.create_image(
                    x * self.TILE_SIZE, y * self.TILE_SIZE, image=image, anchor=NW
                )

    def draw_players(self):
        self.players = [
            self.canvas.create_image(
                self.TILE_SIZE,
                self.TILE_SIZE,
                image=self.assets["player_red"],
                anchor=NW,
            ),
            self.canvas.create_image(
                self.TILE_SIZE,
                self.TILE_SIZE,
                image=self.assets["player_blue"],
                anchor=NW,
            ),
        ]
        self.player_hitboxes = [
            self.canvas.create_image(
                self.TILE_SIZE,
                self.TILE_SIZE,
                image=self.assets["hitbox_red"],
                anchor=NW,
            ),
            self.canvas.create_image(
                self.TILE_SIZE,
                self.TILE_SIZE,
                image=self.assets["hitbox_blue"],
                anchor=NW,
            ),
        ]

    def update(self, game):
        for i in range(len(game.players)):
            self.canvas.moveto(
                self.players[i],
                int(game.players[i].get_visual_x() * 32),
                int(game.players[i].get_visual_y() * 32),
            )
            self.canvas.moveto(
                self.player_hitboxes[i],
                int(game.players[i].x * 32),
                int(game.players[i].y * 32),
            )

        diff = set(self.arrows.values())
        diff_hitboxes = set(self.arrow_hitboxes.values())
        for arrow in game.arrows:
            if arrow not in self.arrows:
                self.arrows[arrow] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["arrow"],
                        anchor=NW,
                    ),
                )
                self.arrow_hitboxes[arrow] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["hitbox_arrow"],
                        anchor=NW,
                    ),
                )
            else:
                diff.remove(self.arrows[arrow])
                diff_hitboxes.remove(self.arrow_hitboxes[arrow])
            self.canvas.moveto(
                self.arrows[arrow],
                int(arrow.get_visual_x() * 32),
                int(arrow.get_visual_y() * 32),
            )
            self.canvas.moveto(
                self.arrow_hitboxes[arrow],
                int(arrow.x * 32),
                int(arrow.y * 32),
            )

        self.canvas.delete(*diff)
        self.canvas.delete(*diff_hitboxes)
