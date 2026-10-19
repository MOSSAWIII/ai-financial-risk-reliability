# Formalisation d'un mandat de gestion dynamique du risque financier

**Date : 19 octobre 2026**

**Statut : proposition scientifique à discuter ; aucun instrument, paramètre, jeu de données ou protocole empirique n'est validé**

## 1. Question financière et statut des propositions

La question de cette étude est :

> Comment un gestionnaire peut-il ajuster dans le temps une exposition au marché actions afin de rechercher une croissance du capital tout en respectant un budget de risque et en supportant les coûts réels de ses rééquilibrages ?

Cette question prolonge les deux documents précédents sans les modifier. Le [cadrage scientifique](CADRAGE_SCIENTIFIQUE.md) établit que le RL ne doit être envisagé qu'après définition d'une décision financière. L'étude du [problème de décision séquentielle](PROBLEME_DECISION_SEQUENTIELLE.md) démontre qu'une suite de décisions ne devient intertemporelle que si une action présente modifie la valeur ou la faisabilité des décisions futures.

Les résultats du projet principal motivent la prudence : `RV5` est une mesure d'amplitude future, bruitée, chevauchante et insensible au signe ; plusieurs prévisions sous-estiment parfois cette amplitude ensemble ; les deux alertes simples du notebook 07 ne reconnaissent pas convenablement les débuts des épisodes étudiés. Ces constats ne définissent cependant ni une perte de portefeuille, ni un mandat, ni la valeur économique d'une action.

Le document distingue explicitement :

- **établi** : identité comptable ou conséquence mathématique des hypothèses ;
- **hypothèse de travail recommandée** : formulation minimale proposée pour une discussion future ;
- **choix ouvert** : décision qui nécessite l'approbation du porteur du projet ;
- **hors périmètre initial** : élément plausible mais non nécessaire au premier cas d'étude.

Aucune formulation ci-dessous ne constitue encore une autorisation d'expérience.

## 2. Le décideur et le mandat économique

### 2.1 Profil stylisé du décideur

Le décideur proposé est le gestionnaire d'une **poche actions à risque contrôlé** appartenant à un investisseur final. Il n'est assimilé à aucun fonds, assureur ou régime réglementaire réel. Le cas stylisé évite de revendiquer des contraintes institutionnelles que nous n'avons pas documentées.

L'investisseur final souhaite participer à la croissance de long terme du marché actions sans accepter une exposition constante lorsque le risque prévu devient incompatible avec son budget. Le gestionnaire choisit périodiquement la fraction du portefeuille placée dans un instrument actions investissable ; le solde reste dans une composante monétaire ou sans risque.

Les intérêts économiques doivent être alignés :

- l'investisseur s'intéresse à la richesse nette, aux pertes, au drawdown et au respect du mandat ;
- le gestionnaire ne doit pas être récompensé pour une simple baisse de volatilité obtenue en restant toujours en espèces ;
- ni le nombre de transactions, ni la sophistication de la politique ne constituent un objectif ;
- toute performance doit être mesurée après les coûts effectivement modélisés.

### 2.2 Trois formulations plausibles

| Formulation | Objectif principal | Atout | Difficulté ou solution triviale |
|---|---|---|---|
| Préservation absolue du capital | minimiser pertes ou drawdown | priorité financière claire | sans exigence de participation, l'exposition nulle domine souvent |
| Ciblage pur de volatilité | maintenir le risque prévu près d'un budget | règle transparente, liée aux travaux existants | ne dit pas pourquoi prendre du risque et peut négocier excessivement |
| Croissance sous budget de risque | faire croître la richesse nette sous une limite explicite de risque | sépare objectif économique et contrainte | nécessite de définir horizon, mesure du risque et information prévisionnelle |

Une quatrième formulation, « maximiser rendement moins une pénalité de risque », est courante mais prématurée ici : le coefficient de pénalité fixerait silencieusement le compromis économique que nous cherchons précisément à comprendre.

### 2.3 Mandat initial recommandé, non validé

La formulation la plus simple et défendable à approfondir est :

> Rechercher la croissance composée de la richesse nette de coûts sur un horizon fini, en détenant uniquement un instrument actions long-only et une composante monétaire, sous une borne d'exposition et un budget de volatilité défini avant la décision.

Une écriture candidate est

$$
\max_{\pi}\quad
\mathbb E^{\pi}\!\left[
\log\left(\frac{W_T^-}{W_0^-}\right)
\right],
$$

sous les contraintes locales

$$
0\leq w_t^+\leq 1,
\qquad
\widehat\sigma_{p,t}(w_t^+)\leq \bar\sigma,
\qquad
W_t^+>0.
$$

Les symboles `-` et `+` désignent respectivement les situations avant et après le rééquilibrage de la date `t`. La richesse terminale incorpore les coûts par la comptabilité ; ceux-ci ne sont pas soustraits une seconde fois dans l'objectif.

Cette recommandation a cinq raisons :

