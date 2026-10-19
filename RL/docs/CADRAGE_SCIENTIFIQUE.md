# Cadrage scientifique — Reinforcement Learning et décisions financières sous incertitude

**Date du cadrage : 19 octobre 2026**

**Statut : document de réflexion ; aucun problème empirique, algorithme ou jeu de données n'est validé**

## 1. Positionnement scientifique

### 1.1 Question provisoire

> Dans quelle mesure des politiques de décision financière apprises séquentiellement peuvent-elles améliorer la gestion du risque lorsque les prévisions sont imparfaites et que les conditions économiques et financières évoluent ?

Cette question contient quatre objets qu'il faudra rendre observables avant toute expérience : une **décision**, une **séquence**, un critère de **gestion du risque** et une notion de **changement d'environnement**. Elle ne suppose ni que le RL est nécessaire, ni qu'une politique apprise est préférable à une règle financière simple.

La formulation la plus prudente du programme est donc :

> Identifier d'abord un problème financier dans lequel les conséquences d'une action présente dépendent matériellement des actions et états futurs ; déterminer ensuite si l'apprentissage séquentiel apporte une valeur mesurable par rapport aux solutions classiques correctement spécifiées.

### 1.2 Statut des affirmations

Le document distingue quatre niveaux :

- **Connaissance établie** : définition ou résultat théorique appuyé sur une référence identifiable.
- **Résultat du projet existant** : constat empirique limité aux protocoles déjà exécutés.
- **Hypothèse de travail** : proposition falsifiable concernant le futur axe RL.
- **Choix ouvert** : décision scientifique qui appartient au porteur du projet.

Aucune « contribution originale » n'est revendiquée. La littérature sur le contrôle stochastique, l'allocation dynamique et le RL financier est déjà vaste ; l'originalité éventuelle ne pourra être discutée qu'après une revue ciblée sur un problème précisément défini.

### 1.3 Articulation avec le projet existant

Le socle actuel établit notamment que :

- `RV5_t` mesure l'amplitude annualisée des rendements `t+1` à `t+5`, mais reste un proxy bruité, chevauchant, insensible au signe et connu seulement après `t` ;
- une partie de sa persistance est mécanique, car deux cibles voisines partagent jusqu'à quatre rendements ;
- sur 2016–2019, plusieurs prévisions simples ou plus complexes améliorent certains critères moyens sans dominer tous les aspects de fiabilité ;
- les cinq modèles connaissent 44 fortes sous-estimations communes regroupées en 13 épisodes ;
- les alertes `HV20` et `HV5/HV20` n'ont reconnu respectivement que 0 et 1 des 13 débuts, et leur précision quotidienne n'a pas dépassé la fréquence de base ;
- aucune fonction de coût financier, politique d'exposition ou utilité économique n'a encore été validée.

Ces résultats ne prouvent pas qu'une politique RL améliorerait la décision. Ils montrent plutôt pourquoi il faut distinguer la qualité d'une **prévision** de la qualité d'une **action prise sous prévision imparfaite**.

Le lien intellectuel possible est le suivant :

```text
information disponible à t
        ↓
prévision imparfaite et incertitude
        ↓
décision d'exposition / allocation / couverture
        ↓
rendement, risque, coûts et contraintes réalisés
        ↓
nouvel état décisionnel à t+1
```

Le nouvel axe reste autonome : il n'est pas limité à `RV5`, aux cinq modèles existants, au marché agrégé Fama–French ou aux périodes déjà analysées. Toute réutilisation de ces éléments devra être justifiée pour la décision choisie.

## 2. Quels problèmes financiers sont réellement séquentiels ?

Une suite chronologique de prédictions ne suffit pas à créer un problème RL. Le caractère séquentiel devient substantiel lorsque l'action `a_t` modifie au moins l'un des éléments suivants :

- la position ou l'inventaire détenu à `t+1` ;
- la richesse, la marge ou le budget de risque futur ;
- les coûts de transaction futurs ;
- l'ensemble des actions encore admissibles ;
- l'information reçue ou, pour un acteur suffisamment important, l'état du marché ;
- la valeur des actions futures par un effet de chemin.

Si l'action n'affecte que le gain immédiat et ne change ni l'état suivant ni les possibilités futures, un problème à une étape, une optimisation répétée ou un contextual bandit peut suffire.

### 2.1 Comparaison des principaux problèmes candidats

