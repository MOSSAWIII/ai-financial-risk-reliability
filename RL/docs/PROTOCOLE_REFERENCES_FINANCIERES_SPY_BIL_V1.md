# Protocole des références financières SPY–BIL v1

Date : 20 octobre 2026

Point de départ : `f2c28077e31799cc7521a3491706e096124dce0a`

Statut : **protocole scientifique proposé, sans exécution**. Ce document ne crée
aucune stratégie, transaction, simulation, période d'évaluation ou performance.
Les paramètres signalés comme ouverts doivent être approuvés avant toute
expérience.

## 1. Question économique étudiée

Le gestionnaire d'une poche autonome en USD choisit une exposition à SPY comprise
entre 0 et 100 %. BIL reçoit normalement le complément ; le cash n'est qu'un
support de règlement, de distribution ou d'arrondi. La question est :

> Dans quelles conditions adapter l'exposition au risque ajoute-t-il une valeur
> économique à des décisions plus simples, après prise en compte des pertes, du
> chemin de richesse, des coûts, des contraintes et des erreurs de risque ?

Une hausse de richesse ne suffit pas à répondre si elle provient seulement d'une
exposition SPY plus forte. Inversement, une volatilité plus basse n'est pas une
preuve d'utilité si elle est obtenue en restant presque toujours en BIL. Les
dimensions de rendement, risque, mécanique financière et validité documentaire
doivent donc rester séparées. L'égalité ou l'infériorité d'une règle dynamique est
un résultat scientifique recevable.

Le projet antérieur a montré que la qualité moyenne d'une prévision de volatilité
ne garantit pas l'absence de fortes sous-estimations. Il a aussi établi que `RV5`
est une cible future : elle peut qualifier ex post une prévision, mais elle ne peut
jamais entrer dans une décision prise à son origine.

## 2. Mandat commun aux références

Toutes les références devront partager exactement le même contrat économique.
Les conventions ci-dessous restent provisoires jusqu'à approbation collective.

| Dimension | Convention commune candidate |
|---|---|
| Univers | SPY, BIL et cash strictement technique ; long-only |
| Exposition | poids SPY dans `[0,1]`, BIL complémentaire à la cible |
| Compte | poche USD stylisée, sans marge, vente à découvert ni retrait |
| Capital | même capital initial pour toutes les références ; 100 000 USD proposé en principal |
| Parts | entières, arrondies à l'entier inférieur lors du calcul d'une cible |
| Décision | grille hebdomadaire commune, 08:00 `America/New_York` |
| Information | uniquement ce qui est admissible avant l'instant de décision |
| Dimensionnement | richesse et closes admissibles ; quantités figées avant l'open |
| Exécution | Yahoo `Open` conditionnel, référence hypothétique et non fill garanti |
| Financement | `H_FIN_NET` limité, lot atomique et cash projeté jamais négatif |
| Distributions | droits, créances et cash comptabilisés aux dates documentées |
| Coûts | même modèle et mêmes scénarios ex ante ; fiscalité exclue |
| Horizon | un an proposé, même début et même fin, sans liquidation forcée |
| Valorisation | richesse économique incluant cash, positions, créances et dettes |
| Blocage | mêmes statuts documentaires et même règle d'arrêt commun |

Les positions héritées, y compris positions réglées, positions économiques et
flux en attente, sont l'état véritable de la poche. Une politique propose une
cible à partir de cet état ; elle ne repart jamais fictivement du capital initial.
Les écarts à la cible dus aux parts entières, gaps, coûts ou rejets sont conservés,
pas corrigés rétroactivement.

## 3. Définition des références financières

Notons `W_d` la richesse économique admissible à la décision `d`, `P_{i,d}` le
close admissible de l'instrument `i`, `q_{i,d^-}` sa quantité héritée et
`w_d` le poids cible SPY. Lorsqu'une politique produit une cible :

\[
q_{SPY,d}^{cible}=\left\lfloor\frac{w_d W_d}{P_{SPY,d}}\right\rfloor,
\qquad
q_{BIL,d}^{cible}=\left\lfloor\frac{(1-w_d)W_d}{P_{BIL,d}}\right\rfloor,
\]

