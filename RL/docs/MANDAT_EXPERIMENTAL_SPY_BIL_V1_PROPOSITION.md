# Mandat expérimental SPY–BIL v1 — proposition soumise à approbation

Date : 20 octobre 2026

Point de départ : `0d94a29a76b8369a084e0df9a70db94825b637ce`

Statut : **proposition non approuvée**. Ce document ne lance aucune expérience et
ne modifie aucune donnée, aucun registre ni aucune convention déjà validée.

## 1. Problème économique précis

Un gestionnaire stylisé administre une poche autonome en USD entre deux ETF :

- SPY représente l'exposition aux actions américaines ;
- BIL représente une exposition investie aux Treasury bills américains de très
  courte maturité ;
- le cash sert uniquement au règlement, aux distributions et aux arrondis.

Chaque semaine, après la dernière clôture commune effectivement observée, le
gestionnaire peut modifier son exposition aux actions. Son problème n'est pas de
prédire un rendement abstrait, mais de décider si le bénéfice attendu d'une nouvelle
allocation justifie le risque, les coûts et les conséquences de transactions qui
modifient les positions et les ressources des semaines suivantes.

L'objectif économique proposé est la croissance composée de la richesse de marché
nette des coûts reconnus sur un horizon fini. Le risque reste évalué séparément ; il
n'est pas transformé à ce stade en seuil dur ou en fonction de récompense.

La difficulté opérationnelle centrale est la suivante : une poche entièrement
investie en BIL doit pouvoir vendre BIL et acheter SPY sans crédit fictif, tout en
respectant le fait que vente et achat ne sont réglés qu'à T+2 puis T+1. Une règle
exigeant uniquement du cash déjà réglé rendrait une réallocation économiquement
financée mais comptablement impossible.

## 2. Ce qu'autorise réellement un compte cash

