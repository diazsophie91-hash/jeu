# Configuration de référence — « C’est cadeau ! »

## 1. Statut et méthode de lecture

Ce document consigne la configuration de conception demandée pour préparer l’implémentation, les tests et les futures simulations. Il distingue une décision de conception validée de son implémentation effective. Les valeurs du benchmark dans `simulation/experiments.py` ne sont pas des règles officielles et ne remplacent pas les décisions ci-dessous.

Le catalogue détaillé des cartes est [catalogue_cartes_reference.md](catalogue_cartes_reference.md) ; il est la source pour les identifiants, les 12 variantes, leurs 24 exemplaires par paquet et les associations de victoire/défaite. Il n’est pas recopié ici.

Les états « conforme » et « divergence » se rapportent au code actuellement présent, pas à une validation de l’équilibre. Aucun résultat de test n’est avancé sans test pertinent cité. Les simulations dites finales ne sont pas lancées ni réputées probantes tant que les divergences d’implémentation ne sont pas résolues.

## 2. Configuration de conception décidée

| Sujet | Référence de conception | Précision / statut d’implémentation |
|---|---|---|
| Nombre de joueurs | 4 à 8 joueurs ; cible d’équilibrage : 6 | La cible est un objectif à étudier, pas un équilibre démontré. La campagne finale devra couvrir 4, 5, 6, 7 et 8. |
| Sac commun | 52 jetons : 13 rouges, 13 bleus, 13 jaunes, 13 verts | Remplace l’hypothèse de 40 jetons dans la v67 ; la configuration se fait par les valeurs de `GameConfig.colors`. |
| Main de départ | 3 jetons par joueur | Règle v67 et défaut de `GameConfig.initial_hand_size`. Ne pas utiliser les 2 jetons du benchmark comme référence. |
| Cartes et manches | Paquet A/C de 24 cartes « défaite seulement » pour A ou C ; paquet B distinct de 24 cartes « défaite + victoire » pour B. Une nouvelle sélection de cartes et nouvelle distribution ont lieu au début de chaque manche. | Les paquets ne forment pas un paquet hybride de 48 cartes. À 4–8 joueurs, le paquet de 24 suffit physiquement à distribuer une carte à chacun ; la compatibilité de la réserve avec le moteur actuel diverge (voir §10). |
| Contrôles de collection | Conditions évaluées aux événements définis par les règles, non à chaque mutation interne. Une collection initiale qui invalide la carte est repiochée ; la mise en place ne provoque aucune élimination réelle ni victoire. | Le deal actuel effectue ces contrôles et rejette/réessaie les collections initiales invalides. L’objectif contextuel 4C doit rester hors des contrôles ordinaires de victoire au setup. |
| Succession | B est la référence ; A est conservée comme variante expérimentale comparative. | Le défaut Python reste A : ce n’est pas une décision de conception et il ne doit pas configurer la référence. |
| Défaite du donneur après retrait | Désactivée immédiatement après le retrait du jeton proposé. Les contrôles ultérieurs autorisés par les règles restent actifs. | Référence `donor_defeat_after_removal=False`. L’option activée reste un bras comparatif, pas la valeur de référence. |
| Refus | Si le sac commun n’est pas vide : le donneur remet secrètement le jeton proposé dans son sac ; le destinataire pioche au hasard dans le sac commun ; la couleur piochée est révélée publiquement. | Référence `reveal_refusal_draw=True`. Si le sac est vide, le refus est impossible et le cadeau est accepté de force : aucune pioche n’a lieu. |
| Pioche de rejeu en A | Si le joueur devant rejouer n’a plus de jetons personnels et pioche dans le sac commun, cette pioche est secrète. La même confidentialité s’applique à l’activation d’un successeur vide dans la continuation A. | Référence `reveal_replay_draw=False`. La règle et l’option concernent A ; elles ne sont pas étendues à B, où un successeur au sac vide est éliminé sans pioche. |
| Mode C : points | 1 point par élimination d’un adversaire attribuée ; 1 point bonus au gagnant de chaque manche. Les points d’élimination, bonus, fin de manche et fin de partie sont distincts. Si le seuil n’est pas atteint, le score maximal détermine le gagnant de manche, qui peut être éliminé. | Décision de conception validée ; ce choix remplace pour le gagnant de manche la règle du dernier survivant de la v67. L’implémentation et les tests restent à adapter. |
| Mode C : seuil de manche | Calculé depuis le nombre de joueurs au début de la manche : 4→2, 5→2, 6→3, 7→3, 8→4 éliminations créditées. | Décision validée ; le code n’a pas cette table automatique et reçoit un seuil scalaire `elimination_threshold`. Une configuration distincte doit être fournie pour chaque taille de table. |
| Mode C1 | Trois manches avec scores cumulés ; si égalité au score maximal après la troisième, une manche supplémentaire ; si l’égalité persiste, victoire partagée. | Règle v67 ; défaut actuel `fixed_rounds=3`, implémentation et tests présents. |
| Mode C2 | Format exclusif de C1 ; objectif de score selon le nombre au début de la partie : 4→6, 5→7, 6→8, 7→9, 8→10. La manche en cours va à sa fin avant que la partie soit conclue. | Décision validée ; le code reçoit un `points_threshold` scalaire et le vérifie à la fin de manche. Le mode C choisit C1 ou C2, jamais les deux critères de fin cumulativement. |
| Cartes | Les variantes, seuils et associations retenus sont ceux de `catalogue_cartes_reference.md`. Les seuils sont une base de conception et restent à équilibrer. | Les conditions simples sont prises en charge ; les expressions composées B, l’objectif 4C dépendant du rang et la réserve de 24 cartes ne sont pas représentables fidèlement par le code actuel (voir §10). |

