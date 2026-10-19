# Audit des prix de marché quotidiens SPY–BIL

**Date de l'audit : 19 octobre 2026**

**Statut scientifique : `AUDITED` — analyse descriptive des OHLCV autorisée sous conventions documentées ; exécution historique non validée**

## 1. Conclusion

Une source commune SPY–BIL a été acquise : les réponses JSON quotidiennes de **Yahoo Finance Historical Data**, du 25 mai 2007 au 16 octobre 2026 pour SPY et du 30 mai 2007 au 16 octobre 2026 pour BIL. Elle contient date/horodatage, open, high, low, close, volume, adjusted close et événements de distribution ou de split.

Le fichier SPY contient 4 880 séances et le fichier BIL 4 878. Leur couverture commune brute et auditée comprend **4 878 séances du 30 mai 2007 au 16 octobre 2026**. Sur la fenêtre prioritaire du 17 octobre 2016 au 16 octobre 2026, les deux ETF et les trois références Nasdaq SPY/IVV/VTI possèdent exactement les mêmes **2 514 dates**.

Les deux fichiers passent les contrôles structurels : aucune date dupliquée ou de week-end, aucune valeur OHLCV manquante, aucun prix non positif, aucun volume négatif ou nul, et aucune violation de `Low ≤ Open, Close ≤ High`. Ces réussites établissent la cohérence interne des fichiers ; elles ne démontrent pas la justesse de chaque observation.

Yahoo indique sur ses pages historiques que `Close` est ajusté des splits et que `Adj Close` est ajusté des splits ainsi que des distributions. L'audit confirme que les OHLC BIL antérieurs au 30 novembre 2017 sont exprimés rétrospectivement sur l'échelle post-split : ils se situent autour de 91 USD alors que la NAV brute est autour de 45,7 USD. Le split `1:2` est correctement présent comme événement. Appliquer une nouvelle correction à la série Yahoo créerait un double ajustement.

La source reste `AUDITED`, et non `VALIDATED_FOR_USE`, pour l'exécution. Yahoo ne documente pas suffisamment si `Open` est le prix de l'enchère principale, le premier échange consolidé ou une autre construction. Les OHLCV peuvent devenir une **référence méthodologique conditionnelle** pour une future hypothèse d'exécution à l'ouverture, mais jamais un prix d'exécution garanti. Les bid/ask, spreads, ordres, profondeur, slippage et impact restent absents.

## 2. Périmètre et niveaux de preuve

La question traitée est :

> Peut-on constituer un historique commun de prix de marché SPY et BIL suffisamment fiable et documenté pour étudier ultérieurement une décision prise après clôture et exécutée à l'ouverture suivante ?

L'audit sépare :

1. **acquisition** : un fichier existe localement avec taille et SHA-256 ;
2. **audit de prix de marché** : structure, calendrier, ajustements et concordances sont contrôlés ;
3. **aptitude à représenter une exécution** : la définition du prix, la liquidité et les conditions d'ordre doivent être suffisantes.

Les deux premiers niveaux sont atteints avec les réserves exposées ci-dessous. Le troisième ne l'est pas.

Aucun portefeuille, rendement de stratégie, backtest, coût calibré, signal ou modèle n'est construit.

## 3. Sources examinées et choix

### 3.1 Nasdaq Historical

Le patrimoine contenait déjà une réponse Nasdaq SPY de 2 514 séances, du 17 octobre 2016 au 16 octobre 2026. Elle est conservée comme référence de contrôle indépendante partielle. Sa réponse contient OHLC et volume, mais ne documente ni ajustements ni distributions et possède une valeur de volume manquante.

