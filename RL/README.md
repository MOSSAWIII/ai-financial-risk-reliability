# Axe de recherche — Reinforcement Learning et décisions financières sous incertitude

## Statut

Ce dossier ouvre un axe de recherche autonome au sein de `ai-financial-risk-reliability`. Il contient un cadrage scientifique, une étude fondamentale sur la nature séquentielle d'une décision, une formalisation financière, un audit de faisabilité d'un mandat SPY–BIL et un patrimoine local de données documentées. BIL-A reste validée sous la convention à l'ex-date. SPY-B et BIL-B suivent les parts, les créances et leur réinvestissement à la date de paiement. BIL-B est validée pour l'analyse NAV du 4 mars 2008 au 15 octobre 2026 ; sa frontière exclut explicitement la distribution du 3 mars 2008 dont les dates historiques restent incohérentes. Aucun algorithme de Reinforcement Learning (RL), modèle prédictif, environnement de simulation, stratégie ou backtest n'a été créé.

La priorité active est désormais : **préspécifier et valider sur cas artificiels le contrat temporel minimal d'une future comparaison C1–C2, sans exécuter C2.** Les données brutes sont conservées localement sous `data/raw/`, exclues de GitHub et sauvegardées sur un disque physique distinct. Leur inventaire publiable se trouve dans [`data_manifest.json`](data_manifest.json), les contrôles reproductibles dans [`scripts/verify_local_data.py`](scripts/verify_local_data.py), et les résultats détaillés dans [`docs/AUDIT_DONNEES_ACADEMIQUES_LOCALES.md`](docs/AUDIT_DONNEES_ACADEMIQUES_LOCALES.md).

Le rapport [`docs/MANDAT_OPERATIONNEL_ET_FAISABILITE_SPY_BIL.md`](docs/MANDAT_OPERATIONNEL_ET_FAISABILITE_SPY_BIL.md) recommande, sans l'adopter, une poche SPY–BIL long-only et sans levier, révisée chaque semaine après clôture puis exécutée à l'ouverture suivante. L'[audit des prix de marché SPY–BIL](docs/AUDIT_PRIX_MARCHE_SPY_BIL.md) a depuis acquis une source Yahoo commune : 4 878 séances communes du 30 mai 2007 au 16 octobre 2026, dont 2 514 sur la fenêtre prioritaire d'octobre 2016 à octobre 2026. Les OHLCV sont cohérents structurellement et ajustés des splits, mais restent `AUDITED` : la définition exacte de l'ouverture et les conditions d'exécution ne sont pas suffisamment documentées, et aucun historique bid/ask n'est acquis.

Le [`protocole d'exécution financière hypothétique v1`](docs/PROTOCOLE_EXECUTION_FINANCIERE_SPY_BIL_V1.md) recommande désormais une convention strictement conditionnelle : quantités entières dimensionnées au close déjà connu, valorisation hypothétique au Yahoo `Open` de la prochaine séance admissible et comptes de règlement séparés. La fenêtre candidate post-split commence le 2 janvier 2018 et contient 2 210 séances communes. Le champ `Open` n'est pas assimilé à un fill ou au prix officiel de l'enchère; le 20 avril 2026 reste non représentable pour une transaction v1 en raison d'une divergence SPY non résolue. Le script [`scripts/audit_spy_open_divergences.py`](scripts/audit_spy_open_divergences.py) reproduit les 17 alertes d'ouverture sans corriger les sources.

Le [registre comptable synthétique](docs/VALIDATION_REGISTRE_COMPTABLE_SYNTHETIQUE.md) implémente, sans données historiques, les positions économiques et réglées, cash, créances/dettes de règlement, distributions, frais et regroupements de parts. Sa [validation temporelle renforcée](docs/VALIDATION_TEMPORELLE_REGISTRE_SPY_BIL.md) ajoute deux calendriers distincts, une chronologie monotone, un ordre journalier explicite, la séparation annonce/ex-date/paiement et le calcul obligatoire T+2/T+1. Les 29 tests initiaux sont conservés; **45 tests artificiels** passent désormais. Le contrôle documentaire retrouve exactement les 2 210 dates communes Yahoo sur 2018–2026, mais le calendrier de règlement officiel reste incomplet et interdit encore toute expérience historique.

Le rapport [`PREREQUIS_EXPERIENCE_FINANCIERE_SPY_BIL.md`](docs/PREREQUIS_EXPERIENCE_FINANCIERE_SPY_BIL.md) ferme le cadrage opérationnel restant. Les règles DTC/NSCC distinguent désormais jours de traitement et dates de règlement, notamment Columbus Day, Veterans Day, Good Friday et les fermetures imprévues. L'archive annuelle 2018–2026 demeure non exhaustive : le projet est `PARTIALLY_READY`, avec financement conservateur recommandé, contrat d'intégration strict et classification déterministe des situations non représentables. Aucune intégration historique n'est encore autorisée.

