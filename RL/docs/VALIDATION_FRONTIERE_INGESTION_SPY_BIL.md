# Validation de la frontière d'ingestion synthétique SPY–BIL

Date : 20 octobre 2026

Point de départ : `a2dd777a13c7787d725c1a5e63576c6e58302bed`

## 1. Conclusion et périmètre

La frontière [`synthetic_input_boundary.py`](../scripts/synthetic_input_boundary.py)
charge désormais un petit contrat JSON strict, entièrement artificiel, puis construit
le registre et l'adaptateur existants sans choisir d'allocation. L'adaptateur refuse
en outre toute intention dont le contenu, l'identifiant, les quantités ou les ordres
ne correspondent pas à la décision préparée.

La suite complète compte **93 tests réussis** : les 69 tests antérieurs sont
conservés et 24 cas supplémentaires ou paramétrés couvrent l'intégrité des
intentions, le contrat sérialisé, la reproductibilité et la persistance minimale.

Aucun prix historique, portefeuille historique, backtest, signal, politique,
modèle prédictif, algorithme RL ou notebook n'a été ajouté ou utilisé. Le
registre comptable n'a pas été modifié et le manifeste des données reste inchangé.

## 2. Défaut d'intégrité confirmé

Avant la correction, `process_intent()` faisait confiance au contenu de l'objet
`DecisionIntent`. Un essai adversarial a préparé une cible de 100 parts SPY, puis
remplacé l'ordre par un achat d'une seule part en conservant l'identifiant. Le
résultat était `EXECUTED_HYPOTHETICAL` et la position devenait une part :
l'identifiant séquentiel n'authentifiait donc ni la décision ni ses ordres.

Le correctif est limité à l'adaptateur. Chaque intention porte maintenant :

- un contenu économique canonique ;
- son SHA-256 `content_sha256` ;
- un identifiant stable `INTENT-<sha256>` dérivé du même contenu.

Avant toute observation de prix d'ouverture ou mutation financière,
`process_intent()` recalcule l'empreinte, confronte l'identifiant au contenu,
retrouve l'intention préparée, recalcule les quantités entières et reconstruit les
ordres attendus à partir des positions héritées. Toute divergence reçoit
`INVALID_INPUT`.

## 3. Contenu canonique et cohérence des ordres

Le contenu couvert comprend la date de décision, la richesse connue, le poids SPY,
les positions héritées, les quantités cibles, les clôtures datées et chaque ordre
avec symbole, quantité, date et prix de décision. Les décimaux sont rendus sous
forme textuelle canonique et le JSON est trié, compact et encodé en UTF-8.

Les quantités attendues restent :

\[
q_{SPY}=\left\lfloor\frac{wW_d}{P_{SPY,d}}\right\rfloor,
\qquad
q_{BIL}=\left\lfloor\frac{(1-w)W_d}{P_{BIL,d}}\right\rfloor.
\]

Pour chaque symbole, l'ordre attendu est exactement
`quantité cible - position héritée`; les ordres nuls sont omis. Les tests altèrent
séparément poids, quantités cibles, ordres, prix et identifiant. Chaque falsification
est refusée sans mutation du registre.

Cette protection ne compare pas l'intégralité du registre au snapshot de décision.
Les règlements et paiements de distributions légitimes peuvent donc survenir entre
décision et exécution. Les contraintes courantes de titres et de financement sont
revérifiées à l'exécution par l'adaptateur et le registre.

## 4. Contrat d'entrée v1

Le schéma est `synthetic_spy_bil_input/v1`. Sa racine exige exactement :

- `schema_version`, `scenario_id` et `provenance` ;
- les calendriers distincts `trading` et `settlement` ;
- `initial_state`, avec cash décimal et positions SPY/BIL explicites ;
- une liste non vide de `decisions`.

Chaque décision fournit explicitement date, richesse connue, clôtures SPY/BIL,
poids cible, date et opens d'exécution, frais, statut documentaire, anomalies,
dates de règlement demandées et statut terminal attendu. La frontière ne calcule
ni ne choisit le poids.

