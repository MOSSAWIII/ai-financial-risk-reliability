# Validation de l'adaptateur synthétique de décision SPY–BIL

Date : 20 octobre 2026

Point de départ : `df93520eac058f2fe9e14e0d29ef09cd7b122d6b`

## 1. Conclusion et portée

Le composant [`synthetic_decision_adapter.py`](../scripts/synthetic_decision_adapter.py)
traduit désormais une allocation SPY explicitement fournie en une intention figée,
puis en un lot comptable hypothétique soumis au registre temporel strict. Il ne
choisit aucun poids, ne lit aucune donnée réelle, ne déroule aucune période et ne
recalcule jamais une quantité avec le prix d'ouverture.

Vingt-quatre nouveaux tests entièrement artificiels portent la suite de **45 à 69 tests**.
Ils démontrent la cohérence du mécanisme implémenté sous les conventions candidates,
pas la réalité d'une exécution, d'un compte cash particulier ou d'un prix Yahoo.

Aucun portefeuille historique, backtest, signal, modèle, environnement RL, mesure
de performance ou donnée dérivée n'est produit. Le registre existant n'a pas été
modifié : sa distinction entre positions économiques et positions réglées permet une
restriction de financement plus conservatrice et vérifiable dans l'adaptateur.

## 2. Architecture minimale

L'architecture comporte deux opérations sans boucle de marché :

```text
poids SPY fourni + état et clôtures connus à d
    -> prepare_intent()
    -> quantités cibles entières et ordres figés

intention + opens artificiels datés à e
    -> process_intent()
    -> contrôles documentaires, temporels, titres et financement
    -> execute_batch(..., H_FIN_NET) ou statut de refus
```

L'adaptateur réutilise directement :

- `whole_share_quantity()` pour l'arrondi inférieur en parts entières ;
- `FixedOrder` pour conserver date et prix de décision ;
- `ExecutionRequest` pour prix d'exécution et frais ;
- `execute_batch()` pour l'atomicité, la livraison et le financement ;
- `SyntheticTradingCalendar` et `SyntheticSettlementCalendar` pour les dates ;
- `FundingConvention.H_FIN_NET` pour la projection des flux par échéance.

Il refuse dès sa construction un registre sans `strict_temporal=True` ou sans les
deux calendriers explicites. Il n'existe aucun calendrier implicite ou de secours.

## 3. Contrat des entrées et sorties

### 3.1 Préparation

`prepare_intent()` reçoit :

- une date de décision appartenant au calendrier de négociation ;
- une richesse de marché connue et cohérente avec le registre ;
- les positions héritées SPY/BIL, identiques aux positions économiques du registre ;
- deux clôtures `DatedPrice` disponibles et datées exactement de la décision ;
- un poids cible SPY explicite dans `[0, 1]`.

Il retourne un `DecisionIntent` immuable contenant un identifiant, les entrées, les
quantités cibles et les `FixedOrder` non nuls. La richesse déclarée est confrontée
aux positions valorisées aux clôtures, au cash, aux créances de distribution et de
vente, puis aux dettes d'achat. Une décision antidatée, une séance absente, une
clôture future, un poids invalide ou un état incohérent déclenche `AdapterError`
avant création de l'intention.

### 3.2 Traitement

`process_intent()` reçoit l'intention déjà figée, la première séance négociable
strictement postérieure, deux opens artificiels datés, des frais explicites et, si
nécessaire, un motif documentaire. Il retourne toujours un `ExecutionOutcome` pour
une intention valide, avec :

- l'intention et ses quantités proposées ;
- dates de décision, transaction et règlement ;
- opens et frais admissibles ;
- statut, motif et source de financement ;
- snapshots comptables avant et après ;
- richesses juste avant et après la transaction lorsque calculables ;
- identifiants de règlement en cas d'acceptation.

Une intention devient terminale au premier traitement, y compris après refus. Une
seconde tentative reçoit `INVALID_INPUT` et ne peut créer de deuxième transaction.

## 4. Poids cible, quantités et ordres

Pour `w` fourni, une richesse connue `W_d` et les clôtures connues `P_{i,d}` :

\[
q_{SPY}^{cible}=\left\lfloor\frac{wW_d}{P_{SPY,d}}\right\rfloor,
\qquad
q_{BIL}^{cible}=\left\lfloor\frac{(1-w)W_d}{P_{BIL,d}}\right\rfloor.
\]

Puis :

\[
\Delta q_i=q_i^{cible}-q_i^{hérité}.
\]

Les ordres nuls sont omis. Si les deux deltas sont nuls, le résultat est
`VOLUNTARY_HOLD`, même si un open sans utilité serait indisponible : aucune
transaction ne requiert alors un prix d'exécution ou une date de règlement.

