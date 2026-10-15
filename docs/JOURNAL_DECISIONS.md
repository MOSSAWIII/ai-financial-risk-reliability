# Journal des décisions scientifiques

Ce journal conserve les décisions qui structurent encore le projet. Les détails
des propositions abandonnées restent accessibles dans l'historique Git ; ils ne
sont plus maintenus comme options dans les documents courants.

## Historique du cadrage

### 15 octobre 2026 — première proposition de Phase 0

Une première version a été proposée puis refusée par le porteur du projet. Elle
transformait trop tôt la question scientifique en protocole comparatif et fixait
des choix insuffisamment justifiés.

### 15 octobre 2026 — deuxième proposition de Phase 0

La deuxième version a renforcé les liens entre économie, finance et IA, mais a
encore introduit des orientations non validées : choix d'un utilisateur
financier, priorité donnée à l'anticipation de la dégradation et première
expérience centrée sur le contraste entre niveau et transition.

### 15 octobre 2026 — retour strict au mandat fondateur

Le porteur du projet a fixé deux règles permanentes : aucune extension du
périmètre sans validation explicite et priorité à la solution scientifique la
plus simple qui répond à la question active. Le protocole a été réduit à la
définition et à l'audit de la cible initiale.

### 15 octobre 2026 — suppression des pistes abandonnées

À la demande explicite du porteur, les options techniques et extensions écartées
ont été supprimées des documents courants. Elles ne sont plus reportées comme
possibilités futures. Cette suppression ne modifie pas le fichier fondateur ;
l'historique Git conserve les versions antérieures.

### 15 octobre 2026 — validation de la Phase 0

Le porteur du projet valide explicitement la Phase 0. La question centrale, la
cible initiale à cinq séances et les contraintes du protocole simplifié sont
acceptées. Cette validation clôt le cadrage ; elle n'autorise pas implicitement
l'ajout d'autres expériences ou méthodes.

### 15 octobre 2026 — audit de la cible autorisé et exécuté

Le porteur autorise explicitement les six opérations de l'audit initial :
importation des rendements Fama–French, vérification des unités et des dates,
construction de la cible à cinq séances, contrôles manuels, contrôle de fuite
temporelle et documentation des valeurs manquantes.

Le notebook exécuté lit 26 317 séances du 1er juillet 1926 au 31 août 2026. Il
produit 26 312 cibles complètes. Les cinq seules cibles manquantes sont les cinq
dernières, qui ne disposent pas de cinq séances futures. Les trois calculs
manuels sont identiques au calcul automatisé et toutes les dates constitutives
de la cible sont strictement postérieures à `t`. L'archive utilisée porte
l'empreinte SHA-256
`2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db`.

L'audit a également identifié 1 158 séances historiques un samedi. Elles sont
conservées car elles appartiennent au calendrier de négociation de la source ;
aucun calendrier moderne n'est imposé rétroactivement.

### 15 octobre 2026 — description de la volatilité réalisée

Le porteur autorise une étape descriptive limitée à la série déjà construite.
Le notebook correspondant examine sa trajectoire historique, sa distribution,
ses périodes extrêmes, son autocorrélation et ses limites comme mesure du
risque, sans ajouter de modèle ni de données.

Sur 26 312 observations, la volatilité annualisée à cinq séances présente une
médiane de 10,61 %, une moyenne de 13,44 %, un 99e centile de 55,74 % et un
maximum de 148,60 %. La distribution est fortement dissymétrique. Le seuil
descriptif du 99e centile rassemble 264 observations en 48 séquences contiguës.

L'autocorrélation vaut 0,938 au décalage d'une séance, où quatre des cinq
rendements sont partagés par construction. Elle reste à 0,668 au décalage de
cinq séances, où les fenêtres ne partagent plus directement de rendement. La
persistance très courte ne doit donc pas être confondue avec une preuve de
prévisibilité ; le chevauchement en explique nécessairement une partie.

### 15 octobre 2026 — corrections après revue des deux notebooks

Le porteur valide globalement les deux notebooks et demande quatre corrections
sans changement de méthode ni de résultat :

- les dates des épisodes extrêmes sont explicitement des dates d'origine `t` ;
  chaque valeur concerne les cinq séances futures, désormais affichées pour le
  pic de chaque épisode ;
