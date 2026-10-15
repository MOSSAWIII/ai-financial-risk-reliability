# Phase 0 — cadrage scientifique simplifié

**Version :** 3, 14 octobre 2026

**Statut :** Phase 0 validée par le porteur du projet le 15 octobre 2026

**Référence supérieure :** `CADRAGE_PROJET_RECHERCHE_IA_FINANCE_CODEX.txt`

Cette version ne crée aucune nouvelle orientation scientifique. Elle retire du
protocole actif les choix introduits trop tôt dans les versions précédentes et
revient au périmètre du document fondateur. Toute extension future devra être
proposée séparément et validée explicitement par le porteur du projet.

## 1. Audit de périmètre des versions précédentes

### Décisions introduites par l'assistant

| Décision introduite | Pourquoi elle dépassait le mandat immédiat | Correction dans cette version |
|---|---|---|
| Faire de l'anticipation de la dégradation le cœur du projet | Le mandat demande d'abord d'étudier la fiabilité sous changement d'environnement ; il ne choisit pas encore entre reconnaître, anticiper ou corriger une dégradation | Anticipation replacée parmi les questions possibles, sans priorité active |
| Choisir un gestionnaire d'exposition actions doté d'un budget de risque comme utilisateur de référence | Ce cas est plausible, mais le porteur du projet ne l'a pas validé | Conservé seulement comme illustration de motivation financière |
| Faire du contraste « niveau élevé contre transition rapide » la première expérience | Cette question nouvelle remplaçait l'étape préalable de définition et d'audit de la cible | Expérience retirée du protocole actif et reportée |
| Imposer une erreur logarithmique signée, un appariement sur le niveau et une règle de persistance | Ces moyens répondaient à l'expérience précédente, elle-même non validée | Choix retirés ; aucune méthode correspondante n'est retenue |
| Décomposer immédiatement le projet en six objectifs d'IA et privilégier certains d'entre eux | La taxonomie était utile pour réfléchir, mais transformait une exploration en programme de recherche | Retour aux trois fonctions du mandat : reconnaître une limite, quantifier l'incertitude, maintenir ou retrouver une fiabilité acceptable |
Les autres choix techniques et extensions proposés dans les versions
précédentes sont supprimés du cadrage courant. Ils ne constituent plus des
options du projet.

## 2. Problématique retenue sans extension

### Phénomène étudié

Le projet cherche à comprendre comment un changement de l'environnement
économique et financier peut affecter la **fiabilité** d'une prévision du risque
de marché. Une hausse du risque observé et une perte de fiabilité prédictive ne
sont pas équivalentes : un modèle peut rester fiable dans un marché volatil, ou
devenir peu fiable avant qu'une forte volatilité soit visible.

### Question centrale

> Comment les changements d'environnement économique affectent-ils la
> fiabilité des prévisions du risque financier, et dans quelle mesure des
> méthodes prédictives peuvent-elles reconnaître leurs limites, quantifier leur
> incertitude et maintenir ou retrouver une fiabilité acceptable lorsque les
> conditions évoluent ?

Cette formulation reprend l'ambition du document fondateur. Elle ne présuppose
ni la supériorité du ML, ni la nécessité d'un nouveau modèle, ni l'existence
d'une solution adaptative.

### Articulation économie–finance–IA

- **Économie :** des changements de conjoncture, de politique monétaire,
  d'incertitude ou de contraintes financières peuvent modifier les relations
  qui rendaient le risque prévisible. Ce sont des mécanismes plausibles, pas des
  causes établies ni des variables déjà retenues.
- **Finance :** une sous-prévision peut laisser une exposition excessive ; une
  sur-prévision peut conduire à une réduction inutile de l'exposition. La
  précision moyenne ne suffit donc pas à établir l'utilité d'une prévision.
  L'utilisateur et la décision exacts restent à préciser avant toute évaluation
  décisionnelle.
- **IA/statistique :** il faut d'abord mesurer loyalement la fiabilité dans le
  temps et représenter honnêtement l'incertitude. Aucun développement de méthode
  n'est engagé avant que le problème empirique soit établi.

## 3. Fondement économique volontairement limité

Trois mécanismes généraux suffisent actuellement à motiver l'enquête. Ils ne
justifient encore ni ajout de données ni revendication causale.

| Mécanisme plausible | Transmission financière attendue | Pourquoi la prévisibilité pourrait changer | Ce qu'une analyse observationnelle ne prouverait pas |
|---|---|---|---|
| Révision des anticipations de croissance, d'inflation ou de taux | Révision des prix, primes et volatilité | Les sensibilités apprises dans un contexte peuvent ne plus être stables | Qu'un indicateur économique précis cause la panne |
| Hausse de l'incertitude et du désaccord | Dispersion des croyances, mouvements discontinus | Les situations comparables deviennent rares et l'incertitude passée moins informative | Que l'incertitude mesurée est exogène aux prix |
| Contraintes de financement, levier et liquidité | Amplification des baisses et hausse conjointe du risque | Une dynamique non linéaire peut remplacer la persistance observée en temps normal | Le sens causal entre liquidité, levier et volatilité |

Ces mécanismes resteront des explications concurrentes à confronter seulement
si une instabilité empirique est d'abord établie. Aucune variable associée
n'entre dans le protocole actuel.

## 4. Ce qui est établi, ouvert ou seulement potentiel

### Éléments établis par la littérature de départ

- La volatilité présente une persistance importante ; une référence simple et
  correctement calibrée peut être difficile à battre uniformément.
