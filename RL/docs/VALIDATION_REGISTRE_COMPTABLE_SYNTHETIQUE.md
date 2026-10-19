# Validation du registre comptable synthétique SPY–BIL

Date : 19 octobre 2026  
Point de départ : `66b18ca39e8ce1d6b9758188ff154af6fbf565c2`

## 1. Verdict

Le module [`synthetic_portfolio_ledger.py`](../scripts/synthetic_portfolio_ledger.py) satisfait les invariants retenus sur **29 tests utilisant exclusivement des données artificielles**. Il représente des transactions, règlements, créances de distribution et regroupements de parts sans création mécanique de richesse ni financement implicite.

Le composant est suffisamment fiable pour servir de socle à une prochaine validation comptable, mais il n'est pas un simulateur de marché, un backtest ou la représentation d'un compte de courtage réel. Les conventions de financement et le calendrier des tests sont illustratifs. Aucune donnée historique, aucun fichier du manifeste et aucun accès réseau ne sont utilisés.

## 2. Périmètre logiciel

Le registre accepte uniquement des entrées explicites : cash initial, symboles, dates, prix, NAV facultatives, quantités entières, frais artificiels, calendrier artificiel et événements comptables. Il ne recherche pas de prix, ne calcule pas de poids cible, ne choisit aucun ordre et ne produit aucune décision.

Les trois éléments nouveaux sont :

- `RL/scripts/synthetic_portfolio_ledger.py` : composant comptable autonome fondé sur la bibliothèque standard Python ;
- `RL/tests/test_synthetic_portfolio_ledger.py` : scénarios numériques artificiels sous `pytest` ;
- le présent rapport.

Les scripts de reconstruction SPY-B/BIL-B, les notebooks, les données et le manifeste ne sont pas modifiés.

## 3. États comptables

### 3.1 Niveau instrument

Pour chaque symbole, le registre suit :

- la position économique, modifiée au trade date ;
- la position réglée, modifiée seulement au settlement date ;
- le prix de marché artificiel courant ;
- la NAV artificielle courante lorsqu'elle est fournie ;
- les transactions en cours de règlement ;
- les créances de distributions acquises ;
- les regroupements déjà appliqués.

La relation structurelle est :

\[
n_i^{économique}
=n_i^{réglé}
+\sum_{j\in règlements\ en\ attente}q_{i,j},
\]

où une quantité d'achat est positive et une quantité de vente négative.

### 3.2 Niveau compte

Le compte suit séparément :

- le cash réglé ;
- les produits de vente à recevoir ;
- les achats à payer ;
- les créances de distribution ;
- les frais reconnus ;
- les dates de transaction et de règlement ;
- le journal des événements acceptés ;
- un journal distinct des refus.

Le cumul des frais est informatif : il n'est pas soustrait une seconde fois de la richesse. Pour un achat, le frais est inclus dans la dette; pour une vente, il réduit la créance.

## 4. Identités de richesse

La richesse de marché calculée est :

\[
W_t^M=
\sum_i n_{i,t}^{économique}P_{i,t}
+C_t+A_t+U_t^{vente}-U_t^{achat}.
\]

La richesse à la NAV remplace seulement `P` par une NAV artificielle `N` :

\[
W_t^{NAV}=
\sum_i n_{i,t}^{économique}N_{i,t}
+C_t+A_t+U_t^{vente}-U_t^{achat}.
\]

Ces deux mesures partagent donc les mêmes comptes monétaires et peuvent différer uniquement par la base de valorisation des positions.

Les tests démontrent :

- achat ou vente sans frais au prix de valorisation : `ΔW=0` ;
- transaction avec frais : `ΔW=−frais`, une seule fois ;
- règlement : `ΔW=0` ;
- paiement d'une créance de distribution : `ΔW=0` ;
- regroupement de parts : `ΔW=0` ;
- variation artificielle du prix : `ΔW=n×ΔP` ;
- opération refusée : état comptable inchangé.

## 5. Chronologie décision–ordre–transaction

`whole_share_quantity()` calcule une quantité entière par arrondi inférieur à partir d'un notionnel et d'un prix de décision fournis. Un `FixedOrder` conserve cette quantité, sa date de décision et son prix de dimensionnement.

