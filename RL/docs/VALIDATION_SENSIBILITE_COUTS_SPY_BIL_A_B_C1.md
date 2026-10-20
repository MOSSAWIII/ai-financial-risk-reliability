# Validation de la couverture et sensibilité aux coûts — SPY/BIL A/B/C1

**Périmètre :** unique épisode préspécifié du 29 mai 2024 au 29 mai 2025
**Verdict :** `COST_SENSITIVITY_VALIDATED`

## 1. Résultat synthétique

Les 251 séances attendues sont toutes présentes pour SPY et BIL, sans date propre à un seul instrument, sans OHLC nul, manquant ou non positif et sans alerte de prix applicable à l'épisode. Les 16 distributions officielles (4 SPY, 12 BIL) sont toutes acquises puis payées exactement une fois. Les richesses S0 publiées sont réconciliées à zéro près avec un calcul direct indépendant du registre.

Les scénarios S0 (0 pb), S1 (1 pb) et S2 (5 pb) sont finançables pour les trois références. Sous S3 (10 pb), A et C1 sont exécutables, mais le lot B de 1 089 parts est rejeté atomiquement : son coût théorique de 99,9375263443 USD excède les 62,4736557007 USD restant après achat. B n'est ni redimensionné ni transformé en performance nulle.

## 2. Exhaustivité des séances

Le contrôle ne déduit plus les séances de la seule intersection Yahoo. Il construit d'abord les séances attendues sur l'intervalle à partir du calendrier NYSE/ICE 2024–2025 déjà archivé et audité, des règles de jours fériés applicables et du mémo NYSE sur la fermeture exceptionnelle du 9 janvier 2025, puis compare séparément SPY et BIL.

| Contrôle | Résultat |
|---|---:|
| Séances NYSE attendues | 251 |
| Dates SPY attendues présentes | 251 |
| Dates BIL attendues présentes | 251 |
| Dates communes | 251 |
| Attendues absentes chez SPY | 0 |
| Attendues absentes chez BIL | 0 |
| Absentes chez les deux | 0 |
| SPY seulement / BIL seulement | 0 / 0 |
| Dates Yahoo inattendues | 0 |
| OHLC requis nul, manquant ou non positif | 0 |
| Dates contestées par l'audit de prix | 0 |

Les trois séances écourtées documentées et présentes sont les 3 juillet, 29 novembre et 24 décembre 2024. Les fermetures de semaine attendues dans la fenêtre sont les 19 juin, 4 juillet, 2 septembre, 28 novembre et 25 décembre 2024, puis les 1er, 9 et 20 janvier, 17 février, 18 avril et 26 mai 2025. Le 9 janvier est une fermeture exceptionnelle documentée ; aucune absence commune n'est donc convertie implicitement en fermeture.

Conclusion limitée : les 251 clôtures sont exhaustives **selon les preuves primaires et les fichiers audités disponibles pour 2024–2025**. Cette conclusion ne vaut ni inventaire intrajournalier des interruptions propres à un titre, ni nouvel audit 2018–2026.

## 3. Distributions et chronologie comptable

Le moteur parcourt désormais l'union ordonnée des séances communes, ex-dates, payment dates et dates de règlement. Une payment date hors séance commune est donc comptabilisée à sa date propre sans fabriquer une séance ni une valorisation. Dans l'épisode réel, les 16 ex-dates et les 16 payment dates coïncident toutes avec une séance commune ; le cas hors séance est néanmoins couvert par un test artificiel.

Chaque cellule de portefeuille ci-dessous donne `parts ouvrant droit / créance / paiement comptabilisé`, en USD pour les deux derniers termes.