### Jetons initiaux et reste au sac commun

| Joueurs en début de manche | Jetons distribués (3 chacun) | Jetons restants sur 52 avant les effets ultérieurs de mise en place |
|---:|---:|---:|
| 4 | 12 | 40 |
| 5 | 15 | 37 |
| 6 | 18 | 34 |
| 7 | 21 | 31 |
| 8 | 24 | 28 |

Une collection invalide peut rendre des jetons au sac et entraîner un nouveau tirage. Le tableau donne le compte après la première distribution nominale, avant ces reprises. Le code `engine/setup.py::_deal_valid_hands` distribue bien trois jetons avec le défaut actuel, réessaie les mains perdantes/gagnantes et refuse une préparation infaisable ; la qualité de sa configuration de cartes demeure une limite distincte.

## 3. Paquets par mode et cycle d’une manche

- **Modes A et C :** utiliser exclusivement le paquet A/C du catalogue, 24 cartes de défaite seule. En mode C, les cartes sont réattribuées à chaque nouvelle manche.
- **Mode B :** utiliser exclusivement le paquet B, 24 cartes avec l’association victoire/défaite de chaque variante. Une nouvelle manche redistribue les cartes et réinitialise le rang des éliminations lié à 4C.
- **Capacité :** 24 cartes physiques permettent de distribuer une carte à 4, 5, 6, 7 ou 8 joueurs. Pour une manche de N joueurs, N cartes sont tirées/attribuées sans doublon physique et les 24−N restantes ne sont pas en jeu.
- Le code actuel ne peut pas encore charger ces paquets comme une réserve valide : `CardPool` exige actuellement deux cartes par `ConditionKind`, alors que le catalogue a 8 cartes `COLOR_COUNT`, 12 `TWO_PAIRS`, 2 `TOTAL_COUNT` et 2 `DIVERSITY`. L’insuffisance est structurelle, pas une insuffisance du nombre physique de cartes.

## 4. Succession de référence B et variante expérimentale A

### B — référence

