# Simulations reproductibles

Lancer depuis la racine du dépôt avec Python installé :

```powershell
py -m simulation --help
py -m simulation run --help
```

Les benchmarks intégrés sont expérimentaux et non officiels. Ils servent à éprouver les agents et les variantes, pas à définir le paquet ou les règles définitives.

## Campagne rapide

```powershell
py -m simulation run --suite reference --games 3 --seed 42 --players 4
```

Cela lance trois parties par mode A, B et C avec le profil déterministe de référence. La sélection du premier joueur tourne par index de simulation. Chaque appel crée un nouveau dossier sous `reports/simulations/`.

## Campagne de référence de milliers de parties

```powershell
py -m simulation run --suite reference --games 1000 --seed 20261016 --players 4 --max-actions 1000
```

Cette commande prévoit 3 000 parties, soit 1 000 par mode. Les graines consécutives commencent à `20261016`. Elle s'arrête au premier échec et sauvegarde l'échec; ajouter `--continue-on-error` pour lancer les autres simulations et produire un rapport complet avec les erreurs isolées.

## Comparer variantes, agents ou cartes

```powershell
py -m simulation run --suite variants --games 500 --seed 7300 --continue-on-error
py -m simulation run --suite agents --games 250 --seed 8400 --continue-on-error
py -m simulation run --suite cards --games 1000 --seed 9500
```

`variants` modifie séparément la succession, le contrôle du donneur et les options de visibilité, avec des graines appariées. `agents` compare le profil déterministe, un agent aléatoire reproductible, le profil prudent, les politiques d'acceptation/refus, les communications véridiques, le bluff, les questions et des groupes mixtes. Les politiques de décision et de communication restent indépendantes.

Les options principales sont `--games`, `--seed`, `--players` (2 à 4 pour le paquet expérimental), `--decision-profile`, `--communication-profile`, `--early-threshold`, `--max-actions`, `--output`, `--continue-on-error` et `--experiment-name`.

## Reproduire et lire les résultats

Pour reproduire une partie, relancer la même suite/configuration avec le même nombre de joueurs, le même profil, la graine inscrite dans `games.csv` et la même révision du dépôt. Une campagne compare les configurations avec la même liste de graines et le même calendrier de premiers joueurs. Une graine commune n'assure pas des trajectoires identiques lorsque les règles diffèrent.

Chaque dossier contient :

- `summary.json` : paramètres, configurations, graines, profils, résultats détaillés et erreurs.
- `summary.csv` : agrégats par configuration et profil.
- `games.csv` : une ligne par partie terminée ou échouée.
- `players.csv` : une ligne par joueur et manche, avec carte attribuée, position, élimination et score.
- `report.md` : rapport lisible avec définitions, effectifs, intervalles et limites.

`actions` compte les commandes soumises au moteur; `gifts_proposed` compte les propositions et sert de tour de jeu; `rounds_played` compte les manches commencées. Les secondes sont le temps informatique mesuré et dépendent du matériel. Le seuil d'élimination précoce par défaut est expérimental : trois cadeaux proposés, seuil inclus. Les rapports conservent également les tours bruts.

Les intervalles à 95 % des proportions utilisent Wilson; ceux des moyennes et différences appariées sont des approximations normales descriptives. Les résultats sont conditionnels aux profils, variantes, cartes et graines testés : une campagne ne démontre ni causalité ni équilibre. Une carte avec moins de 30 attributions est signalée comme insuffisamment observée. Les mesures de cartes secrètes sont effectuées par l'orchestrateur après la partie et ne sont jamais communiquées aux agents.
