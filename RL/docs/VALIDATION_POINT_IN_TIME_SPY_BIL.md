# Validation point-in-time des informations SPY–BIL

Date : 20 octobre 2026

Point de départ : `5150fd19616ce283b462605990d280bd792b3715`

Verdict : **`PARTIALLY_VERIFIED`**

## 1. Conclusion et portée

Le projet peut maintenant distinguer, pour chaque famille d'information requise,
l'événement économique, son observabilité, sa publication, l'acquisition locale et
les révisions possibles. Cette distinction ne rend toutefois pas l'historique
point-in-time complet.

Les prix quotidiens Yahoo actuellement conservés ont été acquis le 19 octobre 2026.
Leur `Close` historique peut servir de **proxy d'un prix de marché observable à
l'époque**, mais aucune archive datée de chaque soir ne prouve que la valeur du
fichier courant était exactement celle alors diffusée. `Adj Close` est une
transformation rétrospective et ne doit pas dimensionner une décision. Le champ
`Open` ne peut être utilisé qu'après l'ouverture, comme référence transactionnelle
hypothétique conditionnelle, jamais comme information de la décision précédente.

Le fichier State Street des distributions ne contient pas de date d'annonce. Les
ex-dates, record dates, payment dates et montants actuellement connus ne prouvent
donc pas que ces caractéristiques étaient disponibles avant chaque ex-date. Les
calendriers de négociation et de règlement restent eux aussi partiels, surtout pour
2018–2021, les exceptions quotidiennes DTC/NSCC et les fermetures imprévues.

Le contrôle autorisé a lu quelques lignes des fichiers locaux en lecture seule. Il
n'a créé ni ordre, ni allocation, ni transaction, ni rendement, ni portefeuille,
ni mesure de performance. Aucun fichier brut, OHLCV, NAV ou manifeste n'est modifié.

## 2. Configuration candidate v1 — fiche non approuvée

Tous les choix ci-dessous restent des **propositions soumises à approbation**. Leur
regroupement dans une fiche unique empêche seulement une dérive silencieuse.

| Dimension | Configuration candidate v1 | Statut |
|---|---|---|
| portefeuille | poche autonome USD, SPY–BIL uniquement | proposé |
| positions | long-only, aucune position négative | proposé |
| levier | aucun emprunt, marge ou levier implicite | proposé |
| compte | compte cash stylisé, fiscalité exclue | proposé |
| financement | `H_FIN_NET` limité aux ventes de titres déjà réglés et aux flux admissibles de même échéance | proposé ; contrat de courtier non prouvé |
| capital principal | 100 000 USD | proposé |
| sensibilités de capital | 10 000 et 1 000 000 USD | proposées ex ante |
| parts | entières | proposé |
| fréquence | hebdomadaire, après la dernière clôture commune | proposé |
| ordre | quantités calculées au close connu puis figées avant l'ouverture | proposé |
| prix de transaction | Yahoo `Open` comme référence hypothétique conditionnelle, jamais comme fill | proposé |
| horizon | un an, sans liquidation terminale forcée | proposé |
| cash | technique et résiduel, non rémunéré | proposé |
| risque | mesuré séparément, sans seuil dur v1 | proposé |
| échec économique | lot rejeté atomiquement, distinct d'un hold volontaire | proposé |
| défaut documentaire | transition non évaluable, distincte d'un rejet économique | proposé |

Le rapport de prérequis recommandait auparavant le cash réglé conservateur comme
cas principal et `H_FIN_NET` comme variante. La proposition de mandat ultérieure
recommande `H_FIN_NET` limité. Cette divergence n'est pas effacée : le porteur doit
explicitement choisir la convention principale avant toute expérience.

## 3. Définition scientifique de l'information disponible

Une observation n'est disponible pour une décision à l'instant `t` que si son
contenu pertinent et sa version admissible peuvent être reliés à une preuve de
publication ou d'observabilité antérieure ou égale à `t`. Cinq dates ou instants
doivent rester séparés :

