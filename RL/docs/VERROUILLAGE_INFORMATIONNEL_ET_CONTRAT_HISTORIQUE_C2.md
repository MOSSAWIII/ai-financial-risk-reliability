# Verrouillage informationnel et contrat historique C2

Date de verrouillage : 21 octobre 2026  
Point de départ : `ffbb85e29734b21e92e7713d9b9829b7e75b06f9`  
Périmètre : préparation technique C1–C2, sans exécution historique C2

## 1. Verdict

**`HISTORICAL_C2_TECHNICALLY_READY`**

La frontière informationnelle E-B est désormais étanche au niveau de l'objet remis à la politique, de sa sérialisation canonique, de son identifiant et de l'intention scellée. Le registre conserve séparément toute l'information économique rétrospective. Les contrôles synthétiques, le protocole strict S et l'audit documentaire ciblé passent. Ce verdict autorise techniquement une future exécution de l'unique épisode préspécifié, mais ne constitue ni son lancement, ni un résultat C2, ni une comparaison empirique C1–C2.

## 2. Vulnérabilité corrigée

Le précédent `DecisionSnapshot` mélangeait la vue de politique et l'audit. Son contenu canonique incluait notamment `economic_distribution_receivables`, `economic_wealth`, `excluded_distribution_claims` et `unavailable_paid_cash`. Un montant de créance inconnu pouvait donc modifier `decision_snapshot_payload()`, son SHA-256 et `snapshot_id`. Comme cet identifiant entrait dans `intent_payload()`, il pouvait ensuite modifier `content_sha256` et `intent_id`, même lorsque budget, cibles et ordres étaient identiques.

Il s'agissait d'une interférence informationnelle indirecte : la politique ne lisait pas nécessairement le montant, mais une empreinte visible en révélait une dépendance.

## 3. Séparation des objets

### 3.1 Vue décisionnelle

`DecisionSnapshot` est maintenant la seule vue admise par `prepare_intent_from_snapshot()`. Elle contient uniquement :

- l'instant de décision, la date et les closes admissibles ;
- les positions héritées utiles ;
- le cash admissible, les règlements connus et les ressources de financement ;
- les créances connues et les identifiants non monétaires des créances exclues ;
- le budget décisionnel, le statut, le motif et les provenances admissibles ;
- les conventions E-B, la référence de valorisation et la coupure informationnelle ;
- `ledger_sequence`, compteur monotone conservé uniquement pour l'intégrité et la péremption.

Elle ne possède plus les champs `economic_distribution_receivables`, `economic_wealth`, `excluded_distribution_claims` ou `unavailable_paid_cash`. Aucun renommage privé n'est utilisé : ces montants ne sont pas présents dans l'objet.

### 3.2 État d'audit

`EconomicAuditState`, construit explicitement par `build_economic_audit_state()`, conserve séparément :

- l'`AccountingSnapshot` complet ;
- les positions, cash, créances de vente, dettes d'achat et frais ;
- la copie immuable des créances avec leurs montants et dates ;
- la richesse économique à la référence de valorisation ;
- les montants exclus, payés mais indisponibles et incorporés au close cum-distribution ;
- la version du registre et une empreinte `AUDIT-<sha256>` indépendante.

Cet état n'est jamais un argument de préparation de décision. Une vue décisionnelle est construite directement depuis les seules composantes admissibles du registre ; elle ne reçoit pas un état d'audit complet pour en ignorer ensuite des champs.

## 4. Sérialisation, scellement et péremption

`decision_snapshot_payload()` est le contenu canonique de politique. `decision_snapshot_content_sha256()` ne couvre que ce contenu admissible et `snapshot_id` vaut `SNAPSHOT-<sha256>`. `intent_payload()` inclut cet identifiant décisionnel, les cibles, ordres, conventions et ressources admissibles ; son hash produit `INTENT-<sha256>`.

L'audit possède une sérialisation distincte, `economic_audit_payload()`, et un hash distinct, `economic_audit_content_sha256()`. Son identifiant n'entre ni dans le snapshot de politique ni dans l'intention.

La péremption reste indépendante du montant caché : `ledger_sequence` est identique dans deux mondes ayant la même suite d'événements, mais toute mutation ultérieure effective du registre incrémente la version et invalide le snapshot ou l'intention avant exécution. Les contrôles d'intégrité du snapshot, de l'intention et du journal persistant sont conservés.

## 5. Non-interférence

Le test principal construit deux registres artificiels identiques, sauf pour une distribution inconnue post-ex : 2 USD contre 7 USD par part, soit 1 000 USD contre 3 500 USD pour 500 parts.

