"""Ce dossier/module contient les stratégies des joueurs."""

import glob
import importlib
import inspect
from pathlib import Path
from typing import Callable, List
from entities import Player


def list_player_constructors() -> List[Callable[[], Player]]:
    """Liste les classes filles de Player."""
    constructors = []
    for file in glob.glob("./players/*.py"):
        for _, constructor in inspect.getmembers(
            importlib.import_module("players." + Path(file).stem),
            lambda constructor: inspect.isclass(constructor)
            and issubclass(constructor, Player)
            and constructor is not Player,
        ):
            constructors.append(constructor)
    return constructors
