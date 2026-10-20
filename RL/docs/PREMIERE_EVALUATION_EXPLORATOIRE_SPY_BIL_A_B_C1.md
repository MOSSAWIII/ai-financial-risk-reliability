# Première évaluation exploratoire SPY–BIL — A, B et C1

Date : 20 octobre 2026

Point de départ : `b490951f497cabc4fbe88fd708824209a78ae37a`

Verdict : **`EXPLORATORY_EVALUATION_VALIDATED`**

## 1. Question financière étudiée

Cette expérience compare, sur un seul épisode fixé avant calcul, trois décisions
initiales sans réallocation ultérieure : acheter et conserver SPY (A), acheter et
conserver BIL (B), ou acheter une allocation initiale 50 % SPY / 50 % BIL puis
laisser ses poids dériver (C1).

La question est descriptive : comment richesse, rendement, risque, cash et
exposition ont-ils différé sous ces trois décisions et les mêmes conventions ?
Elle ne recherche pas la meilleure politique et ne teste ni C2, ni règle dynamique,
ni modèle prédictif, ni reinforcement learning.

## 2. Protocole et dates préspécifiées

Le fixture
[`exploratory_buy_hold_spy_bil_v1.json`](../tests/fixtures/exploratory_buy_hold_spy_bil_v1.json)
a pour SHA-256
`8e29d00bb669c6ddb10556d721f828b31174e2c1d5aa5a6d4641a90f65cefcd0`.
Il fixe avant l'évaluation :

- close de décision : 28 mai 2024 ;
- décision : 29 mai 2024 à 08:00 `America/New_York` ;
- achat initial hypothétique : open du 29 mai 2024 ;
- règlement initial : 30 mai 2024 ;
- anniversaire et terminal effectivement commun : close du 29 mai 2025 ;
- aucun apport, réinvestissement, nouvel ordre ou liquidation terminale.

L'épisode réemploie le cycle initial déjà validé ; il n'a pas été choisi après
observation de son rendement. Cette période et ses données ont néanmoins déjà été
consultées par le projet : l'évaluation est exploratoire, non confirmatoire.

## 3. Sources et empreintes

| Usage | Identifiant du manifeste | SHA-256 |
|---|---|---|
| prix SPY | `yahoo_spy_chart_ohlcv_20261019` | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| prix BIL | `yahoo_bil_chart_ohlcv_20261019` | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| audit des prix | `yahoo_spy_bil_market_audit_v1_20261019` | `e33ba4c2b5b962e6f46b7f37853eb73fc5bdc27269456830dbc77fb72274fe89` |
| distributions | `ssga_spdr_distributions_20261019` | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| règle SEC T+1 | `sec_settlement_cycle_t1_2023_20261019` | `e214bf80244fe9107c867d7abeb6a6b969029c519566036e42b081977a9b575a` |
| calendrier initial DTCC | `dtcc_t1_conversion_guide_may2024_20261020` | `1655962c57e5a1459cf0d29c853b0bf924c3255aba5be0e0d04c4a7d2536b7f2` |

Le composant vérifie taille et empreinte de chaque fichier contre le manifeste
avant lecture. Aucun fichier brut n'est publié ou modifié. Les prix Yahoo restent
des `MARKET_OBSERVABLE_PROXY`, pas des fills ni des versions archivées chaque jour.

## 4. Conventions comptables et mesures

Chaque référence reçoit son propre registre avec 100 000 USD de cash réglé,
`strict_temporal=True`, parts entières, frais externes nuls et `H_FIN_NET`. Comme
les achats partent exclusivement du cash initial, l'expérience ne valide pas le
financement croisé vente–achat.

Les quantités sont calculées aux closes du 28 mai puis scellées avant les opens du
29 mai. Le lot initial est atomique. Le cash résiduel et les distributions payées
restent non rémunérés ; aucune part supplémentaire n'est acquise.

La richesse économique est :

\[
W_t=q_{SPY}P_{SPY,t}+q_{BIL}P_{BIL,t}+C_t+A_t
+U_t^{vente}-U_t^{achat}.
\]