Sans élimination, le destinataire devient actif. Après l’élimination du destinataire, la chaîne désigne le prochain joueur vivant dans le sens horaire, en sautant les joueurs déjà éliminés. Si ce successeur a un sac personnel vide, il est éliminé, puis la chaîne reprend depuis sa place. En mode C, chaque élimination forcée non terminale d’un adversaire dans cette chaîne est créditée au joueur responsable de l’action initiale, même si celui-ci a déjà été éliminé.

Après chaque élimination forcée, conserver exactement la priorité v67 :

1. zéro survivant → égalité terminale, sans point ni bonus pour la dernière élimination ; les points acquis avant cette dernière élimination restent acquis ;
2. si des joueurs restent, attribuer le point de l’élimination admissible et vérifier le seuil C ; s’il est atteint, finir la manche et donner le bonus au joueur qui a atteint le seuil ;
3. si le seuil n’est pas atteint et qu’il reste un seul survivant, terminer la résolution/la manche : fin de partie A/B, ou fin de manche C dont le gagnant et le bonus sont déterminés par le classement aux points. En C, le dernier survivant ne gagne pas automatiquement ; le gagnant aux points peut avoir déjà été éliminé ;
4. continuer uniquement si plusieurs joueurs restent et aucune fin immédiate ne s’applique.

L’égalité terminale d’une action qui élimine tout le monde reste prioritaire et distincte d’une égalité de score à la fin d’une manche C ou du classement final C1/C2. La décision sur le gagnant au score en C ne modifie pas cette priorité. C2 ne met pas fin à la partie au milieu de la manche ; le seuil total est vérifié après la fin de manche et son bonus.

### A — comparaison

Après une élimination, le responsable rejoue immédiatement s’il est toujours en jeu et si aucune fin immédiate ne s’applique. S’il n’a plus de jeton, il pioche si le sac commun en contient ; la pioche est secrète par défaut et les conditions sont contrôlées après celle-ci. Si le responsable est éliminé ou ne peut pas piocher, la succession reprend dans le sens horaire après sa place ; un successeur vide suit les règles v67 de variante A. Une élimination par l’absence de jeton ou par la propre pioche de rejeu ne rapporte pas de point à un autre joueur. La visibilité publique de cette pioche reste une option expérimentale dans le moteur.

Ces effets sont définis dans `specifications/game_flow.md` §§8, 12. La fin prioritaire de B est également établie dans la v67 §4.4 et `engine/transitions.py::_clockwise_chain`. Le choix B comme référence est nouveau ; le défaut actuel de `GameConfig` (`Succession.REPLAY_RESPONSIBLE`, soit A) ne le remplace pas.

## 5. Refus, visibilité et contrôles du donneur

### Séquence de référence après refus

1. Un refus n’est possible que si le sac commun contient un jeton ; sinon le cadeau est accepté de force.
2. Si le donneur est encore en jeu, le jeton proposé retourne dans son sac personnel. L’événement public de retour n’expose ni couleur ni identifiant. Le donneur connaît évidemment son propre jeton.
3. Le destinataire pioche ensuite au hasard dans le sac commun.
4. La couleur et l’identifiant de cette pioche sont publiques dans l’événement si `reveal_refusal_draw=True`, choix de référence. Le destinataire possède également le jeton dans sa vue privée.

Le moteur permet les deux options mais initialise `reveal_refusal_draw=False`. Le code de `simulation/experiments.py` garde aussi ce défaut caché. Le comportement du code **avec l’option de référence activée** respecte la visibilité voulue ; le défaut et le benchmark actuel ne la respectent pas comme configuration de référence.

Les appels d’agent reçoivent des vues publiques/privées via les contrôleurs. L’historique public est construit depuis `public_data`, qui masque les données d’un retour secret et, si le réglage est caché, les données de la pioche. L’état moteur interne (`GameState.events`) conserve des détails internes tels que l’identifiant du jeton ; ce journal interne n’est pas la vue publique remise aux agents. Le runner de simulation conserve les compteurs d’événements et les mesures, pas la charge utile complète des événements internes ; les exports incluent la configuration et `event_counts_json`, pas la couleur cachée d’une pioche.

### Défaite du donneur après retrait