\[
\Delta q_{i,d}=q_{i,d}^{cible}-q_{i,d^-}.
\]

Ces équations traduisent une cible déjà décidée ; elles ne choisissent pas le
poids et n'autorisent aucun redimensionnement après observation de l'open.

### 3.1 Référence A — Buy-and-hold SPY

- **Décision initiale :** `w_0=1`. Acheter le nombre entier de parts SPY permis
  par le capital et conserver le résiduel en cash technique.
- **Après l'achat :** aucune nouvelle cible hebdomadaire et aucun ordre volontaire.
  Les poids observés changent naturellement avec SPY et le cash.
- **Distributions :** constater le droit, la créance puis le cash selon les dates
  documentées. La convention principale proposée est de conserver ce cash sans
  réinvestissement automatique, afin de ne pas transformer la détention en suite
  d'ordres. Cette convention doit être approuvée et appliquée symétriquement.
- **Mesure :** richesse totale, distributions incluses, et risque de la poche
  réellement détenue. Le cash reçu reste dans la richesse.

Cette politique prend une décision d'exposition initiale ; l'évolution ultérieure
de son poids n'est pas une décision répétée. Une grille hebdomadaire peut servir à
valoriser et comparer les trajectoires, jamais à régénérer un ordre SPY inutile.

### 3.2 Référence B — Buy-and-hold BIL

La définition est identique avec `w_0=0` : achat initial de BIL, cash résiduel,
comptabilisation des distributions et absence d'ordre volontaire ultérieur.

BIL est une exposition investie à un ETF de Treasury bills très courts. Ce n'est
ni le cash du registre, ni un taux sans risque théorique, ni un actif parfaitement
sans risque : son prix et sa NAV peuvent varier, il distribue des revenus selon un
calendrier propre, supporte frais, spread, liquidité, tracking et risque
opérationnel d'ETF. Son achat et sa vente exigent eux aussi prix, règlement et
documents admissibles.

### 3.3 Référence C1 — 50/50 initial conservé

À l'initialisation, `w_0=0,5`. Après le lot initial, aucune cible n'est recalculée
et aucun rééquilibrage volontaire n'est effectué. Les poids SPY, BIL et cash
dérivent avec les prix, distributions et arrondis. La politique représente une
diversification initiale, pas le maintien continu d'un budget de risque.

### 3.4 Référence C2 — cible 50/50 rééquilibrée chaque semaine

À chaque date commune admissible, `w_d=0,5`. Les quantités cibles sont recalculées
au close à partir de la richesse et des positions héritées. Si les deltas entiers
sont nuls, la décision produit `VOLUNTARY_HOLD` et aucun open n'est requis. Sinon,
le lot complet est soumis à l'open suivant, aux coûts, au financement et au
règlement communs. Un rejet laisse l'état hérité inchangé et demeure un rejet,
jamais un hold requalifié.

C1 et C2 doivent être conservées comme références distinctes. C1 mesure la
conséquence d'une allocation initiale dont les poids dérivent. C2 mesure la valeur
et le coût d'une discipline de retour à la cible. Leur différence peut provenir
du contrôle des poids, mais aussi du turnover, des gaps, des arrondis, des coûts,
des rejets et du cash résiduel. La fréquence hebdomadaire est proposée par le
mandat antérieur ; elle ne résulte d'aucune performance observée.

### 3.5 Référence D — calibrage déterministe de la poche SPY par le risque

La première règle dynamique candidate est :

\[
w_d^{SPY}=\operatorname{clip}\left(
\frac{\sigma^*}{\widehat{\sigma}_{SPY,d}},0,1\right),
\qquad w_d^{BIL}=1-w_d^{SPY}.
\]

`sigma*` est une cible de risque fixée avant l'évaluation et
`sigmahat_SPY,d` une estimation annualisée calculée uniquement avec des rendements
économiques SPY arrivés et admissibles à 08:00 le jour `d`. Une estimation nulle,
non positive, non finie, insuffisamment longue ou documentairement bloquée ne doit
pas être remplacée par un plancher choisi après coup : la décision est non
évaluable selon une règle à approuver.