La base vaut 100 000 USD aux prix d'exécution hypothétiques de l'open. Le premier
rendement va de cet open au close du même jour ; les suivants sont calculés de
close commun à close commun. La trajectoire comporte 251 closes et 252 points avec
la base d'entrée. La volatilité est l'écart-type échantillonnal des 251 rendements,
annualisé par `sqrt(252)`. Le rendement annualisé composé emploie 365 jours ; ici,
l'épisode dure exactement 365 jours, donc il égale le rendement total.

Le drawdown est calculé sur la richesse complète depuis la base d'entrée. Sa durée
compte les observations de valorisation sous le dernier sommet ; un drawdown non
récupéré au terminal est signalé ouvert. Le « cash moyen » désigne le cash net des
dettes d'achat avant règlement, puis le cash réglé, calculé sur les 252 points.

## 5. Couverture documentaire

Le 29 mai 2025 est présent dans les deux séries ; aucune date de remplacement n'est
nécessaire. Les 251 dates de close sont communes à SPY et BIL. Aucune alerte de
l'audit Yahoo–Nasdaq ne tombe dans la fenêtre et aucun split Yahoo n'y apparaît.

State Street fournit quatre distributions SPY et douze BIL entre l'entrée et le
terminal, avec ex-date, record date, payment date et montant. Leurs ex-dates et
leurs montants arrondis au millième concordent avec les événements Yahoo. Tous les
paiements interviennent avant le terminal. Aucune preuve de date d'annonce n'est
inventée.

Le règlement T+1 du seul achat, du 29 au 30 mai 2024, réutilise la preuve SEC/DTCC
déjà validée. Aucun ordre ultérieur n'exige un nouveau calendrier de règlement.
Les jours sans transaction requièrent seulement une valorisation sur les séances
communes observées, pas une preuve artificielle de settlement.

## 6. Positions initiales

Les closes de décision sont `529.8099975585938` USD pour SPY et
`91.76000213623047` USD pour BIL. Les opens d'exécution sont respectivement
`525.6799926757812` et `91.7699966430664` USD.

| Référence | Parts SPY | Parts BIL | Coût à l'open (USD) | Cash résiduel (USD) | Poids obtenus SPY / BIL / cash |
|---|---:|---:|---:|---:|---:|
| A | 188 | 0 | 98 827,8386 | 1 172,1614 | 98,8278 % / 0 % / 1,1722 % |
| B | 0 | 1 089 | 99 937,5263 | 62,4737 | 0 % / 99,9375 % / 0,0625 % |
| C1 | 94 | 544 | 99 336,7975 | 663,2025 | 49,4139 % / 49,9229 % / 0,6632 % |

Les trois lots sont acceptés sans redimensionnement. A et B comportent un ordre ;
C1 en comporte deux. Ils sont réglés le 30 mai sans variation artificielle de
richesse. Aucun rejet économique n'est observé.

## 7. Trajectoire de richesse et distributions

À chaque ex-date, le registre crée une créance égale aux parts détenues multipliées
par le montant State Street. À la payment date, cette créance devient cash à valeur
identique. Le transfert est neutre pour la richesse ; seul l'acquisition du droit
et le mouvement des prix peuvent la modifier.

Une petite voie comptable distincte,
`accrue_realized_distribution()`, a été ajoutée au registre. Elle marque
explicitement l'événement `EX_POST_ACCOUNTING_ONLY`, n'enregistre aucune annonce
historique fictive, refuse un identifiant déjà traité et interdit à l'adaptateur de
préparer une décision après son utilisation.

| Référence | Droits positifs | Contribution SPY (USD) | Contribution BIL (USD) | Total distributions (USD) |
|---|---:|---:|---:|---:|
| A | 4 | 1 347,138628 | 0 | 1 347,138628 |
| B | 12 | 0 | 4 672,789011 | 4 672,789011 |
| C1 | 16 | 673,569314 | 2 334,249056 | 3 007,818370 |

Les montants sont conservés en cash. La hausse progressive du cash explique que
les expositions investies diminuent même sans vente. Les closes terminaux sont
`590.0499877929688` USD pour SPY et `91.70999908447266` USD pour BIL.

## 8. Résultats de rendement et de risque

Les calculs utilisent les valeurs non arrondies ; le tableau est arrondi pour la
lecture.