| Surface | Résultat |
|---|---|
| richesse économique d'audit | 100 000 USD contre 102 500 USD |
| contenu et hash d'audit | différents, comme attendu |
| objet `DecisionSnapshot` | strictement identique |
| JSON décisionnel, hash et `snapshot_id` | strictement identiques |
| budget admissible | 99 000 USD dans les deux mondes |
| financement et statut | identiques |
| quantités cibles et ordres | identiques |
| contenu, hash et `intent_id` | strictement identiques |

Un second contrôle de schéma interdit explicitement les quatre montants rétrospectifs dans les champs du snapshot et dans son payload. Changer uniquement l'information interdite ne change donc aucune sortie de préparation observable par la politique.

## 6. Budget E-B et ex-date

La convention reste :

\[
B_d=\sum_i q_{i,d}P^{close}_{i,d}+C_d^{admissible}
+A_d^{connues,post\text{-}ex}+U_d^{vente}-U_d^{achat}.
\]

Les parts sont valorisées au dernier close admissible. Une créance du jour n'est pas ajoutée à un close cum-distribution ; une créance inconnue post-ex reste hors budget ; une créance connue post-ex est ajoutée si sa connaissance est admissible. Le cash payé mais non encore disponible est exclu. Le financement reste plus restrictif que le budget, sous `H_FIN_NET`. Les quantités 50/50 sont entières et figées avant tout open.

Le cas 100 parts, close cum 100 USD, distribution 2 USD et open ex 98 USD conserve exactement :

\[
100\times100=100\times98+200=10\,000.
\]

Le droit reste dans l'audit, n'est pas doublé dans le budget et n'est pas perdu si un lot est rejeté. L'écart entre budget au close précédent et richesse valorisée à l'open est autorisé et doit être publié comme différence de référence temporelle, jamais corrigé après lecture de l'open.

## 7. Protocole strict S et séquence synthétique

`build_decision_snapshot()` reste le chemin par défaut. Une créance inconnue continue de rendre S `NOT_EVALUABLE`, le cash sans preuve reste exclu et un open futur ne participe jamais au dimensionnement. E-B exige toujours l'appel distinct, `EXPLORATORY_CONDITIONAL`, et une convention D+1 ou D+2.

La séquence synthétique intégrée existante a été étendue, pas remplacée. Elle couvre achat initial, distribution inconnue, décision, dérive, vente–achat, règlement, paiement, disponibilité D+1/D+2, rejet atomique, héritage des positions inchangées et hold sans frais. À chaque étape, richesse économique, budget et financement proviennent réellement du registre et de l'adaptateur. `H_FIN_NET`, les coûts S0–S3, l'absence de double comptage et les invariants comptables restent validés.

## 8. Contrat historique figé

Les conventions suivantes sont immuables avant consultation de toute performance C2 :

1. épisode unique du 29 mai 2024 au 29 mai 2025 inclus ;
2. capital initial de 100 000 USD ;
3. parts entières uniquement ;
4. C1 et C2 partagent le même achat et les mêmes positions initiales dans chaque scénario homogène ;
5. C1 conserve ces positions ; C2 vise 50/50 du budget E-B aux 52 décisions documentées ;
6. closes Yahoo comme proxys conditionnels de décision ;
7. opens Yahoo comme proxys rétrospectifs d'exécution, invisibles avant scellement ;
8. décisions à 08:00 `America/New_York` ;
9. règlement T+1 selon le calendrier DTC documenté ;
10. créances inconnues traitées selon E-B et toutes les distributions comptabilisées économiquement ;
11. cash D+1 principal, D+2 en sensibilité ;
12. coûts S0, S1, S2 et S3 égaux à 0, 1, 5 et 10 pb du notionnel exécuté ;
13. financement `H_FIN_NET` ;
14. rejet atomique, sans redimensionnement ;
15. aucun réinvestissement automatique des distributions ;
16. terminal commun au 29 mai 2025, sans liquidation fictive ;
17. même source et même convention de valorisation pour les deux membres d'une paire ;
18. toute sortie est étiquetée `EXPLORATORY_CONDITIONAL`, jamais certifiée point-in-time.

Les huit paires autorisées sont le produit cartésien `{S0,S1,S2,S3} × {D+1,D+2}`. Une comparaison C1–C2 ne peut agréger, substituer ou opposer deux cellules différentes.

## 9. Schéma des sorties futures

Chaque enregistrement porte au minimum `episode_id`, `policy_id`, `cost_scenario`, `cost_bps`, `cash_convention`, `protocol_mode`, `valuation_source_ids`, `run_status` et les empreintes des entrées. Aucun champ manquant n'est remplacé par zéro.

