# Audit d’implémentation — règles Versions 66 et 67

## Périmètre et état de départ

Référence de l’audit initial : `C'est cadeau !.docx`, version 66 (« règles de succession et cas terminaux harmonisés »), lue pour les règles et décisions des sections 3 à 7, 10.1, 11, 12 et 14. La contradiction de succession B identifiée lors de cet audit a été clarifiée dans le document en version 67. Dépôt `C:\jeu`, branche `main`, commit de départ de l’audit initial `bc7b2393d4838568f9b88e6e7f466660512693b4`; commit de départ de la clarification `a43639e37bcfe3af6851cf059ab0a9e0daa63c8b`. L’arbre de travail était propre avant chaque intervention. À la fin de l’intervention initiale, aucun commit ni push n’avait été effectué ; l’audit a ensuite été publié dans le commit `e5a0958757c30daebd980a34a273abb4e81cf56b`. La présente passe documentaire ne crée ni commit ni push.

Les résultats des configurations de simulation préexistantes dans `reports/simulations/` ont été conservés. Le statut « décision ouverte » désigne une variante ou un paramètre que le document ne fixe pas comme règle finale.

## Matrice de conformité

| Référence | Règle / comportement examiné | Implémentation et tests | État |
|---|---|---|---|
| §3, §10.1, §11 | Trois jetons par joueur ; contrôle privé des conditions initiales ; nouvelle main complète si défaite ou victoire B ; aucune révélation/élimination initiale ; rejet d’une configuration sans distribution complète ; préparation bornée. | `rules/config.py` (`validate`, `_complete_setup_possible`), `engine/setup.py` (`create_game`, `_deal_valid_hands`), `engine/transitions.py` (`_start_new_round`); `tests/test_setup.py`, `tests/test_card_pool.py`. Le tirage d’une main viable qui condamnait la suite pouvait échouer après la limite aléatoire malgré une solution complète : corrigé par reprise puis recherche bornée parmi les mains complétables. | Conforme après correction et tests ciblés. |
| §5, §8, §12 | Conditions structurées et paramètres validés ; compatibilité physique au stock ; aucune collection ne doit satisfaire victoire et défaite ensemble. | `rules/cards.py` (`condition_matches`), `rules/config.py` (`_validate_condition`, `_conditions_overlap`); `tests/test_config.py`, `tests/test_regressions_point2.py`. | Conforme pour les sémantiques couvertes ; les formulations de cartes candidates restent ouvertes. |
| §5, §8.1 | `COMPOSITION(exact=True)` signifie les quantités indiquées et aucune couleur/quantité supplémentaire ; `exact=False` signifie des minima. | `rules/cards.py`; nouveau test de sémantique et test de non-chevauchement dans `tests/test_regressions_point2.py`. L’absence de contrôle des jetons non listés était un écart confirmé et est corrigée. | Conforme après correction. |
| §4.1–4.3, §10.1 | Choix conscient du jeton ; emplacement temporaire ; acceptation, refus et refus forcé si sac commun vide ; remise au bon sac ; pioche et déclencheurs de victoire/défaite dans l’ordre établi. | `engine/transitions.py` (`_propose`, `_decide`, `_draw`, `_check_recipient`); `tests/test_gifts.py`, `tests/test_eliminations.py`, `tests/test_privacy.py`. | Conforme selon les tests existants. |
| §4.2–4.3, §5 | Donneur éliminé après retrait ; cadeau maintenu en proposition ; carte révélée intégralement à victoire/élimination ; retour des jetons personnels ; absence de double restitution. | `engine/transitions.py` (`_eliminate`, `_decide`); tests de cadeaux et d’éliminations. | Conforme selon les tests existants. |
| §6.1–6.3 | Modes A/B/C, contrôles de victoire secrète, C1 et C2, bonus, seuil de manche et seuil C2 contrôlé à fin de manche. | `engine/transitions.py` (`_finish_round`, `_finish_game`, contrôles dans `_decide`); `tests/test_modes.py`, `tests/test_scoring.py`, `tests/test_gifts.py`. | Conforme selon les tests existants. Les valeurs d’équilibrage demeurent expérimentales. |
| §4.4, §7, §10.1 | Succession A : rejeu du responsable et pioche du successeur vide ; succession B : ordre horaire, sauts des joueurs éliminés, crédit des éliminations forcées non terminales. | `engine/transitions.py` (`_succession_a`, `_clockwise_chain`); `tests/test_eliminations.py`, `tests/test_scoring.py`, `tests/test_regressions_point2.py`. | Conforme pour les suites accessibles et testées. |
| §7, §11 | Égalité si l’action initiale élimine tout le monde ; pas de points/bonus pour cette action ; résultats C sans victoire de manche inventée. | `engine/transitions.py` (`_decide`, `_terminal_tie`); `tests/test_regressions_point2.py`; nouveau test d’intégration complet dans `tests/test_simulation.py`. | Conforme pour l’action initiale. Le scénario réel est décrit ci-dessous. |
| §7, §10.1, §11 | Constat historique de la version 66 : une chaîne B pouvait être lue comme éliminant le dernier survivant, sans crédit de cette dernière élimination. | Corrigé par la version 67. Après chaque élimination forcée, vérifier dans cet ordre : égalité à zéro survivant, seuil de manche C, dernier survivant ; poursuivre la chaîne uniquement s’il reste plusieurs joueurs et qu’aucune fin immédiate ne s’applique. Les points déjà validés lors d’actions précédentes restent acquis. | Conformité établie après clarification version 67 ; le conflit de la version 66 est historique et résolu. |
| §2, §3, §4.1, §10.1 | Secret des cartes et collections ; chaque agent ne reçoit que sa vue privée et les messages qui lui sont destinés. | `engine/transitions.py` (vues et contrôleurs), `agents/communication.py`; `tests/test_privacy.py`, `tests/test_simulation.py`, `tests/test_simulation_experiments.py`. | Conforme selon les tests existants. |
| §10.1, §11 | Une ligne détaillée représente un joueur-manche ; score et compteurs de manche proviennent de la fin réelle de cette manche ; égalité distincte d’une victoire partagée ; exports cohérents. | `simulation/runner.py`, `simulation/statistics.py`, `simulation/reporting.py`; tests simulation et exports dans `tests/test_simulation.py`, `tests/test_simulation_experiments.py`. | Conforme selon les tests existants ; pas de campagne longue relancée pour cet audit. |
| §7, §11, §12 | Première désignation, variantes optionnelles et paramètres encore ouverts restent explicitement configurables ; les campagnes expérimentales ne deviennent pas des règles finales. | `engine/selection.py`, `simulation/experiments.py`, `simulation/runner.py`; `tests/test_selection.py`, tests d’expériences. | Conforme ; plusieurs décisions restent ouvertes au document. |