Une `ExecutionRequest` fournit ensuite un prix d'exécution distinct. Le registre impose :

1. date de décision strictement antérieure au trade date ;
2. quantité entière, signée et non nulle ;
3. prix de décision et d'exécution strictement positifs ;
4. prix d'exécution égal au prix de marché enregistré pour le même instant comptable ;
5. settlement date postérieure au trade date.

Le changement entre prix de décision et prix d'ouverture n'altère jamais la quantité. Si la hausse rend l'achat non finançable, le lot est refusé et n'est pas réduit silencieusement.

## 6. Transactions et atomicité

`execute_batch()` valide toutes les jambes avant de modifier le registre. Après acceptation :

- les positions économiques changent immédiatement ;
- le cash réglé ne change pas ;
- un achat crée une dette égale à `prix × quantité + frais` ;
- une vente crée une créance égale à `prix × quantité − frais` ;
- les positions réglées restent inchangées jusqu'au dénouement.

Un lot est intégralement refusé en cas de quantité nulle ou fractionnaire, prix invalide, vente excessive, cash insuffisant, date incohérente, financement futur négatif ou livraison de titres impossible. Le snapshot comptable reste identique. Le refus apparaît uniquement dans le journal d'audit des rejets, ce qui rend l'échec traçable sans laisser de mutation financière partielle.

Le contrôle long-only s'applique à la position économique et à chaque date future de règlement. Une vente de titres achetés mais livrés plus tard est refusée si sa propre livraison interviendrait avant celle de l'achat.

## 7. Règlement et calendrier artificiel

`SyntheticSettlementCalendar` reçoit la liste exhaustive des dates ouvrées du scénario. Il n'invente ni week-end ni jour férié et refuse un calendrier trop court. Depuis le durcissement temporel ultérieur, la trade date peut être une séance de négociation absente du calendrier de règlement; seules les dates admissibles strictement postérieures sont comptées.

La règle codée est :

- T+2 pour une trade date strictement antérieure au 28 mai 2024 ;
- T+1 à partir du 28 mai 2024.

Le nombre de jours est compté dans les dates fournies, non en jours calendaires. Les tests couvrent :

- un trade du 24 mai 2024 réglé le 29 mai dans un calendrier où le 27 est absent ;
- un trade du 28 mai 2024 réglé le 29 mai ;
- un vendredi T+2 avec week-end et jour férié artificiel, réglé le mercredi suivant.

`settle_through()` groupe les flux par date, compense les créances et dettes du groupe, met à jour cash et positions réglées, puis éteint les comptes en attente. Toutes les échéances demandées sont prévalidées avant mutation, afin que le règlement soit atomique.

Ce calendrier démontre le calcul logiciel des cycles; il ne valide aucun calendrier historique réel.

## 8. Conventions de financement

### 8.1 Convention conservatrice

Les achats en attente, y compris ceux d'opérations antérieures, sont réservés sur le cash réglé courant. Les créances de vente non réglées ne financent pas un nouvel achat. Si la somme des dettes dépasse le cash réglé, le lot est refusé.

Cette convention est volontairement restrictive. Elle ne prétend pas reproduire tous les comptes cash ou toutes les politiques de courtier.

### 8.2 Hypothèse `H-FIN-NET`

Le registre projette le cash par date de règlement en ajoutant les créances de vente et en retranchant les achats à payer. Le solde ne peut devenir négatif à aucune échéance. Une vente BIL et un achat SPY de même montant et même settlement date peuvent donc se compenser.

Le test comparatif part d'une position BIL entièrement réglée et d'un cash nul :

- la vente de 10 BIL à 10 et l'achat de 5 SPY à 20 sont refusés sous la convention conservatrice ;
- le même lot est accepté sous `H-FIN-NET`, crée simultanément 100 à recevoir et 100 à payer, puis se règle sans variation de richesse.

`H-FIN-NET` est une hypothèse comptable nommée, non une règle universelle ni une autorisation contractuelle de courtier.

## 9. Distributions

La convention temporelle est explicite : le droit à une distribution datée `d` est calculé sur la position économique au **début de l'ex-date**, avant tout événement portant cette même date. Un achat au trade date `d` ne reçoit donc pas rétroactivement le droit.

À l'ex-date :

\[
A_{nouveau}=n_{début\ de\ jour}\times distribution\ par\ part.
\]

