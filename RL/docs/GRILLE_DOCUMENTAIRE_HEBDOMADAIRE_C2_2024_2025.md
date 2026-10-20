# Grille documentaire hebdomadaire C2 — 29 mai 2024 au 29 mai 2025

## A. Objet et verdict

Ce travail construit la chronologie documentaire des décisions hebdomadaires candidates C2 sans exécuter C2. Il ne calcule ni position, ni ordre, ni richesse, ni rendement. Le verdict est **`C2_PARTIALLY_DOCUMENTED`** : les 52 couples close–open sont présents et les 52 dates candidates de règlement sont vérifiées, mais aucune décision n'est entièrement prête au sens point-in-time.

## B. Périmètre temporel

L'achat initial du 29 mai 2024 appartient au cycle déjà documenté et n'est pas répété. La première décision récurrente est le lundi 3 juin 2024, fondée sur la dernière close commune de la semaine précédente, le vendredi 31 mai. La dernière décision candidate est le mardi 27 mai 2025, après le Memorial Day; aucune décision n'est créée après la borne terminale du 29 mai 2025.

## C. Convention hebdomadaire

Pour chaque semaine civile postérieure à la semaine d'initialisation :

1. la référence est la dernière séance commune SPY–BIL de la semaine précédente;
2. la décision est horodatée à 08:00 `America/New_York` lors de la première séance commune suivante;
3. l'open du même jour n'est qu'une référence hypothétique rétrospective;
4. le règlement candidat est le premier jour DTC admissible après le trade date sous T+1.

Les horodatages portent leur décalage réel : `-04:00` en heure d'été et `-05:00` en heure standard.

## D. Livrable exhaustif

La grille exhaustive, ligne par ligne, est [grille_documentaire_c2_2024_2025.csv](grille_documentaire_c2_2024_2025.csv). Elle contient 52 décisions candidates et conserve, pour chacune, la close de référence, l'heure de décision, l'open candidat, le règlement, la présence des prix, les événements de distribution pertinents, les dépendances financières conditionnelles, les motifs et les identifiants de sources.

Résumé :

| Élément | Résultat |
|---|---:|
| Décisions candidates | 52 |
| Première / dernière | 2024-06-03 / 2025-05-27 |
| Opens SPY et BIL présents | 52 / 52 |
| Closes SPY et BIL présentes | 52 / 52 |
| Anomalies de prix identifiées dans l'épisode | 0 |
| Règlements `VERIFIED` | 52 |
| `READY_DOCUMENTARY` | 0 |
| `PARTIALLY_DOCUMENTED` | 20 |
| `NOT_EVALUABLE_DOCUMENTARY` | 32 |

Les statuts décisionnels, non exclusifs, comptent 52 `CONDITIONAL_ON_PORTFOLIO_STATE`, 32 `BLOCKED_BY_UNKNOWN_ENTITLEMENT`, 51 `CONDITIONAL_ON_CASH_AVAILABILITY`, zéro `CONDITIONAL_ON_SETTLEMENT` et zéro `NO_DOCUMENTARY_BLOCK_IDENTIFIED`.

## E. Prix de décision et d'ouverture

Les barres Yahoo SPY et BIL existent pour toutes les closes de référence et tous les opens candidats. Leur statut reste **`MARKET_OBSERVABLE_PROXY_NOT_ARCHIVED_PIT`** : le fichier acquis le 19 octobre 2026 ne prouve pas que sa version exacte était disponible à 08:00 le jour de chaque décision. L'open est postérieur à la décision et porte donc le statut **`RETROSPECTIVE_HYPOTHETICAL_PROXY`**, jamais celui d'une information décisionnelle ou d'une exécution garantie.

L'audit de marché déjà versionné n'identifie aucune date d'alerte dans cet épisode. Cela ne transforme pas Yahoo en source point-in-time.

## F. Calendrier de négociation

