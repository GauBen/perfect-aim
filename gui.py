"""Gestion de l'affichage du jeu."""

import time
import tkinter
import tkinter.ttk as ttk
from copy import deepcopy
from typing import List, Optional, Type, Union

import entities
import game
from game import Action
from gamegrid import Tile
import players


class Delta:
    """Temp."""

    def __init__(self):
        """Temp."""
        self.last = time.perf_counter()

    def delta(self) -> float:
        """Temp."""
        t = time.perf_counter()
        out = t - self.last
        self.last = t
        return out


delta = Delta().delta


class AssetsManager:
    """Gestionnaire des ressources graphiques."""

    TILE_SIZE = 32  # pixels

    def __init__(self):
        """Charge toutes les ressources du jeu."""
        self.asset_floor = tkinter.PhotoImage(file="./assets/empty.png")
        self.asset_lava = tkinter.PhotoImage(file="./assets/lava.png")
        self.asset_damaged_floor = tkinter.PhotoImage(
            file="./assets/damaged_ground.png"
        )

        self.asset_hitbox_red = tkinter.PhotoImage(file="./assets/hitbox_red.png")
        self.asset_hitbox_blue = tkinter.PhotoImage(file="./assets/hitbox_blue.png")
        self.asset_hitbox_yellow = tkinter.PhotoImage(file="./assets/hitbox_yellow.png")
        self.asset_hitbox_green = tkinter.PhotoImage(file="./assets/hitbox_green.png")
        self.asset_hitbox_fireball = tkinter.PhotoImage(
            file="./assets/hitbox_fireball.png"
        )
        self.asset_speedboost = tkinter.PhotoImage(file="./assets/speedboost.png")
        self.asset_speedpenalty = tkinter.PhotoImage(file="./assets/hourglass.png")
        self.asset_coin = tkinter.PhotoImage(file="./assets/coin.png")
        self.asset_super_fireball = tkinter.PhotoImage(
            file="./assets/super_fireball.png"
        )
        self.asset_shield = tkinter.PhotoImage(file="./assets/shield.png")

        self.walls: List[tkinter.PhotoImage] = []
        for i in range(16):
            suffix = (
                ("-" if i else "")
                + ("n" if i & 1 else "")
                + ("s" if i & 2 else "")
                + ("w" if i & 4 else "")
                + ("e" if i & 8 else "")
            )
            self.walls.append(
                tkinter.PhotoImage(file=f"./assets/walls/wall{suffix}.png")
            )

        c = {
            Tile.PLAYER_RED: "red",
            Tile.PLAYER_BLUE: "blue",
            Tile.PLAYER_YELLOW: "yellow",
            Tile.PLAYER_GREEN: "green",
        }
        d = {
            Action.WAIT: "i",
            Action.MOVE_UP: "n",
            Action.MOVE_DOWN: "s",
            Action.MOVE_LEFT: "w",
            Action.MOVE_RIGHT: "e",
        }
        self.players = {
            player: {
                action: [
                    tkinter.PhotoImage(
                        file=f"./assets/players/{c[player]}-{d[action]}{i}.png"
                    )
                    for i in (1, 2)
                ]
                for action in d
            }
            for player in c
        }
        self.shielded_players = {
            player: [
                tkinter.PhotoImage(file=f"./assets/players/{c[player]}-shield-{i}.png")
                for i in ("i", "1", "2")
            ]
            for player in c
        }
        self.dead = tkinter.PhotoImage(file=f"./assets/players/dead.png")

        d = {
            Action.MOVE_UP: "n",
            Action.MOVE_DOWN: "s",
            Action.MOVE_LEFT: "w",
            Action.MOVE_RIGHT: "e",
        }
        self.fireball = {
            action: [
                tkinter.PhotoImage(
                    file=f"./assets/fireballs/fireball-{d[action]}{i}.png"
                )
                for i in (1, 2)
            ]
            for action in d
        }

    def tile(self, background: List[List[Tile]], x: int, y: int) -> tkinter.PhotoImage:
        """Renvoie l'image correspondante."""
        tile = background[y][x]
        if tile == Tile.FLOOR:
            return self.asset_floor
        if tile == Tile.WALL:

            neighbors = 0
            if y > 0 and background[y - 1][x] == Tile.WALL:
                neighbors |= 1
            if y < len(background) - 1 and background[y + 1][x] == Tile.WALL:
                neighbors |= 2
            if x > 0 and background[y][x - 1] == Tile.WALL:
                neighbors |= 4
            if x < len(background[y]) - 1 and background[y][x + 1] == Tile.WALL:
                neighbors |= 8
            return self.walls[neighbors]

        if tile == Tile.LAVA:
            return self.asset_lava
        if tile == Tile.DAMAGED_FLOOR:
            return self.asset_damaged_floor
        raise KeyError("Constante inconnue")

    def entity(self, entity: entities.Entity) -> tkinter.PhotoImage:  # noqa
        """Renvoie l'image correspondante."""
        if isinstance(entity, entities.PlayerEntity):
            if entity.shield:
                return self.shielded_players[entity.TILE][
                    0
                    if entity.action == Action.WAIT
                    else int(entity.action_progress * 4) % 2 + 1
                ]
            return self.players[entity.TILE][entity.action.movement()][
                int(entity.action_progress * 4) % 2
                if not entity.action.is_attack()
                else 0
            ]
        if isinstance(entity, entities.Fireball):
            return self.fireball[entity.action][int(entity.action_progress * 4) % 2]

        if entity.TILE == Tile.SPEEDBOOST:
            return self.asset_speedboost
        if entity.TILE == Tile.SPEEDPENALTY:
            return self.asset_speedpenalty
        if entity.TILE == Tile.COIN:
            return self.asset_coin
        if entity.TILE == Tile.SUPER_FIREBALL:
            return self.asset_super_fireball
        if entity.TILE == Tile.SHIELD:
            return self.asset_shield
        raise KeyError("Constante inconnue")

    def player_icon(self, player: game.Player):
        """L'icone associée au joueur, avec ou sans bouclier."""
        if player.dead:
            return self.dead
        if player.shield:
            return self.shielded_players[player.color][0]
        return self.players[player.color][Action.WAIT][1]

    def entity_hitbox(self, entity: entities.Entity) -> tkinter.PhotoImage:  # noqa
        """Renvoie l'image correspondante."""
        if entity.TILE == Tile.PLAYER_RED:
            return self.asset_hitbox_red
        if entity.TILE == Tile.PLAYER_BLUE:
            return self.asset_hitbox_blue
        if entity.TILE == Tile.PLAYER_YELLOW:
            return self.asset_hitbox_yellow
        if entity.TILE == Tile.PLAYER_GREEN:
            return self.asset_hitbox_green
        if entity.TILE == Tile.SPEEDBOOST:
            return self.asset_hitbox_fireball
        if entity.TILE == Tile.SPEEDPENALTY:
            return self.asset_hitbox_fireball
        if entity.TILE == Tile.COIN:
            return self.asset_hitbox_fireball
        if entity.TILE == Tile.SUPER_FIREBALL:
            return self.asset_hitbox_fireball
        if entity.TILE == Tile.SHIELD:
            return self.asset_hitbox_fireball
        if entity.TILE == Tile.FIREBALL:
            return self.asset_hitbox_fireball
        raise KeyError("Constante inconnue")


