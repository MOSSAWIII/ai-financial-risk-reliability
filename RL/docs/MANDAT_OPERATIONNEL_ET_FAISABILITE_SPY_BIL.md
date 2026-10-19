# Mandat opérationnel candidat et faisabilité empirique — SPY/BIL

**Date : 19 octobre 2026**

**Statut : cadrage méthodologique ; mandat candidat non autorisé pour une expérience**

## 1. Conclusion exécutive

La décision financière proposée est une réallocation périodique d'une poche de capital entre **SPY**, exposition au marché actions américain, et **BIL**, exposition aux bons du Trésor américain de très courte maturité. Le gestionnaire est un preneur de prix, long-only, sans levier ni vente à découvert. Son objectif économique est la croissance composée de la richesse nette des coûts, sous des contraintes explicites d'exposition et, si le porteur du projet le confirme, un budget de risque ex ante distinct de l'objectif.

Le mandat candidat principal est une décision **hebdomadaire après la clôture de la dernière séance de la semaine**, exécutée à l'ouverture de la séance suivante. Cette convention permet d'utiliser les informations de clôture sans exécution rétroactive au même prix. Un horizon économique fini d'un an, soit environ 52 décisions, est proposé comme unité d'étude interprétable ; il n'est ni calibré ni adopté.

Le patrimoine actuel permet de représenter correctement la détention de SPY-B et BIL-B à la NAV depuis le 4 mars 2008, avec parts, cash et distributions à recevoir. Il ne permet pas de représenter des transactions historiques communes : SPY possède un OHLCV local audité seulement du 17 octobre 2016 au 16 octobre 2026 ; BIL n'a aucun OHLCV local ; aucun historique local de bid/ask ou de NBBO n'est acquis. Il n'existe donc, à ce jour, **aucune période autorisée pour un backtest négociable SPY–BIL**.

La plus petite étape empirique suivante serait un audit ciblé, sans portefeuille, d'une source commune de prix de marché SPY et BIL — ouverture, clôture et volume — accompagnée du calendrier de séances, des opérations sur titres et des définitions d'ajustement. Un historique de quotes/NBBO serait en outre nécessaire pour estimer empiriquement le spread. Cette acquisition exige une validation explicite avant d'être engagée.

## 2. Statut des éléments mobilisés

Le présent rapport ne rouvre pas les résultats déjà établis. Il utilise quatre catégories.

### 2.1 Scientifiquement établi ou validé dans le projet

- Une répétition de décisions n'est pas, à elle seule, un problème séquentiel. Une action doit modifier une variable qui influence la valeur ou la faisabilité d'une décision future.
- La position héritée, les coûts de rotation, les créances de distribution, la trésorerie et certaines contraintes peuvent créer cette interdépendance.
- SPY-B est `VALIDATED_FOR_USE` pour le rendement total à la NAV sous une comptabilité de détention, de créances et de réinvestissement au paiement.
- BIL-B est `VALIDATED_FOR_USE` pour le même usage limité du 4 mars 2008 au 15 octobre 2026.
- SPY-B et BIL-B peuvent être représentés dans le référentiel commun

  \[
  W_t^{NAV}=\sum_i n_{i,t}N_{i,t}+C_t+A_t.
  \]

- Cette compatibilité comptable ne valide ni des prix d'exécution, ni des coûts externes, ni la combinaison mécanique des deux indices en portefeuille.

### 2.2 Propositions de ce rapport

- Le gestionnaire représente une poche actions à risque contrôlé d'un investisseur final, sans statut réglementaire institutionnel supposé.
- L'univers reste limité à SPY et BIL, avec un reliquat de cash non stratégique.
- La décision est révisable chaque semaine après la clôture, puis exécutée à l'ouverture suivante.
- L'horizon candidat est un an et l'objectif principal porte sur la richesse terminale nette des coûts.
- Les ordres portent par défaut sur des parts entières ; le reliquat reste en cash. Une convention de parts fractionnaires ne pourrait être retenue qu'après choix d'un courtier et validation de ses règles d'exécution historiques.

