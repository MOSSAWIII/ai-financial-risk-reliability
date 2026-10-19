# Validation temporelle du registre SPY–BIL

Date : 19 octobre 2026
Point de départ : `794b47292f3915226eefa193d6edecea5281df72`

## 1. Verdict et frontière

Le registre possède désormais un **mode temporel strict** qui rejette les dates
antidatées, impose un ordre journalier, sépare annonce et acquisition d'un droit,
et calcule obligatoirement le règlement depuis un calendrier fourni. Les 29 tests
antérieurs sont conservés et 16 tests adversariaux portent le total à **45 tests**.

Cette validation reste double et séparée :

- les tests comptables emploient uniquement des prix, quantités, événements et
  calendriers artificiels ;
- l'audit documentaire compare seulement des dates officielles ou dérivées de
  règles officielles aux 2 210 dates communes Yahoo SPY–BIL.

Aucun portefeuille historique, rendement de portefeuille, backtest, signal,
allocation, modèle ou algorithme RL n'est produit. Les OHLCV/NAV existants ne sont
ni modifiés ni complétés.

## 2. Défauts réellement présents avant correction

Le code précédent présentait cinq voies d'incohérence :

1. `execute_batch()` acceptait n'importe quelle `settlement_date` postérieure à
   la trade date sans la confronter à `SyntheticSettlementCalendar` ;
2. `set_prices()` acceptait une date facultative et pouvait antidater un prix ;
3. `accrue_distribution()` reconstruisait `shares_before(ex_date)` même si des
   états plus récents avaient déjà été traités ;
4. `settle_through()` et `pay_distributions_through()` retournaient silencieusement
   une liste vide lors d'une tentative prématurée, répétée ou sans échéance ;
5. il n'existait ni horloge comptable globale, ni ordre explicite entre plusieurs
   événements de même date, ni distinction logicielle entre calendrier de marché
   et calendrier de règlement.

Le contrôle local du regroupement empêchait certains splits antidatés pour un
symbole, mais ne protégeait pas la chronologie globale des prix, règlements et
distributions.

## 3. Corrections logicielles

Le constructeur accepte `strict_temporal=True` avec deux objets obligatoires :

- `SyntheticTradingCalendar`, qui contient les séances négociables et marque les
  séances écourtées ;
- `SyntheticSettlementCalendar`, qui contient les jours admissibles au règlement.

En mode strict :

- une trade date doit appartenir au calendrier de négociation ;
- le prix d'exécution doit avoir été observé et daté de cette trade date ;
- le calendrier de règlement calcule T+2 avant le 28 mai 2024 et T+1 à partir de
  cette date ;
- une date explicite encore transmise n'est acceptée que si elle égale le résultat
  du calendrier ;
- une séance de marché peut être absente du calendrier de règlement ; le calcul
  compte alors les prochaines dates de règlement strictement postérieures ;
- tout effet antérieur à la dernière date comptabilisée est rejeté ;
- une échéance antérieure non traitée bloque l'avancement ;
- règlement et paiement stricts portent exactement sur leur date, et une tentative
  prématurée ou double déclenche une exception traçable.

L'ancienne interface reste disponible hors mode strict pour préserver les 29 cas
historiques. Elle est explicitement une interface de compatibilité et n'est pas
admissible pour une future intégration aux dates réelles.

## 4. Connaissance, date économique et comptabilisation

`announce_distribution()` enregistre la connaissance de l'événement avec :

- `knowledge_date` : date à laquelle l'information est introduite ;
- `ex_date` : date économique d'acquisition du droit ;
- `payment_date` : date future de transfert de la créance vers le cash.

L'annonce ne crée ni créance ni richesse. `accrue_announced_distribution()` ne
peut créer le droit qu'exactement à l'ex-date annoncée. Une annonce introduite
après une ex-date déjà clôturée, un second accrual, un paiement avant acquisition
ou un second paiement sont rejetés.

Ainsi, une annonce future est permise sans anticiper son effet comptable, tandis
qu'une distribution rétroactive ne peut plus réécrire un état finalisé.

## 5. Ordre conventionnel le même jour

En l'absence d'horodatages intrajournaliers, le registre adopte l'ordre suivant :

1. regroupement de parts, avant ouverture ;
2. acquisition des droits de distribution sur la position économique de début de
   journée ;
