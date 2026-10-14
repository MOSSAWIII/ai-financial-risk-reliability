# Phase 0 — cadrage scientifique révisé

**Version :** 2, 15 octobre 2026

**Statut :** Phase 0 non validée ; proposition soumise à nouvel examen critique

**Portée :** aucun téléchargement, calcul, modèle ou résultat empirique nouveau

## 1. Critique substantielle de la version 1

La première version respectait les garde-fous temporels et reproductibles, mais
elle répondait trop vite à une question qui n'était pas encore suffisamment
fondée. Elle doit être corrigée sur six points.

1. **Elle a confondu objet empirique et objet scientifique.** La variance à cinq
   séances peut être un instrument d'étude ; elle n'est pas, par elle-même, le
   phénomène à comprendre. Le phénomène est la perte de fiabilité d'une
   prévision lorsque les relations économiques et financières évoluent.
2. **Elle a organisé le projet comme une compétition de modèles.** La première
   expérience EWMA contre Boosting traitait une faiblesse du prototype, mais ne
   répondait pas à la question économique centrale. Une comparaison équitable
   est une condition de validité, pas une contribution scientifique.
3. **Elle a relégué l'économie et la finance.** Les mécanismes économiques
   étaient remplacés par de futures « variables macro » ; la conséquence
   financière était reportée à un backtest tardif. Cela rompait la chaîne entre
   cause plausible, erreur de prévision et décision affectée.
4. **Elle a assimilé plusieurs notions de régime.** Un changement de volatilité,
   un changement économique, une rupture de distribution et une panne de modèle
   ne sont pas équivalents. L'un peut survenir sans les autres.
5. **Elle a figé des moyens avant les fins.** Variance, QLIKE, réestimation
   annuelle, bootstrap de 22 séances et marché externe étaient raisonnables,
   mais présentés comme directeurs sans démontrer qu'ils correspondaient à la
   décision financière et à l'hypothèse testée.
6. **Elle a produit une feuille de route trop large.** La succession E0–E6
   décrivait un programme technique possible plutôt qu'une enquête où chaque
   étape dépend du résultat précédent.

Ces défauts ne rendent pas inutiles les précautions proposées. La disponibilité
à la date `t`, la contamination de 2020–août 2026, l'immuabilité des données
brutes et l'équité des comparaisons restent des contraintes valides. En revanche,
les choix contestés sont rouverts. Leur statut historique est conservé dans le
journal des décisions et dans Git.

## 2. Phénomène et problématique scientifique

### Le phénomène que nous cherchons à comprendre

Une prévision de risque est apprise dans un environnement où certaines relations
sont suffisamment régulières : persistance du risque, réaction aux rendements
passés, structure des nouvelles, liquidité et comportement des intermédiaires.
Quand l'environnement change, trois choses peuvent arriver :

- le risque augmente mais les relations prédictives restent valides ;
- les relations changent et le modèle devient systématiquement retardé ou mal
  calibré ;
- l'incertitude devient elle-même difficile à estimer, de sorte qu'un système
  continue d'afficher une confiance injustifiée.

Le second et le troisième cas constituent le cœur du projet. Une forte
volatilité n'est pas nécessairement une panne : un modèle peut prévoir
correctement un état durablement agité. Inversement, une transition encore peu
volatile peut déjà rendre ses relations historiques moins fiables.

### Question centrale révisée

> Pourquoi et dans quelles conditions économico-financières une prévision du
> risque de marché, jusque-là utilisable, cesse-t-elle d'être fiable ; peut-on
> reconnaître ou anticiper cette dégradation avec l'information disponible au
> moment de la décision ; et cette information permet-elle à un gestionnaire de
> risque d'agir plus prudemment sans renoncer inutilement à toute exposition ?

Cette question ne suppose ni qu'un modèle d'IA soit nécessaire, ni qu'une
adaptation automatique soit possible. Elle articule :

- une **explication économique** des changements possibles ;
- une **conséquence financière** définie par une décision sous pertes
  asymétriques ;
- un **problème d'IA/statistique** : savoir quand une prédiction et son
  incertitude ne méritent plus le même degré de confiance.

### Ce que signifierait un résultat négatif

Même si aucun modèle ML ne dépasse un modèle traditionnel, la recherche peut :

- établir que les défaillances sont liées au niveau de risque plutôt qu'aux
  transitions, ce qui affaiblirait la thèse de dérive ;