Référence : ne pas contrôler la défaite du donneur juste après le retrait (`donor_defeat_after_removal=False`). Ce réglage ne supprime pas ses contrôles ultérieurs à d’autres événements prévus par les règles. L’option activée contrôle la main du donneur juste après retrait et avant la décision du destinataire (`engine/transitions.py::_propose`) ; elle peut l’éliminer et maintient la proposition en cours. Le moteur respecte la référence par son défaut, et `tests/test_gifts.py::test_t16_disabled_donor_removal_check_does_not_eliminate_donor` couvre le cas désactivé. Les tests couvrent également la variante activée. Le benchmark ne constitue pas une décision sur ce choix.

### Pioche secrète en A

Référence : `reveal_replay_draw=False`. En variante A, le jeton tiré pour le rejeu du responsable ou l’activation d’un successeur vide reste secret dans l’événement public ; il apparaît au joueur dans sa propre collection privée. Le même champ régit les pioches de rejeu/successeur A, et n’est pas consulté dans la chaîne B, qui élimine un successeur vide sans piocher. Défaut code et règle de secret par défaut sont cohérents ; une révélation publique est une variante comparative.

## 6. Mode C : règles de score et paramètres validés

### Seuils de référence

| Joueurs au début de la manche | Seuil d’éliminations créditées | Joueurs au début de la partie | Objectif C2 |
|---:|---:|---:|---:|
| 4 | 2 | 4 | 6 |
| 5 | 2 | 5 | 7 |
| 6 | 3 | 6 | 8 |
| 7 | 3 | 7 | 9 |
| 8 | 4 | 8 | 10 |

Le nombre retenu au début de la partie/manche détermine la valeur ; on ne la recalcule pas selon les joueurs encore vivants. En mode C, les joueurs reviennent à chaque nouvelle manche, de sorte que l’effectif de départ du jeu reste la référence. Une élimination adverse attribuée vaut 1 point et progresse d’autant le compteur de manche ; auto-élimination, propre pioche de rejeu et égalité terminale ne gagnent pas de point d’élimination. Le gagnant de manche reçoit 1 point bonus.

### C1 / C2

- **C1** : trois manches à scores cumulés, puis une manche supplémentaire en cas d’égalité au score maximal ; égalité persistante après le départage = victoire partagée. C’est le format fixe, pas une course à un seuil de score.
- **C2** : format alternatif au C1. Le seuil C2 choisi selon la table ci-dessus est contrôlé en fin de manche, après attribution du bonus. Atteindre l’objectif total C2 pendant une action ou une chaîne ne met pas immédiatement fin à la manche ; la chaîne peut néanmoins s’arrêter selon le seuil d’éliminations C, qui est un contrôle distinct. Le classement final se fait aux scores totaux, et les leaders ex aequo partagent la victoire. Si l’objectif n’est pas atteint après le bonus, une nouvelle manche commence.
- Ces formats sont mutuellement exclusifs. Une partie ne cumule pas la fin après trois manches du C1 et l’objectif de points du C2.

### Gagnant d’une manche sans seuil atteint : décision validée, implémentation en attente

**Si le seuil d’éliminations n’est pas atteint, le joueur qui possède le plus de points à la fin de la manche la gagne et reçoit le bonus d’un point.** Ce joueur peut avoir déjà été éliminé : le dernier survivant ne gagne pas automatiquement la manche C. Si le seuil est atteint, la victoire de manche revient au joueur dont le compteur a atteint ce seuil. Les priorités v67 non incompatibles restent en vigueur : en particulier, vérifier d’abord l’égalité terminale à zéro survivant ; le seuil est vérifié avant le contrôle du dernier survivant. Le dernier survivant termine la résolution de chaîne/la manche quand le seuil n’a pas été atteint, mais ne détermine pas à lui seul le vainqueur.

