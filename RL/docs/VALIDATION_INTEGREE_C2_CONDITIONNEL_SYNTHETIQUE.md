# Validation intégrée C2 conditionnelle synthétique

## 1. Périmètre et conventions approuvées

Cette phase valide exclusivement sur données artificielles le protocole exploratoire conditionnel E-B. Elle n'autorise ni lecture des prix historiques, ni transaction historique, ni résultat C1–C2 empirique.

Les dix conventions approuvées pour ce contrôle sont intégrées :

1. Close et Open sont des références artificielles; l'open reste postérieur au scellement.
2. Le budget C2 est distinct de la richesse économique.
3. Une créance inconnue reste économique mais n'entre ni dans le budget ni dans le financement.
4. Une créance du jour n'est pas ajoutée à un close encore cum-distribution.
5. Le cash payé est disponible à 08:00 à D+1; D+2 est la sensibilité.
6. Comptabilisation économique et capacité de financement restent séparées.
7. Un budget indéterminé donne `NOT_EVALUABLE`; un lot non finançable est rejeté sans redimensionnement.
8. Une défaillance requise bloque le chemin conditionnel au lieu d'être imputée.
9. S0–S3 restent 0, 1, 5 et 10 points de base.
10. Le mode porte explicitement la provenance `EXPLORATORY_CONDITIONAL`.

Le protocole strict S demeure le défaut et son comportement n'a pas été assoupli.

## 2. Modifications minimales

Deux composants existants seulement sont étendus :

- `SyntheticSettlementCalendar.business_date_after()` calcule le premier ou deuxième jour artificiel de règlement après une payment date;
- `SyntheticDecisionAdapter` ajoute les enums `ProtocolMode` et `CashAvailabilityConvention`, les champs conditionnels scellés du snapshot, `build_conditional_decision_snapshot()` et un contrôle de financement E-B avant toute écriture d'open.

Le registre, ses règles de position, `H_FIN_NET`, les distributions, le règlement, l'atomicité et le chemin strict ne sont pas remplacés. Aucun moteur d'événements ni framework de backtest n'est créé.

## 3. Budget décisionnel E-B

À 08:00, avec les dernières closes admissibles :

\[
H_d=\sum_i q_{i,d}P^{close}_{i,d}.
\]

Le cash admissible est :

\[
C_d^{adm}=C_d^{réglé}-C_d^{payé\ mais\ indisponible}.
\]

Les créances connues ne sont ajoutées que si leur ex-date précède la date de décision. Une créance du jour est encore économiquement incorporée au mark cum antérieur et n'est pas ajoutée une seconde fois. Le budget est donc :

\[
B_d=H_d+C_d^{adm}+A_d^{connues,post\text{-}ex}
 +U_d^{vente}-U_d^{achat}.
\]

Les créances inconnues postérieures à leur ex-date sont exclues par somme directe des composantes admissibles. Le code ne calcule jamais `richesse économique − montant inconnu` pour fabriquer le budget.

Les cibles sont exactement :

\[
q^{cible}_{SPY}=\left\lfloor\frac{0.5B_d}{P^{close}_{SPY,d}}\right\rfloor,
\qquad
q^{cible}_{BIL}=\left\lfloor\frac{0.5B_d}{P^{close}_{BIL,d}}\right\rfloor.
\]

Le champ historique `known_market_wealth` de l'intention transporte ce budget sous E-B; `protocol_mode=EXPLORATORY_CONDITIONAL` interdit de l'interpréter comme une richesse exacte à 08:00.

## 4. Richesse économique et financement

À un mark ex-cohérent, la richesse reste :

\[
W_t^{econ}=\sum_i q_{i,t}P_{i,t}+C_t+A_t+U_t^{vente}-U_t^{achat}.
\]

Lorsque le snapshot utilise encore le close cum précédent, la créance du jour est retranchée de l'addition séparée, puisqu'elle est déjà incorporée au mark. Cette valeur porte explicitement `valuation_reference_at`; elle n'est pas qualifiée de richesse de marché exacte à 08:00.

Le financement de base est :

\[
F_d=\max(0,C_d^{adm}-U_d^{achat}).
\]

Lors de l'exécution, `H_FIN_NET` peut compléter ce montant par les ventes du même lot, nettes de frais. Une créance non payée n'est jamais une ressource. Un paiement encore indisponible reste dans la richesse économique, mais pas dans `B_d` ou `F_d`.

## 5. Instantané conditionnel

Le `DecisionSnapshot` immuable conserve séparément :

