"""
Stratégie de l'équipe Les Meilleurs.

<Ajoutez ici une notice de copyright>
"""
from game import Action, Game, Player


class BestPlayer(Player):
    """Stratégie de l'équipe Les Meilleurs."""

    NAME = "n - Les Meilleurs"

    def play(self, game: Game) -> Action:
        """Choisit la meilleure action possible dans la situation donnée en paramètre."""
        return Action.WAIT