La proposition [`MANDAT_EXPERIMENTAL_SPY_BIL_V1_PROPOSITION.md`](docs/MANDAT_EXPERIMENTAL_SPY_BIL_V1_PROPOSITION.md) transforme ces prérequis en choix soumis à approbation. Après examen ciblé des règles de compte cash, elle révise la recommandation provisoire et propose `H_FIN_NET` uniquement pour les produits de ventes de titres réglés et les flux de même échéance, sans marge ni cash projeté négatif. Elle fixe la traduction poids–quantités, le rejet atomique, une richesse principale de 100 000 USD, un horizon économique d'un an et le contrat minimal de la prochaine implémentation. Aucun de ces choix n'est adopté et aucune expérience historique n'est autorisée.

L'[`adaptateur synthétique de décision`](docs/VALIDATION_ADAPTATEUR_DECISION_SPY_BIL.md) implémente maintenant, sans donnée historique, la transformation d'un poids SPY fourni en quantités entières figées puis en lot hypothétique strict. Il limite `H_FIN_NET` aux ventes de parts déjà réglées, distingue cash réglé et produit de vente non réglé, bloque la revente avant paiement et sépare hold volontaire, rejet économique, défaut documentaire et entrée invalide. Les **69 tests artificiels** passent ; ils valident le mécanisme comptable et temporel, pas un courtier, un fill Yahoo ou une expérience financière.

