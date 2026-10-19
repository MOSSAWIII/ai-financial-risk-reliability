# Quand la gestion d'une exposition financière devient-elle un problème de décision séquentielle ?

**Date : 19 octobre 2026**

**Statut : première étude fondamentale ; aucune politique, fonction de récompense ou expérience n'est validée**

## 1. Question scientifique et périmètre

La question étudiée est volontairement antérieure au choix d'un algorithme :

> Dans quelles conditions les décisions successives de gestion d'une exposition financière exigent-elles une optimisation intertemporelle, et dans quelles conditions une règle fixe ou une optimisation période par période suffit-elle ?

Le cas provisoire est celui d'un gestionnaire de portefeuille disposant d'un budget de risque et choisissant une exposition à **un seul actif risqué**. Ce cas est un objet théorique minimal, pas encore l'objet empirique définitif de l'axe `RL/`. Il ne constitue pas une extension vers l'allocation multi-actifs.

Le projet principal motive cette question sans y répondre. Sur 2016–2019, les notebooks 03 à 07 montrent que plusieurs prévisions de `RV5` peuvent améliorer la précision moyenne tout en sous-estimant fortement la volatilité aux mêmes dates. Ils montrent aussi que deux alertes historiques simples reconnaissent mal le début de ces épisodes. Or `RV5` est une amplitude future annualisée, chevauchante, bruitée et insensible au signe : elle n'est ni une perte financière, ni une décision, ni une fonction d'utilité. Le passage de la prévision à l'action doit donc être construit explicitement.

L'étude distingue trois propositions souvent confondues :

1. les décisions sont prises à plusieurs dates ;
2. leur optimisation est réellement intertemporelle ;
3. leur solution doit être apprise par Reinforcement Learning (RL).

La première proposition n'implique pas la deuxième, et la deuxième n'implique pas la troisième.

## 2. Chronologie et notation communes

Les dates de décision sont `t = 0, ..., T-1`. La chronologie minimale est :

1. le gestionnaire observe l'information disponible `\mathcal F_t` ;
2. il choisit une exposition `A_t`, mesurable par rapport à `\mathcal F_t` ;
3. le rendement risqué `R_{t+1}` se réalise ;
4. les gains, coûts, contraintes et nouvel état de portefeuille deviennent observables.

Cette convention interdit d'utiliser `R_{t+1}` ou une volatilité construite avec des rendements futurs pour choisir `A_t`.

On note :

- `Z_t` : résumé observable de l'environnement de marché à `t` ;
- `A_t` : nouvelle exposition choisie à `t` ;
- `H_{t-1}` : exposition héritée juste avant cette décision ;
- `W_t` : richesse disponible ;
- `B_t` : éventuel état d'un budget ou d'une contrainte cumulée ;
- `R_{t+1}` : rendement de l'actif risqué entre `t` et `t+1` ;
- `C_t(A_t-H_{t-1})` : coût d'ajustement, lorsqu'il existe.

Le gestionnaire est supposé **preneur de prix** dans cette étude. Son action ne modifie donc pas la loi du marché :

$$
\mathbb P(Z_{t+1},R_{t+1}\mid \mathcal F_t,A_t=a)
=
\mathbb P(Z_{t+1},R_{t+1}\mid \mathcal F_t).
$$

Cette exogénéité du marché n'exclut pas un problème séquentiel. L'action peut laisser le marché inchangé tout en modifiant la position, la richesse ou les contraintes futures du portefeuille.

## 3. Situation A — décisions indépendantes

### 3.1 Formulation

Supposons que :

1. `A_t` appartient à un ensemble admissible `\mathcal A_t(\mathcal F_t)` qui ne dépend d'aucune action passée et n'impose aucune contrainte commune à plusieurs dates ;
2. l'action courante ne modifie ni la loi des variables exogènes futures, ni l'information future reçue ;
3. le gain total est additif :

$$
J(\pi)=\mathbb E^\pi\!\left[\sum_{t=0}^{T-1}
g_t(A_t,Z_t,R_{t+1})\right] ;
$$

4. `g_t` ne dépend d'aucune autre action que `A_t` ;
5. un maximiseur mesurable existe à chaque date, ou le supremum peut être approché arbitrairement.

Une politique admissible `\pi=(A_0,\ldots,A_{T-1})` choisit chaque action avec l'information de la date. Les rendements peuvent être corrélés dans le temps et `Z_t` peut contenir toute l'histoire utile : l'indépendance statistique des rendements n'est pas requise. La condition décisive est l'absence de lien **décisionnel** entre les dates.

Définissons la valeur conditionnelle immédiate :

$$
m_t(a,\mathcal F_t)
=\mathbb E[g_t(a,Z_t,R_{t+1})\mid\mathcal F_t].
$$

### 3.2 Proposition de séparation

Sous les hypothèses précédentes,

