# Agents de « C'est cadeau ! »

Les agents reçoivent un `PlayerController`, sa `PrivateView` filtrée, les actions légales et les messages destinés aux participants. Le moteur reste la seule autorité sur les règles; une stratégie ne reçoit jamais l'état interne.

## Décisions

- `ReferenceDecision` : politique déterministe de référence, choix dans l'ordre légal et refus quand il est permis.
- `RandomDecision` : choix uniforme parmi les actions légales; `AgentPolicy.for_game()` lui attribue une graine stable calculée depuis la graine de partie, l'identifiant du joueur et le composant.
- `CautiousDecision` : sélectionne un jeton qui ne déclenche pas sa propre défaite connue après retrait et refuse un cadeau inconnu lorsque c'est légal.
- `AlwaysAcceptDecision` et `AlwaysRefuseDecision` : points de comparaison dont les choix respectent toujours les actions légales.
- `ScriptedDecision` : conserve le comportement paramétrable utilisé par les tests déterministes.

Les agents aléatoires sont recréés pour chaque joueur et chaque partie. La dérivation des graines utilise BLAKE2, jamais `hash()`. L'ordre d'exécution des campagnes précédentes n'affecte donc pas leur flux aléatoire.

## Communication

`SilentCommunication`, `ScriptedCommunication` et `ColorClaimCommunication` sont combinables indépendamment des stratégies de décision. Cette dernière permet les annonces véridiques, le bluff, les questions, les réponses et le silence configuré. La véracité d'un message ne détermine pas la décision du destinataire. La chaîne de communication est tenue par l'orchestrateur et n'agit pas sur l'état du moteur.
