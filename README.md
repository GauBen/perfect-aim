# Perfect Aim

## Règles du jeu

Perfect Aim est composé :

-   D'un plateau de jeu
-   De 2 à 4 joueurs
-   D'objets bonus et malus
-   De boules de feu

![Une partie à son commencement](./doc/game.png)

### Le plateau

Le plateau est une matrice bidimensionnelle.
Il se compose :

-   De sol, une case vide dans laquelle un joueur peut aller
-   De murs, une case dans laquelle les joueurs ne peuvent pas aller
-   De lave, une case dans laquelle tout joueur qui s'y rend meurt
-   De sol endommagé, une case de sol qui devient de la lave dans les 5 secondes

Voici un plateau de jeu avec tous ces éléments, ainsi que des objets et des joueurs :

![Une partie assez avancée](./doc/background.png)

Le sol commence à s'endommager par l'extérieur à partir de 65 secondes de jeu. Toutes les 10 secondes la zone de jeu est réduite d'une case depuis tous les côtés.

Au début de la partie, le plateau est parfaitement symétrique.

### Les joueurs

![Joueur rouge](./assets/players/red-i2.png) ![Joueur bleu](./assets/players/blue-i2.png) ![Joueur jaune](./assets/players/yellow-i2.png) ![Joueur vert](./assets/players/green-i2.png)

Un joueur est une entité dont les actions sont déterminées par les programmes des participants. Au début de la partie, un joueur effectue une action toutes les secondes. Cette cadence peut être accélérée grâce à des objets.

Une action d'un joueur est : se déplacer dans une des 4 directions, attaquer dans une des 4 directions, ou attendre sur sa case.

Deux joueurs ne peuvent pas se trouver sur la même case en même temps. Si deux joueurs essaient de se rendre sur la même case, un des deux joueurs restera immobile.

### Les objets

![Bonus de vitesse](./assets/collectibles/speedboost.png) **Bonus de vitesse**

Le ramasser confère un bonus de `0.25` actions par seconde en plus.

![Malus de vitesse](./assets/collectibles/hourglass.png) **Malus de vitesse**

Le ramasser confère un malus de `0.25` actions par seconde en moins. Par conséquent, il annule un bonus de vitesse. La vitesse minimale d'un joueur est `0.5`.

![Pièce](./assets/collectibles/coin.png) **Pièce d'or**

Une pièce d'or, qui n'offre aucun avantage au joueur. Elles sont utilisées pour comparer deux équipes ayant un même nombre de victoires pendant le tournoi.

![Super boule de feu](./assets/collectibles/super_fireball.png) **Super boule de feu**

Un sort qui permet de lancer 4 boules de feu dans toutes les directions. Ce sort est cumulable.

**Des objets sont régénérés sur le plateau s'il n'y en a plus.**

![Bouclier](./assets/collectibles/shield.png) **Bouclier**

Un bouclier, qui protège de la prochaine boule de feu reçue. Non cumulable.

### Les boules de feu

L'attaque du jeu !

Voici les règles associées aux boules de feu :

-   Elles se déplacent à la vitesse de 4 cases / seconde.
-   Elles se déplacent en ligne droite jusqu'au premier mur rencontré.
-   Elles éliminent un joueur sans bouclier, et sont éliminées par un joueur avec bouclier.
-   Elles n'intéragissent pas avec les objets au sol et les autres boules de feu.
-   Deux joueurs sont susceptibles de s'entretuer s'ils s'attaquent en même temps.
-   Un joueur ne peut attaquer que s'il n'y a plus de boules de feu qu'il a envoyées sur le terrain, ou qu'il a un sort de super boules de feu.

![Trois joueurs attaquent en même temps](./doc/fireballs.png)

## API du jeu

La fonction `play` est appelée à intervalle régulier pour demander au joueur quelle action jouer.

```python
class BestPlayer(Player):

    NAME = "Les Meilleurs"

    def play(self, game: Game) -> Action:
        action = Action.WAIT
        # ...votre stratégie...
        return action
```

Les paramètres d'appel sont :

-   Le joueur `self`, instance de la classe `Player`
-   Le jeu `game`, instance de la classe `Game`

Les valeurs de retour possibles sont `WAIT`, `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `ATTACK_UP`, `ATTACK_DOWN`, `ATTACK_LEFT`, `ATTACK_RIGHT`. (À préfixer avec `Action.`.)

### Connaître l'état de son joueur

Les informations disponibles sont les suivantes :

-   `x` et `y (int)` les coordonnées du joueur, respectivement horizontale et verticale. `(0, 0)` est le mur en haut à gauche.
-   `speed (float)` la vitesse du joueur, qui correspond au nombre d'actions que votre joueur effectuer par seconde (`1.0` au début du jeu). Cette valeur est incrémentée de `0.25` à chaque bonus de vitesse collecté. (Et `-0.25` par malus.)
-   `coins (int)` le nombre de pièces du joueur.
-   `super_fireballs (int)` le nombre de super boules de feu collectées. La prochaine attaque en consommera une s'il y en a une disponible.
-   `shield (bool)` la présence d'un bouclier. Vrai si le joueur est protégé de la prochaine boule de feu qu'il reçoit.
-   `action (Action)` la dernière action jouée, une constante parmi les 9.
-   `color (Tile)` la couleur du joueur, une constante parmi `Tile.PLAYER_RED`, `_BLUE`, `_YELLOW`, `_GREEN`.

Par exemple :

```python
play(self, game: Game) -> Action:
    print(f"Je suis le joueur {self.color.name}")
    print(f"Je suis en (x, y) = ({self.x}, {self.y})")
    if self.shield:
        print("J'ai un bouclier !")
    if self.speed >= 2.0:
        print("J'ai ramassé 4 bonus de vitesse")
    return Action.WAIT