| Dimension | Question |
|---|---|
| date économique | à quelle séance ou à quel événement la valeur se rapporte-t-elle ? |
| instant observable | quand un participant pouvait-il raisonnablement l'observer ? |
| publication de la source | quand la source a-t-elle publié cette version ou annonce ? |
| acquisition locale | quand le projet a-t-il figé les octets actuellement audités ? |
| correction/révision | la valeur ou sa transformation a-t-elle pu changer ensuite ? |

Une date économique ancienne n'est pas une preuve de publication ancienne. Une
date d'acquisition en 2026 ne transforme pas non plus une valeur historique en
information future : elle empêche seulement de certifier la version exacte connue
à l'époque sans archive supplémentaire.

## 4. Convention temporelle prudente proposée

Tous les instants sont exprimés dans la zone IANA `America/New_York`. Aucun offset
UTC fixe n'est autorisé ; les changements EDT/EST sont résolus par la base de zones.

La convention proposée est la suivante :

1. `d_k` est la dernière séance effectivement commune SPY–BIL de la semaine ISO,
   confirmée par un calendrier de négociation applicable.
2. Son instant de clôture est l'heure officielle historique : 16:00:00 ET pour une
   séance régulière ou 13:00:00 ET pour une séance écourtée documentée. Un halt ou
   une clôture exceptionnelle doit posséder sa propre preuve.
3. `e_k` est la première séance commune strictement postérieure, qualifiée par le
   calendrier. L'instant candidat de décision est fixé à **08:00:00 ET le jour
   `e_k`**, soit avant l'ouverture régulière prévue à 09:30.
4. Une observation n'entre dans la décision que si sa disponibilité est prouvée au
   plus tard à 08:00:00 ET. Cette attente constitue un embargo prudent entre la
   clôture et la décision ; elle ne prouve pas à elle seule la valeur Yahoo.
5. Les quantités sont figées à 08:00:00 ET. Aucun champ de la barre de `e_k`, y
   compris `Open`, ne peut les modifier.
6. L'`Open` de `e_k` n'est observé qu'après l'ouverture. Il peut alors valoriser une
   transaction hypothétique si son statut et le calendrier sont admissibles.
7. Si une disponibilité, une fermeture, une ouverture retardée ou une anomalie ne
   peut être qualifiée, le cas est documentairement non évaluable. Il n'est ni
   reporté, ni corrigé, ni transformé en hold.

Cette convention est déterministe et choisie sans examiner de performance. Elle est
plus prudente qu'une décision immédiate à 16:00, car les heures historiques de mise
à disposition des barres quotidiennes, NAV et annonces ne sont pas établies. Elle
reste à approuver. Une donnée sans preuve de disponibilité à 08:00 demeure
`UNVERIFIED`, quelle que soit la longueur de l'embargo.

## 5. Prix de clôture et d'ouverture

### 5.1 Clôture

Le prix de clôture du marché était observable après les transactions de la séance.
Le `Close` Yahoo actuel est une approximation plausible de cette information, mais :

- le fichier a été acquis en 2026, pas chaque soir historique ;
- Yahoo indique que `Close` est ajusté des splits ;
- BIL avant le 30 novembre 2017 est rétrospectivement placé sur l'échelle
  post-split ;
- le fournisseur ne documente pas complètement la consolidation de la barre ;
- une acquisition répétée a déjà modifié de nombreuses valeurs d'`Adj Close`.

Le statut du `Close` Yahoo est donc `MARKET_OBSERVABLE_PROXY`, pas
`VERIFIED_POINT_IN_TIME`. Il pourrait dimensionner une future intention uniquement
sous une hypothèse explicitement approuvée et versionnée. La NAV ne le remplace pas.

### 5.2 Ouverture

Le `Open` Yahoo est une barre fournisseur horodatée 09:30 ET. Cet horodatage peut
étiqueter la journée et ne prouve ni Core Open Auction, ni premier échange
consolidé, ni fill. Il est interdit dans l'ensemble d'information de la décision
précédente et dans le calcul des quantités.

