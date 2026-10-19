# Protocole d'exécution financière hypothétique SPY–BIL — v1

Date de l'analyse : 19 octobre 2026  
Point de départ Git : `5e2cc9635179ba7beda4200ef48f1325d08a2b96`

## 1. Verdict et portée

Le protocole v1 peut servir de **spécification pour une future comptabilité synthétique**, mais il n'est pas validé comme reconstruction d'exécutions réelles. Sa convention candidate est une décision hebdomadaire après la dernière clôture réellement observée, un dimensionnement en parts entières à partir d'informations disponibles à cette clôture, puis une valorisation hypothétique des transactions au champ Yahoo `Open` de la prochaine séance commune admissible.

Ce champ est un **prix d'ouverture quotidien de référence**. Il n'est ni un fill observé du portefeuille, ni un prix garanti, ni un prix d'enchère NYSE Arca démontré. Yahoo documente les historiques de prix, distributions et splits ainsi que l'ajustement du `Close` et de l'`Adjusted Close`, mais la documentation publique examinée ne définit pas suffisamment la construction exacte de `Open` ([Yahoo, données historiques](https://help.yahoo.com/kb/finance/certain-amounts-sln2311.html), [Yahoo, adjusted close](https://help.yahoo.com/kb/finance/adjusted-close-sln28256.html)).

La fenêtre commençant le **2 janvier 2018** est la candidate la plus simple : 2 210 séances communes SPY–BIL jusqu'au 16 octobre 2026, calendriers observés identiques, aucune ouverture ou clôture manquante et aucun split postérieur. Elle évite de transformer les prix BIL antérieurs au split inversé du 30 novembre 2017. Elle n'est ni une période expérimentale adoptée, ni une séparation entraînement/test.

Une réserve critique subsiste : l'ouverture SPY du **20 avril 2026** diverge matériellement de Nasdaq, dont la barre est elle-même dégénérée. Toute transaction dont la prochaine ouverture serait cette date doit être déclarée `NON_REPRESENTABLE_V1` tant qu'une source officielle tierce ne résout pas le cas. Aucune valeur n'est corrigée ou supprimée.

Ce document ne crée aucun ordre historique, portefeuille, rendement exécutable, backtest, scénario chiffré de coûts ou moteur de transactions.

## 2. Objets à ne pas confondre

| Objet | Définition dans ce projet | Statut |
|---|---|---|
| Transaction observable | ordre, routage, quantité, venue, heure et fill effectivement enregistrés pour un compte | absente |
| Transaction hypothétique | transformation comptable sous des règles annoncées et un prix de référence | objet futur du protocole |
| Prix de référence | champ de données utilisé conventionnellement pour valoriser une opération hypothétique | Yahoo `Open`, conditionnel |
| Prix garanti | prix auquel l'intégralité d'un ordre donné aurait nécessairement été exécutée | non disponible |
| Prix d'enchère officiel | résultat de l'enchère du marché primaire identifié comme tel | non acquis historiquement |

Un OHLCV quotidien ne révèle pas le type d'ordre, l'heure d'arrivée, la file, la venue d'exécution, les fills partiels, le bid/ask, la profondeur ou les corrections de transactions. Il ne suffit donc pas à reconstituer une transaction individuelle.

## 3. Mandat financier candidat inchangé

Le gestionnaire stylisé administre une poche SPY–BIL :

- long-only, sans emprunt ni vente à découvert ;
- exposition cible SPY comprise entre 0 et 100 % ;
- BIL comme composante monétaire investie, et non comme cash constant ou taux sans risque ;
- cash uniquement résiduel ou technique ;
- décision envisagée chaque semaine après la dernière clôture ;
- croissance composée nette des coûts sous contraintes de risque encore à approuver.

Le poids SPY, la fréquence, l'horizon, la richesse initiale et les contraintes de risque restent des propositions. Le protocole précise seulement ce que signifierait une transaction si le mandat était ultérieurement approuvé.

