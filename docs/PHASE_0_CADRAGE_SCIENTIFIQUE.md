# Phase 0 — cadrage scientifique et protocole initial

**Version :** 15 octobre 2026  
**Statut :** proposition à valider avant toute Phase 1  
**Portée :** aucun résultat empirique nouveau n'est produit dans ce document.

## 1. Recommandation centrale

### Question retenue

> Dans quelle mesure la fiabilité hors échantillon des prévisions à cinq
> séances du risque du marché américain se dégrade-t-elle lors de changements
> d'environnement détectables avec l'information disponible au moment de la
> prévision, et les méthodes adaptatives réduisent-elles cette dégradation par
> rapport à des références simples, correctement calibrées et mises à jour de
> manière comparable ?

Cette formulation est plus étroite que le titre général du projet. Elle est
recommandée parce qu'elle définit une cible, un horizon, un marché, une notion
d'information disponible et un critère comparatif. Elle ne promet ni causalité,
ni supériorité de l'IA.

La « fiabilité » ne sera pas réduite à une métrique moyenne. Elle comprend :

1. l'exactitude ponctuelle hors échantillon ;
2. la calibration des distributions ou intervalles prédictifs ;
3. la stabilité de ces propriétés selon le temps et l'état du marché ;
4. l'absence de sous-estimation systématique dans les périodes critiques ;
5. plus tard seulement, l'utilité dans une décision financière contrôlée.

### Articulation des trois niveaux

- **Économie :** caractériser les conditions et transitions associées aux
  erreurs, sans confondre association prédictive et causalité. Les dates NBER
  sont des annotations ex post, jamais des signaux prétendument disponibles en
  temps réel.
- **Finance :** définir correctement le risque prédit et mesurer le coût
  asymétrique des sous-estimations. Une meilleure erreur moyenne n'implique pas
  automatiquement une meilleure décision.
- **IA/statistique :** comparer des modèles simples et flexibles avec le même
  ensemble d'information, une sélection exclusivement temporelle et des
  budgets raisonnablement comparables ; quantifier ensuite l'incertitude et la
  dérive.

Le premier objet empirique reste volontairement limité au niveau prédictif. Le
backtest de portefeuille, la VaR, l'Expected Shortfall et les variables macro
sont hors de la première expérience.

## 2. Objet mesuré et ensemble d'information

### Série de rendements

Sous réserve de validation, le rendement de marché quotidien est

\[
r_t = (\text{Mkt-RF}_t + \text{RF}_t)/100,
\]

les deux colonnes de la Data Library étant exprimées en pourcentage. Cette
série est un **portefeuille de recherche**, pas un ETF négociable. Son heure de
disponibilité historique réelle n'est pas documentée comme celle d'un flux de
marché. Le protocole supposera donc une prévision de recherche émise après que
le rendement daté `t` est disponible ; toute revendication de négociabilité
exigerait une autre source horodatée.

### Cible recommandée

L'objet statistique principal est le proxy de variance annualisée future :

\[
V^{(5)}_t = \frac{252}{5}\sum_{k=1}^{5} r_{t+k}^{2}.
\]

Pour l'interprétation seulement, on rapportera aussi :

\[
\sigma^{(5)}_t = \sqrt{V^{(5)}_t}.
\]

Cette convention sépare la quantité évaluée en variance de sa présentation en
volatilité annualisée. Avec seulement cinq rendements quotidiens, il faut parler
de **proxy de variation fondé sur les rendements au carré**, et non de realized
variance intrajournalière observée sans bruit. Ce proxy incorpore les mouvements
entre séances mais reste bruité ; il n'est pas un écart-type empirique centré
sur une moyenne estimée.

### Information disponible