Cette décision de conception est validée, mais diverge de la v67 §6.3 et de `specifications/game_flow.md` §8.3, qui attribuent actuellement la manche C et son bonus au dernier survivant en l’absence de seuil. `engine/transitions.py::_decide` et `_clockwise_chain` appellent actuellement `_finish_round` avec ce survivant ; le code ne recherche pas le meneur au score, y compris s’il est éliminé. Il ne faut donc pas présenter la nouvelle règle comme implémentée ou testée : le texte source devra être harmonisé et l’implémentation ainsi que les tests adaptés dans une phase ultérieure.

Si plusieurs joueurs sont à égalité au score maximal lorsqu’aucun n’a atteint le seuil, le choix reste ouvert entre **partager la victoire de manche** et **jouer une manche supplémentaire pour les départager**. La manche supplémentaire prévue en C1 s’applique à une égalité du classement final après trois manches ; elle ne tranche pas cette égalité à la fin d’une manche. Les modalités détaillées du départage et l’attribution du bonus dans ce cas ne sont pas décidées ici.

## 7. Configuration effective du code et des simulations

| Élément | Code courant (`rules/config.py`) | Benchmark courant (`simulation/experiments.py`) | Écart par rapport à la référence |
|---|---|---|---|
| Succession | `Succession.REPLAY_RESPONSIBLE` (A) | A par défaut ; B est un profil de variante | La référence est B ; la configuration principale devra le demander explicitement. |
| Contrôle du donneur | `donor_defeat_after_removal=False` | Faux par défaut | Aligné avec la référence. |
| Visibilité après refus | `reveal_refusal_draw=False` | Cachée | La référence exige une révélation publique ; configurer `True`. |
| Visibilité des pioches A | `reveal_replay_draw=False` | Cachée | Aligné avec la référence A secrète ; ne pas l’appliquer à B. |
| Mains initiales | `initial_hand_size=3` | 2 | Benchmark non conforme au setup de référence. |
| Sac | Paramètre explicite, pas de configuration générale intégrée | 8 rouges + 8 bleus | Pas les quatre couleurs / 13 chacune / 52. |
| Nombre de joueurs | Validation générique ≥2 si config faisable | Référence 4 joueurs ; interface intégrée annoncée 2–4 | Ne couvre pas 4–8. |
| Seuil d’éliminations C | Obligatoire, scalaire `elimination_threshold`, pas de seuil automatique selon joueurs | 1 pour le benchmark C | Ne correspond pas à la table 4→2, 5→2, 6→3, 7→3, 8→4. |
| Partie C | Défaut C1, `fixed_rounds=3`, bonus 1 ; C2 demande `points_threshold` explicite | Benchmark C utilise C1, deux manches expérimentales et seuil d’éliminations 1 | Les valeurs de benchmark sont artificielles ; aucun seuil C2 de référence n’y est fixé. |
| Cartes | `cards` exige exactement une carte par joueur ; `card_pool` représente la réserve et en valide la structure | Paquet de quatre cartes artificiel pour quatre joueurs | Les 24 cartes de chaque catalogue ne sont pas chargeables par `CardPool` actuel, voir §10. |

Les tests de simulation existants sont des tests de comportement et de reproductibilité, souvent sur deux à quatre joueurs, des mains/paquets construits et des graines déterministes. Ils n’établissent pas l’équilibre du catalogue, des seuils ni des configurations 4–8. `simulation/README.md` qualifie explicitement les benchmarks d’expérimentaux et non officiels.

## 8. Audit de conformité

