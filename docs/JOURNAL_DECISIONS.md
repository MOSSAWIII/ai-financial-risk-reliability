# Journal des décisions scientifiques

Ce journal distingue une décision validée par le porteur du projet d'une
recommandation encore ouverte. Il ne doit pas être réécrit rétroactivement : une
révision future ajoute une entrée datée et explique le motif.

## 15 octobre 2026 — Phase 0 proposée

| ID | Statut | Proposition | Justification | Alternative / limite |
|---|---|---|---|---|
| D001 | À valider | Objet initial : variance future du marché US sur 5 séances | périmètre précis et cohérent avec le prototype | VaR/ES et finance reportées |
| D002 | À valider | Cible principale `252/5 * somme(r²)` ; racine pour affichage | QLIKE exige une variance positive ; unités explicites | proxy quotidien bruité, pas RV intraday |
| D003 | À valider | Perte primaire QLIKE | robustesse au bruit du proxy sous les conditions de Patton | MAE-vol et RMSE restent secondaires |
| D004 | À valider | 2020–août 2026 = diagnostic contaminé | résultats déjà consultés | holdout externe ou données futures requis |
| D005 | À valider | Première comparaison : EWMA recalibré vs Boosting | teste directement la fragilité la plus nette du prototype | aucune conclusion générale sans GARCH/GJR |
| D006 | Recommandé | Inférence appariée, blocs 22 + sensibilités 5/10/44/60 + non-overlap | cible à horizon chevauchant | longueur optimale inconnue ex ante |
| D007 | Recommandé | Variables macro exclues du socle | évite révisions et horodatage prématurés | ajout ultérieur via ALFRED |
| D008 | Recommandé | Régimes NBER uniquement descriptifs ex post | annonces non disponibles en temps réel | détecteur unilatéral à préspécifier |
| D009 | Constat | Notebook Colab non audité | lien non lisible dans l'environnement utilisé | demander le fichier `.ipynb` |
| D010 | Constat | Dépôt initial effectivement limité au fichier de cadrage | inspection locale du 15 octobre 2026 | aucune structure antérieure à préserver |
| D011 | Validé par le porteur | Versionner le projet dans un dépôt GitHub public | transparence, traçabilité et collaboration | ne pas publier secrets ni données brutes |
| D012 | Ouvert | Aucune licence ajoutée pour l'instant | rendre public ne suffit pas à définir les droits de réutilisation | choisir ultérieurement MIT, Apache-2.0 ou une autre licence |

## Questions ouvertes de la version 1 (désormais supplantées)

La liste ci-dessous est conservée comme trace historique. L'entrée de révision
qui suit détermine les seuls blocages actuels.

1. Validation ou modification de D001 à D005.
2. Choix du holdout indépendant : marché externe préspécifié ou attente de
   nouvelles données ; recommandation actuelle : marché Developed ex US pour la
   validation externe, futures observations US pour une réplication ultérieure.
3. Obtention éventuelle du notebook Colab original afin de séparer erreur de
   réplication et différence de protocole.
4. Définition primaire d'une transition observable en temps réel et seuil de
   matérialité, à décider seulement après le socle E0–E2.

## 15 octobre 2026 — rejet de la version 1 et réouverture du cadrage

Le porteur du projet a explicitement refusé la Phase 0. Motif : cadrage devenu
prématurément statistique, articulation économie–finance–IA insuffisante et
choix méthodologiques trop tôt transformés en protocole directeur. Cette entrée
ne remplace pas le tableau précédent ; elle en conserve la trace et modifie son
statut à partir de cette date.

| ID | Statut après critique | Révision |
|---|---|---|
| D001 | Rouvert | la variance à 5 séances redevient un instrument possible, non l'objet scientifique |
| D002 | Rouvert | volatilité, variance, risque de queue ou distribution seront choisis selon la décision financière |
| D003 | Retiré du protocole actif | QLIKE n'est pertinent que si la variance devient l'estimand ; aucune métrique primaire fixée |
| D004 | Maintenu comme contrainte | 2020–août 2026 reste contaminée par consultation antérieure, sans préjuger du futur holdout |
| D005 | Retiré du protocole actif | EWMA contre Boosting n'est plus la première question scientifique |
| D006 | Retiré du protocole actif | aucune longueur de bloc ou méthode d'inférence fixée avant diagnostic de dépendance |
| D007 | Révisé | aucune donnée macro immédiate, mais les mécanismes économiques structurent dès maintenant les hypothèses |
| D008 | Maintenu et précisé | dates NBER = diagnostic ex post ; état financier, régime statistique et environnement économique restent distincts |
| D011 | Maintenu | dépôt GitHub public et traçabilité de toutes les versions |
| D012 | Ouvert | licence toujours non choisie |

### Nouvelles propositions soumises à validation

| ID | Statut | Proposition | Justification | Limite |
|---|---|---|---|---|
| D013 | Constat | Phase 0 version 1 refusée ; aucune Phase 1 autorisée | instruction explicite du porteur | — |
| D014 | À valider | phénomène central = dégradation conditionnelle de fiabilité sous changement d'environnement | relie mécanismes, décision et confiance prédictive | formulation encore à challenger |
| D015 | À valider | utilisateur de référence = gestionnaire d'une exposition actions diversifiée avec budget de risque | cohérent avec le portefeuille de marché et les pertes asymétriques | autre utilisateur impliquerait autre cible |
| D016 | À valider | première expérience = niveau élevé contre hausse rapide à niveau comparable, avec une seule référence transparente | départage effet d'échelle et effet de transition | ne révèle pas encore le mécanisme économique |
| D017 | Provisoire | volatilité future sur 5 séances comme proxy de travail de la première expérience | continuité avec le prototype et lecture financière | cible finale et horizon restent ouverts |

### Décisions réellement bloquantes pour la prochaine implémentation

1. D015 : utilisateur et décision financière de référence.
2. D017 : proxy/horizon de la seule première expérience.
3. D016 : question niveau contre transition.
4. Accès éventuel au notebook Colab ; à défaut, accord futur pour reconstruire
   une unique référence transparente.

Toutes les anciennes recommandations relatives à QLIKE, au réentraînement
annuel, au bootstrap de 22 jours, au marché Developed ex US et à la séquence
E0–E6 sont explicitement non contraignantes.