1. la croissance du capital reste l'objectif, ce qui évite la solution « tout en espèces » créée par la seule minimisation du risque ;
2. le logarithme représente la croissance composée et rend comparables des richesses initiales différentes ;
3. le budget de risque est une contrainte distincte, non une pénalité de poids arbitraire ;
4. l'interdiction initiale du levier et de la vente à découvert écarte provisoirement marge, emprunt et risque de richesse négative ;
5. les coûts sont des sorties monétaires réelles, pas une préférence abstraite.

Cette formulation reste un **choix ouvert**. L'utilité logarithmique traduit une préférence particulière ; elle n'est pas neutre. La valeur de `\bar\sigma`, la fréquence des décisions, l'horizon `T` et la mesure `\widehat\sigma_{p,t}` doivent être validés. Une autre utilité ou un objectif de rendement sous contrainte pourrait être préférable si le mandat économique le justifie.

### 2.4 Signification du budget de risque

Dans ce cas minimal, le budget de risque désigne une limite **ex ante** sur la volatilité prévue du portefeuille pendant le prochain intervalle de décision. Si le rendement monétaire est tenu pour connu sur cet intervalle et si l'instrument actions possède une volatilité prévue `\widehat\sigma_{e,t}`, alors

$$
\widehat\sigma_{p,t}(w)=|w|\widehat\sigma_{e,t}.
$$

La contrainte devient `|w|\widehat\sigma_{e,t}\leq\bar\sigma`. Elle limite l'exposition sur la base de l'information disponible à `t`; elle ne garantit pas que la volatilité ou la perte réalisée restera sous `\bar\sigma`. Une erreur de prévision peut provoquer un dépassement réalisé sans que le gestionnaire ait violé la règle ex ante.

Le budget n'est donc ni une garantie de capital, ni une limite certaine de perte, ni une définition complète du risque. Son rôle exact devra être confirmé par l'utilisateur du mandat.

### 2.5 Horizon

Le mandat doit posséder :

- un **intervalle de décision** entre deux rééquilibrages possibles ;
- un **horizon d'évaluation** `T` comprenant plusieurs intervalles ;
- éventuellement un horizon économique plus long que la période d'évaluation statistique.

Aucune valeur calendaire n'est fixée ici. Un choix quotidien, hebdomadaire ou mensuel change les coûts, la qualité de la prévision, la vitesse de réaction et le nombre d'observations. Le choisir avant d'avoir défini l'instrument, les horaires d'exécution et les coûts serait prématuré.

## 3. Instruments, unités et action financière

### 3.1 Deux composantes seulement

Le premier univers envisagé contient :

1. un instrument négociable donnant une exposition diversifiée au marché actions ;
2. une composante monétaire investissable dont le rendement correspond au placement effectivement accessible.

Aucun ETF, indice, fonds ou fournisseur n'est sélectionné. L'univers contient un seul actif risqué : il ne constitue pas une allocation multi-actifs.

### 3.2 Indice de marché et instrument négociable

Un indice est une règle de mesure. Son rendement peut supposer le réinvestissement des dividendes et ignorer frais, fiscalité, écart acheteur-vendeur, impact ou délai d'exécution. Il ne possède pas nécessairement un prix auquel le gestionnaire peut réellement traiter.

Un instrument investissable possède au contraire :

- un prix et un calendrier de cotation ;
- des unités négociables ;
- des dividendes ou distributions ;
- des frais et un éventuel écart de suivi par rapport à l'indice ;
- un bid–ask spread, une liquidité et des règles d'exécution.

Le rendement `Mkt-RF + RF` utilisé dans le projet principal représente un portefeuille de recherche agrégé. Il ne peut pas être traité silencieusement comme le rendement net d'un instrument exécutable. Il pourra servir de référence historique ou de source d'hypothèses, mais une étude de décision exigera des données correspondant à un actif effectivement négociable.

### 3.3 Unités, valeurs et poids

À l'instant précédant le rééquilibrage `t`, notons :

- `N_t^-` : nombre d'unités risquées détenues ;
- `P_t^{\mathrm{exec}}` : prix unitaire auquel l'ordre peut être exécuté ;
- `X_t^-=N_t^-P_t^{\mathrm{exec}}` : valeur risquée avant transaction ;
- `M_t^-` : valeur de la composante monétaire ;
- `W_t^-=X_t^-+M_t^-` : richesse totale avant transaction.

Le poids risqué hérité est

$$
w_t^-=\frac{X_t^-}{W_t^-}.
$$

L'action financière fondamentale peut être décrite comme une variation d'unités `\Delta N_t`. Sa valeur signée au prix d'exécution est

$$
Q_t=P_t^{\mathrm{exec}}\Delta N_t,
$$

où `Q_t>0` est un achat et `Q_t<0` une vente. Cette action est plus primitive qu'un poids cible : elle permet d'écrire exactement les flux monétaires. Un système opérationnel peut afficher un poids cible, mais doit le convertir en ordre compatible avec les coûts et les unités négociables.

