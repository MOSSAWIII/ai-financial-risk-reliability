# Validation du test structurel de séquentialité V2

## 1. Verdict

Le test structurel gelé dans
[`PROTOCOLE_SCIENTIFIQUE_V2.md`](PROTOCOLE_SCIENTIFIQUE_V2.md) a été exécuté
avec le script
[`../scripts/sequentiality_test.py`](../scripts/sequentiality_test.py).

**Verdict : `G1_PASS — STRUCTURAL_SEQUENTIALITY_IDENTIFIED`.**

Les coûts de rotation et la position héritée créent une valeur strictement
positive de la programmation dynamique dans une zone intermédiaire de coûts du
laboratoire synthétique. Les contrôles à coût nul et à horizon unitaire
retrouvent exactement l'équivalence attendue.

Ce verdict ne porte ni sur les données historiques, ni sur la rentabilité de
SPY–BIL, ni sur la nécessité d'un algorithme RL.

## 2. Entrées verrouillées

L'exécution canonique reprend sans modification les paramètres arrêtés après la
phase de conception du laboratoire :

- deux régimes `RISK_ON` et `RISK_OFF` ;
- matrice de transition `[[0.80, 0.20], [0.35, 0.65]]` ;
- rendements hebdomadaires SPY de `0,20 %` et `0,00 %` ;
- rendement hebdomadaire BIL de `0,10 %` dans les deux régimes ;
- cinq poids SPY admissibles : `0`, `0,25`, `0,50`, `0,75`, `1` ;
- poids initial SPY de `0,50` ;
- horizon de douze décisions ;
- coûts de `0`, `5`, `10`, `25`, `50` et `100` points de base ;
- espérance exacte, sans simulation Monte-Carlo.

Les fichiers complets sont publiés sous
[`../results/sequentiality_v2/`](../results/sequentiality_v2/).

## 3. Résultats principaux

| Coût | Valeur dynamique | Valeur myope | `Delta_seq` | Gain multiplicatif | Désaccord atteignable |
|---:|---:|---:|---:|---:|---:|
| 0 pb | 0,0193713854 | 0,0193713854 | 0 | 0 % | non |
| 5 pb | 0,0177024072 | 0,0177024072 | 0 | 0 % | non |
| 10 pb | 0,0160330380 | 0,0133795669 | 0,0026534711 | 0,265699 % | oui |
| 25 pb | 0,0142322720 | 0,0133795669 | 0,0008527051 | 0,085307 % | oui |
| 50 pb | 0,0133795669 | 0,0133795669 | 0 | 0 % | non |
| 100 pb | 0,0133795669 | 0,0133795669 | 0 | 0 % | non |

Le gain multiplicatif est

\[
\exp(\Delta_{seq})-1.
\]

Il représente l'écart de richesse attendu sur les douze périodes du laboratoire,
pas un rendement annualisé estimé.

## 4. Mécanisme identifié

À `10 pb`, depuis un poids hérité de `0,50` :

| Régime | Action dynamique | Action myope |
|---|---:|---:|
| `RISK_ON` | 1,00 | 0,50 |
| `RISK_OFF` | 0,00 | 0,50 |

La politique myope ne paie pas un coût immédiat pour un avantage conditionnel
sur une seule semaine. La politique dynamique valorise la persistance du régime
et amortit ce coût sur plusieurs périodes possibles. L'écart ne vient donc pas
d'une information supplémentaire : il vient de la valeur future de la position
héritée.

À `50` et `100 pb`, les deux politiques conservent `0,50` dans les deux régimes.
Les frictions sont alors assez fortes pour supprimer toute rotation. La valeur
de la séquentialité est donc non monotone en fonction des coûts :

- coûts trop faibles : les deux politiques ajustent immédiatement ;
- coûts intermédiaires : l'horizon futur modifie la décision ;
- coûts très élevés : les deux politiques restent immobiles.

## 5. Contrôles

Les six tests de
[`../tests/test_sequentiality_v2.py`](../tests/test_sequentiality_v2.py) passent :

1. équivalence exacte à coût nul ;
2. équivalence exacte à horizon unitaire ;
3. valeur séquentielle strictement positive à `10 pb` ;
4. domination faible de la programmation dynamique sur les six coûts ;
5. rejet d'une matrice de transition invalide ;
6. passage de tous les critères de la porte G1.

Deux générations consécutives des sorties ont produit les mêmes empreintes de
fichiers. Le JSON valide en outre les probabilités et conserve les SHA-256 du
protocole et du script.

La suite complète exécutée dans la copie GitHub sans données brutes retourne
`170 passed, 2 skipped, 12 failed, 19 errors`. Les échecs et erreurs historiques
s'arrêtent sur l'absence attendue de la source locale exclue de GitHub
`yahoo_spy_chart_ohlcv_20261019`; ils ne révèlent pas une régression V2. Les six
tests V2 et les autres tests indépendants des données brutes passent.

## 6. Portée scientifique exacte

Le résultat établit l'énoncé conditionnel constructif suivant :

> Dans un modèle exogène à régimes persistants, avec position héritée et coûts
> proportionnels, une optimisation période par période peut être strictement
> sous-optimale, même lorsque l'action ne modifie pas les rendements du marché.

Il n'établit pas :

- que les deux régimes existent ou sont observables dans les données SPY–BIL ;
- que leurs transitions peuvent être estimées sans fuite temporelle ;
- que `10` ou `25 pb` représentent les coûts pertinents du mandat historique ;
- que l'effet survivra aux parts entières, dividendes et règlements ;
- qu'un agent RL battra la programmation dynamique ;
- qu'une performance future est attendue.

Le laboratoire a été conçu pour rendre le mécanisme identifiable. Il ne doit
donc pas être présenté comme une découverte statistique indépendante de sa
conception. La véritable épreuve hors échantillon appartient à G2.

## 7. Prochaine porte autorisée

G1 autorise uniquement la conception de **G2 : matérialité empirique de la
séquentialité**. G2 devra comparer une politique myope et un contrôle dynamique
classique dans le moteur historique existant, avec :

- chronologie point-in-time identique ;
- même univers d'actions ;
- mêmes coûts, parts entières, distributions et règles de règlement ;
- périodes de conception explicitement séparées des périodes d'évaluation ;
- registre de toutes les variantes examinées ;
- aucune politique RL avant conclusion de G2.

L'objet immédiat n'est donc toujours pas PPO. Il est de déterminer si le
mécanisme identifié artificiellement possède une importance empirique mesurable
et robuste.