Cette formule est volontairement nommée **calibrage de la poche SPY**, et non
« ciblage exact de la volatilité du portefeuille ». En effet, pour une estimation
de covariance donnée :

\[
\widehat{\sigma}_{p,d}^2(w)=
w^2\widehat{\sigma}_{SPY,d}^2
(1-w)^2\widehat{\sigma}_{BIL,d}^2
2w(1-w)\widehat{\operatorname{Cov}}_d(SPY,BIL).
\]

La règle simple n'annule ni la volatilité de BIL ni la covariance. La volatilité
totale implicite doit être publiée comme diagnostic ex ante si les entrées sont
admissibles, sans prétendre que `sigmahat_p,d=sigma*`. Une future règle résolvant
explicitement cette équation serait une référence différente, plus complexe, avec
risque d'estimation, solutions multiples ou cible parfois irréalisable ; elle
n'appartient pas au premier ensemble.

## 4. Informations nécessaires à la règle déterministe

Avant toute expérience, les éléments suivants doivent être définis et versionnés :

1. une fenêtre rétrospective `L`, son nombre minimal d'observations et la règle
   applicable aux jours absents ;
2. une formule unique d'estimation — par exemple écart-type des rendements
   quotidiens sur `L` séances — et un facteur d'annualisation préspécifié ;
3. `sigma*`, son unité, sa justification économique et son statut de cible de la
   poche SPY plutôt que de promesse sur le portefeuille total ;
4. les rendements économiques SPY et, pour le diagnostic de portefeuille, BIL et
   leur covariance, tous arrêtés à la dernière clôture admissible ;
5. la version exacte des prix, distributions, splits et conventions nécessaires
   pour produire ces rendements sans révision silencieuse ;
6. les positions et flux hérités, la richesse connue, les calendriers et statuts
   documentaires à la décision ;
7. la règle en cas d'historique insuffisant, valeur invalide ou document manquant ;
8. l'éventuel seuil de non-transaction. Aucun seuil n'est retenu en v1 : s'il est
   ajouté, il devra être justifié et fixé sans consulter les performances.

Pour le candidat « écart-type historique », si `s(d)` est la dernière clôture
admissible avant la décision et `r_j^{TR}` les `L` rendements économiques totaux
qui s'y terminent, la définition paramétrique est :

\[
\bar r_d=\frac{1}{L}\sum_{j=s(d)-L+1}^{s(d)}r_j^{TR},
\qquad
\widehat{\sigma}_{SPY,d}=
\sqrt{\frac{A}{L-1}\sum_{j=s(d)-L+1}^{s(d)}
\left(r_j^{TR}-\bar r_d\right)^2}.
\]

`A` est le facteur d'annualisation correspondant à la fréquence quotidienne. Ni
`L` ni `A` ne sont fixés par ce document ; leur convention calendaire et leur
valeur doivent être approuvées avant résultats. L'indice de fenêtre exprime un
ordre de séances admissibles, pas une soustraction naïve de jours calendaires.

Une fenêtre courte réagit davantage mais produit une estimation plus variable ;
une fenêtre longue lisse davantage mais peut réagir tardivement. Ce compromis ne
justifie pas de sélectionner `L` sur la période d'évaluation.

## 5. Rendements de risque et restrictions point-in-time

Quatre objets doivent rester séparés :

| Objet | Disponibilité et usage |
|---|---|
| volatilité passée observée | description ex post d'un intervalle déjà achevé |
| estimation rétrospective | fonction fixée de rendements connus au plus tard à la décision |
| prévision à la décision | valeur produite à `d`, éventuellement évaluée plus tard |
| volatilité future réalisée `RV5_d` | construite avec les cinq rendements futurs ; inconnue à `d` |

`RV5_d`, l'erreur `prévision_d - RV5_d`, le rang futur de `RV5` et l'appartenance
ultérieure à un épisode de sous-estimation sont interdits dans `w_d`. Ils peuvent
seulement servir, après maturation des cinq séances, à un diagnostic ex post de la
prévision et de l'exposition qui avait été décidée sans eux.

