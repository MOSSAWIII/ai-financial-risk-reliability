# Validation G2 — matérialité empirique de la séquentialité

## Verdict

**`G2_MATERIAL_POSITIVE`**. Le passage méthodologique vers G3 est autorisé par
la règle gelée ; aucun algorithme RL n'est encore autorisé automatiquement.

## Résultat primaire

Le contrôleur dynamique `D_G2` est comparé à la politique myope `M_G2` dans les
huit cellules appariées du moteur SPY–BIL. Le seuil de matérialité était fixé à
250 USD, soit 25 pb du capital initial.

| Cellule primaire | Myope | Dynamique | Différence | Capital initial |
|---|---:|---:|---:|---:|
| S3–D+1, 10 pb | 109 466,29 USD | 113 691,55 USD | **+4 225,25 USD** | **+4,2253 %** |
| S3–D+2, 10 pb | 109 445,69 USD | 113 052,83 USD | **+3 607,14 USD** | **+3,6071 %** |

Les deux conventions dépassent le seuil avec un signe positif. `D_G2` change sa
cible neuf fois ; `M_G2` reste à 50/50 sous S3. Le surplus apparaît malgré
1 308,42 USD de frais incrémentaux en D+1 et 1 300,08 USD en D+2.

## Contrôles négatifs

Tous les contrôles gelés passent :

- 16 exécutions complètes et 832 décisions récurrentes ;
- quatre premières décisions à 50/50 pour les deux politiques ;
- en S0, S1 et S2, actions identiques et trajectoires financières identiques ;
- en S3, désaccord atteignable effectivement observé ;
- aucune source manquante et aucun arrêt documentaire ;
- toutes les intentions restent scellées avant lecture de l'open d'exécution.

Les différences S0–S2 sont exactement nulles, ce qui localise l'effet dans la
zone de coûts où G1 prédisait une valeur séquentielle.

## Risque et activité

La dynamique améliore aussi le drawdown maximum d'environ 0,95 point de
pourcentage, mais augmente la volatilité annualisée d'environ 1,20 point en D+1
et 1,12 point en D+2. Son notionnel échangé incrémental atteint environ
1,31 million USD sur l'année. Le résultat n'est donc pas une dominance uniforme
en risque : c'est une différence économiquement importante de trajectoire sous
le mécanisme gelé.

## Reproductibilité

Le script [`g2_empirical_sequentiality.py`](../scripts/g2_empirical_sequentiality.py)
produit `policy_decisions.csv`, `daily_trajectories.csv`,
`financial_summary.csv`, `paired_comparison.csv` et `g2_report.json`.

Les fichiers sont reconstruits dans un répertoire temporaire et comparés octet
pour octet. Les résultats versionnés se trouvent sous
[`results/g2_empirical_sequentiality`](../results/g2_empirical_sequentiality/).
Les deux grilles CSV gelées sont hachées sous une représentation canonique CRLF,
ce qui retrouve les empreintes publiées et supprime la dépendance au système de
fin de ligne du checkout Git.

## Interprétation scientifique

G2 montre que le mécanisme synthétique de G1 peut modifier matériellement une
trajectoire réelle du moteur lorsque les coûts atteignent 10 pb. Il ne démontre
pas que le contrôleur est optimal, que le signal prédit les marchés, ni que le
résultat se généralise.

L'épisode 2024–2025 et les résultats antérieurs avaient déjà été consultés. Le
test est donc un **diagnostic rétrospectif**, pas une validation hors échantillon.
G3 devra maintenant établir si l'apprentissage apporte quelque chose face à ce
contrôleur dynamique connu, avec une évaluation temporelle réellement séparée.
PPO ne découle toujours pas de G2.