### 2.3 Éléments restant à vérifier

- Une série cohérente de prix d'ouverture et de clôture pour **les deux** ETF.
- La définition exacte et les ajustements des prix de marché acquis.
- Un calendrier historique des séances, séances écourtées et interruptions.
- Des quotes bid/ask ou NBBO historiques si le spread doit être estimé plutôt que traité par scénarios.
- Les conditions du courtier : commissions, fractions de parts, utilisation des produits de vente non réglés et types d'ordres.
- La disponibilité point-in-time de toute information utilisée par une future règle de décision.

### 2.4 Décisions appartenant au porteur du projet

- Accepter ou réviser le profil du gestionnaire, la fréquence hebdomadaire et l'horizon d'un an.
- Décider si le budget de volatilité est une contrainte ex ante, une cible ou seulement un indicateur.
- Fixer la richesse initiale, indispensable si les parts sont entières.
- Choisir le cadre de compte et le traitement fiscal.
- Autoriser l'acquisition ciblée des données manquantes puis, séparément, une future expérience.

## 3. Décision financière étudiée

### 3.1 Gestionnaire et mandat économique

Le décideur candidat est le gestionnaire d'une poche autonome de capital libellée en USD. Il cherche à participer à la croissance de long terme du marché actions, tout en pouvant réduire l'exposition risquée lorsque les informations disponibles indiquent que le risque est incompatible avec le mandat. Il ne gère ni passif actuariel, ni marge réglementaire, ni besoin de liquidité externe non documenté.

Le mandat candidat est :

> Faire croître sur un horizon fini la richesse nette des coûts d'une poche investie uniquement en SPY et BIL, en ajustant périodiquement l'exposition à SPY, sans position courte, sans emprunt et sans levier, sous des bornes d'exposition dures et un éventuel budget de risque ex ante fixé avant l'expérience.

BIL n'est pas assimilé à du cash constant ni à un taux sans risque. Sa valeur de marché varie, ses distributions sont événementielles et son ETF supporte ses propres frais et coûts de négociation.

### 3.2 Instruments et cash

Les deux instruments autorisés sont :

- **SPY** : instrument négocié donnant l'exposition actions américaine ;
- **BIL** : instrument négocié donnant l'exposition aux Treasury bills de très courte maturité.

Le cash USD est autorisé seulement comme compte technique : reliquat d'arrondi, distributions encaissées, frais, et flux en attente de règlement. Il ne constitue pas un troisième actif stratégique rémunéré tant qu'une convention de rémunération distincte n'est pas approuvée. Cette restriction évite de substituer silencieusement un taux FRED ou SOFR au rendement réellement accessible.

### 3.3 Action et contraintes

À chaque date de décision, le gestionnaire choisit un poids cible SPY

\[
w_t^{SPY}\in[0,1], \qquad w_t^{BIL}=1-w_t^{SPY},
\]

avant conversion en ordres exécutables. Les contraintes proposées sont :

- positions SPY et BIL non négatives ;
- exposition totale financée au plus par la richesse disponible ;
- aucun emprunt, levier, découvert ou vente à découvert ;
- ordres en parts entières et reliquat en cash dans le cas principal ;
- pas de limite de turnover ajoutée tant qu'un besoin de liquidité ou de capacité n'est pas démontré ;
- pas de détention d'un autre instrument.

Un poids continu est utile pour exprimer la décision économique, mais il ne remplace pas l'ordre. Avec des parts entières, la conversion dépend des prix d'exécution, des coûts et de la richesse initiale. Avec des fractions, elle dépendrait des services et règles du courtier ; cette solution simplifie la recherche mais n'est pas universellement négociable.

### 3.4 Fréquence et horizon proposés

Une révision hebdomadaire est recommandée pour le premier cas : elle est assez fréquente pour permettre une adaptation du risque, mais évite de supposer qu'une réaction quotidienne est économiquement nécessaire. Elle limite aussi les exigences de microstructure sans rendre les coûts inexistants.