| Symbole | Ex-date | Record date | Payment date | USD/part | A | B | C1 |
|---|---|---|---|---:|---:|---:|---:|
| BIL | 2024-06-03 | 2024-06-03 | 2024-06-06 | 0.405038 | 0 / 0 / 0 | 1089 / 441.086382 / 441.086382 | 544 / 220.340672 / 220.340672 |
| SPY | 2024-06-21 | 2024-06-21 | 2024-07-31 | 1.759024 | 188 / 330.696512 / 330.696512 | 0 / 0 / 0 | 94 / 165.348256 / 165.348256 |
| BIL | 2024-07-01 | 2024-07-01 | 2024-07-05 | 0.392200 | 0 / 0 / 0 | 1089 / 427.105800 / 427.105800 | 544 / 213.356800 / 213.356800 |
| BIL | 2024-08-01 | 2024-08-01 | 2024-08-06 | 0.402311 | 0 / 0 / 0 | 1089 / 438.116679 / 438.116679 | 544 / 218.857184 / 218.857184 |
| BIL | 2024-09-03 | 2024-09-03 | 2024-09-06 | 0.396088 | 0 / 0 / 0 | 1089 / 431.339832 / 431.339832 | 544 / 215.471872 / 215.471872 |
| SPY | 2024-09-20 | 2024-09-20 | 2024-10-31 | 1.745531 | 188 / 328.159828 / 328.159828 | 0 / 0 / 0 | 94 / 164.079914 / 164.079914 |
| BIL | 2024-10-01 | 2024-10-01 | 2024-10-04 | 0.371279 | 0 / 0 / 0 | 1089 / 404.322831 / 404.322831 | 544 / 201.975776 / 201.975776 |
| BIL | 2024-11-01 | 2024-11-01 | 2024-11-06 | 0.358528 | 0 / 0 / 0 | 1089 / 390.436992 / 390.436992 | 544 / 195.039232 / 195.039232 |
| BIL | 2024-12-02 | 2024-12-02 | 2024-12-05 | 0.334568 | 0 / 0 / 0 | 1089 / 364.344552 / 364.344552 | 544 / 182.004992 / 182.004992 |
| BIL | 2024-12-19 | 2024-12-19 | 2024-12-24 | 0.382797 | 0 / 0 / 0 | 1089 / 416.865933 / 416.865933 | 544 / 208.241568 / 208.241568 |
| SPY | 2024-12-20 | 2024-12-20 | 2025-01-31 | 1.965548 | 188 / 369.523024 / 369.523024 | 0 / 0 / 0 | 94 / 184.761512 / 184.761512 |
| BIL | 2025-02-03 | 2025-02-03 | 2025-02-06 | 0.325824 | 0 / 0 / 0 | 1089 / 354.822336 / 354.822336 | 544 / 177.248256 / 177.248256 |
| BIL | 2025-03-03 | 2025-03-03 | 2025-03-06 | 0.289327 | 0 / 0 / 0 | 1089 / 315.077103 / 315.077103 | 544 / 157.393888 / 157.393888 |
| SPY | 2025-03-21 | 2025-03-21 | 2025-04-30 | 1.695528 | 188 / 318.759264 / 318.759264 | 0 / 0 / 0 | 94 / 159.379632 / 159.379632 |
| BIL | 2025-04-01 | 2025-04-01 | 2025-04-04 | 0.321379 | 0 / 0 / 0 | 1089 / 349.981731 / 349.981731 | 544 / 174.830176 / 174.830176 |
| BIL | 2025-05-01 | 2025-05-01 | 2025-05-06 | 0.311560 | 0 / 0 / 0 | 1089 / 339.288840 / 339.288840 | 544 / 169.488640 / 169.488640 |

Les contributions totales sont 1 347,138628 USD pour A (SPY), 4 672,789011 USD pour B (BIL), et 673,569314 USD SPY plus 2 334,249056 USD BIL, soit 3 007,818370 USD, pour C1. Elles concordent exactement avec les créances créées et les paiements versés au cash ; aucune créance ne reste ouverte au terminal. `EX_POST_ACCOUNTING_ONLY` demeure actif et aucune date d'annonce fictive n'est créée.

## 4. Réconciliation indépendante de S0

Le contrôle ci-dessous est calculé directement à partir des quantités, opens, closes terminaux et distributions, sans appeler la fonction de richesse du registre :

