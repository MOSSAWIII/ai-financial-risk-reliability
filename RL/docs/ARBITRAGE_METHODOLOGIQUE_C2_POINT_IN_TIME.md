# Arbitrage méthodologique C2 point-in-time

## 1. Problème scientifique exact

L'objectif futur est de comparer une allocation SPY–BIL 50/50 conservée (C1) à la même allocation rééquilibrée chaque semaine (C2). La difficulté n'est pas d'inventer une trajectoire plus complète, mais de séparer trois objets :

- ce qu'un décideur aurait pu utiliser à 08:00 ET;
- ce que le portefeuille possédait économiquement, y compris les droits acquis;
- ce qui pouvait effectivement financer des achats.

La grille stricte de 52 décisions reste inchangée. Elle établit une insuffisance de preuve, non une preuve que les distributions étaient inconnues de tous les investisseurs. Inversement, le classeur State Street acquis en 2026 établit les événements réalisés, pas leur connaissance historique à la décision.

Ce rapport arbitre les conventions d'une expérience conditionnelle. Il n'exécute aucune décision historique, ne construit aucune position C2 et ne calcule aucune performance.

## 2. Les cinq catégories de faits et conventions

| Catégorie | Éléments concernés | Traitement |
|---|---|---|
| Information historiquement absente ou contradictoire | Horodatages d'annonce des 16 distributions; heure de crédit d'un compte client inexistant | Ne jamais déclarer le fait connu; protocole S bloqué lorsqu'il en dépend |
| Proxy non certifié point-in-time | Closes et opens Yahoo actuels | Admissible seulement dans E, avec étiquette permanente de proxy conditionnel |
| État hypothétique endogène | Titres détenus, droits effectivement acquis, cash hérité | Ne peut être résolu avant la trajectoire; conserver `IF_RELEVANT_ASSET_HELD` |
| Convention préspecifiable | Délai de cash, budget partiel, règle de non-financement, arrêt | Peut être fixée ex ante sans devenir un fait historique |
| Information indispensable au 50/50 | Marks de décision admissibles, positions héritées, budget de politique et cash finançable | Doit être déterminée ou la décision reste non évaluable |

Le montant d'une créance inconnue n'est indispensable que si la politique prétend cibler 50/50 sur la richesse économique totale. Il ne l'est pas pour une politique explicitement définie sur un budget partiel qui exclut ce montant.

## 3. Deux protocoles scientifiques distincts

### Protocole S — strict point-in-time

S conserve exactement les protections actuelles du `DecisionSnapshot` :

- toute créance dont le montant nécessaire au dimensionnement n'est pas prouvé comme connu rend la décision `NOT_EVALUABLE`;
- un paiement sans preuve de disponibilité avant 08:00 ne finance rien;
- un open du jour n'entre jamais dans l'instantané de décision;
- les 52 lignes et leurs statuts stricts ne sont pas reclassés.

Résultat inchangé : 0 `READY_DOCUMENTARY`, 20 `PARTIALLY_DOCUMENTED` et 32 `NOT_EVALUABLE_DOCUMENTARY`.

### Protocole E — exploratoire historique conditionnel

E est une expérience de recherche sous conventions, pas une réplication certifiée d'un compte de 2024. Il peut utiliser :

- la close Yahoo précédente comme mark conditionnel du budget;
- l'open Yahoo suivant comme référence hypothétique d'exécution, observée seulement après la décision;
- les dates T+1 documentées;
- une règle préspecifiée de disponibilité du cash;
- un budget C2 partiel distinct de la richesse économique.

Les résultats futurs devront porter simultanément les libellés `EXPLORATORY_CONDITIONAL` et `MARKET_OBSERVABLE_PROXY`. Aucun résultat E ne pourra être présenté comme résultat S.

## 4. Alternatives pour les créances inconnues

### Option A — blocage strict

Le montant exact de toute créance potentiellement acquise doit être prouvé connu. Si le titre concerné est détenu, les 32 décisions exposées restent bloquées; les 20 autres sont potentiellement évaluables sous les autres conventions E.