3. règlement des opérations antérieures ;
4. paiement des distributions déjà acquises ;
5. observation du prix ;
6. nouvelles transactions.

Un événement de phase antérieure ne peut être ajouté après une phase ultérieure
de la même date. Un achat à l'ex-date ne reçoit donc pas le droit, une vente après
l'acquisition ne supprime pas la créance, et un paiement traité avant le trade peut
être disponible selon la convention de financement. Cette règle est une convention
journalière reproductible, pas la reconstruction d'un ordre réel intrajournalier.

## 6. Calendrier de négociation et calendrier de règlement

Le calendrier de négociation répond à la question « l'instrument peut-il être
négocié ce jour ? ». Il comprend les fermetures générales et conserve les séances
écourtées comme séances négociables.

Le calendrier de règlement répond à la question « ce jour peut-il compter dans le
délai de dénouement ? ». Il dépend des infrastructures de compensation, de dépôt et
de paiement. Il ne doit pas être copié mécaniquement depuis le calendrier NYSE.

Les calendriers annuels NYSE 2022–2025 indiquent eux-mêmes des jours bancaires où
NYSE reste ouvert et précisent que certaines fermetures DTCC ne comptent pas pour
les dates concernées. Les avis NSCC anticipés 2025 et 2026 montrent en outre que le
statut NSCC peut être « open » avec des restrictions de service ; ce statut ne
suffit donc pas, seul, à prouver qu'un règlement donné est admissible.

## 7. Sources primaires et couverture 2018–2026

### Sources acquises localement

Huit PDF officiels sont inscrits au manifeste, avec taille et SHA-256, puis copiés
sur `D:\ai-financial-risk-reliability-data-backup\2026-10-19\data\raw\rl_calendars` :

