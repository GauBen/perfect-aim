"""Gestion de l'affichage du jeu."""

from time import monotonic
from tkinter import EW, HORIZONTAL, NSEW, NW
from tkinter import Canvas as tkCanvas
from tkinter import DoubleVar, PhotoImage, Tk, Toplevel, W
from tkinter.ttk import Button, Frame, Label, Progressbar, Scale

from entities import (
    ATTACK_DOWN,
    ATTACK_LEFT,
    ATTACK_RIGHT,
    ATTACK_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    CollectableEntity,
    Fireball,
    Player,
)
from game import Game
from map import (
    COIN,
    DAMAGED_FLOOR,
    FLOOR,
    LAVA,
    PLAYER_BLUE,
    PLAYER_GREEN,
    PLAYER_RED,
    PLAYER_YELLOW,
    SHIELD,
    SPEEDBOOST,
    SPEEDPENALTY,
    SUPER_FIREBALL,
    WALL,
)
from players.indianaJones import IndianaJones


def action_to_str(action):
    """Version textuelle d'une action."""
    if action == MOVE_UP:
        return "Mvt haut"
    if action == MOVE_DOWN:
        return "Mvt bas"
    if action == MOVE_LEFT:
        return "Mvt gauche"
    if action == MOVE_RIGHT:
        return "Mvt droit"
    if action == ATTACK_UP:
        return "Atk haut"
    if action == ATTACK_DOWN:
        return "Atk bas"
    if action == ATTACK_LEFT:
        return "Atk gauche"
    if action == ATTACK_RIGHT:
        return "Atk droit"
    return "Attente"


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


class Delta:
    """Temp."""

    def __init__(self):
        """Temp."""
        self.last = monotonic()

    def delta(self):
        """Temp."""
        t = monotonic()
        out = t - self.last
        self.last = t
        return out


delta = Delta().delta


