# Validation G2 — porte documentaire empirique

## Verdict

**`DOCUMENTARY_BLOCK`** — aucune performance G2 n'a été calculée.

Le protocole G2 a été figé avant l'exécution d'une nouvelle politique. Le
contrôle hors ligne retrouve les quatre artefacts publiés de la comparaison
C1–C2, mais aucune des six sources originales obligatoires n'est présente dans
le clone de travail. Ces artefacts dérivés ne remplacent pas les données brutes.

## Contrôle exécuté

Le script [`g2_empirical_readiness.py`](../scripts/g2_empirical_readiness.py) :

1. résout les six identifiants dans `data_manifest.json` ;
2. exige le chemin, la taille et l'empreinte SHA-256 exacts ;
3. inventorie séparément les résultats historiques versionnés ;
4. produit `readiness_report.json` ;
5. interdit la présence de toute sortie de performance tant que le verdict est
   `DOCUMENTARY_BLOCK`.

Le résultat courant est :

| Contrôle | Résultat |
|---|---|
| Yahoo SPY original | `FILE_MISSING` |
| Yahoo BIL original | `FILE_MISSING` |
| Distributions State Street | `FILE_MISSING` |
| Calendrier NYSE 2022–2025 | `FILE_MISSING` |
| Règle SEC T+1 | `FILE_MISSING` |
| Guide DTCC T+1 | `FILE_MISSING` |
| Contrôles C1–C2 publiés | 4 sur 4 présents et hachés |
| Richesse ou performance G2 | non calculée |

Le rapport machine se trouve sous
[`results/g2_empirical_sequentiality/readiness_report.json`](../results/g2_empirical_sequentiality/readiness_report.json).

## Tests

Six tests ciblés valident :

- l'ouverture de la porte avec un original exact ;
- le blocage si le fichier manque ;
- le blocage si l'empreinte diffère ;
- l'impossibilité de substituer un résultat dérivé à une source brute ;
- l'écriture exclusive du rapport de préparation en cas de blocage ;
- le refus d'un répertoire bloqué contenant déjà une sortie de performance.

## Condition exacte de reprise

Les documents antérieurs indiquent une sauvegarde contrôlée sur le disque
physique distinct, notamment sous
`D:\ai-financial-risk-reliability-data-backup\2026-10-19\` et, pour certains
documents de règlement, sous la sauvegarde datée du 20 octobre 2026.

G2 pourra reprendre uniquement après restauration des fichiers à leurs chemins
relatifs du manifeste et concordance des six empreintes. Un nouveau
téléchargement dont l'empreinte diffère restera `HASH_MISMATCH`. À ce moment, la
prochaine étape sera l'exécution appariée `M_G2`–`D_G2` définie par le protocole,
pas une modification de celui-ci et pas PPO.

## Portée scientifique

Ce blocage est un résultat de reproductibilité, non un échec de la méthode. Il
empêche que des données actuelles ou des sorties agrégées soient silencieusement
présentées comme les sources gelées du moteur historique. Le seul verdict
scientifique établi à ce stade reste donc la préparation documentaire de G2.
