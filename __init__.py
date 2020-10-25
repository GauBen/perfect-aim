from time import monotonic
from tkinter import Tk

from gui import Gui
from game import Game
from players.randomPlayer import RandomPlayer
from players.indianaJones import IndianaJones


class Delta:
    def __init__(self):
        self.last = monotonic()

    def delta(self):
        t = monotonic()
        out = t - self.last
        self.last = t
        return out


delta = Delta().delta


if __name__ == "__main__":
    root = Tk()
    g = Game([IndianaJones, IndianaJones, IndianaJones, IndianaJones])
    canvas = Gui(root)
    canvas.draw_map(g.map)
    canvas.draw_players(g)

    def update():
        dt = delta() * canvas.slider_var.get()
        if dt > 0:
            g.update(dt)
        canvas.update(g)
        root.after(1000 // 60, update)

    delta()
    update()

    root.mainloop()
