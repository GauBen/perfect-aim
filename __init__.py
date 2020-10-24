from time import monotonic
from tkinter import Tk

from gui import Gui
from map import Map
from game import Game


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
    my_map = Map()
    root = Tk()
    g = Game()
    canvas = Gui(root)
    canvas.draw_map(my_map)
    canvas.draw_players()

    def update():
        dt = delta() * canvas.slider_var.get()
        if dt > 0:
            g.update(dt)
        canvas.update(g)
        root.after(16, update)

    delta()
    update()

    root.mainloop()