Les semaines sont dérivées des séances communes observées, sous contrôle des calendriers NYSE 2024 et 2025 déjà audités. Les décalages du lundi férié vers le mardi sont ainsi conservés, notamment le 3 septembre 2024, le 21 janvier 2025, le 18 février 2025 et le 27 mai 2025. La fermeture exceptionnelle du 9 janvier 2025 n'altère aucune première séance hebdomadaire candidate.

## G. Règlement

La règle SEC 15c6-1 impose T+1 à compter du 28 mai 2024. Les Important Notices DTC **19404-23** (calendrier 2024) et **20972-24** (calendrier 2025) distinguent les jours fermés et les jours ouverts sans service de règlement. Aucune des 52 dates T+1 calculées ne tombe un week-end ou un jour sans règlement; elles sont donc toutes `VERIFIED`. Il n'existe ici aucun cas `RULE_BASED_UNVERIFIED`, `CONFLICTING` ou `MISSING`, et aucune ligne n'a besoin de `CONDITIONAL_ON_SETTLEMENT`.

Références primaires : [règle finale SEC 34-96930](https://www.sec.gov/files/rules/final/2023/34-96930.pdf), [DTC 19404-23 — 2024](https://www.dtcc.com/-/media/Files/pdf/2023/12/12/19404-23.pdf), [DTC 20972-24 — 2025](https://www.dtcc.com/Globals/PDFs/2024/October/30/20972-24).

## H. Distributions observées ex post

Le classeur State Street fournit 16 événements officiels réalisés — quatre SPY et douze BIL — avec ex-date, record date, payment date et montant par part :

| Instrument | Ex-date | Record date | Payment date | Montant USD |
|---|---|---|---|---:|
| BIL | 2024-06-03 | 2024-06-03 | 2024-06-06 | 0.405038 |
| SPY | 2024-06-21 | 2024-06-21 | 2024-07-31 | 1.759024 |
| BIL | 2024-07-01 | 2024-07-01 | 2024-07-05 | 0.392200 |
| BIL | 2024-08-01 | 2024-08-01 | 2024-08-06 | 0.402311 |
| BIL | 2024-09-03 | 2024-09-03 | 2024-09-06 | 0.396088 |
| SPY | 2024-09-20 | 2024-09-20 | 2024-10-31 | 1.745531 |
| BIL | 2024-10-01 | 2024-10-01 | 2024-10-04 | 0.371279 |
| BIL | 2024-11-01 | 2024-11-01 | 2024-11-06 | 0.358528 |
| BIL | 2024-12-02 | 2024-12-02 | 2024-12-05 | 0.334568 |
| BIL | 2024-12-19 | 2024-12-19 | 2024-12-24 | 0.382797 |
| SPY | 2024-12-20 | 2024-12-20 | 2025-01-31 | 1.965548 |
| BIL | 2025-02-03 | 2025-02-03 | 2025-02-06 | 0.325824 |
| BIL | 2025-03-03 | 2025-03-03 | 2025-03-06 | 0.289327 |
| SPY | 2025-03-21 | 2025-03-21 | 2025-04-30 | 1.695528 |
| BIL | 2025-04-01 | 2025-04-01 | 2025-04-04 | 0.321379 |
| BIL | 2025-05-01 | 2025-05-01 | 2025-05-06 | 0.311560 |

## I. Connaissance des distributions

Le classeur acquis en 2026 ne contient pas de date d'annonce et ne permet pas de reconstruire ce qui était publié à 08:00 pour chacune des décisions de 2024–2025. Les recherches ciblées n'ont pas produit une archive primaire exhaustive des annonces historiques. Aucun événement n'est donc déclaré connu à la décision sur la seule base de sa réalisation future dans le classeur.

Il n'existe pas non plus de preuve de révision historique : `revision_status = UNKNOWN`, et non « aucune révision ».

## J. Droits conditionnels inconnus

Une décision est `BLOCKED_BY_UNKNOWN_ENTITLEMENT` lorsqu'une ex-date est atteinte mais que la payment date n'est pas passée, car un portefeuille C2 hypothétique pourrait détenir le titre sans que l'annonce historiquement disponible soit prouvée. Cela concerne 32 décisions : un passage pour dix événements BIL et six passages pour chacune des quatre distributions SPY. Cette qualification ne suppose aucune position C2 et ne calcule aucun droit.

Les BIL du 1er octobre 2024 et du 1er avril 2025 ne rencontrent aucune décision entre ex-date et paiement; ils restent néanmoins documentés dans la chronologie exhaustive.

## K. Disponibilité conditionnelle du cash

Une payment date passée prouve la chronologie économique réalisée, pas l'heure de crédit chez un dépositaire ni la disponibilité à 08:00 dans un compte C2 inexistant. Toute décision postérieure à un paiement conserve donc `CONDITIONAL_ON_CASH_AVAILABILITY` lorsque cet événement pourrait affecter l'état hérité. Cette dépendance est conditionnelle au portefeuille; elle ne constitue ni un solde ni un flux C2 reconstruit.

## L. Deux niveaux de préparation

La préparation **exogène** couvre la présence des prix, le calendrier NYSE, T+1 et la chronologie réalisée des distributions. Elle est complète pour les calendriers/règlements candidats, mais seulement partielle pour les prix point-in-time et les annonces.

La préparation **financière conditionnelle** dépend de l'état qu'aurait produit C2 : titres détenus à l'ex-date, droits nés, règlements antérieurs et cash effectivement crédité. Comme cet état n'est pas construit ici, chaque ligne conserve `CONDITIONAL_ON_PORTFOLIO_STATE`, complété selon le cas par `BLOCKED_BY_UNKNOWN_ENTITLEMENT` et/ou `CONDITIONAL_ON_CASH_AVAILABILITY`.

## M. Première rupture et séquence prête

La première décision récurrente, le 3 juin 2024, coïncide avec l'ex-date BIL du 3 juin et précède son paiement du 6 juin. Faute de preuve d'annonce point-in-time, c'est la première rupture documentaire. La longueur de la séquence entièrement prête à partir du début récurrent est donc **zéro**, et aucune des 52 décisions n'est `READY_DOCUMENTARY`.

## N. Reproductibilité et empreintes

Le script [build_c2_documentary_grid.py](../scripts/build_c2_documentary_grid.py) vérifie les empreintes du manifeste, reconstruit les 52 semaines et régénère le CSV. La commande de contrôle est :

```powershell
python RL/scripts/build_c2_documentary_grid.py --check
```

Empreintes SHA-256 des entrées principales :

| Source | SHA-256 |
|---|---|
| Yahoo SPY | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| Yahoo BIL | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| State Street distributions | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| Calendriers NYSE, entrée principale | `2c2e63b780c4a373d8d546904ae46c8ba7e8070ad9357d23d2c92749985bb6c9` |
| Règle SEC T+1 | `e214bf80244fe9107c867d7abeb6a6b969029c519566036e42b081977a9b575a` |
| CSV produit | `d417dee20ba886d28dddcd2c42d2d8e9ebe8b77a30e5dfe00fd70adce1ed311c` |

Les deux avis annuels DTC sont cités par numéro et URL mais ne sont pas ajoutés aux données brutes ni au manifeste dans ce lot. Cette limite de conservation n'affecte pas les 52 dates calculées — toutes sont le jour ouvré civil suivant — mais doit être corrigée avant une prétention de patrimoine documentaire autonome hors ligne.

## O. Limite d'autorisation

Cette grille autorise seulement l'examen documentaire des décisions candidates. Elle n'autorise pas un historique C2, un dimensionnement, un passage d'ordre, une valorisation, une comparaison C1–C2, ni une mesure de performance. Une exécution historique C2 exigerait au minimum une règle explicite pour les annonces non archivées, une preuve de cash disponible à l'heure de décision et l'instanciation contrôlée de l'état hérité.
