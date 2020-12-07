"""Ce dossier/module contient les stratégies des joueurs."""

import importlib
import inspect
from glob import glob
from pathlib import Path
from typing import List, Type

from game import Player


def list_player_constructors() -> List[Type[Player]]:
    """Liste les classes filles de Player."""
    constructors = []
    for file in glob("./players/*.py"):
        for _, constructor in inspect.getmembers(
            importlib.import_module("players." + Path(file).stem),
            lambda constructor: inspect.isclass(constructor)
            and issubclass(constructor, Player)
            and constructor is not Player,
        ):
            constructors.append(constructor)
    return sorted(constructors, key=lambda c: c.NAME)
