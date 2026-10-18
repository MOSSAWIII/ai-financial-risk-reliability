# Protocole proposé — Reconnaître le risque de forte sous-estimation

**Statut : proposition méthodologique soumise à validation — aucune expérience engagée**

## 1. Question scientifique retenue et justification

La prochaine question proposée est :

> À la clôture d'une séance `t`, les seules informations alors disponibles permettent-elles de signaler que les prévisions de `RV5_t` émises à cette date risquent d'être fortement sous-estimées par plusieurs modèles ?

Cette formulation ne demande pas de prévoir une seconde fois le niveau exact de `RV5`. Elle demande si l'on peut reconnaître les circonstances dans lesquelles la prévision principale devient particulièrement peu fiable du côté financièrement préoccupant de la sous-estimation.

La distinction est importante : un modèle peut avoir une bonne RMSE moyenne tout en sous-estimant fortement quelques hausses rapides de volatilité. Inversement, une alerte peut détecter certains cas dangereux tout en étant trop fréquente pour être utile. La fiabilité ne se réduit donc ni à la précision moyenne, ni à la seule détection des épisodes extrêmes.

### 1.1 Ce que les travaux existants établissent

Sur les 1 001 dates d'évaluation de 2016–2019 :

- une sous-estimation forte est définie par une erreur signée `prévision − RV5 <= −10,931` points de volatilité annualisée ; ce seuil absolu commun a été fixé à partir de la validation 2010–2015 ;
- une défaillance commune correspond à au moins quatre modèles sur cinq dépassant ce seuil à la même origine de prévision ;
- 44 dates répondent à cette définition et se regroupent en 13 épisodes contigus ;
- 33 de ces 44 dates concernent les cinq modèles ;
- les configurations approfondies retrouvent 44 de ces 44 dates et n'en ajoutent qu'une : le phénomène n'est donc pas expliqué par un seul réglage particulier ;
- les 44 origines se ramènent à 13 séances futures dominantes, et la contribution médiane de cette séance dominante à `RV5` atteint 60,7 % ; le chevauchement des fenêtres amplifie donc le nombre apparent d'observations ;
- les cinq sous-échantillons non chevauchants contiennent encore chacun des défaillances communes : le phénomène ne disparaît pas lorsque l'on réduit le chevauchement ;
- au début des 13 épisodes, aucun rendement courant en valeur absolue ne dépasse le 95e centile historique, et `HV5 > HV20` n'est observé que dans 5 cas sur 13 ;
- la dispersion entre les prévisions n'est pas exceptionnellement élevée au début des épisodes ;
- certains modèles augmentent ensuite leur prévision, mais cette réaction n'est ni systématique ni nécessairement assez rapide.

Ces constats indiquent une difficulté partagée par des méthodes différentes et montrent qu'aucun précurseur simple et uniforme n'a encore été mis en évidence. Ils ne démontrent ni que les épisodes sont imprévisibles, ni qu'un signal exploitable existe.

### 1.2 Ce qui demeure inconnu

Nous ne savons pas encore :

- si une information disponible à `t` discrimine réellement les débuts d'épisodes des dates ordinaires ;
- si une éventuelle association est assez stable pour être utilisée hors de la période déjà étudiée ;
- si une alerte peut conserver une fréquence acceptable tout en couvrant une part utile des épisodes ;
- si les modèles échouent parce qu'ils réagissent tardivement à une information déjà visible ou parce que le mouvement pertinent survient après `t` sans signe précurseur dans la série utilisée ;
- si les 13 épisodes offrent un échantillon suffisant pour distinguer un signal fragile d'une régularité reproductible.

La période 2016–2019 a déjà servi à construire cette question. Toute analyse supplémentaire sur ces dates restera exploratoire. Les observations jusqu'en août 2026 ont également déjà été consultées dans le projet et ne doivent pas être présentées comme un test final intact.

## 2. Définitions nécessaires

### 2.1 Prévoir le niveau, reconnaître le risque d'erreur et anticiper un épisode

Quatre objectifs doivent rester séparés.

1. **Prévoir le niveau de volatilité** : produire une valeur numérique pour `RV5_t`.
2. **Reconnaître le risque d'erreur à `t`** : au moment où la prévision de `RV5_t` est émise, signaler qu'elle risque d'être fortement sous-estimée. Les cinq rendements futurs ne sont pas encore connus ; il s'agit donc bien d'une prédiction, même si l'alerte porte sur la fiabilité plutôt que sur le niveau.
3. **Anticiper avant le début d'un épisode** : émettre une alerte au plus tard à `t−1` pour un épisode dont la première origine est `t`. Cet objectif impose un délai d'avance supplémentaire et constitue une question distincte, plus difficile.
4. **Reconnaître un épisode déjà commencé** : utiliser les informations apparues après son début. Cette détection peut aider au suivi, mais elle ne prouve pas que le premier échec était anticipable.