Le `RV5` du projet principal est en outre construit sur la série de marché étudiée
dans ce projet, pas sur la richesse du portefeuille SPY–BIL. Une future analyse
devra documenter instrument, fréquence, unités et alignement avant de relier ses
erreurs à une exposition SPY. Elle ne pourra jamais assimiler silencieusement
`RV5`, volatilité SPY et volatilité du portefeuille.

La série nécessaire à `sigmahat_SPY,d` est une série séquentielle de rendements
économiques totaux, reconstruite avec les prix par part et événements effectivement
admissibles à chaque date. Une baisse mécanique à l'ex-date doit être compensée par
la naissance du droit économique correspondant ; sinon elle gonflerait
artificiellement le risque. Les distributions ne doivent toutefois entrer dans
l'information de décision qu'au moment où leur contenu est historiquement connu.

Le champ actuel `Adj Close` ne satisfait pas ce contrat : il peut incorporer
rétrospectivement distributions et splits sur toute la série et sa version
historique exacte n'est pas certifiée. Il ne peut donc pas être copié comme entrée
point-in-time. Avant une expérience, il faut soit une reconstruction progressive,
versionnée et auditée des rendements utilisables à chaque décision, soit classer la
règle D non évaluable. Une série de prix bruts ignorant les distributions n'est pas
une solution acceptable au biais d'ex-date.

## 6. Principes de comparaison équitable

### 6.1 Même contrat, actions différentes

Toutes les politiques reçoivent le même capital, les mêmes événements de marché,
le même calendrier de valorisation et les mêmes règles de parts, financement,
coûts, distribution et terminal. Seuls diffèrent les poids produits et donc les
ordres économiquement nécessaires. Les positions héritées sont transmises sans
réinitialisation ; le cash résiduel n'est ni redistribué fictivement ni rémunéré.

Une date sans ordre est un résultat normal. Elle n'exige ni open ni règlement. Un
ordre rejeté conserve les positions mais compte comme rejet et écart à la cible.
Un défaut documentaire n'est ni une performance nulle, ni un hold, ni une perte.

### 6.2 Règle commune de couverture documentaire

La grille d'épisodes et de décisions doit être fixée sans lire les performances.
La comparaison principale est **appariée** : si une information requise rend l'une
des politiques comparées `NOT_EVALUABLE`, l'épisode commun devient non évaluable
pour le classement à partir du premier blocage. Les autres politiques peuvent être
continuées uniquement pour mesurer leur couverture opérationnelle, mais leurs
résultats non appariés ne peuvent établir une supériorité.

Cette règle évite de supprimer une date difficile seulement pour la politique qui
aurait dû négocier. Elle ne force cependant pas un buy-and-hold à exiger un open
quand il n'a aucun ordre : le blocage propre à l'autre politique est publié comme
différence de faisabilité, puis neutralisé dans la comparaison principale par
l'arrêt commun. Les nombres d'épisodes complets, tronqués et non évaluables, ainsi
que chaque cause, doivent être présentés avant tout résultat financier.

Une sensibilité de couverture ne peut utiliser qu'une règle alternative fixée à
l'avance — par exemple exiger un épisode entièrement documenté dès l'origine — et
jamais une sélection fondée sur les rendements constatés.

### 6.3 Coûts et exposition au risque

Le cas comptable à coûts externes nuls peut contrôler les identités, mais ne doit
pas être présenté comme réaliste. Les scénarios de coûts, leurs unités et leur
application doivent être communs et fixés avant résultats. Un coût est appliqué
uniquement lorsqu'un ordre existe ; cela ne favorise pas artificiellement le
buy-and-hold, mais mesure précisément le coût économique de l'activité choisie.

Les rendements bruts ne suffisent pas à comparer des politiques dont l'exposition
SPY moyenne diffère. Il faut publier conjointement rendement, trajectoire de risque,
poids obtenus et turnover, sans réduire le résultat à un classement unique ou à un
ratio prétendument causal.