class PlayerPanel:
    """Panneau des statistiques d'un joueur."""

    def __init__(
        self,
        assets_manager: AssetsManager,
        frame: ttk.Frame,
        i: int,
        player: game.Player,
    ):
        """Initialise les éléments tkinter."""
        self.assets_manager = assets_manager
        self.player = player

        self.player_icon = ttk.Label(
            frame, image=self.assets_manager.player_icon(self.player)
        )
        self.player_label = ttk.Label(frame, text=self.player.NAME)
        self.speed_icon = ttk.Label(frame, image=self.assets_manager.asset_speedboost)
        self.speed_label = ttk.Label(frame, text=f"{self.player.speed:.2f}")
        self.super_fireball_icon = ttk.Label(
            frame, image=self.assets_manager.asset_super_fireball
        )
        self.super_fireball_label = ttk.Label(
            frame, text=f"{self.player.super_fireballs}"
        )
        self.coin_icon = ttk.Label(frame, image=self.assets_manager.asset_coin)
        self.coin_label = ttk.Label(frame, text=f"{self.player.coins}")
        self.action_label = ttk.Label(frame, text=self.player.action.value)
        self.action_bar = ttk.Progressbar(frame, length=1, max=1.0, value=0.0)

        # Offset vertical
        n = i * 4
        if i > 0:
            ttk.Separator(frame, orient=tkinter.HORIZONTAL).grid(
                row=n, column=0, columnspan=6, sticky=tkinter.EW, padx=16
            )
            n += 1
        self.player_icon.grid(row=n + 0, column=0, padx=(0, 8), pady=(16, 2))
        self.player_label.grid(
            row=n + 0, column=1, columnspan=5, sticky=tkinter.W, pady=(16, 2)
        )
        self.speed_icon.grid(row=n + 1, column=0, padx=(0, 8), pady=2)
        self.speed_label.grid(
            row=n + 1, column=1, sticky=tkinter.W, padx=(0, 8), pady=2
        )
        self.super_fireball_icon.grid(row=n + 1, column=2, padx=8, pady=2)
        self.super_fireball_label.grid(
            row=n + 1, column=3, sticky=tkinter.W, padx=(0, 8), pady=2
        )
        self.coin_icon.grid(row=n + 1, column=4, padx=8, pady=2)
        self.coin_label.grid(row=n + 1, column=5, sticky=tkinter.W, padx=(0, 8), pady=2)
        self.action_label.grid(row=n + 2, column=0, columnspan=4, padx=4, pady=(2, 16))
        self.action_bar.grid(
            row=n + 2, column=4, columnspan=2, sticky=tkinter.EW, padx=4, pady=(2, 16)
        )

    def update(self):
        """Met à jour le panneau."""
        self.player_icon.configure(image=self.assets_manager.player_icon(self.player))
        self.speed_label.configure(text=f"{self.player.speed:.2f}")
        self.super_fireball_label.configure(text=f"{self.player.super_fireballs}")
        self.coin_label.configure(text=f"{self.player.coins}")
        self.action_label.configure(text=self.player.action.value)
        self.action_bar.configure(value=self.player.action_progress)