Le protocole minimal recommande d'étudier d'abord le deuxième objectif. Il correspond exactement à la décision prise à `t` et n'impose pas arbitrairement une fenêtre d'anticipation. Il ne devra pas être décrit comme une capacité à annoncer l'épisode avant son origine.

### 2.2 Cible de défaillance

Pour chaque modèle `m` et chaque date d'origine `t`, l'erreur signée est :

```text
e(m,t) = prévision(m,t) − RV5(t)
```

Avec le seuil déjà validé `s = 10,931`, l'indicateur de forte sous-estimation est :

```text
U(m,t) = 1 si e(m,t) <= −s, 0 sinon
```

La défaillance commune est :

```text
C(t) = 1 si la somme des U(m,t) est au moins égale à 4, 0 sinon
```

Un début d'épisode est une date telle que :

```text
O(t) = 1 si C(t) = 1 et C(t−1) = 0
```

La définition principale doit rester celle du benchmark initial. Utiliser les configurations approfondies pour redéfinir les événements après observation des résultats introduirait une décision rétrospective. Leur concordance peut seulement servir de contrôle de robustesse secondaire.

### 2.3 Signal exploitable à la date `t`

Un signal est exploitable s'il respecte simultanément les conditions suivantes :

- il est calculable à la clôture de `t` à partir d'informations observées au plus tard à `t` ;
- sa formule et son seuil sont fixés avant l'évaluation ;
- il ne contient ni `RV5_t`, ni une erreur de prévision dont les cinq rendements futurs ne sont pas encore tous observés ;
- il ne dépend pas de la connaissance rétrospective des dates d'épisode ;
- il produit une règle d'alerte reproductible et suffisamment rare pour que son coût opérationnel puisse être apprécié.

À la clôture de `t`, les rendements jusqu'à `t`, `HV5_t`, `HV20_t`, `HV60_t` et les cinq prévisions émises à `t` sont disponibles. En revanche, `RV5_t`, les erreurs correspondantes et l'appartenance définitive de `t` à un épisode ne le sont pas.

Il faut également tenir compte du délai de maturation : l'erreur d'une prévision émise à `t` n'est connue qu'après la cinquième séance future. Une règle utilisant la dernière erreur entièrement observée à la date courante ne peut donc employer que des origines âgées d'au moins cinq séances. Dans les épisodes historiques, souvent courts, ce délai rend la reconnaissance par les erreurs passées potentiellement trop tardive pour le début de l'épisode.

## 3. Protocoles envisageables

### 3.1 Analyse quotidienne des 44 dates

Cette option considère `C(t)` comme cible quotidienne.

**Avantage :** elle utilise toutes les dates de sous-estimation commune et mesure directement le risque de la prévision émise chaque jour.

**Limite :** plusieurs dates peuvent être produites par le même grand rendement futur apparaissant dans des fenêtres successives. Traiter les 44 dates comme 44 événements indépendants exagérerait fortement la quantité d'information.

Cette analyse peut être conservée comme description secondaire, mais elle ne doit pas être l'unité principale de conclusion.

### 3.2 Reconnaissance du début des 13 épisodes

Cette option utilise `O(t)`, première origine de chaque épisode, comme cible principale.

**Avantages :** elle évite de créditer plusieurs fois une alerte pour la même séquence et se concentre sur le moment où la difficulté apparaît.

**Limites :** elle ne fournit que 13 événements sur 1 001 dates. Un succès ou un échec supplémentaire modifie fortement les proportions, et les épisodes ne peuvent pas être supposés indépendants au sens statistique sans examen supplémentaire.

C'est néanmoins l'unité la plus défendable pour la question actuelle.

### 3.3 Anticipation une séance avant l'épisode

Cette option demande si une alerte émise à `t−1` annonce `O(t)=1`.

**Avantage :** elle correspond strictement à une alerte antérieure au début observé.

**Limites :** elle change la question, impose un délai particulier et réduit encore la plausibilité d'un signal avec les seules données actuelles. Une alerte à `t` et une alerte à `t−1` ne doivent pas être confondues.

Cette option doit être reportée jusqu'à ce que la reconnaissance du risque à l'origine elle-même soit évaluée.

### 3.4 Détection d'un épisode en cours par les erreurs déjà réalisées