### 3.4 Contraintes d'action candidates

Dans la formulation minimale :

$$
0\leq X_t^+\leq W_t^+,
\qquad
M_t^+\geq 0.
$$

Il n'y a ni position courte, ni emprunt, ni levier. Des tailles minimales d'ordre, fractions d'unités, plafonds de volume ou délais pourraient être opérationnellement importants, mais restent hors du cas initial jusqu'au choix d'un instrument.

## 4. Comptabilité exacte d'un rééquilibrage

### 4.1 Richesse initiale

À `t=0`, l'état comptable vérifie

$$
W_0^-=X_0^-+M_0^->0.
$$

L'allocation initiale doit être traitée explicitement : si construire `X_0^+` nécessite une transaction, son coût doit être inclus. Initialiser gratuitement le portefeuille directement au poids désiré favoriserait artificiellement les politiques qui exigent une position initiale importante.

### 4.2 Coût et positions après transaction

Soit `K_t(Q_t)\geq0` le coût monétaire total de l'ordre. Après exécution :

$$
\begin{aligned}
X_t^+ &= X_t^-+Q_t,\\
M_t^+ &= M_t^- - Q_t-K_t(Q_t),\\
W_t^+ &= X_t^++M_t^+
       = W_t^- - K_t(Q_t).
\end{aligned}
$$

Ces identités montrent que l'achat de l'actif risqué transfère `Q_t` depuis la poche monétaire, tandis que le coût détruit de la richesse. Le coût n'est pas simultanément retranché du rendement futur : il est déjà payé dans `W_t^+`.

Une première représentation possible est un coût proportionnel :

$$
K_t(Q_t)=\kappa_t|Q_t|,
$$

où `\kappa_t` est un coût par unité de montant risqué traité. Cette écriture peut représenter commissions et une approximation du spread ou du slippage. Il faudra éviter de compter le spread une première fois dans un prix d'exécution défavorable puis une seconde fois dans `\kappa_t`.

La proportionnalité, la symétrie achat–vente et l'absence d'impact de marché sont des hypothèses de travail, non des faits établis.

### 4.3 Poids après transaction

Le poids risqué réellement obtenu est

$$
w_t^+=\frac{X_t^+}{W_t^+}
=\frac{X_t^-+Q_t}{W_t^- - K_t(Q_t)}.
$$

Le dénominateur est la richesse **après coût**. Écrire simplement `Q_t=(w_t^+-w_t^-)W_t^-` serait inexact dès que le coût est positif.

Pour un coût proportionnel, posons `q_t=Q_t/W_t^-` et `x_t=w_t^-`. Si l'action est exprimée comme un poids cible `a_t=w_t^+`, l'ordre exact satisfait

$$
a_t=\frac{x_t+q_t}{1-\kappa_t|q_t|}.
$$

On obtient, sous les conditions de faisabilité :

$$
q_t=
\begin{cases}
\dfrac{a_t-x_t}{1+\kappa_t a_t}, & a_t\geq x_t \quad\text{(achat)},\\[8pt]
\dfrac{a_t-x_t}{1-\kappa_t a_t}, & a_t<x_t \quad\text{(vente)}.
\end{cases}
$$

Lorsque `\kappa_t=0`, la relation habituelle `q_t=a_t-x_t` réapparaît. Cette conversion exacte permet de choisir l'exposition en poids sans perdre la cohérence des flux.

### 4.4 Turnover

Nous définissons le turnover sur le seul montant risqué négocié par

$$
\tau_t=\frac{|Q_t|}{W_t^-}=|q_t|.
$$

Sous coût proportionnel,

$$
\frac{K_t(Q_t)}{W_t^-}=\kappa_t\tau_t.
$$

D'autres conventions additionnent achats et ventes ou divisent par une richesse moyenne. Elles peuvent produire des chiffres différents pour la même transaction. La convention devra donc être conservée explicitement dans toute comparaison.

### 4.5 Rendements et richesse suivante

Après le rééquilibrage, les deux composantes produisent des rendements bruts `G_{t+1}^e=1+R_{t+1}^e` et `G_{t+1}^f=1+R_{t+1}^f` :

$$
\begin{aligned}
X_{t+1}^- &= X_t^+G_{t+1}^e,\\
M_{t+1}^- &= M_t^+G_{t+1}^f,\\
W_{t+1}^- &= X_t^+G_{t+1}^e+M_t^+G_{t+1}^f\\
&=W_t^+\left[
w_t^+G_{t+1}^e+(1-w_t^+)G_{t+1}^f
\right].
\end{aligned}
$$

`G_{t+1}^e` doit être un rendement de détention cohérent incluant les distributions selon une convention explicite. Si celles-ci sont versées dans la poche monétaire plutôt que réinvesties dans la poche risquée, les deux lignes de position doivent être adaptées sans modifier leur somme totale.

Par rapport à la richesse antérieure au coût :

