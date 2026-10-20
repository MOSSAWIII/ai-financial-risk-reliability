# Validation synthétique du rééquilibrage C2

**Périmètre :** données, prix, calendriers, distributions et disponibilités entièrement artificiels
**Politique :** cible 50 % SPY / 50 % BIL, décisions successives
**Verdict :** `SYNTHETIC_C2_VALIDATED`

## 1. Question économique

C2 doit ramener périodiquement un portefeuille hérité vers 50 % SPY et 50 % BIL sans réinitialiser son capital. Une décision dépend donc des positions et flux produits par les cycles antérieurs. La difficulté nouvelle n'est pas le calcul du poids, mais la distinction entre ce qui s'est économiquement produit, ce qui était connaissable à 08:00 ET et ce qui pouvait effectivement financer le lot suivant.

Cette phase valide uniquement cette mécanique sur des scénarios artificiels. Elle ne charge aucun historique Yahoo, ne produit aucune performance C2 et ne compare pas C1 à C2.

## 2. Trois états distincts

Le mécanisme conserve trois vues explicitement séparées.

1. **État économique réalisé.** Positions économiques, cash, créances et dettes de règlement, créances de distribution, frais et paiements effectivement enregistrés dans `SyntheticPortfolioLedger`.
2. **État informationnel.** `DecisionSnapshot` ne révèle que les closes et événements dont la disponibilité est prouvée au plus tard à l'instant exact de décision.
3. **État de financement.** Positions réglées, cash réglé, dettes et produits de règlement, dates de dénouement et frais du lot. Le registre applique ensuite `H_FIN_NET` ; une créance de distribution n'est jamais assimilée à du cash.

La richesse économique peut donc différer de la richesse admissible. Cette différence est visible dans l'instantané et ne conduit ni à modifier le registre ni à imputer silencieusement zéro à une information inconnue.

## 3. Contrat `DecisionSnapshot`

L'instantané immuable contient :

- `decision_at`, obligatoirement 08:00 `America/New_York` lors d'une séance artificielle ;
- la dernière séance antérieure et les closes SPY/BIL admissibles ;
- l'instant de disponibilité de chaque close ;
- positions économiques et positions réglées ;
- cash réglé dont la disponibilité est prouvée, ventes à recevoir et achats à payer ;
- créances connues ; le total économique n'est affiché que s'il ne révèle aucune information interdite ;
- identifiants des créances de montant non démontré comme connu ;
- identifiants des paiements dont la disponibilité du cash n'est pas prouvée ;
- richesse économique seulement si elle est informationnellement publiable, richesse admissible éventuelle et ressources de financement ;
- version monotone du registre ;
- statut global `READY` ou `NOT_EVALUABLE`, motif et provenance champ par champ.

Les provenances obligatoires couvrent séparément les deux closes, les calendriers de négociation et de règlement, les positions économiques et réglées, le cash, les règlements en attente et les distributions.

### Règles de disponibilité

| Champ | Règle stricte |
|---|---|
| Close SPY/BIL | dernière séance antérieure ; `available_at <= decision_at` |
| Positions économiques/réglées | état courant du registre, sans événement postérieur |
| Cash et règlements | événements dus déjà traités ; flux propres au portefeuille connus |
| Créance annoncée | annonce artificielle prouvée avant la décision ; le même jour exige un instant exact |
| Créance réalisée non annoncée | montant masqué à la politique ; richesse exacte `NOT_EVALUABLE` |
| Cash de distribution | utilisable seulement si `cash_available_at <= decision_at` |
| Paiement daté du jour | la date seule ne prouve pas une disponibilité avant 08:00 |

Une créance inconnue n'est jamais estimée et n'est jamais remplacée par zéro. Si elle est nécessaire au calcul exact du 50/50, `admissible_wealth=None` et aucune intention ne peut être scellée.