- montrer qu'une dégradation n'est pas anticipable avec l'information retenue ;
- quantifier le coût d'une confiance excessive et la valeur éventuelle d'un
  avertissement ou d'une abstention ;
- délimiter les conditions dans lesquelles la complexité adaptative n'apporte
  rien de robuste.

Ce seraient des conclusions scientifiques, pas des échecs du projet.

## 3. Quatre notions à ne plus confondre

| Notion | Définition de travail | Ce qu'elle ne prouve pas |
|---|---|---|
| Environnement économique | état des anticipations de croissance, inflation, politique monétaire, incertitude et financement | qu'une rupture statistique est déjà observable |
| État financier | niveau de volatilité, liquidité, levier, primes et corrélations observables | la cause économique de cet état |
| Régime statistique | stabilité ou changement de la distribution et des relations entre prédicteurs et risque futur | qu'un mécanisme causal précis agit |
| Dégradation du modèle | hausse conditionnelle de perte, biais, sous-couverture ou confiance mal alignée | que tout le marché a changé de régime |

Le terme « transition » devra toujours préciser laquelle de ces notions est
visée. Une annotation NBER, un détecteur de rupture et une hausse de volatilité
ne sont donc pas des mesures interchangeables.

## 4. Articulation réelle entre économie, finance et IA

La chaîne scientifique proposée est :

> mécanisme économique plausible → transmission financière → modification des
> relations prédictives → erreur coûteuse pour une décision → besoin de
> diagnostic, d'incertitude ou d'adaptation.

Nous retenons trois familles de mécanismes, suffisamment distinctes pour générer
des observations différentes sans prétendre couvrir toute la macrofinance.

### Mécanisme A — nouvelles sur les flux futurs et les taux d'actualisation

**Logique économique.** Le prix des actions dépend des flux de trésorerie futurs
attendus et des taux auxquels ils sont actualisés. Une modification des
anticipations de croissance, d'inflation ou de politique monétaire peut changer
leur niveau, leur dispersion et leur sensibilité aux annonces. Schwert (1989)
relie la volatilité à l'activité, aux variables nominales et au levier, tout en
montrant qu'aucun facteur simple n'explique une part dominante de ses variations.

**Transmission financière attendue.** Révision simultanée des prix, des taux et
des primes ; volatilité plus forte autour des nouvelles ; possibles changements
de corrélations entre actifs.

**Pourquoi la prévisibilité peut changer.** Un modèle ajusté dans une période de
réactions monétaires stables peut sous-estimer l'effet d'une annonce lorsque la
fonction de réaction, l'inflation dominante ou la sensibilité des valorisations
change. Le problème est alors la stabilité des coefficients, pas seulement la
hausse du niveau de volatilité.

**Observations discriminantes, plus tard.** Surprises macro datées, courbe des
taux connue à `t`, dispersion des prévisions et millésimes de données ; comparer
les erreurs autour des annonces et des changements de relation, conditionnellement
au niveau de risque passé.

**Limite causale.** Une association entre erreurs, inflation ou taux ne sépare
pas les nouvelles sur les flux, les primes de risque et la réaction de politique
monétaire. Sans choc identifié ou autre stratégie crédible, nous conclurions à
une association prédictive, pas à une cause.

### Mécanisme B — incertitude, désaccord et apprentissage sur un environnement nouveau

**Logique économique.** Lors d'un choc inhabituel, les agents ignorent parfois
quel scénario ou quelle règle est pertinente. Bloom (2009) formalise des chocs
d'incertitude qui retardent investissement et embauche ; Schwert souligne aussi
que l'incertitude sur la nature même d'un régime ne se résume pas à sa variance
historique.

**Transmission financière attendue.** Dispersion accrue des croyances,
réévaluations discontinues et possibles sauts de prix. Deux périodes de même
volatilité passée peuvent alors différer fortement par la gamme de scénarios
envisagés.

**Pourquoi la prévisibilité peut changer.** Les exemples historiques proches du
nouvel état sont rares ; les résidus peuvent changer avant que leur moyenne
glissante ne le révèle ; une calibration apprise en environnement familier peut
devenir trop confiante.