$$
\frac{W_{t+1}^-}{W_t^-}
=
\left(1-\frac{K_t(Q_t)}{W_t^-}\right)
\left[
w_t^+G_{t+1}^e+(1-w_t^+)G_{t+1}^f
\right].
$$

Cette identité sépare la destruction immédiate de richesse par le coût et le rendement de la position effectivement détenue ensuite.

### 4.6 Poids hérité à la date suivante

Avant toute nouvelle transaction,

$$
w_{t+1}^-
=
\frac{w_t^+G_{t+1}^e}
{w_t^+G_{t+1}^e+(1-w_t^+)G_{t+1}^f}.
$$

En général, `w_{t+1}^-\neq w_t^+`. Une surperformance de l'instrument actions augmente mécaniquement son poids ; une sous-performance le réduit. Ainsi :

- le **poids choisi** `w_t^+` est l'allocation juste après l'ordre ;
- le **poids hérité** `w_{t+1}^-` est l'allocation obtenue après les rendements, avant l'ordre suivant ;
- le prochain turnover dépend de leur différence.

Confondre ces deux poids effacerait précisément l'état interne qui transmet les conséquences d'une décision au futur.

### 4.7 Pertes et drawdown

Le rendement net de portefeuille sur l'intervalle est

$$
R_{t+1}^{p,\mathrm{net}}
=\frac{W_{t+1}^-}{W_t^-}-1.
$$

Une perte financière correspond par exemple à `R_{t+1}^{p,\mathrm{net}}<0`, pas à une volatilité élevée en soi.

Le maximum historique de richesse et le drawdown sont

$$
\overline W_t=\max_{0\leq u\leq t}W_u^- ,
\qquad
D_t=1-\frac{W_t^-}{\overline W_t}.
$$

Le drawdown est dépendant du chemin. Dans le mandat initial recommandé, il serait un **indicateur d'évaluation**, pas encore une contrainte. En faire une contrainte dynamique obligerait à ajouter `\overline W_t` à l'état et à préciser si la limite doit être certaine, probabiliste ou moyenne.

## 5. Chronologie de l'information et de l'exécution

Une période doit respecter l'ordre suivant :

1. **Observation :** le gestionnaire connaît `W_t^-`, `X_t^-`, `M_t^-`, les données de marché publiées et disponibles avant une heure limite, ainsi que les paramètres du mandat.
2. **Décision :** il choisit un ordre `Q_t` ou un poids cible converti en ordre.
3. **Exécution :** l'ordre est exécuté à un prix et selon une convention définis ; `K_t` est payé ; `w_t^+` devient connu.
4. **Détention :** les rendements postérieurs à l'exécution se réalisent.
5. **Valorisation :** `W_{t+1}^-` et `w_{t+1}^-` sont calculés avant la décision suivante.

Le prix utilisé dans l'information ne peut pas être simultanément un prix d'exécution disponible avant que l'information ne soit connue. Par exemple, employer toutes les données de clôture de `t` puis prétendre traiter à cette même clôture crée une hypothèse d'exécution potentiellement irréaliste. Une future étude devra choisir entre des conventions telles que « signal avant clôture, exécution à la clôture » ou « signal après clôture, exécution au prix suivant », puis aligner exactement les rendements détenus.

Le délai d'ordre, le fuseau, les jours non négociés, les distributions et les ajustements de prix doivent être traités comme des éléments de la chronologie, non comme de simples détails de nettoyage.

## 6. Objectifs, contraintes, coûts et indicateurs

### 6.1 Classification nécessaire

| Élément | Rôle possible | Erreur à éviter |
|---|---|---|
| Croissance terminale | objectif à optimiser | la confondre avec un rendement moyen non composé |
| Borne long-only | contrainte dure | l'autoriser implicitement contre une pénalité |
| Budget de volatilité prévu | contrainte ex ante | le présenter comme garantie de perte réalisée |
| Coût de transaction | sortie monétaire dans la richesse | le retrancher aussi dans une récompense |
| Turnover | source du coût et indicateur opérationnel | le pénaliser arbitrairement en plus du coût sans justification |
| Drawdown | indicateur, objectif ou contrainte selon le mandat | utiliser les trois rôles simultanément |
| Rendement, volatilité réalisée, perte maximale | indicateurs d'évaluation | les traiter tous comme composantes obligatoires d'une récompense |

### 6.2 Utilité de richesse terminale

Maximiser `\mathbb E[U(W_T^-)]` donne un rôle direct à la richesse et au cumul des décisions. Avec `U(w)=\log w`, l'objectif équivaut à la somme des log-rendements nets :

$$
\log\left(\frac{W_T^-}{W_0^-}\right)
=\sum_{t=0}^{T-1}
\log\left(\frac{W_{t+1}^-}{W_t^-}\right).
$$

Cette additivité ne rend pas automatiquement les décisions indépendantes : le coût à `t+1` dépend du poids `w_{t+1}^-`, lui-même produit par l'action et le rendement précédents.