- `economic_wealth`;
- `decision_budget`;
- identifiants et valeur comptable des créances exclues;
- créances du jour encore incorporées au close cum;
- `unavailable_paid_cash`;
- `financing_cash`;
- `valuation_reference_at`;
- `information_cutoff`;
- `protocol_mode`;
- `cash_availability_convention`.

Le snapshot et l'intention incluent ces conventions pertinentes dans leur contenu canonique SHA-256. Une altération du budget invalide l'empreinte. Toute écriture au registre entre snapshot et open invalide l'intention. L'intention ne publie ni `economic_wealth` ni le montant exclu; son calcul utilise uniquement le budget scellé.

## 6. Ex-date et absence de double comptage

Le cas prioritaire emploie 100 parts, un close cum de 100 USD, un droit de 2 USD et un open ex de 98 USD :

\[
100\times100=10\,000,
\]

\[
100\times98+100\times2=10\,000.
\]

Le snapshot E-B du jour conserve un budget de 10 000 USD aux prix antérieurs et n'ajoute pas le droit de 200 USD. Après l'open, le registre retrouve 10 000 USD avec le prix ex et la créance. Le calcul interdit `100×100+200=10 200`.

Après l'ex-date, un close déjà ex permet d'ajouter séparément une créance connue. Une créance inconnue reste exclue. Deux montants inconnus artificiels différents produisent le même budget, les mêmes cibles et les mêmes ordres, mais des richesses économiques différentes : le montant ne fuit pas dans la politique.

Un second cas ex-date part de closes 120/100, scelle les cibles 458/550 puis observe des opens 118/100. La vente figée de 42 SPY ne finance pas les 50 BIL à acheter : le lot est rejeté sans redimensionnement, et les positions 500/500 ainsi que la créance de 1 000 USD sont conservées.

## 7. Cash D+1 et D+2

La payment date transfère le droit vers le cash économique sans changer la richesse. L'admissibilité est ensuite calculée avec les jours fournis par le calendrier synthétique :

- D+1 : 08:00 le premier jour de règlement ultérieur;
- D+2 : 08:00 le deuxième jour de règlement ultérieur.

Un paiement le vendredi 24 janvier devient disponible le lundi 27 sous D+1 et le mardi 28 sous D+2. Au snapshot du lundi :

| Mesure artificielle | D+1 | D+2 |
|---|---:|---:|
| Richesse économique | 101 000 | 101 000 |
| Budget décisionnel | 101 000 | 100 000 |
| Cash finançable | 1 000 | 0 |
| Cash payé indisponible | 0 | 1 000 |

Un calendrier omettant le lundi 20 janvier confirme que week-end et jour sans règlement sont sautés. Un paiement le jour même reste indisponible à 08:00 sous les deux conventions.

## 8. Séquence C2 intégrée

La séquence déterministe utilise uniquement SPY et BIL artificiels :

| Cycle | Date | État et décision | Résultat |
|---|---|---|---|
| 0 — initialisation | 6 janv. | 100 000 USD, closes 100/100, cible 500/500 | achats 500/500, règlement le 7 |
| 1 — ex-date | 13 janv. | droit SPY 1 000 inconnu, close cum 100, open ex 98 | budget 100 000, hold, richesse à l'open 100 000 |
| 2 — dérive | 21 janv. | positions 500/500, closes 120/100, budget 110 000, richesse 111 000 | vente 42 SPY, achat 50 BIL, `H_FIN_NET`, règlement le 22 |
| 3 — paiement | 27 janv. | positions 458/550, cash D+1 1 040, budget 101 840 | achat 51 SPY, vente 41 BIL, positions 509/509 après règlement |
| 4 — rejet | 3 févr. | cibles figées 466/560, opens 120/200 | lot non finançable, rejet atomique |
| 5 — reprise | 10 févr. | positions héritées 509/509, closes 100/100 | `VOLUNTARY_HOLD` |

Chaque décision repart de l'état transmis. Le rejet ne réinitialise ni positions, ni cash, ni droits, ni obligations. Le lot rejeté n'est pas redimensionné à partir des opens.

## 9. Transactions, règlement et rejet

Au cycle 2, les 42 ventes SPY règlent le même jour que les 50 achats BIL. Le financement net est positif et le registre interdit toute position réglée négative. Au cycle 3, le cash D+1 complète la vente BIL.

Au cycle 4, les opens transforment le lot figé en vente SPY de 5 160 USD contre achat BIL de 10 200 USD. Les 40 USD de cash et la vente ne suffisent pas; l'adaptateur rejette avant mutation des prix ou des positions. Les positions restent 509/509, le cash 40 USD et aucun règlement n'est créé.

Les invariants du registre confirment : cash jamais négatif, aucune vente de titres non réglés, aucune position courte, règlements T+1 fournis et lots atomiques.