**Observations discriminantes, plus tard.** Dispersion des prévisionnistes,
ampleur des surprises, fréquence des sauts, largeur des distributions implicites
et erreurs de couverture. Une dégradation présente à volatilité passée égale,
mais croissante avec désaccord ou surprise, serait plus compatible avec ce
mécanisme qu'avec un simple effet d'échelle.

**Limite causale.** Les mesures d'incertitude sont souvent construites à partir
des prix mêmes que nous voulons expliquer. La simultanéité et les variables
omises empêchent une interprétation causale automatique.

### Mécanisme C — levier, contraintes de financement et spirales de liquidité

**Logique économique.** Des pertes réduisent les fonds propres, resserrent les
contraintes et peuvent provoquer des ventes. Brunnermeier et Pedersen (2009)
montrent comment liquidité de financement et liquidité de marché peuvent se
renforcer ; Adrian et Shin (2010) documentent un levier d'intermédiaires
procyclique et un lien entre bilan des dealers et risque de marché.

**Transmission financière attendue.** Asymétrie après rendements négatifs,
assèchement de liquidité, hausse conjointe des corrélations et de la volatilité,
avec amplification non linéaire d'un choc initial.

**Pourquoi la prévisibilité peut changer.** Une dynamique autorégressive
calibrée en temps normal ne représente pas nécessairement un mécanisme de ventes
forcées ou de marges qui s'active au franchissement d'une contrainte. La vitesse
du changement, et non son niveau final, devient essentielle.

**Observations discriminantes, plus tard.** Erreurs asymétriques après baisses,
spreads et profondeur de marché, mesures de financement, levier des
intermédiaires et mouvements communs entre actifs. Si l'effet de transition
disparaît en contrôlant les grands rendements mais pas la liquidité, les
interprétations diffèrent.

**Limite causale.** Volatilité, marges, levier et liquidité se déterminent
conjointement. Des données observationnelles peuvent tester la cohérence d'un
mécanisme, non identifier seules le sens causal.

Ces mécanismes peuvent coexister. Le but n'est pas de choisir immédiatement une
variable par mécanisme, mais de formuler des implications qui permettront plus
tard de départager des explications.

## 5. Justification financière : une décision concrète

### Utilisateur de référence proposé

Le cas d'usage le plus cohérent avec le portefeuille de marché Fama–French est
un **gestionnaire du risque d'une exposition actions diversifiée** qui révise à
courte fréquence un budget de risque ou une borne d'exposition. Il ne s'agit pas
encore d'un trader cherchant un alpha ni d'un calcul réglementaire de capital.

La décision stylisée est : maintenir, réduire ou différer l'exposition lorsque
le risque prévu et la confiance accordée à cette prévision changent. Ce choix
justifie d'étudier une prévision de court horizon, mais ne valide pas encore
précisément cinq séances.

### Asymétrie des erreurs

- **Sous-prévoir** peut laisser une exposition trop élevée, provoquer un
  dépassement de budget de risque, aggraver un drawdown ou créer un besoin de
  réduction forcée au pire moment.
- **Sur-prévoir** réduit inutilement l'exposition, sacrifie une prime de risque
  potentielle et peut accroître le turnover si les alertes sont instables.
- **Changer trop souvent d'avis** est coûteux même si l'erreur moyenne est
  faible.
- **Afficher une confiance excessive** est distinct d'une mauvaise prévision
  ponctuelle : le décideur ne sait pas qu'il devrait ralentir, demander une
  marge de sécurité ou s'abstenir.

Une baisse moyenne de MAE ne garantit donc pas une meilleure maîtrise du risque.
La prévision utile doit combiner : niveau de risque, biais de sous-prévision,
calibration ou honnêteté de l'incertitude, stabilité des alertes et capacité à
signaler les situations où elle est moins digne de confiance. La fonction de
perte décisionnelle exacte reste ouverte tant que les règles d'exposition,
contraintes et coûts ne sont pas définis.

Si le projet choisissait plutôt un responsable du capital réglementaire ou un
desk d'options, la cible, l'horizon et la fonction de perte devraient changer.
On ne peut donc pas justifier une métrique statistique avant de choisir
l'utilisateur.

## 6. Les six problèmes d'IA/statistique sont différents