L'horizon candidat est d'un an. Ce choix donne une signification à la croissance composée, au drawdown et à la persistance des coûts sur plusieurs décisions. Il ne définit pas les périodes historiques d'entraînement, de validation ou de test, et n'est fondé sur aucune performance observée.

Une fréquence quotidienne offrirait plus de réactivité et d'observations, mais amplifierait turnover, dépendance aux spreads et sensibilité à l'heure exacte. Une fréquence mensuelle diminuerait ces exigences, au prix d'une réaction plus lente et de seulement douze décisions par horizon annuel. Ces deux variantes restent des alternatives, non le mandat principal.

## 4. Chronologie économique et prévention du look-ahead

### 4.1 Convention principale

Pour la dernière séance négociée d'une semaine, notée `d` :

1. **Pendant `d`** : aucune donnée de clôture de `d` n'est réputée connue.
2. **Après la clôture de `d`** : le gestionnaire observe uniquement les données publiées et effectivement disponibles à cette heure, y compris les clôtures de `d` si leur disponibilité est documentée.
3. **Décision** : il fixe les poids cibles et construit les ordres sans connaître le prix d'ouverture suivant.
4. **Transmission** : les ordres destinés à l'ouverture suivante sont transmis avant l'heure limite du lieu d'exécution et du courtier.
5. **Exécution** : les ordres éligibles sont exécutés à l'ouverture de la prochaine séance ; une non-exécution, exécution partielle ou suspension doit avoir une règle prédéfinie.
6. **Comptabilisation économique** : les nouvelles positions, le prix exécuté et les coûts sont reconnus à la date de transaction.
7. **Règlement** : créances de vente et dettes d'achat restent séparées du cash réglé jusqu'à la date de règlement applicable.
8. **Détention** : distributions, opérations sur titres et variations de prix affectent les positions jusqu'à la décision suivante.
9. **Valorisation** : la richesse est valorisée chaque séance à la NAV pour le contrôle économique et au prix de marché pour le portefeuille négociable, sans confondre les deux.