## 10. Contrôle synthétique C1–C2

C1 et C2 commencent tous deux avec 100 000 USD, 500 SPY, 500 BIL, les mêmes prix, le même droit SPY de 1 000 USD, les mêmes dates, règles de paiement et marks terminaux.

C1 ne produit aucun trade après le 6 janvier et termine le contrôle avec 500/500 et 1 000 USD de cash. C2 exécute uniquement les rééquilibrages décrits et termine avec 509/509 et 40 USD de cash. Aux marks artificiels 100/100 :

- richesse C1 contrôlée par `500×100 + 500×100 + 1 000 = 101 000`;
- richesse C2 contrôlée par `509×100 + 509×100 + 40 = 101 840`.

Les deux valeurs utilisent la même fonction comptable. Leur différence provient uniquement des transactions et expositions synthétiques. Elle ne constitue aucune conclusion de performance générale.

## 11. Coûts S0–S3

Avec closes 101/101, cibles 495/495 et opens 100/100, le notionnel effectivement négocié vaut 99 000 USD :

| Scénario | Frais artificiels |
|---|---:|
| S0 — 0 pb | 0 |
| S1 — 1 pb | 9,90 |
| S2 — 5 pb | 49,50 |
| S3 — 10 pb | 99,00 |

Dans chaque cas accepté, `richesse après = richesse avant − frais`. Le règlement ne déduit pas les frais une seconde fois. Deux lots S1 cumulent exactement 9,90 puis 0,996 USD; un hold sous S3 ajoute zéro.

Avec closes 100/100, les cibles 500/500 consomment déjà les 100 000 USD. Les 100 USD de frais S3 rendent le lot non finançable : rejet sans réduction des quantités.

## 12. Tests et invariants

La suite contient **169 tests réussis**, dont 18 nouveaux contrôles intégrés E-B. Ils couvrent explicitement :

1. montant inconnu absent des cibles;
2. identité de l'ex-date sans double comptage;
3. séparation richesse, budget et financement;
4. paiement D+1/D+2 et même jour;
5. week-end et jour sans règlement;
6. cash non négatif;
7. positions économiques et réglées;
8. absence de short et de vente non réglée;
9. scellement avant open;
10. refus des intentions altérées ou périmées;
11. paiement sans réinvestissement automatique;
12. absence de trade caché pour C1;
13. transfert créance–cash sans variation artificielle de richesse;
14. conservation d'état après rejet;
15. reproduction exacte de toute la séquence;
16. S0–S3, cumul et absence de double déduction;
17. blocage strict S inchangé face à une créance inconnue.

Les fichiers concernés passent Ruff et les deux registres terminaux passent `assert_invariants()`.

## 13. Préservation du protocole strict

`build_decision_snapshot()` reste le chemin par défaut. Une créance réalisée non annoncée continue de produire `NOT_EVALUABLE`, le cash sans preuve reste exclu et les opens futurs restent interdits. E-B exige un appel distinct, le mode `EXPLORATORY_CONDITIONAL` et D+1 ou D+2.

Les tests stricts antérieurs passent sans modification de leurs attentes. Les grilles historiques, le manifeste et les données brutes ne sont pas modifiés.

## 14. Limites et conditions avant l'historique

Cette preuve porte sur un calendrier, des prix, des distributions et des comptes entièrement artificiels. Elle ne résout pas : version historique exacte de Yahoo, qualité d'exécution de l'open, annonces réelles des distributions, compte dépositaire réel, ni validité empirique du budget partiel.

Le snapshot contient une vue comptable d'audit, mais seul le budget scellé entre dans l'intention. Une future interface de politique devra maintenir cette séparation d'accès et ne jamais exposer le montant économique exclu comme variable décisionnelle.

Avant une expérience historique, il reste à :

1. approuver explicitement l'activation historique E-B;
2. figer D+1 principal et D+2 sensibilité;
3. figer le contrat de sortie et les libellés conditionnels;
4. appliquer l'extension à une copie contrôlée de l'unique épisode sans changer les grilles;
5. effectuer un audit pré-exécution confirmant que seules les sources déjà autorisées seront lues.

## 15. Verdict scientifique

**`SYNTHETIC_CONDITIONAL_C2_VALIDATED`**

Une politique C2 peut enchaîner plusieurs décisions sous E-B avec un budget distinct de la richesse, des droits exacts mais non révélés au dimensionnement, un cash D+1/D+2, `H_FIN_NET`, des coûts, des règlements et des rejets atomiques. Les intentions restent scellées avant les opens et la référence stricte S demeure intacte.

Ce verdict valide uniquement la mécanique synthétique conditionnelle. Il n'autorise aucune phase historique.
