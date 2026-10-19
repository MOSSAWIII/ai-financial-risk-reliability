# Axe de recherche — Reinforcement Learning et décisions financières sous incertitude

## Statut

Ce dossier ouvre un axe de recherche autonome au sein de `ai-financial-risk-reliability`. Il contient un cadrage scientifique, une étude fondamentale sur la nature séquentielle d'une décision, une formalisation financière, un audit de faisabilité d'un mandat SPY–BIL et un patrimoine local de données documentées. BIL-A reste validée sous la convention à l'ex-date. SPY-B et BIL-B suivent les parts, les créances et leur réinvestissement à la date de paiement. BIL-B est validée pour l'analyse NAV du 4 mars 2008 au 15 octobre 2026 ; sa frontière exclut explicitement la distribution du 3 mars 2008 dont les dates historiques restent incohérentes. Aucun algorithme de Reinforcement Learning (RL), modèle prédictif, environnement de simulation, stratégie ou backtest n'a été créé.

La priorité active est désormais : **valider séparément la comptabilité synthétique, le mandat et les données d'exécution avant toute expérience historique.** Les données brutes sont conservées localement sous `data/raw/`, exclues de GitHub et sauvegardées sur un disque physique distinct. Leur inventaire publiable se trouve dans [`data_manifest.json`](data_manifest.json), les contrôles reproductibles dans [`scripts/verify_local_data.py`](scripts/verify_local_data.py), et les résultats détaillés dans [`docs/AUDIT_DONNEES_ACADEMIQUES_LOCALES.md`](docs/AUDIT_DONNEES_ACADEMIQUES_LOCALES.md).

Le rapport [`docs/MANDAT_OPERATIONNEL_ET_FAISABILITE_SPY_BIL.md`](docs/MANDAT_OPERATIONNEL_ET_FAISABILITE_SPY_BIL.md) recommande, sans l'adopter, une poche SPY–BIL long-only et sans levier, révisée chaque semaine après clôture puis exécutée à l'ouverture suivante. L'[audit des prix de marché SPY–BIL](docs/AUDIT_PRIX_MARCHE_SPY_BIL.md) a depuis acquis une source Yahoo commune : 4 878 séances communes du 30 mai 2007 au 16 octobre 2026, dont 2 514 sur la fenêtre prioritaire d'octobre 2016 à octobre 2026. Les OHLCV sont cohérents structurellement et ajustés des splits, mais restent `AUDITED` : la définition exacte de l'ouverture et les conditions d'exécution ne sont pas suffisamment documentées, et aucun historique bid/ask n'est acquis.

Le [`protocole d'exécution financière hypothétique v1`](docs/PROTOCOLE_EXECUTION_FINANCIERE_SPY_BIL_V1.md) recommande désormais une convention strictement conditionnelle : quantités entières dimensionnées au close déjà connu, valorisation hypothétique au Yahoo `Open` de la prochaine séance admissible et comptes de règlement séparés. La fenêtre candidate post-split commence le 2 janvier 2018 et contient 2 210 séances communes. Le champ `Open` n'est pas assimilé à un fill ou au prix officiel de l'enchère; le 20 avril 2026 reste non représentable pour une transaction v1 en raison d'une divergence SPY non résolue. Le script [`scripts/audit_spy_open_divergences.py`](scripts/audit_spy_open_divergences.py) reproduit les 17 alertes d'ouverture sans corriger les sources.

Le [registre comptable synthétique](docs/VALIDATION_REGISTRE_COMPTABLE_SYNTHETIQUE.md) implémente désormais, sans aucune donnée historique, les positions économiques et réglées, cash, créances/dettes de règlement, distributions, frais et regroupements de parts. Ses 29 tests artificiels vérifient la conservation de richesse, l'atomicité des refus, T+2/T+1 sur calendriers fournis, le financement conservateur et l'hypothèse séparée `H-FIN-NET`. Ce composant n'est ni un simulateur de marché, ni un moteur de stratégie, ni une autorisation d'utiliser les historiques.

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
- [ ] Approbation de Yahoo `Open` comme référence conventionnelle, sans le confondre avec une exécution garantie.
- [ ] Acquisition d'un calendrier officiel versionné 2018–2026 et résolution du cas SPY du 20 avril 2026.
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

Aucun benchmark décisionnel, environnement, backtest ou choix d'algorithme ne découle automatiquement de ces audits. BIL-A, SPY-B et BIL-B sont `VALIDATED_FOR_USE` uniquement pour leurs analyses NAV et périodes documentées ; SPY-A reste `AUDITED`. SPY-B et BIL-B sont compatibles dans un même référentiel comptable de détention à partir du 4 mars 2008. Les OHLCV Yahoo sont `AUDITED` pour l'analyse descriptive des prix split-adjusted, pas validés comme exécutions garanties. Le protocole v1 est une spécification conditionnelle et le registre synthétique valide seulement des identités sur cas artificiels. Aucun des deux n'autorise un portefeuille, une simulation ou un backtest. Une expérience reste interdite tant que le mandat, le calendrier, le financement et la convention d'ouverture ne sont pas approuvés. La prochaine étape devra être autorisée explicitement.