`valeur terminale des parts + cash résiduel initial + distributions acquises − coût = richesse terminale`.

| Référence | Valeur terminale des parts | Cash initial résiduel | Distributions | Coût | Reconstruction | Registre | Écart |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 110 929.39770507813440 | 1 172.1613769531344 | 1 347.138628 | 0 | 113 448.69771003126880 | 113 448.69771003126880 | 0 |
| B | 99 872.18900299072674 | 62.4736557006904 | 4 672.789011 | 0 | 104 607.45166969141714 | 104 607.45166969141714 | 0 |
| C1 | 105 354.93835449219424 | 663.2025146484456 | 3 007.818370 | 0 | 109 025.95923914063984 | 109 025.95923914063984 | 0 |

C1 est bien la somme économique de 94 parts SPY, 544 parts BIL et du cash résiduel ; aucun rendement n'est créé en dehors des variations de prix et distributions de ces positions.

## 5. Scénarios de coûts préspécifiés

Le coût est une friction théorique unique par achat initial : `notionnel exécuté × pb / 10 000`. Il est intégré au contrôle `H_FIN_NET` avant acceptation. Ce n'est ni un spread observé, ni du slippage, ni une commission historique. Les mêmes taux s'appliquent à toutes les références et aucune autre couche de coût n'est ajoutée.

| Scénario | Référence | Statut | Coût USD | Cash après coût | Richesse terminale nette | Rendement net | Volatilité ann. | Drawdown max. | Δ richesse vs S0 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| S0 | A | exécuté | 0.000000 | 1 172.161377 | 113 448.697710 | 13.448698 % | 19.979958 % | -18.371442 % | 0.000000 |
| S0 | B | exécuté | 0.000000 | 62.473656 | 104 607.451670 | 4.607452 % | 0.222237 % | -0.010683 % | 0.000000 |
| S0 | C1 | exécuté | 0.000000 | 663.202515 | 109 025.959239 | 9.025959 % | 10.022155 % | -9.513834 % | 0.000000 |
| S1 | A | exécuté | 9.882784 | 1 162.278593 | 113 438.814926 | 13.438815 % | 19.981859 % | -18.372988 % | -9.882784 |
| S1 | B | exécuté | 9.993753 | 52.479903 | 104 597.457917 | 4.597458 % | 0.222259 % | -0.010684 % | -9.993753 |
| S1 | C1 | exécuté | 9.933680 | 653.268835 | 109 016.025559 | 9.016026 % | 10.023113 % | -9.514689 % | -9.933680 |
| S2 | A | exécuté | 49.413919 | 1 122.747458 | 113 399.283791 | 13.399284 % | 19.989465 % | -18.379175 % | -49.413919 |
| S2 | B | exécuté | 49.968763 | 12.504893 | 104 557.482907 | 4.557483 % | 0.222346 % | -0.010689 % | -49.968763 |
| S2 | C1 | exécuté | 49.668399 | 613.534116 | 108 976.290840 | 8.976291 % | 10.026948 % | -9.518113 % | -49.668399 |
| S3 | A | exécuté | 98.827839 | 1 073.333538 | 113 349.869871 | 13.349870 % | 19.998981 % | -18.386916 % | -98.827839 |
| S3 | B | **rejeté** | 99.937526 | — | — | — | — | — | — |
| S3 | C1 | exécuté | 99.336797 | 563.865717 | 108 926.622442 | 8.926622 % | 10.031746 % | -9.522397 % | -99.336797 |

Le coût apparaît exactement une fois : la baisse de richesse terminale par rapport à S0 est égale au coût initial non réinvesti. Les quantités, dates, opens, distributions, positions et closes terminaux sont identiques. Les petites variations de volatilité et de drawdown proviennent du retrait d'un montant de cash constant de toute la trajectoire nette, et non d'une nouvelle exposition.