Cette option utilise uniquement les erreurs arrivées à maturité, donc avec au moins cinq séances de retard.

**Avantage :** elle peut indiquer une dégradation effectivement observée sans fuite temporelle.

**Limite :** sur les épisodes actuels, dont la durée va de une à six origines, l'information sur la première erreur devient généralement disponible lorsque l'épisode est terminé ou presque. Elle étudie le suivi d'une défaillance, pas son anticipation.

Elle ne constitue pas la prochaine expérience prioritaire.

## 4. Protocole expérimental minimal proposé

### 4.1 Principe

L'expérience proposée ne développe ni classifieur, ni nouveau modèle de volatilité. Elle confronte deux règles d'alerte transparentes aux débuts d'épisodes :

1. **Alerte de niveau élevé** : `HV20_t` dépasse son 90e centile calculé sur 1990–2015.
2. **Alerte d'accélération récente** : le ratio `HV5_t / HV20_t` dépasse son 90e centile calculé sur 1990–2015.

La première demande si le risque de défaillance est reconnaissable lorsque la volatilité récente est déjà élevée. La seconde demande si une hausse relative sur cinq séances contient une information que le niveau mensuel masque. Ces deux quantités utilisent exclusivement les rendements historiques et les transformations déjà présentes dans le benchmark.

Le 90e centile n'est pas présenté comme optimal. Il fixe ex ante une fréquence d'alerte historique approximativement limitée à 10 %, sans utiliser les événements de 2016–2019 pour l'ajuster. Tester plusieurs seuils puis retenir le meilleur créerait une optimisation supplémentaire disproportionnée avec 13 épisodes.

Ces règles ne sont pas des candidats automatiquement validés. Les résultats du notebook 06, notamment `HV5 > HV20` dans seulement 5 débuts sur 13, donnent au contraire une raison sérieuse d'accepter qu'elles puissent échouer.

### 4.2 Chronologie exacte

Pour une date d'origine `t` :

1. après observation du rendement de `t`, calculer `HV20_t` et `HV5_t / HV20_t` ;
2. appliquer les seuils figés sur 1990–2015 ;
3. enregistrer immédiatement l'alerte éventuelle ;
4. attendre les cinq séances futures nécessaires au calcul de `RV5_t` ;
5. déterminer alors, et seulement alors, si `C(t)=1` et si `t` constitue un début d'épisode.

Cette séquence doit être démontrée explicitement dans le futur notebook. Les variables de signal ne peuvent contenir aucune observation postérieure à `t`.

### 4.3 Unités d'analyse et chevauchement

L'unité principale est le début des 13 épisodes. Une alerte est pertinente au sens principal uniquement si elle est active à la date d'origine du début d'épisode. Une alerte à une date ordinaire est une fausse alerte ; un début sans alerte est un épisode manqué.

L'analyse quotidienne sur les 44 dates sera secondaire et clairement identifiée comme affectée par le chevauchement. Elle indiquera si une règle devient active après le début, sans transformer cette réaction tardive en anticipation réussie.

La sensibilité aux cinq décalages d'observations espacées de cinq séances sera conservée. Elle ne servira pas à produire cinq confirmations : chaque décalage contient très peu d'événements. Elle vérifiera seulement que le résultat descriptif ne dépend pas entièrement d'un décalage particulier.

Les alertes quotidiennes consécutives seront également regroupées en épisodes d'alerte pour rendre visible leur persistance. Toutefois, le calcul principal gardera chaque date d'alerte dans le dénominateur de la précision : répéter longtemps une alerte ne doit pas permettre de revendiquer plusieurs succès pour un seul épisode.

### 4.4 Références minimales

Trois comparaisons suffisent :

- **aucune alerte**, qui manque nécessairement tous les épisodes et montre pourquoi l'exactitude globale serait trompeuse avec des événements rares ;
- **référence sans information**, dont la précision attendue est simplement la fréquence des débuts d'épisodes parmi les dates admissibles ;
- **alerte de niveau `HV20`**, comparée à l'alerte d'accélération `HV5/HV20` avec la même règle de centile.

Une procédure aléatoire simulée, un classifieur ou une recherche de seuil n'est pas nécessaire pour répondre à la première question.

### 4.5 Séparation temporelle et statut des résultats

Les seuils des signaux seront calculés uniquement sur 1990–2015, puis figés. Les événements et alertes seront examinés sur les mêmes 1 001 dates de 2016–2019 afin de préserver la comparabilité avec les notebooks 05 et 06.