## 7. Critères d'évaluation futurs

Aucune mesure n'est calculée dans ce protocole. Les définitions et fréquences
exactes devront être figées avec l'expérience.

### 7.1 Richesse et rendement

- **Richesse terminale économique :** positions valorisées plus cash, créances et
  produits de vente, moins dettes d'achat et frais. Elle répond à « combien reste-t-il
  sous ces conventions ? », pas à « pourquoi ? ».
- **Rendement total :** `W_T/W_0-1`, distributions comprises. Il mesure le gain
  cumulé, mais confond exposition, chemin et risque.
- **Rendement composé/annualisé :** taux cohérent avec la durée exacte ; utile
  entre épisodes de même protocole, sensible au point de départ et impropre si la
  durée ou les apports diffèrent.
- **Effet des distributions :** contribution comptable séparée des variations de
  prix, sans attribuer causalement la performance à une politique.
- **Coûts :** différence entre richesse brute théorique et nette, avec ventilation
  par type ; dépendante du modèle de coût choisi.

### 7.2 Risque

- **Volatilité des variations de richesse :** dispersion à fréquence commune ;
  elle n'indique ni le signe ni la gravité économique d'une perte.
- **Pertes importantes :** pire rendement périodique et mesures de queue à un
  niveau fixé ex ante ; elles sont fragiles avec peu d'observations.
- **Drawdown maximal :** plus forte baisse de richesse depuis un sommet antérieur ;
  mesure le chemin mais dépend de l'horizon et du point initial.
- **Durée des drawdowns :** temps passé sous le précédent sommet ; un drawdown
  encore ouvert au terminal doit rester censuré comme tel.
- **Sous-estimation du risque :** erreurs de prévision arrivées à maturité,
  exposition SPY décidée lors de ces erreurs et pertes ultérieures, rapportées
  séparément. Ce diagnostic relie fiabilité et conséquence sans transformer `RV5`
  futur en information de décision. Une forte `RV5` n'est pas automatiquement une
  perte.

### 7.3 Mécanique financière

- turnover notionnel rapporté à la richesse avant ordre ;
- nombres de décisions, lots et ordres par instrument ;
- holds volontaires et rejets économiques par cause ;
- cash résiduel moyen, maximal et terminal ;
- écart absolu entre poids cible et poids obtenu, avant et après transaction ;
- temps et montants en règlement.

Ces mesures expliquent comment une politique produit son résultat. Elles ne sont
pas des coûts interchangeables et ne doivent pas être agrégées arbitrairement.

### 7.4 Validité expérimentale

- part des épisodes et décisions complètement documentés ;
- blocages et observations non évaluables par cause et par politique ;
- stabilité directionnelle sur sous-périodes fixées ex ante, sans recherche du
  découpage le plus favorable ;
- sensibilité à des hypothèses de coûts préspécifiées ;
- dépendance aux paramètres voisins seulement si cette grille est fixée avant
  l'évaluation.

Ces diagnostics mesurent la portée de la conclusion, pas la qualité financière de
la politique.

## 8. Protocole temporel futur

La grille candidate conserve provisoirement une décision hebdomadaire à 08:00 ET
le jour de la première séance commune suivant la dernière clôture commune de la
semaine précédente. Les données doivent être disponibles à cet instant. La cible
et les quantités sont figées avant l'ouverture ; l'open suivant ne sert qu'à
l'exécution hypothétique conditionnelle.

L'initialisation proposée est commune : chaque épisode commence en cash réglé ; la
première décision utilise le dernier close admissible antérieur et le premier lot
est présenté à l'open commun suivant. Le début économique de l'épisode, la règle
exacte d'anniversaire et la dernière date de valorisation doivent encore être
approuvés. Aucun capital n'est ajouté après l'initialisation. D exige en outre une
période de chauffe antérieure contenant au moins `L` rendements admissibles ; elle
sert uniquement à former l'information initiale et ne contribue pas à la
performance de l'épisode.