La [frontière d'ingestion synthétique](docs/VALIDATION_FRONTIERE_INGESTION_SPY_BIL.md) ajoute un contrat JSON v1 strict et reproductible, une empreinte exacte du fixture, des identifiants d'intention dérivés du contenu et un journal terminal minimal. Elle refuse les intentions altérées et les doubles traitements après rechargement, sans prétendre restaurer le registre après incident. Les **93 tests artificiels** passent. Cette validation n'utilise aucune donnée de marché et n'autorise toujours ni ingestion historique, ni portefeuille, ni backtest.

La [validation point-in-time SPY–BIL](docs/VALIDATION_POINT_IN_TIME_SPY_BIL.md) distingue maintenant date économique, observabilité, publication, acquisition et révision. Un contrôle en lecture seule de huit lignes Yahoo présélectionnées vérifie les empreintes, met en regard la transition T+2/T+1 documentée et retrouve l'anomalie SPY du 20 avril 2026, sans transaction ni performance. Les `Close`/`Open` actuels restent des `MARKET_OBSERVABLE_PROXY`, les annonces historiques de distributions et plusieurs calendriers restent insuffisamment prouvés, et le verdict est **`PARTIALLY_VERIFIED`**. À ce stade documentaire, aucune intégration financière n'était encore autorisée.

Le [premier cycle historique contrôlé](docs/PREMIER_CYCLE_HISTORIQUE_CONTROLE_SPY_BIL.md) relie désormais les closes du 28 mai 2024 et les opens du 29 mai à l'adaptateur et au registre strict, puis au règlement T+1 explicitement documenté du 30 mai. Les quantités 94 SPY et 544 BIL sont figées avant lecture de l'open ; le lot complet est accepté, réglé et conserve exactement la richesse comptable à prix constant. Le verdict est **`HISTORICAL_CYCLE_VALIDATED`** et les **103 tests** passent. Cette preuve ponctuelle utilise des proxys Yahoo, ne mesure aucune performance et n'autorise ni deuxième cycle, ni backtest, ni stratégie.

Le [protocole des références financières SPY–BIL](docs/PROTOCOLE_REFERENCES_FINANCIERES_SPY_BIL_V1.md) définit maintenant cinq politiques opérationnellement distinctes : détention de SPY, détention de BIL, 50/50 conservé, 50/50 rééquilibré et calibrage déterministe de la poche SPY par une estimation de volatilité disponible à la décision. Il sépare explicitement `RV5` futur des informations admissibles, impose une comparaison appariée sur couverture documentaire commune et recommande de commencer, après approbation, par les trois références sans décisions répétées. Le document ne fixe aucun paramètre arbitraire, n'exécute aucune politique et ne calcule aucune performance.

La [première évaluation exploratoire A/B/C1](docs/PREMIERE_EVALUATION_EXPLORATOIRE_SPY_BIL_A_B_C1.md) applique ce socle à l'unique épisode préspécifié du 29 mai 2024 au 29 mai 2025. Les trois achats initiaux sont réglés, les positions restent constantes, quatre distributions SPY et douze BIL deviennent créances puis cash sans réinvestissement, et 251 closes communes alimentent les mesures. Sur cette seule réalisation à coûts externes nuls, A termine à 113 448,70 USD avec le risque le plus élevé, B à 104 607,45 USD avec le risque le plus faible et C1 à 109 025,96 USD avec des mesures intermédiaires. Le verdict est **`EXPLORATORY_EVALUATION_VALIDATED`** ; il ne démontre aucune supériorité générale et n'autorise ni C2, ni règle D, ni second épisode.

La [validation de couverture et sensibilité aux coûts A/B/C1](docs/VALIDATION_SENSIBILITE_COUTS_SPY_BIL_A_B_C1.md) confronte désormais l'épisode au calendrier NYSE 2024–2025 : les 251 séances attendues sont présentes pour les deux instruments, les 16 distributions sont intégralement réconciliées et les richesses terminales sont retrouvées indépendamment. Les scénarios théoriques S0, S1 et S2 sont finançables pour les trois références ; à 10 pb (S3), B est rejeté sans redimensionnement parce que ses frais excèdent son cash résiduel. Le verdict est **`COST_SENSITIVITY_VALIDATED`**. C2 reste bloqué par le calendrier de règlement hebdomadaire et la séparation point-in-time entre comptabilité ex post et information décisionnelle.

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
- [x] Proposition d'un problème financier précis, sous réserve de validation explicite.
- [x] Définition d'un utilisateur, d'une décision, d'un horizon et de contraintes candidats.
- [x] Premier audit des instruments actions–monétaire, des sources publiques et de leur disponibilité temporelle.
- [x] Acquisition et audit local de 19 fichiers académiques ou institutionnels, avec SHA-256 et statuts d'usage.
- [x] Vérificateur hors ligne et sauvegarde contrôlée sur un disque physique distinct.
- [x] Reconstruction comptable et audit des rendements totaux quotidiens à la NAV de SPY et BIL.
- [x] Confirmation documentaire du fractionnement inversé BIL et contrôle contre quatre performances NAV officielles.
- [x] Explication comptable de l'écart SPY et validation limitée d'une série distincte à la date de paiement.
- [x] Compatibilité comptable à la NAV de SPY-B et BIL-B à partir du 2008-03-04, avec créances et cash séparés.
- [x] Formalisation de la chronologie décision–ordre–exécution–règlement et audit de faisabilité du mandat SPY–BIL.
- [x] Acquisition et audit d'une source OHLCV commune SPY–BIL, avec sauvegarde indépendante et contrôle du split BIL.
- [x] Contrôle croisé SPY contre Nasdaq et SPY/BIL contre NAV et premium/discount State Street.
- [x] Établissement d'une couverture commune auditée, sans la confondre avec une exécution garantie.
- [x] Définition d'un protocole hypothétique v1 et investigation reproductible des divergences d'ouverture.
- [x] Implémentation et validation sur cas artificiels d'un registre minimal trade date/settlement date.
- [x] Durcissement temporel du registre, 45 tests artificiels et concordance documentaire des 2 210 dates de séance.
- [x] Matrice des décisions finales, contrat d'intégration stricte et délimitation documentaire du règlement DTC/NSCC.
- [x] Proposition d'un mandat expérimental v1 et d'une convention de financement permettant les rééquilibrages sous conditions explicites.
- [x] Adaptateur minimal décision–ordres–registre strict, avec 69 tests artificiels et traçabilité du financement.
- [x] Frontière JSON synthétique v1, intentions liées à leur contenu, rejeu reproductible et refus persistant des doubles traitements, avec 93 tests artificiels.
- [x] Référentiel point-in-time, fiche candidate v1 et contrôle descriptif minimal de quelques observations réelles, verdict `PARTIALLY_VERIFIED`.
- [x] Premier contrôle d'intégration historique préspécifié du 28 au 30 mai 2024, avec intention figée, règlement T+1 ciblé et invariants comptables.
- [x] Conception méthodologique des références classiques SPY, BIL, 50/50 conservé/rééquilibré et calibrage déterministe du risque, sans exécution.
- [x] Première évaluation exploratoire appariée de A, B et C1 sur un épisode d'un an, avec distributions en cash et aucune décision après l'achat initial.
- [x] Validation des 251 séances, des 16 distributions, des richesses terminales et de la sensibilité préspécifiée S0–S3, avec rejet atomique de B sous S3.
- [ ] Approbation de Yahoo `Open` comme référence conventionnelle, sans le confondre avec une exécution garantie.
- [ ] Complétion d'un calendrier officiel de règlement DTC/NSCC versionné 2018–2026 et résolution du cas SPY du 20 avril 2026.
- [ ] Validation des références classiques avant toute méthode RL.
- [ ] Autorisation explicite d'une première expérience.

## Questions prioritaires à discuter

1. Valide-t-on le gestionnaire proposé, la fréquence hebdomadaire après clôture, l'exécution à l'ouverture suivante et l'horizon d'un an ?
2. Le budget de volatilité doit-il être une contrainte ex ante, une cible ou seulement un indicateur ?
3. Quelle richesse initiale et quelles règles de parts entières, de courtier, de règlement et de fiscalité représentent le mandat ?
4. Approuve-t-on Yahoo `Open` comme référence hypothétique conditionnelle, et faut-il acquérir la source officielle permettant de résoudre le 20 avril 2026 ?
5. Quelle convention de financement faut-il retenir : cash réglé conservateur ou compensation des flux au même règlement (`H-FIN-NET`) ?
6. Quelles règles simples devront être examinées avant que le RL puisse être jugé utile ?
7. Comment réserver une évaluation réellement non consultée alors que plusieurs périodes du projet principal ont déjà orienté la recherche ?

Le document [docs/CADRAGE_SCIENTIFIQUE.md](docs/CADRAGE_SCIENTIFIQUE.md) développe ces questions, les données candidates, les alternatives et les références examinées. L'étude [docs/PROBLEME_DECISION_SEQUENTIELLE.md](docs/PROBLEME_DECISION_SEQUENTIELLE.md) démontre quand les décisions se séparent période par période, quels mécanismes financiers créent une interdépendance et pourquoi ce besoin de contrôle ne suffit pas à justifier le RL. La proposition [docs/FORMALISATION_MANDAT_FINANCIER.md](docs/FORMALISATION_MANDAT_FINANCIER.md) décrit un gestionnaire stylisé et les flux d'un portefeuille actions–monétaire. Le [mandat opérationnel et audit de faisabilité SPY–BIL](docs/MANDAT_OPERATIONNEL_ET_FAISABILITE_SPY_BIL.md) précise le candidat principal, la chronologie, le registre nécessaire et les coûts. L'[audit des prix de marché](docs/AUDIT_PRIX_MARCHE_SPY_BIL.md) documente la source OHLCV commune, les ajustements, calendriers, anomalies, contrôles croisés et limites d'une future référence d'ouverture. Le [protocole d'exécution v1](docs/PROTOCOLE_EXECUTION_FINANCIERE_SPY_BIL_V1.md) formalise ensuite la chronologie, les quantités connues avant l'ouverture, le financement, le règlement, les coûts et les conditions de non-représentabilité. La [validation du registre synthétique](docs/VALIDATION_REGISTRE_COMPTABLE_SYNTHETIQUE.md) démontre ces transferts comptables sur des exemples artificiels, sans données de marché. Le notebook exécuté [EDA/01_reconstruction_rendements_totaux_SPY_BIL.ipynb](EDA/01_reconstruction_rendements_totaux_SPY_BIL.ipynb) conserve la reconstruction historique à l'ex-date. Les scripts [scripts/reconstruct_spy_payment_date_returns.py](scripts/reconstruct_spy_payment_date_returns.py) et [scripts/reconstruct_bil_payment_date_returns.py](scripts/reconstruct_bil_payment_date_returns.py) produisent séparément les comptabilités de détention à la date de paiement. Le rapport [docs/VALIDATION_RENDEMENTS_TOTAUX_SPY_BIL.md](docs/VALIDATION_RENDEMENTS_TOTAUX_SPY_BIL.md) précise les validations antérieures ; [docs/COHERENCE_COMPTABLE_SPY_BIL.md](docs/COHERENCE_COMPTABLE_SPY_BIL.md) établit le référentiel commun, documente l'anomalie BIL non résolue et sépare compatibilité NAV et exécution. L'[audit du patrimoine local](docs/AUDIT_DONNEES_ACADEMIQUES_LOCALES.md) conserve la traçabilité des fichiers bruts et des limites identifiées avant cette reconstruction.

## Règle d'arrêt

Aucun benchmark décisionnel, environnement, backtest ou choix d'algorithme ne découle automatiquement de ces audits. BIL-A, SPY-B et BIL-B sont `VALIDATED_FOR_USE` uniquement pour leurs analyses NAV et périodes documentées ; SPY-A reste `AUDITED`. SPY-B et BIL-B sont compatibles dans un même référentiel comptable de détention à partir du 4 mars 2008. Les OHLCV Yahoo sont des proxys conditionnels, pas des exécutions garanties. L'autorisation actuelle s'arrête à A, B et C1 sur l'épisode publié. Aucun second épisode, scénario de coûts, C2, règle D, environnement ou RL n'en découle. La prochaine étape devra être autorisée explicitement.