Comme référence transactionnelle postérieure à la décision, son statut est
`MARKET_OBSERVABLE_PROXY` sous approbation. Pour SPY le 20 avril 2026, Yahoo publie
708,780029296875 tandis que Nasdaq publie 710,14 avec quatre OHLC identiques et un
volume `N/A`. Les plages sont incompatibles. Le statut reste `DISPUTED` et le code
opérationnel futur doit rester `PRICE_DISPUTED`/`PRICE_MISSING_OR_DISPUTED`, sans
choix opportuniste d'un fournisseur.

### 5.3 Adjusted Close et NAV

`Adj Close` incorpore les splits et distributions selon une transformation actuelle
du fournisseur. Il est `EX_POST_ONLY` pour une décision : ce n'est ni le cash, ni le
prix par part alors affiché, ni un prix exécutable. Les NAV State Street servent aux
contrôles comptables et de détention, pas à remplacer silencieusement `Close` ou
`Open`.

## 6. Distributions et opérations sur titres

### 6.1 Distributions

Le classeur State Street actuel contient `EX-DATE`, `RECORD DATE`, `PAYABLE DATE`,
`DIVIDEND ($)`, gains en capital et fréquence. Il ne contient ni date/heure
d'annonce, ni version d'annonce, ni date de modification du montant.

Il faut distinguer :

- l'annonce, qui peut rendre dates et montant utilisables dans une décision ;
- l'ex-date, où le détenteur admissible acquiert comptablement une créance ;
- la record date, qui ne prouve pas la date de connaissance ;
- la payment date, où la créance devient cash ;
- l'acquisition du classeur, le 19 octobre 2026.

La naissance comptable d'une créance à l'ex-date n'implique donc pas que le montant
ou la payment date étaient connus avant cette ex-date. Sans archive d'annonce, les
caractéristiques futures de la distribution sont `UNVERIFIED` pour une décision
antérieure. L'événement réalisé peut rester utilisé ex post pour une comptabilité
correcte, à condition de ne pas l'introduire plus tôt dans l'état d'information.

Deux premières distributions de la fenêtre candidate, choisies sans rendement,
illustrent la lacune :

| Instrument | Ex-date | Record date | Payment date | Montant USD/part | Annonce pré-ex-date prouvée ? | Statut avant ex-date |
|---|---|---|---|---:|---|---|
| BIL | 2018-02-01 | 2018-02-02 | 2018-02-07 | 0,086157 | non, champ absent | `UNVERIFIED` |
| SPY | 2018-03-16 | 2018-03-19 | 2018-04-30 | 1,096775 | non, champ absent | `UNVERIFIED` |

Le cas BIL du 3 mars 2008 conserve en outre des record/payment dates incohérentes ;
aucune correction n'est autorisée.

### 6.2 Split BIL

Le dépôt SEC BIL a été accepté le 28 novembre 2017 avec le champ
`ACCEPTANCE-DATETIME=20171128124402`. Il annonce un reverse split programmé le
30 novembre : la nature et la date de l'événement possèdent donc une preuve
antérieure. Ce dépôt ne donne pas le ratio. Le Form 8937 qui confirme deux anciennes
parts pour une nouvelle est signé le 6 décembre, après l'événement. Le ratio n'est
donc pas démontré point-in-time par les seules pièces locales avant le split.

Les OHLC Yahoo antérieurs sont déjà multipliés par deux sur l'échelle post-split.
Cette transformation est `EX_POST_ONLY` pour le prix par ancienne part. Aucune
reconstruction de prix non ajusté ou de volume n'est créée. La fenêtre candidate
commençant en janvier 2018 évite ce conflit d'échelle sans prétendre que la série
pré-split était historiquement disponible sous sa forme actuelle.

## 7. Calendriers connus, constatés et reconstruits