Les tests appliquent la même formule à 10 000, 100 000 et 1 000 000 USD. Ces valeurs
ne sont pas des performances ni une calibration ; elles éprouvent seulement les
effets d'échelle des parts entières.

## 5. Chronologie et absence de look-ahead

Les clôtures doivent porter la date de décision. L'exécution doit porter la première
séance explicite postérieure. `FixedOrder.decision_date < trade_date` est ensuite
revérifié par le registre, et chaque open doit être daté de la trade date.

Un test prépare 100 parts SPY avec un close de 100 USD :

- si l'open vaut 105 USD, l'ordre reste 100 parts et le lot est rejeté faute de
  financement ;
- si l'open vaut 95 USD, l'ordre reste 100 parts et le reliquat demeure en cash.

L'adaptateur ne possède aucune méthode permettant de remplacer le delta après
observation de l'open. Une date de décision égale ou postérieure à l'exécution, une
clôture future, un open mal daté ou une décision rétroactive reçoit une erreur
explicite.

## 6. Financement `H_FIN_NET` limité

Le registre projette le cash à chaque settlement date en agrégeant cash réglé,
créances de vente, dettes d'achat et frais. Il refuse dès qu'un solde projeté devient
négatif. Les mêmes créances ne peuvent donc financer plusieurs dettes dont la somme
les dépasse, et une vente réglée après un achat ne peut financer l'échéance plus
précoce.

L'adaptateur ajoute trois restrictions :

1. toute quantité vendue doit être disponible dans `settled_positions` au trade
   date, pas seulement dans `economic_positions` ;
2. toutes les jambes du lot passent par la settlement date commune calculée par le
   calendrier strict ;
3. le lot entier est transmis atomiquement avec ses frais à `H_FIN_NET`.

La source de financement rapportée distingue :

- `SETTLED_CASH` si le cash réglé net des dettes existantes couvre les achats ;
- `UNSETTLED_SALE_PROCEEDS` si le lot n'est finançable qu'avec ses ventes ;
- `NONE` s'il n'existe aucun achat.

Cette étiquette explique le mécanisme accepté ; elle n'ajoute ni pouvoir d'achat ni
nouveau compte au registre.

## 7. Titres intégralement payés et revente prématurée

Le registre ne conserve pas de lots fiscaux ni une provenance contractuelle part par
part. Une extension prétendant reconstituer cette provenance aurait donc été
artificielle. La règle retenue est volontairement plus restrictive :

> seules les parts déjà présentes dans `settled_positions` peuvent être vendues.

Dans ce modèle, une acquisition ne rejoint `settled_positions` qu'au règlement de
sa dette simultanément au débit du cash, et le règlement est refusé s'il créerait un
cash négatif. Une position réglée est donc la meilleure preuve disponible de
livraison et de paiement intégral dans le périmètre du registre.

Un achat financé par une vente non réglée apparaît immédiatement dans
`economic_positions`, mais pas dans `settled_positions`. Toute tentative de revente
avant son règlement est refusée `ECONOMIC_ORDER_REJECTED`. Après règlement, les
parts deviennent vendables. Pour un symbole comprenant à la fois des parts anciennes
réglées et des parts nouvelles en attente, seules les anciennes quantités réglées
peuvent être vendues : cette règle est conservatrice et ne revendique pas une
affectation réelle des lots par le courtier.

## 8. Statuts et atomicité

| Statut | Sens implémenté |
|---|---|
| `EXECUTED_HYPOTHETICAL` | documents et contraintes satisfaits ; lot comptabilisé aux opens artificiels |
| `VOLUNTARY_HOLD` | la cible reproduit les quantités héritées ; aucun ordre non nul |
| `ECONOMIC_ORDER_REJECTED` | transaction demandée mais titres ou financement insuffisants |
| `NOT_EVALUABLE` | prix manquant/contesté, calendrier insuffisant ou défaut documentaire explicite |
| `INVALID_INPUT` | chronologie, date, frais, double traitement ou autre contrat logiciel invalide |

Les défauts documentaires sont détectés avant toute marque de prix ou mutation
financière. Pour un rejet économique évalué à l'open, les prix de marché peuvent
changer : cette variation de valorisation est enregistrée séparément. En revanche,
cash, positions, créances, dettes, frais et règlements sont identiques juste avant et
juste après la tentative. Les tests comparent explicitement ces snapshots.

Un lot invalide n'est jamais réduit, reporté ou transformé en hold. Le statut et le
motif restent dans `ExecutionOutcome`; le registre conserve en plus son propre
journal de rejet lorsque `execute_batch()` a été atteint.