Sur S0–S2, seuls scénarios où les trois références sont comparables, l'ordre descriptif ne change pas : A porte le rendement et le risque les plus élevés, B les plus faibles, C1 reste intermédiaire. S3 ne permet pas de comparaison appariée à trois politiques. Cette expérience à un seul achat ne dit rien sur le coût cumulé d'un rééquilibrage hebdomadaire.

## 6. Parts entières, cash, poids et risques

Les effets économiques restent distincts : les parts entières créent dès S0 un cash non investi de 1 172,16 USD (A), 62,47 USD (B) et 663,20 USD (C1) ; les coûts réduisent ce cash sans modifier les parts. Le poids SPY de C1 dérive ensuite avec les prix et les distributions. Son résultat est la combinaison de 94 SPY, 544 BIL et cash, non une prime automatique de diversification. Les distributions augmentent le cash non rémunéré et ne sont jamais réinvesties.

## 7. Préparation de C1–C2 : état de faisabilité

C2 n'est **pas encore exécutable scientifiquement**. L'infrastructure de base peut être étendue sans refonte, mais les preuves et conventions suivantes manquent :

1. un calendrier de règlement DTC/NSCC exhaustif et versionné pour chaque transaction hebdomadaire de la fenêtre, au-delà de la seule preuve ciblée du 29–30 mai 2024 ;
2. une règle testée imposant qu'une vente ne porte que sur des positions réglées ;
3. la convention exacte de financement `H_FIN_NET` pour un lot atomique vente–achat simultané, avec cash, produits non réglés et frais ;
4. une information point-in-time des distributions : le fichier historique donne ex-date, record date, payment date et montant, mais aucune date d'annonce historique fiable ;
5. une séparation explicite entre le registre comptable rétrospectif et l'état observable par la politique au moment de chaque décision ;
6. le traitement préspécifié d'un gap d'open qui rend le lot figé non finançable ;
7. la conservation des positions héritées après rejet atomique, sans achat partiel ni redimensionnement ;
8. la preuve que les quantités sont figées avant lecture des opens à chaque cycle ;
9. une vérification documentaire complète de toutes les dates de décision, exécution et règlement avant tout calcul ;
10. l'application symétrique de S0–S3 à C1 et C2 lorsqu'un ordre existe, sans facturer un hold.

Le plus petit mécanisme à spécifier — sans l'implémenter ici — est une frontière à deux vues : (a) une comptabilité rétrospective capable d'acquérir et payer les distributions réalisées ; (b) un instantané décisionnel qui n'expose que positions réglées, cash disponible, prix et événements dont `knowledge_at` est prouvé à l'instant de décision. La restriction actuelle de `EX_POST_ACCOUNTING_ONLY` ne doit être levée qu'au profit de cette séparation testée ; sa suppression simple créerait un risque d'information future. Si aucune annonce historique ne peut être documentée, une convention conservatrice devra exclure les créances non payées de l'information et du financement décisionnels jusqu'au paiement, puis être préspécifiée identiquement pour C1 et C2.

## 8. Tests et reproductibilité

Six tests artificiels ciblés ont été ajoutés : séance absente chez un instrument, séance attendue absente chez les deux, distribution manquante ou dupliquée, paiement hors séance commune, réconciliation directe, coût appliqué une seule fois avec dates/parts constantes, et rejet sans redimensionnement (certains contrôles partagent un test). La configuration versionnée fixe S0–S3 et son empreinte SHA-256. Le résultat réel est rejoué deux fois à l'identique.

Les validations finales portent sur la suite complète, Ruff, les invariants du registre, les empreintes du manifeste et la confirmation Git qu'aucun brut ni notebook n'a changé.

## 9. Recommandation

La prochaine étape scientifique minimale est de rédiger puis tester, uniquement sur données artificielles, le contrat temporel de C2 : calendrier hebdomadaire, instant de décision, lot atomique, règlement, financement, rejets hérités, vue point-in-time des distributions et coûts S0–S3. Ensuite seulement, acquérir ou qualifier la couverture documentaire ciblée des dates de règlement et d'information nécessaires à cet unique épisode. Aucun résultat C2 ne doit être calculé avant ces deux preuves.