| Information | Ce qui est établi | Limite point-in-time |
|---|---|---|
| séances observées SPY/BIL | les dates Yahoo concordent sur 2018–2026 | une absence commune est un constat ex post, pas le motif ni l'anticipabilité |
| calendriers NYSE 2022–2025 | fermetures et early closes documentés par des PDF annuels | corpus incomplet pour 2018–2021 et 2026 ; dates de publication non uniformes |
| fermeture du 2018-12-05 | mémo NYSE publié le 2018-12-03 | non connaissable avant l'annonce |
| fermeture du 2025-01-09 | mémo NYSE publié le 2025-01-02 | non connaissable avant l'annonce |
| interruptions de mars 2020 | séances existantes interrompues | historique exhaustif des halts par symbole absent |
| cycle T+1 | règle SEC publiée le 2023-02-15, effective le 2024-05-28 | ne détermine pas seule chaque jour de règlement admissible |
| DTC/NSCC | règles 2026 et guides 2025–2026 distinguent traitement et règlement | pas d'archive exhaustive des avis 2018–2026 |

Une fermeture imprévue ne peut entrer dans une décision antérieure à son annonce.
Une fois annoncée, son usage exige la publication horodatée applicable. Inversement,
une fermeture de marché n'implique pas automatiquement l'arrêt du règlement : les
journées nationales de deuil 2018 et 2025 ont conservé des activités de règlement.

La transition réglementaire est point-in-time vérifiée. Le 24 mai 2024 appartient
encore au régime T+2 et le 28 mai au régime T+1. Déduire une settlement date précise
exige néanmoins le calendrier DTC/NSCC pertinent ; la règle SEC seule ne suffit pas.

## 8. Classification d'admissibilité point-in-time

| Statut | Définition | Conséquence pratique |
|---|---|---|
| `VERIFIED_POINT_IN_TIME` | contenu et disponibilité avant la décision établis par une preuve adaptée | admissible dans l'information de décision selon la version prouvée |
| `MARKET_OBSERVABLE_PROXY` | approximation actuelle d'une observation de marché alors observable, sans archive de cette version | admissible seulement sous hypothèse explicite approuvée et analyse de sensibilité documentaire |
| `EX_POST_ONLY` | information ou transformation construite/consolidée rétrospectivement | interdite dans la décision ; utilisable uniquement pour audit ou comptabilité postérieure clairement séparée |
| `UNVERIFIED` | instant ou contenu historique non démontré | bloque l'usage requis ; aucune imputation |
| `DISPUTED` | sources contradictoires ou anomalie critique non résolue | bloque l'information ou le prix concerné ; aucune substitution opportuniste |

Un proxy n'est jamais cité comme preuve point-in-time. Un futur calcul pourrait
admettre `MARKET_OBSERVABLE_PROXY` uniquement après approbation formelle de la
convention Yahoo et en publiant la couverture. `UNVERIFIED` et `DISPUTED` bloquent
le passage à l'adaptateur. `EX_POST_ONLY` ne peut jamais influencer un poids, une
quantité ou une sélection de date antérieure.

## 9. Contrôle historique minuscule

### 9.1 Règle de sélection

Les dates ont été fixées avant lecture de leurs valeurs et sans utiliser les
rendements :

1. première séance de la fenêtre candidate : 2018-01-02 ;
2. dernière séance avant l'entrée en vigueur de T+1 : 2024-05-24 ;
3. première séance sous T+1 : 2024-05-28 ;
4. anomalie imposée par le protocole : 2026-04-20.

Pour chaque date, seules les deux lignes Yahoo SPY/BIL ont été lues. Nasdaq SPY
n'est consulté que pour le contrôle imposé du 20 avril 2026. Les valeurs ci-dessous
sont les nombres tels que parsés depuis les JSON figés ; aucun arrondi n'alimente un
calcul et aucun calcul de rendement n'est effectué. Les timestamps Unix bruts Yahoo,
identiques pour SPY et BIL, sont respectivement `1514903400`, `1716557400`,
`1716903000` et `1776691800` ; ils correspondent à l'étiquette 09:30 locale des
barres, pas à une heure de publication du fichier.

### 9.2 Sources et empreintes vérifiées