L'utilité logarithmique pénalise fortement l'approche de la ruine et valorise la croissance composée, mais elle représente un choix de préférence. Une utilité linéaire pourrait favoriser une exposition extrême lorsqu'un excès de rendement positif est attendu ; une utilité plus concave introduirait une autre aversion au risque. Aucune n'est universellement correcte.

Cette formulation exige en outre `W_T^->0` pour toute trajectoire admissible. L'absence de levier réduit le risque de richesse négative, mais une exposition de 100 % à un instrument pouvant perdre toute sa valeur rendrait encore le logarithme indéfini. Il faudrait alors justifier une borne strictement inférieure à 1, une hypothèse sur les rendements bruts ou une autre utilité ; aucun de ces choix n'est pris ici.

### 6.3 Croissance sous contrainte de risque

Séparer l'objectif de croissance et une contrainte de volatilité rend le mandat lisible. Toutefois :

- la contrainte dépend d'une prévision imparfaite ;
- une contrainte locale ne contrôle pas directement le drawdown total ;
- le budget doit être choisi économiquement, pas optimisé après observation des résultats ;
- une volatilité prévue très élevée peut forcer une faible exposition, tandis qu'une sous-estimation peut laisser trop de risque réalisé.

Le projet principal devient pertinent ici : il documente que la précision moyenne d'une prévision ne suffit pas à garantir sa fiabilité conditionnelle. Il ne détermine pas encore la prévision qui doit gouverner ce budget.

### 6.4 Ciblage de volatilité comme objectif

Minimiser

$$
\sum_t\left(widehat\sigma_{p,t}(w_t^+)-\bar\sigma\right)^2
$$

force l'adhésion à une cible prévue, mais ne récompense pas la croissance nette et peut induire des transactions coûteuses pour corriger de faibles écarts. Cette formulation est mieux comprise comme une règle de contrôle ou un critère secondaire que comme l'objectif économique complet.

### 6.5 Contrôle des pertes ou du drawdown

Un objectif portant sur une perte de queue ou un drawdown se rapproche d'une préoccupation de préservation. Il soulève néanmoins trois difficultés :

1. le drawdown est dépendant du chemin ;
2. une garantie dure peut être impossible face à un rendement risqué non borné ;
3. une approximation moyenne ou probabiliste change la signification du mandat.

Ces difficultés justifient de reporter une contrainte de drawdown plutôt que de l'ajouter au premier modèle sans définition précise.

### 6.6 Turnover et coûts

Le coût monétaire `K_t` réduit déjà `W_t^+`. Une pénalité additionnelle sur `\tau_t` ne serait justifiée que si le turnover produit une nuisance absente de `K_t` : capacité opérationnelle, fiscalité non modélisée ou limite institutionnelle. Sinon, elle double compte le même effet.

Une limite dure de turnover `\tau_t\leq\bar\tau` pourrait être nécessaire pour un instrument peu liquide. Elle reste hors du mandat minimal tant que l'instrument et sa liquidité ne sont pas choisis.

### 6.7 Indicateurs d'évaluation envisagés

Sans les transformer en récompense unique, une étude future devrait au minimum séparer :

- croissance et rendement net cumulés ;
- volatilité et pertes réalisées ;
- drawdown maximal et durée des drawdowns ;
- respect ex ante du budget et dépassements réalisés ;
- turnover et coûts cumulés ;
- stabilité de l'exposition et concentration temporelle des pertes ;
- comportement lors des épisodes de sous-estimation du risque.

La supériorité sur un indicateur ne démontrerait pas une domination financière globale.

## 7. Mécanisme intertemporel minimal

### 7.1 Ensemble recommandé

Le plus petit ensemble intéressant est :

1. un horizon comprenant plusieurs décisions ;
2. un poids risqué hérité qui dérive avec les rendements ;
3. un coût positif du changement d'exposition ;
4. un objectif de richesse terminale nette de ces coûts.

Le mécanisme est

$$
w_t^+
\longrightarrow
w_{t+1}^-
\longrightarrow
Q_{t+1}
\longrightarrow
K_{t+1}
\longrightarrow
W_{t+1}^+.
$$

Choisir `w_t^+` modifie le poids hérité et donc le coût nécessaire pour atteindre toute exposition future. Une décision peut accepter un écart temporaire au poids désiré afin d'éviter une transaction qui serait probablement inversée, ou payer un coût aujourd'hui si l'exposition doit être conservée assez longtemps.

### 7.2 Ce qui n'est pas nécessaire initialement

Il n'est pas nécessaire d'ajouter simultanément :

- un budget de turnover cumulatif ;
- une contrainte de drawdown ;
- une marge ou du levier ;
- une liquidation terminale obligatoire ;
- un budget de risque évolutif ;
- un impact de marché ;
- plusieurs actifs risqués.

Chacun créerait un état ou une contrainte supplémentaire, mais aucun n'est requis pour démontrer la dépendance intertemporelle provenant des coûts.

### 7.3 Rôle exact de la richesse

