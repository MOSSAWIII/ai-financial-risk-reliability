# Protocole G2 — matérialité empirique de la séquentialité

## 1. Statut

**Statut : `FROZEN_RETROSPECTIVE_DIAGNOSTIC`.**

**Amendement documentaire non analytique du 10 novembre 2026.** Lors du premier
appel au moteur, avant tout calcul de performance, le rapport dérivé d'audit
Yahoo et les trois PDF calendaires additionnels déclarés dans le manifeste ont
été identifiés comme dépendances techniques. Ils ont été ajoutés à la porte
documentaire avec leurs empreintes existantes. Aucun signal, paramètre,
politique, seuil, mesure ou règle de verdict n'a été modifié.

Ce protocole définit la première traduction empirique du mécanisme identifié
par G1. Il est gelé avant toute exécution d'une nouvelle politique sur le moteur
historique. Il ne constitue pas une préinscription confirmatoire : l'épisode du
29 mai 2024 au 29 mai 2025, les prix et les résultats C1–C2 ont déjà été
consultés dans les phases antérieures.

G2 est donc un diagnostic rétrospectif de mécanisme. Il peut montrer que la
planification dynamique change matériellement ou non la trajectoire comptable
dans le moteur réel du projet. Il ne peut démontrer une performance hors
échantillon ni une capacité prédictive généralisable.

## 2. Question scientifique

> Lorsque l'information, les actions et les coûts sont identiques, la prise en
> compte de la position héritée et des coûts futurs produit-elle une différence
> économiquement matérielle par rapport à une décision myope dans le moteur
> historique SPY–BIL ?

La question porte sur la **matérialité du couplage intertemporel**, pas encore
sur l'apprentissage. Les deux politiques utilisent le même signal observable et
le même modèle de décision gelé ; seule leur profondeur de planification diffère.

## 3. Frontière documentaire obligatoire

L'exécution canonique exige les fichiers originaux identifiés par le manifeste,
notamment :

| Source | SHA-256 requis |
|---|---|
| Yahoo SPY | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| Yahoo BIL | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| Audit dérivé Yahoo SPY–BIL | `e33ba4c2b5b962e6f46b7f37853eb73fc5bdc27269456830dbc77fb72274fe89` |
| Distributions State Street | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| Calendrier NYSE 2022–2025 | `2c2e63b780c4a373d8d546904ae46c8ba7e8070ad9357d23d2c92749985bb6c9` |
| Règle SEC T+1 | `e214bf80244fe9107c867d7abeb6a6b969029c519566036e42b081977a9b575a` |
| Guide DTC T+1 | `1655962c57e5a1459cf0d29c853b0bf924c3255aba5be0e0d04c4a7d2536b7f2` |

L'audit dérivé est une dépendance technique explicite du moteur, pas un substitut
aux deux réponses Yahoo brutes. Une nouvelle réponse téléchargée depuis la même URL n'est pas substituable si
son empreinte diffère. Les sorties historiques versionnées peuvent servir de
contrôle de réplication, mais ne remplacent pas silencieusement les sources
brutes pour l'exécution d'une nouvelle politique.

Si une source obligatoire est absente ou différente, le verdict est
`DOCUMENTARY_BLOCK`; aucune richesse G2 n'est calculée.

## 4. Épisode et cellules

Le périmètre reste celui déjà documenté :

- décision initiale : 29 mai 2024 à 08:00 ET ;
- achat initial : open Yahoo du 29 mai 2024 ;
- terminal : close commun du 29 mai 2025 ;
- capital initial : 100 000 USD ;
- parts entières ;
- long-only, sans levier ;
- financement `H_FIN_NET` ;
- absence de liquidation terminale fictive ;
- 52 décisions récurrentes candidates ;
- conventions de cash D+1 et D+2 ;
- coûts S0, S1, S2, S3 égaux à 0, 1, 5, 10 pb.

Les huit cellules sont le produit

\[
\{S0,S1,S2,S3\}\times\{D+1,D+2\}.
\]

Chaque paire myope–dynamique partage exactement les mêmes sources, dates,
positions initiales, distributions et règles d'arrêt.

## 5. Signal observable gelé

À la décision récurrente `k`, les closes SPY et BIL du dernier jour admissible
sont `P^S_k` et `P^B_k`. À partir de la cinquième décision récurrente, le signal
est l'excès de rendement logarithmique sur quatre intervalles de décision :

\[
X_k=
\log\left(\frac{P^S_k}{P^S_{k-4}}\right)
-
\log\left(\frac{P^B_k}{P^B_{k-4}}\right).
\]

Le régime observable est

\[
Z_k=
\begin{cases}
RISK\_ON,&X_k\ge 0,\\
RISK\_OFF,&X_k<0.
\end{cases}
\]

Les quatre premières décisions récurrentes reçoivent `WARMUP` et imposent la
cible 50/50 aux deux politiques. Le signal n'utilise ni open futur, ni rendement
futur, ni `Adjusted Close`, ni information rétrospective de distribution.