- L'évaluation dépend de la cible et de la fonction de perte ; une amélioration
  statistique moyenne n'implique pas automatiquement une amélioration
  financière.
- Les performances peuvent varier dans le temps ; une évaluation moyenne peut
  masquer des périodes de dégradation.
- Une garantie ou une calibration obtenue dans un environnement donné ne doit
  pas être supposée inchangée sous changement de distribution.

Le socle bibliographique actif reste volontairement court : Engle et Patton
(2001), Hansen et Lunde (2005), Corsi (2009), Patton (2011), ainsi que Moreira
et Muir (2017). Les références supplémentaires repérées dans la version 2
demeurent traçables dans Git, mais ne justifient aucune méthode active et ne
fondent aucune revendication de nouveauté.

### Hypothèses ouvertes issues du document fondateur

- **H1 :** les erreurs se dégradent davantage pendant certaines transitions
  que pendant des périodes stables comparables.
- **H2 :** un gain statistique moyen n'implique pas nécessairement un gain
  financier.

Ces hypothèses structurent l'ambition générale, mais ne sont pas à tester
maintenant. H1 n'autorise pas à imposer immédiatement une définition de
« transition » ; H2 exige d'abord une décision financière explicite.

### Contribution potentielle, non revendiquée

La contribution pourrait porter sur une caractérisation rigoureuse de la perte
de fiabilité sous changement d'environnement, puis éventuellement sur une
manière de la signaler ou de la limiter. Elle reste conditionnelle aux résultats
et à une revue de littérature plus approfondie. Comparer des algorithmes ou
ajouter une méthode connue ne constituerait pas, en soi, une contribution.

## 5. Objet empirique initial et choix encore ouverts

Le document fondateur délimite l'objet de départ : rendement quotidien du
portefeuille de marché américain Fama–French et risque réalisé sur les cinq
séances futures. Une définition candidate est :

\[
RV_{5,t}=\sqrt{\frac{252}{5}\sum_{k=1}^{5}r_{t+k}^{2}},
\]

avec les rendements exprimés en décimal. Son annualisation, son traitement des
rendements moyens et son interprétation comme mesure approchée d'une volatilité
latente doivent être explicités avant calcul.

Les décisions indispensables à l'étape immédiate sont seulement :

1. définir sans ambiguïté la cible à cinq séances et ses unités ;
2. définir l'information autorisée à la date `t` et vérifier l'alignement
   `t+1` à `t+5` ;
3. conserver MAE et RMSE comme mesures initiales prévues par le document
   fondateur, sans désigner encore une métrique unique comme vérité scientifique.

## 6. Contraintes déjà indispensables

Les éléments suivants ne sont pas une sophistication facultative ; ils
conditionnent la validité de toute expérience ultérieure :

- aucune information postérieure à `t` dans les variables explicatives ;
- séparation chronologique entre ajustement, validation et évaluation ;
- prise en compte du chevauchement des cibles à cinq séances avant toute
  inférence ;
- comparaison à des références simples calibrées loyalement ;
- conservation des prévisions individuelles et des choix effectués ;
- qualification de 2020–août 2026 comme période déjà consultée, donc non
  assimilable silencieusement à un test final intact ;
- distinction entre association prédictive et interprétation causale.

Le notebook Colab antérieur n'a pas été audité dans ce dépôt. Ses résultats ne
constituent donc pas une base validée.

## 7. Protocole initial réduit au strict nécessaire

La Phase 0 ne contient plus de séquence E0–E6 ni d'expérience comparative déjà
figée. Elle doit seulement produire, puis faire valider :

1. une définition formelle de la cible initiale ;
2. une convention temporelle vérifiable pour chaque observation ;
3. une description de la source, des unités et des transformations autorisées ;
4. un principe de découpage chronologique ;
5. les critères minimaux qui rendront une future comparaison interprétable.

Aucun modèle ni ajout de données n'appartient au protocole actif.

## 8. Prochaine étape la plus simple

Après validation explicite de la Phase 0, la première étape recommandée est un
unique notebook consacré à une seule question :

> Pouvons-nous construire et auditer sans ambiguïté la volatilité réalisée des
> cinq séances futures à partir des rendements Fama–French, en garantissant que
> toute information prédictive est disponible à la date `t` ?

Ce notebook ne comparera aucun modèle. Il devra afficher quelques observations
calculées manuellement, les dates utilisées pour chaque cible, les unités avant
et après transformation, les valeurs manquantes et les contrôles d'alignement.

Le critère de réussite sera la reproductibilité exacte de la cible et l'absence
de fuite temporelle. En cas d'ambiguïté ou d'échec, aucune modélisation ne devra
commencer. Cette étape n'est pas lancée par le présent document.

## 9. Décisions validées par le porteur

La validation de la Phase 0 confirme :

1. la question centrale formulée dans ce document ;
2. la volatilité réalisée annualisée des cinq séances futures comme cible
   initiale, avec rendements en décimal et la formule présentée à la section 5 ;
3. les contraintes de validité et le protocole initial limité décrits ci-dessus.

Le choix d'un utilisateur financier précis, d'une métrique primaire, d'une
définition de transition ou d'un modèle ne demande aucune décision maintenant,
car aucun de ces éléments n'appartient à l'étape immédiate.

**Clôture de phase :** la Phase 0 est validée. Le notebook unique d'audit décrit
à la section 8 a ensuite été autorisé et exécuté le 15 octobre 2026. Cette
autorisation ne s'étend à aucune autre expérience.