Le registre conserve toujours les montants économiques exacts. En revanche, si une créance ou un paiement n'est pas admissible, le snapshot remet `economic_distribution_receivables` et `economic_wealth` à `None`, retranche du cash visible tout paiement non prouvé et ne publie que les identifiants bloquants. La politique ne peut donc pas inférer le montant caché par différence.

## 4. Articulation avec l'adaptateur

`SyntheticDecisionAdapter.build_decision_snapshot()` construit la frontière informationnelle. `prepare_intent_from_snapshot()` accepte uniquement un instantané `READY`, encore identique à la version courante du registre, puis calcule :

\[
q_{SPY}=\left\lfloor\frac{0,5W_d}{P_{SPY,d}^{close}}\right\rfloor,
\qquad
q_{BIL}=\left\lfloor\frac{0,5W_d}{P_{BIL,d}^{close}}\right\rfloor.
\]

Les ordres sont les différences entre ces quantités cibles et les positions économiques héritées. L'intention contient l'instant de décision, l'identifiant de l'instantané et la version du registre dans son empreinte. Une mutation entre l'instantané et l'open rend l'intention périmée avant toute transaction.

Le chemin historique antérieur `prepare_intent()` reste inchangé et continue de refuser toute décision postérieure à `EX_POST_ACCOUNTING_ONLY`.

## 5. Séparation minimale de la comptabilité ex post

Le blocage de sécurité n'a pas été supprimé. Une transaction après une distribution réalisée ex post reste interdite par défaut, y compris via un appel direct au registre.

La seule exception est une autorisation interne à usage unique, créée par l'adaptateur après validation d'un instantané scellé et à jour. Elle permet au registre économique de conserver la vraie créance ou son paiement tout en empêchant le montant inconnu de contaminer la politique. L'autorisation est consommée par le lot accepté ou rejeté.

Les créances portent maintenant deux métadonnées minimales :

- mode informationnel (`ANNOUNCED`, `REALIZED_EX_POST` ou ancien mode) ;
- instant prouvé de disponibilité du cash après paiement, lorsqu'il existe.

Une annonce peut aussi porter un instant exact de connaissance. Aucune date d'annonce n'est inventée.

## 6. Chronologie d'un cycle

Chaque cycle artificiel suit cet ordre : événements économiques dus, règlements, instantané à 08:00 ET, contrôle documentaire, calcul et scellement des quantités, lecture des opens, calcul des frais, exécution/hold/rejet atomique, puis transmission de l'état inchangé ou modifié au cycle suivant.

Le `price_date` reste la dernière séance close ; `decision_at` est 08:00 ET à la séance suivante et l'exécution hypothétique utilise l'open de cette même séance. Les deux temps sont distincts dans l'intention scellée.

## 7. Scénario principal à décisions successives

Le calendrier artificiel contient des séances espacées par week-ends, un jour non négociable et des dates de règlement distinctes.

| Cycle | Closes SPY/BIL | Positions héritées | Cibles | Ordres | Résultat |
|---|---:|---:|---:|---|---|
| Initial | 100 / 100 | 0 / 0 | 500 / 500 | +500 / +500 | exécuté, puis réglé |
| Dérive SPY positive | 120 / 100 | 500 / 500 | 458 / 550 | -42 SPY / +50 BIL | exécuté sous `H_FIN_NET` |
| Dérive inverse | 80 / 100 | 458 / 550 | 573 / 458 | +115 SPY / -92 BIL | exécuté sous `H_FIN_NET` |
| Équilibre exact | 458 / 573 | 573 / 458 | 573 / 458 | aucun | `VOLUNTARY_HOLD` |

Le cash final intermédiaire de 40 USD est hérité ; aucun cycle ne réinitialise 100 000 USD. Le hold ne crée ni ordre, ni règlement, ni frais.

## 8. Ventes, achats, règlements et `H_FIN_NET`

Les tests confirment :