Cette séparation empêche l'utilisation directe des résultats futurs dans le calcul des seuils, mais elle ne rend pas 2016–2019 indépendant : cette période a déjà inspiré la question, le choix des signaux et l'analyse des épisodes. L'expérience ne pourra donc fournir qu'un test exploratoire plus discipliné de la plausibilité du signal.

Une confirmation indépendante exige un ensemble temporel qui n'a pas encore orienté les choix. À ce stade, aucune période historique disponible dans le projet ne remplit clairement cette condition. Le protocole et les seuils pourraient être figés pour une évaluation prospective sur de futures observations, mais cette décision et les règles d'actualisation éventuelle des cinq modèles devront être validées séparément. Il n'est pas proposé d'élargir maintenant les données ou les marchés.

## 5. Critères d'évaluation

Le faible nombre d'épisodes impose des nombres bruts en plus des proportions.

### 5.1 Mesures principales

- **Épisodes reconnus / 13** : nombre et proportion de débuts d'épisodes portant une alerte. C'est le rappel au niveau des épisodes.
- **Épisodes manqués / 13** : complément du précédent, financièrement important puisque chaque omission correspond à une défaillance commune non signalée.
- **Alertes pertinentes / total des dates d'alerte** : précision de l'alerte. Elle mesure combien d'alertes quotidiennes correspondent réellement à un début d'épisode.
- **Fausses alertes pour 100 séances** : mesure directe de la charge opérationnelle.

L'exactitude globale ne sera pas une mesure principale : avec 13 débuts sur 1 001 dates, une règle qui ne déclenche jamais d'alerte paraîtrait excellente tout en étant inutile pour la question étudiée.

### 5.2 Diagnostics secondaires indispensables

- effectifs bruts pour chaque règle ;
- nombre d'épisodes d'alerte distincts et durée de ces épisodes ;
- résultat sur l'ensemble des 44 dates, séparé du résultat sur les 13 débuts ;
- distribution descriptive des résultats dans les cinq décalages non chevauchants ;
- chronologie montrant si une alerte apparaît au début, seulement après le début, ou jamais.

Aucun test de significativité supplémentaire n'est nécessaire dans l'expérience minimale. Avec 13 événements et une période déjà explorée, une valeur-p ne transformerait pas l'analyse en preuve indépendante.

### 5.3 Lecture financière prudente

Une forte volatilité ne signifie pas automatiquement une perte : `RV5` est insensible au signe des rendements et ne représente ni une position de portefeuille, ni une fonction de coût. Une alerte pourrait néanmoins signaler que les limites de risque, la taille d'une position ou une couverture fondées sur la prévision méritent un examen supplémentaire.

Sans décision financière et coût relatif des fausses alertes et des épisodes manqués, il est impossible d'affirmer qu'une règle est économiquement supérieure. Le protocole mesure donc la capacité de reconnaissance et la charge d'alerte, pas une utilité financière finale.

## 6. Risques méthodologiques et précautions

### 6.1 Fuite temporelle

La principale fuite serait d'utiliser `RV5_t`, une erreur non arrivée à maturité, le rang futur de la volatilité ou l'appartenance à un épisode pour calculer l'alerte. La future implémentation devra afficher pour quelques dates les bornes exactes de chaque fenêtre et comporter des assertions vérifiant que le dernier rendement du signal est daté de `t` au plus tard.

### 6.2 Choix rétrospectif du signal

Les données de 2016–2019 ont déjà montré certaines caractéristiques des épisodes. Même une formule calculée sans données futures peut être choisie après avoir vu les résultats et bénéficier ainsi d'une fuite conceptuelle. La transparence exige de figer maintenant les deux règles proposées et de qualifier leur évaluation d'exploratoire.

### 6.3 Pseudo-réplication due au chevauchement

Les 44 dates ne constituent pas 44 réalisations indépendantes. Les conclusions reposeront d'abord sur les 13 débuts d'épisodes, puis sur les cinq décalages non chevauchants comme sensibilité descriptive. Aucun intervalle de confiance supposant l'indépendance quotidienne ne sera présenté.

### 6.4 Rareté des événements

Treize épisodes ne permettent pas une sélection fiable parmi de nombreuses variables, règles ou valeurs de seuil. Le protocole interdit donc la recherche extensive de combinaisons et l'ajustement du seuil sur 2016–2019. Les résultats devront être accompagnés des effectifs : reconnaître 6 épisodes au lieu de 5 peut sembler une hausse importante en pourcentage tout en ne reposant que sur un cas.

### 6.5 Confusion entre association et prédiction généralisable

