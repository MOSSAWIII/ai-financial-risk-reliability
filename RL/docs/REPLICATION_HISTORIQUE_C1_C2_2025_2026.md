# Réplication historique C1–C2 — épisode 2025–2026

Date : 21 octobre 2026

Commit de configuration : `7372cf3db90dfcd7d8eafb06cfe9151c98bf3490`

Configuration canonique : `39c05d75a8ef83eef4601cdd9343e0c0fc0ac93c84009c389da90a250795e1b9`

Verdict : **`DOCUMENTARY_BLOCK`**

## 1. Réponse scientifique

La deuxième comparaison C1–C2 ne peut pas être exécutée fidèlement avec les sources actuellement archivées. Le calendrier reconstruit contient une décision C2 indispensable le 20 avril 2026. Pour cette date, les OHLC SPY Yahoo et Nasdaq sont mutuellement incompatibles et aucune source primaire acquise ne permet d'identifier la bonne ouverture conventionnelle.

Le verrou antérieur impose `PRICE_MISSING_OR_DISPUTED` dans cette situation. Choisir l'une des valeurs après observation, supprimer le cycle ou exécuter le lendemain modifierait les règles. Les huit cellules C2 sont donc interrompues au cycle 47 et aucune performance terminale n'est produite. Cette absence de résultat est l'application du protocole, pas un échec économique de C2.

## 2. Réponses A–U

**A. Le nouvel épisode a-t-il été verrouillé avant calcul des performances ?**

Oui. Le commit `7372cf3` contient la configuration, la grille et les sources avant tout calcul de performance. Le champ `performance_computed` vaut `false`.

**B. Quelles nouvelles sources ont été utilisées et vérifiées ?**

Le calendrier annuel officiel NYSE 2026 a été acquis le 21 octobre 2026 et vérifié sous l'identifiant `nyse_trading_calendar_2026_20261021`, SHA-256 `70f5577eb43e60a9dbbecaae3cec23d0f02028c05c7f175013bb3e97816d394f`. Les prix Yahoo SPY/BIL, les distributions State Street, le calendrier NYSE 2025, la règle SEC T+1 et le corpus DTC/NSCC 2025–2026 existants ont été réutilisés après vérification de leurs empreintes. Les 51 entrées du manifeste passent sans échec.

La recherche a également identifié NYSE Daily TAQ comme source primaire pertinente pour résoudre l'open contesté. Cette donnée historique exige un achat ou un accès autorisé et n'a pas été acquise; elle n'est donc pas utilisée.

**C. Combien de séances et de décisions hebdomadaires couvre-t-il ?**

252 séances communes du 29 mai 2025 au 29 mai 2026 et 52 décisions candidates, du 2 juin 2025 au 26 mai 2026.

**D. Combien de distributions SPY/BIL sont enregistrées ?**

16 événements : 4 SPY et 12 BIL. Ils sont énumérés avec ex-date, payment date et montant dans la configuration.

**E. Les huit cellules sont-elles complètes ?**

Non. Zéro cellule terminale complète. Le cycle 47 est indispensable aux huit cellules C2 et porte le statut `DOCUMENTARY_BLOCK`.

**F. Quelle est la richesse terminale C1 et C2 par cellule ?**

Non calculée. Publier C1 seul ou une trajectoire C2 tronquée ne répondrait pas à la comparaison appariée autorisée.

**G. Quelle est la différence de rendement C2−C1 ?**

Indisponible, car aucune paire terminale valide n'existe.

**H. Quelle politique présente le meilleur drawdown ?**

Indéterminable sur 2025–2026.

**I. Quelle politique présente la volatilité la plus faible ?**

Indéterminable sur 2025–2026.

**J. Combien de rééquilibrages C2 ont été exécutés ?**

Aucun résultat de simulation n'est publié. Il serait trompeur de traiter les cycles antérieurs au blocage comme une expérience terminale.

**K. Combien de holds et de rejets ont été observés ?**

Non calculés. Le cas du 20 avril est un défaut documentaire `NOT_EVALUABLE`, pas un rejet économique.

**L. Quels frais C2 a-t-il supportés ?**

Non calculés.

**M. Quel est l'effet de D+1 contre D+2 ?**

Non calculable sans trajectoires complètes. Le même blocage de prix affecte les deux conventions.

