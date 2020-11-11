from tkinter import Canvas as tkCanvas, PhotoImage, DoubleVar, NW, HORIZONTAL
from math import floor
from tkinter.ttk import Scale, Label

from map import (
    WALL,
    LAVA,
    PLAYER_RED,
    PLAYER_BLUE,
    PLAYER_YELLOW,
    PLAYER_GREEN,
    SPEEDBOOST,
    SPEEDPENALTY,
    SUPER_FIREBALL,
    COIN,
    SHIELD,
    FLOOR,
    DAMAGED_FLOOR,
)

from entities import Player, Fireball, CollectableEntity


def floor_const_to_str(f):
    if f == FLOOR:
        return "floor"
    if f == WALL:
        return "wall"
    if f == LAVA:
        return "lava"
    if f == DAMAGED_FLOOR:
        return "damaged_floor"
    raise KeyError("Constante inconnue")


def player_const_to_str(p):
    """
    Transforme un constante `PLAYER_*` en `"*"`.
    """
    if p == PLAYER_RED:
        return "red"
    if p == PLAYER_BLUE:
        return "blue"
    if p == PLAYER_YELLOW:
        return "yellow"
    if p == PLAYER_GREEN:
        return "green"
    raise KeyError("Constante inconnue")


def collectible_const_to_str(c):
    if c == SPEEDBOOST:
        return "speedboost"
    if c == SPEEDPENALTY:
        return "speedpenalty"
    if c == COIN:
        return "coin"
    if c == SUPER_FIREBALL:
        return "super_fireball"
    if c == SHIELD:
        return "shield"
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
        self.canvas.grid(column=0, row=0, rowspan=3)

        self.slider_var = DoubleVar(value=1.0)
        self.label = Label(text="x 1.0")
        self.label2 = Label(text="0 s")
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
        self.slider.grid(column=1, row=0, sticky="NSEW")
        self.label.grid(column=1, row=1, sticky="NSEW")
        self.label2.grid(column=1, row=2, sticky="NSEW")

        self.master.columnconfigure(0, weight=0)
        self.master.columnconfigure(1, weight=1)

        self.fireballs = {}
        self.fireball_hitboxes = {}
        self.players = {}
        self.player_hitboxes = {}
        self.collectibles = {}
        self.shielded_players = set()

        self.assets = {}
        self.assets["floor"] = PhotoImage(file="./assets/empty.png")
        self.assets["wall"] = PhotoImage(file="./assets/wall.png")
        self.assets["lava"] = PhotoImage(file="./assets/lava.png")
        self.assets["damaged_floor"] = PhotoImage(file="./assets/damaged_ground.png")
        self.assets["player_red"] = PhotoImage(file="./assets/player_red.png")
        self.assets["player_red_shield"] = PhotoImage(
            file="./assets/player_red_shield.png"
        )
        self.assets["player_blue"] = PhotoImage(file="./assets/player_blue.png")
        self.assets["player_blue_shield"] = PhotoImage(
            file="./assets/player_blue_shield.png"
        )
        self.assets["player_yellow"] = PhotoImage(file="./assets/player_yellow.png")
        self.assets["player_yellow_shield"] = PhotoImage(
            file="./assets/player_yellow_shield.png"
        )
        self.assets["player_green"] = PhotoImage(file="./assets/player_green.png")
        self.assets["player_green_shield"] = PhotoImage(
            file="./assets/player_green_shield.png"
        )
        self.assets["hitbox_red"] = PhotoImage(file="./assets/hitbox_red.png")
        self.assets["hitbox_blue"] = PhotoImage(file="./assets/hitbox_blue.png")
        self.assets["hitbox_yellow"] = PhotoImage(file="./assets/hitbox_yellow.png")
        self.assets["hitbox_green"] = PhotoImage(file="./assets/hitbox_green.png")
        self.assets["fireball"] = PhotoImage(file="./assets/fireball.png")
        self.assets["hitbox_fireball"] = PhotoImage(file="./assets/hitbox_fireball.png")
        self.assets["speedboost"] = PhotoImage(file="./assets/speedboost.png")
        self.assets["speedpenalty"] = PhotoImage(file="./assets/hourglass.png")
        self.assets["coin"] = PhotoImage(file="./assets/coin.png")
        self.assets["super_fireball"] = PhotoImage(file="./assets/super_fireball.png")
        self.assets["shield"] = PhotoImage(file="./assets/shield.png")

    def draw_map(self, game):
        """
        Affiche le fond de la zone de jeu.
        """
        background = game.background
        size = self.TILE_SIZE * game.map.size
        self.canvas.config(width=size, height=size)
        self.grid = [[None] * game.map.size for _ in range(game.map.size)]
        for y in range(game.map.size):
            for x in range(game.map.size):
                image = self.assets[floor_const_to_str(background[y][x])]
                self.grid[y][x] = (
                    background[y][x],
                    self.canvas.create_image(
                        x * self.TILE_SIZE,
                        y * self.TILE_SIZE,
                        image=image,
                        anchor=NW,
                        tags="background",
                    ),
                )

    def draw_players(self, game):
        """Dessine les joueurs."""
        return game

    def update(self, game):
        """Met à jour la zone de jeu."""
        self.label2.config(text=str(floor(10.0 * game.t) / 10.0) + " s")
        # La map
        changed = False
        for y in range(game.map.size):
            for x in range(game.map.size):
                grid_id, image_id = self.grid[y][x]
                if grid_id != game.background[y][x]:
                    changed = True
                    self.canvas.delete(image_id)
                    image = self.assets[floor_const_to_str(game.background[y][x])]
                    self.grid[y][x] = (
                        game.background[y][x],
                        self.canvas.create_image(
                            x * self.TILE_SIZE,
                            y * self.TILE_SIZE,
                            image=image,
                            anchor=NW,
                            tags="background",
                        ),
                    )
        if changed:
            self.canvas.lower("background")

        # Les items
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

        # Les joueurs
        diff = set(self.players.values())
        diff_hitboxes = set(self.player_hitboxes.values())
        for p in filter(lambda e: isinstance(e, Player), game.entities):
            if p not in self.players:
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
                diff.add(self.players[p])
                diff_hitboxes.add(self.player_hitboxes[p])
            if p.shield and p not in self.shielded_players:
                self.players[p] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets[
                            "player_" + player_const_to_str(p.color) + "_shield"
                        ],
                        anchor=NW,
                    ),
                )
                self.shielded_players.add(p)
                diff.add(self.players[p])
            elif not p.shield and p in self.shielded_players:
                self.players[p] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["player_" + player_const_to_str(p.color)],
                        anchor=NW,
                    ),
                )
                self.shielded_players.remove(p)
                diff.add(self.players[p])

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

        # Les boules de feu
        diff = set(self.fireballs.values())
        diff_hitboxes = set(self.fireball_hitboxes.values())
        for fireball in filter(lambda e: isinstance(e, Fireball), game.entities):
            if fireball not in self.fireballs:
                self.fireballs[fireball] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["fireball"],
                        anchor=NW,
                    ),
                )
                self.fireball_hitboxes[fireball] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["hitbox_fireball"],
                        anchor=NW,
                    ),
                )
            else:
                diff.remove(self.fireballs[fireball])
                diff_hitboxes.remove(self.fireball_hitboxes[fireball])
            self.canvas.moveto(
                self.fireballs[fireball],
                int(fireball.get_visual_x() * 32),
                int(fireball.get_visual_y() * 32),
            )
            self.canvas.moveto(
                self.fireball_hitboxes[fireball],
                int(fireball.x * 32),
                int(fireball.y * 32),
            )

        self.canvas.delete(*diff)
        self.canvas.delete(*diff_hitboxes)