class GameInterface:
    """Affiche une partie de Perfect Aim."""

    def __init__(
        self, master: tkinter.Tk, assets_manager: AssetsManager, game: game.Game
    ):
        """Initialise la fenêtre tk."""
        self.master = master
        self.assets_manager = assets_manager
        self.game = game

        # Ouverture et fermeture de la fenêtre
        self.window = tkinter.Toplevel(self.master)
        self.window.title("Perfect Aim")
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.master.destroy())

        # Widgets
        self.create_widgets()

        # Premier affichage
        self.draw_background()
        self.update()

    def start(self):
        """Lance la boucle du jeu."""

        def update():
            """Temp."""
            u = delta()
            # print(u)
            dt = u * self.time_scale_var.get()
            if dt > 0:
                self.game.update(dt)
            self.update()
            if not self.game.over:
                self.master.after(10, update)

        delta()
        update()

    def update(self):
        """Met à jour la fenêtre."""
        # Le timer
        self.time_label.config(text=f"{self.game.t:.1f} s")

        # Les stats
        for p in self.player_panels:
            p.update()

        # Le terrain
        if self.background != self.game.background:
            self.draw_background()

        # Les entités
        self.draw_entities()

    def create_widgets(self):
        """Crée les widgets tk dans la fenêtre du jeu."""
        # Canvas
        size = self.assets_manager.TILE_SIZE * self.game.size
        self.canvas = tkinter.Canvas(
            self.window, background="#eee", width=size, height=size
        )
        self.canvas.grid(column=0, row=0, columnspan=3)

        # Gestion du temps en bas
        self.time_scale_label = ttk.Label(self.window, text="x 1.0")
        self.time_label = ttk.Label(self.window, text="0 s")
        self.time_scale_var = tkinter.DoubleVar(value=1.0)
        self.time_scale = ttk.Scale(
            self.window,
            from_=0.0,
            to=10.0,
            orient=tkinter.HORIZONTAL,
            variable=self.time_scale_var,
            command=lambda _: self.time_scale_label.config(
                text="Paused" if (x := self.time_scale_var.get()) == 0 else f"x {x:.1f}"
            ),
        )
        self.time_scale.grid(column=0, row=1, sticky=tkinter.NSEW)
        self.time_scale_label.grid(column=1, row=1, sticky=tkinter.NSEW)
        self.time_label.grid(column=2, row=1, sticky=tkinter.NSEW)

        # Les joueurs sur le côté
        self.player_panels_frame = ttk.Frame(self.window, padding=16)
        self.player_panels_frame.grid(column=3, row=0, rowspan=2, sticky=tkinter.EW)
        self.player_panels_frame.grid_columnconfigure(1, weight=1)
        self.player_panels_frame.grid_columnconfigure(3, weight=1)
        self.player_panels_frame.grid_columnconfigure(5, weight=1)
        self.window.grid_columnconfigure(3, weight=1)

        self.player_panels = [
            PlayerPanel(
                self.assets_manager,
                self.player_panels_frame,
                i,
                self.game.players[i],
            )
            for i in range(len(self.game.players))
        ]

    def draw_background(self):
        """Dessine le fond du plateau."""
        self.background = deepcopy(self.game.background)
        self.canvas.delete("background")
        for y in range(self.game.size):
            for x in range(self.game.size):
                self.canvas.create_image(
                    x * self.assets_manager.TILE_SIZE,
                    y * self.assets_manager.TILE_SIZE,
                    image=self.assets_manager.tile(self.background, x, y),
                    anchor=tkinter.NW,
                    tags="background",
                )
        self.canvas.lower("background")

    def draw_entities(self):
        """Dessine les entités."""
        self.canvas.delete("entities")
        self.canvas.delete("hitboxes")
        for entity in sorted(self.game.entities.copy(), key=lambda entity: entity.TILE):
            # if isinstance(entity, entities.MovingEntity):
            #     self.canvas.create_image(
            #         entity.x * self.assets_manager.TILE_SIZE,
            #         entity.y * self.assets_manager.TILE_SIZE,
            #         image=self.assets_manager.entity_hitbox(entity),
            #         anchor=tkinter.NW,
            #         tags="hitboxes",
            #     )
            self.canvas.create_image(
                int(entity.visual_x * self.assets_manager.TILE_SIZE),
                int(entity.visual_y * self.assets_manager.TILE_SIZE),
                image=self.assets_manager.entity(entity),
                anchor=tkinter.NW,
                tags="entities",
            )