- le seuil du 99e centile est qualifié de descriptif, rétrospectif et calculé
  sur l'ensemble de l'échantillon ;
- l'archive brute utilisée est conservée localement en lecture seule sous
  `data/raw/`, exclue de Git et contrôlée par son empreinte SHA-256 ;
- le README distingue la validation de la définition et de la construction
  technique de la cible de sa pertinence économique, qui reste à établir.

### 15 octobre 2026 — troisième expérience simple autorisée et exécutée

Le porteur autorise une seule comparaison : une prévision constante fondée sur
la moyenne de `RV5` pendant l'apprentissage 1990–2015 contre la volatilité
historique des 20 séances connues à `t`. La fenêtre de 20 séances est imposée,
sans optimisation. L'évaluation 2016–2019 est explicitement exploratoire et les
cibles sont purgées aux frontières pour rester entièrement dans leur période.

Sur 1 001 dates d'évaluation, la volatilité historique 20 obtient une MAE de
4,839 points de volatilité annualisée contre 7,054 pour la constante, soit une
réduction descriptive de 31,40 %. Sa RMSE vaut 6,796 contre 8,129, soit une
réduction de 16,41 %. Elle présente une surestimation moyenne de 0,873 point,
contre 3,639 points pour la constante.

Ce meilleur résultat moyen n'est pas uniforme : la constante obtient une RMSE
plus faible en 2019. La volatilité historique 20 sous-estime aussi la cible sur
36,7 % des dates, contre 21,1 % pour la constante. Une erreur moyenne plus faible
ne suffit donc pas à établir une meilleure maîtrise financière du risque.

### 15 octobre 2026 — diagnostic des erreurs existantes autorisé

Le porteur autorise l'examen des prévisions déjà calculées dans le notebook 03,
sans nouvelle donnée, variable ou méthode prédictive. Les dix plus fortes
sous-estimations et surestimations de la volatilité historique 20 sont décrites
rétrospectivement à partir des rendements qui composent déjà la prévision et la
cible.

Parmi les dix dates de plus forte sous-estimation, la séance future dominante
représente une part médiane de 55,5 % de la somme des cinq rendements futurs au
carré. Parmi les dix plus fortes surestimations, le rapport médian entre l'énergie
des cinq rendements futurs et celle des cinq rendements les plus anciens sur le
point de sortir de la fenêtre vaut 0,28. Ces observations sont compatibles avec
une réaction retardée aux mouvements soudains et avec une mémoire temporaire des
mouvements passés, sans établir une cause ni un signal disponible à `t`.

Les dates extrêmes se concentrent dans quelques épisodes et leurs cibles se
chevauchent. Les dix lignes de chaque tableau ne sont donc pas dix événements
indépendants ; leurs résumés ne doivent pas être interprétés comme une fréquence
générale.

### 15 octobre 2026 — EDA limitée des données brutes autorisée et exécutée

Après correction d'une ambiguïté rédactionnelle, le porteur autorise un dossier
`EDA` et un unique notebook consacré à la nature des rendements déjà utilisés.
Sont explicitement exclus : nouveaux modèles ou nouvelles cibles, variables
économiques, détection de crises ou de régimes, tests statistiques avancés,
suppression automatique des extrêmes, analyse de `SMB` ou `HML` et répétition
exhaustive des notebooks 01–03.

L'exécution sur la copie locale immuable retrouve 26 317 séances du 1er juillet
1926 au 31 août 2026, sans valeur manquante ni date dupliquée. Les 1 158 séances
historiques du samedi sont conservées et aucune date n'est ajoutée. Le rendement
de marché étudié reste exclusivement `(Mkt-RF + RF) / 100`.

La distribution quotidienne présente un écart-type de 1,077 %, une asymétrie de
-0,166 et une kurtosis excédentaire de 16,125. Ces valeurs décrivent des queues
épaisses ; elles ne constituent pas un test statistique. L'autocorrélation au
décalage d'une séance vaut 0,046 pour le rendement, contre 0,298 pour son
amplitude et 0,259 pour son carré. Cette différence est compatible avec une
faible dépendance linéaire du signe et une persistance de l'amplitude, sans
établir une prévision exploitable ni une cause économique.

