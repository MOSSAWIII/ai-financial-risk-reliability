# Prérequis d'une expérience financière contrôlée SPY–BIL

Date : 20 octobre 2026

Point de départ : `ef3ca1018bf25fcf98c23ec1dddec69073b7ecd0`

## 1. Conclusion

Le projet dispose désormais d'un registre comptable strict, de prix quotidiens
audités, d'une chronologie d'exécution conditionnelle et d'un calendrier de
négociation concordant sur 2 210 séances. Il ne dispose toujours pas d'une archive
annuelle exhaustive des jours de règlement DTC/NSCC pour 2018–2026.

Cette lacune n'interdit pas de préparer l'expérience. Elle interdit en revanche de
fabriquer un calendrier complet par analogie. La voie défendable est de valider les
dates de règlement effectivement requises, de rendre toute date incertaine non
représentable et de mesurer cette indisponibilité sans la transformer en décision de
portefeuille.

Verdict : **`PARTIALLY_READY`**. Les décisions finales peuvent être soumises au
porteur du projet, mais l'intégration historique devra rester limitée aux dates de
règlement documentées jusqu'à constitution d'un calendrier versionné suffisant.

## 2. Prérequis déjà satisfaits

| Élément | État démontré | Limite persistante |
|---|---|---|
| Registre | mode strict, calendriers séparés, ordre journalier, atomicité; 45 tests artificiels | ce n'est pas un compte de courtier |
| Négociation | 2 210 séances communes SPY–BIL concordantes avec les règles NYSE | horaires historiques 2018–2021 non exhaustifs |
| Prix | OHLCV Yahoo audités, parts BIL homogènes après le split | `Open` est une référence conventionnelle, pas un fill |
| Ouverture | protocole décision au close puis quantité figée avant l'open | SPY 2026-04-20 reste contesté |
| Distributions | ex-date, créance et paiement séparés | source événementielle à figer pour l'intégration |
| Règlement | T+2 puis T+1 contrôlés par calendrier | dates DTC/NSCC historiques incomplètes |
| Conservation | manifeste, SHA-256, sauvegarde physique | droits de redistribution propres à chaque source |

Les séries NAV validées restent des références comptables et de contrôle. Elles ne
sont pas des prix de transaction.

## 3. Calendrier de règlement DTC/NSCC

### 3.1 Ce que les sources établissent

