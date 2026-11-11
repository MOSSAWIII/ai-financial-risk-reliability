# Clôture scientifique du candidat RL SPY–BIL

## Décision

**Statut : `CLOSED_AS_NEGATIVE_RL_NECESSITY_RESULT`.**

Le mandat SPY–BIL n'est pas abandonné comme infrastructure financière. Son
registre, ses contrôles temporels, ses conventions de règlement et ses
benchmarks restent valides et réutilisables. En revanche, la question
« faut-il un algorithme RL pour ce problème ? » est close sous la formulation
actuelle.

## Chaîne de résultats

1. G1 a montré qu'une position héritée et des coûts intermédiaires peuvent
   créer une valeur séquentielle dans un modèle synthétique.
2. G2 a retrouvé une différence matérielle entre contrôleur dynamique et
   contrôleur myope dans le moteur historique SPY–BIL.
3. G3A a appris les paramètres en fenêtre croissante et a dépassé
   `D_G2_FROZEN` de 5 297,85 USD sous le proxy close-à-close.
4. La validation canonique a reproduit exactement les quatre sorties de la
   réplication indépendante.
5. `D_G3_LEARNED` et `M_G3_LEARNED` ont pourtant produit les mêmes actions et
   la même richesse : après quatre décisions à 50/50, les deux ont conservé
   100 % SPY.

Le contraste décisif est donc

\[
V(D_{G3})-V(M_{G3})=0,
\]

malgré

\[
V(D_{G3})-V(D_{G2})>0.
\]

L'apprentissage a modifié l'exposition moyenne, mais la planification
séquentielle apprise n'a rien ajouté.

## Ce que le résultat permet d'affirmer

- Le contrôleur stylisé G2 était mal calibré pour la fenêtre G3A.
- L'estimation empirique des rendements conditionnels a une importance
  économique dans ce proxy.
- Une règle simple reproduit la politique apprise.
- L'ajout de PPO, CQL ou IQL ne possède aucune justification empirique sous
  l'état, les actions et l'objectif actuels.

## Ce que le résultat ne permet pas d'affirmer

- que le RL est inutile en finance ;
- que 100 % SPY constitue une stratégie généralisable ;
- que les richesses G3A sont des rendements exécutables ;
- que les contraintes de risque, d'inventaire ou de liquidité sont sans valeur ;
- que le moteur SPY–BIL doit être supprimé.

## Règle de non-réouverture

Le candidat SPY–BIL ne peut être rouvert au RL simplement en ajoutant des
variables, un réseau neuronal ou un nouvel algorithme. Une réouverture exige au
minimum une nouvelle décision financière, une nouvelle source d'interdépendance
endogène et un protocole gelé avant les résultats.

La suite du programme est G4 : rechercher un problème où la décision présente
modifie réellement les possibilités futures, puis tenter de falsifier ce besoin
avant tout apprentissage complexe.