class PlayerSelector:
    """Une icone et une combobox de choix de joueur."""

    def __init__(
        self,
        assets_manager: AssetsManager,
        players: List[Union[None, game.Player]],
        frame: ttk.Frame,
        i: int,
    ):
        """Crée les widgets tkinter."""
        self.player_constructors = players
        self.assets_manager = assets_manager
        color = [
            Tile.PLAYER_RED,
            Tile.PLAYER_BLUE,
            Tile.PLAYER_YELLOW,
            Tile.PLAYER_GREEN,
        ][i]
        self.icon = ttk.Label(
            frame,
            image=self.assets_manager.players[color][Action.WAIT][1],
        )
        self.combobox = ttk.Combobox(
            frame,
            values=tuple(c.NAME for c in self.player_constructors) + ("<aucun>",),
            state="readonly",
        )
        self.combobox.current(i % len(self.player_constructors))
        self.icon.grid(row=i + 1, column=0, padx=8, pady=4)
        self.combobox.grid(row=i + 1, column=1, padx=8, pady=4)

    @property
    def selected_constructor(self) -> Optional[Type[game.Player]]:
        """Constructeur du joueur choisi."""
        value = self.combobox.get()
        for c in self.player_constructors:
            if c.NAME == value:
                return c
        return None


class GameLauncher:
    """Lanceur du jeu, affiche la sélection des joueurs."""

    def __init__(self):
        """Initialise la fenêtre principale de tkinter."""
        self.master = tkinter.Tk()
        self.master.title("Perfect Aim")

        self.assets_manager = AssetsManager()
        self.player_constructors = players.list_player_constructors()

        self.game_launched = False
        self.create_launcher()

    def start(self):
        """Lance la boucle de tkinter."""
        self.master.mainloop()

    def create_launcher(self):
        """Crée la fenêtre de lancement du jeu."""
        # Cadre principal
        frame = ttk.Frame(self.master, padding=(32, 16))
        frame.grid(row=0, column=0)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        # Titre, cadre, bouton
        label_title = ttk.Label(frame, text="Perfect Aim", font=("", 24, "bold"))
        label_title.grid(row=0, column=0, columnspan=2)
        subframe = ttk.Frame(frame, padding=16)
        subframe.grid(row=1, column=0, columnspan=2)
        button_play_1 = ttk.Button(
            frame, text="Jouer une partie", command=self.play_1_callback
        )
        button_play_2020 = ttk.Button(
            frame, text="Jouer 2020 parties", command=self.play_2020_callback
        )
        button_play_1.grid(row=2, column=0, padx=8)
        button_play_2020.grid(row=2, column=1, padx=8)

        # Sélecteur
        self.selectors = []
        for i in range(game.Game.MAX_PLAYERS):
            selector = PlayerSelector(
                self.assets_manager, self.player_constructors, subframe, i
            )
            self.selectors.append(selector)

    def play_1_callback(self):
        """Quand le bouton 1 est appuyé."""
        players = [s.selected_constructor for s in self.selectors]
        n = sum(int(c is not None) for c in players)
        if not (game.Game.MIN_PLAYERS <= n <= game.Game.MAX_PLAYERS):
            return
        self.launch_one_game(players)

    def play_2020_callback(self):
        """Quand le bouton 2020 est appuyé."""
        players = [s.selected_constructor for s in self.selectors]
        n = sum(int(c is not None) for c in players)
        if not (game.Game.MIN_PLAYERS <= n <= game.Game.MAX_PLAYERS):
            return
        self.launch_many_games(players)

    def launch_one_game(self, players: List[Optional[Type[game.Player]]]):
        """Lance une partie."""
        if self.game_launched:
            return
        self.game_launched = True

        self.master.withdraw()
        g = game.Game(players)
        GameInterface(self.master, self.assets_manager, g).start()

    def launch_many_games(self, players: List[Optional[Type[game.Player]]]):
        """Lance 2020 parties simultanées."""
        if self.game_launched:
            return
        self.game_launched = True
