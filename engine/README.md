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

`GameConfig.validate` contrôle le mode, le stock, les cartes, les couleurs référencées, les conditions contradictoires et l'existence d'une répartition complète de départ. `Card` accepte une `Condition` de défaite historique ou un tuple de plusieurs conditions ; toutes sont évaluées lors d'un contrôle applicable et une élimination reste unique.

Les scénarios déterministes peuvent continuer à injecter `cards` directement. Pour un paquet, fournissez `cards=()` et `card_pool=CardPool(cards, expected_defeat_counts)` à `GameConfig`. La composition déclare les familles de conditions présentes et le nombre attendu (deux par famille). La réserve vérifie les identifiants, la compatibilité des cartes et sa capacité, puis distribue sans doublon à l'aide du générateur de `create_game`. Elle redonne une sélection pour chaque nouvelle manche.

Les commandes sont `ChooseRecipient`, `ProposeGift`, `AcceptGift` et `RefuseGift`. `legal_actions()` renvoie les commandes actuellement acceptées. L'orchestrateur distribue à chaque agent son propre objet `game.controller(player_id)` ; le contrôleur expose seulement la vue privée de ce joueur et ses commandes. `public_view()` et `public_event_history()` appliquent les règles de visibilité. `controller.view().common_bag_colors` décrit les couleurs possibles selon la configuration ; il ne révèle pas les quantités restantes. Ne transmettez pas l'objet moteur directement à un agent.

Le moteur conserve les identifiants de jetons et vérifie leur unicité et leur conservation après chaque commande. `start_new_round(game)` démarre une manche uniquement lorsque le format sélectionné l'autorise ; les scores cumulés sont conservés. L'objet `GameEngine._state` est un détail interne et ne doit pas être modifié par les agents.

## Agents, messages et simulations

Les modules `agents/strategies.py` et `agents/communication.py` fournissent des politiques déterministes simples. Les stratégies de décision ne reçoivent que `PrivateView`, les actions légales et les messages des participants ; elles soumettent les commandes via `Agent.controller`. Les stratégies de communication sont séparées : `SilentCommunication`, `ScriptedCommunication` et `ColorClaimCommunication` permettent silence, annonces, questions, réponses et déclarations configurées véridiques ou mensongères. Les messages écrits sont privés aux donneur et destinataire, liés à l'identifiant de la proposition, et ne changent jamais l'état du moteur. Le moteur ne vérifie pas leur contenu.

`engine.selection.select_first_player` accepte un choix collectif explicite ou des horodatages de récence. Une égalité de récence exige un choix ou une fonction de consensus explicite. `create_game_with_selection` transmet la sélection résolue et sa méthode à l'historique de préparation. L'API `create_game(..., first_player_id=...)` reste compatible.

`simulation.run_game` exécute un pilote via les contrôleurs et vérifie les invariants après chaque commande. `simulation.run_campaign` compare plusieurs configurations et profils de stratégies sur une liste de graines identique ; chaque résultat conserve le nom de configuration, les règles, les stratégies, le numéro, la graine, les vainqueurs, les tours, les messages et les éventuelles erreurs. `simulation.summarize` donne des statistiques descriptives par configuration. Les campagnes longues sont appelables séparément ; les tests pytest utilisent de petits cas fixes.

Les cartes candidates d'élimination précoce, les pouvoirs secrets et toute famille de règle non définie dans les spécifications ne sont pas activés. Les règles et seuils expérimentaux restent des options explicites de configuration. Une condition de majorité doit préciser son interprétation (`MajorityBasis.PLURALITY` ou `MajorityBasis.MORE_THAN_HALF`) ; le moteur n'en choisit pas une à la place du groupe. Les campagnes fournissent des mesures reproductibles ; elles ne démontrent pas à elles seules l'équilibre d'une variante.

`DIVERSITY` est une condition expérimentale : `colors` énumère les couleurs candidates et `minimum` fixe le nombre minimal de couleurs candidates présentes (au moins un jeton). Les couleurs hors de cette liste ne comptent pas. Si `max_per_color` est défini, aucune couleur candidate ne peut dépasser cette limite, y compris si elle n'est pas nécessaire pour atteindre le minimum. Le minimum doit être compris entre 1 et le nombre de couleurs candidates.