Avantage : rigueur maximale. Limite : elle empêche l'expérience pour une absence d'archive qui n'établit pas l'ignorance réelle.

### Option B — budget décisionnel conservateur

Le budget de C2 comprend uniquement :

- les actifs marqués selon la référence de décision préspecifiée;
- le cash devenu admissible selon la convention de compte;
- les créances dont le montant est prouvé connu, si le protocole décide de les inclure au budget.

Une créance de montant non vérifié est conservée dans la comptabilité économique, mais exclue du budget et du financement. Changer son montant ex post ne peut donc changer la décision préparée. Les conséquences attendues sont un sous-investissement relatif, une dérive par rapport au 50/50 de richesse totale et une possible accumulation temporaire de valeur hors budget. Ces effets sont une caractéristique déclarée de C2-E, pas une erreur à corriger rétrospectivement.

Le rendement économique futur inclurait toujours le droit acquis puis son cash; seul le chemin d'exposition décidé peut différer parce que cette valeur ne participe temporairement pas au dimensionnement. Une comparaison équitable avec C1 doit donc conserver le droit dans les deux richesses économiques tout en attribuant à C2 seul les conséquences de son budget prudent.

Une cible 50/50 reste interprétable si elle est nommée précisément : **50/50 des actifs admissibles au budget décisionnel**, et non 50/50 de la richesse économique totale.

### Option C — information reconstruite conditionnelle

Le montant réalisé est supposé connu avant la décision malgré l'absence d'archive d'annonce. Cette option permettrait potentiellement de traiter les 32 lignes, mais introduit une fuite d'information non réfutée. Elle ne convient qu'à une sensibilité explicitement qualifiée de `LOOK_AHEAD_RISK`, jamais au protocole principal.

### Recommandation

Retenir B comme protocole E principal; conserver A comme référence stricte et C comme diagnostic secondaire non probant. B répond à une question financière distincte mais valide : comment une politique se comporte-t-elle lorsqu'elle refuse volontairement de dimensionner sur une valeur non prouvée comme connue ?

## 5. Disponibilité du cash après paiement

Trois conventions ont été examinées :

| Convention | Information admissible à 08:00 | Effet sur financement | Risque |
|---|---|---|---|
| Premier jour ouvré suivant la payment date (`D+1`) | Payment date réalisée et premier jour DTC ultérieur atteint | Cash finançable à 08:00 de D+1 | Crédit hypothétique, mais jamais le jour même |
| Deuxième jour ouvré (`D+2`) | Même règle avec un jour ouvré supplémentaire | Retarde cinq décisions de la grille | Plus conservateur, toujours hypothétique |
| Preuve indépendante seulement | Horodatage de compte ou dépositaire | Aucun cash sans preuve | Reproduit S et laisse 51 alertes sans compte réel à observer |

La convention principale recommandée est **D+1 à 08:00 ET**. La sensibilité unique est **D+2 à 08:00 ET**. Un paiement daté du jour n'est jamais disponible à 08:00 ce même jour.

D+2 affecte cinq décisions par rapport à D+1 : 8 juillet, 9 septembre et 7 octobre 2024, puis 3 février et 7 avril 2025. Cette différence résulte des paiements du vendredi; elle ne préjuge pas de la possession des titres.

La payment date transforme une créance en cash économique. La date conventionnelle D+1 ou D+2 détermine seulement quand ce cash entre dans `financing_cash`.

## 6. Démonstration économique de l'ex-date

Exemple artificiel sans mouvement de marché :

- 100 parts;
- close cum-distribution : 100;
- distribution par part : 2;
- prix mécanique ex-distribution : 98.

Avant détachement :

\[
W_{avant}=100\times100=10\,000.
\]

Après détachement :

\[
W_{après}=100\times98+100\times2=9\,800+200=10\,000.
\]

L'identité économique est conservée. La créance remplace la baisse mécanique de la valeur des parts.

La formule incorrecte serait :

\[
100\times100+200=10\,200.
\]

Elle ajoute une créance au prix cum-distribution qui la contenait encore économiquement et la compte deux fois.