```

Méthodes disponibles :

-   `is_action_valid(action: Action) -> bool` : renvoie vrai si l'action est valide.
-   `can_attack() -> bool` : renvoie vrai si on peut attaquer.

```python
if self.is_action_valid(Action.MOVE_UP):
    print("Cap au Nord capitaine !")
    return Action.MOVE_UP
```

Les actions possèdent des méthodes pour les manipuler facilement :

-   `apply(coords)` où coords est une paire de coordonnées : applique un déplacement
-   `swap()` : donne la direction inverse
-   `to_attack()` : transforme un déplacement en attaque
-   `to_movement()` : transforme une attaque en déplacement
-   `is_attack()` : vrai si c'est une attaque
-   `is_movement()` : devine

Par exemple :

```python
coords = (1, 1)
# Action.MOVE_RIGHT.apply(coords) == (1, 2)

a = Action.ATTACK_UP
# a.swap() == Action.ATTACK_DOWN
# a.to_movement() == Action.MOVE_UP
# a.is_movement() == False

# a.swap().to_movement() == Action.MOVE_DOWN
#                        == a.to_movement().swap()
# a.swap().to_movement().apply(coords) == (2, 1)

```

### Connaître l'état du jeu

Le paramètre `game` est un object complexe qui représente l'état du jeu.

Valeurs simples :

-   `t (float)` le temps de jeu écoulé depuis le début de la partie, en secondes.
-   `size (int)` la dimension de la grille.

#### `game.tile_grid (List[List[Tile]])`

La représentation la plus simple du jeu est `tile_grid`. C'est une matrice bidimensionnelle de `Tile` où `Tile` est l'énumération de tous les objets du jeu possibles.

Par exemple, comme le jeu est toujours entouré d'un mur, on a `game.tile_grid[0][0] == Tile.WALL`.

Les valeurs possibles de `Tile` sont :

-   `FLOOR` une case vide où il est possible de se rendre
-   `WALL`
-   `LAVA` une case de lave qui tue tous les joueurs y entrant
-   `DAMAGED_FLOOR` une case qui va devenir de la lave dans un futur proche (moins de 5 secondes)
-   `SPEEDBOOST`
-   `SPEEDPENALTY`
-   `COIN`
-   `SUPER_FIREBALL`
-   `SHIELD`
-   `PLAYER_RED`
-   `PLAYER_BLUE`
-   `PLAYER_YELLOW`
-   `PLAYER_GREEN`
-   `FIREBALL` une boule de feu

S'il y a une superposition (par exemple `DAMAGED_FLOOR`, `SPEEDBOOST`, `FIREBALL` sur la même case), c'est le dernier objet dans l'ordre de la liste au dessus qui est enregistré dans `tile_grid` (donc dans cet exemple `FIREBALL`).

Il existe des méthodes pour savoir rapidement si un élément de la classe `Tile` est dans une certaine catégorie :

-   `is_floor()` : `FLOOR` et `DAMAGED_FLOOR`
-   `is_background()` : `FLOOR`, `WALL`, `LAVA` et `DAMAGED_FLOOR`
-   `is_collectible()` : un des 5 objets ramassables
-   `is_bonus()` : un des 3 objets qui offrent un bonus de statistique
-   `is_player()` : un des 4 joueurs
-   `is_dangerous()` : `LAVA`, `DAMAGED_FLOOR`, les joueurs et `FIREBALL`

Par exemple :

```python
a = Tile.FLOOR
b = Tile.SHIELD
# a.is_background() == True
# a.is_bonus()      == False
# b.is_background() == False
# b.is_bonus()      == True
```

Voici des exemples plus complets :

```python
def play(self, game: Game) -> Action:
    # ...
    if game.tile_grid[self.y][self.x + 1] == Tile.DAMAGED_FLOOR:
        print("Je ne dois pas aller à droite, c'est dangereux !")
    # ...
```

Pour se repérer dans une matrice bidimensionnelle :

-   Au dessus : `g[y - 1][x]`.
-   En dessous : `g[y + 1][x]`.
-   À gauche : `g[y][x - 1]`.
-   À droite : `g[y][x + 1]`.

```python
def play(self, game: Game) -> Action:

    # On regarde dans les 4 directions
    for a in (Action.MOVE_UP, Action.MOVE_DOWN,
              Action.MOVE_LEFT, Action.MOVE_RIGHT):

        # La case adjacente au joueur dans la direction `a`
        x, y = a.apply((self.x, self.y))

        # S'il y a un joueur sur cette case, on attaque dans cette direction
        if game.tile_grid[y][x].is_player():
            return a.to_attack()

    # ...
```

#### Representation complète

Pour avoir une représentation complète du jeu, il faut utiliser conjointement `background (List[List[Tile]])` et `entity_grid (List[List[Set[Entity]]])`. Ce sont deux matrices bidimensionnelles, comme `tile_grid`, mais elles permettent de connaître les éléments superposés, ainsi que des détails sur eux.

## Crédits

**Code** :

-   Code du jeu par [Gautier Ben Aïm](https://github.com/GauBen), sous licence MIT
-   Code des stratégies des participants : consulter les licences dans les fichiers du dossier ./players/

**Ressources graphiques** :

-   [Instant Dungeon! v1.4 Art Pack](https://opengameart.org/content/instant-dungeon-v14-art-pack) ([Jeu d'origine](http://www.indiedb.com/games/instant-dungeon)) par Scott Matott, Voytek Falendysz et José Luis Peiró Lima, sous licence [OGA-BY-3.0](https://static.opengameart.org/OGA-BY-3.0.txt)
-   [Magma / Lava Tileset 8x8](https://opengameart.org/content/magma-lava-tileset-8x8) par GoodClover, sous licence [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
