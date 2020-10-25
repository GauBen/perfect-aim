from tkinter import Canvas as tkCanvas, PhotoImage, DoubleVar, NW, HORIZONTAL

from tkinter.ttk import Scale, Label

from map import (
    WALL,
    PLAYER_RED,
    PLAYER_BLUE,
    PLAYER_YELLOW,
    PLAYER_GREEN,
    SPEEDBOOST,
    SPEEDPENALTY,
)

from entities import Player, Arrow, CollectableEntity


def player_const_to_str(p):
    """
    Transforme un constante `PLAYER_*` en `"*"`.
    """
    if p == PLAYER_RED:
        return "red"
    elif p == PLAYER_BLUE:
        return "blue"
    elif p == PLAYER_YELLOW:
        return "yellow"
    elif p == PLAYER_GREEN:
        return "green"
    raise KeyError("Constante inconnue")


def collectible_const_to_str(c):
    if c == SPEEDBOOST:
        return "speedboost"
    elif c == SPEEDPENALTY:
        return "speedpenalty"
    raise KeyError("Constante inconnue")


class Gui:
    """
    Gestion de l'affichage de Perfect Aim.
    """

    def __init__(self, master):
        """
        Initialise la fenêtre tkinter.
        """
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

        self.collectibles = {}

        self.assets = {}
        self.assets["empty"] = PhotoImage(file="./assets/empty.png")
        self.assets["wall"] = PhotoImage(file="./assets/wall.png")
        self.assets["player_red"] = PhotoImage(file="./assets/player_red.png")
        self.assets["player_blue"] = PhotoImage(file="./assets/player_blue.png")
        self.assets["player_yellow"] = PhotoImage(file="./assets/player_yellow.png")
        self.assets["player_green"] = PhotoImage(file="./assets/player_green.png")
        self.assets["hitbox_red"] = PhotoImage(file="./assets/hitbox_red.png")
        self.assets["hitbox_blue"] = PhotoImage(file="./assets/hitbox_blue.png")
        self.assets["hitbox_yellow"] = PhotoImage(file="./assets/hitbox_yellow.png")
        self.assets["hitbox_green"] = PhotoImage(file="./assets/hitbox_green.png")
        self.assets["arrow"] = PhotoImage(file="./assets/arrow.png")
        self.assets["hitbox_arrow"] = PhotoImage(file="./assets/hitbox_arrow.png")
        self.assets["speedboost"] = PhotoImage(file="./assets/speedboost.png")
        self.assets["speedpenalty"] = PhotoImage(file="./assets/hourglass.png")

    def draw_map(self, map):
        """
        Affiche le fond de la zone de jeu.
        """
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

    def draw_players(self, game):
        """
        Dessine les joueurs.
        """
        self.players = {}
        self.player_hitboxes = {}
        for p in filter(lambda e: isinstance(e, Player), game.entities):
            self.players[p] = (
                self.canvas.create_image(
                    self.TILE_SIZE,
                    self.TILE_SIZE,
                    image=self.assets["player_" + player_const_to_str(p.color)],
                    anchor=NW,
                ),
            )
            self.player_hitboxes[p] = self.canvas.create_image(
                self.TILE_SIZE,
                self.TILE_SIZE,
                image=self.assets["hitbox_" + player_const_to_str(p.color)],
                anchor=NW,
            )

    def update(self, game):
        """
        Met à jour la zone de jeu.
        """
        diff = set(self.collectibles.values())
        for collectible in filter(
            lambda e: isinstance(e, CollectableEntity), game.entities
        ):
            if collectible not in self.collectibles:
                self.collectibles[collectible] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets[
                            collectible_const_to_str(collectible.grid_id)
                        ],
                        anchor=NW,
                    ),
                )
                self.canvas.moveto(
                    self.collectibles[collectible],
                    int(collectible.x * 32),
                    int(collectible.y * 32),
                )
            else:
                diff.remove(self.collectibles[collectible])

        self.canvas.delete(*diff)

        diff = set(self.players.values())
        diff_hitboxes = set(self.player_hitboxes.values())
        for p in filter(lambda e: isinstance(e, Player), game.entities):
            self.canvas.moveto(
                self.players[p],
                int(p.get_visual_x() * 32),
                int(p.get_visual_y() * 32),
            )
            self.canvas.moveto(
                self.player_hitboxes[p],
                int(p.x * 32),
                int(p.y * 32),
            )
            diff.remove(self.players[p])
            diff_hitboxes.remove(self.player_hitboxes[p])

        self.canvas.delete(*diff)
        self.canvas.delete(*diff_hitboxes)

        diff = set(self.arrows.values())
        diff_hitboxes = set(self.arrow_hitboxes.values())
        for arrow in filter(lambda e: isinstance(e, Arrow), game.entities):
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
