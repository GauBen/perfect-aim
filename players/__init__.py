"""Ce dossier/module contient les stratégies des joueurs."""

import glob
import importlib
import inspect
from pathlib import Path
from entities import Player


def list_player_subclasses():
    """Liste les classes filles de Player."""
    for file in glob.glob("./players/*.py"):
        for name, constructor in inspect.getmembers(
            importlib.import_module("players." + Path(file).stem),
            lambda constructor: inspect.isclass(constructor)
            and issubclass(constructor, Player)
            and constructor is not Player,
        ):
            yield (name, constructor)