## Écarts corrigés

1. **Composition exacte incomplète.** `condition_matches` comparait les quantités des seules couleurs mentionnées. Un jeton rouge supplémentaire pouvait donc satisfaire la composition exacte bleu/jaune/vert. La fonction exige maintenant que le total de la collection égale le total déclaré ; le mode minimal reste permissif.
2. **Distribution bloquée par un tirage intermédiaire aléatoire.** Une main individuellement valide pouvait laisser un stock impossible aux joueurs restants ; dans les configurations à cartes injectées, le moteur échouait immédiatement alors qu’une répartition complète existait. Il rejette désormais ce tirage, poursuit les reprises bornées et, si elles épuisent leur limite, choisit avec le générateur fourni parmi les mains qui préservent une solution complète. Le repli reste reproductible avec la graine.

## Test d’égalité terminale réelle en mode C

Le test `test_mode_c_terminal_tie_runs_through_real_runner_stats_and_exports` utilise `run_game`, la graine `1`, deux cartes de défaite « exactement deux rouges », un stock de quatre rouges et deux bleus, des mains de trois, le contrôle du donneur après retrait et des agents qui choisissent le destinataire, offrent un rouge et acceptent.

La trace réelle exécute trois actions (choisir le destinataire, proposer le jeton, accepter). Le donneur est éliminé au retrait ; le destinataire reçoit le jeton et est éliminé à son tour. L’événement `game_finished` donne le résultat `terminal_tie` (reflété par `run.terminal_ties == 1`), aucun gagnant, aucun résumé/achèvement de manche, zéro score et compteur final nul pour les deux joueurs. Les lignes joueur indiquent `tied`, sans victoire ni score fictif de manche.