Pour A, B et C1, les rendez-vous hebdomadaires servent à observer la richesse et
les risques, pas à reformuler la décision initiale. C2 et D produisent une cible à
chaque rendez-vous admissible. Avant chaque décision, le registre applique dans
l'ordre tous les événements et règlements dont l'instant est dû. Les positions en
règlement restent économiques mais seules les parts réglées sont vendables. Une
décision nouvelle n'annule ni ne réécrit un lot antérieur en attente ; elle peut
produire un hold, un rejet ou un blocage selon le même contrat.

Au terminal, aucune liquidation artificielle n'est imposée. La richesse est
valorisée à la dernière clôture commune admissible selon la règle calendaire
approuvée, en incluant positions, cash, créances et dettes encore ouvertes. Une
donnée indispensable manquante rend le terminal non évaluable ; aucun dernier prix
n'est reporté opportunistement.

## 9. Logique scientifique des comparaisons

Les questions doivent être traitées séquentiellement, sans présumer la réponse.

1. **Diversification initiale :** comparer A, B et C1. Une position intermédiaire
   peut modifier rendement et risque, mais aucun résultat ne prouvera à lui seul
   que 50/50 est optimal.
2. **Discipline de rééquilibrage :** comparer C2 à C1. Les mécanismes candidats
   sont le maintien des poids, la vente relative de l'actif apprécié, le turnover,
   les coûts, les rejets et le cash. La comparaison ne doit pas être confondue avec
   SPY contre BIL.
3. **Adaptation au risque :** comparer D à C2 et C1 sous le même contrat. Un gain
   potentiel doit être relié aux changements d'exposition et à la fiabilité de
   `sigmahat`, pas attribué automatiquement à la dynamique.

Une méthode séquentielle plus complexe ne mériterait d'être étudiée que si :

- des décisions successives et l'état hérité créent un effet de chemin matériel ;
- C2 ou D révèle un compromis réel entre adaptation, risque et coûts que les
  références conservées ne capturent pas ;
- aucune règle simple préspécifiée ne traite suffisamment ce compromis ;
- la couverture documentaire et les données permettent une évaluation distincte
  d'une simple extrapolation hors support ;
- l'amélioration recherchée subsiste après coûts et à exposition au risque
  explicitement décrite.

Même alors, rien ne conclurait encore en faveur du RL et aucun algorithme n'est
proposé ici.

## 10. Risques méthodologiques et décisions ex ante

| Risque | Garde-fou requis |
|---|---|
| look-ahead bias | borner chaque entrée à son `knowledge_at`; interdire `RV5_d`, open futur et événement non annoncé dans la décision |
| choix rétrospectif | figer `L`, `sigma*`, formule, annualisation, fréquence et règles invalides avant toute performance |
| data snooping | limiter les variantes, conserver un registre de toutes celles examinées et réserver une évaluation qui n'a pas choisi les règles |
| overfitting | privilégier D transparente, peu paramétrée, et ne pas sélectionner une combinaison sur le résultat |
| rendements ajustés rétrospectivement | reconstruire séquentiellement prix et événements ; interdire l'`Adj Close` actuel comme donnée point-in-time |
| sélection d'épisodes | figer calendrier et règle documentaire ; publier tous les blocages, sans retirer les périodes défavorables |
| expositions différentes | publier poids, exposition SPY, risque, rendement et coûts ensemble ; aucune conclusion sur le seul rendement |
| coûts irréalistes | séparer zéro-coût comptable et scénarios économiques, fixés ex ante et appliqués uniquement aux ordres réels |

Doivent aussi être fixés avant toute observation de performances : capital,
initialisation, traitement des distributions, cash, horizon, terminal, calendriers,
prix, financement, atomicité, événements, règle d'arrêt commun, mesures, périodes
d'apprentissage/validation/évaluation éventuelles et statut exploratoire ou
confirmatoire. Aucun découpage temporel n'est choisi dans cette phase.

## 11. Hypothèses ouvertes et conditions avant expérience

### 11.1 Paramètres à approuver

- capital principal et éventuelles sensibilités d'échelle ;
- traitement commun des distributions après paiement : cash conservé proposé, ou
  règle de réinvestissement entièrement spécifiée ;
