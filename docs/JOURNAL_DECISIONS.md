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

## Questions ouvertes qui conditionnent la suite

1. Validation ou modification de D001 à D005.
2. Choix du holdout indépendant : marché externe préspécifié ou attente de
   nouvelles données ; recommandation actuelle : marché Developed ex US pour la
   validation externe, futures observations US pour une réplication ultérieure.
3. Obtention éventuelle du notebook Colab original afin de séparer erreur de
   réplication et différence de protocole.
4. Définition primaire d'une transition observable en temps réel et seuil de
   matérialité, à décider seulement après le socle E0–E2.