## 7. Résolution du double comptage

Trois cas doivent être distingués.

1. **Budget arrêté à la close cum antérieure.** Le budget garde le mark antérieur et n'ajoute pas la créance courante inconnue. Il représente un budget ancré à la close précédente, pas la richesse exacte à 08:00.
2. **Comptabilité économique avec mark ex-cohérent.** Dès qu'un prix ex est utilisé pour valoriser les parts, la créance acquise est comptabilisée séparément. L'identité économique est alors préservée.
3. **Richesse exacte prétendue à 08:00.** Si le montant requis ou un mark admissible manque, S classe la décision `NOT_EVALUABLE`. Soustraire ex post le dividende réalisé de la close n'est pas autorisé dans S.

La recommandation E est le cas 1 pour le dimensionnement, puis le cas 2 pour la comptabilité économique après observation de l'open ou d'un close ex. Le budget antérieur et la richesse économique ne doivent jamais être additionnés entre eux.

## 8. Tests artificiels

Le module [analyze_c2_conditional_protocol.py](../scripts/analyze_c2_conditional_protocol.py) contient uniquement des identités arithmétiques, des coupures temporelles et la dérivation documentaire. Les neuf tests ajoutés établissent :

- l'identité 10 000 avant/après détachement et l'erreur 10 200;
- la séparation entre richesse économique, budget, valeur exclue et financement;
- l'invariance du budget au montant d'une créance cachée;
- l'impossibilité de financer avec du cash payé mais pas encore disponible;
- la différence entre D+1 et D+2, week-ends compris;
- l'exclusion de l'open de 09:30 d'une décision à 08:00;
- l'ordre close, droit, décision, open;
- le maintien du caractère figé de `DecisionSnapshot`;
- la conservation des statuts stricts dans la grille dérivée.

Ces tests sont indépendants des prix SPY/BIL. Ils n'appellent ni registre historique ni politique C2.

La suite complète contient désormais **151 tests réussis** (142 antérieurs et 9 nouveaux). Les fichiers ajoutés passent Ruff.

## 9. Couverture documentaire S contre E

La grille complémentaire [grille_conditionnelle_c2_2024_2025.csv](grille_conditionnelle_c2_2024_2025.csv) dérive les trois options ligne par ligne sans remplacer [la grille stricte](grille_documentaire_c2_2024_2025.csv).

Son empreinte SHA-256 est `d8f58b1bba900573d7b15cdf3af6d4d3648233d33746d6b3eb9e67758ea7af59`; `python RL/scripts/analyze_c2_conditional_protocol.py --check` en vérifie la reproduction exacte.

| Protocole / option | `CONDITIONALLY_DOCUMENTED` | `CONDITIONAL_WITH_OPEN_ASSUMPTIONS` | `BLOCKED_EVEN_CONDITIONALLY` |
|---|---:|---:|---:|
| E avec A — blocage du droit inconnu | 20 | 0 | 32 potentielles si le titre est détenu |
| E avec B — budget conservateur | 52 | 0 | 0 |
| E avec C — montant réalisé supposé connu | 20 | 32 | 0 |

Les 52 lignes de B sont **potentiellement évaluables après approbation des conventions et construction de l'état hérité**. Elles ne sont pas `READY`, car aucune position C2 n'existe encore. Le statut `IF_RELEVANT_ASSET_HELD` reste attaché aux événements de distribution.

Dans C, `CONDITIONAL_WITH_OPEN_ASSUMPTIONS` désigne une hypothèse scientifique non résolue — la connaissance du montant — et non l'open de marché. Dans toutes les options E, Yahoo Open demeure un proxy d'exécution explicite.

## 10. Cas du 3 juin 2024

Sous S, la décision reste `NOT_EVALUABLE` si BIL est détenu : le droit du 3 juin peut être acquis, mais son montant n'est pas prouvé connu.

Sous E-B :

