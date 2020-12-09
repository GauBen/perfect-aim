"""
Perfect Aim, un jeu développé spécialement pour un hackathon.

Perfect Aim
===========

Un jeu de stratégie en temps discret développé specialement pour un hackathon.
Votre objectif ? Créer un joueur ordinateur meilleur que celui des autres.
"""

if __name__ == "__main__":
    import os

    from gui import GameLauncher

    os.chdir(os.path.dirname(__file__))

    launcher = GameLauncher()
    # Pour lancer automatiquement une partie configurée :
    # from players.indianajones import IndianaJones
    # launcher.launch_one_game([IndianaJones(), IndianaJones()])
    launcher.start()