| Objectif | Question propre | Information nécessaire | Échec caractéristique | Place proposée |
|---|---|---|---|---|
| Améliorer la précision | la prévision centrale est-elle plus proche en moyenne ? | cibles observées après coup | petit gain moyen, crises inchangées | secondaire |
| Détecter la dégradation | le modèle s'est-il déjà détérioré ? | erreurs récemment réalisées | alerte nécessairement retardée | diagnostic indispensable |
| Anticiper la dégradation | sait-on avant la cible que la confiance devrait baisser ? | signaux disponibles à `t` | faux signaux ou alerte trop tardive | cœur potentiel du projet |
| Quantifier l'incertitude | l'intervalle/distribution décrit-il honnêtement les issues ? | distribution prédictive et calibration | confiance excessive sous shift | cœur complémentaire |
| Maintenir la calibration | la propriété reste-t-elle acceptable pendant le changement ? | retour séquentiel des erreurs | couverture moyenne correcte mais locale mauvaise | question ultérieure |
| Adapter le modèle | quand et comment oublier, pondérer ou réentraîner ? | détection + règle d'intervention | adaptation au bruit, oubli utile | seulement si une dégradation exploitable est établie |

La littérature sur la dérive conceptuelle traite déjà l'apprentissage sous
contexte changeant ; Giacomini et Rossi (2009) distinguent détection et prévision
des ruptures de prévision ; Ovadia et al. (2019) montrent que l'incertitude peut
se dégrader sous changement de distribution ; Gibbs et Candès (2021) proposent
une adaptation de couverture en ligne. Aucun de ces résultats n'autorise à
affirmer qu'une méthode connue résout notre cas financier dépendant et
décisionnel.

### Priorité scientifique proposée

Le projet devrait d'abord étudier **la dégradation conditionnelle et son
anticipation**, puis seulement demander si une incertitude ou une adaptation la
réduit. Construire immédiatement un modèle adaptatif inverserait l'ordre de la
preuve : on ne sait pas encore si la panne est détectable, anticipable, générale
ou propre à un modèle.

## 7. Littérature : établi, ouvert, potentiel

Cette revue est ciblée, non systématique. « Non trouvé ici » ne signifie jamais
« absent de la littérature ».

### Ce que les sources examinées permettent d'établir

- La volatilité est persistante, asymétrique et pertinente pour les décisions
  financières ; des références simples et GARCH sont difficiles à battre de
  manière uniforme (Engle & Patton, 2001 ; Hansen & Lunde, 2005).
- Activité économique, incertitude, taux, levier et liquidité sont associés à
  la volatilité, mais aucune explication simple ne domine et l'identification
  causale est difficile (Schwert, 1989 ; Bloom, 2009 ; Brunnermeier & Pedersen,
  2009 ; Adrian & Shin, 2010).
- Les ruptures de performance prédictive et la dérive de concept sont des
  problèmes anciens, distincts de la seule comparaison moyenne de modèles
  (Widmer & Kubat, 1996 ; Giacomini & Rossi, 2009).
- Les effets des ruptures sur les prévisions de second moment, les GARCH à
  coefficients changeants et l'ajout de variables macrofinancières aux
  prévisions de volatilité ont déjà été étudiés. La performance de ces ajouts
  varie dans le temps et selon les actifs (Clements & Hendry, 2006 ; Frijns,
  Lehnert & Zwinkels, 2011 ; Christiansen, Schmeling & Schrimpf, 2012).
- Des travaux très récents conditionnent déjà la prévision du risque de queue
  de portefeuille sur des probabilités d'états économiques futurs (Jiao & Zhou,
  2026). « Ajouter le régime économique à la prévision » ne peut donc pas être
  revendiqué comme contribution en soi.
- Une incertitude bien calibrée en distribution d'entraînement peut se dégrader
  sous changement de distribution ; adaptation conforme et prédiction sélective
  sont déjà des champs actifs (Ovadia et al., 2019 ; Gibbs & Candès, 2021 ;
  Bates et al., 2021).
- L'utilité économique d'une prévision dépend de la décision, des coûts et des
  préférences, pas seulement d'une perte statistique (Fleming, Kirby & Ostdiek,
  2001 ; Moreira & Muir, 2017).

### Questions encore ouvertes pour notre projet

Nous ignorons encore :

1. si la dégradation observée est autre chose qu'un effet mécanique de niveau,
   de sauts rares ou d'un proxy bruité ;
2. si un signal disponible avant réalisation de la cible contient une
   information sur cette dégradation ;