Les horaires réguliers actuels de NYSE Arca comprennent une séance cœur de 9 h 30 à 16 h 00 ET, avec enchères d'ouverture et de clôture ; l'historique exact des horaires et séances écourtées doit toutefois être acquis, et non extrapolé depuis le calendrier actuel ([NYSE, Trading Information](https://www.nyse.com/trade/trading-information)). Les pages State Street locales identifient NYSE Arca comme marché principal de SPY et BIL.

### 4.2 Pourquoi cette convention est recommandée

Une décision utilisant la clôture `d` ne peut pas prétendre avoir été exécutée à cette même clôture sans preuve qu'un signal complet était formé et un ordre admissible transmis avant les cut-offs. L'ouverture suivante est observable dans un historique quotidien standard et impose un délai clair. Elle expose réellement le gestionnaire au risque overnight ; ce risque est une conséquence de la convention, pas une fuite d'information.

Une décision avant séance exécutée à son ouverture serait également cohérente si toutes les entrées étaient horodatées avant le cut-off. Elle devient plus exigeante pour les publications nocturnes, les fuseaux et les mises à jour. Une exécution à la clôture est praticable via des ordres dédiés, mais ne convient que si le signal est figé avant les limites d'ordre ; elle n'autorise pas l'emploi de la clôture finale comme entrée.

### 4.3 Date de transaction et date de règlement

La position économique change à l'exécution ; le mouvement définitif de titres et de cash intervient au règlement. Pour les ETF américains couverts par la règle standard :

- T+3 s'applique à la partie ancienne de la période jusqu'au passage à T+2 ;
- T+2 s'applique à compter du 5 septembre 2017 ;
- T+1 s'applique à compter du 28 mai 2024.

La SEC confirme que la transition de 2017 a fait passer les transactions couvertes, y compris les ETF, de T+3 à T+2 ([SEC, adoption de T+2](https://www.sec.gov/newsroom/press-releases/2017-68-0)) et que T+1 est devenu la norme le 28 mai 2024 ([SEC, règle finale 34-96930](https://www.sec.gov/rules-regulations/2023/02/34-96930), [déclaration de mise en œuvre](https://www.sec.gov/newsroom/press-releases/2024-62)). Le futur registre doit paramétrer la convention par date et calendrier ouvré, puis documenter les exceptions éventuelles.

La date de règlement ne doit pas déplacer artificiellement la date d'exposition au marché. Elle crée plutôt des comptes à recevoir et à payer. Les règles du courtier sur l'utilisation de produits de vente non réglés restent à vérifier avant de déclarer un rééquilibrage autofinancé exécutable.

## 5. Prix négociables et état réel des données

### 5.1 Ce qu'est un prix exécutable

Un investisseur de marché secondaire achète et vend un ETF à un prix de marché, non à sa NAV. La SEC rappelle que le prix peut être supérieur ou inférieur à la NAV et varie pendant la séance ([Investor.gov, ETF](https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds-and-exchange-traded-2)). Deux prix sont simultanément pertinents : le bid pour une vente immédiate et l'ask pour un achat immédiat ; leur différence est un coût de transaction ([Investor.gov, bulletin ETF](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-24)).

Pour la convention principale, il faut au minimum, pour SPY et BIL :

- prix officiel d'ouverture ou résultat d'enchère selon une définition commune ;
- prix officiel de clôture pour la valorisation de marché et l'information ;
- dates, heures, fuseau et identifiant du marché ;
- volume, interruptions, non-exécutions et séances écourtées ;
- opérations sur titres et statut ajusté/non ajusté de chaque champ ;
- distributions avec ex-date, record date et payable date ;
- idéalement bid, ask et profondeur au moment de l'ordre.

### 5.2 Inventaire local utile

| Élément | Acquisition locale | Statut / qualité | Usage réellement permis | Manque décisif |
|---|---|---|---|---|
| SPY-B à la NAV | Oui, 2003-12-01–2026-10-15 | `VALIDATED_FOR_USE` limité | performance économique NAV, créances et paiement | prix de transaction et coûts |
| BIL-B à la NAV | Oui, 2008-03-04–2026-10-15 | `VALIDATED_FOR_USE` limité | même référentiel comptable que SPY-B | prix de transaction et coûts |
| OHLCV SPY Nasdaq | Oui, 2016-10-17–2026-10-16 | `AUDITED` | description de prix/volume affichés | ajustements non documentés ; pas de bid/ask |
| OHLCV BIL | **Non** | absent | aucun | série complète d'ouverture, clôture et volume |
| Premium/décote SPY | Oui, 2025-01-02–2026-10-16 | `AUDITED` | comparaison descriptive à la NAV | fichier limité à l'écart quotidien ; pas un prix ni un spread |
| Premium/décote BIL | Oui, 2025-01-02–2026-10-16 | `AUDITED` | même usage descriptif | même limite |
| Distributions SPY/BIL | Oui | `VALIDATED_FOR_USE` pour l'usage documenté | droits et flux de distribution | réserves sur l'événement BIL du 2008-03-03 |
| Split BIL 2017 | Oui | document SEC et Form 8937 validés | ratio 1-pour-2 et date | intégration à vérifier dans tout prix acquis |
| Bid/ask ou NBBO historique | Non | absent | aucun | quotes horodatées des deux ETF |
| Calendrier de marché historique | Non comme jeu dédié validé | présence implicite de dates, insuffisante | contrôle partiel des dates observées | séances écourtées, fermetures, interruptions, cut-offs |
| Commissions/courtier | Non | non défini | aucun | barèmes et type de compte par période |
| Variables d'information | Plusieurs séries locales, statuts hétérogènes | disponibilité point-in-time non validée pour ce mandat | documentation/descriptif selon manifeste | heure de publication, révisions et règle de décision |

### 5.3 Période historiquement exploitable

La période commune NAV du 4 mars 2008 au 15 octobre 2026 est exploitable uniquement pour la comptabilité économique déjà validée. Elle ne devient pas une période de trading.

Pour une exécution à l'ouverture, la couverture locale conjointe est actuellement vide : l'OHLCV SPY commence en octobre 2016, mais BIL n'a pas de série de prix de marché. Même sur 2025–2026, les fichiers de premium/décote ne fournissent pas l'ouverture, le bid, l'ask ou une clôture autonome. Il serait donc incorrect d'annoncer 2008–2026, 2016–2026 ou 2025–2026 comme fenêtre négociable disponible.

Aucune période d'entraînement, de validation ou de test n'est choisie ici. Les périodes déjà consultées dans le projet devront être prises en compte lors d'un futur protocole de séparation temporelle.

## 6. Coûts et contraintes d'exécution

| Composante | Sens économique | Donnée requise | Statut actuel | Traitement défendable futur |
|---|---|---|---|---|
| Spread bid-ask | coût de franchissement entre achat et vente | bid/ask ou NBBO horodaté au moment de l'ordre | inconnu historiquement | estimation empirique seulement après acquisition ; sinon scénarios explicitement hypothétiques |
| Commission | tarif explicite du courtier | barème, compte, date, taille et type d'ordre | inconnu | calcul déterministe après choix du courtier ; ne pas supposer zéro historiquement |
| Slippage | écart entre prix de référence/ordre et prix réellement obtenu | ordre, timestamp, exécution, quotes et profondeur | non identifiable par OHLC | scénarios ou modèle documenté ; jamais présenté comme mesure empirique sans données d'ordres |
| Impact de marché | déplacement du prix causé par l'ordre | taille, carnet/profondeur, participation, dynamique intrajournalière | inconnu | peut être supposé négligeable pour un petit preneur de prix préspécifié, mais reste une hypothèse |
| Frais internes | charges supportées dans le fonds | NAV/prospectus et convention de rendement | déjà incorporés à la NAV | ne pas les déduire une seconde fois ; vérifier la portée pour les prix de marché |
| Quantité | indivisibilité, lots, fractions et arrondis | règles du marché et du courtier, richesse initiale | non validé | parts entières + cash résiduel dans le candidat ; fractions seulement après validation |
| Règlement | décalage entre transaction, titres et cash | cycle T+n, calendrier ouvré, règles du courtier | règle de marché documentable ; opérations du compte inconnues | comptes de règlement séparés et convention datée |
| Fiscalité | impôts sur distributions et cessions | juridiction, investisseur, enveloppe, lots fiscaux | hors périmètre défini | exclure sous une hypothèse de compte fiscalement neutre, et non prétendre qu'elle vaut zéro universellement |

Un coût uniforme fixe ne représenterait pas le marché historique. Il pourrait seulement constituer plus tard un scénario de sensibilité clairement étiqueté. Les statistiques actuelles de premium/décote et le volume SPY ne permettent pas d'en déduire le spread historique des deux ETF.

## 7. Registre comptable requis

### 7.1 Deux mesures de richesse

Le registre devra conserver simultanément :

\[
W_t^{NAV}=\sum_i n_{i,t}N_{i,t}+C_t+A_t+U_t^{vente}-U_t^{achat},
\]

\[
W_t^{marché}=\sum_i n_{i,t}P_{i,t}+C_t+A_t+U_t^{vente}-U_t^{achat},
\]

où `P` est le prix de marché de valorisation, `N` la NAV, `C` le cash réglé disponible, `A` les distributions acquises mais non encaissées, `U^{vente}` les produits de vente à recevoir et `U^{achat}` les achats/frais à payer. La première mesure prolonge le référentiel validé ; la seconde mesure la valeur liquidable approximative au marché selon une convention de prix explicite.

Ni l'une ni l'autre n'est automatiquement le montant exécutable. Pour acheter, il faut l'ask ou le prix d'enchère, les frais et la règle de disponibilité du cash. Pour vendre, le produit est fondé sur le bid ou le prix effectivement obtenu, puis reste à recevoir jusqu'au règlement.

### 7.2 Effet d'une transaction

À la date de transaction, pour chaque instrument `i`, l'ordre exécuté `\Delta n_{i,t}` modifie immédiatement la position économique. Sa contrepartie monétaire devient une dette d'achat ou une créance de vente, augmentée des frais externes. Au règlement, ces comptes s'éteignent contre le cash et la livraison des titres, sans création de richesse.

Une vente de SPY destinée à financer un achat de BIL ne peut pas être représentée par une simple variation de deux poids. Il faut enregistrer séparément chaque quantité, prix, frais, créance/dette et date de règlement, puis vérifier la règle de financement du compte.

### 7.3 Distributions et opérations sur titres

Les parts effectivement détenues à l'ex-date créent une créance `n_i D_i`. Une vente ultérieure ne supprime pas ce droit ; un achat postérieur ne le crée pas. À la payable date, la créance devient du cash, qui reste cash jusqu'à une décision d'investissement. Le réinvestissement automatique à la NAV, utile aux séries SPY-B/BIL-B, ne doit pas être importé silencieusement dans un portefeuille négociable : un réinvestissement réel aurait son propre prix, ses fractions éventuelles et ses conditions de courtier.

Un split modifie les quantités et le prix par part sans créer de richesse. Le split inversé BIL du 30 novembre 2017 doit être pris en compte exactement une fois. Toute série de marché acquise devra révéler si elle est brute ou ajustée afin d'éviter une double correction.

Cette logique explique pourquoi une combinaison pondérée des indices SPY-B et BIL-B ne représente pas un portefeuille rééquilibré : les nombres de parts, les droits aux distributions et les flux de transaction dépendent du chemin propre au portefeuille.

## 8. Objectifs, risques, contraintes et indicateurs

### 8.1 Classification proposée

| Rôle | Élément candidat |
|---|---|
| Objectif à maximiser | croissance composée de la richesse terminale nette des coûts sur l'horizon |
| Risques à maîtriser | exposition aux pertes actions, volatilité prévue, sous-estimation du risque, coûts de rotation |
| Contraintes dures | long-only, absence de levier/emprunt, exposition SPY entre 0 et 100 %, autofinancement |
| Indicateurs d'évaluation | rendement net, volatilité réalisée, pertes, drawdown maximal et durée, dépassements du budget, turnover, coûts, comportement lors des sous-estimations |

Le budget de volatilité prévu est proposé comme contrainte ex ante séparée si le porteur confirme ce rôle. Il ne garantit ni une perte maximale ni un drawdown. Sa valeur ne doit pas être choisie pour améliorer les performances historiques.

### 8.2 Formulations alternatives

- **Croissance sous contrainte de risque — recommandée** : sépare la finalité économique, les limites et les diagnostics. Elle exige de définir le budget et l'information disponible.
- **Minimisation de la volatilité** : conduit facilement à une exposition nulle et ne représente pas la participation recherchée à la croissance.
- **Ciblage pur de volatilité** : fournit une règle simple et un futur comparateur, mais peut imposer des transactions sans valoriser directement la richesse nette.
- **Rendement moins pénalités multiples** : compacte l'objectif, mais transforme des arbitrages économiques en coefficients difficiles à justifier et peut autoriser implicitement des violations.
- **Contrainte de drawdown** : pertinente pour la préservation, mais dépendante du chemin et difficile à garantir ; elle est reportée et reste un indicateur dans le candidat.

Aucune fonction de récompense RL n'est définie. La formalisation du mandat précède le choix éventuel d'une méthode.

## 9. Pourquoi la décision est séquentielle

Le mécanisme minimal est réel et sobre :

```text
position exécutée aujourd'hui
        ↓
position et poids hérités après rendements
        ↓
ordre requis au prochain ajustement
        ↓
spread, frais et comptes de règlement
        ↓
richesse et cash disponibles pour les décisions suivantes
```

L'action présente modifie les quantités détenues, les droits aux distributions, la richesse, les créances/dettes de règlement et le coût du prochain déplacement. Avec des coûts positifs, accepter temporairement un écart à une cible peut éviter un aller-retour ; payer un coût aujourd'hui peut être rationnel si la position est conservée. L'horizon restant influence cet arbitrage.

En revanche, la simple observation d'un marché changeant, la répétition hebdomadaire, une borne locale de poids ou la présence comptable de la richesse ne suffisent pas. Si les coûts sont négligeables et les contraintes locales, une règle répétée ou une optimisation à une période peut suffire. Si les transitions et coûts sont spécifiables, une bande de rééquilibrage ou un contrôle dynamique classique peut suffire. Le RL reste une possibilité ultérieure, jamais une conclusion de ce rapport.

## 10. Matrice de faisabilité

| Élément | Théoriquement disponible | Acquis localement | Audité / validé pour l'usage | Manque | Conséquence |
|---|---:|---:|---|---|---|
| Rendements SPY/BIL à la NAV | oui | oui | validés, usage limité SPY-B/BIL-B | prix d'exécution | socle économique, insuffisant au trading |
| Ouverture/clôture SPY | oui | oui, 2016-10-17–2026-10-16 | audité descriptivement | ajustements et validation d'exécution | candidat partiel seulement |
| Ouverture/clôture BIL | oui | non | non | série locale commune | bloque toute fenêtre de trading |
| Bid/ask des deux ETF | oui chez certains fournisseurs | non | non | quotes/NBBO historiques | spread non mesurable |
| Volume SPY | oui | oui, avec OHLCV | audité descriptivement | capacité et qualité d'exécution | information partielle |
| Volume BIL | oui | non | non | série locale | liquidité non auditable |
| Premium/décote | oui | oui, 2025–2026 | audité descriptivement | ce n'est ni le spread ni un prix d'ouverture | ne calibre pas les transactions |
| Distributions | oui | oui | validées dans leur périmètre | anomalie BIL 2008 exclue par la frontière | registre possible depuis 2008-03-04 à la NAV |
| Opérations sur titres | oui | split BIL documenté | validé pour cet événement | exhaustivité à contrôler dans le prix de marché | risque de double/mauvais ajustement |
| Calendrier et horaires historiques | oui | pas de jeu dédié | non | séances écourtées, halts, cut-offs | chronologie incomplète |
| Cycles de règlement | oui | références documentaires | règles générales vérifiables | calendrier et règles du courtier | comptes réglés/non réglés à construire |
| Commissions | dépend du courtier | non | non | compte et barèmes historiques | coût externe inconnu |
| Slippage/impact | données spécialisées | non | non | ordres, quotes, profondeur | seulement hypothèses/scénarios futurs |
| Fractions de parts | dépend du courtier | non | non | fournisseur et modalités | action continue non exécutable par défaut |
| Information de décision point-in-time | variable par série | partiellement | non validée pour ce mandat | délais, révisions, heure de disponibilité | état décisionnel non prêt |
| Fiscalité | dépend de l'investisseur | non | non | juridiction et enveloppe | performance après impôt hors périmètre |

## 11. Mandat candidat principal

Sous réserve d'approbation, le premier objet empirique serait :

| Dimension | Proposition principale |
|---|---|
| Gestionnaire | gestionnaire preneur de prix d'une poche actions à risque contrôlé |
| Instruments | SPY et BIL ; cash USD résiduel non stratégique |
| Décision | poids cible SPY dans `[0,1]`, solde cible BIL, converti en ordres |
| Contraintes | long-only, sans levier, sans emprunt, autofinancé ; parts entières par défaut |
| Fréquence | hebdomadaire, après la dernière clôture de la semaine |
| Exécution | ouverture de la prochaine séance, ordre et cut-off documentés |
| Horizon | un an, environ 52 décisions ; proposition non calibrée |
| Richesse | double valorisation NAV/marché ; coûts, cash, créances de distribution et règlement séparés |
| Objectif | croissance composée terminale nette des coûts |
| Risque | budget ex ante à confirmer ; pertes, drawdown, sous-estimation et turnover rapportés séparément |
| Données indispensables | OHLCV commun SPY/BIL, calendrier, distributions/splits, quotes pour spread, règles de courtier et information point-in-time |

Ce mandat est simple parce qu'il n'ajoute ni levier, ni vente à découvert, ni actif supplémentaire, ni contrainte de drawdown, ni budget cumulatif artificiel. Il est réaliste sous réserve de données parce qu'il distingue la décision, l'ordre, l'exécution, le règlement, la détention et la valorisation. Il n'est pas autorisé pour une expérience.

## 12. Obstacles et plus petite prochaine étape

Les obstacles bloquants sont :

1. absence totale d'OHLCV BIL local ;
2. absence d'une validation commune des prix d'ouverture SPY/BIL ;
3. absence de quotes historiques pour mesurer le spread ;
4. absence de définition du courtier, des commissions, des fractions et de l'usage des fonds non réglés ;
5. calendrier historique d'exécution non audité ;
6. budget de risque, richesse initiale et statut fiscal non décidés ;
7. information de décision non encore validée point-in-time ;
8. périodes déjà consultées à intégrer dans un futur protocole honnête.

La plus petite étape empirique utile est un **audit de données de marché sans calcul de portefeuille** : identifier puis, après autorisation, acquérir une source commune SPY/BIL couvrant ouverture, clôture et volume avec définitions d'ajustement ; acquérir le calendrier de marché et les opérations sur titres ; vérifier dates, fuseaux, séances écourtées, trous, split BIL et concordance partielle avec les sources State Street. Les quotes/NBBO peuvent former un lot distinct si leur coût ou leurs droits empêchent une acquisition immédiate. Aucun rendement exécutable ne doit être construit avant le verdict de cet audit.

## 13. Réponses A–G

**A. Mandat recommandé.** Une poche SPY–BIL long-only, sans levier, réallouée hebdomadairement par un gestionnaire preneur de prix pour rechercher la croissance composée nette des coûts, avec exposition SPY entre 0 et 100 %, cash seulement résiduel et budget de risque ex ante à confirmer.

**B. Chronologie recommandée.** Décision après la dernière clôture de la semaine avec uniquement l'information alors publiée ; ordre transmis avant le cut-off ; exécution à l'ouverture de la séance suivante ; transaction comptabilisée au trade date et cash/titres réglés selon T+3, T+2 ou T+1 selon la date.

**C. Données de transaction possédées.** Un OHLCV SPY audité depuis octobre 2016 et des volumes associés ; aucun OHLCV BIL ; aucun bid/ask historique ; des premium/décote SPY et BIL depuis 2025 qui ne sont pas des prix d'exécution. La couverture négociable commune est donc nulle.

**D. Coûts.** Les frais internes sont déjà incorporés à la NAV. Les commissions deviendraient calculables après choix du courtier. Le spread est mesurable seulement avec des quotes non acquises. Slippage et impact sont inconnus sans données d'ordres/de carnet ; des scénarios seraient possibles mais non empiriques. Fiscalité et règles de fractions restent indéfinies.

**E. Séquentialité.** La position choisie devient la position héritée, détermine les droits aux distributions, le cash et les comptes de règlement, puis le volume et le coût du prochain ordre. Les conséquences ne se limitent donc pas au rendement immédiat.

**F. Obstacles.** Prix BIL absents, exécution commune non validée, quotes et coûts manquants, calendrier incomplet, conventions de courtier/fiscalité non choisies, variables de décision non validées point-in-time et paramètres économiques non approuvés.

**G. Prochaine étape minimale.** Autoriser un audit ciblé des prix de marché SPY/BIL et du calendrier, sans portefeuille, simulation, optimisation ou entraînement. Son premier livrable doit être un verdict d'adéquation à l'exécution, pas une performance.

## 14. Règle d'arrêt

Ce rapport n'autorise aucun backtest, benchmark décisionnel, simulateur, MDP opérationnel, environnement Gymnasium, optimisation, modèle prédictif ou agent RL. Il ne modifie aucune série ni aucun statut de validation. Le mandat, l'acquisition ciblée des données et toute expérience ultérieure nécessitent des validations explicites et séparées.