**N. Les identités comptables passent-elles ?**

Aucune nouvelle transaction n'a été comptabilisée, donc aucune identité quotidienne 2025–2026 n'est revendiquée. Les identités et tests antérieurs restent inchangés et réussissent.

**O. Les résultats sont-ils reproductibles ?**

Le verrou, la grille, l'inventaire des sources et le constat de blocage sont reproductibles byte-for-byte. Il n'existe pas de résultats financiers à reproduire.

**P. Les résultats 2024–2025 sont-ils intégralement préservés ?**

Oui. Les cinq empreintes C1–C2 et les sept empreintes C3 sont vérifiées avant la reconstruction du verrou; aucune ne change.

**Q. Quelles différences économiques observe-t-on entre les deux épisodes ?**

Aucune comparaison économique valide ne peut être formulée. Le seul fait nouveau est documentaire : contrairement au premier épisode, le second traverse une date d'exécution hebdomadaire dont l'open SPY est contesté entre les deux sources archivées.

**R. L'avantage de C2 se reproduit-il ou disparaît-il ?**

Indéterminable. Toute réponse chiffrée exigerait une convention ou une donnée non autorisée.

**S. Quelles limites empêchent une conclusion générale ?**

Le deuxième épisode est bloqué avant son terme; la source primaire TAQ n'est pas acquise; Yahoo Open reste un proxy conditionnel; les annonces historiques de distribution ne sont pas point-in-time; et, même après résolution, deux années consécutives et huit cellules dépendantes ne constitueraient pas des répétitions statistiques indépendantes.

**T. Combien de tests réussissent ?**

La suite complète contient 197 tests réussis : les 189 tests antérieurs et 8 tests nouveaux de verrouillage/blocage. Ruff réussit sur les fichiers concernés.

**U. Quels commits contiennent la configuration, les sources et les résultats ?**

- Configuration, manifeste de source NYSE 2026, grille et tests : `7372cf3db90dfcd7d8eafb06cfe9151c98bf3490`.
- Rapport et artefacts reproductibles du blocage : commit de publication indiqué dans le compte rendu final.
- Aucun commit de performance n'existe, conformément au blocage.

## 3. Preuve du cas bloquant

| Champ SPY, 20 avril 2026 | Yahoo | Nasdaq |
|---|---:|---:|
| Open | 708,780029 | 710,14 |
| High | 709,909973 | 710,14 |
| Low | 706,140015 | 710,14 |
| Close | 708,719971 | 710,14 |
| Volume | 43 546 800 | absent |

La valeur Nasdaq est hors de toute la plage Yahoo et réciproquement. Le contrôle local ne démontre ni erreur fournisseur ni différence de définition. La page officielle NYSE décrit Daily TAQ comme l'historique consolidé des transactions et cotations, mais son observation du 20 avril 2026 n'est pas disponible dans le patrimoine local.

## 4. Livrables publiés

- `RL/tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json` : configuration verrouillée.
- `RL/docs/grille_documentaire_c2_2025_2026.csv` : 52 décisions et statut documentaire.
- `RL/results/historical_c1_c2_2025_2026/statut_validation_documentaire.json` : portée exacte du blocage.
- `RL/results/historical_c1_c2_2025_2026/sources_configuration.csv` : sources et empreintes.
- `RL/scripts/lock_second_historical_episode.py` : reconstruction et vérification.

Les fichiers de synthèse financière, comparaison appariée, décisions exécutées, trajectoires et graphique ne sont volontairement pas créés : leur présence laisserait croire à huit cellules valides.

## 5. Reproduction

```powershell
python RL/scripts/lock_second_historical_episode.py --check --check-block
python RL/scripts/verify_local_data.py
python -m pytest -q
python -m ruff check RL/scripts/lock_second_historical_episode.py RL/tests/test_lock_second_historical_episode.py
```

## 6. Condition de levée

Le blocage peut être levé par l'acquisition et l'archivage d'une observation primaire NYSE Daily TAQ, ou d'une source équivalente explicitement autorisée, permettant de fixer avant simulation l'open SPY du 20 avril 2026. Si cette source impose une autre définition de l'open, son adoption requiert une autorisation explicite et une mise à jour versionnée du verrou; aucune substitution silencieuse n'est admise.

**`DOCUMENTARY_BLOCK`**
