# Cohérence comptable de SPY et BIL

## 1. Question financière et périmètre

La question traitée est étroite : **SPY et BIL peuvent-ils être représentés par les mêmes règles de détention — parts, NAV, cash et distributions à recevoir — sans assimiler cette représentation à un portefeuille négociable ?**

Ce travail ne construit ni portefeuille, ni stratégie, ni backtest. Il ne modifie pas les séries antérieures. Il distingue quatre objets :

- **SPY-A et BIL-A** : distributions attribuées et réinvesties conventionnellement à l'ex-date ;
- **SPY-B et BIL-B** : droit acquis à l'ex-date, créance jusqu'au paiement, puis réinvestissement à la NAV de la date de paiement ;
- **comptabilité commune** : règles permettant de suivre deux instruments dans un même référentiel ;
- **exécution** : transactions réellement possibles à des prix de marché, non validées ici.

Deux conventions de rendement peuvent être chacune cohérentes pour un usage donné sans produire exactement la même performance. La cohérence commune recherchée porte sur les événements économiques, pas sur l'égalité artificielle de deux indices préconstruits.

## 2. Preuves documentaires et distributions BIL

La source State Street de distributions contient 232 lignes BIL entre le 2 juillet 2007 et le 1er octobre 2026 : 127 montants positifs et 105 montants nuls. Aucune date n'est absente. Une seule ligne a une chronologie impossible :

| Ex-date | Record date | Payment date | Montant USD/part |
|---|---|---|---:|
| 2008-03-03 | 2008-02-05 | 2008-02-11 | 0,086739 |

Les record et payment dates reproduisent celles de la distribution précédente du 1er février 2008. Ce motif rend plausible une erreur de publication, mais ne démontre ni la date fautive ni sa correction.

Deux nouveaux documents primaires sont conservés localement, hors Git, avec taille et SHA-256 dans `RL/data_manifest.json` :

