"""Gestion de l'affichage du jeu."""

import tkinter
import tkinter.ttk as ttk
from copy import deepcopy
from time import perf_counter
from typing import Callable, List, Optional, Type

import entities
import game
import players
from game import Action
from gamegrid import Tile


class AssetsManager:
    """Gestionnaire des ressources graphiques."""

    TILE_SIZE = 32  # pixels

    def __init__(self):
        """Charge toutes les ressources du jeu."""
        # Background
        self.floor = tkinter.PhotoImage(file="./assets/background/floor.png")
        self.lava = tkinter.PhotoImage(file="./assets/background/lava.png")
        self.damaged_floor = tkinter.PhotoImage(
            file="./assets/background/damaged-floor.png"
        )
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
                tkinter.PhotoImage(file=f"./assets/background/wall{suffix}.png")
            )

        # Players
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

        # Fireballs
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

        # Collectibles
        self.speedboost = tkinter.PhotoImage(
            file="./assets/collectibles/speedboost.png"
        )
        self.speedpenalty = tkinter.PhotoImage(
            file="./assets/collectibles/hourglass.png"
        )
        self.coin = tkinter.PhotoImage(file="./assets/collectibles/coin.png")
        self.super_fireball = tkinter.PhotoImage(
            file="./assets/collectibles/super_fireball.png"
        )
        self.shield = tkinter.PhotoImage(file="./assets/collectibles/shield.png")

    def tile(self, background: List[List[Tile]], x: int, y: int) -> tkinter.PhotoImage:
        """Renvoie l'image correspondante."""
        tile = background[y][x]
        if tile == Tile.FLOOR:
            return self.floor
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
            return self.lava
        if tile == Tile.DAMAGED_FLOOR:
            return self.damaged_floor
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
            return self.players[entity.TILE][entity.action.to_movement()][
                int(entity.action_progress * 4) % 2
                if not entity.action.is_attack()
                else 0
            ]
        if isinstance(entity, entities.Fireball):
            return self.fireball[entity.action][int(entity.action_progress * 4) % 2]

        if entity.TILE == Tile.SPEEDBOOST:
            return self.speedboost
        if entity.TILE == Tile.SPEEDPENALTY:
            return self.speedpenalty
        if entity.TILE == Tile.COIN:
            return self.coin
        if entity.TILE == Tile.SUPER_FIREBALL:
            return self.super_fireball
        if entity.TILE == Tile.SHIELD:
            return self.shield
        raise KeyError("Constante inconnue")

    def player_icon(self, game: game.Game, color: Tile):
        """L'icône associée au joueur, avec ou sans bouclier."""
        try:
            player = game.player_entity_from_color(color)
            if player.shield:
                return self.shielded_players[player.color][0]
            return self.players[player.color][Action.WAIT][1]
        except KeyError:
            return self.dead

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
        game: game.Game,
        player_entity: entities.PlayerEntity,
    ):
        """Initialise les éléments tkinter."""
        self.assets_manager = assets_manager
        self.game = game
        self.player_entity = player_entity

        self.player_icon = ttk.Label(
            frame,
            image=self.assets_manager.player_icon(self.game, self.player_entity.color),
        )
        self.player_label = ttk.Label(
            frame, text=self.game.players[self.player_entity.color].NAME
        )
        self.speed_icon = ttk.Label(frame, image=self.assets_manager.speedboost)
        self.speed_label = ttk.Label(frame, text=f"{self.player_entity.speed:.2f}")
        self.super_fireball_icon = ttk.Label(
            frame, image=self.assets_manager.super_fireball
        )
        self.super_fireball_label = ttk.Label(
            frame, text=f"{self.player_entity.super_fireballs}"
        )
        self.coin_icon = ttk.Label(frame, image=self.assets_manager.coin)
        self.coin_label = ttk.Label(frame, text=f"{self.player_entity.coins}")
        self.action_label = ttk.Label(frame, text=self.player_entity.action.value)
        self.action_bar = ttk.Progressbar(frame, length=1, max=1.0, value=0.0)

        # Offset vertical
        n = i * 4
        if i > 0:
            ttk.Separator(frame, orient=tkinter.HORIZONTAL).grid(
                row=n, column=0, columnspan=6, sticky=tkinter.EW, padx=16
            )
            n += 1
        self.player_icon.grid(row=n + 0, column=0, padx=(0, 8), pady=(12, 2))
        self.player_label.grid(
            row=n + 0, column=1, columnspan=5, sticky=tkinter.W, pady=(12, 2)
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
        self.action_label.grid(row=n + 2, column=0, columnspan=4, padx=4, pady=(2, 12))
        self.action_bar.grid(
            row=n + 2, column=4, columnspan=2, sticky=tkinter.EW, padx=4, pady=(2, 12)
        )

    def update(self):
        """Met à jour le panneau."""
        self.player_icon.configure(
            image=self.assets_manager.player_icon(self.game, self.player_entity.color)
        )
        self.speed_label.configure(text=f"{self.player_entity.speed:.2f}")
        self.super_fireball_label.configure(
            text=f"{self.player_entity.super_fireballs}"
        )
        self.coin_label.configure(text=f"{self.player_entity.coins}")
        self.action_label.configure(text=self.player_entity.action.value)
        self.action_bar.configure(value=self.player_entity.action_progress)


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

    def create_widgets(self):
        """Crée les widgets tk dans la fenêtre du jeu."""
        # Canvas
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        size = self.assets_manager.TILE_SIZE * self.game.size
        self.canvas = tkinter.Canvas(
            self.window, background="#eee", width=size, height=size
        )
        self.canvas.grid(column=0, row=0, rowspan=2, padx=8, pady=8)

        # Les joueurs sur le côté
        self.player_panels_frame = ttk.Frame(self.window, padding=16)
        self.player_panels_frame.grid(column=1, row=0, sticky=tkinter.EW)
        self.player_panels_frame.grid_columnconfigure(1, weight=1)
        self.player_panels_frame.grid_columnconfigure(3, weight=1)
        self.player_panels_frame.grid_columnconfigure(5, weight=1)

        player_entities = list(self.game.player_entities)
        self.player_panels = [
            PlayerPanel(
                self.assets_manager,
                self.player_panels_frame,
                i,
                self.game,
                player_entities[i],
            )
            for i in range(len(player_entities))
        ]

        # Contrôles en bas à droite
        self.control_frame = ttk.Frame(self.window, padding=8)
        self.control_frame.grid(column=1, row=1, sticky=tkinter.EW)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=1)

        self.time_label = ttk.Label(
            self.control_frame, text="0 s", font=("", 12, "bold")
        )
        self.time_label.grid(column=0, row=0, pady=4, columnspan=2)

        self.time_scale_label = ttk.Label(self.control_frame, text="x 1.0", width=8)
        self.time_scale_var = tkinter.DoubleVar(value=1.0)
        self.time_scale = ttk.Scale(
            self.control_frame,
            from_=0.0,
            to=10.0,
            orient=tkinter.HORIZONTAL,
            variable=self.time_scale_var,
            command=lambda _: self.time_scale_label.config(
                text=f"Pause" if (x := self.time_scale_var.get()) == 0 else f"x {x:.1f}"
            ),
        )
        self.time_scale.grid(column=0, row=1, padx=4, sticky=tkinter.E)
        self.time_scale_label.grid(column=1, row=1, padx=4, sticky=tkinter.W)

        self.checkbox_value = tkinter.StringVar(value="off")
        self.checkbox = ttk.Checkbutton(
            self.control_frame,
            text="Voir les hitboxes",
            onvalue="on",
            offvalue="off",
            variable=self.checkbox_value,
        )
        self.checkbox.grid(column=0, row=2, columnspan=2, pady=4)

        self.restart_button = ttk.Button(self.control_frame, text="Recommencer")
        self.settings_button = ttk.Button(self.control_frame, text="Retour")
        self.restart_button.grid(column=0, row=3, padx=4, sticky=tkinter.E)
        self.settings_button.grid(column=1, row=3, padx=4, sticky=tkinter.W)

    def start(self, restart_callback: Callable, settings_callback: Callable):
        """Lance la boucle du jeu."""
        t = perf_counter()
        last = t
        stop = False

        def restart():
            nonlocal stop
            stop = True
            self.window.destroy()
            restart_callback()

        def settings():
            nonlocal stop
            stop = True
            self.window.destroy()
            settings_callback()

        self.restart_button.config(command=restart)
        self.settings_button.config(command=settings)

        def update():
            """Provoque la mise à jour du jeu et de la fenêtre."""
            if stop:
                return

            nonlocal t, last
            t = perf_counter()
            dt = t - last
            last = t

            if self.time_scale_var.get() > 0:
                self.game.update(dt * self.time_scale_var.get())
            self.update()

            if not self.game.over:
                self.master.after(
                    max(1, int(1000 / 60 - 1000 * (perf_counter() - last))), update
                )

            elif self.game.over:
                self.game_over()

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

    def draw_background(self):
        """Dessine le fond du plateau."""
        self.background = deepcopy(self.game.background)
        self.canvas.delete("background")
        for y in range(self.game.size):
            for x in range(self.game.size):
                self.canvas.create_image(
                    x * self.assets_manager.TILE_SIZE + 1,
                    y * self.assets_manager.TILE_SIZE + 1,
                    image=self.assets_manager.tile(self.background, x, y),
                    anchor=tkinter.NW,
                    tags="background",
                )
        self.canvas.lower("background")

    def draw_entities(self):
        """Dessine les entités."""
        self.canvas.delete("entities")
        self.canvas.delete("hitboxes")

        def x(entity: entities.Entity):
            if self.checkbox_value.get() == "on":
                return entity.x
            return entity.visual_x

        def y(entity: entities.Entity):
            if self.checkbox_value.get() == "on":
                return entity.y
            return entity.visual_y

        for entity in sorted(self.game.entities.copy(), key=lambda entity: entity.TILE):
            self.canvas.create_image(
                int(x(entity) * self.assets_manager.TILE_SIZE) + 1,
                int(y(entity) * self.assets_manager.TILE_SIZE) + 1,
                image=self.assets_manager.entity(entity),
                anchor=tkinter.NW,
                tags="entities",
            )

    def game_over(self):
        """Affiche le nom du gagnant."""
        if self.game.winner is None:
            self.time_label.config(text="Match nul")
        else:
            self.time_label.config(
                text=f"Victoire de",
                image=self.assets_manager.players[self.game.winner.color][Action.WAIT][
                    1
                ],
                compound=tkinter.RIGHT,
            )
        self.time_scale.config(state=tkinter.DISABLED)
        self.checkbox.config(state=tkinter.DISABLED)


class PlayerSelector:
    """Une icone et une combobox de choix de joueur."""

    def __init__(
        self,
        assets_manager: AssetsManager,
        players: List[Optional[Type[game.Player]]],
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

        self.master.iconphoto(True, self.assets_manager.fireball[Action.MOVE_RIGHT][0])

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

        def settings():
            self.game_launched = False
            self.master.deiconify()

        def restart():
            self.game_launched = False
            self.launch_one_game(players)

        GameInterface(self.master, self.assets_manager, g).start(restart, settings)

    def launch_many_games(self, players: List[Optional[Type[game.Player]]]):
        """Lance 2020 parties simultanées."""
        if self.game_launched:
            return
        self.game_launched = True


if __name__ == "__main__":
    print("Le lanceur du jeu est le fichier ./main.py")