- vente limitée aux positions réglées et intégralement payées ;
- aucun short, emprunt ou découvert ;
- vente et achat du même lot atomiques ;
- produit de vente utilisable seulement lorsque sa date de règlement est compatible avec l'achat ;
- frais inclus dans le besoin de financement ;
- cash projeté non négatif ;
- titres achetés non revendables avant règlement ;
- conservation intégrale des règlements antérieurs après un rejet.

Lors du premier rééquilibrage, les 42 SPY vendus financent les 50 BIL achetés à la même échéance. Les positions économiques deviennent immédiatement 458/550, tandis que les positions réglées restent 500/500 jusqu'au règlement. Cette convention demeure une hypothèse stylisée de compte cash, non une règle universelle de courtier.

## 9. Rejets et état hérité

Avec 495 SPY et 495 BIL réglés, un open BIL artificiellement porté de 100 à 200 rend le lot figé impossible à financer. Le lot entier est rejeté : aucune jambe n'est exécutée, aucun frais n'est reconnu, les positions restent 495/495 et aucune obligation de règlement n'apparaît.

La décision suivante hérite exactement de 495/495 et peut produire un nouveau lot 563/450. Le rejet antérieur et les marques de prix restent au journal ; rien n'est effacé ou reconstruit depuis l'état terminal.

## 10. Distributions point-in-time

### Annonce prouvée

Une annonce artificielle horodatée avant l'ex-date produit une créance SPY de 1 000 USD sur 500 parts. À la décision suivante, richesse économique et richesse admissible valent 101 000 USD. Les ressources de financement restent nulles : la créance n'est pas du cash.

### Réalisation non annoncée

La même créance enregistrée par `accrue_realized_distribution()` existe avec son montant exact dans le registre économique, mais l'instantané expose seulement son identifiant à la politique. Les montants économique et admissible y sont expurgés (`None`). Le statut est `NOT_EVALUABLE`; aucune quantité 50/50 n'est calculée.

### Paiement prouvé

Un paiement artificiel effectué un samedi est comptabilisé ce samedi sans créer de séance. Si `cash_available_at` est prouvé avant la décision du lundi à 08:00, les 1 000 USD rejoignent le cash et peuvent financer la décision. Une transaction postérieure devient alors possible via l'instantané strict.

### Paiement du jour

Un paiement daté du lundi mais crédité artificiellement à 09:00 n'est pas disponible pour la décision de 08:00. L'instantané est `NOT_EVALUABLE`. La date civile seule ne suffit donc pas.

## 11. Coûts S0–S3

`cost_scenario_fees()` accepte exclusivement 0, 1, 5 ou 10 pb. Pour chaque ordre d'achat **ou de vente**, le coût est `abs(quantité) × open × pb / 10 000`. Les quantités sont déjà scellées et ne changent jamais après lecture des opens.

Sur un achat initial artificiel de 495 SPY et 495 BIL à 100 USD :

| Scénario | Notionnel négocié | Frais | Statut |
|---|---:|---:|---|
| S0 | 99 000 USD | 0 USD | exécuté |
| S1 | 99 000 USD | 9,90 USD | exécuté |
| S2 | 99 000 USD | 49,50 USD | exécuté |
| S3 | 99 000 USD | 99,00 USD | exécuté |

Deux cycles sous S1 cumulent exactement 10,896 USD : 9,90 USD à l'achat initial puis 0,996 USD sur la vente SPY et l'achat BIL. Le règlement ne déduit pas les frais une seconde fois. Un hold sous S3 coûte zéro.

Avec des cibles initiales de 500/500 à des opens de 100, S3 exige 100 USD au-delà du notionnel de 100 000 USD : le lot est rejeté sans passer à 499 parts.

Un second cas commence par un lot S3 exécuté de 495/495, puis construit un rééquilibrage qui serait couvert avant friction mais ne l'est plus après les frais cumulés. Le rejet conserve 495/495, les règlements restent vides et les 99 USD déjà payés ne sont ni annulés ni déduits une seconde fois.

## 12. Invariants et absence de fuite

Les tests vérifient à chaque branche :