| Référence | Richesse terminale (USD) | Rendement total / annualisé | Volatilité annualisée | Pire jour | Drawdown maximal | Durée max | Ouvert au terminal |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 113 448,70 | 13,4487 % | 19,9800 % | -5,7117 % | -18,3714 % | 69 séances | oui |
| B | 104 607,45 | 4,6075 % | 0,2222 % | -0,0107 % | -0,0107 % | 1 séance | non |
| C1 | 109 025,96 | 9,0260 % | 10,0222 % | -2,8324 % | -9,5138 % | 69 séances | oui |

Ces nombres décrivent un épisode brut de coûts externes. Ils ne mesurent ni spread,
slippage, impact, fiscalité ni qualité réelle de fill à l'open.

## 9. Comparaison de structure et d'exposition

| Référence | Exposition SPY moyenne | Min–max SPY aux closes | Poids terminaux SPY / BIL / cash | Cash moyen / terminal (USD) |
|---|---:|---:|---:|---:|
| A | 98,2365 % | 97,3718–98,8760 % | 97,7793 % / 0 % / 2,2207 % | 1 778,14 / 2 519,30 |
| B | 0 % | 0–0 % | 0 % / 95,4733 % / 4,5267 % | 2 622,48 / 4 735,26 |
| C1 | 50,6317 % | 46,6915–52,2428 % | 50,8729 % / 45,7600 % / 3,3671 % | 2 245,02 / 3 671,02 |

Les quantités restent exactement 188/0, 0/1 089 et 94/544 après l'achat initial.
Les mouvements de poids proviennent exclusivement des prix et de l'accumulation de
cash. Il n'existe aucun rééquilibrage caché, rachat de distribution ou liquidation.

## 10. Mécanismes expliquant les différences

Sur cet épisode, A bénéficie entièrement de la hausse de SPY et termine avec la
richesse la plus élevée. Ce résultat a exigé l'exposition actions la plus forte et
s'accompagne aussi de la volatilité, du pire jour et du drawdown les plus élevés.

B transforme principalement les distributions mensuelles de BIL en cash. Il offre
la trajectoire la plus stable, mais participe peu à la hausse de SPY ; cette faible
exposition constitue simultanément son mécanisme défensif et son coût d'opportunité
sur la période.

C1 combine dès l'origine les deux sources de richesse. Sans rééquilibrage, sa part
SPY dérive avec les prix ; elle n'est donc pas une cible 50/50 maintenue. Ses
résultats intermédiaires proviennent de cette allocation initiale, de la
diversification, des distributions des deux ETF et du cash non réinvesti. Dans
cette seule réalisation, son rendement, sa volatilité et son drawdown se situent
entre ceux des deux expositions extrêmes ; ce n'est pas une loi générale.

## 11. Limites scientifiques

- Un seul épisode déjà exploré ne fournit ni validation indépendante, ni mesure de
  robustesse, ni inférence sur d'autres régimes.
- Les proxys Yahoo ont été acquis en 2026 et ne sont ni des fills garantis ni des
  archives quotidiennes point-in-time.
- Les événements réalisés peuvent mesurer ex post la richesse d'une politique sans
  nouvelle décision ; leurs dates d'annonce restent inconnues et ne pourraient pas
  alimenter une règle dynamique.
- Les coûts externes sont nuls par convention théorique, pas par observation.
- La conservation du cash de distribution, les parts entières et l'absence de
  liquidation influencent les résultats.
- BIL est un ETF investi, pas du cash rémunéré ni un actif parfaitement sans risque.
- Le drawdown terminal de A et C1 est encore ouvert : sa durée future est inconnue.
- Les résultats ne sont ni une recommandation d'investissement, ni une preuve que
  A, B ou C1 serait supérieure.

## 12. Décision recommandée pour la phase suivante

L'expérience valide la chaîne minimale « position initiale → règlement →
distributions → richesse → mesures » pour A, B et C1. Elle montre aussi pourquoi
rendement et risque doivent être lus conjointement : la meilleure richesse observée
coïncide ici avec l'exposition et le drawdown les plus élevés.

La prochaine étape minimale n'est pas C2. Elle consiste à soumettre cette première
comparaison et ses conventions à validation scientifique, puis à préspécifier une
sensibilité commune aux coûts d'exécution. Cette sensibilité devra fixer ses
hypothèses avant tout nouveau calcul et rester sur le même épisode si elle est
autorisée. Aucun nouvel épisode, rééquilibrage ou modèle ne découle automatiquement
du présent résultat.