| Sujet | Décision de référence | Règle source | Comportement du code | Tests existants | Statut |
|---|---|---|---|---|---|
| 4–8 joueurs, cible 6 ; 52 jetons, 13 par couleur | Configuration validée | v67 §3 donne 40/4/8 comme hypothèse ; catalogue fixe 52 et 4–8 | Mapping de stock configurable, validation générique ≥2. Aucun défaut/set de référence 52 n’est fourni. | `tests/test_setup.py` teste distributions simplifiées ; benchmarks 2–4 joueurs seulement. | Décision validée, implémentation/configuration de référence à ajouter ; équilibre non vérifié. |
| 3 jetons initiaux et contrôle initial | 3 chacun ; collections invalides repiochées, sans élimination réelle | v67 §§3, 6.3 | `initial_hand_size=3`; `engine/setup.py::_deal_valid_hands` rejette pertes et victoires B de collection, cherche une distribution faisable ; nouvelles manches redistribuent. | `tests/test_setup.py` (T01–T06/T55), `tests/test_card_pool.py`; `test_t42_new_round_resets_elimination_counters_but_keeps_scores_and_redeals`. | Conforme au mécanisme de deal testé, mais le paquet de référence et 4–8 joueurs ne sont pas encore utilisables via `CardPool`. |
| Paquets 24 A/C et 24 B | Deux configurations séparées, pas un paquet hybride | Catalogue de cartes §§2–4 ; v67 §§3, 8 | `CardPool` impose actuellement un effectif de deux par enum `ConditionKind`, incompatible avec 8 `COLOR_COUNT` et 12 `TWO_PAIRS`. L’injection directe exige exactement N cartes et ne pioche pas dans un catalogue de 24. | `tests/test_card_pool.py` couvre réserves génériques, pas les paquets complets du catalogue. | Divergence identifiée ; implémentation à vérifier avant simulation. |
| Conditions de défaite catalogue | 12 variantes et seuils précis du catalogue | v67 §8 laisse le catalogue ouvert ; catalogue `catalogue_cartes_reference.md` | Types simples pris en charge, mais conditions composées/sélection de paquet doivent être vérifiées ; le moteur actuel ne charge pas la réserve complète. | `tests/test_config.py`, `tests/test_regressions_point2.py` couvrent sémantiques génériques ; aucun test de catalogue 24 cartes. | Décision validée ; catalogue non couvert dans son ensemble. |
| Objectifs ordinaires B | Associations catalogue, victoire et défaite incompatibles | v67 §6.2 exige objectif/vérifications, §8 laissait objectifs ouverts | `Card.victory` est un seul `Condition`; formules CD/DP/ACC requièrent des conjonctions/exclusions. `_conditions_overlap` rejette les chevauchements, mais ne sait pas exprimer la priorité conditionnelle souhaitée. | `tests/test_modes.py::test_t61_complete_deterministic_secret_objective_pilot_wins_on_authorized_gift`, tests de config/overlap ; aucune association catalogue testée. | Divergence identifiée ; tests du catalogue requis après représentation des expressions. |
| Objectif B 4C par cause et rang | Élimination due à 4C et rang 1/2/3 selon 4–8, barème du catalogue | v67 §§8, 12 n’établissent qu’un objectif d’élimination précoce générique ; catalogue §5.4 tranche le cas 4C | Aucun rang ou compteur d’éliminations dans `Card`/`GameState`; `_check_recipient` teste victoire avant défaite pour un joueur vivant. N’enregistre pas une victoire post-élimination conditionnée par cause/rang. | Aucun test de rang 4C. | Divergence identifiée ; non implémenté et non testé. |
| Succession B et ordre terminal | B référence ; zéro survivant, seuil C, dernier survivant, continuer seulement sans fin immédiate | v67 §4.4, §6.3 et `specifications/game_flow.md` §8.3 | `_decide` vérifie fin initiale, point/seuil, puis survivant ; `_clockwise_chain` traite une élimination forcée à la fois, attribue point si non terminal, teste seuil avant dernier survivant. | `tests/test_regressions_point2.py::test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus`; `tests/test_modes.py::test_t63_variant_comparison_is_recorded_as_distinct_explicit_configurations`. | Ordre B conforme et testé ; sélection B comme défaut de conception n’est pas le défaut actuel (`GameConfig` reste A). |
| Succession A expérimentale et pioche secrète | A conservée en comparaison ; pioche de rejeu/successeur secrète | v67 §4.4 / registre ; `specifications/game_flow.md` §8.2 | A réplique le responsable ; `reveal_replay_draw=False` masque les données publiques ; le code n’utilise pas cette option pour la chaîne B. | `tests/test_eliminations.py::test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag`, `test_t70_empty_successor_draws_and_survives_with_configured_visibility`. | Conforme pour la variante secrète ; l’option visible est expérimentale. |
| Donneur après retrait | Contrôle immédiat désactivé ; contrôles ultérieurs conservés | v67 §§4.1, 7 et `specifications/game_flow.md` §12 | `donor_defeat_after_removal=False` saute le contrôle à `_propose`; autres checks d’événements persistent. | `tests/test_gifts.py::test_t16_disabled_donor_removal_check_does_not_eliminate_donor`; variantes activées aussi couvertes. | Conforme au réglage de référence ; benchmark optionnel. |
| Refus : retour secret, nouvelle pioche publique | `reveal_refusal_draw=True` en référence | v67 §4.3 permet les deux visibilités ; `game_flow.md` §§7, 12 | Retour donneur publié sans id/couleur ; pioche publique seulement si le flag est vrai ; config et benchmark par défaut le cachent. Les exports de simulation ne publient pas le contenu d’événements internes. | `tests/test_gifts.py::test_t08_refusal_returns_offer_and_draws_replacement_with_configured_visibility`; `tests/test_privacy.py::test_t08_t28_hidden_refusal_draw_is_known_to_recipient_but_not_public`; T81 couvre retour/pioche si donneur éliminé. | Divergence de valeur par défaut, comportement configurable ; référence publique à demander explicitement. |
| Seuil C dépendant du nombre | 4→2, 5→2, 6→3, 7→3, 8→4 au début de manche | v67 §6.3 propose 3 à ajuster ; nouvelle table validée ici | Seuil unique obligatoire en config, aucun calcul basé sur effectif initial. | Tests C vérifient seuil ponctuel, pas la table multi-effectif. | Décision validée, implémentation/configuration multi-effectif absente ; test table requis. |
| Attribution d’éliminations B en chaîne | Un point à l’initiateur pour chaque élimination forcée non terminale d’un autre joueur ; aucune attribution terminale/auto-élimination | v67 §6.3, §4.4 ; `game_flow.md` §8.3/§12 | `_clockwise_chain` crédite l’initiateur puis vérifie le seuil après chaque élimination forcée ; l’action initiale éliminant tous les joueurs est terminale avant crédit. | `tests/test_regressions_point2.py::test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus`; `test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards`. | Conforme pour les cas couverts. |
| Gagnant C sans seuil atteint | Joueur au plus grand score en fin de manche, même s’il a été éliminé ; bonus 1 | Décision de conception validée ; v67 §6.3 et `game_flow.md` §8.3 indiquent encore le dernier survivant | `_decide`/`_clockwise_chain` transmettent actuellement le dernier survivant à `_finish_round`, sans chercher le meneur au score. | Aucun test du gagnant éliminé au classement de manche sans seuil. | Divergence texte/code ; harmonisation de la règle source, adaptation du moteur et tests requis ultérieurement. |
| C1 | Trois manches cumulatives ; tiebreak en cas d’égalité, puis égalité partagée si elle persiste | v67 §6.3, `game_flow.md` §10 | `fixed_rounds=3`, `_finish_round` déclenche une manche de départage et `_leaders` permet plusieurs gagnants finaux. | `tests/test_modes.py::test_t43_c1_ends_after_three_rounds_using_cumulative_scores`, `test_t44_c1_tiebreak_round_shares_persistent_tie_or_accepts_new_leader`. | Conforme aux règles finales de partie ; le résultat individuel d’une manche sans seuil reste divergent. |
| C2 et fin de manche | Seuil selon joueurs au début ; finir manche et bonus avant classement final | v67 §6.3 ; `game_flow.md` §10 | `points_threshold` scalaire vérifié dans `_finish_round` après bonus ; la chaîne B s’arrête au seuil de manche ou au dernier survivant, non au seuil C2. | `tests/test_modes.py::test_t46_c2_below_threshold_can_begin_another_round`, `test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus`. | Moment de contrôle conforme ; table de seuils non automatisée et non testée. |