- La SEC impose le cycle standard T+2 sur la première partie de la fenêtre, puis
  T+1 à compter du 28 mai 2024 ([SEC 34-96930](https://www.sec.gov/files/rules/final/2023/34-96930.pdf)).
- DTC réalise le transfert final des titres et des fonds; NSCC/CNS calcule et
  transmet les obligations nettes. Le règlement monétaire utilise les banques de
  règlement et le National Settlement Service de la Réserve fédérale
  ([DTCC Settlement](https://www.dtcc.com/clearing-and-settlement-services/settlement),
  [DTCC CNS](https://www.dtcc.com/products-and-services/clearing-settlement-services/equities-clearing/cns)).
- La Rule 25 de DTC prévoit que les jours d'ouverture sont définis par les
  procédures et qu'une instruction portant sur un jour fermé est reportée au
  prochain jour d'ouverture. La simple qualité de jour ouvré civil ne suffit donc
  pas ([règles DTC](https://www.dtcc.com/-/media/Files/Downloads/legal/rules/dtc_rules.pdf)).
- Le document opérationnel TradeSuite 2025 indique qu'un confirm DTC-éligible ne
  peut avoir pour settlement date ni les jours fériés réguliers, ni Columbus Day,
  Veterans Day ou Good Friday. Il distingue en même temps confirmation et
  règlement : du traitement peut continuer un jour qui reste inadmissible au
  règlement ([DTCC TradeSuite](https://files.dtcc.com/download/assets/Holiday-Processing-B1P3.pdf/1d95076e8f8711f18ff132b7a3250aba)).
- L'avis NSCC Columbus Day 2018 déclare NSCC ouvert pour recevoir et traiter des
  trades, tout en précisant que le 8 octobre n'est pas une settlement date et que
  les services de livraison/règlement sont fermés. « NSCC open » ne prouve donc pas
  le règlement ([avis A8612](https://www.dtcc.com/-/media/Files/pdf/2018/9/17/a8612-18.pdf)).
- Lors d'une fermeture imprévue des marchés, DTCC vise au contraire la continuité
  si banques et Fedwire restent ouverts. Le guide cite les précédents des journées
  de deuil; les avis du 5 décembre 2018 et du 9 janvier 2025 confirment que le
  règlement a continué ([guide DTCC](https://www.dtcc.com/-/media/Files/Downloads/issues/Unscheduled_Close.pdf),
  [avis DTC 10142-18](https://www.dtcc.com/-/media/Files/pdf/2018/12/3/10142-18.pdf),
  [avis NSCC A9545](https://www.dtcc.com/-/media/Files/pdf/2025/1/8/a9545.pdf)).

Ces preuves établissent une différence réelle entre :

1. séance de négociation ;
2. traitement ou confirmation par NSCC/ITP ;
3. règlement CNS/DTC de titres et de cash ;
4. disponibilité des banques et de Fedwire.

### 3.2 Corpus local ajouté

Quatre PDF DTCC ont été acquis le 20 octobre 2026 et inscrits au manifeste :

- règles DTC au 28 avril 2026 ;
- règles et procédures NSCC au 21 septembre 2026 ;
- fiche TradeSuite de traitement des jours fériés, codée octobre 2025 ;
- guide DTCC des fermetures imprévues du 6 mars 2026.

Les copies brutes restent exclues de GitHub et sont sauvegardées sous
`D:\ai-financial-risk-reliability-data-backup\2026-10-20\` avec quatre empreintes
SHA-256 concordantes.

### 3.3 Couverture réellement défendable

| Catégorie | Conclusion | Niveau de preuve |
|---|---|---|
| week-end | non admissible | règle opérationnelle stable |
| jours fériés réguliers DTC | non admissibles | procédure DTCC courante; dates NYSE 2022–2026 acquises/vérifiées |
| Columbus Day, Veterans Day | marché souvent ouvert, règlement non admissible | procédure courante + avis historiques ponctuels |
| Good Friday | marché fermé; pas de settlement date pour les confirms DTC-éligibles visés par TradeSuite, malgré certains services DTC limités | procédure courante; détails par service variables |
| séances écourtées | séances et jours de règlement ordinaires sauf avis contraire | calendriers NYSE; aucune fermeture DTC déduite de l'heure réduite |
| deuils 2018 et 2025 | marché fermé mais règlement maintenu | avis DTCC spécifiques |
| fermeture imprévue future | décision selon banques, Fedwire et avis DTCC du jour | guide de continuité, non règle automatique |

### 3.4 Lacunes et conséquence

Il manque un ensemble figé et exhaustif des avis DTC/NSCC propres à chaque jour
férié de 2018 à 2026. Les règles consolidées acquises en 2026 et la fiche
opérationnelle publiée en 2025 ne prouvent pas à elles seules l'absence de variation
historique. Certains avis décrivent aussi des restrictions différentes selon CNS,
DTC, ACATS, ETF create/redeem ou autres services.

Aucune sous-fenêtre continue de 2018–2026 n'est donc déclarée exhaustive. Les
documents 2025–2026 rendent les catégories courantes mieux défendables pour cette
période, mais ils ne remplacent pas les avis annuels et exceptionnels applicables à
chaque date effectivement sollicitée.

Aucun fichier de calendrier dérivé n'est donc publié dans cette phase. Pour la
future expérience :

- seules les dates appuyées par une règle historique ou un avis applicable pourront
  entrer dans `SyntheticSettlementCalendar` ;
- une date douteuse ne sera ni ajoutée ni simplement sautée, car les deux choix
  modifieraient artificiellement l'échéance ;
- toute transaction dont le calcul T+n rencontre une date non qualifiée recevra
  `CALENDAR_UNVERIFIED` avant mutation du registre ;
- les avis nécessaires pourront être acquis de manière ciblée pour les seules
  dates effectivement sollicitées, sans prétendre reconstituer inutilement tous les
  services DTCC.

## 4. Décisions méthodologiques à approuver

| Décision | Alternatives raisonnables | Conséquence | Recommandation pour une première étude |
|---|---|---|---|
| Financement | cash réglé conservateur / `H_FIN_NET` | le premier peut refuser un rééquilibrage croisé; le second suppose une compensation autorisée | **conservateur en principal**; `H_FIN_NET` seulement comme variante préspécifiée après preuve contractuelle |
| Prix de transaction | Yahoo `Open` / enchère officielle ou quotes | Yahoo couvre la fenêtre mais ne garantit aucun fill | Yahoo `Open` comme **référence hypothétique conditionnelle**, jamais comme exécution observée |
| SPY 2026-04-20 | choisir un fournisseur / corriger / déclarer indisponible | tout choix ex post serait opportuniste | `PRICE_DISPUTED`; ne pas corriger ni supprimer la date |
| Parts | entières / fractionnaires | richesse et arrondis changent les actions accessibles | parts entières; fractions seulement après preuve de courtier |
| Richesse initiale | montant unique / grille de sensibilité | change quantités, cash résiduel et faisabilité | montant économique fixé avant résultats + grille préspécifiée; aucun choix sur performance |
| Coûts | zéro externe / scénarios / estimation empirique | distingue identité comptable, robustesse et réalisme | cas théorique sans coût externe, puis sensibilités explicitement hypothétiques; aucune calibration sans quotes/barème |
| Compte et fiscalité | compte imposable / enveloppe / compte de recherche neutre | fiscalité et restrictions diffèrent | compte de recherche USD, cash, non margé et fiscalement neutre; « fiscalité exclue », jamais « fiscalité universellement nulle » |
| Cash | résiduel non rémunéré / rémunéré | peut devenir un troisième actif | résiduel non rémunéré jusqu'à convention approuvée |
| Budget de risque | contrainte / cible / indicateur | une contrainte change l'ensemble des actions; une cible change l'objectif | indicateur dans la première expérience; contrainte seulement après justification et seuil fixé ex ante |
| Fréquence et horizon | quotidien/hebdomadaire/mensuel; horizon variable | turnover, nombre de décisions et sens économique diffèrent | hebdomadaire après clôture, ouverture suivante, horizon d'un an, sous réserve d'approbation |

Le choix conservateur de financement ne prétend pas reproduire un courtier. Il
évite d'accorder implicitement un crédit ou un netting non documenté. Les refus qu'il
engendre devront rester visibles et ne pourront être redimensionnés après observation
de l'ouverture.

Concrètement, `CONSERVATIVE_SETTLED_CASH` exige le cash déjà réglé avant un achat et
les titres déjà réglés avant une vente. Il peut donc refuser un rééquilibrage croisé
présenté au même open lorsque l'achat dépend du produit encore non réglé de la vente.
`H_FIN_NET` autorise la compensation définie par le registre entre les jambes du
rééquilibrage; son usage comme représentation économique exigerait toutefois une
preuve du contrat de compte, des délais de disponibilité et des droits de netting. La
capacité logicielle du registre ne constitue pas cette preuve.

## 5. Contrat d'intégration historique

La future voie d'intégration devra être une frontière étroite : données auditées →
événements datés → registre strict. Elle devra refuser l'entrée avant toute mutation
si l'un des champs ou contrôles suivants manque.

### 5.1 Entrées minimales

| Groupe | Champs requis |
|---|---|
| Provenance | identifiant de manifeste, chemin, SHA-256, version du calendrier, statut d'usage |
| Décision | date et instant de décision, information disponible, close connu, quantité figée |
| Transaction | prochaine séance commune, Yahoo `Open`, statut d'anomalie, quantité inchangée |
| Règlement | régime T+2/T+1, source des jours admissibles, settlement date calculée |
| Événements | knowledge date, ex-date, payment date, montant, splits et source |
| Compte | richesse initiale, parts entières, financement, cash, coûts et fiscalité |

### 5.2 Garde-fous obligatoires

1. Construire exclusivement `SyntheticPortfolioLedger(..., strict_temporal=True,
   trading_calendar=..., settlement_calendar=...)`.
2. L'entrée future devra affirmer `ledger.strict_temporal is True`; aucune branche
   de compatibilité ne sera exposée par l'adaptateur.
3. Le close de décision doit précéder strictement la trade date; l'open ne peut
   jamais redimensionner l'ordre.
4. Trade date et price date doivent être la même séance négociable.
5. La settlement date doit être calculée par le calendrier documenté, jamais fournie
   comme vérité libre par la donnée source.
6. Aucun prix manquant, nul, corrigé, interpolé ou rétroajusté silencieusement.
7. Une NAV ne peut être utilisée comme prix de transaction.
8. Distributions et splits doivent être des événements sourcés et appliqués une fois.
9. Toute anomalie, règle contractuelle absente ou date calendaire incertaine doit
   être classée avant appel au registre.
10. Le snapshot financier avant un refus doit égaler le snapshot après refus.

Le code actuel satisfait déjà les contrôles ciblés de mode strict, chronologie des
annonces, obligations échues, phases de même date et atomicité. Aucun défaut nouveau
reproductible n'a été trouvé; le registre n'est donc pas modifié dans cette phase.

## 6. Non-représentabilité

### 6.1 Classification minimale

| Code | Nature | Exemple |
|---|---|---|
| `PRICE_MISSING_OR_DISPUTED` | échec de donnée | open absent ou SPY 2026-04-20 |
| `CALENDAR_UNVERIFIED` | échec documentaire | jour T+n sans preuve DTC/NSCC suffisante |
| `EVENT_UNDOCUMENTED` | échec documentaire | distribution ou split sans dates fiables |
| `CONTRACT_UNAPPROVED` | hypothèse non autorisée | netting ou fractions sans règle de compte |
| `FUNDING_INFEASIBLE` | infaisabilité économique modélisée | cash réglé insuffisant après gap |
| `DELIVERY_INFEASIBLE` | infaisabilité économique modélisée | titres non livrables à l'échéance |
| `INPUT_INVALID` | violation technique | prix non positif, quantité fractionnaire interdite |

### 6.2 Traitement déterministe

- Toujours conserver l'intention de décision, les ordres envisagés, l'état avant
  exécution, le code, la cause et la source documentaire.
- Les quatre premières classes empêchent de connaître une transition financière :
  la trajectoire est **non évaluable à partir de cet instant**. Elles ne deviennent
  ni une conservation de position, ni un passage au cash, ni une observation retirée.
- `FUNDING_INFEASIBLE` et `DELIVERY_INFEASIBLE` sont des rejets du modèle de compte
  approuvé. Le registre reste inchangé par atomicité, mais le résultat est étiqueté
  « ordre rejeté », pas « décision de conserver ».
- `INPUT_INVALID` arrête l'exécution comme erreur de protocole.
- Aucune politique de remplacement, réduction de quantité ou fournisseur préféré
  ne peut être choisie après observation des résultats.

Les futurs rapports devront publier séparément : nombre d'intentions, exécutions,
rejets économiques, trajectoires interrompues par données, causes et dates. Aucun
seuil d'acceptabilité n'est fixé ici; il devra être préenregistré.

## 7. Conditions minimales d'une première expérience

### Investisseur et décision

Un gestionnaire stylisé administre une poche USD autonome, non margée, fiscalement
neutre, sans passif externe. À la dernière clôture commune de la semaine, il choisit
une exposition cible SPY/BIL long-only; les quantités entières sont déterminées avec
le close alors connu et présentées à l'ouverture commune suivante.

### Information disponible

Uniquement les observations publiées au plus tard à la décision, avec leurs délais
et révisions documentés. Aucun open futur, NAV future, distribution non annoncée ou
état révisé ultérieurement n'entre dans la décision.

### Contraintes et horizon

- SPY et BIL uniquement, positions non négatives, aucun levier ou emprunt ;
- cash résiduel non rémunéré ;
- financement conservateur en principal ;
- ordre entier figé avant l'ouverture ;
- horizon économique candidat d'un an et fréquence hebdomadaire ;
- arrêt documentaire selon la classification précédente.

### Objectif, contraintes et mesures

- **Objectif économique** : croissance de la richesse de marché nette des coûts
  reconnus sur l'horizon.
- **Contraintes** : long-only, autofinancement, calendrier, information disponible,
  instruments et ordre des événements.
- **Mesures descriptives** : rendement brut/net selon couche de coûts, volatilité,
  drawdown et durée, turnover, coûts, cash résiduel, écarts à la cible, rejets et
  non-représentabilité.
- **Indicateur de risque** : dépassement d'un budget éventuel, sans seuil choisi ici.

Avant toute méthode RL, les mêmes entrées et comptes devront être appliqués à des
références simples : détention SPY, détention BIL, allocation fixe avec la même règle
de rééquilibrage, règle déterministe sans apprentissage et, si justifié, ciblage de
volatilité classique. Aucune de ces références n'est exécutée dans cette phase.

## 8. Décisions requises et prochaine étape minimale

Le porteur doit approuver explicitement :

1. investisseur stylisé et compte fiscalement neutre non margé ;
2. financement conservateur principal et statut éventuel de `H_FIN_NET` ;
3. Yahoo `Open` comme référence hypothétique conditionnelle ;
4. traitement `PRICE_MISSING_OR_DISPUTED` du 20 avril 2026 ;
5. parts entières, richesse initiale ou grille fixée ex ante ;
6. couches de coûts autorisées ;
7. cash résiduel non rémunéré ;
8. budget de risque comme indicateur ou contrainte ;
9. fréquence hebdomadaire et horizon d'un an ;
10. politique d'arrêt et seuil acceptable de non-représentabilité ;
11. niveau de preuve exigé pour chaque settlement date.

Après ces décisions seulement, la prochaine étape minimale serait de constituer le
calendrier versionné des dates de règlement nécessaires, avec chaque fermeture et
exception reliée à une source primaire, puis de tester un adaptateur d'intégration
sur données artificielles. Elle ne doit encore produire aucune performance.

## 9. Limites obligatoires des futurs résultats

Tout résultat futur devra rappeler que Yahoo `Open` n'est pas un fill, que le compte
et le financement sont stylisés, que la fiscalité est exclue, que les coûts sans
quotes sont hypothétiques, que l'impact et les fills partiels ne sont pas observés,
que le calendrier peut limiter la couverture, que les chemins interrompus ne sont
pas des non-investissements et que les résultats historiques ne démontrent ni
causalité, ni robustesse hors échantillon, ni supériorité d'une méthode RL.

La présente phase n'autorise aucune intégration, simulation ou expérience financière.