La richesse doit être suivie pour calculer les positions, coûts et performances. Pourtant, avec des coûts strictement proportionnels, des décisions exprimées en poids, aucune contrainte dépendant du montant et une utilité logarithmique, le problème peut être homogène en `W_t`. La richesse absolue pourrait alors ne pas être nécessaire comme variable de décision, même si elle reste indispensable à la comptabilité.

Elle redevient un état décisionnel indispensable si les coûts contiennent une partie fixe, si les unités ne sont pas fractionnables, si la marge dépend du montant, ou si l'utilité et les contraintes ne sont pas homogènes. Cette distinction devra être testée analytiquement avant de construire un état empirique.

### 7.4 Quand une règle myope suffit encore

Une solution période par période peut suffire si :

- `K_t=0` et les contraintes sont locales ;
- le poids peut être réinitialisé gratuitement ;
- les coûts sont si faibles que leur effet futur est économiquement négligeable ;
- le mandat impose directement une règle de poids sans arbitrage intertemporel ;
- l'horizon futur n'ajoute aucune valeur dépendant de l'action courante.

Même avec un coût positif, une règle simple de bande de rééquilibrage ou un contrôleur classique peut capter l'essentiel du compromis. La présence du mécanisme séquentiel autorise une comparaison dynamique ; elle ne préjuge pas de la méthode gagnante.

## 8. Données nécessaires à une future étude

Aucune donnée n'est collectée ici. Les familles suivantes sont classées par fonction économique.

### 8.1 Données indispensables au premier cas d'étude

| Famille | Fonction | Exigences minimales |
|---|---|---|
| Instrument actions investissable | exécution, valorisation et rendement détenu | prix exécutables horodatés, total return, distributions, splits, frais, calendrier |
| Composante monétaire investissable | rendement du capital non exposé | taux ou prix correspondant au placement accessible, convention et fréquence compatibles |
| Historique de l'instrument | information minimale de risque | rendements disponibles avant chaque décision, sans ajustement rétrospectif invisible |
| Coûts et liquidité d'exécution | relier turnover et richesse nette | spread, commissions, slippage ou hypothèses documentées ; volume si capacité pertinente |
| Métadonnées temporelles | empêcher la fuite | heure, fuseau, jours de marché, date de distribution, délai entre signal et ordre |

Les données Fama–French actuelles ne suffisent pas à elles seules : elles ne fournissent ni prix d'exécution d'un instrument, ni spread, ni unité négociable. Elles peuvent rester un point de comparaison pour les rendements de marché.

### 8.2 Données de l'environnement financier : enrichissements possibles

Ces familles ne sont pas toutes nécessaires à la première expérience. Chacune doit répondre à une question avant d'être admise :

| Famille | Question économique possible | Statut initial |
|---|---|---|
| Volatilité implicite | le prix de la protection contient-il une information prospective absente des rendements passés ? | enrichissement possible |
| Taux et courbe de taux | le rendement de la poche monétaire et le coût d'opportunité de réduire l'exposition changent-ils ? | taux monétaire indispensable ; courbe complète reportée |
| Conditions de crédit | une détérioration du financement signale-t-elle un environnement où le risque actions change ? | reporté |
| Liquidité de marché | le coût et la possibilité de rééquilibrer se dégradent-ils lorsque le risque augmente ? | coût minimal nécessaire ; indicateurs larges reportés |
| Variables macroéconomiques | l'état de l'activité, de l'inflation ou de la politique monétaire modifie-t-il la décision utile ? | reporté jusqu'à une hypothèse précise |
| Information propre à l'instrument | frais, distributions, tracking et capacité affectent-ils le rendement réellement capturé ? | indispensable après choix de l'instrument |

Cette cartographie n'autorise pas l'ajout simultané de ces variables. Les conclusions des notebooks 06 et 07 permettent seulement de demander si l'information historique de rendement est insuffisante ; elles ne prouvent pas quelle famille supplémentaire serait utile.

### 8.3 Données utilisées par une prévision

Il faut distinguer les données qui décrivent le portefeuille de celles qu'un modèle prédictif serait autorisé à employer. Pour toute variable candidate, il faudra documenter :

- l'heure et la date de première disponibilité ;
- le délai de publication ;
- la fréquence native ;
- les révisions et le millésime disponible à l'époque ;
- la transformation appliquée uniquement avec le passé ;
- la disponibilité au moment exact de l'action.

Une variable macroéconomique datée d'un mois ne peut pas être réputée connue pendant ce mois si elle est publiée plus tard. Une série révisée actuelle ne reproduit pas nécessairement l'information historique du gestionnaire.

### 8.4 Données d'exécution et de valorisation

Un adjusted close peut aider à calculer un rendement total, mais n'est pas automatiquement un prix exécutable. Une étude devra séparer :

- prix servant au signal ;
- prix auquel l'ordre est supposé exécuté ;
- prix de valorisation ;
- dividendes et distributions ;
- frais internes à l'instrument ;
- coûts externes de transaction.

