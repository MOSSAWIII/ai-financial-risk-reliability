# Protocole scientifique V2 — valeur de la séquentialité avant RL

## 1. Statut et règle de lecture

**Statut : `FROZEN_STRUCTURAL_MECHANISM_TEST`.**

Ce document définit le prochain jalon scientifique de l'axe SPY–BIL. Les
paramètres ont été choisis pendant une phase de conception comportant des
calculs exploratoires, puis gelés avant l'exécution canonique décrite aux
sections 7 à 10. Il ne s'agit donc pas d'une préinscription statistique et le
laboratoire ne sert pas à produire une p-value. Il constitue une preuve
constructive, reproductible et falsifiable du mécanisme. Le document ne modifie
ni les résultats historiques déjà publiés, ni les conventions comptables et
documentaires de la version 1.

Le jalon ne cherche pas à montrer qu'un agent de Reinforcement Learning est
rentable. Il cherche d'abord à répondre à une question logiquement antérieure :

> Les frictions et la position héritée créent-elles une valeur mesurable de la
> décision dynamique par rapport à une optimisation myope ?

Le test est exclusivement synthétique. Son succès établirait un mécanisme de
séquentialité dans un modèle contrôlé, pas une performance financière réelle.
Son échec interdirait de justifier un algorithme RL par ce mécanisme précis.

## 2. Héritage scientifique conservé

Le protocole conserve les principes déjà établis :

- décision SPY–BIL long-only, sans levier ;
- position, cash, coûts, distributions et règlements comptabilisés séparément ;
- information point-in-time distincte de l'état économique d'audit ;
- prix futurs exclus de l'information de décision ;
- politiques simples évaluées avant toute politique apprise ;
- résultats négatifs conservés ;
- aucune assimilation d'un prix Yahoo `Open` à un fill individuel ;
- aucune extension historique automatique à partir d'une preuve synthétique.

Les moteurs historiques et comptables existants restent la référence pour les
expériences empiriques futures. Le test V2 utilise un modèle minimal séparé afin
d'isoler exactement le mécanisme étudié.

## 3. Question, hypothèses et objet falsifiable

Soit un état de marché observable `Z_t`, un poids SPY hérité `H_t` et une action
`A_t` choisie dans un ensemble fini de poids SPY. La position suivante est

\[
H_{t+1}=A_t.
\]

Cette identité transmet l'action courante aux coûts de rotation futurs. Les
rendements de marché restent exogènes : le portefeuille est preneur de prix.

### Hypothèse nulle structurelle

\[
H_0^{\mathrm{seq}}:
V^{\mathrm{DP}}(z,h)=V^{\mathrm{myope}}(z,h)
\]

pour le modèle et l'horizon préspecifiés.

### Hypothèse alternative structurelle

\[
H_1^{\mathrm{seq}}:
\exists c>0,\;\exists(z,h)
\quad
V^{\mathrm{DP}}(z,h)>V^{\mathrm{myope}}(z,h).
\]

L'alternative exige une supériorité calculée sous les mêmes transitions,
rendements, actions, coûts et distribution initiale. Elle n'est pas satisfaite
par une comparaison entre deux moteurs ou deux jeux de données différents.

## 4. Critère économique

Pour une richesse avant décision `W_t`, un poids hérité `h`, une cible `a`, un
coût proportionnel unidirectionnel `c` et les rendements simples conditionnels
`R_SPY(z)` et `R_BIL(z)`, le facteur de richesse synthétique est

\[
G(z,h,a;c)
=
\left(1-c|a-h|\right)
\left(1+aR_{SPY}(z)+(1-a)R_{BIL}(z)\right).
\]

La récompense est l'incrément de log-richesse :

\[
r(z,h,a;c)=\log G(z,h,a;c).
\]

Cette écriture rend les récompenses additives et applique le coût une seule
fois. Un état-action est invalide si l'un des deux facteurs est non positif.
Aucun terme de volatilité, drawdown ou turnover n'est ajouté arbitrairement à
la récompense de ce premier test.

## 5. Deux politiques comparées

### 5.1 Politique myope

\[
\pi^{M}(z,h)
\in
\arg\max_{a\in\mathcal A} r(z,h,a;c).
\]

Elle maximise uniquement le gain conditionnel immédiat. En cas d'égalité
numérique, la règle déterministe choisit d'abord la rotation la plus faible,
puis le poids SPY le plus faible.

### 5.2 Programmation dynamique finie

Avec `V_T=0`, la récurrence est