$$
\sup_{\pi}J(\pi)
=
\sum_{t=0}^{T-1}
\mathbb E\!\left[
\sup_{a\in\mathcal A_t(\mathcal F_t)}m_t(a,\mathcal F_t)
\right].
$$

Une politique optimale est obtenue en choisissant, à chaque date,

$$
A_t^*\in
\arg\max_{a\in\mathcal A_t(\mathcal F_t)}m_t(a,\mathcal F_t).
$$

**Démonstration.** Pour toute politique admissible,

$$
\begin{aligned}
J(\pi)
&=\sum_t\mathbb E[g_t(A_t,Z_t,R_{t+1})]\\
&=\sum_t\mathbb E[m_t(A_t,\mathcal F_t)]\\
&\leq \sum_t\mathbb E\!\left[
\sup_{a\in\mathcal A_t(\mathcal F_t)}m_t(a,\mathcal F_t)
\right].
\end{aligned}
$$

La première égalité utilise l'additivité, la deuxième l'espérance conditionnelle, et l'inégalité compare l'action effectivement choisie au meilleur choix conditionnel de la même date. Si chaque supremum possède un maximiseur mesurable `A_t^*`, la politique composée de ces maximisateurs atteint simultanément la borne. Il n'existe aucun arbitrage entre sacrifier une récompense aujourd'hui et améliorer les possibilités de demain : une équation de Bellman n'ajouterait rien à cette optimisation.

Des pondérations temporelles déterministes, par exemple `\sum_t \beta_t g_t`, ne détruisent pas la séparation. Elles se placent simplement dans chaque terme. En revanche, qualifier l'objectif d'« additif » ne suffit pas si une contrainte, un coût ou un état commun relie les actions.

### 3.3 Exemple d'une décision myope cohérente

Considérons une approximation rendement–risque à une période :

$$
m_t(a)=a\mu_t-\frac{\eta}{2}a^2\sigma_t^2,
\qquad a\in[\underline a,\overline a],
$$

où `\mu_t` et `\sigma_t^2` sont la moyenne et la variance conditionnelles estimées à `t`, et `\eta>0` traduit ici une préférence locale donnée. Le choix est

$$
A_t^*=\operatorname{proj}_{[\underline a,\overline a]}
\left(\frac{\mu_t}{\eta\sigma_t^2}\right).
$$

Le calcul peut être répété à chaque date sans planification intertemporelle si les hypothèses de séparation sont vraies. Il ne valide toutefois ni cette fonction d'objectif, ni `\eta`, ni les prévisions employées. Il montre seulement qu'un problème conditionnel peut être dynamique dans ses données sans être dynamique dans ses décisions.

Il révèle aussi une difficulté financière : si l'objectif ne contenait qu'une pénalité de volatilité, l'exposition nulle serait souvent la solution triviale. Une prévision de volatilité ne définit donc pas, à elle seule, la raison de prendre du risque.

### 3.4 Ce qui ne suffit pas à invalider la séparation

- **Plusieurs dates.** Une suite de problèmes à une période reste une suite de problèmes à une période.
- **Prévisions variables.** Une prévision mise à jour modifie `m_t`, pas nécessairement les choix futurs disponibles.
- **Persistance du marché.** Elle peut être résumée dans `\mathcal F_t` sans que l'action agisse sur le futur.
- **Une borne locale d'exposition.** Si `A_t\in[\underline a_t,\overline a_t]` indépendamment à chaque date, l'optimisation reste séparable.
- **Une position héritée purement descriptive.** Si la nouvelle position peut être réinitialisée gratuitement et si aucun gain, coût ou contrainte ne dépend de l'ancienne, `H_{t-1}` est sans conséquence décisionnelle.
- **Un horizon long.** Allonger `T` ne crée pas de couplage lorsque l'objectif et les ensembles admissibles restent séparables.

### 3.5 Richesse et utilité : deux nuances indispensables

Une dynamique de richesse peut empêcher la séparation, mais pas automatiquement. Si l'exposition est une fraction `a_t` de la richesse, sans coût ni contrainte, alors

$$
W_{t+1}=W_t(1+a_tR_{t+1}).
$$

Avec une utilité logarithmique terminale et une richesse toujours positive,

$$
\log W_T=\log W_0+
\sum_{t=0}^{T-1}\log(1+a_tR_{t+1}).
$$

Sous exogénéité du marché et sans autre couplage, cette transformation rend de nouveau le problème additif : la présence de `W_t` dans l'équation comptable ne suffit donc pas à prouver l'interdépendance.

À l'inverse, une utilité terminale générale

$$
\max_\pi\ \mathbb E[U(W_T)]
$$

ne se décompose normalement pas en une somme de choix locaux. L'action courante modifie la distribution de richesse à laquelle s'appliquera l'utilité future ; sa valeur dépend alors de la continuation. Il existe des cas particuliers — utilités homothétiques, rendements spécifiques, contraintes absentes — où une solution myope réapparaît. Ces cas doivent être démontrés, pas supposés.