3. si cette information est commune à plusieurs modèles ou seulement la faiblesse
   d'une règle trop lente ;
4. si un avertissement fiable apporte plus à la décision qu'une légère
   amélioration de prévision centrale ;
5. si une méthode existante répond déjà à cette combinaison précise de
   dépendance temporelle, transition économique et perte financière asymétrique.

### Contribution potentielle, sous conditions

Une contribution ne serait ni « utiliser le ML », ni « ajouter du conformal ».
Elle pourrait être : une caractérisation temps réel, économiquement interprétée
et décisionnellement évaluée des moments où une prévision de risque devient peu
fiable, accompagnée d'un mécanisme d'avertissement dont la valeur incrémentale
est démontrée face à des solutions simples.

Cette formulation reste une **hypothèse de contribution**. Elle exige une revue
bibliographique systématique dédiée aux ruptures de prévision de volatilité, à
la calibration conditionnelle financière et aux décisions avec abstention avant
toute revendication de nouveauté. La littérature déjà identifiée sur les
modèles de volatilité à changement de régime rend la barre de nouveauté élevée :
il faudra montrer que l'anticipation d'une *perte de fiabilité* apporte autre
chose que modéliser directement un régime de volatilité ou conditionner la
distribution future sur un état économique prévu.

### Sources primaires examinées à ce stade

- Schwert (1989), *Why Does Stock Market Volatility Change Over Time?*, DOI
  https://doi.org/10.1111/j.1540-6261.1989.tb02647.x — texte intégral consulté.
- Engle & Patton (2001), *What Good Is a Volatility Model?*, DOI
  https://doi.org/10.1088/1469-7688/1/2/305 — texte intégral consulté.
- Hansen & Lunde (2005), *Does Anything Beat a GARCH(1,1)?*, DOI
  https://doi.org/10.1002/jae.800 — texte intégral consulté.
- Patton (2011), *Volatility Forecast Comparison Using Imperfect Volatility
  Proxies*, DOI https://doi.org/10.1016/j.jeconom.2010.03.034 — texte intégral
  consulté.
- Bloom (2009), *The Impact of Uncertainty Shocks*, Econometrica 77, 623–685 —
  texte intégral identifié et résumé examiné.
- Brunnermeier & Pedersen (2009), *Market Liquidity and Funding Liquidity*, DOI
  https://doi.org/10.1093/rfs/hhn098 — article auteur et résumé examinés.
- Adrian & Shin (2010), *Liquidity and Leverage*, DOI
  https://doi.org/10.1016/j.jfi.2008.12.002 — version Federal Reserve examinée.
- Giacomini & Rossi (2009), *Detecting and Predicting Forecast Breakdowns*, DOI
  https://doi.org/10.1111/j.1467-937X.2009.00545.x — texte intégral consulté.
- Clements & Hendry (2006), *Forecasting with Breaks*, Handbook of Economic
  Forecasting, DOI https://doi.org/10.1016/S1574-0706(05)01012-8 — résumé
  éditeur examiné ; texte intégral à lire avant choix d'une procédure de rupture.
- Frijns, Lehnert & Zwinkels (2011), *Modeling Structural Changes in the
  Volatility Process*, Journal of Empirical Finance 18, 522–532 — résumé
  éditeur examiné ; texte intégral à lire avant toute revendication sur
  l'adaptation de volatilité.
- Christiansen, Schmeling & Schrimpf (2012), *A Comprehensive Look at Financial
  Volatility Prediction by Economic Variables*, BIS Working Paper 374 — résumé
  et version institutionnelle examinés ; publication finale à vérifier.
- Jiao & Zhou (2026), *Economic Conditions and Portfolio Tail Risk: A
  Probability-Weighted Simulation Approach*, Journal of Empirical Finance 87,
  101715, DOI https://doi.org/10.1016/j.jempfin.2026.101715 — article ouvert et
  résumé éditeur examinés ; lecture intégrale requise avant toute revendication
  de contribution sur les états économiques.
- Widmer & Kubat (1996), *Learning in the Presence of Concept Drift and Hidden
  Contexts*, DOI https://doi.org/10.1007/BF00116900 — texte et résumé examinés.
- Ovadia et al. (2019), *Can You Trust Your Model's Uncertainty?*, NeurIPS 32 —
  article et résumé de conférence examinés.
