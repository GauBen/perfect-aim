"""Gestion de l'affichage du jeu."""

from tkinter import Canvas as tkCanvas, PhotoImage, DoubleVar, NW, HORIZONTAL
from math import floor
from tkinter.ttk import Scale, Label, Frame, Progressbar

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


def const_to_str(f):  # noqa
    """Transforme une constante en clé de dictionnaire."""
    if f == FLOOR:
        return "floor"
    if f == WALL:
        return "wall"
    if f == LAVA:
        return "lava"
    if f == DAMAGED_FLOOR:
        return "damaged_floor"
    if f == PLAYER_RED:
        return "red"
    if f == PLAYER_BLUE:
        return "blue"
    if f == PLAYER_YELLOW:
        return "yellow"
    if f == PLAYER_GREEN:
        return "green"
    if f == SPEEDBOOST:
        return "speedboost"
    if f == SPEEDPENALTY:
        return "speedpenalty"
    if f == COIN:
        return "coin"
    if f == SUPER_FIREBALL:
        return "super_fireball"
    if f == SHIELD:
        return "shield"
    raise KeyError("Constante inconnue")


class Gui:
    """Gestion de l'affichage de Perfect Aim."""

    def __init__(self, master):
        """Initialise la fenêtre tkinter."""
        self.TILE_SIZE = 32

        self.master = master
        master.title("Perfect Aim")

        self.canvas = tkCanvas(master, background="#eee")
        self.canvas.grid(column=0, row=0, columnspan=3)

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
        self.slider.grid(column=0, row=1, sticky="NSEW")
        self.label.grid(column=1, row=1, sticky="NSEW")
        self.label2.grid(column=2, row=1, sticky="NSEW")

        # self.master.columnconfigure(0, weight=0)
        # self.master.columnconfigure(1, weight=1)

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
        """Affiche le fond de la zone de jeu."""
        background = game.background
        size = self.TILE_SIZE * game.map.size
        self.canvas.config(width=size, height=size)
        self.grid = [[None] * game.map.size for _ in range(game.map.size)]
        for y in range(game.map.size):
            for x in range(game.map.size):
                image = self.assets[const_to_str(background[y][x])]
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

    def _player_string(self, player):
        return (
            f"Vitesse {player.speed} / "
            f"Fireballs {player.super_fireball} / "
            f"Coins {player.coins}"
        )

    def draw_players(self, game):

        self.player_panels_data = []
        self.player_panels_frame = Frame(self.master)

        for i in range(len(game.players)):

            data = {}
            player_panel_frame = Frame(self.player_panels_frame, padding=10)
            self.player_panels_data.append(data)

            player = game.players[i]

            label = Label(player_panel_frame, text=player.get_name())
            data["label"] = label

            bar = Progressbar(player_panel_frame, maximum=1.0)
            data["bar"] = bar

            label2 = Label(
                player_panel_frame,
                text=self._player_string(player),
            )
            data["label2"] = label2

            label.grid(row=0, column=0)
            label2.grid(row=1, column=0, sticky="EW")
            bar.grid(row=2, column=0, sticky="EW")
            player_panel_frame.grid(row=i, column=0, sticky="EW")
            player_panel_frame.columnconfigure(0, weight=1)

        self.player_panels_frame.grid(column=3, row=0, rowspan=2, sticky="EW")

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
                    image = self.assets[const_to_str(game.background[y][x])]
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
                        image=self.assets[const_to_str(collectible.grid_id)],
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
        for p in range(len(game.players)):
            self.player_panels_data[p]["bar"].config(
                value=game.players[p].action_progress
            )
            self.player_panels_data[p]["label2"].config(
                text=self._player_string(game.players[p])
            )

        diff = set(self.players.values())
        diff_hitboxes = set(self.player_hitboxes.values())
        for p in filter(lambda e: isinstance(e, Player), game.entities):
            if p not in self.players:
                self.players[p] = (
                    self.canvas.create_image(
                        self.TILE_SIZE,
                        self.TILE_SIZE,
                        image=self.assets["player_" + const_to_str(p.color)],
                        anchor=NW,
                    ),
                )
                self.player_hitboxes[p] = self.canvas.create_image(
                    self.TILE_SIZE,
                    self.TILE_SIZE,
                    image=self.assets["hitbox_" + const_to_str(p.color)],
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
                            "player_" + const_to_str(p.color) + "_shield"
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
                        image=self.assets["player_" + const_to_str(p.color)],
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