- calendrier hebdomadaire, date initiale, horizon exact et valorisation terminale ;
- `H_FIN_NET`, parts entières, lot atomique et Yahoo `Open` conditionnel ;
- modèle de coûts et scénarios de sensibilité ;
- fenêtre `L`, formule, annualisation, `sigma*` et traitement d'une estimation
  invalide pour D ;
- construction point-in-time des rendements économiques de risque ;
- règle de couverture commune et seuil minimal de couverture acceptable ;
- mesures, fréquence de calcul et éventuels niveaux de queue ;
- découpage temporel futur et statut des conclusions.

### 11.2 Conditions nécessaires

Avant une première expérience, il faudra :

1. approuver le mandat commun et toutes les définitions de politiques ;
2. prouver la disponibilité point-in-time des entrées de D, notamment une série de
   rendements économiques sans ajustement rétrospectif ;
3. figer des calendriers de négociation et règlement couvrant toutes les dates
   sollicitées et les événements applicables ;
4. résoudre ou bloquer formellement chaque prix et événement contesté ;
5. figer coûts, règle documentaire, épisodes et mesures sans consulter les
   performances ;
6. vérifier par tests artificiels le chemin multi-décision, les distributions,
   ordres en règlement, rejets, terminal et arrêt commun ;
7. réserver une procédure d'évaluation compatible avec les périodes déjà
   consultées et annoncer clairement son statut scientifique.

Le premier cycle historique validé prouve le passage source–intention–registre sur
une date. Il ne prouve aucune de ces conditions à l'échelle d'un épisode.

## 12. Recommandation minimale et tableau d'approbation

Le plus petit premier ensemble cohérent est **A, B et C1** : buy-and-hold SPY,
buy-and-hold BIL et 50/50 initial conservé. Il répond seulement à la question de
diversification initiale et contrôle la mesure de richesse sans décisions répétées.
Après validation de ce socle, **C2** doit être ajouté pour isoler l'effet du
rééquilibrage, puis **D** pour isoler l'adaptation au risque. Tester D directement
contre SPY seul confondrait adaptation, diversification et niveau d'exposition.

Cette recommandation décrit un ordre scientifique futur ; elle n'autorise aucune
expérience.

| Référence ou convention | Définition proposée | Paramètres à approuver | Question isolée |
|---|---|---|---|
| A — SPY conservé | achat initial `w=1`, puis aucun ordre volontaire | distributions, cash, initialisation | exposition actions extrême |
| B — BIL conservé | achat initial `w=0`, puis aucun ordre volontaire | mêmes choix que A | exposition défensive investie |
| C1 — 50/50 conservé | achat initial 50/50, poids ensuite libres de dériver | arrondi et traitement des flux | diversification initiale |
| C2 — 50/50 hebdomadaire | cible `w=0,5` à chaque décision, hold si deltas nuls | fréquence, coûts, financement, rejet | effet propre du rééquilibrage |
| D — calibrage du risque SPY | `clip(sigma*/sigmahat_SPY,d,0,1)`, complément BIL | `L`, estimateur, annualisation, `sigma*`, données invalides | valeur de l'adaptation au risque |
| Rendements de risque | reconstruction économique séquentielle, sans `Adj Close` actuel | prix, distributions, splits, `knowledge_at` | absence de fuite et d'effet ex-date |
| Calendrier | décision hebdomadaire 08:00 ET, ordre à l'open suivant | dates, early closes, règlement, terminal | chronologie commune |
| Compte | USD, long-only, parts entières, `H_FIN_NET`, cash technique | capital, courtier stylisé, atomicité | faisabilité identique |
| Coûts | couche comptable distincte de scénarios économiques | formule et valeurs ex ante | valeur nette de l'activité |
| Couverture | arrêt apparié au premier blocage d'une politique comparée | seuil de couverture et sensibilité | comparaison sur support commun |
| Évaluation | vecteur rendement–risque–mécanique–validité | mesures, fréquence, périodes | conclusion multidimensionnelle |
