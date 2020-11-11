"""
Perfect Aim, un jeu développé spécialement pour un hackathon.

Perfect Aim
===========

Un jeu de stratégie en temps discret développé specialement pour un hacktathon.
Votre objectif ? Créer un joueur ordinateur meilleur que celui des autres.
"""

from time import monotonic
from tkinter import Tk

from gui import Gui
from game import Game

# from players.randomPlayer import RandomPlayer
from players.indianaJones import IndianaJones


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


if __name__ == "__main__":
    root = Tk()
    g = Game([IndianaJones, IndianaJones, IndianaJones, IndianaJones])
    canvas = Gui(root)
    canvas.draw_map(g)
    canvas.draw_players(g)

    def update():
        """Temp."""
        dt = delta() * canvas.slider_var.get()
        if dt > 0:
            g.update(dt)
        canvas.update(g)
        if not g.over:
            root.after(1000 // 60, update)

    delta()
    update()

    root.mainloop()