| Problème | Pourquoi il est séquentiel | Décision possible | Références classiques indispensables | Difficulté empirique | Appréciation actuelle |
|---|---|---|---|---|---|
| Exposition dynamique / ciblage de volatilité | la position courante détermine le coût de rotation, le levier, la richesse et parfois la marge futurs | exposition au marché ou budget de risque | règle fixe, ciblage de volatilité, contrôle avec coûts | modérée si l'on reste sur un actif liquide et une fréquence basse | candidat le plus simple à approfondir |
| Allocation multi-actifs | les poids, la richesse et les contraintes évoluent ; rééquilibrer crée des coûts | vecteur de poids | allocation statique, moyenne-variance, allocation multi-périodes, contrôleur déterministe | élevée : dimension, covariance, actifs et biais de survie | pertinent, mais probablement trop large au départ |
| Couverture dynamique | la sensibilité du portefeuille et le temps restant évoluent ; chaque couverture modifie la position future | quantité d'actif ou de dérivé | delta-hedging, contrôle stochastique | élevée : options, volatilité implicite, conventions, coûts | scientifiquement naturel, données plus exigeantes |
| Exécution optimale | l'inventaire restant, l'impact et le temps contraignent les actions suivantes | taille et calendrier des ordres | règles d'exécution et contrôle optimal | très élevée : données intrajournalières et impact contrefactuel | clairement séquentiel, mais prématuré |
| Contrôle de limites ou de marge | une action peut éviter une violation future mais réduire l'exposition ou la liquidité | réduction, maintien ou couverture | règles de seuil, optimisation contrainte | élevée : règles institutionnelles et données de portefeuille | utile si un utilisateur concret est défini |
| Sélection répétée sans coûts ni état de portefeuille | chaque choix produit surtout un gain immédiat et le marché reste exogène | choix parmi quelques expositions | meilleure action fixe, contextual bandit | faible à modérée | le RL complet pourrait être inutile |

La littérature classique montre déjà que les coûts de transaction rendent l'allocation dynamique dépendante du chemin et peuvent créer des zones de non-transaction ; ce phénomène ne vient pas du RL lui-même ([Davis et Norman, 1990](https://doi.org/10.1287/moor.15.4.676)). De même, le ciblage de volatilité possède des références empiriques simples qui doivent précéder toute méthode apprenante ([Moreira et Muir, 2017](https://doi.org/10.1111/jofi.12513)).

### 2.2 Candidat prioritaire proposé, sans validation

**Hypothèse de travail :** la gestion dynamique d'une exposition risquée sous prévision imparfaite de volatilité est le candidat le plus maîtrisable pour une première étude.

Ses avantages sont :

- un lien direct avec la question existante de fiabilité des prévisions ;
- une action simple et interprétable, par exemple une exposition bornée ;
- des références fortes : exposition constante, règle de ciblage de volatilité, règle prudente déterministe ;
- une dépendance intertemporelle introduite explicitement par le coût de rotation, les bornes de levier, la richesse ou le budget de risque ;
- la possibilité de montrer que le RL est inutile si les références simples suffisent.

Ses limites sont tout aussi importantes : le rendement de marché Fama–French actuel est une série de recherche et non un instrument directement négociable ; `RV5` n'est ni une perte ni une fonction de décision ; sans coûts ou contraintes, choisir chaque jour une exposition peut se réduire à une règle myope. Le candidat ne doit donc pas être adopté avant d'avoir défini l'utilisateur, l'instrument, la chronologie d'exécution et les coûts.

## 3. Fondements mathématiques nécessaires

Les définitions ci-dessous suivent le cadre standard des processus de décision markoviens présenté notamment par [Sutton et Barto](http://incompleteideas.net/book/RLbook2020.pdf) et la théorie des MDP de [Puterman](https://doi.org/10.1002/9780470316887).

### 3.1 Processus de décision markovien

Un MDP peut être décrit par le quintuplet :

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},P,R,\gamma),
$$

où :

