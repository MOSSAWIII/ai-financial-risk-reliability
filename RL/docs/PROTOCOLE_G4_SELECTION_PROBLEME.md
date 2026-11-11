# Protocole G4 — sélection d'un problème réellement séquentiel

## 1. Statut

**Statut : `FROZEN_BEFORE_G4_DATA_AUDIT`.**

G4 ne démarre pas par le choix d'un algorithme. Il sélectionne d'abord une
décision financière pour laquelle l'action actuelle modifie un état contrôlé et
les décisions futures. Aucun rendement G4 n'a été calculé au moment du gel.

## 2. Candidats examinés

| Candidat | Séquentialité endogène | Données publiques | Comparateurs crédibles | Décision |
|---|---:|---:|---:|---|
| SPY–BIL enrichi de signaux | faible après G3A | forte | forte | rejeté |
| Allocation multi-actifs contrainte | forte | moyenne à forte | forte | retenu |
| Exécution avec inventaire | très forte | faible | forte | réserve future |
| Couverture dynamique d'options | très forte | faible | forte | réserve future |

Le candidat retenu maximise la possibilité de falsification avec des données
publiques et des références classiques solides. L'exécution et la couverture
offrent une structure séquentielle supérieure, mais nécessitent des données de
microstructure ou d'options qui ne sont pas encore disponibles.

## 3. Mandat candidat

Un gestionnaire long-only répartit chaque semaine son portefeuille entre quatre
poches économiques candidates : actions américaines, Treasuries intermédiaires,
or et actif monétaire. Les instruments de représentation proposés sont SPY,
IEF, GLD et BIL, mais ils ne deviennent définitifs qu'après G4.1, l'audit des
prix, distributions, dates de lancement et calendriers.

L'espace d'actions initial est la grille simplexe par pas de 25 % :

\[
\mathcal A=\left\{w\in\{0,0.25,0.5,0.75,1\}^4:
\sum_{i=1}^{4}w_i=1\right\},
\]

soit 35 allocations. Les positions sont long-only, sans levier ni vente à
découvert.

## 4. Source de séquentialité

L'état contrôlé minimal est

\[
S_t=(w_{t^-}, B_t, W_t, DD_t, \widehat\Sigma_t, Z_t),
\]

où `w_{t^-}` est l'allocation héritée, `B_t` le budget de turnover restant,
`W_t` la richesse, `DD_t` le drawdown courant, `Sigma_t` une covariance
strictement point-in-time et `Z_t` un état de marché minimal.

Le budget évolue selon

\[
B_{t+1}=B_t-\tfrac12\lVert w_t-w_{t^-}\rVert_1.
\]

Une transaction aujourd'hui consomme donc irréversiblement une ressource qui
pourrait être utile demain. Cette variable, en plus des coûts et de la position
héritée, crée l'interdépendance à tester.

## 5. Objectif et contraintes

L'objectif primaire reste la log-richesse terminale nette :

\[
\max_\pi\;\mathbb E_\pi[\log W_T].
\]

Les préférences de risque ne sont pas cachées dans une somme arbitraire de
pénalités. Elles sont rapportées ou imposées séparément :

\[
w_{i,t}\ge 0,\qquad \sum_iw_{i,t}=1,
\]

\[
\tfrac12\lVert w_t-w_{t^-}\rVert_1
\le \min(0.25,B_t),
\]

et une limite de volatilité ex ante candidate de 12 % annualisés. Cette limite
doit faire l'objet d'une analyse de faisabilité avant adoption définitive ; elle
ne sera pas ajustée pour améliorer un résultat observé.

## 6. Comparateurs obligatoires

Avant toute méthode RL, la même comptabilité doit exécuter :

1. allocations statiques par poche et portefeuille équipondéré ;
2. 60/40 actions–obligations ;
3. volatility targeting ;
4. risk parity ;
5. moyenne–variance avec estimation roulante ;
6. contrôleur à zone de non-transaction ;
7. model predictive control à horizon court ;
8. politique myope apprise ;
9. programmation dynamique oracle sur laboratoire discret.

Une méthode apprise doit battre les comparateurs simples sans seulement prendre
plus de risque ou consommer davantage le budget de turnover.

## 7. Portes G4

| Porte | Exigence | Conséquence d'un échec |
|---|---|---|
| G4.0 | clôture SPY–BIL enregistrée | arrêt |
| G4.1 | données point-in-time et distributions auditables | blocage documentaire |
| G4.2 | DP oracle matériellement supérieur au myope dans un laboratoire préspecifié | retour à un problème plus simple |
| G4.3 | comparateurs classiques implémentés dans le même moteur | apprentissage interdit |
| G4.4 | support suffisant des états/actions hors ligne | CQL/IQL interdits |
| G4.5 | gain walk-forward après coûts, risque et tests multiples | résultat négatif conservé |

PPO exige en plus un simulateur validé dont les trajectoires conditionnelles,
queues de distribution, coûts et transitions résistent à des contrôles
empiriques. La simple répétition de l'histoire ne constitue pas un simulateur.

## 8. Prochaine opération autorisée

Seule G4.1 est autorisée : audit documentaire et statistique des quatre poches,
avec inventaire des sources et couverture commune. Aucun backtest, réglage de
signal, sélection de fenêtre ou entraînement n'est autorisé avant ce jalon.