- identité `positions réglées + quantités en attente = positions économiques` ;
- cash, créances et dettes non négatifs ;
- richesse modifiée une seule fois par les frais ;
- paiement de créance neutre pour la richesse ;
- intention immuable et liée par SHA-256 à son instantané ;
- version du registre inchangée entre snapshot et open ;
- closes disponibles avant la décision et opens lus seulement après scellement ;
- aucune réécriture d'intention et aucune reconstruction depuis le futur ;
- reproductibilité binaire d'un même instantané artificiel.

Une close dont la disponibilité est postérieure à 08:00, une créance inconnue, un cash non prouvé, un événement futur ou un événement dû non traité rendent le snapshot `NOT_EVALUABLE`.

## 13. Modifications minimales

Deux composants existants seulement sont étendus :

- `synthetic_portfolio_ledger.py` : métadonnées informationnelles des distributions, preuve facultative de disponibilité du cash et autorisation interne à usage unique ;
- `synthetic_decision_adapter.py` : `DecisionSnapshot`, construction point-in-time, scellement depuis snapshot, contrôle de péremption et coûts S0–S3.

Aucun moteur d'événements, framework de backtest, nouvelle couche de simulation ou composant historique C2 n'est créé. Le défaut corrigé est l'impossibilité de distinguer une créance économiquement connue du registre d'une créance admissible à la décision.

## 14. Tests artificiels

Dix-sept tests déterministes couvrent : décisions successives, deux dérives et hold, richesse héritée, positions économiques/réglées, close future, annonce admissible, réalisation non annoncée, paiement prouvé ou trop tardif, paiement hors séance, vente–achat `H_FIN_NET`, rejet par gap, décision après rejet, S0–S3, cumul et unicité des frais, rejet initial et rejet ultérieur par frais, conservation de l'état, absence de redimensionnement, péremption et reproductibilité.

Ils utilisent uniquement les constantes définies dans le fichier de test. Aucun fichier du manifeste ou historique de marché n'est lu.

## 15. Limites et preuves nécessaires à C2 historique

La période historique candidate demeure strictement le 29 mai 2024–29 mai 2025. Avant toute exécution, il faudra fournir :

1. la liste préspécifiée des dernières clôtures communes hebdomadaires et séances d'exécution suivantes ;
2. la preuve de disponibilité de chaque close avant 08:00 ET et la qualification des opens Yahoo comme proxys admissibles ;
3. le calendrier DTC/NSCC applicable à chaque lot, pas seulement au premier achat ;
4. pour chaque distribution, ex-date, record date, payment date, montant et date/instant de connaissance démontré ;
5. pour chaque paiement utilisé, une convention documentée de disponibilité du cash avant la décision ;
6. une convention préspécifiée pour les créances sans annonce historique — le comportement strict actuel est `NOT_EVALUABLE` ;
7. la vérification ciblée des anomalies de prix sur toutes les dates C2 ;
8. les conditions de financement et de règlement de chaque vente–achat ;
9. le traitement préspécifié des gaps, rejets atomiques et positions héritées ;
10. l'application identique de S0–S3 à C1 et C2 lorsqu'un ordre existe ;
11. la convention terminale pour les ordres, règlements, paiements et créances proches du 29 mai 2025.

La validation artificielle ne prouve aucun de ces faits historiques. L'absence actuelle de dates d'annonce historiques et d'un calendrier de règlement exhaustif pour tous les lots reste bloquante.

## 16. Prochaine étape minimale

Construire, sans lancer de transaction, la grille documentaire ciblée des seules décisions hebdomadaires candidates de l'épisode : close, décision, open, règlement, distributions connues et anomalies. Chaque ligne devra recevoir un statut `READY` ou un motif `NOT_EVALUABLE`. Une exécution historique C2 ne pourra être autorisée qu'après validation complète de cette grille et approbation explicite de la convention applicable aux créances sans annonce.

La mécanique synthétique nécessaire à cette future étude est validée ; la faisabilité historique ne l'est pas.