Les unités temporelles des rendements risqué et monétaire doivent coïncider. Les jours sans cotation ne doivent pas être ajoutés artificiellement.

### 8.5 Données pour les risques réalisés

La richesse nette suffit à calculer rendement et drawdown du portefeuille. La volatilité réalisée nécessite une convention de fréquence et de fenêtre ; une mesure à cinq séances peut être conservée comme diagnostic, mais son chevauchement et son bruit doivent rester explicites. Les pertes de queue exigent assez d'événements et ne peuvent être évaluées honnêtement sur quelques épisodes déjà consultés.

### 8.6 Séparation temporelle future

Les périodes 2016–2019 et 2020–août 2026 ont déjà influencé le projet principal. Elles ne peuvent pas devenir silencieusement un test final intact. Avant toute étude, il faudra réserver la sélection des règles, l'estimation des paramètres et l'évaluation, purger les horizons qui traversent les frontières et figer les conventions d'exécution avant de regarder les résultats.

## 9. Références décisionnelles classiques

| Référence | Décision représentée | Ce qu'elle teste | Information nécessaire |
|---|---|---|---|
| Conservation d'une allocation initiale | ne plus traiter après l'initialisation | valeur de toute adaptation face aux coûts | prix et rendements des deux composantes |
| Poids constant rééquilibré | revenir périodiquement à un poids fixé | bénéfice d'un rééquilibrage simple ; coût de maintenir un poids | poids hérité, prix, coûts |
| Bande de rééquilibrage | ne traiter que lorsque l'écart dépasse une bande | valeur d'une inertie explicite et transparente | poids hérité, cible, coûts |
| Ciblage de volatilité | adapter le poids à une prévision de risque | utilité d'un budget de risque mécanique | prévision disponible à `t`, budget, bornes |
| Optimisation myope | choisir le meilleur compromis du prochain intervalle | coût d'ignorer les conséquences au-delà d'une période | prévision locale, coût courant, contraintes |
| Contrôle dynamique classique | valoriser les coûts et états futurs sous un modèle | valeur de l'optimisation intertemporelle elle-même | transitions, coûts et horizon spécifiés |

Une « exposition constante » doit être précisée. Conserver un nombre constant d'unités laisse le poids dériver ; maintenir un poids constant exige des transactions. Ces références ne sont donc pas équivalentes.