\[
V_t(z,h)=
\max_{a\in\mathcal A}
\left\{
r(z,h,a;c)
+
\sum_{z'}P(z'\mid z)V_{t+1}(z',a)
\right\}.
\]

La politique dynamique applique la même règle de départage. Le marché est
exogène, mais la position héritée contrôlée suffit à coupler les décisions
lorsque `c>0`.

## 6. Paramètres gelés du laboratoire synthétique

Le laboratoire principal contient deux régimes :

| Paramètre | `RISK_ON` | `RISK_OFF` |
|---|---:|---:|
| Rendement hebdomadaire SPY | 0,20 % | 0,00 % |
| Rendement hebdomadaire BIL | 0,10 % | 0,10 % |
| Probabilité initiale | 50 % | 50 % |

La matrice de transition, lignes = régime courant et colonnes = régime suivant,
est

\[
P=
\begin{pmatrix}
0.80 & 0.20\\
0.35 & 0.65
\end{pmatrix}.
\]

Autres paramètres :

- horizon : `T=12` décisions hebdomadaires ;
- poids initial SPY : `H_0=0.50` ;
- actions : `A={0, 0.25, 0.50, 0.75, 1}` ;
- coûts testés : `0, 5, 10, 25, 50, 100` points de base ;
- calcul : espérance exacte par propagation de probabilités, sans Monte-Carlo ;
- tolérance numérique de comparaison : `1e-12` sur les valeurs agrégées.

Ces rendements sont des paramètres artificiels, non des estimations de primes
futures. Le but est d'obtenir un laboratoire interprétable dans lequel l'écart
de rendement conditionnel est du même ordre que les frictions testées.

## 7. Contrôles négatifs obligatoires

Le test doit vérifier avant toute interprétation :

1. **coût nul** : la politique dynamique et la politique myope ont la même
   valeur attendue, car l'action courante ne modifie plus aucun coût futur ;
2. **horizon unitaire** : les deux politiques coïncident, quel que soit le coût,
   car aucune conséquence future ne reste à valoriser ;
3. **domination faible** : la valeur dynamique calculée ne peut être inférieure
   à celle de la politique myope évaluée dans le même modèle ;
4. **probabilités** : chaque ligne de la matrice de transition et la distribution
   initiale somment à un ;
5. **reproductibilité** : deux exécutions produisent les mêmes fichiers et la
   même empreinte du modèle.

Une violation invalide le test avant examen du résultat principal.

## 8. Mesure primaire

Pour chaque coût `c`, la valeur séquentielle est

\[
\Delta_{seq}(c)
=
V_0^{DP}(c)-V_0^{M}(c).
\]

Son équivalent multiplicatif de richesse est

\[
U_{seq}(c)=\exp\!\left(\Delta_{seq}(c)\right)-1.
\]

Les valeurs sont des espérances exactes de log-richesse sous la distribution
initiale préspecifiée. Aucun test de significativité n'est pertinent dans ce
laboratoire déterministe : il n'existe ni échantillonnage ni bruit Monte-Carlo.

## 9. Porte G1 — décision gelée

La porte structurelle `G1` passe si et seulement si :

1. tous les contrôles négatifs de la section 7 passent ;
2. `|Delta_seq(0)| <= 1e-12` ;
3. il existe au moins un coût strictement positif gelé tel que
   `Delta_seq(c) > 1e-12` ;
4. au moins une décision dynamique diffère de la décision myope dans une
   cellule atteignable depuis la distribution initiale.

Le passage de G1 signifie seulement :

> la position héritée et les coûts suffisent à créer une décision
> intertemporelle dans le laboratoire V2.

Il ne signifie pas que l'effet est matériel aux coûts réels, qu'un état de
marché est observable, que la matrice est estimable, ni qu'un algorithme RL est
nécessaire.

## 10. Sorties reproductibles

Le script `scripts/sequentiality_test.py` doit écrire :

- `results/sequentiality_v2/sequentiality_results.csv` ;
- `results/sequentiality_v2/sequentiality_report.json`.

Le rapport JSON contient les paramètres, les valeurs, les actions initiales,
les contrôles, le verdict G1 et les empreintes SHA-256 du script et du présent
protocole. Les résultats générés sont versionnés avec le code.

## 11. Ce que G1 n'autorise pas

Même si G1 passe, sont interdits sans protocole additionnel :

- entraînement PPO, DQN, SAC, CQL, IQL ou autre agent ;
- calibration des régimes sur les épisodes déjà examinés ;
- conclusion de rentabilité historique ou future ;
- sélection ex post d'un coût ou d'un horizon favorable ;
- modification des paramètres du laboratoire puis présentation du nouveau
  résultat comme préspecifié ;
- extension de la politique synthétique au moteur historique.

## 12. Étapes conditionnelles après G1

### G2 — matérialité empirique de la séquentialité

Construire une comparaison historique verrouillée entre optimisation myope et
contrôle dynamique classique dans le moteur comptable existant. Les périodes
2024–2026 déjà consultées doivent être déclarées contaminées pour la sélection.

### G3 — besoin d'apprentissage

Identifier quelle quantité inconnue exige l'apprentissage d'une politique. Si
un modèle de contrôle explicite ou une règle de non-transaction suffit, le RL
n'est pas retenu.

### G4 — support et évaluation

Avant tout offline RL : documenter le support état-action, verrouiller un vrai
hors-échantillon temporel, enregistrer toutes les variantes testées, appliquer
une inférence tenant compte de la dépendance temporelle et des essais multiples.

## 13. Critère d'arrêt scientifique

Le programme doit s'arrêter ou revenir à un contrôleur plus simple si :

- G1 échoue ;
- l'écart dynamique disparaît sous des coûts plausibles ;
- l'état nécessaire n'est pas observable point-in-time ;
- le gain provient uniquement d'un régime ou d'une période consultée ;
- la politique apprise propose principalement des actions hors support ;
- la supériorité disparaît après coûts, corrections de sélection ou ablations.

Un arrêt documenté constitue un résultat scientifique valide.
