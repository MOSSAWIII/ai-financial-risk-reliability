# Verrouillage du deuxième épisode C1–C2 — 2025–2026

Date de verrouillage : 21 octobre 2026

Référence antérieure : `893afda71ed930b5eec8a95058ebcfca962f49b1`

Configuration : `RL/tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json`

SHA-256 canonique de configuration : `39c05d75a8ef83eef4601cdd9343e0c0fc0ac93c84009c389da90a250795e1b9`

Statut documentaire avant performance : **`DOCUMENTARY_BLOCK`**

## 1. Objet du verrou

Ce verrou est enregistré avant tout calcul de performance du deuxième épisode. Il fixe une réplication temporelle exploratoire du 29 mai 2025 au 29 mai 2026, initialisée indépendamment avec 100 000 USD. Le choix de cette période intervient après observation du premier épisode et n'est donc pas présenté comme confirmatoire.

Les politiques restent inchangées : C1 achète initialement 50/50 SPY–BIL puis conserve; C2 partage exactement cet achat initial puis vise chaque semaine 50/50 du budget admissible E-B. Les décisions récurrentes ont lieu à 08:00 ET lors de la première séance NYSE de la semaine, à partir du dernier close admissible. L'open du jour ne peut être lu qu'après scellement.

Les cellules S0–S3 × D+1/D+2, les parts entières, T+1, `H_FIN_NET`, les distributions économiques, l'absence d'emprunt/short/découvert et le rejet sans redimensionnement sont repris sans recalibrage. C3 est absent.

## 2. Couverture reconstruite

- Close initial : 28 mai 2025.
- Exécution initiale candidate : 29 mai 2025.
- Règlement initial T+1 : 30 mai 2025.
- Terminal commun : 29 mai 2026, sans liquidation fictive.
- Séances communes SPY/BIL : **252**.
- Décisions hebdomadaires candidates : **52**, du 2 juin 2025 au 26 mai 2026.
- Distributions : **16**, dont 4 SPY et 12 BIL.
- Première séance de chaque semaine et close antérieur reconstruits sans supposer 52 décisions à l'avance.

La grille complète est publiée dans `RL/docs/grille_documentaire_c2_2025_2026.csv`.

## 3. Sources verrouillées

| Usage | Identifiant | SHA-256 principal | Couverture |
|---|---|---|---|
| SPY Open/Close | `yahoo_spy_chart_ohlcv_20261019` | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` | 2007-05-25–2026-10-16 |
| BIL Open/Close | `yahoo_bil_chart_ohlcv_20261019` | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` | 2007-05-30–2026-10-16 |
| Audit des prix | `yahoo_spy_bil_market_audit_v1_20261019` | `e33ba4c2b5b962e6f46b7f37853eb73fc5bdc27269456830dbc77fb72274fe89` | jusqu'au 2026-10-16 |
| Distributions | `ssga_spdr_distributions_20261019` | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` | SPY/BIL jusqu'en 2026 |
| NYSE 2025 | `nyse_trading_calendars_2022_2025_20261019` | `2c2e63b780c4a373d8d546904ae46c8ba7e8070ad9357d23d2c92749985bb6c9` | calendriers 2022–2025; fichier 2025 additionnel vérifié |
| NYSE 2026 | `nyse_trading_calendar_2026_20261021` | `70f5577eb43e60a9dbbecaae3cec23d0f02028c05c7f175013bb3e97816d394f` | année civile 2026 |
| Règle T+1 | `sec_settlement_cycle_t1_2023_20261019` | `e214bf80244fe9107c867d7abeb6a6b969029c519566036e42b081977a9b575a` | régime T+1 depuis le 28 mai 2024 |
| DTC/NSCC | `dtcc_settlement_documentary_bundle_20261020` | `129d15810713a064d4de9aaf0bdd60319ae9065260268caa4f66976f84a1bf6e` | règles et traitement 2025–2026; fichiers additionnels vérifiés |

Le calendrier NYSE 2026 officiel a été acquis le 21 octobre 2026 et ajouté séparément au manifeste. Les 51 entrées du manifeste passent leur contrôle d'empreinte. Les calendriers annuels et les dates Yahoo concordent sur toute la fenêtre.

## 4. Blocage documentaire préexistant confirmé

Le cycle 47 doit utiliser le close du 17 avril 2026 et l'open SPY du 20 avril 2026. Les deux sources locales disponibles sont incompatibles :

| Source | Open | High | Low | Close | Volume |
|---|---:|---:|---:|---:|---:|
| Yahoo | 708,780029 | 709,909973 | 706,140015 | 708,719971 | 43 546 800 |
| Nasdaq | 710,14 | 710,14 | 710,14 | 710,14 | absent |

L'open Nasdaq est hors de la plage Yahoo et l'open Yahoo est hors de la plage Nasdaq. Aucun document local ne démontre une différence de définition ni une erreur de fournisseur. L'anomalie avait déjà été classée `CAS_NON_RESOLU` et `PRICE_MISSING_OR_DISPUTED` avant l'autorisation du deuxième épisode.

La recherche ciblée retrouve le produit primaire NYSE Daily TAQ, qui couvre les transactions consolidées mais exige un achat ou un accès autorisé. Aucune observation primaire gratuite permettant d'arbitrer cette date n'a été trouvée. Choisir Yahoo parce qu'il fournit une trajectoire complète, reprendre Nasdaq ou supprimer la décision constituerait un changement ex post interdit.

Le cycle 47 est donc `DOCUMENTARY_BLOCK` et affecte les huit cellules C2. Conformément au contrat, une décision `NOT_EVALUABLE` indispensable interrompt la cellule. Aucune performance terminale C1–C2 n'est calculée sous ce verrou.

## 5. Reproduction du verrou

```powershell
python RL/scripts/lock_second_historical_episode.py --check
python -m pytest -q RL/tests/test_lock_second_historical_episode.py
python -m ruff check RL/scripts/lock_second_historical_episode.py RL/tests/test_lock_second_historical_episode.py
python RL/scripts/verify_local_data.py
```

Le passage aux performances exige une source primaire acquise et archivée qui résout l'open SPY du 20 avril 2026, puis une nouvelle autorisation explicite si sa convention diffère de Yahoo `Open`. Le verrou interdit toute substitution silencieuse.