- $\mathcal{S}$ est l'espace des états ;
- $\mathcal{A}$ est l'espace des actions ;
- $P(s'\mid s,a)$ est la loi de transition vers l'état suivant ;
- $R$ décrit la récompense ou son espérance conditionnelle ;
- $\gamma\in[0,1]$ est le facteur d'actualisation dans un problème à horizon actualisé.

La propriété de Markov exige que, conditionnellement à l'état et à l'action présents, le passé n'ajoute pas d'information nécessaire à la loi de l'état suivant :

$$
\Pr(S_{t+1}=s'\mid S_0,A_0,\ldots,S_t=s,A_t=a)
=P(s'\mid s,a).
$$

Cette propriété ne signifie pas que les marchés « oublient » le passé. Elle signifie que l'état construit doit résumer toute l'information passée pertinente. En finance, cet état pourrait devoir inclure les observations de marché, la position précédente, la richesse, les coûts accumulés, le temps restant et les contraintes. Déclarer arbitrairement que quelques rendements constituent un état markovien serait une hypothèse forte, pas un fait.

### 3.2 État, observation et action en finance

Pour une gestion d'exposition simple, une formulation illustrative — non validée — pourrait distinguer :

$$
S_t=(X_t,W_t,H_{t-1},C_t),
$$

avec $X_t$ information de marché, $W_t$ richesse, $H_{t-1}$ position héritée et $C_t$ état des contraintes. L'action $A_t$ serait la nouvelle exposition souhaitée. La transition intégrerait le rendement suivant et le coût du changement $A_t-H_{t-1}$.

Cette écriture montre pourquoi la position précédente importe : avec un coût de transaction $\kappa |A_t-H_{t-1}|$, deux investisseurs observant le même marché mais partant de positions différentes ne font pas nécessairement face à la même décision.

### 3.3 Politique et trajectoire

Une politique $\pi$ associe un état à une distribution d'actions :

$$
\pi(a\mid s)=\Pr(A_t=a\mid S_t=s).
$$

Une politique déterministe est un cas particulier $A_t=\mu(S_t)$. Une politique stochastique n'est pas automatiquement préférable ; elle peut servir à l'exploration ou représenter une décision aléatoire, mais cette randomisation doit avoir une justification financière.

Une trajectoire est la suite :

$$
\tau=(S_0,A_0,R_1,S_1,A_1,R_2,\ldots).
$$

Le retour actualisé depuis `t` est :

$$
G_t=\sum_{k=0}^{T-t-1}\gamma^k R_{t+k+1}
$$

pour un horizon fini $T$. Le facteur $\gamma$ donne moins de poids aux conséquences lointaines, mais il ne doit pas être choisi seulement par habitude algorithmique. Pour un mandat financier à horizon défini, un problème à horizon fini avec objectif terminal peut être plus interprétable que l'actualisation géométrique.

### 3.4 Fonctions de valeur

La valeur d'un état sous une politique est le retour conditionnel espéré :

$$
V^{\pi}(s)=\mathbb{E}_{\pi}[G_t\mid S_t=s].
$$

La valeur état-action est :

$$
Q^{\pi}(s,a)=\mathbb{E}_{\pi}[G_t\mid S_t=s,A_t=a].
$$

Interprétation financière : $Q^{\pi}(s,a)$ ne mesure pas seulement le gain de l'action courante. Il agrège le gain immédiat et les conséquences futures si l'on choisit `a` puis suit $\pi$. Cette différence est précisément ce qui pourrait justifier une méthode séquentielle lorsque les transactions ou contraintes ont des effets persistants.

### 3.5 Équations de Bellman

La décomposition récursive de la valeur donne :

$$
V^{\pi}(s)=\sum_a \pi(a\mid s)
\sum_{s'}P(s'\mid s,a)
\left[r(s,a,s')+\gamma V^{\pi}(s')\right].
$$

L'équation d'optimalité s'écrit :

$$
V^*(s)=\max_a
\sum_{s'}P(s'\mid s,a)
\left[r(s,a,s')+\gamma V^*(s')\right].
$$

La première équation **évalue** une politique fixée. La seconde cherche l'action qui maximise la valeur en tenant compte de la meilleure continuation future. Financièrement, elle compare une action non seulement par son rendement immédiat, mais par l'état de portefeuille et les possibilités qu'elle laisse ensuite.

L'équation de Bellman ne garantit pas qu'un problème réel soit bien spécifié. Une mauvaise définition de l'état, des transitions ou de la récompense peut produire une solution mathématiquement cohérente mais financièrement dépourvue de sens.

### 3.6 Observabilité partielle et POMDP

Le véritable état économique — anticipations, liquidité latente, tolérance au risque des investisseurs ou mécanisme générateur des rendements — n'est pas directement observé. Un POMDP ajoute une observation $O_t$ générée conditionnellement à un état latent. Le décideur agit à partir d'un **état de croyance** :

$$
b_t(s)=\Pr(S_t=s\mid O_{0:t},A_{0:t-1}).
$$

La mise à jour de $b_t$ combine transition et vraisemblance de la nouvelle observation. En théorie, cette croyance peut servir d'état markovien. En pratique, elle doit être estimée, et une erreur de modèle peut créer une confiance artificielle. Les POMDP fournissent un langage utile pour l'information économique incomplète ; ils ne justifient pas automatiquement un réseau récurrent ou une architecture complexe. Voir [Kaelbling, Littman et Cassandra, 1998](https://www.cassandra.org/arc/papers/aij98.pdf).

### 3.7 Exploration et exploitation

L'exploration choisit parfois une action incertaine afin d'apprendre ses conséquences ; l'exploitation choisit l'action actuellement jugée meilleure. Sur un marché réel, explorer avec du capital peut être coûteux, risqué ou incompatible avec un mandat. Avec des données historiques fixes, l'agent ne peut pas générer librement les conséquences d'actions absentes des données.

Ce point rend l'**offline RL** conceptuellement pertinent mais difficile. Une politique nouvelle peut choisir des actions peu ou jamais représentées dans les données, et ses valeurs sont alors extrapolées hors distribution. [Levine et al., 2020](https://arxiv.org/abs/2005.01643) présentent ce déplacement de distribution comme une difficulté centrale. Ce problème est particulièrement grave si les données historiques ne contiennent même pas les actions d'une politique de portefeuille passée.

### 3.8 Contrôle optimal, programmation dynamique, bandits et RL

| Cadre | Modèle des transitions connu ? | Effet de l'action sur le futur ? | Objet principal | Quand il peut suffire |
|---|---:|---:|---|---|
| Optimisation statique | non requis | non modélisé | meilleure décision à une date | décision réellement indépendante ou réoptimisée sans coût de chemin |
| Contrôle optimal stochastique | généralement spécifié | oui | politique optimale sous un modèle | dynamique et préférences suffisamment connues |
| Programmation dynamique | oui ou estimé séparément | oui | résoudre récursivement un contrôle | espaces et modèle traitables |
| Contextual bandit | contexte observé, pas de transition contrôlée | pas de conséquence différée pertinente | meilleur choix conditionnel immédiat | action n'affectant pas l'état ou les choix suivants ; voir [Lattimore et Szepesvári, 2020](https://doi.org/10.1017/9781108571401) |
| Reinforcement Learning | dynamique inconnue ou partiellement inconnue | oui | apprendre une politique ou des valeurs par les données/interactions | effet séquentiel réel, données suffisantes et évaluation crédible |

Le RL n'est donc pas synonyme de contrôle optimal : le contrôle définit le problème, tandis que le RL désigne des méthodes d'apprentissage de solutions lorsque le modèle n'est pas entièrement connu. Une méthode de RL peut elle-même être model-free ou apprendre un modèle.

### 3.9 Apprendre une politique

L'apprentissage d'une politique peut suivre plusieurs logiques, sans qu'aucune soit encore retenue :

- **évaluer puis améliorer** : estimer $V^\pi$ ou $Q^\pi$ pour une politique, puis choisir des actions de plus grande valeur ;
- **optimiser directement une politique paramétrée** : ajuster les paramètres de $\pi_\theta(a\mid s)$ pour augmenter le retour attendu ;
- **apprendre un modèle** : estimer transitions et récompenses, puis planifier dans ce modèle ;
- **combiner politique et valeur** : utiliser une fonction de valeur pour guider l'optimisation de la politique.

Dans tous les cas, trois tâches doivent rester distinctes : apprendre à partir des données disponibles, sélectionner une politique et estimer honnêtement sa valeur hors échantillon. Une politique facile à optimiser dans l'historique peut être impossible à évaluer si elle choisit des actions hors du support des données. Le choix entre méthodes fondées sur la valeur, gradients de politique, actor–critic ou modèle appris est donc prématuré tant que le problème et les données ne sont pas fixés.

## 4. Quatre incertitudes à ne pas confondre

### 4.1 Incertitude prédictive

Elle concerne une quantité future : rendement, volatilité, perte ou coût. Elle comporte une part aléatoire irréductible et une part épistémique liée au modèle, aux paramètres et aux données. Une prévision ponctuelle de volatilité ne résume pas la distribution des rendements ni l'incertitude sur cette prévision.

### 4.2 Risque financier

Le risque dépend de la position et de l'objectif : perte, drawdown, violation de marge, risque de queue, liquidité ou écart à un budget. Une volatilité élevée peut accompagner une hausse ; elle n'est pas une perte. Le risque d'un portefeuille n'est pas identique à l'incertitude d'un modèle.

### 4.3 Contraintes de décision

Les bornes d'exposition, interdictions de vente à découvert, limites de levier, turnover, budget de risque et contraintes réglementaires définissent les actions admissibles. Les traiter comme de simples pénalités peut autoriser des violations si le poids de pénalité est mal choisi. Les MDP contraints offrent un cadre séparant un objectif des contraintes attendues ([Altman, 1999](https://www.routledge.com/Constrained-Markov-Decision-Processes/Altman/p/book/9780849303821)). Ce cadre est envisagé, pas adopté.

### 4.4 Incertitude sur l'environnement

Les relations entre états, actions et conséquences peuvent changer : volatilité, liquidité, coûts, corrélations et réponse du marché ne sont pas stationnaires. Un agent peut être très certain dans un modèle devenu faux. La robustesse à une famille de transitions relève d'une question différente de la simple estimation prédictive ; la programmation dynamique robuste formalise ce type d'incertitude ([Iyengar, 2005](https://doi.org/10.1287/moor.1040.0129)).

### 4.5 Conséquence pour notre projet

Une future politique ne devrait pas être déclarée « consciente du risque » uniquement parce que sa récompense soustrait une variance. Il faudra préciser :

- la variable financière que l'on veut contrôler ;
- l'horizon auquel elle importe ;
- le statut de chaque limite : objectif, préférence ou contrainte dure ;
- ce qui est connu à `t` ;
- la conséquence d'une violation ;
- la manière dont l'incertitude de modèle influence l'action.

Les objectifs sensibles au risque, par exemple ceux fondés sur la CVaR, existent dans la littérature RL ([Tamar, Glassner et Mannor, 2015](https://doi.org/10.1609/aaai.v29i1.9561)), mais leur existence ne suffit pas à choisir une fonction de récompense pour ce projet.

## 5. Cartographie conceptuelle des données

Cette section identifie des familles et des sources candidates ; elle n'autorise aucune collecte et ne fixe aucune variable.

### 5.1 Données pour observer l'environnement

| Famille | Signification et apport potentiel | Sources publiques candidates vérifiées | Fréquence et problèmes temporels | Risques méthodologiques |
|---|---|---|---|---|
| Actions et facteurs | rendement, dispersion, momentum, exposition au risque agrégé | [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/Ken.French/data_library.html) pour facteurs de recherche ; fournisseurs ou places de marché à auditer pour instruments négociables | quotidien ou inférieur ; corporate actions, horaires et changements de méthode | facteur non directement négociable, biais de survie selon l'univers, licences, millésimes |
| Taux souverains et courbe | coût sans risque, conditions monétaires, pente et duration | [U.S. Treasury Daily Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve), FRED/ALFRED | quotidien pour les taux ; ruptures de maturité et changement de méthode de courbe | valeurs indicatives, interpolation, maturités absentes, synchronisation avec la décision |
| Volatilité implicite | prix de l'incertitude sous mesure risque-neutre et demande de protection | [Cboe VIX Historical Data](https://www.cboe.com/tradable_products/vix/vix_historical_data) et documentation méthodologique | quotidien/intraday selon accès ; heure de clôture et changements méthodologiques | VIX n'est ni volatilité réalisée ni prévision sans biais ; historique et licences |
| Crédit | prime de défaut, tolérance au risque et fonctionnement du financement | [NY Fed CMDI](https://www.newyorkfed.org/research/policy/cmdi), certaines séries FRED, données publiques TRACE selon conditions FINRA | CMDI hebdomadaire publié mensuellement ; spreads parfois quotidiens | délais de publication, univers changeant, données propriétaires sous-jacentes |
| Liquidité et financement | coût de transaction, stress de financement, capacité à prendre ou réduire une position | [OFR Financial Stress Index](https://www.financialresearch.gov/financial-stress-index/), [OFR Short-term Funding Monitor](https://www.financialresearch.gov/short-term-funding-monitor/), taux de référence NY Fed | quotidien à mensuel ; l'OFR FSI est publié avec deux jours ouvrés de retard | indice composite, révisions, changement LIBOR/SOFR, disponibilité réelle à `t` |
| Macroéconomie | inflation, activité, emploi, politique monétaire ; contexte plus lent que le marché | [ALFRED](https://alfred.stlouisfed.org/) pour millésimes, organismes producteurs comme BLS/BEA/Fed | mensuel ou trimestriel, publié avec retard puis révisé | utiliser la dernière valeur révisée crée une fuite ; fréquence mal alignée ; surprises plutôt que niveaux parfois pertinentes |
| Cycles économiques | annotation rétrospective des expansions et récessions | [NBER Business Cycle Dating](https://www.nber.org/research/business-cycle-dating) | mensuel, annoncé plusieurs mois après le retournement | diagnostic ex post, jamais signal disponible à la date historique du retournement |
| Autres classes d'actifs | diversification et transmission des risques : obligations, devises, matières premières, immobilier | [BIS Data Portal](https://data.bis.org/topics), banques centrales, organismes statistiques, fournisseurs à auditer | quotidien à trimestriel, calendriers et fuseaux différents | conversions de devises, contrats futures, roulements, univers et licences |

Une source « publique » n'est pas nécessairement libre de redistribution ni disponible avec les mêmes conditions sur tout l'historique. Chaque série éventuellement retenue devra avoir un dictionnaire, une licence, un calendrier de publication, un millésime et une règle d'alignement.

### 5.2 Données nécessaires pour évaluer les décisions

Les variables servant à observer l'environnement ne suffisent pas. Une évaluation financière exige potentiellement :

- rendements effectivement réalisables de l'instrument choisi ;
- prix auxquels la décision peut raisonnablement être exécutée après l'observation ;
- spreads, commissions, impact et coûts d'emprunt ;
- position précédente, turnover et contraintes ;
- taux de financement et rémunération du collatéral ;
- richesse et trajectoire de drawdown ;
- événements de corporate action, roulements de futures ou échéances de dérivés.

Ces données déterminent la récompense réalisée et la faisabilité, mais ne doivent pas toutes devenir des variables d'état. Par exemple, un coût ex post peut servir à évaluer une décision sans avoir été parfaitement connu avant l'ordre ; dans ce cas, seule une estimation disponible à `t` peut guider la politique.

### 5.3 Le problème spécifique des données hors ligne

Un historique de prix montre ce qui s'est passé sur le marché, mais pas nécessairement ce qui se serait passé sous une autre politique. Pour un petit investisseur supposé sans impact, on peut considérer les rendements de marché comme exogènes et recalculer mécaniquement la richesse de politiques alternatives. Cette hypothèse devient moins crédible pour l'exécution, les actifs illiquides ou les grandes positions.

L'off-policy evaluation vise à estimer la valeur d'une politique à partir de trajectoires produites par une autre politique. Des estimateurs dédiés existent ([Jiang et Li, 2016](https://proceedings.mlr.press/v48/jiang16.html) ; [Thomas, Theocharous et Ghavamzadeh, 2015](https://doi.org/10.1609/aaai.v29i1.9541)), mais ils exigent des hypothèses de support et souvent la connaissance des probabilités d'action de la politique comportementale. Une simple série de prix sans actions historiques ne satisfait pas automatiquement ces conditions.

## 6. Quand le RL apporterait-il réellement quelque chose ?

### 6.1 Test de nécessité avant tout algorithme

Le RL ne devrait être envisagé que si les réponses aux questions suivantes sont positives :

1. Existe-t-il plusieurs décisions successives liées par un état persistant ?
2. L'action présente modifie-t-elle les coûts, contraintes, positions ou possibilités futures ?
3. Le critère financier dépend-il du chemin, et pas seulement d'un gain immédiat ?
4. Un modèle classique fiable des transitions est-il indisponible ou trop restrictif ?
5. Les données couvrent-elles suffisamment les états et actions que la politique pourrait choisir ?
6. Peut-on évaluer honnêtement une politique sans supposer le résultat recherché ?

Si l'une des trois premières réponses est négative, une méthode plus simple est probablement préférable. Si les trois dernières sont négatives, le RL peut être conceptuellement adapté mais empiriquement non identifiable.

### 6.2 Alternatives obligatoires

| Alternative | Question qu'elle permet de trancher | Ce qu'un RL devrait démontrer en plus |
|---|---|---|
| Exposition constante | la dynamique apporte-t-elle quelque chose ? | amélioration nette et robuste sans prendre simplement plus de risque |
| Règle financière fixe | une relation économique simple suffit-elle ? | gain au-delà d'une règle transparente préspécifiée |
| Ciblage de volatilité | utiliser directement une estimation de risque suffit-il ? | meilleure maîtrise du risque après coûts, sans instabilité excessive |
| Optimisation statique répétée | l'effet de chemin est-il matériel ? | bénéfice attribuable à la prise en compte du futur, pas à un meilleur prédicteur |
| Contrôleur dynamique traditionnel | l'apprentissage de la dynamique est-il nécessaire ? | robustesse lorsque le modèle classique est mal spécifié |
| Contextual bandit | les actions ont-elles des conséquences différées ? | valeur du crédit temporel au-delà de la récompense immédiate |
| Politique déterministe simple et bornée | la flexibilité est-elle utile ? | amélioration reproductible suffisante pour justifier opacité et variance |

Une publication ancienne applique déjà un apprentissage direct à des portefeuilles et systèmes de trading ([Moody et Saffell, 2001](https://doi.org/10.1109/72.935097)). Les revues récentes montrent que portefeuille, trading, exécution et pricing ont tous été étudiés avec le RL ([Hambly, Xu et Yang, 2023](https://doi.org/10.1111/mafi.12382)). La présence de cette littérature interdit de présenter une simple application d'un algorithme standard comme une nouveauté.

## 7. Fonction de récompense : le principal risque de confusion

Une récompense illustrative pourrait prendre la forme :

$$
R_{t+1}=A_t r_{t+1}-\kappa |A_t-A_{t-1}|-\lambda\,\ell_{t+1},
$$

où $A_t r_{t+1}$ est le rendement de la position, le deuxième terme un coût de rotation et $\ell$ une pénalité de risque. Cette formule n'est **pas** proposée comme choix final.

Elle révèle plusieurs arbitrages :

- modifier $\lambda$ change le problème économique, pas seulement un hyperparamètre ;
- une pénalité quadratique peut masquer les pertes de queue ;
- une récompense quotidienne additive ne représente pas directement un drawdown maximal ou une probabilité de ruine ;
- transformer une contrainte dure en pénalité permet parfois sa violation ;
- le ratio de Sharpe n'est pas additif période par période et son optimisation estimée peut être instable ;
- maximiser le rendement net n'est pas synonyme de contrôler le risque.

Avant tout apprentissage, il faudra écrire la décision sous une forme financière compréhensible : objectif principal, contraintes, horizon, valeur terminale et coûts. Le choix de la récompense devra être traité comme une hypothèse économique à défendre.

## 8. Risques scientifiques majeurs

### 8.1 Surajustement du backtest

Le nombre de choix possibles explose rapidement : état, horizon, action, récompense, coûts, architecture, graine et hyperparamètres. Sélectionner la meilleure combinaison sur les mêmes périodes produit un biais de recherche. Les travaux sur le backtest overfitting montrent pourquoi un holdout réutilisé ne protège plus après de nombreux essais ([Bailey et al., 2015](https://doi.org/10.2139/ssrn.2326253)). Le registre des essais et une période véritablement gelée seront indispensables.

### 8.2 Non-stationnarité

Une politique peut apprendre des corrélations propres à une structure de marché, une réglementation ou un régime de coûts. La performance moyenne masque les transitions. Une adaptation en ligne n'est pas automatiquement une solution : elle peut amplifier le bruit ou oublier des situations rares.

### 8.3 Observabilité partielle

Un état mal défini peut faire croire à une dynamique markovienne inexistante. Ajouter davantage de variables ne résout pas nécessairement le problème et augmente le risque de surajustement.

### 8.4 Récompense mal spécifiée

L'agent optimise exactement le signal fourni, pas l'intention du chercheur. Une récompense peut encourager levier, rotation, concentration ou report du risque hors de l'horizon mesuré.

### 8.5 Données historiques limitées et événements rares

Une longue série quotidienne fournit beaucoup de lignes mais peu de crises, changements institutionnels ou épisodes de liquidité indépendants. Les trajectoires chevauchantes ne multiplient pas l'information économique.

### 8.6 Simulateur irréaliste

Un environnement qui réutilise des rendements historiques tout en laissant l'agent négocier sans impact, avec coût constant et liquidité infinie, peut être utile comme abstraction mais ne doit pas être qualifié de marché réaliste. Un modèle génératif sophistiqué peut aussi reproduire ses propres hypothèses plutôt que les risques réels.

### 8.7 Fuite temporelle

Les risques incluent : indicateurs révisés, normalisation sur tout l'échantillon, univers connu ex post, prix de clôture utilisé à la fois comme observation et prix d'exécution, cibles chevauchant les frontières, coûts estimés avec des données futures et sélection d'une politique après consultation du test.

### 8.8 Évaluation contrefactuelle

La politique candidate choisit des actions différentes de celles ayant produit les données. Sans hypothèse d'exogénéité, simulateur crédible ou support suffisant, sa valeur n'est pas observable. Les méthodes d'évaluation hors politique réduisent certains biais, mais ne créent pas l'information absente.

### 8.9 Écart entre simulation et utilité financière

Un Sharpe ratio simulé supérieur ne garantit ni respect des contraintes, ni capacité d'exécution, ni robustesse, ni valeur pour un utilisateur. La comparaison doit rapporter rendement, pertes, exposition, turnover, coûts et violations séparément avant toute agrégation.

### 8.10 Périodes déjà consultées

Les périodes 2016–2019 et 2020–août 2026 ont déjà orienté le projet principal. Elles peuvent servir au développement ou à l'illustration, jamais à une confirmation finale intacte d'une politique conçue après leur examen.

## 9. Trajectoire scientifique progressive

Cette trajectoire est une suite de portes décisionnelles, pas un calendrier automatique.

### Étape 1 — Maîtriser le problème mathématique

**Question :** quelles propriétés rendent notre décision réellement séquentielle ?

Livrable éventuel : formulation sur papier d'un état, d'une action, d'une transition, d'un objectif et de contraintes, accompagnée d'un contre-exemple où un bandit ou une règle myope suffit. Aucun code n'est requis.

**Condition de passage :** pouvoir expliquer pourquoi l'action à `t` change la valeur des actions futures.

### Étape 2 — Choisir un problème financier et un utilisateur

**Question :** quelle décision concrète et quel coût d'erreur cherchons-nous à améliorer ?

Comparer au minimum exposition dynamique, allocation et couverture. Définir instrument, fréquence, calendrier d'exécution, horizon, levier, contraintes et coûts.

**Condition de passage :** le problème reste pertinent même si le RL est finalement rejeté.

### Étape 3 — Auditer les données

**Question :** quelles informations étaient réellement disponibles à chaque décision et quelles données mesurent les conséquences ?

Audit attendu : provenance, licence, millésime, publication, révision, fuseau, fréquence, valeurs manquantes, univers, corporate actions et faisabilité d'une période non consultée.

**Condition de passage :** aucune variable ne dépend implicitement du futur et l'instrument évalué est économiquement interprétable.

### Étape 4 — Construire les références classiques

**Question :** une règle simple ou un contrôleur classique résout-il déjà le problème ?

Ordre minimal : absence d'action dynamique, règle fixe, cible de volatilité ou optimisation classique, puis éventuellement bandit si le futur n'est pas affecté.

**Condition de passage :** un besoin séquentiel non couvert reste visible.

### Étape 5 — Évaluer la pertinence empirique du RL

**Question :** les données permettent-elles d'apprendre et d'évaluer une politique nouvelle sans extrapolation incontrôlée ?

Examiner support des actions, nombre de trajectoires, non-stationnarité, possibilité d'évaluation hors politique et réalisme d'un éventuel simulateur.

**Condition de passage :** la méthode est identifiable et falsifiable.

### Étape 6 — Expérience minimale, seulement si autorisée

Une seule formulation, un espace d'action réduit, un algorithme simple et des références fortes. Le protocole, les métriques, la période de validation et les critères d'échec seraient fixés avant l'exécution.

### Étape 7 — Robustesse et généralisation

Seulement après un résultat initial compréhensible : coûts, sous-périodes, changements de marché, graines, choix voisins raisonnables et période réellement indépendante. Une multiplication post hoc de variantes ne remplacerait pas une validation.

## 10. Hypothèses de travail et critères d'abandon

### Hypothèses envisageables, non validées

- **H-RL1 :** lorsque les coûts de rotation et contraintes rendent l'état de portefeuille persistant, une politique tenant compte du futur peut améliorer le contrôle du risque net de coûts par rapport à une règle myope.
- **H-RL2 :** une meilleure prévision ponctuelle de volatilité ne conduit pas nécessairement à une meilleure politique d'exposition.
- **H-RL3 :** dans des données financières hors ligne et non stationnaires, la flexibilité d'une politique apprise peut dégrader la généralisation par rapport à une règle simple.

### Résultats qui affaibliraient la justification du RL

- les actions n'affectent pas les transitions ni l'ensemble des décisions futures ;
- une règle déterministe simple égale ou dépasse la politique après coûts ;
- les gains disparaissent avec un calendrier d'exécution réaliste ;
- la politique exploite principalement une fuite, une période ou un actif particulier ;
- les actions proposées sont hors du support des données historiques ;
- les résultats changent qualitativement selon des choix mineurs de récompense ;
- aucune période ou procédure d'évaluation crédible ne peut être réservée.

Un abandon du RL pour un problème donné serait un résultat scientifique, pas un échec du projet.

## 11. Premières questions à étudier ensemble

Avant toute nouvelle phase, cinq arbitrages sont prioritaires :

1. **Décision :** souhaitons-nous approfondir d'abord l'exposition dynamique, l'allocation multi-actifs ou un autre problème ?
2. **Utilisateur :** gestionnaire visant un budget de risque, investisseur long terme, responsable de couverture ou autre ?
3. **Nature du risque :** volatilité, perte de queue, drawdown, violation de contrainte ou combinaison explicitement hiérarchisée ?
4. **Structure séquentielle :** quels coûts ou états persistants rendent une décision myope insuffisante ?
5. **Évaluation :** quelle période ou quel mécanisme pourra rester réellement non consulté ?

### Recommandation limitée

La première discussion devrait comparer mathématiquement deux formulations stylisées de la gestion d'exposition :

- une décision quotidienne indépendante, sans coûts ni état de portefeuille ;
- la même décision avec position héritée, coût de rotation et contrainte d'exposition.

Cette comparaison permettrait de déterminer si le problème exige un MDP ou peut rester une règle statique/contextuelle. Elle ne nécessite encore ni donnée, ni notebook, ni algorithme RL. Le choix de poursuivre cette question appartient au porteur du projet.

## 12. Références examinées

### Fondements

- Sutton, R. S. et Barto, A. G. (2018), *Reinforcement Learning: An Introduction*, 2e éd. [Texte des auteurs](http://incompleteideas.net/book/RLbook2020.pdf).
- Puterman, M. L. (1994), *Markov Decision Processes: Discrete Stochastic Dynamic Programming*. [DOI](https://doi.org/10.1002/9780470316887).
- Kaelbling, L. P., Littman, M. L. et Cassandra, A. R. (1998), « Planning and Acting in Partially Observable Stochastic Domains ». [Article](https://www.cassandra.org/arc/papers/aij98.pdf).
- Altman, E. (1999), *Constrained Markov Decision Processes*. [Éditeur](https://www.routledge.com/Constrained-Markov-Decision-Processes/Altman/p/book/9780849303821).
- Lattimore, T. et Szepesvári, C. (2020), *Bandit Algorithms*. [DOI](https://doi.org/10.1017/9781108571401) ; [édition en accès libre](https://tor-lattimore.com/downloads/book/book.pdf).

### RL hors ligne, risque et robustesse

- Levine, S., Kumar, A., Tucker, G. et Fu, J. (2020), « Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems ». [arXiv](https://arxiv.org/abs/2005.01643).
- Jiang, N. et Li, L. (2016), « Doubly Robust Off-policy Value Evaluation for Reinforcement Learning ». [PMLR](https://proceedings.mlr.press/v48/jiang16.html).
- Thomas, P., Theocharous, G. et Ghavamzadeh, M. (2015), « High-Confidence Off-Policy Evaluation ». [AAAI](https://doi.org/10.1609/aaai.v29i1.9541).
- Tamar, A., Glassner, Y. et Mannor, S. (2015), « Optimizing the CVaR via Sampling ». [AAAI](https://doi.org/10.1609/aaai.v29i1.9561).
- Iyengar, G. N. (2005), « Robust Dynamic Programming ». [DOI](https://doi.org/10.1287/moor.1040.0129).

### Finance et évaluation

- Davis, M. H. A. et Norman, A. R. (1990), « Portfolio Selection with Transaction Costs ». [DOI](https://doi.org/10.1287/moor.15.4.676).
- Moody, J. et Saffell, M. (2001), « Learning to Trade via Direct Reinforcement ». [DOI](https://doi.org/10.1109/72.935097).
- Moreira, A. et Muir, T. (2017), « Volatility-Managed Portfolios ». [DOI](https://doi.org/10.1111/jofi.12513).
- Hambly, B., Xu, R. et Yang, H. (2023), « Recent Advances in Reinforcement Learning in Finance ». [DOI](https://doi.org/10.1111/mafi.12382) ; [version auteur](https://people.maths.ox.ac.uk/~hambly/PDF/Papers/RL-finance.pdf).
- Bailey, D. H., Borwein, J. M., López de Prado, M. et Zhu, Q. J. (2015), « The Probability of Backtest Overfitting ». [SSRN/DOI](https://doi.org/10.2139/ssrn.2326253).

### Sources de données documentaires

- [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/Ken.French/data_library.html).
- [ALFRED — Archival FRED](https://alfred.stlouisfed.org/) et [documentation API](https://fred.stlouisfed.org/docs/api/fred/alfred.html).
- [U.S. Treasury — Daily Treasury Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve).
- [Cboe — VIX Historical Data](https://www.cboe.com/tradable_products/vix/vix_historical_data).
- [Office of Financial Research — Financial Stress Index](https://www.financialresearch.gov/financial-stress-index/).
- [Federal Reserve Bank of New York — Corporate Bond Market Distress Index](https://www.newyorkfed.org/research/policy/cmdi).
- [BIS Data Portal](https://data.bis.org/topics).
- [NBER — Business Cycle Dating](https://www.nber.org/research/business-cycle-dating).

Les articles en accès direct et les pages officielles de données ont été examinés pour ce cadrage. Pour certains ouvrages, seuls la référence bibliographique, la table des matières ou les éléments accessibles ont pu être vérifiés ; ils ne sont pas présentés comme intégralement consultés. Aucune donnée n'a été téléchargée.