- Gibbs & Candès (2021), *Adaptive Conformal Inference Under Distribution
  Shift*, NeurIPS 34 — article examiné.
- Bates et al. (2021), *Distribution-Free, Risk-Controlling Prediction Sets*,
  JACM 68(6) — texte auteur et résumé examinés ; application à notre dépendance
  temporelle non établie.
- Fleming, Kirby & Ostdiek (2001), *The Economic Value of Volatility Timing*,
  Journal of Finance 56 — texte auteur identifié ; lecture détaillée à faire
  avant de définir une fonction de valeur.
- Moreira & Muir (2017), *Volatility-Managed Portfolios*, DOI
  https://doi.org/10.1111/jofi.12513 — résumé éditeur examiné ; texte intégral à
  lire avant toute expérience financière.

## 8. Arbitrages méthodologiques rouverts

| Choix | Pourquoi il peut être approprié | Alternatives réelles | Moment légitime de décision | Statut actuel |
|---|---|---|---|---|
| Variance future | additive, naturelle pour plusieurs modèles et certaines pertes robustes | volatilité, perte absolue, quantile, VaR/ES, distribution complète | après choix de l'utilisateur et de la décision | ouvert |
| Volatilité future | unité lisible et directement liée à un budget de volatilité | variance ou risque de queue si la décision l'exige | avec la première expérience | recommandée provisoirement |
| Horizon 5 séances | cohérent avec une révision hebdomadaire et le prototype | 1, 10, 20 jours selon décision et bruit | après validation du cas d'usage | ouvert, candidat 5 jours |
| QLIKE primaire | classement robuste de prévisions de variance sous certaines conditions de proxy | MAE/RMSE, score probabiliste, perte asymétrique décisionnelle | seulement si la variance est l'estimand | non retenu à ce stade |
| Réestimation annuelle | limite calcul et variations de protocole | fixe, quotidienne, mensuelle, déclenchée par alerte | après diagnostic de vitesse de dérive | non fixée |
| Bootstrap 22 jours | respecte une partie de la dépendance locale | HAC, bootstrap stationnaire, blocs choisis par données/simulation, origines non chevauchantes | après observation de la dépendance et définition de l'estimand | non fixé |
| Marché Developed ex US | teste une certaine transportabilité | futur US, autres indices, périodes historiques gelées | après définition de la population visée | reporté |
| EWMA vs Boosting | audit utile du prototype | un seul instrument transparent, GARCH, aucune compétition | uniquement si la question devient comparative | décentré |
| Variables économiques | permettent de confronter les mécanismes | événements datés, variables financières, analyse qualitative | après preuve qu'une transition statistique mérite explication | aucune intégration immédiate |

Une décision méthodologique sera adoptée seulement si elle répond à : quelle
question résout-elle, pourquoi maintenant, quelle solution plus simple existe,
et que perd-on si on l'omet ?

## 9. Protocole actif volontairement limité

Le protocole actif ne contient qu'une expérience diagnostique. Il n'inclut ni
catalogue de modèles, ni macroéconomie intégrée, ni calibration adaptative, ni
validation internationale, ni backtest.

Avant son exécution, trois éléments seulement devront être gelés :

1. le cas d'usage financier et l'horizon correspondant ;
2. un proxy positif du risque et une mesure signée de sous-prévision ;
3. une prévision de référence transparente, utilisée comme instrument de
   diagnostic et non comme adversaire à battre.

Les règles universelles restent : information disponible à `t`, cible strictement
future, séparation temporelle, conservation des prévisions individuelles,
documentation des choix et qualification de 2020–août 2026 comme période déjà
consultée. La procédure d'inférence sera choisie après avoir caractérisé le
chevauchement et la dépendance ; aucun bloc de 22 jours n'est pré-désigné.

## 10. Une seule première expérience

### Question

> Les sous-prévisions d'un modèle de risque transparent se concentrent-elles
> parce que le niveau de risque est élevé, ou parce que le marché est en train
> de passer rapidement d'un niveau à un autre ?

Cette expérience précède toute comparaison ML. Elle cherche à départager au
moins deux explications :

- **explication de niveau :** les erreurs paraissent fortes parce que la cible
  est plus grande, plus bruitée ou évaluée sur une échelle inadéquate ;
- **explication de transition :** à niveau passé comparable, la direction et la
  vitesse du changement contiennent une information supplémentaire sur la
  sous-prévision.