- calendriers annuels [NYSE 2022](https://www.nyse.com/publicdocs/ICE_NYSE_2022_Yearly_Trading_Calendar.pdf),
  [2023](https://www.nyse.com/publicdocs/ICE_NYSE_2023_Yearly_Trading_Calendar.pdf),
  [2024](https://www.nyse.com/publicdocs/ICE_NYSE_2024_Yearly_Trading_Calendar.pdf)
  et [2025](https://www.nyse.com/publicdocs/ICE_NYSE_2025_Yearly_Trading_Calendar.pdf) ;
- mémos NYSE Arca des fermetures exceptionnelles du 5 décembre 2018 et du
  [9 janvier 2025](https://www.nyse.com/publicdocs/nyse/markets/arca-options/rule-interpretations/2025/National_Day_of_Mourning_20250102.pdf) ;
- [règle finale SEC T+1](https://www.sec.gov/files/rules/final/2023/34-96930.pdf),
  publiée en 2023 et applicable le 28 mai 2024 ;
- [avis SEC/NYSE Arca sur Juneteenth](https://www.sec.gov/files/rules/sro/nysearca/2021/34-93186.pdf),
  qui documente son ajout à partir de 2022.

Les copies brutes restent exclues de GitHub. Le manifeste indique leur nature,
couverture, limites et conditions de réutilisation. La comparaison des huit copies
de sauvegarde donne **0 discordance SHA-256**.

### Sources vérifiées sans acquisition locale

- la [page NYSE des horaires et jours fériés 2026–2028](https://www.nyse.com/trade/hours-calendars)
  documente pour 2026 les fermetures, les clôtures à 13 h et les horaires réguliers
  de NYSE Arca ;
- la [SEC](https://www.sec.gov/newsroom/press-releases/2017-163) confirme que T+2
  était effectif depuis le 5 septembre 2017 ;
- les avis officiels NSCC « Anticipated Holiday Schedule » 2025 et 2026 ont été
  consultés dans l'index DTCC. Leurs liens PDF ont ensuite répondu 404 lors de
  l'acquisition locale ; ils ne sont donc pas déclarés acquis.

### Concordance des dates

`RL/scripts/audit_historical_calendars.py` construit une grille de séances à partir
des règles de jours fériés, de l'introduction non rétroactive de Juneteenth, des deux
fermetures exceptionnelles et de l'exception de fin d'exercice du 31 décembre 2021.
Sur la fenêtre du 2 janvier 2018 au 16 octobre 2026 :

- calendrier NYSE dérivé : **2 210 séances** ;
- intersection Yahoo SPY–BIL déjà auditée : **2 210 séances** ;
- absences dans Yahoo : **0** ;
- dates Yahoo inattendues : **0** ;
- neuf séances écourtées officiellement vérifiées entre 2022 et la fin de la
  fenêtre : toutes sont présentes dans Yahoo.

Cette égalité ne transforme pas Yahoo en source officielle et ne prouve pas les
prix, horaires effectifs ou exécutions.

### Lacunes documentaires

La couverture officielle n'est **pas déclarée exhaustive** :

- aucun calendrier annuel NYSE archivé 2018–2021 n'a été acquis ; ces années sont
  contrôlées par les règles publiées et la concordance des dates, sans preuve
  annuelle complète des séances écourtées ;
- 2026 est couvert par la page NYSE courante, non par un millésime PDF figé ;
- aucun jeu officiel unique et exhaustif des jours admissibles au règlement
  DTC/NSCC n'a été constitué pour 2018–2026 ;
- les restrictions propres à chaque service DTCC, les ouvertures retardées et les
  interruptions propres à un titre ne sont pas assimilées à des fermetures générales.

Le calendrier de règlement d'une future expérience devra donc être fourni comme
jeu versionné et approuvé, et non inféré de la seule concordance NYSE/Yahoo.

## 8. Financement et atomicité

`CONSERVATIVE_SETTLED_CASH` réserve toutes les dettes d'achat en attente sur le
cash réglé. Une vente non réglée ne finance pas un achat. Un paiement de distribution
n'est utilisable qu'après la phase de paiement.

`H_FIN_NET` projette le cash par échéance et n'autorise la compensation que pour
les flux compatibles à leur date. Le cash projeté ne peut être négatif à aucune
échéance. Cette hypothèse reste non approuvée contractuellement.

Les tests couvrent les achats successifs, la réservation des dettes, une vente
réglée trop tard, les flux de même échéance, plusieurs échéances, le paiement avant
un achat, le gap de prix qui rend un ordre figé non finançable, les titres non
livrables et les lots multi-instruments. Un refus peut ajouter une trace dans le
journal des rejets, mais ne change aucun solde financier, position, créance ou dette.

## 9. Tests adversariaux et invariants

Commande :

```text
python -m pytest RL/tests/test_synthetic_portfolio_ledger.py -q
```

Résultat : `45 passed`.

Les nouveaux cas vérifient notamment : calendriers distincts obligatoires, date de
règlement dérivée, désaccord explicite refusé, transition T+2/T+1, séance négociable
non admissible au règlement, séance écourtée, calendriers incomplets, prix antidaté,
annonce future sans effet, déclaration tardive, paiement prématuré/double, règlement
prématuré/double, split avant droit le même jour, ordre intrajournalier et
compensation `H_FIN_NET`.

Les assertions portent sur cash, positions économiques et réglées, créances,
dettes, compteurs et richesse. Elles confirment :

\[
W_t^M=\sum_i n_{i,t}P_{i,t}+C_t+A_t+U_t^{vente}-U_t^{achat}.
\]

- trade sans frais au prix de valorisation : richesse inchangée ;
- frais : diminution exactement égale au frais ;
- règlement et paiement d'une créance : transferts neutres ;
- split : changement d'unités neutre ;
- variation de prix : effet égal à la position économique multipliée par le
  mouvement ;
- refus : comptes financiers inchangés ;
- long-only et absence d'emprunt implicite : maintenus.

## 10. Décisions encore ouvertes

Le composant est suffisamment durci pour envisager une **intégration contrôlée**,
mais cette intégration n'est pas autorisée par le présent travail. Avant une première
expérience historique, il reste à approuver :

1. un calendrier de règlement DTC/NSCC exhaustif, versionné et propre au service ;
2. la convention contractuelle de compte : cash conservateur ou compensation nette ;
3. le traitement des journées NSCC ouvertes avec restrictions et des accords de
   règlement dérogatoires permis par Rule 15c6-1 ;
4. la convention d'exécution à l'ouverture et le cas SPY du 20 avril 2026 ;
5. les coûts, fiscalité, traitement des fractions et politique des corporate actions ;
6. la règle d'arrêt ou de non-représentabilité lorsqu'une preuve calendaire manque.

La réussite des 45 tests ne vaut ni validation de courtier, ni validation historique
de l'exécution, ni autorisation de lancer un portefeuille.