1. le budget est arrêté aux marks du 31 mai;
2. la créance BIL du 3 juin n'est pas ajoutée à ce budget;
3. elle ne finance aucun achat;
4. l'open du 3 juin n'est lu qu'après scellement de la décision;
5. la comptabilité économique reconnaît ensuite le droit réalisé avec une valorisation ex-cohérente;
6. son cash ne devient finançable qu'à D+1 après la payment date du 6 juin, soit le 7 juin selon la convention principale.

Le budget du 31 mai n'est pas appelé « richesse de marché à 08:00 le 3 juin ».

## 11. Comparabilité future de C1 et C2

C1 et C2 devront partager : capital initial, sources, calendrier économique, traitement des distributions, convention D+1 ou D+2, coûts S0–S3, financement `H_FIN_NET`, dates de valorisation et terminal.

La richesse économique comparable sera calculée avec la même identité pour les deux politiques : valeur des positions au même mark, cash économique, créances acquises, autres créances et dettes. Le budget partiel de C2 ne modifiera jamais cette mesure commune.

C1 conserve ses positions et n'est pas soumis à des décisions fictives. C2 seul applique hebdomadairement sa cible au budget admissible. Une dérive de C2 due à l'exclusion d'une créance appartient à la politique; elle ne justifie ni de retirer la créance de sa richesse économique ni de modifier C1.

Si une source commune nécessaire à la valorisation économique échoue, la comparaison appariée s'arrête pour les deux. Si une décision C2 reste indéterminée, C1 peut demeurer descriptif, mais aucune comparaison finale C1–C2 n'est publiée pour l'épisode incomplet.

## 12. Conventions recommandées pour approbation

1. Yahoo Close et Open restent des proxys exploratoires conditionnels; Open n'est jamais visible à 08:00.
2. Le budget C2 est la valeur des actifs admissibles aux marks de décision plus les flux connus admissibles, distincte de la richesse économique.
3. Une créance inconnue est préservée économiquement mais exclue du budget et du financement.
4. À l'ex-date, la close cum antérieure et la créance courante ne sont jamais additionnées; le budget reste ancré à la close précédente jusqu'à un mark ex-cohérent.
5. Le cash payé devient disponible à 08:00 le premier jour ouvré DTC suivant la payment date; D+2 est la sensibilité conservatrice.
6. Comptabiliser un montant ne le rend pas automatiquement finançable.
7. Si le budget admissible est déterminé mais insuffisant, aucune dépense hors budget n'est autorisée; si le budget est indéterminé, la décision est `NOT_EVALUABLE`, sans imputation.
8. Toute défaillance de comptabilité économique commune ou toute décision C2 indispensable non évaluable bloque la comparaison appariée finale.
9. Les seules sensibilités méthodologiques sont A, B-D+2 et C avec avertissement de fuite; les coûts S0–S3 existants restent inchangés.
10. Avant exécution, ces conventions doivent être approuvées, traduites dans une extension séparée du snapshot, testées sur une séquence entièrement artificielle puis gelées.

Ces conventions ne sont pas sélectionnées pour améliorer le rendement de C2.

## 13. Risques résiduels et prochaine étape minimale

Risques subsistants : révisions possibles des barres Yahoo, absence de preuve de publication des distributions, open non exécutable garanti, staleness du budget à la close antérieure, hypothèse de compte D+1/D+2, dépendance aux positions futures, et effets ultérieurs des parts entières et des coûts.

L'option B évite une fuite directe du montant inconnu, mais elle change l'objet de la cible 50/50. Elle ne prouve pas ce qu'un investisseur réel savait. L'option C ne peut pas démontrer l'absence de look-ahead bias.

La prochaine étape minimale est une **approbation conjointe des dix conventions ci-dessus**. Après cette approbation seulement, il faudra étendre minimalement le snapshot synthétique pour représenter `economic_wealth`, `decision_budget`, `excluded_claims` et `financing_cash`, puis valider une séquence artificielle. Aucune exécution historique ne doit commencer dans cette phase.

Verdict : **`CONDITIONAL_PROTOCOL_READY_FOR_APPROVAL`**. Le protocole E-B est économiquement cohérent et reproductible comme hypothèse de recherche, tout en restant explicitement distinct de S. Il n'est pas encore autorisé ni exécuté.
