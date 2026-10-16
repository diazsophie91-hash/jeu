# Moteur Python

Le moteur fonctionne avec Python 3.10 ou ultérieur et ne dépend que de la bibliothèque standard. Fournissez soit `seed`, soit un objet `random.Random` personnalisé à `create_game`, jamais les deux. `first_player_id` doit être choisi explicitement par le groupe ; le moteur n'invente pas de méthode de départage. Une nouvelle manche demande également un premier joueur explicite.

## API de partie

```python
from engine import create_game, ChooseRecipient, ProposeGift, AcceptGift
from rules import Card, Condition, ConditionKind, GameConfig, GameMode

defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=4)
cards = tuple(Card(f"carte-{i}", defeat) for i in range(2))
config = GameConfig({"rouge": 10, "bleu": 10}, GameMode.LAST_SURVIVOR, cards)
game = create_game(["Alice", "Bob"], config, seed=123, first_player_id="Alice")
alice = game.controller("Alice")
bob = game.controller("Bob")

alice.submit(ChooseRecipient("Bob"))
token = alice.view().hand[0]
alice.submit(ProposeGift(token.id))
bob.submit(AcceptGift())
```

`GameConfig.validate` contrôle le mode, le stock, une carte fournie par joueur, les couleurs référencées, les conditions contradictoires et l'existence d'une répartition complète de départ. Le moteur ne gère pas un paquet complet ni sa composition ; fournissez les cartes de la manche explicitement. Les seuils expérimentaux sont des paramètres de `Condition` et de `GameConfig` ; aucun seuil de carte d'essai n'est fourni comme règle officielle.

Les commandes sont `ChooseRecipient`, `ProposeGift`, `AcceptGift` et `RefuseGift`. `legal_actions()` renvoie les commandes actuellement acceptées. L'orchestrateur distribue à chaque agent son propre objet `game.controller(player_id)` ; le contrôleur expose seulement la vue privée de ce joueur et ses commandes. `public_view()` et `public_event_history()` appliquent les règles de visibilité. `controller.view().common_bag_colors` décrit les couleurs possibles selon la configuration ; il ne révèle pas les quantités restantes. Ne transmettez pas l'objet moteur directement à un agent.

Le moteur conserve les identifiants de jetons et vérifie leur unicité et leur conservation après chaque commande. `start_new_round(game)` démarre une manche uniquement lorsque le format sélectionné l'autorise ; les scores cumulés sont conservés. L'objet `GameEngine._state` est un détail interne et ne doit pas être modifié par les agents.

Les cartes candidates d'élimination précoce, les pouvoirs secrets et toute famille de règle non définie dans les spécifications ne sont pas activés. Les règles et seuils expérimentaux restent des options explicites de configuration. Une condition de majorité doit préciser son interprétation (`MajorityBasis.PLURALITY` ou `MajorityBasis.MORE_THAN_HALF`) ; le moteur n'en choisit pas une à la place du groupe.

`DIVERSITY` est une condition expérimentale : `colors` énumère les couleurs candidates et `minimum` fixe le nombre minimal de couleurs candidates présentes (au moins un jeton). Les couleurs hors de cette liste ne comptent pas. Si `max_per_color` est défini, aucune couleur candidate ne peut dépasser cette limite, y compris si elle n'est pas nécessaire pour atteindre le minimum. Le minimum doit être compris entre 1 et le nombre de couleurs candidates.