Les dates doivent être des chaînes ISO canoniques `YYYY-MM-DD`. Les montants sont
des chaînes décimales sans exposant, afin d'être convertis directement en
`Decimal`. Les seuls symboles admis sont SPY et BIL. Les champs inconnus, absents,
dupliqués ou contradictoires sont refusés. Une version inconnue, une provenance
différente, un calendrier vide, non trié ou dupliqué, un prix nul, négatif,
indisponible de manière incohérente, une date ambiguë ou un statut documentaire
`CLEAR` accompagné d'anomalies provoquent `BoundaryError` avant construction du
registre.

La v1 exige des positions initiales nulles. C'est une limitation explicite du petit
scénario d'intégration, pas une valeur complétée silencieusement.

## 5. Provenance et empreinte du fixture

Le fixture publié est
[`synthetic_spy_bil_v1.json`](../tests/fixtures/synthetic_spy_bil_v1.json). Sa
provenance doit être exactement `SYNTHETIC`. Cette marque signifie seulement que
les nombres ont été inventés pour les tests ; elle ne certifie aucune source de
marché.

L'empreinte couvre **tous les octets exacts du fichier JSON**, du premier au dernier.
Elle est placée hors du JSON dans le fichier compagnon `.json.sha256`, ce qui évite
tout hash circulaire. L'empreinte stable v1 est :

```text
24b752be3b700dc2c4a5d1d17a74164f8c8e5708b3dfb049569d0c64c7386440
```

Le chargeur vérifie le nom, le format hexadécimal et le SHA-256 avant de décoder le
JSON. Un octet ajouté après validation suffit à faire échouer un rechargement. Le
test fixe aussi la valeur attendue dans le code de test : une modification volontaire
du fixture impose donc une mise à jour explicite des trois éléments. Un attribut Git
local au dossier désactive la conversion automatique des fins de ligne pour le JSON,
afin que les octets publiés restent identiques sous Windows et Unix.

## 6. Persistance : garantie réelle et limites

`SyntheticIntentJournal` est un journal JSON minimal de version
`synthetic_intent_journal/v1`. Avant traitement, il enregistre l'identifiant,
l'empreinte et le contenu canonique de l'intention. Après un résultat terminal, il
enregistre le statut et la trace de résultat. L'enveloppe entière possède sa propre
empreinte SHA-256 et est remplacée via un fichier temporaire.

Après rechargement, le journal vérifie son schéma, son empreinte, chaque contenu,
la relation `identifiant = SHA-256`, la présence d'un résultat terminal et la validité
du statut. Une intention terminale identique est reconnue et sa seconde exécution
est refusée avant mutation. Un même identifiant associé à un autre contenu est
également refusé.

La garantie est volontairement bornée :

| Cas | Garantie |
|---|---|
| rejeu complet depuis le même état initial avec un nouveau journal | mêmes intentions, résultats et signature comptable |
| rechargement d'un journal terminal | détection du traitement antérieur et refus du doublon |
| journal incomplet au rechargement | arrêt explicite ; aucune reprise supposée |
| reprise d'un registre comptable persisté | non implémentée |
| garantie transactionnelle après incident | non revendiquée |

Le registre reste en mémoire. Il existe donc une fenêtre d'incident entre sa
mutation et l'écriture du résultat terminal. Le journal ne peut ni déterminer seul
si cette mutation a eu lieu, ni restaurer les soldes. Pour cette raison, une entrée
sans résultat terminal est refusée au rechargement. Une vraie reprise exigerait un
registre persisté et un protocole de commit cohérent ; ils sont hors périmètre.

## 7. Séquence d'intégration artificielle

Le fixture contient trois décisions datées et des poids fournis :

1. avec 10 000 unités de cash, cible 0 % SPY : achat de 100 BIL à 100, exécuté
   puis réglé en T+2 artificiel ;
2. cible 50 % SPY : vente de 50 BIL et achat figé de 50 SPY ; l'open SPY vaut 99
   au lieu du close 100, sans redimensionnement. Le lot est accepté sous
   `H_FIN_NET` et identifié `UNSETTLED_SALE_PROCEEDS` ;