La Regulation T distingue un compte cash d'un compte sur marge. L'achat est permis
si les fonds sont suffisants ou si le courtier accepte de bonne foi l'engagement de
paiement intégral avant revente. Le titre acheté ne peut pas être revendu avant
d'avoir été intégralement payé sans exposer le compte aux règles de freeriding et de
gel ([Federal Reserve, Regulation T § 220.8](https://www.federalreserve.gov/frrs/regulations/section-2208-cash-account.htm)).

Le bulletin de la SEC donne précisément l'exemple d'un titre entièrement payé vendu
et d'un autre acheté le même jour avec ce produit non réglé : l'achat est permis si
le nouveau titre n'est pas revendu avant le règlement de la vente de financement
([SEC, *Trading in Cash Accounts*](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated-9)).
Fidelity illustre une pratique de courtier comparable : une vente exécutée peut
financer un achat, mais une revente trop précoce du nouvel achat crée une *good
faith violation*
([Fidelity, cash account violations](https://www.fidelity.com/learning-center/trading-investing/trading/avoiding-cash-trading-violations)).

Ces sources établissent qu'utiliser le produit non réglé d'une vente de titres déjà
payés n'est pas automatiquement un emprunt. Elles n'établissent pas que tout courtier,
tout statut de compte ou toute combinaison d'ordres autorise universellement cette
pratique. Le futur compte reste donc stylisé et son hypothèse contractuelle doit être
approuvée comme telle.

| Question opérationnelle | Réponse limitée retenue pour la proposition |
|---|---|
| L'ordre d'achat peut-il être présenté ? | oui seulement si le courtier accepte les produits non réglés comme capacité de négociation ou accepte l'engagement de paiement de bonne foi |
| Les fonds sont-ils déjà réglés ou retirables ? | non ; une capacité d'achat affichée ne transforme pas le produit en cash réglé ou retirable |
| Quand l'achat doit-il être payé ? | au plus tard selon l'échéance réglementaire et contractuelle applicable |
| Le nouveau titre peut-il être revendu immédiatement ? | non s'il dépend du produit non réglé ; il doit être conservé jusqu'au paiement intégral |
| Les flux peuvent-ils être compensés ? | le modèle peut tester leur suffisance à une même échéance ; il ne présume aucun droit général de netting chez le courtier |
| Y a-t-il marge ou emprunt ? | non : aucun débit projeté, intérêt, collatéral ou pouvoir d'achat emprunté n'est admis |

## 3. Comparaison des conventions de financement

| Convention | Réallocation SPY–BIL | Exposition et risque | Hypothèse contractuelle | Simplicité et registre | Verdict |
|---|---|---|---|---|---|
| `CONSERVATIVE_SETTLED_CASH` | achat limité au cash déjà réglé ; une rotation presque complète peut être rejetée | conserve involontairement l'ancienne exposition | minimale | déjà représentable, mais trop restrictive | non retenue en principal |
| compte cash avec produit de vente non réglé, représenté par `H_FIN_NET` | vente et achat de même trade date peuvent se financer si leurs échéances concordent et si le cash projeté reste non négatif | rejoint immédiatement l'allocation obtenue, sous réserve du gap et des arrondis | compte non restreint, acceptation du courtier, titres vendus déjà payés, aucune revente prématurée | projection et atomicité présentes ; garde de revente à imposer dans la future intégration | **recommandée** |
| rééquilibrage en deux étapes | vente, attente du règlement, puis achat à une ouverture ultérieure | passage temporaire au cash, risque de prix et écart à la cible | faible au-delà du compte cash | deux transactions et deux dates ; calendrier plus complexe | sensibilité opérationnelle possible |
| réserve structurelle de cash | finance seulement les achats jusqu'à épuisement de la réserve | coût d'opportunité et exposition durable à un troisième actif | aucune garantie de suffisance | exige de fixer une cible de cash | écartée en v1 |

### 3.1 Convention principale recommandée

La proposition principale est **`H_FIN_NET` sous l'interprétation limitée
`CASH_ACCOUNT_UNSETTLED_SALE_PROCEEDS`**. Elle ne signifie ni compte sur marge, ni
crédit gratuit, ni droit juridique de compensation du client chez DTC. Elle signifie
seulement que le modèle accepte un lot vente–achat si toutes les conditions suivantes
sont remplies :

1. le compte cash n'est soumis à aucune restriction de paiement préalable ;
2. les parts vendues sont économiquement et juridiquement réglées avant la vente ;
3. le courtier hypothétique accepte que leur produit finance un achat le même jour ;
4. vente et achat ont la même settlement date documentée ;
5. le cash réglé, augmenté des ventes et diminué des achats et coûts dus à chaque
   échéance, ne devient jamais négatif ;
6. aucun retrait ne consomme le produit avant règlement ;
7. le titre acheté avec ce produit ne peut être revendu avant paiement intégral ;
8. aucune jambe ne crée de position négative, de fraction implicite ou de levier ;
9. le lot entier est accepté ou refusé atomiquement.

Le règlement net du registre est une représentation de suffisance des flux à
l'échéance, pas une affirmation sur la comptabilité interne d'un courtier réel.
L'alignement T+2/T+1 de deux ETF négociés le même jour rend la convention
économiquement cohérente ; le calendrier doit néanmoins démontrer cette égalité pour
chaque lot. Le registre sait déjà contrôler le cash par échéance et l'atomicité ; la
future voie d'intégration devra en plus interdire explicitement la revente avant le
paiement intégral lorsqu'un achat dépend de fonds non réglés.

### 3.2 Variante de sensibilité

Le rééquilibrage en deux étapes peut être préspécifié comme sensibilité : vente à la
première ouverture, achat à la première ouverture commune admissible après mise à
disposition des fonds. La cible reste celle de la décision initiale et n'est pas
recalculée avec les prix futurs. Entre les deux jambes, la poche détient du cash
transitoire ; le délai, le mouvement de prix et l'écart à la cible sont des
conséquences économiques à publier. Une nouvelle décision hebdomadaire ne doit pas
écraser une réallocation encore en cours sans règle approuvée.

Cette variante ne doit pas être confondue avec le cas principal : elle change le
chemin d'exposition. La réserve structurelle de cash n'est pas retenue, car elle
transformerait le cash en troisième allocation stratégique sans garantir le
financement de tous les ordres.

## 4. Décision hebdomadaire et traduction en opérations

### 4.1 Objets distincts

À la date de décision `d`, après la clôture commune :

- **allocation héritée** : poids issus des quantités antérieures et des prix connus ;
- **décision** : poids cible `w_d^SPY` dans `[0,1]`, avec
  `w_d^BIL = 1 - w_d^SPY` ;
- **quantités détenues** : parts économiques et réglées avant l'ordre ;
- **quantités cibles** : parts entières calculées avec la richesse et les clôtures
  connues à `d` ;
- **ordres proposés** : différences entre quantités cibles et détenues ;
- **lot finançable** : ordres qui passent les contrôles de titres, cash, coûts et
  règlement aux prix de référence de l'ouverture ;
- **allocation obtenue** : poids constatés après le lot exécuté, différents de la
  cible à cause des arrondis, gaps, coûts et cash résiduel.

Pour une richesse de marché connue `W_d^M` :

\[
q_{SPY}^{cible}=\left\lfloor
\frac{w_d^{SPY}W_d^M}{P_{SPY,d}^{close}}\right\rfloor,
\qquad
q_{BIL}^{cible}=\left\lfloor
\frac{(1-w_d^{SPY})W_d^M}{P_{BIL,d}^{close}}\right\rfloor.
\]

Les ordres `Delta q_i = q_i^cible - q_i^hérité` sont figés avant l'ouverture
suivante. L'open futur ne peut jamais servir à recalculer ou réduire les quantités.
Les créances de distribution ou de vente incluses dans la richesse économique ne
sont pas automatiquement des ressources disponibles : le contrôle de financement
les traite selon leur date réelle.

### 4.2 Règle principale en cas d'impossibilité

Le lot SPY–BIL est **tout ou rien** :

1. si toutes les jambes sont admissibles, livrables et finançables, elles sont
   comptabilisées ensemble ;
2. sinon, le lot entier est rejeté sans mutation financière ;
3. la position héritée demeure mécaniquement parce qu'aucune transaction n'a eu
   lieu, mais le résultat porte `ECONOMIC_ORDER_REJECTED` et non `VOLUNTARY_HOLD` ;
4. la décision cible, les ordres proposés, les prix, la cause et l'écart à la cible
   sont conservés et publiés.

Une exécution partielle exigerait une priorité entre SPY, BIL et cash et pourrait
utiliser indirectement l'open futur pour redimensionner. Elle n'est pas retenue en
v1. Une réallocation différée appartient uniquement à la variante en deux étapes ;
elle n'est jamais déclenchée silencieusement après un rejet du cas principal.

## 5. Conventions financières proposées

| Dimension | Fait établi | Hypothèse proposée v1 | Justification | Limite et décision à approuver |
|---|---|---|---|---|
| Investisseur | SPY et BIL sont des ETF négociés en USD | gestionnaire preneur de prix d'une poche autonome, compte cash non restreint, fiscalement neutre | mandat simple sans passif externe | aucune juridiction, fiscalité personnelle ou courtier réel n'est représenté |
| Contraintes | le registre sait séparer positions économiques/réglées et flux | long-only, aucune vente à découvert, aucun levier, aucun retrait | empêche de financer une exposition par dette | accepter la stylisation du compte |
| Financement | `H_FIN_NET` projette le cash par échéance | `CASH_ACCOUNT_UNSETTLED_SALE_PROCEEDS` selon les neuf conditions de la section 3 | rend possibles les rotations autofinancées | acceptation du courtier fictive et explicitement conditionnelle |
| Richesse initiale | les parts entières rendent le résultat dépendant de l'échelle | **100 000 USD** en principal ; sensibilités **10 000** et **1 000 000 USD** | montants ronds fixés ex ante, montrant forte, moyenne et faible granularité d'arrondi | aucune valeur ne sera choisie d'après les rendements |
| Prix | Yahoo `Open` est audité mais n'est pas un fill | référence hypothétique conditionnelle à la prochaine ouverture commune | chronologie reproductible avec quantités déjà figées | approuver la convention ; `2026-04-20` reste indisponible |
| Parts | le registre principal emploie des entiers | parts entières uniquement | ne suppose aucun service fractionnaire | cash et écart à la cible persistent |
| Coûts | aucune quote ou exécution individuelle historique n'est disponible | couche comptable sans coût externe ; sensibilités hypothétiques préspécifiées séparément ; couche empirique seulement après preuve | sépare identité, robustesse et réalisme | montants de sensibilité à figer avant résultats ; aucun coût zéro présenté comme observé |
| Cash | le cash est nécessaire au règlement et aux arrondis | cash technique, résiduel ou transitoire, non rémunéré ; aucun poids cible | évite un troisième actif stratégique, BIL restant la composante défensive | coût d'opportunité réel non modélisé |
| Risque | aucune valeur de budget n'est scientifiquement justifiée | volatilité, pertes, drawdown, durée et sous-estimation comme indicateurs | évite qu'un seuil arbitraire change l'espace d'action | aucune contrainte dure en v1 |
| Fréquence | le candidat antérieur est hebdomadaire après clôture | décision après la dernière clôture commune de chaque semaine, ordre à l'ouverture commune suivante | évite l'exécution rétrospective et limite le turnover | heures historiques et séances doivent être documentées |
| Horizon | un an était proposé comme unité économique | un épisode dure un an calendaire, environ 52 décisions, et se termine par une valorisation sans liquidation forcée | horizon interprétable ; pas de coût terminal artificiel | règle exacte de date terminale à encoder et tester |
| Données | 2018–2026 est la fenêtre homogène candidate post-split | seulement une fenêtre de faisabilité | ne préjuge pas d'un découpage expérimental | apprentissage, validation et évaluation restent à définir sans consulter leurs résultats |

L'épisode proposé commence à une clôture de décision admissible et se termine à la
dernière clôture commune disponible au plus tard à son premier anniversaire, avec
environ 52 occasions hebdomadaires. Toute dette ou créance non réglée reste dans la
richesse terminale ; aucune vente finale artificielle n'est imposée. Cette définition
doit être identique pour toutes les politiques comparées.

## 6. Ordres impossibles et données non représentables

### 6.1 Deux familles qui ne doivent pas être confondues

| Famille | Codes | Traitement |
|---|---|---|
| échec documentaire | `PRICE_MISSING_OR_DISPUTED`, `CALENDAR_UNVERIFIED`, `EVENT_UNDOCUMENTED`, `CONTRACT_UNAPPROVED` | transition inconnue ; trajectoire non évaluable à partir de l'événement requis |
| infaisabilité économique | `FUNDING_INFEASIBLE`, `DELIVERY_INFEASIBLE` | lot rejeté atomiquement ; état financier inchangé et trajectoire poursuivie avec marqueur de rejet |
| erreur de protocole | `INPUT_INVALID` | arrêt en erreur ; résultat non admissible |

Une trajectoire interrompue pour défaut documentaire n'est ni un non-investissement,
ni une conservation choisie, ni une observation à supprimer. Si des politiques ont
des couvertures évaluables différentes, aucun classement direct ne peut être annoncé
sans analyse commune préspécifiée ; les couvertures et causes doivent être publiées.

### 6.2 Politique documentaire minimale

- Yahoo `Open` reste une référence et non un fill. Un ordre non nul prévu le
  20 avril 2026 reçoit `PRICE_MISSING_OR_DISPUTED`; aucune correction ou ouverture
  de remplacement n'est autorisée.
- Chaque trade date doit appartenir au calendrier de négociation versionné.
- Chaque settlement date doit être calculée par le régime T+2/T+1 et un calendrier
  versionné propre au service pertinent. Une règle ou un calendrier annuel doit
  couvrir la date ordinaire ; tout jour férié, fermeture imprévue ou restriction
  exige l'avis applicable. Une simple mention « NSCC open » ne suffit pas.
- La vérification ciblée calcule d'abord les dates requises sans muter le registre,
  relie chaque date et exception à une source primaire, puis produit le calendrier
  figé et son empreinte. Toute date non prouvée devient `CALENDAR_UNVERIFIED`.
- Distributions, paiements et opérations sur titres doivent porter source,
  knowledge date, date d'effet et statut d'usage.

Pour tous les rejets, le futur résultat doit publier les intentions, lots exécutés,
rejets par cause, montants refusés, écarts à la cible et trajectoires interrompues.
Aucune exclusion ne peut dépendre des performances observées.

## 7. Références financières futures

Avant toute méthode d'apprentissage, les mêmes prix, calendriers, coûts, règles de
financement et conventions de non-représentabilité devront être appliqués à :

1. détention simple de SPY ;
2. détention simple de BIL ;
3. allocation fixe SPY–BIL avec la même règle de rééquilibrage ;
4. règle déterministe de réallocation fondée uniquement sur l'information disponible ;
5. éventuellement, règle classique de ciblage de volatilité préspécifiée.

Une politique dynamique meilleure montrerait seulement qu'une adaptation donnée a
été utile sous ces hypothèses et sur l'évaluation prévue ; elle ne prouverait ni la
causalité, ni la supériorité du RL. Une équivalence indiquerait que la complexité
n'ajoute pas de valeur détectable. Une performance inférieure pourrait révéler que
les coûts, erreurs de prévision, arrondis ou contraintes dominent le bénéfice de
l'adaptation. Les diagnostics de rendement, risque, coûts et rejets devront rester
séparés pour distinguer ces mécanismes.

## 8. Hypothèses encore incertaines

Les points suivants ne sont pas résolus par cette proposition :

- aucun courtier réel n'est choisi et son acceptation des ordres liés n'est pas
  démontrée historiquement ;
- `H_FIN_NET` est économiquement défendable sous conditions, mais reste une
  convention de recherche à approuver ;
- Yahoo `Open` n'est pas une exécution garantie et le 20 avril 2026 reste contesté ;
- le calendrier DTC/NSCC 2018–2026 n'est pas archivé exhaustivement ;
- bid/ask, slippage, impact et commissions individuels ne sont pas observés ;
- les valeurs des scénarios de coûts ne sont pas fixées ;
- les variables d'information et leurs délais point-in-time restent à spécifier ;
- le découpage apprentissage/validation/évaluation n'est pas choisi ;
- le registre est validé sur cas artificiels, pas sur transactions historiques.

Ces limites ne justifient pas de revenir au cash réglé conservateur comme mandat
principal. Elles imposent de présenter le compte comme stylisé, de tester ses règles
et d'arrêter toute transition sans preuve suffisante.

## 9. Contrat minimal de la prochaine implémentation

### 9.1 Paramètres à figer

- richesse principale et sensibilités ;
- fréquence, règle de date terminale et univers SPY–BIL ;
- `w^SPY` cible, complément BIL, parts entières et règle d'arrondi ;
- convention `H_FIN_NET` limitée et interdiction de revente avant paiement ;
- prix, couches de coûts, statut du cash et mesures de risque ;
- codes de rejet et politique d'arrêt documentaire.

### 9.2 Entrées requises

- clôtures connues à la décision et opens conditionnels à la transaction ;
- calendriers de négociation et de règlement versionnés ;
- régime T+2/T+1 ;
- distributions avec dates d'annonce, ex-date et paiement ;
- splits et autres opérations sur titres ;
- métadonnées d'anomalie, source, empreinte et statut du manifeste ;
- informations de décision avec date réelle de disponibilité.

### 9.3 Pipeline et garde-fous

```text
information disponible à la clôture
    -> poids cible
    -> quantités entières figées au close
    -> lot vente/achat à l'open de référence
    -> contrôles documentaires, livraison et cash par échéance
    -> exécution atomique ou rejet qualifié
    -> événements et règlement dans le registre strict
```

La voie historique devra construire exclusivement
`SyntheticPortfolioLedger(..., strict_temporal=True, trading_calendar=...,
settlement_calendar=...)`, puis affirmer que `strict_temporal is True`. Elle ne doit
exposer aucun mode de compatibilité, aucun calendrier implicite, aucun prix silencieux,
aucune NAV comme prix de transaction et aucun redimensionnement à l'open.

### 9.4 Tests artificiels minimaux avant données historiques

1. vente réglée et achat de même échéance acceptés sans cash négatif ;
2. échéances différentes non compensées ;
3. parts vendues non réglées refusées ;
4. revente avant paiement du titre acheté avec fonds non réglés refusée ;
5. gap d'ouverture et coûts rendant le lot déficitaire : rejet atomique ;
6. distinction journalisée entre `VOLUNTARY_HOLD` et `ECONOMIC_ORDER_REJECTED` ;
7. quantités entières et arrondis reproductibles aux trois richesses ;
8. prix contesté, calendrier incomplet ou événement antidaté : arrêt avant mutation ;
9. ordre des événements de même date et absence de double distribution ;
10. richesse terminale correcte avec créances et dettes encore ouvertes.

L'intégration historique n'est autorisable qu'après approbation des paramètres,
réussite de ces tests, disponibilité de toutes les entrées, résolution ciblée des
dates de règlement sollicitées et verrouillage du mode strict. Elle reste interdite
si un prix requis est contesté, un calendrier implicite, une source hors statut, un
coût présenté abusivement comme observé ou une information future peut entrer.

## 10. Décisions soumises à approbation

Le porteur du projet doit approuver, modifier ou rejeter ensemble les choix suivants :

1. compte cash USD stylisé, fiscalement neutre, non restreint et sans marge ;
2. `H_FIN_NET` limité aux produits de ventes réglées et aux flux de même échéance ;
3. interdiction de revendre un achat avant le règlement de sa vente de financement ;
4. lot SPY–BIL atomique et rejet intégral sans redimensionnement à l'open ;
5. poids cible SPY, BIL complémentaire, parts entières ;
6. 100 000 USD en principal et sensibilités 10 000/1 000 000 USD ;
7. Yahoo `Open` conditionnel et indisponibilité du 20 avril 2026 ;
8. cash technique non rémunéré, sans cible stratégique ;
9. couches de coûts séparées et valeurs de sensibilité fixées avant résultats ;
10. risque comme ensemble d'indicateurs, sans contrainte dure en v1 ;
11. décision hebdomadaire et horizon économique d'un an sans liquidation terminale ;
12. politique de rejet, d'arrêt documentaire et de comparaison sur couverture
    commune ;
13. variante éventuelle de rééquilibrage en deux étapes ;
14. critères du contrat minimal avant toute intégration historique.

## 11. Fiche de décision synthétique

| Sujet | Choix recommandé | Alternative importante | Motif décisif | Approbation |
|---|---|---|---|---|
| Investisseur | poche USD autonome, compte cash non restreint, fiscalité exclue | compte/courtier réel | simplicité ; hypothèses visibles | ☐ |
| Univers | SPY + BIL, long-only | ajouter un actif | mandat minimal | ☐ |
| Décision | poids cible SPY `[0,1]`, BIL complémentaire | ordre direct en parts | interprétable, puis conversion déterministe | ☐ |
| Financement | `H_FIN_NET` limité aux ventes réglées et même échéance | deux étapes après règlement | rotations possibles sans cash négatif | ☐ |
| Interdictions | aucune marge, dette, vente à découvert, retrait ou revente avant paiement | `CONSERVATIVE_SETTLED_CASH` | cohérence d'un compte cash | ☐ |
| Exécution | lot entier figé au close, Yahoo `Open` conditionnel | prix d'enchère officiel futur | absence de look-ahead | ☐ |
| Échec économique | rejet atomique tracé ; position héritée inchangée | exécution partielle | pas de priorité arbitraire ni redimensionnement futur | ☐ |
| Défaut documentaire | trajectoire non évaluable, jamais assimilée à un hold | substitution de prix/date | aucune correction opportuniste | ☐ |
| Richesse | 100 000 USD ; sensibilités 10 000 et 1 000 000 | autre grille ex ante | mesure la granularité des parts entières | ☐ |
| Cash | technique/résiduel/transitoire, non rémunéré | réserve stratégique | BIL reste l'actif défensif | ☐ |
| Coûts | zéro externe théorique + sensibilités préspécifiées + empirique si prouvé | coût unique prétendument observé | sépare comptabilité et réalisme | ☐ |
| Risque | indicateurs séparés | contrainte dure | aucun seuil justifié | ☐ |
| Temps | hebdomadaire ; épisode d'un an ; pas de liquidation finale | autre fréquence/horizon | unité économique lisible | ☐ |
| Données | 2018–2026 seulement comme faisabilité candidate | découpage immédiat | évite une sélection sur résultats connus | ☐ |
| Sensibilité de financement | vente puis achat après règlement | réserve de cash | alternative sans hypothèse de disponibilité immédiate | ☐ |
| Étape suivante | spécification et tests artificiels de l'adaptateur strict | intégration immédiate | prouve les règles avant l'historique | ☐ |

**Proposition finale :** approuver conditionnellement le mandat v1 avec `H_FIN_NET`
interprété comme usage encadré de produits de vente non réglés dans un compte cash.
Cette convention rend les rééquilibrages possibles sans autoriser un cash projeté
négatif. Elle reste une hypothèse de recherche, non l'affirmation qu'un courtier réel
l'aurait offerte à toutes les dates. Aucune mise en œuvre ou expérience ne découle de
ce document sans approbation explicite.