## 4. Situation B — décisions interdépendantes

L'analyse suivante ajoute les mécanismes un par un. Son résultat principal est négatif autant que positif : certains ajouts créent un état pertinent, d'autres non.

### 4.1 Position héritée

Écrivons d'abord la transition interne :

$$
H_t=A_t.
$$

Si l'exposition peut être changée librement et si ni le gain ni les contraintes ne dépendent de `H_{t-1}`, cette transition est comptable mais sans valeur économique. Deux portefeuilles ayant le même marché observable mais des positions initiales différentes peuvent choisir gratuitement le même `A_t`; leur problème est identique.

La position héritée devient un véritable état seulement lorsqu'elle influence au moins un élément futur : coût de rotation, vitesse maximale d'ajustement, marge, liquidation terminale ou ensemble admissible. La présence d'une variable d'état dans un fichier ne suffit donc pas à rendre le problème séquentiel.

### 4.2 Coûts de transaction

Avec un coût `C_t(A_t-H_{t-1})`, le problème à minimiser peut prendre la forme

$$
\mathbb E\!\left[
\sum_{t=0}^{T-1}
\left\{\ell_t(A_t,Z_t,R_{t+1})
+C_t(A_t-H_{t-1})\right\}
\right].
$$

L'action `A_t` devient la position héritée de la date suivante. Elle détermine donc le coût du prochain changement, même si les rendements restent totalement exogènes.

Un exemple analytique minimal montre pourquoi l'optimum immédiat peut échouer. Prenons deux dates, `H_{-1}=0`, les actions `H_t\in\{0,1\}`, une exposition souhaitée égale à 1 et la perte

$$
L_t=(H_t-1)^2+\frac{3}{2}|H_t-H_{t-1}|.
$$

À une date isolée en partant de zéro, conserver `H_t=0` coûte `1`, alors que passer à `H_t=1` coûte `3/2`. Une règle myope ne négocie donc jamais et supporte une perte totale de `2`. Sur deux périodes, passer à `H_0=1` puis conserver cette position coûte seulement `3/2` au total. Le coût initial, défavorable immédiatement, est amorti par la seconde période. La décision optimale courante dépend de la durée future de détention.

La récursion correcte est ici

$$
V_t(z,h^-)=\min_{a\in\mathcal A_t(z,h^-)}
\mathbb E\!\left[
\ell_t(a,z,R_{t+1})+C_t(a-h^-)
+V_{t+1}(Z_{t+1},a)
\mid Z_t=z
\right].
$$

Les coûts peuvent produire de l'inertie ou une zone de non-transaction, phénomène classique en allocation avec coûts proportionnels ([Davis et Norman, 1990](https://doi.org/10.1287/moor.15.4.676)). Cela justifie une optimisation intertemporelle, pas nécessairement le RL : si la dynamique et les coûts sont connus et le problème traitable, le contrôle stochastique classique suffit.

### 4.3 Richesse

En mesurant `A_t` comme une exposition monétaire, une transition simplifiée est

$$
W_{t+1}=W_t+A_tR_{t+1}-C_t(A_t-H_{t-1}).
$$

La richesse devient décisionnellement pertinente si elle influence :

- l'utilité marginale d'un gain ou d'une perte ;
- les limites de levier ou de marge ;
- le montant risqué lors des décisions suivantes ;
- la possibilité de continuer après une perte ;
- un objectif terminal, de drawdown ou de solvabilité.

Avec une utilité terminale, la valeur prend la forme

$$
V_t(z,w,h^-)=\max_a
\mathbb E\!\left[
V_{t+1}\bigl(Z_{t+1},
w+aR_{t+1}-C_t(a-h^-),a\bigr)
\mid Z_t=z
\right],
$$

avec `V_T(z,w,h)=U(w)` éventuellement diminuée d'un coût de liquidation. Une action courante modifie alors la richesse sur laquelle seront prises toutes les décisions suivantes.

Mais la richesse ne doit pas être ajoutée mécaniquement à l'état. Si l'objectif est une somme de gains monétaires linéaires, si les expositions admissibles ne dépendent pas de `W_t` et si aucun critère terminal n'utilise la richesse, sa comptabilisation peut ne rien changer au choix. Le besoin de planifier vient de la manière dont la richesse modifie les valeurs ou possibilités futures, non de son seul nom.

### 4.4 Contraintes d'exposition et de risque

Les contraintes doivent être classées selon leur portée temporelle.

**Contrainte locale.** Une borne `A_t\in[\underline a,overline a]` ou une limite instantanée

$$
|A_t|\widehat\sigma_t\leq b
$$

reste compatible avec une optimisation période par période si `b` est remis à zéro chaque date et si la contrainte ne dépend pas du chemin. Elle peut modifier l'action sans créer d'état futur.

**Contrainte liée à la position.** Une limite de rotation