## 4. Chronologie sans information future

Toutes les heures sont définies dans le fuseau IANA `America/New_York`. Aucun décalage UTC ou Casablanca fixe ne doit être codé : le changement d'heure est géré par la zone historique.

Pour une semaine ISO `k` :

1. `d_k` est la date maximale effectivement présente pour SPY et BIL dans cette semaine, sans créer de séance ni interpoler.
2. La décision ne peut être horodatée qu'après la clôture effective de `d_k` **et** après disponibilité des données nécessaires. Une clôture anticipée remplace 16 h comme borne pertinente.
3. L'ensemble d'information contient uniquement des valeurs dont l'horodatage de disponibilité est inférieur ou égal à la décision. Le close de `d_k` peut dimensionner l'ordre; l'open de la séance suivante ne le peut pas.
4. `e_k` est la première date commune strictement postérieure à `d_k` que le calendrier officiel et les données déclarent admissible.
5. Les quantités sont figées avant l'ouverture de `e_k`. Elles ne sont jamais recalculées avec `Open(e_k)`.
6. Si les deux `Open(e_k)` sont valides et non frappés d'une anomalie critique non résolue, la comptabilité hypothétique les emploie comme prix de référence.
7. Sinon, le rééquilibrage est `NON_REPRESENTABLE_V1`; les positions antérieures sont conservées et l'ordre n'est pas reporté silencieusement à une autre séance.
8. L'exposition économique change au trade date `e_k`; cash et titres sont dénoués à la settlement date applicable.

Cette règle empêche le biais principal : choisir les quantités après avoir observé le prix auquel elles sont supposées s'exécuter.

## 5. Enchère NYSE Arca et nature des ordres

### 5.1 Règles documentées

Les horaires NYSE Arca actuels indiquent une séance cœur de 9 h 30 à 16 h ET et une Core Open Auction à 9 h 30. La publication des déséquilibres commence à 8 h; les demandes d'annulation MOO/LOO sont rejetées à partir de 9 h 29 et les nouveaux MOO/LOO à partir du gel de 9 h 29 min 55 s ([NYSE, Auctions](https://www.nyse.com/trade/auctions), [NYSE, hours and calendars](https://www.nyse.com/trade/hours-calendars)). Les enchères ne concernent que les titres admissibles.