Ce signal est volontairement minimal. Il n'est pas présenté comme un estimateur
optimal des régimes économiques.

## 6. Modèle de décision commun

Le laboratoire G1 est réutilisé sans recalibration :

- actions SPY : `{0, 0.25, 0.50, 0.75, 1}` ;
- rendements conditionnels stylisés : SPY `0,20 %` en `RISK_ON`, `0 %` en
  `RISK_OFF`, BIL `0,10 %` dans les deux états ;
- transition : `[[0.80, 0.20], [0.35, 0.65]]` ;
- horizon dynamique : 12 décisions ;
- récompense interne du contrôleur : log-richesse après coût proportionnel.

Ces paramètres ne sont pas estimés sur 2024–2025. Ils servent à isoler la
différence entre profondeur zéro et profondeur dynamique, non à revendiquer un
modèle prédictif correctement calibré.

## 7. Politiques comparées

### 7.1 `M_G2` — politique myope

Pour le régime observable, le poids hérité et le coût de la cellule, `M_G2`
choisit l'action maximisant uniquement la récompense conditionnelle immédiate.

### 7.2 `D_G2` — contrôleur dynamique

`D_G2` résout à chaque décision le programme dynamique G1 sur un horizon
glissant de douze périodes et applique uniquement sa première action.

### 7.3 Traduction financière commune

La cible de poids est remise au même adaptateur strict :

- budget E-B identique ;
- quantités entières dimensionnées au close connu ;
- intention scellée avant l'open ;
- exécution hypothétique au prochain Yahoo `Open` admissible ;
- règlement, distributions, cash et coûts traités par le même registre ;
- rejet atomique, sans redimensionnement ex post.

## 8. Contrôles négatifs

Avant toute interprétation :

1. les politiques doivent produire les mêmes actions en S0, S1 et S2 dans
   toutes les cellules atteignables de l'épisode ;
2. lorsque les actions sont identiques, leurs trajectoires et richesses doivent
   être identiques octet pour octet ;
3. chaque action doit dépendre uniquement des closes disponibles, du poids
   hérité, du coût gelé et du modèle commun ;
4. modifier un open futur sans changer les closes ne doit pas modifier
   l'intention scellée ;
5. chaque cellule doit s'arrêter au premier `DOCUMENTARY_BLOCK` ou
   `NOT_EVALUABLE` commun ;
6. les résultats C1–C2 existants ne sont ni des entrées de politique, ni des
   cibles de calibration.

## 9. Mesures

La mesure primaire par convention de cash est la différence S3 :

\[
\Delta W_T
=W_T(D\_G2)-W_T(M\_G2),
\qquad
\delta_T=\frac{\Delta W_T}{100000}.
\]

Mesures secondaires :

- différence de log-richesse terminale ;
- différence de maximum drawdown ;
- différence de volatilité annualisée ;
- turnover et notionnel échangé ;
- frais cumulés ;
- nombre de changements de cible ;
- nombre de lots exécutés, holds et rejets ;
- décomposition de `Delta W_T` entre exposition et coûts, descriptive seulement.

## 10. Seuil de matérialité et verdicts

Le seuil économique est gelé à 25 pb du capital initial :

\[
|\delta_T|\ge 0.0025
\quad\Longleftrightarrow\quad
|\Delta W_T|\ge 250\;USD.
\]

Trois verdicts sont possibles :

- `G2_MATERIAL_POSITIVE` : seuil atteint avec `Delta W_T>0` dans D+1 et signe
  positif dans D+2 ;
- `G2_MATERIAL_OTHER` : seuil absolu atteint mais bénéfice non cohérent entre
  D+1 et D+2 ;
- `G2_NOT_MATERIAL` : seuil non atteint ;
- `DOCUMENTARY_BLOCK` : sources originales absentes ou invalides.

Le passage vers G3 exige `G2_MATERIAL_POSITIVE`. Les autres verdicts ne
justifient pas l'apprentissage d'une politique.

## 11. Sorties obligatoires

Sous `results/g2_empirical_sequentiality/` :

- `readiness_report.json` ;
- `policy_decisions.csv` ;
- `daily_trajectories.csv` ;
- `financial_summary.csv` ;
- `paired_comparison.csv` ;
- `g2_report.json`.

En cas de blocage documentaire, seul `readiness_report.json` est écrit. Les
autres fichiers restent absents : aucune valeur manquante n'est remplacée par
zéro.

## 12. Limites d'interprétation

Même un verdict positif resterait :

- rétrospectif et limité à un épisode déjà consulté ;
- conditionnel aux proxys Yahoo et aux conventions E-B, D+1/D+2 ;
- dépendant d'un signal et d'un modèle stylisés non estimés ;
- sans correction crédible du data snooping sur un seul épisode ;
- insuffisant pour conclure que CQL, IQL, PPO ou tout autre RL est nécessaire.

G2 peut autoriser G3 — démontrer le besoin d'apprentissage — mais ne l'anticipe
pas.