## Clarification Version 67 : succession B

La version 66 associait l’arrêt de succession au dernier survivant avec des passages autorisant une chaîne B à éliminer ensuite ce dernier joueur. La clarification normative intégrée en version 67 donne priorité à l’ordre détaillé de la section 4.4 : égalité à zéro joueur, seuil de manche C, dernier survivant, puis poursuite seulement si plusieurs joueurs restent sans fin immédiate. Une chaîne B ne peut donc pas éliminer le dernier survivant. Les points validés lors d’actions initiales précédentes restent acquis. Les sections 4.1 à 4.4, 5, 6.3, 7, 10.1, 11 et 14, ainsi que les entrées correspondantes du registre, ont été harmonisées. L’égalité terminale de l’action initiale reste distincte de l’égalité au score de C1/C2.

Le test `test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus` couvre une séquence d’actions réelle et vérifie l’arrêt au dernier survivant après les éliminations forcées. Les tests de seuil vérifient l’autre fin immédiate prioritaire. Aucun test ne prétend qu’une chaîne B puisse éliminer son dernier survivant.

Le test `test_mode_c_terminal_tie_runs_through_real_runner_stats_and_exports` joue une vraie partie déterministe avec `run_game` (graine 1), puis transmet son résultat à `summarize` et `write_campaign`. Il vérifie le seul événement `game_finished` d’égalité, l’absence d’événement `round_finished`, de points et de bonus, deux lignes joueur-manche sans score/résultat de manche, une partie sans gagnant, les compteurs de `summary.csv` et `summary.json`, et la distinction égalité terminale/victoire partagée dans `report.md`. `games.csv` inclut désormais `event_counts_json` afin de vérifier les événements du moteur sans exporter leur contenu privé.

## Décisions et paramètres encore ouverts

Conformément aux sections 7, 8, 11 et 12, restent à choisir/équilibrer : configuration du sac et nombre de joueurs, seuils et formulations finales des cartes, paquet final, objectifs de victoire, seuils C, couleur dangereuse exacte/minimale, certaines règles de deux paires/majorité, pouvoirs secrets, visibilité des pioches et variantes optionnelles de succession/contrôle du donneur. Ces points ouverts ne remettent pas en cause l’ordre de résolution de la succession B, établi en version 67. Les valeurs de `simulation/experiments.py` restent expérimentales.

## Fichiers modifiés

- `rules/cards.py` : sémantique de composition exacte complète.
- `engine/setup.py` : reprises et sélection de repli parmi des mains complétables.
- `engine/transitions.py` : utilise la même distribution vérifiée au début des manches suivantes.
- `tests/test_regressions_point2.py` : composition exacte/minimale et chevauchement.
- `tests/test_setup.py` : démontre qu’une graine aléatoire défavorable ne fait pas échouer une configuration faisable.
- `tests/test_simulation.py` : égalité C produite par le runner puis vérifiée dans les statistiques et cinq exports.
- `simulation/runner.py` : compteurs d’événements non privés dans le résultat de simulation.
- `simulation/reporting.py` : colonne `event_counts_json` dans `games.csv` et définition de la mesure dans le rapport.
- `C'est cadeau !.docx` : version 67, clarification de la succession B et mise à jour des sections et du registre concernés.
- `specifications/audit_implementation_version66.md` : matrice initiale version 66 et addendum de conformité à la clarification version 67.