## 9. Décisions qui restent ouvertes

1. **Égalité au score maximal en fin d’une manche C sans seuil atteint :** choisir entre partager la victoire de manche et jouer une manche supplémentaire pour départager les joueurs concernés. La règle C1 de manche supplémentaire porte sur l’égalité du classement final après trois manches et ne tranche pas cette égalité de manche. Les modalités détaillées et l’attribution du bonus dans ce cas restent à définir.
3. **Plusieurs porteurs 4C éligibles dans un rang partagé :** tous satisfont le critère de rang selon le catalogue, mais la conséquence de fin de partie B n’indique pas explicitement si plusieurs porteurs gagnent ensemble ou si un seul événement de victoire est retenu. Aucun comportement moteur n’existe encore.
4. **Objectif d’élimination précoce générique et pouvoirs secrets :** v67 §§8–9/12 laisse ces sujets en phase de conception. Le catalogue a défini une exception précise pour les cartes 4C, mais ne formalise pas de mécanique générique au-delà ; confirmer ultérieurement si cette exception suffit ou si l’objectif générique reste souhaité. Les pouvoirs peuvent attendre une phase ultérieure.

Les cas de seuil dans une chaîne et les points attribués à l’initiateur sont définis en v67 : chaque élimination forcée est traitée successivement ; l’initiateur reçoit le point pour l’élimination non terminale d’un adversaire, puis le seuil est contrôlé immédiatement ; le premier compteur qui atteint le seuil termine la manche avant la poursuite. Si une même opération future pouvait faire franchir simultanément le seuil à plusieurs joueurs, le texte/code ne définit pas de départage de cette situation ; aucun chemin normal actuel ne crédite plusieurs joueurs dans une seule étape de chaîne.

