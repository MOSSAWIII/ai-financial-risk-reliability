# Axe de recherche — Reinforcement Learning et décisions financières sous incertitude

## Statut

Ce dossier ouvre un axe de recherche autonome au sein de `ai-financial-risk-reliability`. Il contient un cadrage scientifique, une étude fondamentale sur la nature séquentielle d'une décision, une formalisation financière d'un mandat stylisé et un premier audit empirique des données candidates. Aucun algorithme de Reinforcement Learning (RL), modèle prédictif, environnement de simulation, stratégie ou backtest n'a été créé.

La question de départ est provisoire :

> Dans quelle mesure des politiques de décision financière apprises séquentiellement peuvent-elles améliorer la gestion du risque lorsque les prévisions sont imparfaites et que les conditions économiques et financières évoluent ?

Le RL n'est pas présumé nécessaire ni supérieur. Il ne sera retenu que si le problème financier comporte une dépendance intertemporelle réelle que des méthodes plus simples ne traitent pas convenablement.

## Pourquoi cet axe existe

Le projet principal a étudié la fiabilité de prévisions de volatilité future. Il a montré qu'une meilleure précision moyenne ne garantit pas une meilleure maîtrise des sous-estimations importantes, et que plusieurs modèles peuvent échouer aux mêmes dates. Les deux alertes historiques simples du notebook 07 n'ont pas reconnu convenablement les débuts de ces défaillances.

Ces résultats motivent une question différente : que doit faire un décideur lorsqu'une prévision est imparfaite ? Une décision d'exposition, d'allocation ou de couverture peut affecter la richesse, les coûts, les contraintes et les choix futurs. C'est cette structure séquentielle — et non la volonté d'utiliser une technologie particulière — qui pourrait justifier le RL.

Le nouvel axe ne modifie ni les conclusions ni le périmètre empirique des travaux antérieurs. `RV5`, les données Fama–French et les périodes déjà examinées constituent un socle critique, pas un environnement RL déjà validé.

## Principes scientifiques

- Partir d'une décision financière, d'un utilisateur et d'une contrainte explicites.
- Vérifier qu'une action présente modifie réellement les conséquences ou possibilités futures.
- Comparer le RL à une règle fixe, une politique déterministe simple, une optimisation classique et, lorsque c'est pertinent, un contextual bandit ou un contrôleur dynamique.
- Séparer rendement, risque, contraintes et coûts plutôt que de les masquer prématurément dans une récompense unique.
- Respecter strictement l'information disponible à la date de décision, les délais de publication et les révisions de données.
- Traiter les données historiques comme un ensemble hors ligne produit par des marchés et politiques passés, non comme un simulateur permettant une exploration sans coût.
- Conserver les résultats négatifs et ne pas confondre performance simulée, validation hors échantillon et utilité financière réelle.
- N'ajouter de complexité qu'après avoir montré ce qu'elle permet de comprendre ou de décider.

## Candidats actuellement étudiés conceptuellement

1. **Gestion dynamique d'une exposition risquée ou ciblage de volatilité.** Candidat le plus simple et le plus directement relié aux travaux existants. La décision présente modifie la position, les coûts de rotation et l'exposition future. Une règle classique de ciblage de volatilité constitue une référence naturelle.
2. **Allocation multi-actifs sous contraintes.** Problème plus riche, mais beaucoup plus exigeant en données, estimation des dépendances, traitement des coûts et dimension des actions.
3. **Couverture ou exécution dynamique.** Structure séquentielle forte, car l'inventaire et les transactions modifient les décisions futures. Les exigences de données, de microstructure et de simulation rendent toutefois ces problèmes prématurés comme point de départ.

Aucun de ces candidats n'est encore adopté comme objet empirique.

## État d'avancement

- [x] Relecture du socle scientifique et empirique existant.
- [x] Formalisation des notions minimales : MDP, POMDP, politique, valeurs et Bellman.
- [x] Comparaison conceptuelle du RL avec les principales alternatives.
- [x] Cartographie documentaire des grandes familles de données candidates.
- [x] Identification des risques de recherche et d'une trajectoire progressive.
- [x] Démonstration des conditions séparant décisions indépendantes et optimisation intertemporelle pour une exposition risquée.
- [x] Formalisation comptable d'un mandat actions–monétaire et proposition non validée d'un mécanisme intertemporel minimal.
- [ ] Choix d'un problème financier précis.
- [ ] Définition de l'utilisateur, de la décision, de l'horizon et des contraintes.
- [x] Premier audit des instruments actions–monétaire, des sources publiques et de leur disponibilité temporelle.
- [ ] Choix des instruments et audit d'une source de rendements totaux suffisamment profonde.
- [ ] Validation des références classiques avant toute méthode RL.
- [ ] Autorisation explicite d'une première expérience.

## Questions prioritaires à discuter

1. Quel utilisateur financier et quelle décision voulons-nous représenter ?
2. Les actions affectent-elles seulement le gain courant, ou aussi l'état futur par la position, les coûts, la richesse ou les contraintes ?
3. Le risque doit-il être un objectif, une pénalité ou une contrainte séparée ?
4. Quelle fréquence de décision est économiquement réaliste et compatible avec les données ?
5. Quelles règles simples doivent être difficiles à battre avant que le RL soit jugé utile ?
6. Comment réserver une évaluation réellement non consultée alors que plusieurs périodes du projet principal ont déjà orienté la recherche ?

Le document [docs/CADRAGE_SCIENTIFIQUE.md](docs/CADRAGE_SCIENTIFIQUE.md) développe ces questions, les données candidates, les alternatives et les références examinées. L'étude [docs/PROBLEME_DECISION_SEQUENTIELLE.md](docs/PROBLEME_DECISION_SEQUENTIELLE.md) démontre quand les décisions se séparent période par période, quels mécanismes financiers créent une interdépendance et pourquoi ce besoin de contrôle ne suffit pas à justifier le RL. La proposition [docs/FORMALISATION_MANDAT_FINANCIER.md](docs/FORMALISATION_MANDAT_FINANCIER.md) décrit un gestionnaire stylisé, les flux exacts d'un portefeuille actions–monétaire, un mandat initial à discuter et les arbitrages requis avant toute expérience. Le notebook exécuté [EDA/01_audit_univers_financier.ipynb](EDA/01_audit_univers_financier.ipynb) audite SPY, IVV, VTI, deux séries de taux et le VIX, puis distingue ce qui est reconstructible de ce qui manque encore. Les copies brutes horodatées et hachées sont conservées localement sous `data/raw/` et exclues de GitHub.

## Règle d'arrêt

Aucun benchmark décisionnel, environnement, backtest ou choix d'algorithme ne découle automatiquement de cet audit. La prochaine étape devra être validée explicitement.