1. Le [Form 485BPOS du SPDR Series Trust déposé à la SEC le 28 octobre 2008](https://www.sec.gov/Archives/edgar/data/1064642/000095013508006743/b72723a1e485bpos.txt) inclut explicitement le « SPDR Lehman 1-3 Month T-Bill ETF » et indique que les distributions sont réinvesties à la NAV aux dates de paiement respectives des fonds. Il établit la convention historique du Trust, mais ne donne pas les dates de l'événement de mars 2008.
2. Le [calendrier 2026 des distributions SPDR](https://www.ssga.com/library-content/products/fund-data/etfs/us/distribution/SPDR_Dividend_Distribution_Schedule.pdf) définit ex-date, record date et payable date et place BIL dans un calendrier mensuel actuel. Il ne permet pas de reconstruire une date de 2008.

Les archives SEC pertinentes de 2007–2009 ont été examinées sans trouver de document primaire donnant la record date et la payment date exactes de l'événement du 3 mars 2008. Des calendriers secondaires suggèrent des dates mensuelles plausibles, mais ils ne sont pas une preuve suffisante. **L'anomalie n'est donc pas résolue, aucune valeur brute n'est corrigée et aucun paiement n'est inventé.**

Les 105 lignes à montant nul restent dans la source et dans l'audit du calendrier. Elles ne créent ni créance, ni cash, ni rendement dans BIL-B, car leur effet économique est exactement nul.

## 3. Comptabilité commune

Pour les instruments (i\in\{SPY,BIL\}), la richesse de clôture est

\[
W_t=\sum_i n_{i,t}N_{i,t}+C_t+A_t,
\]

où (n_{i,t}) est le nombre de parts, (N_{i,t}) la NAV, (C_t) le cash disponible et (A_t=\sum_j a_{j,t}) les créances acquises mais non payées.

### 3.1 Ex-date

Pour une distribution (D_{i,k}) et les parts déjà détenues (n_{i,t}^{-}), une créance est créée :

\[
a_{i,k,t}=n_{i,t}^{-}D_{i,k},\qquad A_t^{+}=A_t^{-}+a_{i,k,t}.
\]

Cette écriture représente le droit acquis. Elle ne suppose pas que la baisse de NAV observée soit exactement égale à la distribution.

### 3.2 Paiement puis réinvestissement

Au paiement d'une créance (a),

\[
A_t^{+}=A_t^{-}-a,\qquad C_t^{+}=C_t^{-}+a.
\]

Le transfert conserve la richesse : (Delta(C_t+A_t)=0). Si le cash est ensuite réinvesti à la NAV (N_{i,t}),

\[
n_{i,t}^{+}=n_{i,t}^{-}+\frac{C_t^{-}}{N_{i,t}},\qquad C_t^{+}=0,
\]

et (n_{i,t}^{+}N_{i,t}+C_t^{+}=n_{i,t}^{-}N_{i,t}+C_t^{-}). Le paiement et le réinvestissement sont donc des transferts internes, pas des gains supplémentaires.

### 3.3 Regroupement de parts

Pour un facteur (q) exprimé en parts nouvelles par part ancienne,

\[
n_{i,t}^{+}=q n_{i,t}^{-},\qquad N_{i,t}^{+}=\frac{N_{i,t}^{-}}{q}.
\]

Alors (n_{i,t}^{+}N_{i,t}^{+}=n_{i,t}^{-}N_{i,t}^{-}). Pour le regroupement BIL du 30 novembre 2017, (q=0{,}5) : deux anciennes parts deviennent une nouvelle part. Une créance déjà acquise est un montant monétaire ; elle reste inchangée pendant le regroupement.

### 3.4 Frontières de période

- Un investisseur qui entre le jour d'une ex-date n'est pas réputé posséder un droit antérieur : les événements de date égale ou antérieure au début sont exclus.
- Une créance acquise pendant la période mais non payée à la fin reste incluse dans (A_T).
- Si ex-date et paiement coïncident, la créance est créée puis transférée et réinvestie le même jour, une seule fois.
- Une payment date absente ou antérieure à l'ex-date est refusée.

Ces conventions sont nécessaires pour que le rapport de richesse d'un nouvel investisseur ne récupère pas une créance acquise avant son entrée.

## 4. Construction et couverture de BIL-B

Le script `RL/scripts/reconstruct_bil_payment_date_returns.py` réutilise le mécanisme de détention éprouvé pour SPY-B sans modifier ce dernier. Il produit séparément :

- `data/processed/rl/bil_nav_total_returns_payment_date_v1.csv` ;
- `data/processed/rl/bil_payment_date_validation_v1.json`.

La couverture commence le **4 mars 2008**, première NAV strictement postérieure à l'ex-date ambiguë. Un investisseur entrant à cette date n'a aucun droit sur la distribution détachée le 3 mars ; l'absence de payment date fiable pour cette distribution ne contamine donc pas son registre. Toute construction qui commencerait avant ou inclurait le droit du 3 mars reste bloquée.

La série comprend 4 688 jours de NAV jusqu'au 15 octobre 2026, sans doublon ni date ajoutée. Elle traite 118 distributions positives postérieures à la frontière et le regroupement du 30 novembre 2017. Le solde final de cash et de créances est nul.

## 5. Tests comptables et contrôles historiques

Les tests synthétiques vérifient :

- une créance acquise puis payée ;
- une créance impayée en fin de période ;
- l'exclusion d'un droit détaché avant l'entrée ;
- plusieurs créances simultanées ;
- l'absence d'effet d'une distribution nulle ;
- le regroupement de deux parts en une ;
- l'invariance d'une créance monétaire pendant un regroupement ;
- une ex-date et un paiement le même jour ;
- le rejet d'une payment date absente ou incohérente ;
- l'absence de double comptage.

Tous passent. Sur les données historiques :

- erreur maximale de l'identité de richesse : (3{,}55\times10^{-15}) USD ;
- erreur maximale d'un transfert créance–cash–parts : (7{,}11\times10^{-15}) USD ;
- erreur de solde cumulé des créances : (3{,}55\times10^{-15}) USD ;
- 12,3946273263 USD de créances cumulées créées par la part initiale, intégralement payées et réinvesties à l'arrondi numérique près.

Ces montants cumulés dépendent de l'évolution des parts fractionnaires du détenteur ; ils ne sont pas la somme brute des distributions par part.

## 6. Comparaison aux performances officielles

Les références sont les performances NAV State Street au 30 septembre 2026. La tolérance préexistante reste 0,01 point de pourcentage.

| Fenêtre | Officiel | BIL-A ex-date | Écart A | BIL-B paiement | Écart B | Effet B−A |
|---|---:|---:|---:|---:|---:|---:|
| 1 an, 2025-09-30–2026-09-30 | 3,661900 % | 3,663486 % | +0,001586 pp | 3,661849 % | −0,000051 pp | −0,001637 pp |
| 10 ans annualisés, 2016-09-30–2026-09-30 | 2,293200 % | 2,294479 % | +0,001279 pp | 2,293176 % | −0,000024 pp | −0,001302 pp |

BIL-A et BIL-B passent toutes deux la tolérance. BIL-B est plus proche sur ces deux fenêtres, ce qui est cohérent avec la convention de paiement documentée par le dépôt SEC. Ce résultat ne prouve pas que chaque date historique est exacte : la page officielle, la NAV et les distributions proviennent du même émetteur, et les fenêtres commencent en 2016 ou 2025. Elles ne valident donc pas l'événement de 2008.

BIL-A reste utile comme indice conventionnel attribuant la distribution à l'ex-date. BIL-B représente plus directement le registre prospectif d'un détenteur dont le droit reste une créance jusqu'au paiement. Le faible écart observé ne rend pas les conventions interchangeables.

## 7. Compatibilité SPY–BIL et statuts

| Objet | Période | Statut | Usage établi |
|---|---|---|---|
| SPY-A | 2003-12-01–2026-10-15 | `AUDITED` | rendement NAV conventionnel à l'ex-date |
| BIL-A | 2007-05-30–2026-10-15 | `VALIDATED_FOR_USE` | rendement NAV conventionnel à l'ex-date |
| SPY-B | 2003-12-01–2026-10-15 | `VALIDATED_FOR_USE` | détention, créances et paiement à la NAV |
| BIL-B | 2008-03-04–2026-10-15 | `VALIDATED_FOR_USE` | détention, créances, paiement et regroupement à la NAV |

À partir du 4 mars 2008, SPY-B et BIL-B sont **compatibles pour une représentation comptable commune à la NAV** : même définition de richesse, même séparation cash/créances, même règle d'acquisition et de paiement, même valorisation de fin de période. Leurs calendriers et opérations propres peuvent différer sans rompre ce référentiel.

Cette compatibilité n'élève pas automatiquement la paire au statut de données de portefeuille validées. Les usages conjoints de portefeuille, d'exécution ou de backtest restent `AUDITED` ou non validés selon le fichier concerné. En particulier, additionner ou pondérer mécaniquement deux indices de rendement total préconstruits peut être faux : le droit à une distribution dépend du nombre réel de parts détenues à l'ex-date, lui-même dépendant des décisions et transferts antérieurs.

## 8. Conditions avant un portefeuille négociable

Une étude ultérieure nécessiterait une autorisation distincte et, au minimum :

1. un registre conjoint actualisant directement les parts SPY/BIL, les créances et le cash après chaque décision ;
2. une convention d'ordre intrajournalier entre décision, opération sur titres, paiement et valorisation ;
3. des prix d'exécution validés, distincts des NAV, avec horaires et calendriers compatibles ;
4. les règles de fractionnement des parts lors des transactions et les contraintes de parts fractionnaires ;
5. des coûts, spreads, délais de règlement, fiscalité et contraintes de liquidité explicitement choisis et justifiés ;
6. une disponibilité point-in-time des informations utilisées ;
7. des contrôles de conservation lors de chaque transfert et une définition de la performance nette.

Aucun de ces éléments n'est construit ici. La conclusion acquise est comptable : **un même langage de richesse peut représenter SPY et BIL à la NAV à partir du 4 mars 2008**. Elle n'est ni une preuve d'exécutabilité, ni une validation de stratégie.