Une concentration des épisodes lorsque `HV20` ou `HV5/HV20` est élevé établirait au mieux une association rétrospective sur cette période. Une capacité généralisable exigerait que la règle, son seuil et son usage soient définis avant une nouvelle période non consultée.

### 6.6 Fréquence excessive des alertes

Un rappel élevé obtenu en restant presque toujours en alerte n'est pas informatif. Le nombre d'alertes, leur durée et les fausses alertes pour 100 séances doivent être examinés conjointement avec les épisodes reconnus. En l'absence de fonction de coût validée, aucun compromis unique ne sera déclaré optimal.

## 7. Résultats possibles et interprétation

### 7.1 Rappel et précision tous deux faibles

Les deux résumés historiques simples ne permettent pas de reconnaître utilement les débuts d'épisodes dans ces données. Ce résultat ne prouverait pas que toute reconnaissance est impossible, mais il invaliderait l'idée qu'une règle évidente fondée sur le seul niveau ou l'accélération récente suffit.

### 7.2 Rappel élevé, précision faible

La règle couvre plusieurs épisodes mais produit beaucoup de fausses alertes. Elle décrit un contexte fréquent compatible avec les défaillances, sans les discriminer suffisamment. Son utilité financière resterait indéterminée sans coût des alertes.

### 7.3 Précision élevée, rappel faible

La règle identifie éventuellement un sous-type rare d'épisode, mais ne répond pas au problème général de fiabilité. Elle pourrait motiver une investigation ciblée ultérieure, sans être qualifiée de solution globale.

### 7.4 Résultat apparemment favorable mais instable selon les décalages

Une performance dépendant fortement du décalage des fenêtres suggérerait que le résultat repose sur quelques dates ou sur le chevauchement. Elle ne justifierait pas une extension plus complexe.

### 7.5 Alertes surtout postérieures au début

La règle serait davantage un indicateur de réaction ou de suivi qu'un signal de risque au moment de la première défaillance. Cette information resterait descriptive, mais elle ne répondrait pas à la question prioritaire.

### 7.6 Résultat favorable et relativement cohérent

Même si une règle reconnaît plusieurs débuts avec peu de fausses alertes et reste cohérente entre décalages, la conclusion devra rester : « signal candidat observé sur une période déjà explorée ». La prochaine exigence scientifique serait une validation prospective, et non l'ajout immédiat d'un modèle plus complexe.

## 8. Décisions nécessitant une validation avant exécution

1. **Objectif principal** : valider la reconnaissance, à la date `t`, du risque associé à la prévision émise à `t`, sans la présenter comme une anticipation à `t−1`.
2. **Unité principale** : valider les 13 débuts d'épisodes comme unité de conclusion, les 44 dates restant un diagnostic secondaire.
3. **Définition de l'événement** : conserver le seuil absolu `10,931` et la règle d'au moins quatre modèles sur cinq du benchmark initial.
4. **Signaux autorisés** : limiter l'expérience à `HV20_t` et au ratio `HV5_t/HV20_t`, sans combinaison ni apprentissage.
5. **Seuil d'alerte** : valider le 90e centile de chaque signal sur 1990–2015, choisi pour limiter simplement la fréquence historique des alertes et non pour optimiser leur performance.
6. **Statut de 2016–2019** : confirmer que le résultat sera exclusivement exploratoire, cette période ayant déjà été examinée.
7. **Confirmation future** : décider ultérieurement si le protocole doit être gelé pour une évaluation prospective ; aucune collecte, actualisation ou extension n'est incluse dans la présente proposition.

## 9. Recommandation

La prochaine expérience minimale recommandée est une évaluation exploratoire, sur les 1 001 dates déjà communes de 2016–2019, de deux alertes entièrement prédéfinies : niveau élevé de `HV20` et accélération élevée de `HV5/HV20`, chacune au-dessus de son 90e centile calculé sur 1990–2015.

L'analyse doit prendre les 13 débuts d'épisodes comme unité principale, publier les effectifs bruts, le rappel, la précision et les fausses alertes pour 100 séances, puis montrer séparément les 44 dates chevauchantes et les cinq décalages non chevauchants. Elle ne doit entraîner aucun modèle, optimiser aucun seuil ni prétendre fournir une validation indépendante.

Ce protocole est volontairement falsifiable : il peut conclure que les informations historiques simples déjà disponibles ne reconnaissent pas suffisamment les défaillances. Un tel résultat serait scientifiquement utile, car il distinguerait l'absence de signal simple dans notre série de l'idée, non démontrée, qu'une sophistication algorithmique résoudrait nécessairement le problème.

**Aucune exécution ne doit commencer avant validation explicite des sept décisions ci-dessus.**