### 9.1 Résultats économiques par politique

| Champ | Unité et règle figée |
|---|---|
| `initial_wealth_usd` | USD ; 100 000 avant le premier lot |
| `terminal_wealth_usd` | USD ; parts au close Yahoo du 29 mai 2025 + cash + créances + ventes à recevoir − achats à payer − frais déjà reconnus |
| `total_return` | ratio ; `terminal_wealth / initial_wealth - 1` |
| `annualized_return` | ratio/an ; `(1 + total_return)^(365.2425 / jours_calendaires) - 1` |
| `annualized_volatility` | ratio/an ; écart-type échantillonnal (`ddof=1`) des rendements quotidiens de richesse, multiplié par `sqrt(252)` |
| `max_drawdown` | ratio ; minimum de `W_t / max_{u≤t}(W_u) - 1` sur les 251 séances communes |
| `max_time_under_water_sessions` | séances ; plus longue séquence après un sommet sans égaler ou dépasser ce sommet |
| `worst_daily_return` | ratio ; minimum de `W_t / W_{t-1} - 1` |
| `terminal_cash_usd` | USD ; cash réglé au terminal, sans liquidation |
| `distributions_accrued_usd` | USD ; somme des droits acquis dans l'épisode |
| `distributions_paid_usd` | USD ; somme des paiements effectivement enregistrés avant ou au terminal |
| `cumulative_fees_usd` | USD ; somme des frais reconnus une fois sur lots exécutés |
| `terminal_share_value_usd` | USD ; `q_SPY×Close_SPY + q_BIL×Close_BIL` au terminal |

La richesse quotidienne utilise la même comptabilité économique et les mêmes closes pour C1 et C2. Le rendement journalier n'est calculé que lorsque les deux richesses adjacentes existent.

### 9.2 Activité C2

| Champ | Unité et règle figée |
|---|---|
| `candidate_decisions` | compte ; 52 si aucune règle d'arrêt antérieure |
| `evaluable_intents` | compte des intentions scellées dont les entrées indispensables sont disponibles |
| `voluntary_holds` | compte des `VOLUNTARY_HOLD` |
| `executed_batches` | compte des lots `EXECUTED_HYPOTHETICAL` |
| `rejected_batches` | compte des `ECONOMIC_ORDER_REJECTED` |
| `rejection_reasons` | table `{reason: count}`, sans suppression |
| `buy_order_count`, `sell_order_count` | comptes des ordres non nuls appartenant aux lots exécutés |
| `gross_traded_notional_usd` | USD ; somme de `abs(q_order)×Open` sur ordres exécutés |
| `cumulative_costs_usd` | USD ; somme des frais des lots exécutés |
| `mean_spy_exposure`, `mean_bil_exposure` | ratios ; moyenne sur les 251 fins de séance communes de `q_i×Close_i / richesse_économique` |
| `mean_predecision_target_gap` | ratio ; moyenne sur décisions évaluables de `abs(q_SPY×Close_SPY/B_d - 0.5)` |
| `cash_and_claims_path` | table datée en USD : cash réglé, cash admissible, créances connues, créances exclues d'audit, ventes à recevoir et achats à payer |

Un lot comporte simultanément ses ventes et achats. Un rejet ne crée aucun ordre exécuté, aucun notionnel et aucun coût, mais demeure compté comme décision et rejet.

### 9.3 Comparaison appariée

Pour une même cellule `(cost_scenario, cash_convention)`, les champs sont :

- `terminal_wealth_difference_usd = W_T(C2) - W_T(C1)` ;
- `total_return_difference = R(C2) - R(C1)` ;
- `max_drawdown_difference = MDD(C2) - MDD(C1)` ;
- `annualized_volatility_difference = σ(C2) - σ(C1)` ;
- `incremental_rebalancing_cost_usd = fees(C2) - fees(C1)` ;
- `executed_rebalances`, nombre de lots C2 exécutés après l'allocation initiale ;
- `cash_delay_effect`, différence descriptive D+2 moins D+1 calculée séparément pour chaque politique et scénario de coûts, jamais assimilée à une paire C1–C2 principale.

## 10. Règles d'arrêt

Chaque décision reçoit exactement un statut terminal :

- `EXECUTED_HYPOTHETICAL` : lot figé exécuté ; la séquence continue ;
- `VOLUNTARY_HOLD` : aucun ordre demandé ; la séquence continue sans frais ;
- `ECONOMIC_ORDER_REJECTED` : lot atomiquement rejeté ; positions et cash hérités restent inchangés et la séquence continue ;
- `NOT_EVALUABLE` : information opérationnelle indispensable absente ou invalide ; la paire s'arrête avant mutation ;
- `DOCUMENTARY_BLOCK` : source, empreinte, calendrier ou preuve conventionnelle indispensable absente ou contradictoire ; la paire s'arrête avant mutation.