Une documentation SEC/NYSE de 2017 montre que les règles Pillar 7.31-E et 7.35-E encadraient déjà les ordres et enchères avant la fenêtre candidate ([SEC, exhibit 5c de 2017](https://www.sec.gov/files/rules/sro/nysearca/2017/34-80929-ex5c.pdf)). Cela soutient la structure générale à partir de 2018, mais ne prouve pas que chaque détail ou cutoff actuel est resté inchangé chaque jour. Une validation historique exhaustive des versions de règles reste nécessaire avant toute affirmation d'admissibilité réelle.

### 5.2 MOO, ordre au marché et ouverture observée

- Un **Market-on-Open (MOO)** est un ordre au marché destiné uniquement à l'enchère d'ouverture ou, selon les règles, à une enchère de reprise. Son acceptation dépend du titre, de la venue, de l'heure d'arrivée et des contrôles du membre/courtier.
- Un **ordre au marché ordinaire** recherche une exécution lorsqu'il devient éligible. Transmis pendant une séance étendue ou routé vers une autre venue, il ne désigne pas nécessairement le prix de la Core Open Auction.
- Le champ quotidien **`Open`** est une observation de fournisseur. Il ne porte aucune preuve sur l'ordre, le routage ou le fill d'un investisseur.

Affirmer qu'un ordre aurait participé à une enchère précise nécessiterait au minimum : marché primaire et symbole admissible ce jour-là, version historique des règles, type et instructions de l'ordre, quantité, heure d'acceptation, statut de l'ordre, courtier/routage, déséquilibre et collars, interruptions, résultat d'enchère et éventuels rejets. Ces éléments ne sont pas présents dans Yahoo ou Nasdaq.

Le protocole v1 n'affirme donc pas « exécution MOO ». Il énonce seulement « transaction hypothétique au champ Yahoo `Open` de la séance admissible ».

## 6. Investigation des divergences SPY

Le script [`audit_spy_open_divergences.py`](../scripts/audit_spy_open_divergences.py) relit les sources figées du manifeste. Il applique le seuil antérieur de 10 points de base, compare chaque ouverture à la plage `[Low, High]` de l'autre fournisseur et ne modifie aucune observation.

### 6.1 Les 17 alertes d'ouverture

Treize alertes sont classées **observations économiquement plausibles** : les deux ouvertures appartiennent aux deux plages quotidiennes. Cette compatibilité ne prouve pas une différence de définition, mais elle est cohérente avec des premiers échanges ou des agrégations distincts.

| Date | Open Yahoo | Open Nasdaq | Écart (pb) | Test de plage | Classement |
|---|---:|---:|---:|---|---|
| 2016-10-21 | 213,88 | 212,96 | +43,20 | mutuellement compatibles | plausible |
| 2016-11-07 | 208,55 | 211,45 | −137,15 | Yahoo hors plage Nasdaq | non résolu |
| 2017-01-23 | 226,74 | 226,35 | +17,23 | mutuellement compatibles | plausible |
| 2017-02-01 | 227,53 | 228,255 | −31,76 | mutuellement compatibles | plausible |
| 2017-02-02 | 227,62 | 227,20 | +18,49 | mutuellement compatibles | plausible |
| 2017-02-08 | 228,94 | 228,61 | +14,44 | mutuellement compatibles | plausible |
| 2017-02-09 | 229,24 | 229,56 | −13,94 | Yahoo hors plage Nasdaq | non résolu |
| 2017-03-23 | 234,28 | 234,00 | +11,97 | mutuellement compatibles | plausible |
| 2017-05-03 | 238,77 | 238,29 | +20,14 | mutuellement compatibles | plausible |
| 2017-05-17 | 240,08 | 238,10 | +83,16 | Yahoo hors plage Nasdaq | non résolu |
| 2017-10-30 | 256,47 | 257,07 | −23,34 | mutuellement compatibles | plausible |
| 2017-12-05 | 263,19 | 264,43 | −46,89 | mutuellement compatibles | plausible |
| 2017-12-06 | 263,30 | 262,87 | +16,36 | mutuellement compatibles | plausible |
| 2017-12-07 | 264,07 | 263,09 | +37,25 | mutuellement compatibles | plausible |
| 2017-12-11 | 266,31 | 265,58 | +27,49 | mutuellement compatibles | plausible |
| 2017-12-12 | 267,21 | 266,57 | +24,01 | mutuellement compatibles | plausible |
| 2026-04-20 | 708,78 | 710,14 | −19,15 | plages incompatibles | non résolu critique |

Aucune alerte n'est classée « différence de définition documentée » ou « erreur de fournisseur démontrée ». La cohérence interne ne permet pas d'attribuer la vérité à l'une des deux sources.

### 6.2 Cas prioritaires

| Date | Champs matériels | Constat | Classement |
|---|---|---|---|
| 2016-11-07 | open, low | Yahoo ouvre et cote au plus bas à 208,55; le low Nasdaq est 211,30 | non résolu, hors fenêtre candidate |
| 2017-05-17 | open, high | Yahoo ouvre et cote au plus haut à 240,08; le high Nasdaq est 238,64 | non résolu, hors fenêtre candidate |
| 2019-08-14 | high | 288,74 Yahoo contre 292,4644 Nasdaq; les autres champs ne justifient pas l'écart | non résolu; n'affecte pas directement `Open` |
| 2021-03-09 | low | 385,31 Yahoo contre 381,7299 Nasdaq | non résolu; n'affecte pas directement `Open` |
| 2026-04-17 | volume | 70 661 900 Yahoo contre exactement 9 999 999 Nasdaq | anomalie Nasdaq probable, mais erreur non démontrée |
| 2026-04-20 | OHLC et volume | Nasdaq publie quatre OHLC égaux à 710,14 et aucun volume; Yahoo publie 708,78/709,91/706,14/708,72 | non résolu critique pour l'ouverture |

Le produit historique officiel NYSE TAQ Closing Prices annonce des champs Open/High/Low/Last et volume pour les titres NYSE Arca, mais il s'agit d'un produit de données soumis à accès et licence; il n'a pas été acquis dans cette phase ([NYSE, Historical Data](https://www.nyse.com/market-data/historical), [NYSE, Academic Customers](https://www.nyse.com/market-data/academics)). Sans cette référence ou un équivalent contractuel, une correction serait arbitraire.

## 7. Nature et ajustements de Yahoo `Open`

Les réponses locales portent `exchangeName=PCX`, `fullExchangeName=NYSEArca`, `exchangeTimezoneName=America/New_York` et `dataGranularity=1d`. Le timestamp quotidien local est cohérent avec 9 h 30, mais cela ne démontre ni l'origine consolidée du prix ni sa participation à l'enchère.

Les preuves disponibles établissent :

- les OHLC SPY et BIL sont cohérents structurellement ;
- les OHLC BIL antérieurs au 30 novembre 2017 ont été rétrospectivement placés sur l'échelle post-split ;
- `Close` est présenté comme ajusté des splits et `Adjusted Close` comme ajusté en plus des distributions ;
- aucune documentation consultée ne tranche entre premier échange régulier, prix officiel d'enchère, barre consolidée ou autre construction pour `Open` ;
- aucun bid/ask ou indicateur de transaction hors séance n'accompagne la barre.

La dénomination obligatoire est donc : **prix d'ouverture quotidien Yahoo, utilisé conditionnellement comme référence conventionnelle de transaction, sans garantie de correspondance à une exécution individuelle**.

## 8. Fenêtre historique candidate

### 8.1 Proposition 2018–2026

Du 2 janvier 2018 au 16 octobre 2026 :

- 2 210 dates SPY et 2 210 dates BIL, toutes communes ;
- 2 210 `Open` et `Close` disponibles pour chaque instrument ;
- 459 semaines ISO observées ;
- aucun split SPY ou BIL dans les événements Yahoo ;
- une seule alerte d'ouverture SPY au seuil de 10 pb : le 20 avril 2026, critique et non résolue ;
- les restrictions Yahoo imposent la conservation locale, l'exclusion Git des données et l'absence de redistribution publique.

Cette fenêtre est homogène du point de vue de l'échelle par part BIL. Elle reste conditionnelle : une transaction hebdomadaire pointant vers le 20 avril 2026 n'est pas représentable en v1.

### 8.2 Comparaison avec 2016

Une fenêtre commençant en 2016 ajoute le split BIL du 30 novembre 2017. Les prix Yahoo antérieurs sont déjà ajustés sur l'échelle post-split et ne représentent donc pas le prix par ancienne part observable à l'époque. Il faudrait restaurer prix et quantités historiques de façon cohérente, traiter le volume dont l'ajustement est inconnu et appliquer le split exactement une fois dans le registre. Elle comprend aussi trois ouvertures SPY non résolues avant 2018. Ce surcroît de risque documentaire, et non les performances réalisées, motive la préférence pour 2018.

## 9. Calendrier et admissibilité des séances

### 9.1 Preuves disponibles

Les calendriers observés SPY et BIL sont identiques sur la fenêtre candidate et concordent avec Nasdaq SPY sur la fenêtre de contrôle. Les calendriers annuels officiels NYSE 2022, 2023, 2024 et 2025 identifient jours fermés et clôtures anticipées à 13 h ET ([2022](https://www.nyse.com/publicdocs/ICE_NYSE_2022_Yearly_Trading_Calendar.pdf), [2023](https://www.nyse.com/publicdocs/ICE_NYSE_2023_Yearly_Trading_Calendar.pdf), [2024](https://www.nyse.com/publicdocs/ICE_NYSE_2024_Yearly_Trading_Calendar.pdf), [2025](https://www.nyse.com/publicdocs/ICE_NYSE_2025_Yearly_Trading_Calendar.pdf)). La page NYSE courante couvre les années futures proches et les horaires de séance.

La fermeture exceptionnelle du 5 décembre 2018 est corroborée par une annonce SEC du jour de deuil national ([SEC](https://www.sec.gov/newsroom/whats-new/edgar-be-closed-wednesday-december-5-2018)); celle du 9 janvier 2025 est documentée par un mémo NYSE ([NYSE Regulation](https://www.nyse.com/publicdocs/nyse/markets/american-options/rule-interpretations/2025/National_Day_of_Mourning_20250102.pdf)). Les quatre interruptions de marché de mars 2020 sont documentées par NYSE; elles interrompent des séances existantes et ne justifient pas leur suppression ([NYSE, 2020 volatility](https://www.nyse.com/article/assessing-nyse-model-performance)).

### 9.2 Limite et règle v1

Le calendrier est suffisamment fiable pour **ordonner provisoirement les dates observées**, mais pas encore pour affirmer exhaustivement l'heure réelle de clôture, un retard d'ouverture ou une interruption propre à chaque titre sur toutes les années 2018–2026. Les archives officielles 2018–2021 des clôtures anticipées et un historique de statuts/halts par symbole ne sont pas localement acquis.

La future implémentation devra donc :

- prendre l'intersection des séances SPY et BIL, validée contre un calendrier officiel versionné ;
- définir la dernière séance hebdomadaire comme le maximum réellement ouvert de la semaine, même un jeudi ou une séance écourtée ;
- définir la prochaine séance comme le minimum commun strictement postérieur ;
- enregistrer l'heure de clôture effective et décider seulement après celle-ci ;
- ne jamais ajouter un jour ouvré civil absent, ni interpoler un prix ;
- rendre la transaction non représentable si une ouverture manque, vaut zéro, viole l'OHLC, correspond à une anomalie critique ou si une ouverture retardée/enchère ne peut être qualifiée.

## 10. Poids, quantités et ordres conceptuels

### 10.1 Dimensionnement connu avant l'ouverture

Soit `W_d^M` la richesse de marché connue après la clôture de décision `d`, `w_SPY` le poids cible et `w_BIL=1-w_SPY`. Avec des parts entières :

\[
q_{i}^{cible}=\left\lfloor \frac{w_i W_d^M}{P_{i,d}^{close}} \right\rfloor,
\qquad
\Delta q_i=q_i^{cible}-q_{i,d}.
\]

Le prix de dimensionnement est le `Close` disponible à `d`, pas l'`Open` futur. Les quantités sont figées avant `e`. Le cash restant après dimensionnement est un reliquat, pas un troisième choix stratégique. Les fractions sont désactivées dans le cas principal; leur activation exigerait les règles historiques d'un courtier.

L'allocation effectivement obtenue à l'ouverture différera de la cible en raison du gap, de l'arrondi, des éventuels coûts et des contraintes de financement. Cet écart doit être mesuré ultérieurement, jamais effacé par un redimensionnement utilisant le futur.

### 10.2 Financement et échec

Le protocole distingue deux conventions, sans prétendre qu'elles sont contractuellement disponibles :

1. **Cash réglé conservateur** : les achats doivent être couverts par le cash réglé avant transaction. Les produits de vente du même jour ne sont pas disponibles. Un rééquilibrage croisé peut alors être infaisable.
2. **Netting au même règlement (`H-FIN-NET`)** : créances de vente et dettes d'achat ayant la même date de règlement peuvent être compensées pour tester le financement. Cette hypothèse est compatible avec un registre institutionnel stylisé, mais exige l'approbation du type de compte, du courtier et de ses règles.

Le cas principal recommandé pour une future comptabilité synthétique est `H-FIN-NET`, explicitement étiqueté comme hypothèse. Il ne devient admissible qu'après approbation. Les ventes et achats sont simultanés au prix de référence; « vendre d'abord » ne décrit pas une enchère commune.

Après application des prix d'ouverture et des coûts autorisés, si le cash net final serait négatif ou une quantité indisponible, l'ensemble du rééquilibrage est `NON_REPRESENTABLE_V1`. Il n'y a ni part fractionnaire implicite, ni emprunt, ni réduction après coup des achats, ni fill partiel inventé. Une convention de réduction déterministe pourrait être approuvée dans une version ultérieure.

La richesse initiale ne reçoit aucune valeur numérique dans ce document.

## 11. Trade date, settlement date et registre

Pour la fenêtre candidate, T+2 s'applique du 2 janvier 2018 au 24 mai 2024 inclus, puis T+1 à partir du 28 mai 2024. La SEC fixe le passage T+2 au 5 septembre 2017 et le passage T+1 au 28 mai 2024 ([SEC, T+2](https://www.sec.gov/newsroom/press-releases/2017-68-0), [SEC, règle T+1](https://www.sec.gov/rules-regulations/2023/02/34-96930), [SEC, mise en œuvre T+1](https://www.sec.gov/newsroom/press-releases/2024-62)). T+3 ne concerne qu'une éventuelle extension antérieure au 5 septembre 2017.

Au trade date, le registre doit enregistrer séparément :

- l'ordre conceptuel et la quantité hypothétiquement exécutée ;
- le prix de référence et les coûts externes ;
- la nouvelle position économique ;
- les titres achetés ou vendus en cours de règlement ;
- la créance de vente et la dette d'achat ;
- le régime et la date de règlement calculée sur un calendrier ouvré de règlement.

Au settlement date, livraison de titres, créance de vente et dette d'achat sont transférées contre le cash réglé. Ce dénouement est un transfert comptable et ne crée pas de richesse.

La richesse doit pouvoir être présentée sous deux valorisations cohérentes :

\[
W_t^{NAV}=\sum_i n_{i,t}N_{i,t}+C_t+A_t+R_t^{vente}-D_t^{achat}-K_t,
\]

\[
W_t^{M}=\sum_i n_{i,t}P_{i,t}^{M}+C_t+A_t+R_t^{vente}-D_t^{achat}-K_t,
\]

où `A` désigne les distributions acquises non encaissées, `R` les produits de vente à recevoir, `D` les achats à payer et `K` les coûts externes déjà reconnus. Les titres en règlement doivent être inclus une seule fois dans la position économique.

Une vente postérieure à l'ex-date ne supprime pas un droit déjà acquis. Le paiement d'une distribution annule la créance contre du cash sans nouveau gain. Un split modifie parts et prix par part sans modifier la richesse. Les indices SPY-B et BIL-B ne doivent pas être combinés mécaniquement pour représenter ce registre rééquilibré.

Les règles SEC sur les comptes cash montrent que l'utilisation et la revente de titres non intégralement payés peuvent déclencher des restrictions; les pratiques exactes restent celles du courtier ([SEC, Trading in Cash Accounts](https://www.sec.gov/files/investor/alerts/cashaccounts.pdf)).

## 12. Coûts de transaction

| Composante | Données actuelles | Traitement honnête |
|---|---|---|
| frais internes des ETF | déjà incorporés aux NAV/prix | ne pas les ajouter une seconde fois |
| commissions/frais du compte | aucun courtier ni barème historique choisi | observables après choix et archivage contractuel |
| spread bid-ask | aucun NBBO historique acquis | potentiellement estimable après acquisition de quotes horodatées |
| slippage individuel | absent des OHLCV | non identifiable; scénario seulement |
| profondeur/impact | carnet et taille d'ordre absents | non identifiable; scénario ou données microstructure |
| qualité de l'enchère/fill partiel | ordres et messages d'enchère absents | non identifiable dans les barres |
| fiscalité | résidence, compte et lots fiscaux non choisis | hors v1 jusqu'à décision explicite |

Trois couches pourront être séparées :

1. cas comptable théorique au `Open` de référence, sans frais externes ;
2. scénarios hypothétiques de coûts, clairement étiquetés et non calibrés ici ;
3. estimation empirique fondée sur quotes, barèmes et données d'exécution réellement acquises.

Le premier cas vérifie un registre; il ne mesure pas une performance nette historiquement accessible. Aucun coût numérique n'est choisi dans cette phase.

## 13. Matrice de validation

| Élément | Preuve disponible | Hypothèse / limite | Statut v1 | Conséquence |
|---|---|---|---|---|
| intégrité OHLCV | hashes, manifeste, 4 878 dates communes, audit reproductible | définition fournisseur limitée | `AUDITED` | descriptif autorisé |
| champ Yahoo `Open` | présent, positif, OHLC cohérent, contrôle Nasdaq | construction exacte non documentée | `CONDITIONAL_REFERENCE` | simulation hypothétique seulement |
| divergences SPY | 17 alertes reproduites; 13 plausibles, 4 non résolues | aucune source officielle tierce acquise | `PARTIAL` | 2026-04-20 non représentable |
| fenêtre depuis 2018 | 2 210 dates communes, aucun split ou champ manquant | fin au 2026-10-16 | `CANDIDATE` | pas encore période expérimentale |
| calendrier de dates | concordance SPY/BIL/Nasdaq, calendriers NYSE partiels | archives exhaustives 2018–2021 et halts par titre absents | `PARTIAL` | sélection provisoire des dates seulement |
| horaires/cutoffs | règles actuelles et pièces 2017 | historique quotidien non exhaustif | `PARTIAL` | ne pas prétendre à un MOO réel |
| split BIL | SEC, State Street et Yahoo concordent sur 2017 | prix/volume pré-split complexes | `VALIDATED_EVENT` | commencer en 2018 |
| quantité avant open | formule au close antérieur, parts entières | richesse initiale non approuvée | `PROPOSED` | évite le look-ahead |
| comptabilité trade/settlement | identité NAV validée et règles SEC T+2/T+1 | moteur non construit | `SPECIFIED` | implémentation synthétique possible après accord |
| financement | variantes cash réglé et `H-FIN-NET` | compte/courtier absent | `NOT_APPROVED` | bloque l'exécutabilité du rééquilibrage |
| coûts empiriques | frais internes seulement | quotes, barèmes et ordres absents | `BLOCKED_FOR_EMPIRICAL_COSTS` | zéro coût = cas théorique uniquement |
| exécution réelle | aucune donnée de compte ou de fill | venue/routage/file inconnus | `NOT_VALIDATED` | aucune revendication de réalisme intégral |

## 14. Conditions minimales avant une comptabilité synthétique

Une première implémentation purement comptable, encore sans stratégie ni backtest, exige :

1. approbation explicite du mandat, de la fréquence et de la convention Yahoo `Open` ;
2. approbation de la fenêtre candidate et de l'exclusion transactionnelle du 20 avril 2026 ;
3. calendrier NYSE Arca officiel versionné avec jours fermés, early closes et exceptions 2018–2026 ;
4. règle documentée pour les retards/halts et les ouvertures absentes ;
5. richesse initiale, parts entières et règle de non-représentabilité approuvées ;
6. choix entre cash réglé et `H-FIN-NET`, appuyé si possible sur un type de compte réel ;
7. schéma de registre testable séparant positions économiques, titres en règlement, cash, créances, dettes, distributions et coûts ;
8. jeux de tests artificiels de conservation de richesse, sans données historiques ni performance ;
9. politique de coûts choisie : zéro coût théorique ou scénarios explicitement hypothétiques ;
10. aucune promotion des OHLCV au statut de fills observés.

## 15. Décisions encore ouvertes et règle d'arrêt

Le porteur du projet doit encore approuver : mandat, horizon, fréquence, richesse initiale, fractions, compte/courtier, financement, traitement d'une transaction non représentable, coûts, calendrier officiel et usage conditionnel de Yahoo `Open`.

Le plus petit travail scientifique suivant serait de **figer un calendrier officiel 2018–2026 et de spécifier/tester sur cas artificiels le registre trade-date/settlement-date**, sans ordre historique, allocation, performance ou calibration. L'acquisition ciblée d'un prix officiel d'ouverture pour les quatre cas non résolus peut constituer un lot documentaire séparé.

Aucune phase supplémentaire, aucune implémentation comptable et aucune expérience ne découle automatiquement de ce rapport.

## 16. Réponses A–J

**A. Convention recommandée.** Décision hebdomadaire après la clôture effective, quantités entières dimensionnées avec le close alors connu, puis transaction hypothétique au Yahoo `Open` de la prochaine séance commune admissible. Elle évite d'utiliser l'open futur pour calculer l'ordre et reste explicitement un modèle.

**B. Définition de Yahoo `Open`.** Non. La présence et la cohérence du champ sont auditées, mais sa correspondance au premier échange régulier, au prix officiel d'enchère ou à une consolidation n'est pas suffisamment documentée.

**C. Divergences problématiques.** Quatre ouvertures ont une incompatibilité de plage : 2016-11-07, 2017-02-09, 2017-05-17 et 2026-04-20. Seule la dernière est dans la fenêtre 2018; elle rend non représentable une transaction pointant sur cette ouverture. Les anomalies de high 2019, low 2021 et volume 2026 restent non résolues mais ne déterminent pas directement le prix d'ouverture v1.

**D. Période défendable.** Du 2 janvier 2018 au 16 octobre 2026 comme fenêtre de faisabilité candidate, parce qu'elle est commune, complète pour Open/Close et postérieure au split BIL. Ce choix est indépendant des rendements.

**E. Calendrier.** Les dates observées sont suffisamment concordantes pour une règle provisoire. Le calendrier n'est pas encore exhaustivement validé pour heures de clôture anticipée, ouvertures retardées et halts sur toute la fenêtre.

**F. Quantités, cash et règlements.** Dimensionner les parts entières au close antérieur, conserver le reliquat, enregistrer positions et comptes de règlement séparément, et interdire toute dépense de produits non réglés sauf hypothèse `H-FIN-NET` approuvée. Toute insuffisance rend le rééquilibrage non représentable plutôt que d'inventer un financement.

**G. Coûts.** Les commissions deviendraient observables avec un courtier et son barème; le spread serait estimable avec des quotes fiables. Slippage, profondeur, impact et qualité individuelle ne sont pas identifiables dans les OHLCV et exigeraient données supplémentaires ou scénarios annoncés.

**H. Établi contre à approuver.** Sont établis l'intégrité des fichiers, leur couverture, le split BIL, les régimes T+2/T+1 et la cohérence comptable générale. Restent à approuver l'open conventionnel, le calendrier complet, les quantités, la richesse initiale, le financement, le courtier et les coûts.

**I. Conditions minimales.** Calendrier officiel versionné, conventions approuvées, traitement des anomalies, schéma de registre et tests artificiels de conservation de richesse, sans utiliser encore de trajectoire historique de portefeuille.

**J. Travail suivant minimal.** Compléter le calendrier officiel et construire uniquement des tests comptables synthétiques trade/settlement sur cas artificiels; rechercher séparément un prix d'ouverture officiel pour les quatre divergences non résolues.
