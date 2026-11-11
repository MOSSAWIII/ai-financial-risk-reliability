# Validation G4.1 — disponibilité et audit structurel des données

## Décision

**G4.1 est validé.** Les dix exigences documentaires gelées sont présentes,
leurs octets locaux concordent avec les empreintes SHA-256 attendues, et
l'audit structurel des quatre instruments ne détecte aucun défaut bloquant.

Cette décision autorise uniquement la construction déterministe du jeu de
données G4 et ses contrôles. Elle n'autorise ni entraînement, ni sélection de
modèle, ni mesure de performance. PPO, CQL et IQL restent hors périmètre.

## Sources ajoutées

| Instrument | Rôle | Empreinte SHA-256 |
|---|---|---|
| IEF | Yahoo OHLCV quotidien | `9daa83ee383e208e1b4c09e0148b19f92d82049056e71a967323cd54dc744108` |
| IEF | classeur officiel iShares | `5558efd11d698945862e4f11f68ec9cd3faeb8a732cad4ec05704e18fab0b275` |
| GLD | Yahoo OHLCV quotidien | `39b8398c597fb20f03330319904ae9f9549b84e8e6b66d32e509a80daeae4172` |
| GLD | archive historique officielle SPDR | `85c8770862db5a1411e29e2021d81e0f42240832ab7fdfd3f2a63d9ff66ccd04` |

Les octets bruts restent exclus du dépôt. Le manifeste, le code d'acquisition,
les empreintes et les rapports reproductibles sont versionnés.

## Résultats structurels

| Contrôle | SPY | IEF | GLD | BIL |
|---|---:|---:|---:|---:|
| Observations | 4 880 | 4 880 | 4 880 | 4 878 |
| Début | 2007-05-25 | 2007-05-25 | 2007-05-25 | 2007-05-30 |
| Fin | 2026-10-16 | 2026-10-16 | 2026-10-16 | 2026-10-16 |
| Lignes OHLC invalides | 0 | 0 | 0 | 0 |
| Lignes avec valeur manquante | 0 | 0 | 0 | 0 |
| Valeurs de prix non positives | 0 | 0 | 0 | 0 |
| Événements de distribution Yahoo | 78 | 233 | 0 | 128 |
| Événements de split Yahoo | 0 | 0 | 0 | 1 |

L'intersection exacte contient **4 878 séances**, du **2007-05-30** au
**2026-10-16**. Les deux dates supplémentaires de SPY, IEF et GLD précèdent la
première observation BIL; aucune divergence calendaire subsiste ensuite dans
les fichiers acquis.

Le classeur iShares contient les sections `Historical` et `Distributions` avec
les champs `Record Date`, `Ex-Date`, `Payable Date` et `Total Distribution`.
L'archive SPDR contient la feuille `US GLD Historical Archive`, 5 734 lignes
en-têtes comprises, et les champs de date, NAV, or par part, volume et actif
net du trust attendus.

## Limites maintenues

- Les OHLCV Yahoo restent des proxys de fournisseur, pas des prix d'exécution.
- Le contrôle présent ne valide ni spread, ni slippage, ni profondeur.
- Aucun rendement, ratio de performance ou signal de récompense n'est calculé.
- Les distributions doivent encore être transformées selon une convention
  point-in-time explicite avant de former les transitions du problème G4.

## Étape suivante autorisée

**G4.2 : construire et geler le jeu de transitions point-in-time** pour
SPY–IEF–GLD–BIL, avec calendrier commun, distributions, état du budget de
rotation et contrôles anti-fuite. La comparaison entre contrôleur classique et
apprentissage ne commencera qu'après ce nouveau gel.