Après `NOT_EVALUABLE` ou `DOCUMENTARY_BLOCK`, aucun résultat terminal C1–C2 apparié n'est publié. C1 peut rester descriptif sous une section explicitement non appariée. Les valeurs futures restent nulles au sens « absentes », jamais numériques zéro. Les rejets économiques et holds sont conservés dans le journal.

## 11. Audit pré-exécution ciblé

L'audit a utilisé uniquement les sources et grilles déjà autorisées. Il n'a construit aucun portefeuille C2 historique, ordre, richesse ou rendement.

| Contrôle | Preuve | Résultat |
|---|---|---|
| manifeste | `verify_local_data.py` | 50 entrées contrôlées, 0 échec ; les 2 entrées sans fichier local attendu sont hors périmètre C2 |
| prix SPY/BIL | hashes manifeste `b77099…` et `2eaa05…` | closes et opens présents pour 52/52 décisions |
| distributions State Street | hash `6b65cb…` | 16 événements documentés et chargeables |
| calendrier NYSE | hash `2c2e63…` | 52 dates reproduites, fuseau et DST contrôlés |
| SEC T+1 | hash `e214bf…` | règle présente et validée pour usage |
| DTC | avis `DTC-19404-23` et `DTC-20972-24`, bundle `129d15…`, guide `165596…` | 52/52 dates de règlement `VERIFIED` |
| grille stricte | SHA-256 `d417dee20ba886d28dddcd2c42d2d8e9ebe8b77a30e5dfe00fd70adce1ed311c` | 52 lignes reproduites à l'identique |
| grille E-B | SHA-256 `d8f58b1bba900573d7b15cdf3af6d4d3648233d33746d6b3eb9e67758ea7af59` | 52/52 `CONDITIONALLY_DOCUMENTED` ; D+2 affecte 5 décisions |
| terminal | dernier règlement candidat le 28 mai 2025 ; dernière distribution le 6 mai 2025 | aucun événement économique connu ne dépasse le terminal du 29 mai |

Les 32 blocages stricts liés aux droits inconnus et les 51 dépendances à une preuve réelle de disponibilité du cash restent inscrits dans la grille stricte. Ils ne sont pas effacés : E-B les remplace seulement par les conventions conditionnelles désormais figées. Les versions historiques quotidiennes de Yahoo à 08:00 et les heures réelles de crédit dépositaire ne sont toujours pas prouvées ; c'est pourquoi le futur résultat portera obligatoirement le qualificatif exploratoire conditionnel.

Aucun résultat C2 préexistant n'a été chargé ou consulté pour choisir les paramètres. Les scripts appelés pour cet audit produisent seulement des classifications documentaires et des tests de reproductibilité.

## 12. Validation logicielle

- suite complète : **170 tests réussis** ;
- contrôles ciblés de grille et de protocole : 15 réussis ;
- Ruff : requis sans erreur sur les fichiers concernés ;
- invariants comptables, ex-date, D+1/D+2, `H_FIN_NET`, coûts S0–S3, rejet atomique, scellement et péremption : couverts ;
- manifeste, données brutes, notebooks et deux grilles historiques : inchangés.

## 13. Limites scientifiques à publier avec tout résultat

Une future comparaison restera une étude d'un épisode unique et ne permettra aucune inférence de supériorité générale. Les closes et opens Yahoo sont des proxys rétrospectifs, non des archives point-in-time ni des fills garantis. Les coûts en points de base ne modélisent ni spread variable, ni impact, ni liquidité, ni fiscalité. Le calendrier et `H_FIN_NET` stylisent un compte, sans prouver les pratiques d'un dépositaire ou courtier réel. D+1/D+2 sont des conventions, pas des observations historiques de crédit. Les annonces historiques complètes des distributions ne sont pas disponibles à chaque décision. Les résultats seront sensibles à l'arrondi en parts entières, à la fenêtre unique, aux flux de distribution et à la convention terminale sans liquidation. Ils devront rester séparés de tout résultat strictement certifié point-in-time.

## 14. Autorisation technique

Il ne subsiste pas d'obstacle technique bloquant dans le périmètre conditionnel E-B figé. L'expérience historique ne doit toutefois commencer qu'après autorisation explicite. Aucun paramètre de ce contrat ne pourra alors être modifié après consultation des performances.

