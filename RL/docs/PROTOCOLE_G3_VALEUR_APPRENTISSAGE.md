# Protocole G3 — valeur incrémentale de l'apprentissage

## 1. Statut et frontière d'interprétation

**Statut : `FROZEN_BEFORE_G3_EXECUTION`.**

Ce protocole est figé avant le calcul de toute performance G3. G3 teste si des
paramètres appris uniquement dans le passé améliorent une politique dynamique
par rapport au contrôleur stylisé `D_G2`. Il ne teste pas encore PPO, CQL ou
IQL et ne constitue pas une preuve de rentabilité déployable.

L'épisode G2 2024–2025 a déjà été consulté et reste réservé au diagnostic et à
la validation du code. La mesure primaire G3 utilise une fenêtre temporelle
postérieure et ne permet aucune sélection d'hyperparamètres après observation.

## 2. Question scientifique

> À état, espace d'actions, horizon et coût identiques, le remplacement des
> paramètres stylisés de `D_G2` par des paramètres estimés sans fuite temporelle
> apporte-t-il une valeur économique appariée sur une période future ?

Le contraste causal visé est donc :

\[
\Delta_{learn}=V(\pi_{learned})-V(\pi_{D\_G2}).
\]

Les deux politiques utilisent le même signal à quatre semaines, la même
position héritée et le même programme dynamique. Seuls les rendements
conditionnels et la matrice de transition sont appris par `pi_learned`.

## 3. Données et séparation temporelle

- source de prix : réponses Yahoo SPY/BIL gelées au manifeste et vérifiées par
  SHA-256 ;
- entraînement initial : du 30 mai 2007 au 28 mai 2024 inclus ;
- aucune observation 2024–2025 n'entre dans la mesure primaire ;
- évaluation primaire : décisions du 2 juin 2025 au 13 avril 2026, avec dernier
  close terminal au 17 avril 2026 ;
- la borne du 17 avril 2026 est imposée par le verrou documentaire préexistant :
  l'open SPY du 20 avril 2026 est contesté. Elle est fixée avant performance G3 ;
- les paramètres sont réestimés en fenêtre croissante avant chaque décision,
  sans utiliser le rendement réalisé après cette décision.

La fenêtre 2025–2026 est une réplication temporelle exploratoire et non un test
vierge au sens fort : sa configuration documentaire existait déjà. En revanche,
aucun résultat de la politique apprise n'a été observé lors du gel de ce
protocole.

## 4. Variables et estimation

Sur les premiers closes communs de chaque semaine, le signal est

\[
X_t=\log(P^S_t/P^S_{t-4})-\log(P^B_t/P^B_{t-4}),
\qquad
Z_t=\mathbf 1\{X_t\ge 0\}.
\]

Les rendements d'une période sont les log-rendements du close hebdomadaire
admissible au close hebdomadaire suivant. Pour chaque date de décision, le
modèle appris estime sur les observations strictement antérieures :

\[
\widehat\mu_{a,z}=\frac{1}{N_z}\sum_{t:Z_t=z} r_{t+1}(a),
\qquad
\widehat p_{zz'}=
\frac{N_{zz'}+1/2}{N_z+1}.
\]

La correction de Jeffreys `1/2` est préspecifiée pour empêcher des transitions
nulles. Aucune variable supplémentaire, aucun seuil de signal et aucune
pondération temporelle ne sont autorisés dans G3.

## 5. Politiques

L'espace d'actions SPY reste

\[
\mathcal A=\{0,0.25,0.50,0.75,1\},
\]

avec poids BIL `1-a`, horizon dynamique de 12 décisions et coût proportionnel
de 10 pb appliqué au changement de poids. La récompense de contrôle est

\[
u_t(a)=r_{t+1}(a)-c|a-a_{t^-}|.
\]

- `D_G2_FROZEN` : modèle stylisé exact de G2, sans recalibrage ;
- `D_G3_LEARNED` : même solveur dynamique, avec paramètres estimés en fenêtre
  croissante ;
- `M_G3_LEARNED` : contrôle myope appris, rapporté comme diagnostic secondaire.

Les quatre premières décisions de la mesure primaire sont un warm-up commun à
50/50. Le poids hérité est ensuite celui de l'action précédente de chaque
politique.

## 6. Mesure économique G3A

G3A utilise une comptabilité continue close-à-close volontairement séparée du
moteur d'exécution :

\[
W_{t+1}=W_t\exp\{a_t r^S_{t+1}+(1-a_t)r^B_{t+1}}
\bigl(1-c|a_t-a_{t^-}|\bigr).
\]

Elle isole la valeur du modèle appris sans dépendre d'un open contesté, des
parts entières ou du règlement. Elle ne doit jamais être présentée comme une
performance du registre financier complet.

Mesure primaire : différence de richesse terminale entre `D_G3_LEARNED` et
`D_G2_FROZEN` à 10 pb. Mesures secondaires : log-richesse, drawdown,
volatilité, turnover, nombre de changements d'action et fréquence de désaccord.

## 7. Contrôles négatifs obligatoires

1. chaque estimation s'arrête strictement avant le rendement évalué ;
2. modifier un rendement futur ne change aucune action antérieure ;
3. le solveur stylisé reproduit exactement `D_G2` pour les états testés ;
4. une série où les paramètres vrais égalent ceux de G2 ne crée pas
   artificiellement une différence d'implémentation ;
5. les trois politiques partagent dates, rendements, coûts et warm-up ;
6. toutes les sorties sont reproductibles octet pour octet.

## 8. Règle de verdict

Le seuil préspecifié reste 25 pb du capital initial, soit 250 USD :

- `G3_LEARNING_VALUE_POSITIVE` si `D_G3_LEARNED - D_G2_FROZEN >= 250 USD` ;
- `G3_LEARNING_VALUE_NEGATIVE` si la différence est `<= -250 USD` ;
- `G3_LEARNING_VALUE_NOT_MATERIAL` sinon ;
- `DOCUMENTARY_BLOCK` si une source ou une borne temporelle n'est pas vérifiable.

Le verdict doit être rapporté quel que soit son signe. Un résultat positif
autorise uniquement G3B : traduction dans le registre financier complet après
résolution documentaire de l'open du 20 avril 2026 ou sur une nouvelle période
prospective. Il n'autorise pas automatiquement PPO. Un résultat nul ou négatif
interdit l'escalade vers un agent plus complexe sans nouvelle hypothèse
scientifique préspécifiée.

## 9. Sorties attendues

Sous `RL/results/g3_learning_value/` :

- `model_estimates.csv` ;
- `policy_decisions.csv` ;
- `wealth_paths.csv` ;
- `paired_comparison.csv` ;
- `g3_report.json`.

Le rapport doit inclure les empreintes des sources, du présent protocole et de
toutes les sorties, ainsi que la frontière d'interprétation G3A.