Le ciblage de volatilité est une référence obligatoire si le budget recommandé est retenu ; il possède une justification et une littérature propres, notamment [Moreira et Muir (2017)](https://doi.org/10.1111/jofi.12513). Le contrôle avec coûts doit être confronté à la littérature classique, dont [Davis et Norman (1990)](https://doi.org/10.1287/moor.15.4.676), avant d'attribuer un éventuel résultat à l'apprentissage.

Un contextual bandit pourrait suffire dans une formulation simplifiée où chaque action ne produit qu'un gain immédiat et ne change ni coûts ni possibilités futures ; voir [Lattimore et Szepesvári (2020)](https://tor-lattimore.com/downloads/book/book.pdf). Dans la formulation minimale avec position héritée et coûts, supprimer cette transition changerait le problème plutôt que le résoudre.

Aucune de ces approches n'est développée ou entraînée dans cette étude.

## 10. Principales difficultés méthodologiques

### 10.1 Spécification du mandat

Une performance élevée n'a de sens qu'au regard d'un objectif et de contraintes décidés avant l'évaluation. Modifier le budget, l'horizon ou les coûts après observation des résultats produirait un mandat adapté à l'échantillon.

### 10.2 Prévision de rendement et de risque

L'objectif de croissance dépend de la distribution des rendements, pas seulement de leur volatilité. Les rendements espérés à courte fréquence sont difficiles à estimer. Une politique peut paraître prudente parce qu'elle prévoit peu de risque tout en renonçant durablement à la prime actions ; inversement, une prévision de volatilité sous-estimée peut autoriser une exposition excessive.

### 10.3 Modèle de coûts

Un coût proportionnel constant est transparent mais peut être irréaliste pendant les périodes tendues. Utiliser des coûts futurs observés comme s'ils étaient connus à `t` créerait une fuite ; les prévoir ajoute un nouveau problème. Des analyses de sensibilité seraient nécessaires plus tard, mais aucune grille n'est fixée ici.

### 10.4 Exécution contrefactuelle

Un investisseur preneur de prix permet de recalculer plusieurs expositions sur une même trajectoire, mais seulement si ses ordres n'auraient pas modifié les prix et si la liquidité aurait permis leur exécution. Cette hypothèse devient moins crédible avec la taille, la fréquence ou le levier.

### 10.5 Risque et mesure

La volatilité prévue, la perte réalisée, le drawdown et le risque de modèle sont différents. Agréger ces quantités dans un score unique masquerait les compromis. `RV5` peut rester un diagnostic de l'amplitude future, pas la définition automatique de la qualité du mandat.

### 10.6 Non-stationnarité et périodes consultées

Les rendements, la volatilité, les taux et la liquidité changent. Une politique sélectionnée sur des épisodes rares peut apprendre leurs dates plutôt qu'un mécanisme généralisable. Les périodes déjà examinées ne fournissent pas une confirmation indépendante.

### 10.7 Comparabilité

Toutes les références devront employer les mêmes dates, rendements négociables, composante monétaire, coûts, contraintes et richesse initiale. Elles peuvent utiliser des règles d'information différentes si cette différence est l'objet de la comparaison, mais elle devra être déclarée.

## 11. Hypothèses recommandées et éléments reportés

### 11.1 Hypothèses de travail recommandées

- gestionnaire preneur de prix ;
- un instrument actions investissable et une composante monétaire ;
- portefeuille long-only sans levier ;
- action exprimée par un ordre signé ou un poids cible exactement converti en ordre ;
- coût initialement proportionnel au montant risqué traité ;
- richesse terminale nette de coûts comme base de l'objectif ;
- budget de volatilité prévu comme contrainte locale distincte ;
- drawdown, pertes et turnover rapportés séparément ;
- poids hérité et coût de rééquilibrage comme mécanisme intertemporel minimal.

Ces hypothèses forment une **recommandation cohérente**, pas une décision validée.

### 11.2 Éléments explicitement reportés

- sélection d'un ETF, indice, fonds ou fournisseur ;
- valeur du budget de volatilité ;
- fréquence et horizon calendaires ;
- vente à découvert, levier et marge ;
- coûts fixes, impact de marché ou fiscalité ;
- contrainte dynamique de drawdown ;
- budget cumulatif ou évolutif ;
- liquidation terminale obligatoire ;
- variables macroéconomiques, crédit, volatilité implicite ou liquidité large ;
- extension à plusieurs actifs risqués ;
- choix d'une méthode d'optimisation ou d'apprentissage.

## 12. Décisions nécessitant l'approbation du porteur

Avant toute expérience, il faut valider séparément :

1. **Profil et finalité :** la poche actions à risque contrôlé représente-t-elle bien l'utilisateur étudié ?
2. **Objectif :** la croissance logarithmique terminale nette de coûts est-elle acceptable, ou faut-il une autre représentation des préférences ?
3. **Budget de risque :** la volatilité prévue doit-elle être une contrainte, une cible, ou seulement un indicateur ?
4. **Univers :** confirme-t-on un seul instrument actions long-only et une poche monétaire sans levier ?
5. **Action :** le système choisira-t-il un poids cible continu, un ordre, ou un ensemble discret d'expositions ?
6. **Coûts :** un coût proportionnel est-il une première approximation acceptable, et quelles composantes doit-il couvrir ?
7. **Chronologie :** quelles fréquence, heure d'observation, heure d'exécution et durée de détention représentent une décision réaliste ?
8. **Horizon :** quelle durée économique donne un sens à la croissance et aux conséquences futures ?
9. **Instrument et données :** quels actifs investissables et quelles sources devront ensuite faire l'objet d'un audit, sans réutiliser automatiquement Fama–French ?
10. **Références :** quelles règles simples seront obligatoires avant tout contrôle appris ?

## 13. Conclusion

### 13.1 Ce que la formalisation établit

La gestion proposée peut être décrite sans RL par une comptabilité à deux composantes. Un ordre transfère une valeur entre la poche monétaire et l'instrument actions, détruit une richesse égale au coût, puis les deux positions produisent leurs rendements. Le poids après transaction n'est pas le poids hérité à la date suivante : les rendements le font dériver. Cette dérive détermine le prochain ordre et son coût.

Le mécanisme intertemporel minimal ne nécessite ni levier, ni drawdown contraignant, ni plusieurs actifs. Un poids hérité, un coût positif et un horizon multi-périodes suffisent pour que l'action présente modifie le coût des décisions futures. La dynamique de richesse mesure les conséquences, mais elle ne doit appartenir à l'état décisionnel que si l'homogénéité du problème ne permet pas de la factoriser.

La croissance du capital sous budget de volatilité constitue une formulation initiale plus défendable que la seule minimisation du risque. Elle sépare l'objectif, la contrainte et le coût, et évite un coefficient de préférence arbitraire. Elle ne garantit toutefois ni les pertes, ni le drawdown, et dépend de prévisions imparfaites.

### 13.2 Ce qui reste à démontrer

Il n'est pas établi que le mandat recommandé représente le meilleur utilisateur, que le coût de rotation est économiquement assez important pour exiger une solution dynamique, qu'une prévision de volatilité améliore la décision nette, ni que les données nécessaires sont disponibles sans fuite. Il n'est pas établi non plus qu'un contrôle classique serait insuffisant ou qu'un RL apporterait une valeur supplémentaire.

La prochaine étape ne doit donc pas être un entraînement. Elle doit être la validation — ou la révision — des dix arbitrages ci-dessus, puis seulement l'audit ciblé des données nécessaires au mandat accepté.