À l'origine de prévision `t`, toute variable doit être une fonction de données
datées au plus tard `t`. Une observation d'apprentissage `(X_s, V_s^(5))` n'est
utilisable que lorsque `s+5 <= t`. Les cinq dernières cibles encore incomplètes
sont donc purgées lors de chaque estimation. Toutes les transformations
(standardisation, sélection, imputation, calibration et choix
d'hyperparamètres) sont ajustées uniquement dans la fenêtre d'apprentissage.

## 3. Questions et hypothèses falsifiables

### Q1 — références équitables

**Question.** L'avantage exploratoire du Gradient Boosting subsiste-t-il face à
des références simples recalibrées sur la même information ?

**H1a.** Le Gradient Boosting a une perte QLIKE attendue plus faible que l'EWMA
recalibré dans une évaluation pseudo-hors-échantillon appariée.

**Règle de réfutation opérationnelle.** H1a n'est pas soutenue si l'intervalle
de confiance bilatéral à 95 % du différentiel moyen
`QLIKE(EWMA) - QLIKE(Boosting)` contient zéro ou est négatif. Une différence
positive mais économiquement minuscule sera décrite comme telle, pas comme une
victoire générale de l'IA.

### Q2 — transitions plutôt que niveau de risque

**Question.** Les erreurs augmentent-elles davantage pendant une transition
détectée en temps réel que dans un état de volatilité élevée mais établi ?

**H1b.** À niveau de volatilité passée comparable, la perte et la
sous-prévision sont plus fortes lors des transitions que dans les états
établis.

**Réfutation.** H1b n'est pas soutenue si l'effet conditionnel de transition
n'est pas positif, est trop imprécis, ou disparaît sous des définitions
préspécifiées raisonnables. La définition primaire du détecteur et le seuil
d'effet substantiel devront être gelés avant ce test ; explorer de nombreux
détecteurs puis retenir le meilleur invaliderait son caractère confirmatoire.

### Q3 — précision et décision financière

**Question.** Le classement statistique des modèles prédit-il leur classement
dans une règle simple de ciblage de volatilité après coûts et contraintes ?

**H2.** Une amélioration de perte prédictive moyenne n'implique pas
nécessairement une amélioration substantielle de contrôle du risque net de
coûts.

Cette proposition est actuellement trop générale pour un test confirmatoire.
Elle devra être reformulée avec une règle d'exposition, des coûts, une fonction
d'utilité et un seuil de matérialité fixés avant la Phase 5.

### Q4 — incertitude adaptative

**Question.** Une procédure adaptative améliore-t-elle la couverture
conditionnelle pendant les transitions sans rendre les intervalles inutilement
larges ?

**H3.** Par rapport à une recalibration glissante non adaptative, une méthode
adaptative préspécifiée réduit l'écart absolu à la couverture nominale dans les
transitions, sans hausse excessive de largeur moyenne ni dégradation hors
transition.

Les garanties conformes sous échangeabilité ne doivent pas être transposées
sans précaution aux séries dépendantes. La couverture marginale de long terme
n'est pas une garantie conditionnelle par régime.

## 4. Diagnostic du prototype Colab

Le notebook original n'a pas pu être ouvert dans l'environnement de recherche.
Les chiffres communiqués dans le cadrage sont donc traités comme **résultats
rapportés, non audités**.

Faiblesses prioritaires :

1. **Test déjà regardé.** La période 2020–août 2026 a influencé la conception ;
   elle ne peut plus servir de confirmation indépendante.
2. **Comparaison asymétrique.** Un EWMA non calibré a été opposé à des modèles
   ajustés ; les calendriers de réentraînement des prévisions ponctuelles et
   quantiles différaient.
3. **Cibles chevauchantes.** Deux cibles consécutives partagent quatre
   rendements sur cinq. Un bootstrap arbitraire de 22 jours ne suffit pas, à lui
   seul, à valider l'inférence.
4. **Proxy mal nommé ou insuffisamment défini.** La somme de cinq rendements
   quotidiens au carré n'est pas une mesure intrajournalière de volatilité
   réalisée et demeure un proxy bruité.
5. **Régimes circulaires.** Un régime défini par volatilité passée peut être
   utile comme état observable, mais ce n'est ni un régime économique objectif,
   ni une explication causale.
6. **Sous-couverture importante.** Une couverture de 70,64 % pour un nominal de
   80 % est un échec de calibration substantiel à expliquer, surtout si elle
   tombe à 65,73 % en période agitée.
7. **Sélection et multiplicité inconnues.** Sans le notebook, on ignore le
   nombre d'essais, les hyperparamètres, les transformations, les graines et les
   choix faits après observation des résultats.
8. **Valeur financière non établie.** Les écarts de MAE ne démontrent ni la
   maîtrise des pertes extrêmes, ni la valeur nette d'une décision.

Le fichier `.ipynb` original reste nécessaire pour reproduire précisément les
alignements et expliquer les résultats antérieurs. Sa remise n'est toutefois
pas nécessaire pour reconstruire ensuite un socle indépendant et plus simple.

## 5. Données, accessibilité et limites

| Donnée | Usage | Accessibilité | Limite principale |
|---|---|---|---|
| Fama/French 3 Factors Daily | `Mkt-RF`, `RF`, cible et prédicteurs retardés | téléchargement public | portefeuille de recherche, révisions possibles, horaire réel non garanti |
| Archives Fama/French | figer une version et étudier les révisions | public lorsque disponible | méthodologie CRSP modifiée ; comparer les millésimes |
| FRED/ALFRED | variables macro point-in-time, plus tard | public, API avec clé pour certains usages | dates de publication, révisions et fréquences hétérogènes |
| NBER Business Cycle Dates | diagnostic ex post | public | annonce retardée ; interdit comme prédicteur temps réel |
| Marché développé hors États-Unis, à choisir | validation externe gelée | potentiellement Fama/French daily | historique plus court et construction différente |

La Data Library indique qu'à partir de la livraison de janvier 2025 la source
CRSP est passée du format historique FIZ au format CIZ, avec des changements de
construction. Chaque téléchargement futur devra conserver l'URL, la date/heure,
le fichier brut immuable, son SHA-256, le README source et, si possible, un
millésime historique.

Les variables macro ne seront intégrées qu'après audit de leurs dates de
publication et de leurs millésimes ALFRED. Le FRED courant ne représente pas
nécessairement ce qu'un prévisionniste savait à l'époque.

## 6. État de l'art initial vérifié

### Éléments établis utiles au protocole

- Hansen et Lunde (2005) comparent hors échantillon 330 variantes ARCH/GARCH et
  montrent que la sophistication ne domine pas uniformément GARCH(1,1). Leur
  emploi de plusieurs fonctions de perte et de contrôles du data snooping
  justifie une référence GARCH sérieuse avant toute revendication générale.
- Corsi (2009) propose HAR-RV pour représenter parcimonieusement plusieurs
  horizons de volatilité réalisée. Ici, sans données intrajournalières, une
  construction multi-horizons à partir de carrés de rendements quotidiens ne
  devra pas être présentée comme une réplication fidèle de HAR-RV.
- Patton (2011) montre que le classement des prévisions de variance peut être
  faussé par un proxy imparfait avec certaines pertes, et caractérise des pertes
  robustes dont QLIKE. Cela motive la variance comme objet principal et QLIKE
  comme perte primaire.
- Diebold et Mariano (1995) fournissent un cadre de comparaison de précision
  prédictive avec erreurs sériellement corrélées ; l'horizon chevauchant impose
  ici une inférence dépendante.
- Giacomini et White (2006) étudient la capacité prédictive conditionnelle. Leur
  cadre est pertinent pour demander *quand* une méthode échoue, mais ses
  conditions exactes devront être alignées au schéma d'estimation retenu.
- Gibbs et Candès (2021) proposent l'Adaptive Conformal Inference sous dérive de
  distribution et une propriété de fréquence de couverture à long terme. Cela
  ne résout pas automatiquement la couverture conditionnelle dans des séries
  financières dépendantes.
- Moreira et Muir (2017) relient l'état de volatilité au levier des portefeuilles
  et trouvent des gains dans plusieurs facteurs. Cette motivation financière ne
  dispense pas notre futur backtest de contraintes, coûts, plafonds et tests de
  robustesse.

### Références primaires consultées ou vérifiées

1. Hansen, P. R. & Lunde, A. (2005), *A Forecast Comparison of Volatility
   Models: Does Anything Beat a GARCH(1,1)?*, Journal of Applied Econometrics,
   20, 873–889. DOI : https://doi.org/10.1002/jae.800 — texte intégral consulté.
2. Corsi, F. (2009), *A Simple Approximate Long-Memory Model of Realized
   Volatility*, Journal of Financial Econometrics, 7, 174–196. DOI :
   https://doi.org/10.1093/jjfinec/nbp001 — résumé éditeur consulté ; texte
   intégral à examiner avant implémentation.
3. Patton, A. J. (2011), *Volatility Forecast Comparison Using Imperfect
   Volatility Proxies*, Journal of Econometrics, 160, 246–256. DOI :
   https://doi.org/10.1016/j.jeconom.2010.03.034 — texte intégral auteur
   consulté.
4. Diebold, F. X. & Mariano, R. S. (1995), *Comparing Predictive Accuracy*,
   Journal of Business & Economic Statistics, 13, 253–263. DOI :
   https://doi.org/10.1080/07350015.1995.10524599 — résumé éditeur consulté ;
   texte intégral à relire pour l'implémentation exacte.
5. Giacomini, R. & White, H. (2006), *Tests of Conditional Predictive Ability*,
   Econometrica, 74, 1545–1578 — texte disponible identifié ; examen détaillé à
   faire avant le test conditionnel.
6. Gibbs, I. & Candès, E. (2021), *Adaptive Conformal Inference Under
   Distribution Shift*, NeurIPS 34. https://arxiv.org/abs/2106.00170 — article
   et résumé de conférence consultés.
7. Moreira, A. & Muir, T. (2017), *Volatility-Managed Portfolios*, Journal of
   Finance, 72, 1611–1644. DOI : https://doi.org/10.1111/jofi.12513 — résumé et
   métadonnées éditeur consultés ; texte intégral à examiner avant la Phase 5.
8. Kenneth R. French Data Library :
   https://mba.tuck.dartmouth.edu/pages/faculty/Ken.French/data_library.html —
   page source et avertissement FIZ/CIZ consultés.
9. FRED/ALFRED, documentation des périodes temps réel :
   https://fred.stlouisfed.org/docs/api/fred/realtime_period.html —
   documentation officielle consultée.

### Nouveauté : ce qui est établi et ce qui reste possible

Il est déjà établi que la volatilité est persistante, que des références GARCH
ou multi-horizons sont fortes, que les proxies sont imparfaits, que les
comparaisons hors échantillon doivent intégrer la dépendance, et que des méthodes
conformes adaptatives existent. « Appliquer du boosting à la volatilité » ou
« observer une sous-couverture en crise » ne constitue donc pas une nouveauté.

Une contribution potentielle — non démontrée — pourrait résider dans un
protocole commun reliant : détection strictement temps réel des transitions,
décomposition de la perte de fiabilité ponctuelle et probabiliste, comparaison
équitable simple/ML/adaptatif, puis matérialité financière. La nouveauté devra
être réévaluée après une revue systématique plus large.

## 7. Protocole expérimental initial

### Unité de prévision et calendrier

- Origine : chaque séance `t`, après disponibilité du rendement `t`.
- Horizon : cinq séances futures.
- Prédictions : quotidiennes, donc chevauchantes.
- Réestimation des paramètres : annuelle dans le protocole primaire ; données
  et caractéristiques retardées mises à jour quotidiennement.
- Fenêtre primaire : croissante ; fenêtre glissante comme sensibilité, pas
  comme choix post hoc.
- Purge : aucune cible dont une composante dépasse la date d'estimation.

### Séparation des usages des dates

- Jusqu'à 2019 : zone de développement pseudo-hors-échantillon pour construire
  et auditer le protocole. Elle ne sera pas qualifiée de confirmation vierge.
- 2020–août 2026 : zone contaminée par consultation antérieure, utilisable
  uniquement pour réplication et diagnostic étiquetés.
- Confirmation : soit données futures accumulées après gel du protocole, soit
  un marché externe choisi une seule fois avant inspection des résultats. Le
  choix recommandé est une série quotidienne « Developed ex US » de la même
  bibliothèque, après vérification de son historique et de sa construction.

Les dates exactes de la zone de développement seront fixées après inspection
des données et avant calcul des performances ; elles ne doivent pas être
choisies pour produire un résultat favorable.

### Prédicteurs initiaux communs

Uniquement des fonctions de rendements passés : carrés/sommes sur 1, 5, 22, 60
et 252 séances, rendement signé retardé et indicateur de baisse pour capter une
asymétrie simple. Aucun indicateur macro, aucune date NBER, aucun signal issu du
futur.

### Modèles par portes

1. Historique simple et EWMA, avec et sans facteur multiplicatif calibré sur
   l'apprentissage selon QLIKE.
2. Ridge et Gradient Boosting sur le même ensemble de caractéristiques.
3. Après validation du socle : GARCH(1,1), GJR-GARCH et une référence
   multi-horizons adaptée aux seules données quotidiennes.
4. Seulement après les comparaisons ponctuelles : quantiles et calibration
   adaptative.

L'ajout d'un modèle répondra à une question identifiée. GARCH doit être présent
avant toute conclusion générale sur une supériorité du ML, mais n'est pas
nécessaire pour l'audit mécanique de la toute première expérience.

### Sélection et équité

- même date d'origine, même cible et même jeu d'information pour tous ;
- hyperparamètres choisis dans des découpages temporels internes seulement ;
- grille réduite et préspécifiée, même fréquence de réestimation des paramètres ;
- calibration estimée uniquement sur l'historique disponible ;
- graines et versions enregistrées ;
- toutes les prévisions sauvegardées avant agrégation des métriques.

### Métriques et inférence

Perte primaire sur variance positive :

\[
QLIKE(V, \widehat V)=V/\widehat V-\log(V/\widehat V)-1.
\]

Secondaires : MAE de la volatilité annualisée, RMSE, biais signé et taux de
sous-prévision. Les métriques par année et par états sont descriptives tant que
leurs tests ne sont pas préspécifiés.

Chaque comparaison est appariée par date. On rapportera le différentiel moyen,
son intervalle et la série temporelle des écarts. L'inférence primaire utilisera
un bootstrap en blocs mobiles de 22 séances, avec sensibilités 5, 10, 44 et 60,
ainsi qu'une évaluation sur origines non chevauchantes. Une conclusion qui
dépend d'une seule longueur de bloc sera qualifiée de fragile. Une estimation
HAC cohérente avec le schéma retenu servira de contrôle, pas d'arbitre unique.

## 8. Matrice des expériences prévues

| Porte | Question mesurable | Comparateur | Risque principal | Sortie attendue |
|---|---|---|---|---|
| E0 | cible et alignement sont-ils exacts ? | calcul manuel sur mini-série | fuite `t+1:t+5`, unités | tests d'identité et tableau d'audit |
| E1 | l'avantage Boosting survit-il à la calibration ? | EWMA calibré primaire | comparaison inéquitable, sélection | différentiel QLIKE apparié + IC |
| E2 | GARCH/asymétrie changent-ils le classement ? | GARCH, GJR, modèle multi-horizons | optimisation et convergence | classement robuste par pertes |
| E3 | où les erreurs se concentrent-elles ? | états établis vs transitions temps réel | définition opportuniste | effets conditionnels + sensibilités |
| E4 | les intervalles sont-ils fiables ? | quantiles glissants vs adaptatif | dépendance, couverture marginale | couverture, largeur, excès par état |
| E5 | le gain prédit-il une valeur financière ? | règle de risque fixe | coûts/look-ahead/levier | risque réalisé, turnover, coûts |
| E6 | le résultat se généralise-t-il ? | marché externe gelé | choix après inspection | réplication sans retuning opportuniste |

## 9. Risques méthodologiques et contrôles

| Risque | Conséquence | Contrôle prévu |
|---|---|---|
| fuite temporelle | performance artificielle | audit ligne par ligne, purge de 5 jours, tests automatisés |
| chevauchement | IC trop étroits | blocs, HAC, origines non chevauchantes |
| proxy bruité | mauvais classement | QLIKE primaire, langage prudent, future donnée intraday éventuelle |
| sélection sur 2020–2026 | confirmation invalide | étiquette diagnostic, holdout externe/futur gelé |
| benchmark faible | fausse supériorité ML | calibration, GARCH/GJR, mêmes informations et mises à jour |
| régimes ex post | look-ahead et causalité abusive | détecteur unilatéral pour prédire ; NBER descriptif seulement |
| données révisées | non-reproductibilité | brut immuable, millésime, URL, horodatage, SHA-256 |
| macro révisée | fuite silencieuse | ALFRED et date de publication, pas seulement date d'observation |
| multiplicité | faux positifs | question primaire, modèle primaire, corrections/sensibilités déclarées |
| hyperparamètres | surapprentissage | validation temporelle imbriquée et budget limité |
| instabilité structurelle | moyenne trompeuse | résultats par sous-période et tests conditionnels préspécifiés |
| faible matérialité | gain statistique sans intérêt | tailles d'effet et seuils économiques avant Phase 5 |

### Critères de validité scientifique

Un résultat principal ne sera considéré robuste que si : (i) l'alignement et la
provenance passent les audits ; (ii) le modèle et la métrique ont été gelés avant
le holdout ; (iii) l'effet est apparié, accompagné d'incertitude et stable sous
des contrôles justifiés ; (iv) aucune baseline évidente n'est volontairement
affaiblie ; (v) la conclusion distingue clairement association, prédiction et
causalité ; (vi) les résultats négatifs restent auditables ; et (vii) une
validation indépendante confirme toute revendication de généralisation.

## 10. Toute première expérience recommandée

### Question

**Le gain exploratoire du Gradient Boosting persiste-t-il lorsque l'EWMA est
recalibré dans exactement le même protocole temporel ?**

### Hypothèse

`H_E1` : le différentiel moyen
`d_t = QLIKE(EWMA_calibré)_t - QLIKE(Boosting)_t` est strictement positif.

Cette hypothèse est réfutable : si l'IC à 95 % de `mean(d_t)` inclut zéro, nous
conclurons « avantage non établi », et non « modèles équivalents ». Si l'IC est
entièrement négatif, le résultat contredit directement l'hypothèse.

### Données

Fama/French 3 Factors Daily, version figée, `r=Mkt-RF+RF` en décimal ; uniquement
les rendements disponibles à `t`. La période exacte de développement sera gelée
après audit de couverture. La période 2020–août 2026 sera exclue du test principal
et réservée à une réplication explicitement contaminée.

### Méthode

1. Auditer dates, doublons, valeurs manquantes, unités, reconstruction et cible.
2. Vérifier la cible sur une mini-série calculée manuellement.
3. Produire des prévisions quotidiennes avec paramètres réestimés annuellement.
4. EWMA : paramètre de décroissance sélectionné dans une petite grille temporelle
   interne et facteur d'échelle positif minimisant QLIKE sur l'apprentissage.
5. Boosting : mêmes caractéristiques retardées, grille réduite, sélection
   temporelle interne et aucun accès à la période évaluée.
6. Sauvegarder les prévisions avant de calculer les agrégats.
7. Comparer QLIKE apparié ; contrôles par MAE, blocs alternatifs et origines
   non chevauchantes.

### Critères de décision

- **Soutien à H_E1 :** moyenne positive et borne basse de l'IC 95 % > 0, sans
  inversion majeure dans les contrôles préspécifiés.
- **Résultat fragile :** signe positif mais IC incluant 0, ou forte dépendance à
  la longueur de bloc/période.
- **Réfutation :** moyenne non positive ou IC entièrement négatif.
- Dans tous les cas, rapporter la taille absolue du gain, pas seulement une
  significativité.

Cette expérience ne testera pas encore les régimes, la calibration des
intervalles ou la valeur financière. Son rôle est de déterminer si le premier
constat motivant le projet survit à une comparaison minimale équitable.

## 11. Structure minimale proposée après validation

Les seuls fichiers créés en Phase 0 sont ceux listés dans le README. Après
validation, la Phase 1 ajouterait progressivement :

```text
notebooks/
  01_cible_donnees_et_alignement.ipynb
  02_premiere_comparaison_equitable.ipynb   # seulement après succès du notebook 01
data/
  raw/                                     # source immuable, non versionnée si lourde
  metadata/                                # provenance et checksums
tests/
  test_alignement_temporel.py              # si les contrôles sortent du notebook
```

Le premier notebook répondra uniquement à E0. Le second ne sera créé que si les
audits réussissent. Aucun package, dashboard, API, base de données ou catalogue
de modèles n'est justifié à ce stade.

## 12. Arbitrages à valider avant la Phase 1

1. **Cible :** accepter `V_t^(5)` comme proxy de variance principal, QLIKE comme
   perte primaire et sa racine annualisée comme présentation secondaire.
2. **Horodatage :** accepter le cadre de recherche « après disponibilité du
   rendement Fama/French daté t », sans prétention de négociabilité temps réel.
3. **Indépendance :** réserver 2020–août 2026 au diagnostic et choisir avant
   inspection entre un marché Developed ex US gelé et une accumulation future
   comme confirmation principale.
4. **Portée de E1 :** autoriser d'abord l'audit EWMA calibré contre Boosting,
   sans revendication générale avant l'ajout de GARCH/GJR.
5. **Prototype :** fournir si possible le `.ipynb` Colab original pour audit ;
   à défaut, accepter une reconstruction indépendante sans prétendre reproduire
   exactement les chiffres rapportés.

**Arrêt de phase :** aucune Phase 1 ne commence avant validation explicite de
ces arbitrages.