Le cash ne change pas. À la payment date, la créance est transférée au cash et la richesse reste constante. Une vente postérieure à l'ex-date n'annule pas le droit acquis. Les créances simultanées restent individualisées; une distribution nulle crée un événement à montant nul; une créance non arrivée à échéance reste ouverte.

Le registre ne réinvestit jamais automatiquement une distribution. Un achat ultérieur exige une nouvelle transaction à un prix de marché fourni.

## 10. Regroupement de parts

`apply_reverse_split()` traite un ratio entier `anciennes:nouvelles`. Pour deux anciennes parts contre une nouvelle :

- les positions économiques et réglées sont divisées par deux ;
- prix de marché et NAV sont multipliés par deux ;
- la valeur des titres est conservée ;
- les créances monétaires déjà acquises ne changent pas.

Le registre refuse un ratio invalide, une part fractionnaire résultante, un événement avec titres en règlement ou la seconde application du même regroupement. Le scénario utilise 20 parts artificielles à 10, devenant 10 parts à 20; aucune donnée BIL de 2017 n'est importée.

## 11. Résultats des tests

Commande exécutée :

```text
python -m pytest RL/tests/test_synthetic_portfolio_ledger.py -q
```

Résultat :

```text
29 passed
```

| Risque contrôlé | Preuve synthétique |
|---|---|
| achat et vente simples | positions économiques/réglées et comptes intermédiaires vérifiés |
| rééquilibrage SPY–BIL | lot simultané sous `H-FIN-NET` et comparaison conservatrice |
| hausse close–open | quantité figée; achat devenu trop cher refusé |
| financement insuffisant | refus sans modification comptable |
| plusieurs transactions | deux instruments et obligations agrégées |
| zéro, fraction, prix négatif | refus explicites |
| vente excessive | aucune position négative |
| livraison de titres | vente réglée trop tôt refusée |
| T+2/T+1 | transition et dates artificielles vérifiées |
| week-end/jour férié | saut selon liste ouvrée explicite |
| distribution | acquisition, paiement, vente post-ex-date, achat à l'ex-date |
| créances multiples | paiement partiel par échéance, zéro et impayé final |
| regroupement | quantité/prix/valeur et créance conservés; double application refusée |
| frais | baisse de richesse exactement égale au frais |
| prix | variation de richesse égale à la position multipliée par le mouvement |
| absence de données réelles | aucune lecture de fichier ou réseau; test de garde dédié |

## 12. Limites et hypothèses non approuvées

Le composant ne représente pas :

- l'acceptation, le routage, la priorité ou le fill d'un ordre réel ;
- un calendrier de marché ou de règlement historique validé ;
- les pratiques contractuelles d'un courtier ;
- les quotes, spreads, slippage, impact ou fills partiels ;
- les fractions de parts, lots fiscaux, fiscalité, marge, intérêts ou prêt de titres ;
- les opérations sur titres autres que le regroupement entier testé ;
- une stratégie, un portefeuille historique, une performance ou une politique RL.

La règle d'entitlement au début de l'ex-date, les parts entières, la convention conservatrice et `H-FIN-NET` sont des conventions synthétiques explicites. Elles ne sont pas des décisions scientifiques définitives sur le futur mandat.

## 13. Conditions avant toute donnée historique

Avant d'appliquer ce registre à une série réelle, il faudrait au minimum :

1. approuver le mandat, la richesse initiale et la convention de financement ;
2. valider le calendrier historique des trades et règlements ;
3. qualifier le prix d'exécution de référence et ses anomalies ;
4. documenter les règles du compte ou courtier représenté ;
5. étendre les opérations sur titres uniquement lorsque des événements réels l'exigent ;
6. choisir et documenter les coûts sans les calibrer silencieusement ;
7. définir les contrôles de rapprochement avec une référence indépendante ;
8. conserver la distinction entre test comptable, simulation hypothétique et exécution réelle.

## 14. Règle d'arrêt

Cette phase démontre uniquement la cohérence d'un registre sur cas artificiels. Elle n'autorise aucune ingestion de prix historiques, trajectoire d'allocation, simulation de portefeuille, stratégie, calibration, optimisation ou expérience RL. La prochaine phase nécessite une autorisation explicite.