## 10. Étapes avant les simulations finales

1. Appliquer ultérieurement la règle du meilleur score lorsque le seuil C n’est pas atteint ; décider séparément le traitement de l’égalité au score maximal et du bonus associé.
2. Implémenter sans altérer le mécanisme de distribution : réserve physique par variante, expressions composées de victoire/défaite et objectif contextuel 4C ; conserver les contrôles de faisabilité, la graine et la redistribution à chaque manche.
3. Construire des configurations A, B et C reproduisant les deux paquets distincts, le sac 13×4, trois jetons initiaux, 4–8 joueurs, seuil C en fonction du nombre initial, B de référence, contrôle donneur désactivé, pioche après refus publique, et C1/C2 exclusifs.
4. Ajouter les tests d’acceptation catalogue, faisabilité 8 joueurs, scores/seuils par effectif, refus/publicité, rang 4C et priorité de succession B ; aucun paramètre n’est considéré vérifié par la seule mise à jour documentaire.
5. Lancer ensuite seulement des campagnes équilibrage distinctes pour chaque nombre de joueurs 4–8, en mettant en évidence six joueurs comme cible, avec graines et profils reproductibles. Garder A, le contrôle du donneur activé et les autres options comme bras expérimentaux séparés.

## Sources examinées

- `C'est cadeau !.docx`, version 67 : §§3–8, 12–14 et registre des décisions.
- `specifications/catalogue_cartes_reference.md`.
- `specifications/audit_decisions_ouvertes.md`.
- `specifications/game_flow.md`, `rules_spec.md`, `audit_final_coherence.md`.
- `rules/config.py`, `rules/cards.py`, `rules/card_pool.py`, `rules/rules.py`.
- `engine/setup.py`, `engine/transitions.py`, `engine/state.py`, `engine/selection.py`.
- `simulation/experiments.py`, `simulation/runner.py`, `simulation/README.md`.
- Tests mentionnés dans la matrice, notamment `tests/test_modes.py`, `test_gifts.py`, `test_eliminations.py`, `test_privacy.py`, `test_card_pool.py`, `test_setup.py`, `test_regressions_point2.py` et `test_simulation_experiments.py`.