| Identifiant du manifeste | Acquisition | SHA-256 |
|---|---|---|
| `yahoo_spy_chart_ohlcv_20261019` | 2026-10-19 | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| `yahoo_bil_chart_ohlcv_20261019` | 2026-10-19 | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| `nasdaq_spy_ohlcv_20261019` | 2026-10-19 | `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5` |
| `ssga_spdr_distributions_20261019` | 2026-10-19 | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |

Les quatre empreintes locales correspondent exactement au manifeste.

### 9.3 Observations descriptives

| Date | Instrument | Open | High | Low | Close | Volume | Adj Close | Statut proposé | Usage à la décision |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 2018-01-02 | SPY | 267.8399963378906 | 268.80999755859375 | 267.3999938964844 | 268.7699890136719 | 86655700 | 235.36984252929688 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement, sous hypothèse approuvée |
| 2018-01-02 | BIL | 91.41000366210938 | 91.43000030517578 | 91.41000366210938 | 91.41000366210938 | 790000 | 73.3365478515625 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement, sous hypothèse approuvée |
| 2024-05-24 | SPY | 527.8499755859375 | 530.27001953125 | 526.8800048828125 | 529.4400024414062 | 41291100 | 514.2559814453125 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement ; régime T+2 |
| 2024-05-24 | BIL | 91.76000213623047 | 91.7699966430664 | 91.76000213623047 | 91.7699966430664 | 4187400 | 82.98102569580078 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement ; régime T+2 |
| 2024-05-28 | SPY | 530.27001953125 | 530.510009765625 | 527.1099853515625 | 529.8099975585938 | 36269600 | 514.615478515625 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement ; régime T+1 |
| 2024-05-28 | BIL | 91.76000213623047 | 91.7699966430664 | 91.76000213623047 | 91.76000213623047 | 4940900 | 82.97200775146484 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement ; régime T+1 |
| 2026-04-20 | SPY | 708.780029296875 | 709.9099731445312 | 706.1400146484375 | 708.719970703125 | 43546800 | 705.1477661132812 | `DISPUTED` | bloque le prix requis ; aucune substitution |
| 2026-04-20 | BIL | 91.55999755859375 | 91.55999755859375 | 91.55000305175781 | 91.55999755859375 | 7961400 | 89.9505615234375 | `MARKET_OBSERVABLE_PROXY` | `Close` seulement sous hypothèse ; ne résout pas SPY |

Le contrôle Nasdaq du 20 avril 2026 donne `Open=High=Low=Close=710.14` et
`Volume=N/A`. Il confirme une contradiction, pas la valeur correcte. Aucun autre
fournisseur n'est sélectionné.

### 9.4 Ce que ce contrôle établit

Le petit échantillon confirme que les fichiers, dates, champs et empreintes sont
accessibles et que la transition de régime peut être étiquetée sans transaction. Il
retrouve aussi l'anomalie imposée. Il ne prouve ni la disponibilité exacte du fichier
Yahoo chaque soir, ni les settlement dates effectives, ni l'exécutabilité des opens,
ni l'admissibilité du reste de l'historique.

## 10. Contrat minimal de mappage historique proposé

La provenance `SYNTHETIC` est interdite pour les données réelles. Une future
extension distincte, par exemple `historical_spy_bil_input/v1`, devrait exiger pour
chaque valeur ou événement :

| Groupe | Champs minimaux |
|---|---|
| identité | version du schéma, identifiant stable de l'observation, symbole |
| source | identifiant du manifeste, source, chemin logique, SHA-256, date d'acquisition, version de série |
| temps | date/instant économique, fuseau, instant ou convention de disponibilité, date de publication, date d'acquisition |
| admissibilité | statut point-in-time, identifiant de preuve, statut d'anomalie, motif |
| valeur | champ brut, unité, convention de prix, transformation appliquée |
| calendrier | identifiants/version des calendriers de négociation et de règlement |
| révisions | version d'origine si connue, correction et date de correction, ou indicateur d'absence de preuve |