3. avant le paiement de l'achat SPY, cible 0 % SPY : la tentative de vendre les 50
   parts encore non réglées reçoit `ECONOMIC_ORDER_REJECTED`, puis le règlement
   normal intervient.

Les statuts sont donc, dans l'ordre : `EXECUTED_HYPOTHETICAL`,
`EXECUTED_HYPOTHETICAL`, `ECONOMIC_ORDER_REJECTED`. L'état final contient 50 SPY,
50 BIL et 50 unités de cash réglé, sans créance de vente, dette d'achat ou
règlement en attente. La richesse finale aux derniers prix artificiels est 10 000.

Deux exécutions complètes indépendantes depuis l'état initial produisent la même
signature, y compris les identifiants d'intention. Il s'agit d'une vérification
d'intégration synthétique, pas d'un backtest ni d'un simulateur de marché.

## 8. Atomicité, statuts et invariants financiers

Les cinq statuts existants sont conservés sans extension. Un défaut documentaire
connu est traité avant l'observation d'un nouvel open et n'autorise aucune mutation.
Un rejet économique, lui, peut survenir après la nouvelle valorisation : la variation
de valeur de marché n'est pas annulée, tandis qu'aucune transaction n'est enregistrée
et les soldes comptables restent inchangés.

La séquence et les tests antérieurs vérifient ensemble :

- `strict_temporal=True` et deux calendriers explicites distincts ;
- aucun open utilisé pour dimensionner les ordres ;
- quantités figées entre décision et exécution ;
- vente limitée aux titres réglés et payés ;
- financement net sans cash projeté négatif ;
- aucune position négative, aucun levier implicite et aucune revente prématurée ;
- conservation de richesse hors frais et variation de marché ;
- refus atomiques, distributions uniques, absence de double règlement et absence
  de double traitement d'intention.

## 9. Tests et vérifications

Les nouveaux cas couvrent notamment : intention modifiée, identifiant réutilisé,
règlement légitime entre décision et exécution, schéma/provenance/date/décimal/
symbole/prix/calendrier invalides, champ inconnu, contradiction documentaire,
empreinte de fixture altérée, rejeu identique, séquence financière complète,
journal terminal rechargé, double exécution, contenu différent, journal incomplet
et journal altéré.

Résultats du 20 octobre 2026 :

```text
python -m pytest -q
93 passed

python -m ruff check RL/scripts/synthetic_decision_adapter.py \
  RL/scripts/synthetic_input_boundary.py \
  RL/tests/test_synthetic_decision_adapter.py \
  RL/tests/test_synthetic_input_boundary.py
All checks passed!
```

Le vérificateur local confirme séparément les 49 entrées du manifeste existant.
Ces données n'ont pas été lues par la nouvelle frontière ni par ses tests.

## 10. Conditions restant requises avant l'historique

Cette étape ne lève aucune interdiction historique. Restent notamment requis :

1. l'approbation explicite du mandat, de `H_FIN_NET`, de la richesse, de la
   fréquence et de la convention d'ouverture ;
2. un calendrier officiel de règlement exhaustif et versionné pour la période visée ;
3. une définition point-in-time de disponibilité pour prix, calendriers,
   distributions et opérations sur titres ;
4. la résolution ou l'exclusion formelle du cas SPY du 20 avril 2026 ;
5. une politique documentée pour les anomalies, données absentes et versions de
   schéma historiques ;
6. un choix explicite entre simple rejeu intégral et vraie reprise transactionnelle ;
7. si une reprise est exigée, la persistance cohérente du registre et du journal ;
8. l'autorisation explicite d'une première intégration historique.

La plus petite étape scientifique suivante, soumise à autorisation, est de figer
les conventions encore ouvertes et de spécifier le mappage d'un **minuscule extrait
historique point-in-time** vers ce contrat, sans politique, backtest ni mesure de
performance. Aucun travail de cette phase suivante n'est commencé ici.