La même acquisition a été tentée pour BIL. La [page historique Nasdaq BIL](https://www.nasdaq.com/market-activity/etf/bil/historical) et son API publique ont répondu qu'aucune donnée n'était disponible. Nasdaq ne pouvait donc pas constituer la source commune sans autre produit. L'offre [Nasdaq Data Link](https://www.nasdaq.com/products/data/data-link/api) annonce des barres historiques via des services dédiés, mais leur accès, leurs droits et leur coût n'ont pas été engagés dans cet audit ciblé.

### 3.2 Yahoo Finance — source commune retenue

Yahoo Finance a été retenu parce que :

- SPY et BIL sont disponibles par le même point d'accès et sous le même schéma ;
- la couverture dépasse la fenêtre prioritaire ;
- OHLCV, adjusted close, distributions et splits figurent dans la même réponse ;
- l'acquisition ne nécessitait ni compte, ni contournement, ni donnée intrajournalière massive ;
- la page historique documente au moins les deux principales conventions d'ajustement.

La page [Yahoo Finance SPY Historical Data](https://finance.yahoo.com/quote/SPY/history/) décrit `Close` comme ajusté des splits et `Adj Close` comme ajusté des splits et des distributions. Les [conditions Yahoo](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) encadrent l'accès et la réutilisation. Les fichiers sont donc conservés localement, exclus de GitHub et non redistribués.

Ce choix ne signifie pas que Yahoo est une source officielle de la place de cotation. Le champ `fullExchangeName` vaut `NYSEArca`, mais l'origine exacte des consolidations et la méthode de construction des barres ne sont pas exposées dans la réponse.

### 3.3 State Street et documents réglementaires

Les NAV, premium/discount, distributions, le dépôt SEC et le Form 8937 déjà validés ne servent pas de substitut aux prix. Ils permettent de contrôler :

- l'ordre de grandeur des clôtures par rapport à la NAV ;
- la cohérence des dates de marché ;
- les événements de distribution ;
- le split inversé BIL du 30 novembre 2017.

La NAV et le prix de marché peuvent légitimement différer. Aucune égalité n'est imposée.

## 4. Fichiers réellement acquis

| Instrument | Fichier local | Octets | SHA-256 | Observations |
|---|---|---:|---|---:|
| SPY | `data/raw/rl_market/yahoo_spy_2007-05-25_2026-10-16_acquired-2026-10-19_sha256-b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52.json` | 541 190 | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` | 4 880 |
| BIL | `data/raw/rl_market/yahoo_bil_2007-05-25_2026-10-16_acquired-2026-10-19_sha256-2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2.json` | 522 516 | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` | 4 878 |

Le volume brut acquis est de **1 063 706 octets** pour **9 758 observations instrument-date**. Le rapport déterministe `data/processed/rl/yahoo_spy_bil_market_audit_v1.json` contient les contrôles détaillés ; sa taille est 26 632 octets et son SHA-256 `e33ba4c2b5b962e6f46b7f37853eb73fc5bdc27269456830dbc77fb72274fe89`.

Les octets bruts sont préservés. Le script d'acquisition ne les transforme pas et refuse une collision de nom avec un contenu différent.

## 5. Nature des champs

### 5.1 Métadonnées de réponse

Les deux réponses déclarent :

| Champ | SPY | BIL |
|---|---|---|
| `instrumentType` | ETF | ETF |
| `currency` | USD | USD |
| `exchangeName` | PCX | PCX |
| `fullExchangeName` | NYSEArca | NYSEArca |
| `exchangeTimezoneName` | America/New_York | America/New_York |
| `dataGranularity` | 1d | 1d |

Les timestamps des barres correspondent tous à 09:30 heure locale, avec l'offset saisonnier `-0400` ou `-0500`. Ce timestamp est compatible avec l'ouverture de la séance cœur, mais il peut simplement étiqueter la barre quotidienne : il ne prouve pas que le champ `Open` est le prix de l'enchère.

Les horaires actuels de [NYSE Arca](https://www.nyse.com/trade/hours-calendars) fixent la séance cœur de 09:30 à 16:00 ET et une Core Open Auction à 09:30. Cette documentation actuelle ne suffit pas à attribuer rétroactivement chaque champ Yahoo à cette enchère ni à prouver l'absence de changement historique.

### 5.2 Open, high, low et close

- `Open`, `High`, `Low` et `Close` décrivent une barre quotidienne de marché secondaire selon Yahoo.
- Yahoo indique explicitement que `Close` est ajusté des splits.
- Le comportement de BIL démontre empiriquement que les quatre champs OHLC sont sur une échelle post-split cohérente.
- La réponse ne dit pas si les OHLC proviennent du marché principal, d'un flux consolidé ou d'une sélection de transactions.
- L'inclusion précise des transactions étendues n'est pas documentée. La présence d'un timestamp 09:30 ne résout pas cette question.
- `Close` ne doit pas être confondu avec la NAV, le midpoint bid/ask State Street ou un rendement total.

### 5.3 Adjusted close

`Adj Close` est annoncé comme ajusté des splits, distributions et gains en capital. Il n'est pas un prix historiquement exécutable. Il n'est utilisé dans aucun contrôle d'exécution.

Deux acquisitions successives ont produit les mêmes dates, OHLC, volumes et événements SPY, mais de légères différences dans 3 839 valeurs d'`Adj Close` et dans les métadonnées temps réel. Une seule réponse complète est conservée. Cette observation montre que l'acquisition Yahoo n'est pas nécessairement binaire dans le temps, même lorsque l'OHLC demandé reste stable. L'audit hors ligne du fichier figé est, lui, déterministe.

### 5.4 Volume

Le volume est positif et présent à chaque ligne. Yahoo ne précise pas dans la réponse si les volumes historiques sont rétroactivement ajustés lors d'un split. Le volume ne doit donc pas être transformé ni utilisé pour calibrer une capacité avant preuve supplémentaire.

## 6. Contrôles structurels et OHLC

| Contrôle | SPY | BIL |
|---|---:|---:|
| Dates | 4 880 | 4 878 |
| Ouvertures valides | 4 880 | 4 878 |
| Clôtures valides | 4 880 | 4 878 |
| Doublons | 0 | 0 |
| Dates de week-end | 0 | 0 |
| Valeurs OHLCV manquantes | 0 | 0 |
| Prix non positifs | 0 | 0 |
| Volumes négatifs | 0 | 0 |
| Volumes nuls | 0 | 0 |
| Violations OHLC | 0 | 0 |
| Séances avec `High = Low` | 0 | 11 |
| Plus longue série de clôtures identiques | 2 | 19 |

Les onze barres BIL sans amplitude et les clôtures identiques prolongées sont compatibles avec la faible variation d'un ETF de Treasury bills, surtout pendant les régimes de taux proches de zéro. Elles ne sont pas supprimées. Leur plausibilité économique n'établit toutefois pas à elle seule la qualité transactionnelle de chaque barre.

Les plus fortes variations de clôture SPY correspondent notamment à la crise de 2008, mars 2020 et avril 2025. La plus forte variation absolue BIL est inférieure à 0,45 %. Aucun extrême n'est exclu automatiquement.

## 7. Split inversé BIL du 30 novembre 2017

### 7.1 Événement fournisseur

Yahoo fournit exactement :

```text
date          2017-11-30
splitRatio    1:2
numerator     1
denominator   2
```

Cet événement correspond aux documents SEC et State Street locaux : deux anciennes parts deviennent une nouvelle, soit `q = 0,5` en nombre de parts.

### 7.2 Échelle des prix

| Date | Clôture Yahoo | NAV State Street brute |
|---|---:|---:|
| 2017-11-27 | 91,4600 | 45,738140 |
| 2017-11-28 | 91,5000 | 45,739794 |
| 2017-11-29 | 91,4800 | 45,741272 |
| 2017-11-30 | 91,4800 | 91,488207 |
| 2017-12-01 | 91,4200 | 91,428412 |

Avant le split, `Close Yahoo / NAV brute` est proche de 2 : écart médian d'environ 10 000,8 points de base. En divisant le close Yahoo par deux pour le seul contrôle documentaire, l'écart médian devient 0,39 point de base. Après le split, l'écart médian est 0,68 point de base.

Conclusion : Yahoo a déjà ajusté rétrospectivement les OHLC antérieurs au split. Il ne faut **pas** appliquer de nouveau facteur à cette série pour une analyse continue de prix. Pour reconstituer le prix par ancienne part réellement coté avant le 30 novembre, il faudrait diviser les OHLC antérieurs par deux et résoudre séparément le volume ; aucune série dérivée exécutable n'est publiée ici.

Le registre futur de positions devra, lui, appliquer `q = 0,5` au nombre de parts détenues à l'événement. Ajuster un graphique de prix et transformer les parts réelles sont deux opérations différentes.

### 7.3 Distributions Yahoo autour du split

Les distributions BIL Yahoo antérieures au split sont elles aussi principalement sur une échelle rétrospectivement ajustée : le ratio médian montant Yahoo / montant State Street est proche de 2 avant l'événement, contre 1 après. `Adj Close` et les événements Yahoo ne doivent donc pas alimenter silencieusement le registre comptable State Street déjà validé.

## 8. Calendriers observés

### 8.1 Couverture complète

- SPY commence le 25 mai 2007.
- BIL commence le 30 mai 2007.
- Les seules dates propres à SPY sont les 25 et 29 mai 2007, avant la première observation BIL.
- BIL ne possède aucune date propre.
- La couverture commune contient 4 878 séances du 30 mai 2007 au 16 octobre 2026.

### 8.2 Fenêtre prioritaire

Du 17 octobre 2016 au 16 octobre 2026 :

- Yahoo SPY : 2 514 dates ;
- Yahoo BIL : 2 514 dates ;
- intersection Yahoo : 2 514 dates ;
- intersection Nasdaq SPY/IVV/VTI : 2 514 dates ;
- date propre à un instrument ou un fournisseur : 0.

Le calendrier quotidien observé est donc parfaitement concordant sur cette fenêtre. Les jours de semaine absents de toutes les séries correspondent aux fermetures usuelles et incluent les fermetures exceptionnelles observables du 5 décembre 2018 et du 9 janvier 2025. Ce classement reste empirique : l'absence commune prouve l'absence d'observation, pas à elle seule le motif juridique de fermeture.

Les séances écourtées ne peuvent pas être détectées dans un OHLCV quotidien dépourvu d'heure de clôture. Le site NYSE actuel documente les prochaines fermetures anticipées, mais aucun fichier officiel historique exhaustif 2016–2026 n'a été acquis. Cette lacune est conservée ; aucune séance n'est inventée ou complétée.

Aucun prix n'est interpolé, forward-filled ou remplacé par une NAV.

## 9. Contrôles croisés

### 9.1 SPY Yahoo contre Nasdaq

Les 2 514 dates sont communes. Les corrélations de niveau dépassent 0,999999 pour chaque champ de prix. La médiane des différences est nulle ou voisine de zéro. Cette forte concordance soutient la cohérence générale sans prouver l'indépendance des flux sous-jacents.

Une règle de diagnostic, sans exclusion automatique, signale un écart relatif supérieur à 10 points de base sur au moins un OHLC, ou supérieur à 5 %/manquant sur le volume. Elle marque **39 dates sur 2 514** : 17 alertes d'ouverture, 5 de high, 7 de low, 1 de clôture et 16 de volume, plusieurs champs pouvant être signalés le même jour. Ce décompte mesure des divergences de fournisseurs, pas 39 erreurs Yahoo démontrées.

Des divergences isolées significatives subsistent :

- le 7 novembre 2016, l'ouverture Yahoo vaut 208,55 USD contre 211,45 chez Nasdaq ;
- le 17 mai 2017, l'ouverture Yahoo vaut 240,08 contre 238,10 ;
- le 14 août 2019, le high Nasdaq vaut 292,4644 contre 288,74 chez Yahoo ;
- le 9 mars 2021, les lows diffèrent d'environ 3,58 USD ;
- le 20 avril 2026, Nasdaq publie 710,14 pour les quatre OHLC, alors que Yahoo présente une barre 708,78 / 710,14 / 706,14 / 708,72 ;
- le 17 avril 2026, le volume Nasdaq vaut exactement 9 999 999 contre 70 661 900 chez Yahoo.

Ces cas ressemblent à des anomalies ponctuelles de fournisseur ou à des définitions de flux différentes. Aucun fournisseur n'est corrigé à partir de l'autre, et aucune ligne n'est exclue. Une future étude utilisant une de ces dates devra appliquer une règle d'anomalie prédéfinie ou obtenir une troisième preuve de marché.

### 9.2 Prix Yahoo contre NAV State Street

Sur 4 879 dates SPY communes, l'écart médian `Close/NAV − 1` est de 0,25 point de base ; le maximum absolu est de 161,05 points de base. Sur les 2 230 dates BIL post-split communes, la médiane est de 0,68 point de base et le maximum absolu de 7,01 points de base.

Ces résultats sont compatibles avec deux ETF normalement proches de leur NAV, sans imposer l'égalité. Ils ne valident ni l'open ni la transaction d'un investisseur.

### 9.3 Premium/discount State Street

Sur 448 dates depuis le 2 janvier 2025 :

- pour SPY, l'écart médian entre `Close Yahoo/NAV − 1` et le premium/discount officiel est de 0,00487 point de pourcentage ; le maximum de 0,95361 point survient dans la zone déjà signalée autour du 9 avril 2025 ;
- pour BIL, la médiane est pratiquement nulle et le maximum absolu 0,01638 point.

La comparaison n'est pas une identité attendue : State Street définit son premium/discount à partir du midpoint bid/ask de 16 h et de l'INAV, tandis que Yahoo fournit un close selon sa propre convention.

### 9.4 Distributions

Pour SPY, les 78 dates positives Yahoo concordent avec les 78 dates State Street de la fenêtre ; les écarts de montant sont faibles et attribuables notamment à l'arrondi du fournisseur.

Pour BIL, 127 dates positives sont communes, mais Yahoo contient en plus un événement de 0,022 USD au 1er mars 2022, alors que State Street enregistre explicitement un montant nul. Cette contradiction est conservée. Les distributions State Street validées restent la référence comptable ; les événements Yahoo ne sont utilisés ici que pour auditer le fournisseur.

## 10. Couvertures et usages réellement défendables

| Niveau | Couverture | Séances | Verdict |
|---|---|---:|---|
| Brute commune Yahoo | 2007-05-30–2026-10-16 | 4 878 | acquise |
| Audit structurel split-adjusted | 2007-05-30–2026-10-16 | 4 878 | cohérent, avec anomalies documentées |
| Fenêtre prioritaire commune | 2016-10-17–2026-10-16 | 2 514 | calendriers identiques aux références Nasdaq |
| Échelle historique directement comparable au prix par part BIL courant | 2017-11-30–2026-10-16 | 2 231 BIL | pas de conversion pré-split nécessaire |
| Référence future d'ouverture | au plus la couverture auditée | — | conditionnelle à une hypothèse explicite |
| Exécution garantie | aucune | 0 | non démontrée |

La fenêtre 2007–2026 peut servir à l'analyse descriptive de séries **split-adjusted**. Pour une future comptabilité exprimée aux prix réellement cotés par part, la période antérieure au split BIL exige une dérivation documentée des OHLC et une décision sur le volume. La solution la plus prudente sans nouvelle validation commence le 30 novembre 2017.

Cette conclusion ne choisit aucune période d'entraînement, de validation, de test ou de backtest.

## 11. Aptitude à une référence d'exécution à l'ouverture

### 11.1 Ce qui est acquis

- un champ `Open` quotidien complet et commun ;
- des dates cohérentes avec NYSE Arca et avec les trois références Nasdaq sur la fenêtre prioritaire ;
- une devise, un fuseau et une granularité explicites ;
- un traitement du split BIL identifiable ;
- des contrôles indépendants partiels sur SPY et des contrôles NAV pour les deux ETF.

### 11.2 Ce qui n'est pas démontré

- que l'open Yahoo est le prix officiel de la Core Open Auction ;
- qu'un ordre market-on-open aurait été accepté avant le cut-off et entièrement exécuté à ce prix ;
- qu'une quantité donnée trouvait assez de liquidité ;
- le bid, l'ask, le spread et la profondeur disponibles ;
- le slippage, l'impact, les interruptions ou exécutions partielles ;
- les règles du courtier et les fractions de parts ;
- l'heure exacte de clôture lors des séances écourtées.

Le statut approprié est donc :

> **Référence quotidienne de marché auditée, conditionnellement utilisable dans un futur protocole comme approximation de l'ouverture, mais non validée comme prix d'exécution garanti.**

Une future simulation devrait nommer explicitement l'hypothèse « exécution au champ Open Yahoo », limiter la taille à un preneur de prix, appliquer une règle de non-exécution et séparer les coûts. Elle ne peut pas présenter le résultat comme une reconstruction de fills réels.

## 12. Reproductibilité et conservation

Les commandes sont :

```powershell
python RL/scripts/acquire_yahoo_spy_bil_ohlcv.py
python RL/scripts/audit_spy_bil_market_prices.py
python RL/scripts/verify_local_data.py
```

L'acquisition dépend de la disponibilité Yahoo et peut produire des métadonnées dynamiques ou de petites révisions de l'adjusted close. Les fichiers figés sont identifiés par SHA-256. L'audit hors ligne produit de façon déterministe le même rapport à partir des mêmes entrées.

Les deux fichiers bruts et le rapport dérivé ont été copiés sous `D:\ai-financial-risk-reliability-data-backup\2026-10-19\` en conservant leur chemin relatif. Les trois empreintes de sauvegarde correspondent aux originaux.

Les fichiers `data/raw/` et `data/processed/` restent exclus de Git. Seuls les scripts, le manifeste et la documentation sont publiables.

## 13. Réponses A–I

**A. Source retenue.** Yahoo Finance Historical Data est la source commune, car elle offre le même schéma OHLCV et les événements pour les deux ETF sur toute la fenêtre. Nasdaq reste le contrôle SPY ; son historique BIL public était indisponible.

**B. Quantité et période.** Deux JSON, 1 063 706 octets, 9 758 observations. SPY couvre 2007-05-25–2026-10-16 ; BIL et la couverture commune couvrent 2007-05-30–2026-10-16 avec 4 878 séances.

**C. Ajustements.** Les OHLC sont sur une base ajustée des splits ; `Adj Close` ajoute les distributions. Les champs ne sont pas des prix bruts pré-split ni un rendement total directement exécutable. Le volume est conservé tel quel, sa convention de split restant non documentée.

**D. Split BIL.** L'événement `1:2` du 30 novembre 2017 concorde avec SEC/State Street et les OHLC antérieurs sont déjà multipliés par deux. Aucun second ajustement n'est appliqué.

**E. Anomalies et limites.** Divergences ponctuelles Yahoo/Nasdaq sur certains OHLC et volumes, événement BIL Yahoo erroné ou incompatible au 1er mars 2022, définition de l'open insuffisante, adjusted close non stable bit à bit, volume autour du split non documenté et absence de calendrier officiel exhaustif des séances écourtées.

**F. Couverture exploitable.** 4 878 séances communes pour l'analyse split-adjusted ; 2 514 sur la fenêtre prioritaire. Pour une échelle directement comparable aux parts BIL historiques sans reconstruction pré-split, la fenêtre prudente commence le 30 novembre 2017.

**G. Validation des prix de marché.** Les fichiers restent `AUDITED`. Ils sont autorisés pour l'analyse descriptive locale des OHLCV sous convention Yahoo, pas pour un backtest net ou une exécution garantie.

**H. Référence d'ouverture.** Oui, conditionnellement, comme approximation méthodologique nommée et accompagnée de ses limites. Non, si « référence » signifie enchère officiellement identifiée ou fill assuré.

**I. Plus petites étapes restantes.** Obtenir la définition contractuelle ou officielle des barres d'ouverture, un calendrier historique des séances écourtées, résoudre les quelques divergences OHLC significatives par une troisième source ciblée, définir le traitement pré-split du prix/volume BIL, puis choisir les règles du courtier. Un lot NBBO ne devient nécessaire que si le spread doit être estimé empiriquement.

## 14. Règle d'arrêt

Cet audit n'autorise aucun portefeuille, backtest, simulation de trading, coût calibré, allocation, optimisation, modèle prédictif ou agent RL. Aucune série NAV existante ni donnée brute antérieure n'a été modifiée. Toute comptabilité de portefeuille négociable constitue une phase distincte soumise à validation explicite.