Le mappage vers l'adaptateur serait bloqué si :

1. le SHA-256 ne correspond pas au manifeste ;
2. une provenance, date économique, disponibilité, transformation ou preuve manque ;
3. le statut est `UNVERIFIED`, `EX_POST_ONLY` pour une décision, ou `DISPUTED` ;
4. un `MARKET_OBSERVABLE_PROXY` n'a pas été explicitement autorisé ;
5. un `Open` entre dans le calcul de la décision ou des quantités ;
6. une NAV ou un `Adj Close` remplace un prix de transaction ;
7. une anomalie est ignorée, un prix est imputé ou une date est interpolée ;
8. la séance ou la settlement date ne possède pas de calendrier applicable ;
9. une distribution n'a pas de `knowledge_at` antérieur à l'usage proposé ;
10. un ajustement de split risque d'être appliqué deux fois.

Ce contrat est une spécification ; aucun connecteur historique, validateur général,
lot de décisions ou boucle temporelle n'est implémenté dans cette phase.

## 11. Lacunes, blocages et décisions à approuver

### 11.1 Lacunes documentaires

- aucune archive quotidienne de la version Yahoo disponible à chaque décision ;
- aucune heure historique de publication des barres quotidiennes ou NAV ;
- aucune date d'annonce dans le fichier de distributions ;
- aucune histoire des modifications de montants de distribution ;
- ratio du split BIL non prouvé avant l'événement par les pièces locales ;
- calendriers de négociation 2018–2021 et 2026 non archivés exhaustivement ;
- heures d'early close et halts par symbole non exhaustifs ;
- avis DTC/NSCC historiques non exhaustifs et settlement dates non toutes prouvées ;
- définition exacte de Yahoo `Open` et anomalie SPY 2026-04-20 non résolues.

### 11.2 Approbations requises

Le porteur doit encore approuver ou rejeter :

1. toute la fiche candidate v1, sans transformer sa présence en adoption ;
2. `H_FIN_NET` ou cash réglé comme convention principale ;
3. l'usage du `Close` Yahoo comme `MARKET_OBSERVABLE_PROXY` ;
4. Yahoo `Open` comme référence hypothétique et le blocage du 20 avril 2026 ;
5. la décision à 08:00:00 ET le jour de la prochaine séance commune ;
6. le niveau de preuve exigé pour annonces de distributions et calendriers ;
7. les statuts admissibles et la politique d'arrêt au premier champ bloquant ;
8. le seuil acceptable de couverture/non-représentabilité avant une expérience ;
9. la version du futur contrat historique et ses règles de révision ;
10. capital, parts, horizon, coûts, cash, risque et compte stylisé.

## 12. Verdict d'admissibilité et prochaine étape

Le verdict est **`PARTIALLY_VERIFIED`** :

- l'intégrité des fichiers et le sens des champs sont suffisamment documentés pour
  un contrôle descriptif ciblé ;
- la règle SEC T+1 et certaines annonces de calendrier/opération sur titres ont une
  preuve de publication point-in-time ;
- les prix actuels restent des proxys, les annonces de distributions manquent et les
  calendriers ne permettent pas une trajectoire historique complète ;
- le cas SPY du 20 avril 2026 reste bloquant et aucune convention n'est approuvée.

Une première intégration financière n'est donc pas encore autorisée. Après
approbation des conventions et qualification documentaire des dates requises, la
plus petite expérience envisageable serait un **seul cycle hebdomadaire
présélectionné**, avec poids fourni hors des données, close admissible, quantités
figées, un open non contesté et une settlement date prouvée. Elle vérifierait
uniquement le passage source → intention → registre, sans rendement, comparaison,
optimisation ou conclusion de performance. Elle exige une autorisation distincte.

Les trois frontières scientifiques restent intactes : série ajustée ne signifie pas
disponibilité passée ; comptabilité valide ne signifie pas exécution réelle ; petit
échantillon conforme ne signifie pas historique complet sans biais.