L'exemple du 19 octobre 1987 montre qu'un seul rendement entre dans cinq cibles
`RV5` successives et représente entre 72,75 % et 89,67 % de leur somme de carrés.
Il matérialise à la fois la dépendance mécanique due au chevauchement et le bruit
d'une mesure construite sur cinq observations seulement.

Un approfondissement ultérieur, autorisé dans le même notebook et sans nouvelle
méthode prédictive, généralise ce diagnostic. Une seule séance représente plus de
50 % de la somme des carrés dans 63,90 % des cibles `RV5`, et plus de 75 % dans
17,00 % des cibles. Autour des 264 amplitudes dépassant le 99e centile global
rétrospectif, l'amplitude médiane reste élevée avant et après la date centrale ;
les trajectoires peuvent toutefois se chevaucher et ne sont pas des événements
indépendants.

Sur l'évaluation exploratoire 2016–2019 déjà examinée, les 10 % de dates ayant
les plus fortes erreurs concentrent 62,61 % de l'erreur carrée totale. À niveau
de `RV5` comparable, la concentration de la cible ne classe pas régulièrement la
MAE : la difficulté ne se réduit donc pas à la domination d'une séance future.
Ces constats sont descriptifs et ne constituent pas une confirmation indépendante.

## Décisions en vigueur

| ID | Statut | Décision | Conséquence |
|---|---|---|---|
| D004 | Contrainte maintenue | la période 2020–août 2026 a déjà été consultée | elle ne peut pas être présentée comme une évaluation finale intacte |
| D009 | Constat maintenu | le notebook exploratoire antérieur n'a pas été audité dans ce dépôt | ses résultats ne constituent pas une base validée |
| D011 | Validé par le porteur | versionner le projet dans un dépôt GitHub public | préserver la traçabilité sans publier de secrets ni de données brutes |
| D013 | Supplanté | la Phase 0 n'était pas validée avant le 15 octobre 2026 | remplacé par D021 |
| D018 | Validé par le porteur | aucune extension scientifique sans demande ou validation explicite | toute nouvelle orientation doit être proposée avant intégration |
| D019 | Validé par le porteur | privilégier la méthode la plus simple répondant à la question active | aucune complexité préventive |
| D020 | Validé et exécuté | réaliser un seul notebook d'audit de la cible à cinq séances | audit réussi ; aucun modèle n'a été entraîné |
| D021 | Validé par le porteur | la Phase 0 est validée le 15 octobre 2026 | le cadrage est clos ; la prochaine action reste soumise à autorisation |
| D022 | Constat | la cible utilise exactement les séances `t+1` à `t+5` et les contrôles de construction passent | cela établit l'alignement de la cible, pas encore celui des variables d'un futur modèle |
| D023 | Constat | la cible est très dissymétrique, extrême par épisodes et fortement autocorrélée | le chevauchement explique mécaniquement une partie de la persistance de court terme ; aucune prévisibilité hors échantillon n'est encore établie |
| D024 | Validé par le porteur | conserver localement le millésime brut immuable et vérifier son SHA-256 | les résultats restent reproductibles même si la source distante évolue ; le fichier brut demeure exclu de Git |
| D025 | Constat exploratoire | sur 2016–2019, la volatilité historique 20 améliore en moyenne MAE et RMSE face à la constante 1990–2015 | résultat non uniforme selon l'année, sans test statistique ni confirmation indépendante ; aucune supériorité financière établie |
| D026 | Constat descriptif | les plus fortes erreurs sont cohérentes avec le décalage entre la fenêtre passée et les cinq rendements futurs | sélection rétrospective et cibles chevauchantes ; aucune détection en temps réel ni explication causale établie |
| D027 | Validé et exécuté | réaliser puis approfondir une EDA limitée aux rendements et prévisions déjà utilisés | composition de `RV5`, trajectoires extrêmes et concentration des erreurs sont documentées sans étendre le périmètre scientifique |

## Prochaine décision nécessaire

Examiner les résultats de l'EDA et de la troisième expérience, puis définir
explicitement la question minimale suivante. Aucun modèle, test supplémentaire
ou extension des données n'est autorisé sans accord du porteur.