Une troisième explication restera surveillée : quelques sauts extrêmes ou une
asymétrie après rendements négatifs peuvent créer artificiellement un « effet de
transition ».

### Objet concret proposé, encore soumis à accord

- Portefeuille de marché américain Fama–French, rendement total de recherche.
- Risque observé : volatilité annualisée fondée sur les cinq rendements futurs
  au carré, conservée comme **proxy**, non comme vérité latente.
- Prévision : une seule règle de persistance transparente utilisant uniquement
  les rendements passés. La forme exacte de lissage sera fixée avant lecture des
  résultats conditionnels ; elle ne sera pas optimisée pour gagner.
- Erreur principale de diagnostic : erreur signée et sans unité, par exemple
  `log(risque observé / risque prévu)`, positive en cas de sous-prévision. Ce
  choix évite qu'une différence en niveau soit automatiquement une différence
  en erreur absolue, mais exige des quantités strictement positives.
- État observable à `t` : séparer le **niveau passé** du risque de sa **variation
  récente**. Les seuils seront fixés sans consulter les erreurs futures.

### Comparaison

Comparer les erreurs entre :

1. risque passé élevé et relativement stable ;
2. risque passé de niveau comparable mais en hausse rapide.

Une stratification ou un appariement sur le niveau passé est préférable à une
simple comparaison de moyennes. Les observations successives partagent une
cible ; l'incertitude statistique devra respecter cette dépendance, mais la
méthode exacte n'est pas choisie avant diagnostic.

### Résultats possibles et conséquence scientifique

| Résultat | Interprétation permise | Prochaine décision |
|---|---|---|
| effet de transition après contrôle du niveau | compatible avec un retard ou une instabilité ; ne prouve pas un changement économique | vérifier s'il est commun à une autre référence simple, puis chercher les mécanismes |
| effet absorbé par le niveau | la thèse « transition » est affaiblie ; problème possible d'échelle ou de bruit | revoir la métrique/cible avant toute adaptation |
| effet limité aux grands sauts négatifs | compatible avec asymétrie/jumps plutôt qu'un régime général | étudier ce mécanisme précis, pas ajouter un détecteur générique |
| effet propre à une seule règle de persistance | faiblesse de modèle, non preuve d'instabilité générale | améliorer la référence la plus simple |
| aucune concentration claire | prémisse empirique du programme affaiblie | ne pas construire de méthode adaptative sans autre preuve |

### Ce qui invaliderait notre interprétation

- la variable de transition utilise directement ou indirectement `t+1:t+5` ;
- les seuils ou la période sont choisis après observation des erreurs ;
- l'effet disparaît dès que l'erreur est rendue sans unité ou le niveau apparié ;
- il dépend uniquement de quelques observations dont le rôle n'est pas décrit ;
- le proxy de risque ou le chevauchement suffit à reproduire le motif dans une
  expérience placebo/simulée appropriée ;
- nous qualifions la transition d'« économique » sans observation économique ;
- nous généralisons d'une règle de prévision à tous les modèles.

### Ce que cette expérience ne dira pas

Elle ne permettra pas encore d'identifier lequel des trois mécanismes économiques
agit, de démontrer une causalité, de choisir une méthode d'IA, ni d'établir une
valeur financière. Elle décidera seulement si la distinction niveau/transition
mérite la prochaine investigation.

## 11. Décisions réellement nécessaires avant implémentation

1. **Cas d'usage :** valider ou remplacer le gestionnaire d'une exposition
   actions diversifiée avec budget de risque comme utilisateur de référence.
2. **Instrument initial :** accepter provisoirement la volatilité future à cinq
   séances comme proxy de travail, sans la promouvoir en cible définitive du
   programme.
3. **Première question empirique :** valider le test « niveau élevé contre
   transition montante à niveau comparable » avant toute compétition de modèles.
4. **Matériel antérieur :** fournir si possible le notebook Colab pour auditer
   les prévisions existantes ; sinon autoriser plus tard la reconstruction d'une
   unique référence transparente.

Les métriques finales, le calendrier de réentraînement, l'inférence, la méthode
adaptative et la validation externe ne nécessitent pas encore de décision.

**Arrêt de phase :** la Phase 0 demeure non validée. Aucun passage en Phase 1
avant accord explicite sur ce cadrage révisé.