$$
|A_t-H_{t-1}|\leq\delta
$$

rend la position héritée déterminante : choisir `A_t` modifie directement les positions atteignables à `t+1`.

**Contrainte cumulée.** Un budget de transaction ou de risque

$$
\sum_{u=0}^{T-1}|A_u-H_{u-1}|\leq B_0
$$

nécessite un état résiduel

$$
B_{t+1}=B_t-|A_t-H_{t-1}|.
$$

Dépenser le budget maintenant réduit les choix ultérieurs.

**Contrainte dépendante du chemin.** Une limite de drawdown dépend du maximum passé de richesse ; une contrainte de marge dépend de la richesse et de l'exposition ; une obligation de liquidation impose une condition terminale. Ces quantités doivent être incluses dans l'état si l'on veut retrouver une représentation markovienne.

Une contrainte dure ne doit pas être remplacée sans justification par une pénalité arbitraire. Une pénalité autorise implicitement une violation lorsque le gain compensatoire est assez grand, ce qui peut contredire un mandat. Les MDP contraints séparent formellement objectif et contraintes ([Altman, 1999](https://www.routledge.com/Constrained-Markov-Decision-Processes/Altman/p/book/9780849303821)), mais aucun cadre de ce type n'est encore retenu ici.

### 4.5 Horizon et condition terminale

L'horizon agit lorsqu'il existe déjà une conséquence différée. Avec des coûts, une position est moins intéressante à ouvrir juste avant la fin parce qu'il reste peu de périodes pour amortir son coût et qu'une liquidation terminale peut être nécessaire. Avec un budget, l'utilité de le conserver dépend du temps restant. Le temps `t` ou la durée résiduelle doit alors appartenir à l'état d'un problème fini.

En revanche, un horizon de cent périodes ne crée aucune interdépendance si les cent termes et ensembles admissibles restent séparables comme dans la situation A. Le temps long augmente le nombre de décisions ; il ne change pas leur nature logique.

### 4.6 Mécanisme commun

Les ajouts précédents peuvent être résumés par un critère :

> Une décision est intertemporelle si l'action courante modifie une variable qui influence la valeur ou la faisabilité d'au moins une décision future.

Dans le cas étudié, cette variable est normalement **interne au portefeuille** : position, richesse, budget résiduel, maximum de richesse, marge ou temps avant liquidation. Le processus de marché peut rester exogène. L'impact de marché serait une autre source de transition contrôlée, mais il est exclu du présent cas.

## 5. Représentation comme problème de décision markovien

### 5.1 État minimal candidat

Une représentation illustrative, non validée, est

$$
S_t=(Z_t,H_{t-1},W_t,B_t,t).
$$

Chaque composante doit gagner sa place :

- `Z_t` résume l'information de marché utile à la loi conditionnelle des rendements et coûts ;
- `H_{t-1}` détermine le coût ou la faisabilité de l'ajustement ;
- `W_t` détermine l'utilité, le levier ou la marge si le mandat l'exige ;
- `B_t` résume une ressource ou contrainte cumulée ;
- `t` représente le temps restant et les conditions terminales.

Si une composante n'affecte ni transition, ni gain, ni contrainte, elle est superflue. Si une information passée pertinente manque, l'état est insuffisant.

### 5.2 Transition factorisée

Sous l'hypothèse de preneur de prix :

$$
(Z_{t+1},R_{t+1})\sim P_t(\cdot\mid Z_t),
$$

alors que les transitions internes sont contrôlées :

$$
\begin{aligned}
H_t &= A_t,\\
W_{t+1} &= W_t+A_tR_{t+1}-C_t(A_t-H_{t-1};Z_t),\\
B_{t+1} &= G_t(B_t,S_t,A_t,R_{t+1}).
\end{aligned}
$$

La loi de transition globale peut donc dépendre de l'action même si la composante de marché n'en dépend pas. Cette factorisation empêche une confusion importante : « le gestionnaire ne déplace pas le marché » ne signifie pas « son action est sans conséquence future ».

### 5.3 Objectif, valeur et Bellman

Sans fixer de récompense financière particulière, écrivons un objectif générique à horizon fini :

$$
J_t^\pi(s)=
\mathbb E^\pi\!\left[
\sum_{u=t}^{T-1}r_u(S_u,A_u,S_{u+1})
+U_T(S_T)\mid S_t=s
\right].
$$

La fonction de valeur optimale est

$$
V_t^*(s)=\sup_\pi J_t^\pi(s).
$$

Si l'état est markovien, les actions admissibles sont correctement définies et les espérances existent, le principe d'optimalité donne

$$
V_t^*(s)=
\sup_{a\in\mathcal A_t(s)}
\mathbb E\!\left[
r_t(s,a,S_{t+1})+V_{t+1}^*(S_{t+1})
\mid S_t=s,A_t=a
\right],
$$

avec `V_T^*(s)=U_T(s)`.

Le premier terme mesure la conséquence immédiate ; le second valorise l'état laissé à la prochaine date. Une politique myope supprime ce second terme ou suppose implicitement qu'il ne varie pas avec `a`.

Le principe de Bellman découle d'un argument simple. Si la continuation d'une politique prétendument optimale était sous-optimale après un état atteignable `s'`, on pourrait la remplacer par une meilleure continuation sans modifier les décisions antérieures. La politique initiale serait alors améliorée, contradiction. Cette logique exige que `s'` contienne tout ce qui est nécessaire pour comparer les continuations.

### 5.4 Quand la représentation MDP est-elle correcte ?

Il faut pouvoir défendre les conditions suivantes :

1. **suffisance de l'état** : conditionnellement à `(S_t,A_t)`, l'histoire ne change ni la loi de `S_{t+1}`, ni les gains et contraintes futurs ;
2. **chronologie exacte** : seules les informations disponibles avant l'action figurent dans `S_t` ;
3. **action exécutable** : `A_t` correspond à une décision réellement possible, avec prix et délai cohérents ;
4. **transition de portefeuille complète** : position, coûts, richesse et contraintes sont mis à jour sans contradiction comptable ;
5. **objectif cohérent** : les récompenses et la valeur terminale représentent le mandat, sans double comptage ;
6. **temps traité correctement** : si les lois ou objectifs dépendent de la date, le temps appartient à l'état ou les transitions sont explicitement non stationnaires.

Déclarer `Z_t=(HV5,HV20,HV60)` ne démontrerait pas la propriété de Markov. Ces variables pourraient être des observations utiles sans résumer toute l'information pertinente.

### 5.5 Observabilité partielle

L'état économique véritable — liquidité latente, anticipations, contraintes d'autres acteurs ou mécanisme générateur des rendements — n'est pas nécessairement observable. Si un état latent `X_t` produit une observation `O_t`, la décision dépend en théorie de la croyance

$$
b_t(x)=\mathbb P(X_t=x\mid O_{0:t},A_{0:t-1}).
$$

Cette croyance peut servir d'état dans un POMDP, à condition de connaître ou d'estimer les lois de transition et d'observation. Une histoire de rendements ou un état récurrent appris n'est pas automatiquement une croyance bien calibrée. L'observabilité partielle augmente l'incertitude de spécification ; elle ne justifie pas à elle seule un algorithme complexe. Le cadre formel est notamment exposé par [Kaelbling, Littman et Cassandra (1998)](https://www.cassandra.org/arc/papers/aij98.pdf).

### 5.6 Dynamique inconnue

Lorsque `P_t` et les conséquences financières sont connues, la programmation dynamique ou le contrôle optimal cherchent directement la politique. Lorsqu'elles sont inconnues, plusieurs options précèdent le RL : estimer un modèle simple puis contrôler, utiliser une règle robuste, ou réduire le problème si les effets différés sont négligeables.

Le RL devient un candidat lorsque la politique ou la valeur doit être apprise à partir de données ou d'interactions **et** que l'effet séquentiel est matériel. Dans un cadre historique hors ligne, une politique peut choisir des actions peu soutenues par les données et recevoir une valeur extrapolée. Cette difficulté est centrale en offline RL ([Levine et al., 2020](https://arxiv.org/abs/2005.01643)).

Le cas d'un preneur de prix possède une nuance favorable : si les rendements sont exogènes et les coûts entièrement connus, certaines conséquences de plusieurs expositions hypothétiques peuvent être recalculées sur la même trajectoire. Mais cette commodité ne crée pas de nouvelles trajectoires de marché, ne résout pas la non-stationnarité et ne rend pas honnête une politique choisie après consultation répétée des mêmes périodes.

## 6. Comparaison des cadres de décision

| Cadre | Question résolue | Information nécessaire | Hypothèse déterminante | Atout | Limite dans notre cas |
|---|---|---|---|---|---|
| Règle fixe | appliquer une relation décidée à l'avance | variables de la règle | relation stable et défendable | transparente, auditable | ne valorise pas explicitement les conséquences futures |
| Optimisation période par période | maximiser le critère conditionnel immédiat | distribution ou prévision à un pas, contraintes locales | séparation démontrée ou effets futurs négligeables | solution minimale et interprétable | incorrecte si l'action modifie coûts ou faisabilité futurs |
| Ciblage de volatilité classique | ajuster l'exposition pour viser un budget de volatilité | prévision de volatilité, borne et cible | volatilité prévue pertinente pour le budget | référence financière naturelle et simple | ignore rendement espéré, erreur de prévision et coûts futurs sauf modification explicite |
| Programmation dynamique / contrôle optimal | optimiser une suite d'actions couplées | état, transitions, coûts, contraintes et horizon modélisés | modèle suffisamment crédible et problème calculable | traite directement les effets différés | sensible à la mauvaise spécification ; dimension potentiellement élevée |
| Contextual bandit | apprendre la meilleure action immédiate conditionnelle au contexte | contexte, actions et récompenses immédiates | pas de conséquence différée pertinente | apprend sans construire un MDP artificiel | inadéquat si position, richesse ou budget transmettent l'effet de l'action |
| Reinforcement Learning | apprendre une politique ou des valeurs séquentielles | trajectoires avec états, actions et conséquences, ou environnement crédible | effet différé réel, support de données et évaluation possibles | peut apprendre lorsque la dynamique complète n'est pas connue | surajustement, extrapolation, instabilité et évaluation contrefactuelle difficiles |

### 6.1 Règles fixes et ciblage de volatilité

Une règle classique peut être

$$
A_t=\min\!\left(\overline a,
\frac{\sigma^{\text{cible}}}{\widehat\sigma_t}\right).
$$

Elle vise approximativement `|A_t|\widehat\sigma_t=\sigma^{\text{cible}}`, sous une convention d'échelle. Elle est une règle de **budget d'amplitude prévue**, pas une politique optimale universelle. Elle ne devient une solution économique qu'après justification de la cible, du levier, du rendement attendu, des coûts et de la réaction aux erreurs de prévision. La littérature sur les portefeuilles gérés par la volatilité fournit une référence empirique à examiner avant une méthode apprenante ([Moreira et Muir, 2017](https://doi.org/10.1111/jofi.12513)).

### 6.2 Contextual bandit ou optimisation supervisée

Si l'action n'affecte que le résultat courant et si la relation contexte–gain est inconnue, un contextual bandit peut apprendre quel choix immédiat fonctionne selon `Z_t` ; voir [Lattimore et Szepesvári (2020)](https://doi.org/10.1017/9781108571401). Si le rendement réalisé permet de calculer après coup le gain de **toutes** les expositions admissibles, le retour est même proche d'une information complète : une estimation supervisée suivie d'une optimisation peut être plus simple qu'un bandit.

Un bandit n'est pas une approximation convenable d'un vrai problème de rotation si le choix actuel devient la position héritée et modifie le coût de demain.

### 6.3 Contrôle classique ou RL

Le besoin d'une équation de Bellman établit un besoin de **contrôle séquentiel**, pas un besoin de RL. Le contrôle classique suffit lorsque transitions, coûts et contraintes peuvent être spécifiés avec une crédibilité acceptable et résolus à la dimension considérée. Le RL ne devient scientifiquement pertinent que si l'apprentissage à partir des données répond à une difficulté réelle du modèle et peut être évalué sans masquer davantage d'incertitude qu'il n'en résout.

## 7. Six objets distincts sous le mot « risque »

### 7.1 Incertitude sur les rendements

`R_{t+1}` est inconnu à `t`. Sa distribution conditionnelle comprend direction, dispersion, asymétrie et queues. Même une variance conditionnelle parfaitement connue ne donne pas le rendement réalisé.

### 7.2 Erreur de prévision de volatilité

L'écart entre `\widehat\sigma_t` et une mesure future comme `RV5_t` mélange erreur de modèle et bruit de mesure. Dans le projet principal, `RV5` repose sur cinq rendements, se chevauche d'une date à l'autre et ignore leur signe. Une sous-estimation de `RV5` ne signifie pas automatiquement une perte de portefeuille.

### 7.3 Incertitude sur les transitions

La loi `P_t` reliant le contexte courant aux états futurs peut être inconnue ou changer. Cette incertitude de modèle est différente de l'aléa d'un rendement conditionnellement à un modèle donné. Une politique très précise dans un modèle faux peut être fragile ; la programmation dynamique robuste formalise une réponse possible sans être adoptée ici ([Iyengar, 2005](https://doi.org/10.1287/moor.1040.0129)).

### 7.4 Risque de perte financière

Une perte dépend du signe de l'exposition, du rendement, des coûts et parfois du chemin de richesse :

$$
\Delta W_{t+1}=A_tR_{t+1}-C_t(A_t-H_{t-1}).
$$

Une forte volatilité peut correspondre à un gain important pour une exposition correctement orientée. À l'inverse, des coûts répétés peuvent causer une perte dans un marché peu volatil.

### 7.5 Contrainte de gestion du risque

Une contrainte définit ce qui est autorisé : levier maximal, perte tolérable, marge, drawdown ou budget de rotation. Elle n'est ni une prévision ni une préférence. Sa violation peut être juridiquement ou institutionnellement inadmissible, raison pour laquelle une pénalité souple ne lui est pas automatiquement équivalente.

### 7.6 Incertitude sur la politique

Une politique estimée varie avec l'échantillon, les hypothèses, les hyperparamètres et les changements de distribution. Cette incertitude porte sur la règle de décision elle-même. Elle doit être distinguée de l'incertitude du rendement qu'elle affronte et ne disparaît pas lorsque la valeur historique estimée est élevée.

### 7.7 Pourquoi la volatilité n'est pas automatiquement une récompense

Minimiser directement la volatilité favorise trivialement l'absence d'exposition. Maximiser le rendement moins un multiple arbitraire de la variance transforme une décision économique non résolue en coefficient technique. Cibler `RV5` récompenserait la prévision d'une amplitude future, pas nécessairement la protection contre une perte, le respect d'un mandat ou la création de valeur nette de coûts.

La volatilité peut jouer plusieurs rôles légitimes mais distincts : information d'état, prévision utilisée par une contrainte, composante d'un budget de risque ou diagnostic ex post. Le projet doit choisir un objectif économique — par exemple utilité terminale, suivi d'un budget avec coûts, ou rendement sous contrainte explicite — avant de définir une récompense. Aucun de ces choix n'est validé dans cette étude.

## 8. Test de pertinence et critères de renoncement au RL

### 8.1 Questions cumulatives avant d'envisager le RL

1. **Décision réelle :** l'action, son moment d'exécution et l'instrument sont-ils définis ?
2. **Conséquence différée :** l'action change-t-elle matériellement position, coûts futurs, richesse, budget ou faisabilité ?
3. **Échec du modèle myope :** cette conséquence ne peut-elle pas être négligée ou intégrée dans une règle simple sans perte économique importante ?
4. **Référence classique :** un contrôle connu ou une programmation dynamique simple est-il insuffisant pour une raison identifiée ?
5. **Besoin d'apprentissage :** quelle partie inconnue doit être apprise plutôt que spécifiée ou estimée séparément ?
6. **État observable :** les variables nécessaires sont-elles disponibles à la date de décision, sans fuite ?
7. **Support des actions :** les données contiennent-elles assez d'information sur les conséquences des actions envisagées ?
8. **Évaluation honnête :** existe-t-il un protocole non consulté ou une méthode contrefactuelle crédible pour comparer les politiques nettes de coûts ?
9. **Gain matériel :** le bénéfice attendu dépasse-t-il l'incertitude d'estimation, la complexité et les risques opérationnels ?

Le RL n'est candidat que si les réponses positives forment une chaîne cohérente. Une seule réponse manquante peut déplacer la question vers la collecte d'information, le contrôle classique ou l'abandon.

### 8.2 Conditions explicites de renoncement

Il faudrait renoncer au RL pour ce cas si :

- la situation A décrit suffisamment le mandat ;
- les coûts et contraintes sont négligeables aux fréquences réalistes ;
- une règle fixe ou un contrôleur classique traite les effets différés ;
- l'état nécessaire n'est pas observable avec une chronologie défendable ;
- les trajectoires historiques ne soutiennent pas les actions de la politique ;
- aucune période ou procédure d'évaluation crédible ne peut être préservée ;
- les résultats dépendent d'une récompense ou d'un coefficient de risque sans justification économique ;
- la politique complexe n'améliore pas matériellement une référence simple après coûts et sous contraintes.

Un tel renoncement serait un résultat scientifique utile : il identifierait la structure du problème plutôt qu'un échec à employer une technique.

## 9. Difficultés encore ouvertes

Cette étude ne tranche pas les points suivants :

- quel instrument négociable représente l'exposition et à quel prix l'action est exécutée ;
- quelle fréquence de décision correspond au mandat et aux coûts réels ;
- quel objectif économique distingue une bonne décision d'une simple réduction de volatilité ;
- quelles contraintes sont dures, locales ou cumulatives ;
- si la position est mesurée en unités, en exposition monétaire ou en fraction de richesse ;
- quelle forme et quel millésime de coûts seraient défendables ;
- quel résumé `Z_t` est suffisamment informatif, et si un état markovien observable existe ;
- quelle importance quantitative ont réellement les conséquences intertemporelles ;
- quelle partie de la dynamique serait inconnue au point de justifier un apprentissage de politique ;
- comment préserver une évaluation non consultée, compte tenu des périodes déjà explorées par le projet principal.

Les erreurs communes observées dans les notebooks 05 et 06 et l'échec des alertes du notebook 07 ne répondent à aucune de ces questions. Ils montrent seulement qu'une décision future ne peut pas être justifiée par la précision moyenne d'une prévision de volatilité.

## 10. Décisions nécessaires avant toute première expérience

Les choix suivants relèvent du porteur du projet et ne sont pas pris ici :

1. **Utilisateur et mandat :** confirmer le gestionnaire doté d'un budget de risque et préciser ce que ce budget protège.
2. **Instrument et action :** définir l'exposition négociable, ses unités, ses bornes et sa chronologie d'exécution.
3. **Objectif économique :** choisir entre utilité, objectif de rendement sous contraintes, suivi d'un budget ou autre formulation défendable ; décider du rôle exact de la volatilité.
4. **Source de séquentialité :** déterminer quels mécanismes sont réellement inclus — coûts, richesse, rotation, marge, contrainte cumulée ou liquidation — plutôt que les ajouter tous.
5. **Horizon et fréquence :** fixer la durée économique sur laquelle les conséquences doivent être valorisées.
6. **Références minimales :** choisir la règle fixe, le ciblage de volatilité et, si nécessaire, le contrôle classique auxquels toute méthode apprise devrait être comparée.
7. **Observabilité et données :** vérifier que les états, coûts et contraintes seraient disponibles à chaque date et qu'une évaluation honnête resterait possible.

La décision la plus immédiate n'est donc pas « quel algorithme RL ? », mais « quel mécanisme intertemporel représente réellement le mandat du gestionnaire ? ».

## 11. Conclusion : établi, conditionnel et non démontré

### 11.1 Ce que l'étude établit mathématiquement

- Un problème multi-périodes se sépare en optimisations conditionnelles indépendantes lorsque l'objectif est additif, que chaque action n'apparaît que dans son terme courant, que les ensembles admissibles ne sont pas couplés et que l'action ne modifie ni la loi, ni l'information, ni les possibilités futures.
- Une position héritée, une richesse comptable ou un horizon long ne créent pas automatiquement une interdépendance.
- Le problème devient réellement intertemporel lorsqu'une action modifie une variable qui détermine la valeur ou la faisabilité des décisions futures.
- Les coûts de transaction, la richesse avec utilité ou contraintes dépendantes, les limites de rotation, les budgets cumulatifs et les conditions terminales sont des mécanismes possibles ; leur simple mention ne prouve pas leur importance quantitative.
- Dans le cas d'un preneur de prix, le marché peut rester exogène tandis que l'état du portefeuille est contrôlé et justifie une équation de Bellman.
- Le besoin de Bellman établit au plus la nécessité d'un contrôle séquentiel. Il ne démontre pas la nécessité du RL.

### 11.2 Ce qui reste conditionnel

Une règle fixe ou une optimisation myope suffit si les conditions de séparation sont acceptables ou si les conséquences différées sont économiquement négligeables. Un contextual bandit peut suffire lorsque seule la meilleure récompense immédiate conditionnelle doit être apprise. La programmation dynamique ou le contrôle optimal suffit si la dynamique séquentielle peut être spécifiée et résolue. Le RL ne pourrait se justifier qu'en présence simultanée d'une interdépendance matérielle, d'une dynamique insuffisamment connue, de données adéquates et d'une évaluation crédible.

### 11.3 Ce qui n'est pas démontré

Cette étude ne démontre pas que la gestion d'exposition retenue est le meilleur objet empirique, que les données actuelles permettent de construire son état, que les coûts rendent la décision matériellement séquentielle, qu'une récompense particulière est défendable, ni qu'une politique RL améliorerait une décision financière. Elle ne transforme pas `RV5` en mesure de perte et ne tire aucune conclusion causale des épisodes historiques.

## 12. Références mobilisées

Les références ci-dessous ont déjà été identifiées et leur statut d'accès documenté dans le [cadrage scientifique RL](CADRAGE_SCIENTIFIQUE.md). Les ouvrages ne sont pas présentés comme intégralement consultés lorsque seuls leurs éléments bibliographiques accessibles ont été vérifiés.

- Sutton, R. S. et Barto, A. G. (2018), *Reinforcement Learning: An Introduction*, 2e éd. [Version des auteurs](http://incompleteideas.net/book/RLbook2020.pdf).
- Puterman, M. L. (1994), *Markov Decision Processes: Discrete Stochastic Dynamic Programming*. [DOI](https://doi.org/10.1002/9780470316887).
- Kaelbling, L. P., Littman, M. L. et Cassandra, A. R. (1998), « Planning and Acting in Partially Observable Stochastic Domains ». [Article](https://www.cassandra.org/arc/papers/aij98.pdf).
- Altman, E. (1999), *Constrained Markov Decision Processes*. [Éditeur](https://www.routledge.com/Constrained-Markov-Decision-Processes/Altman/p/book/9780849303821).
- Lattimore, T. et Szepesvári, C. (2020), *Bandit Algorithms*. [Édition en accès libre](https://tor-lattimore.com/downloads/book/book.pdf).
- Levine, S., Kumar, A., Tucker, G. et Fu, J. (2020), « Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems ». [arXiv](https://arxiv.org/abs/2005.01643).
- Davis, M. H. A. et Norman, A. R. (1990), « Portfolio Selection with Transaction Costs ». [DOI](https://doi.org/10.1287/moor.15.4.676).
- Moreira, A. et Muir, T. (2017), « Volatility-Managed Portfolios ». [DOI](https://doi.org/10.1111/jofi.12513).
- Iyengar, G. N. (2005), « Robust Dynamic Programming ». [DOI](https://doi.org/10.1287/moor.1040.0129).
