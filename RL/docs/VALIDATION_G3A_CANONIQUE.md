# Validation canonique G3A — 11 novembre 2026

## Verdict de reproductibilité

**Statut : `G3A_CANONICAL_VALIDATED`.**

Le script officiel `RL/scripts/g3_learning_value.py` du commit GitHub
`be553d8bb5ecb9474a74078f4c6a69b8cbf9652e` a été exécuté avec les deux réponses
Yahoo originales. La porte documentaire a confirmé les tailles et les SHA-256
du manifeste avant tout calcul :

- SPY : `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` ;
- BIL : `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` ;
- protocole G3 : `5caba8a67da6a8ceef721ad2ddc2dde1d9a3cee7780674d6d7cd40309afefd79`.

Les quatre fichiers canoniques correspondent exactement aux empreintes publiées
par la reproduction indépendante :

| Sortie | SHA-256 canonique | Concordance |
|---|---|---|
| `model_estimates.csv` | `0d714f511cdbbab8c10f1309c95b3659659ba54ab0181a25fd1aae0f2fdd59e5` | exacte |
| `policy_decisions.csv` | `21af4ddd915f65d3db3434190e66b45891380a698d9345e524567a751bb6bb55` | exacte |
| `wealth_paths.csv` | `1ae6c384afb895123744663ef0faa22fb6a104580e3e96501c721b53c7b1eb4e` | exacte |
| `paired_comparison.csv` | `f28706978ac9aee57811ed20a0c6bcca38615b95b696b1e1a1fe43b2f3f6c192` | exacte |

Le rapport canonique `g3_report.json` porte l'empreinte
`db030b657197dd9ea8f6382047ce676b2409868d3e8e806aeba200086a157a6f`.

## Résultat primaire confirmé

Sur les 46 décisions du 2 juin 2025 au 13 avril 2026, avec close terminal le
17 avril 2026 et coût de 10 pb :

| Politique | Richesse terminale |
|---|---:|
| `D_G2_FROZEN` | 112 178,85 USD |
| `D_G3_LEARNED` | 117 476,70 USD |
| `M_G3_LEARNED` | 117 476,70 USD |

La différence appariée est de **+5 297,85 USD**, supérieure au seuil gelé de
250 USD. Le verdict primaire `G3_LEARNING_VALUE_POSITIVE` est donc reproduit
par l'implémentation canonique.

## Interprétation scientifique obligatoire

Ce verdict ne démontre aucune valeur incrémentale du RL :

- `D_G3_LEARNED` et `M_G3_LEARNED` ont exactement les mêmes actions, coûts et
  richesses ;
- après quatre décisions de warm-up à 50/50, les deux passent à 100 % SPY et
  conservent cette cible ;
- aucune valeur additionnelle de la programmation dynamique ou de la matrice de
  transition apprise n'est observée ;
- le résultat repose sur des closes Yahoo non ajustés, sans distributions,
  exécution, bid/ask, parts entières ou règlement.

Ainsi, le résultat positif mesure uniquement une différence face au contrôleur
stylisé `D_G2_FROZEN`. Il n'autorise pas PPO, CQL ou IQL sur le problème actuel.

## Contrôles

Les neuf tests G3 passent, notamment : séparation du holdout G2, absence de
fuite future, invariance du contrôleur gelé, calendriers appariés, warm-up,
reproductibilité octet pour octet et interdiction d'écrire une performance
lorsque la porte documentaire échoue.

La prochaine décision scientifique est distincte de cette validation : soit
clore SPY–BIL comme résultat négatif pour la nécessité du RL, soit préspécifier
un problème plus riche dans lequel l'action présente modifie réellement les
contraintes et opportunités futures.