class Gui:
    """Gestion de l'affichage de Perfect Aim."""

    def __init__(self):
        """Initialise la fenêtre tkinter."""
        self.TILE_SIZE = 32
        self.master = Tk()
        Button(self.master, text="Play", command=self.play).pack(padx=10, pady=10)
        self.master.mainloop()

    def play(self):
        """Lance une nouvelle partie."""
        g = Game([IndianaJones, IndianaJones, IndianaJones, IndianaJones])
        self.master.withdraw()

        self.create_main_window(self.master)
        self.game_window.protocol("WM_DELETE_WINDOW", lambda: self.master.destroy())
        self.draw_map(g)
        self.draw_players(g)

        def update():
            """Temp."""
            dt = delta() * self.slider_var.get()
            if dt > 0:
                g.update(dt)
            delta()
            self.update(g)
            if not g.over:
                self.master.after(1000 // 60, update)

        delta()
        update()

    def create_main_window(self, master):
        """Crée la fenêtre principale du jeu."""
        self.game_window = Toplevel(master)
        master.title("Perfect Aim")

        self.canvas = tkCanvas(self.game_window, background="#eee")
        self.canvas.grid(column=0, row=0, columnspan=3)

        self.slider_var = DoubleVar(value=1.0)
        self.label = Label(self.game_window, text="x 1.0")
        self.label2 = Label(self.game_window, text="0 s")
        self.slider = Scale(
            self.game_window,
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
        self.slider.grid(column=0, row=1, sticky=NSEW)
        self.label.grid(column=1, row=1, sticky=NSEW)
        self.label2.grid(column=2, row=1, sticky=NSEW)

        self.fireballs = {}
        self.fireball_hitboxes = {}
        self.players = {}
        self.player_hitboxes = {}
        self.collectibles = {}
        self.shielded_players = set()

        self.create_assets()

    def create_assets(self):
        """Initialise les ressources du jeu."""
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

    def create_player_panel(self, player: Player, frame: Frame):
        """Crée le panneau des statistiques d'un joueur."""
        widgets = {}
        widgets["player_icon"] = Label(frame, image=self.assets["player_red"])
        widgets["player_label"] = Label(frame, text=player.get_name())
        widgets["speed_icon"] = Label(frame, image=self.assets["speedboost"])
        widgets["speed_label"] = Label(frame, text=f"{player.speed:.2f}")
        widgets["super_fireball_icon"] = Label(
            frame, image=self.assets["super_fireball"]
        )
        widgets["super_fireball_label"] = Label(frame, text=f"{player.super_fireball}")
        widgets["coin_icon"] = Label(frame, image=self.assets["coin"])
        widgets["coin_label"] = Label(frame, text=f"{player.coins}")
        widgets["action_label"] = Label(frame, text=action_to_str(player.action))
        widgets["action_bar"] = Progressbar(frame, length=1, max=1.0, value=0.0)

        widgets["player_icon"].grid(row=0, column=0)
        widgets["player_label"].grid(row=0, column=1, columnspan=5, sticky=W)
        widgets["speed_icon"].grid(row=1, column=0)
        widgets["speed_label"].grid(row=1, column=1, sticky=W)
        widgets["super_fireball_icon"].grid(row=1, column=2)
        widgets["super_fireball_label"].grid(row=1, column=3, sticky=W)
        widgets["coin_icon"].grid(row=1, column=4)
        widgets["coin_label"].grid(row=1, column=5, sticky=W)
        widgets["action_label"].grid(row=2, column=0, columnspan=4)
        widgets["action_bar"].grid(row=2, column=4, columnspan=2, sticky=EW, padx=8)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(5, weight=1)

        return widgets

    def update_player_panel(self, player: Player):
        """Met à jour le panneau des statistiques d'un joueur."""
        widgets = self.player_panels_data[player]
        widgets["speed_label"].configure(text=f"{player.speed:.2f}")
        widgets["super_fireball_label"].configure(text=f"{player.super_fireball}")
        widgets["coin_label"].configure(text=f"{player.coins}")
        widgets["action_label"].configure(text=action_to_str(player.action))
        widgets["action_bar"].configure(value=player.action_progress)

    def draw_players(self, game):
        """Dessine le panneau des statistiques."""
        self.player_panels_data = {}
        self.player_panels_frame = Frame(self.game_window)

        for i in range(len(game.players)):
            player_panel_frame = Frame(self.player_panels_frame, padding=10)
            self.player_panels_data[game.players[i]] = self.create_player_panel(
                game.players[i], player_panel_frame
            )
            player_panel_frame.grid(row=i, column=0, sticky=EW)

        self.player_panels_frame.grid(column=3, row=0, rowspan=2, sticky=EW)
        self.player_panels_frame.columnconfigure(0, weight=1)
        self.game_window.grid_columnconfigure(3, weight=1)

    def update(self, game):
        """Met à jour la zone de jeu."""
        self.label2.config(text=f"{game.t:.1f} s")
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
                    int(collectible.x * self.TILE_SIZE),
                    int(collectible.y * self.TILE_SIZE),
                )
            else:
                diff.remove(self.collectibles[collectible])

        self.canvas.delete(*diff)

        # Les joueurs
        for p in game.players:
            self.update_player_panel(p)

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
                int(p.get_visual_x() * self.TILE_SIZE),
                int(p.get_visual_y() * self.TILE_SIZE),
            )
            self.canvas.moveto(
                self.player_hitboxes[p],
                int(p.x * self.TILE_SIZE),
                int(p.y * self.TILE_SIZE),
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
                int(fireball.get_visual_x() * self.TILE_SIZE),
                int(fireball.get_visual_y() * self.TILE_SIZE),
            )
            self.canvas.moveto(
                self.fireball_hitboxes[fireball],
                int(fireball.x * self.TILE_SIZE),
                int(fireball.y * self.TILE_SIZE),
            )

        self.canvas.delete(*diff)
        self.canvas.delete(*diff_hitboxes)
