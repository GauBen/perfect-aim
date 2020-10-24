from player import Player


class Game:
    def __init__(self):
        self.players = [Player(), Player(15, 15, 1.5)]
        self.t = 0

    def update(self, remaining: float):
        # On peut pas update tout indépendammenent, il faut recalculer la map à chaque fin d'update
        dt = min([p.next_update_in(remaining) for p in self.players] + [remaining])
        for p in self.players:
            p.update(self, dt)
        self.t += dt
        if remaining - dt > 0:
            self.update(remaining - dt)