## 9. Scénarios artificiels vérifiés

Les **24 nouveaux tests** couvrent :

1. refus d'un registre non strict ;
2. quantités entières pour 10 000, 100 000 et 1 000 000 USD ;
3. clôture future et richesse incohérente ;
4. décision hors séance ou rétroactive ;
5. gap défavorable sans redimensionnement et rejet atomique ;
6. gap favorable sans augmentation de quantité ;
7. décision antérieure obligatoire et interdiction de sauter la prochaine séance ;
8. open mal daté refusé avant mutation ;
9. calendrier de règlement insuffisant classé non évaluable ;
10. rééquilibrage BIL vers SPY financé par une vente à même échéance ;
11. refus de vendre une position économique non réglée ;
12. refus de revendre un achat financé par une vente avant son paiement ;
13. frais rendant un lot déficitaire ;
14. frais acceptés déduits exactement une fois ;
15. vente réglée trop tard pour financer un achat ;
16. impossibilité de réutiliser un même produit de vente au-delà du total disponible ;
17. open manquant ou contesté avant mutation ;
18. distinction entre hold volontaire et rejet ;
19. interdiction d'exécuter deux fois la même intention ;
20. défaut documentaire avant mutation.

Les cas paramétrés expliquent pourquoi cette liste logique correspond à vingt-quatre tests
Pytest. Les 45 tests du registre restent inchangés et passent avec les nouveaux.

## 10. Invariants effectivement vérifiés

Après transaction :

\[
W_t^M=\sum_i n_{i,t}P_{i,t}+C_t+A_t+U_t^{vente}-U_t^{achat}.
\]

Les tests démontrent sur les états intermédiaires que :

- un rééquilibrage sans frais au prix de valorisation conserve la richesse ;
- les frais diminuent la richesse exactement une fois ;
- le règlement transfère titres et cash sans gain supplémentaire ;
- cash, positions économiques et positions réglées restent non négatifs ;
- les ventes n'excèdent pas les parts réglées ;
- le cash projeté reste non négatif à chaque échéance ;
- un rejet ne change aucun solde financier ;
- un défaut documentaire ne change ni prix, ni journal, ni solde ;
- une exécution acceptée conserve l'identité entre position économique, position
  réglée et quantités en règlement.

## 11. Validité scientifique et limites

| Dimension | Ce qui est démontré | Ce qui ne l'est pas |
|---|---|---|
| validité comptable | conservation, frais, comptes de règlement et atomicité sur cas artificiels | rapprochement avec un relevé de courtier |
| validité temporelle | clôtures à la décision, quantités figées, opens datés et calendriers stricts | disponibilité historique réelle de chaque information |
| cohérence du financement | restrictions explicites de `H_FIN_NET`, titres réglés et cash par échéance | acceptation contractuelle par un courtier ou netting juridique réel |
| réalisme de marché | aucun | fill à Yahoo `Open`, spread, slippage, impact ou fills partiels |
| validité expérimentale | aucun résultat de stratégie n'est produit | performance historique, causalité, robustesse ou utilité d'une politique |

La contrainte `settled_positions` est une politique de recherche conservatrice. Elle
ne suit pas la provenance exacte du financement après règlement et ne remplace pas
les règles d'un compte réel. Les calendriers, prix et frais des tests sont fictifs.

L'adaptateur maintient l'intention terminale en mémoire. Une implémentation historique
persistante devrait stocker les identifiants et résultats hors processus pour rendre
l'idempotence durable après redémarrage ; cette infrastructure n'est ni nécessaire
ni autorisée ici.

## 12. Conditions avant une intégration historique

La plus petite étape suivante, soumise à autorisation, serait de spécifier une
frontière d'ingestion sans encore exécuter de stratégie. Elle devrait :

1. figer les choix encore proposés dans le mandat v1 ;
2. fournir des calendriers de négociation et règlement versionnés pour les seules
   dates requises ;
3. fournir clôtures, opens, distributions et opérations sur titres avec provenance,
   empreintes, anomalies et disponibilité point-in-time ;
4. bloquer notamment l'open SPY contesté du 20 avril 2026 ;
5. préspécifier les couches de coûts sans les calibrer sur les résultats ;
6. persister les identifiants d'intention et les statuts ;
7. rejouer d'abord les mêmes contrôles sur un petit fixture artificiel sérialisé ;
8. interdire l'historique tant qu'une date, un événement ou une convention manque.

Cette validation autorise seulement à considérer le mécanisme synthétique comme
cohérent dans son périmètre. Elle n'autorise aucune ingestion, simulation, politique
d'allocation, comparaison ou expérience historique.
