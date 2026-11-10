# G3A — reproduction empirique indépendante, 10 novembre 2026

**Statut :** `INDEPENDENT_REPLICATION_POSITIVE_PENDING_CANONICAL_REEXECUTION`.

Ce rapport documente une reproduction indépendante des équations du protocole G3 gelé, fondée sur la sauvegarde originale `2026-10-19.zip`. Il ne prétend pas que le script canonique GitHub `RL/scripts/g3_learning_value.py` a été exécuté dans son environnement de dépôt. Les deux sources brutes Yahoo ne sont pas publiées dans GitHub.

## Identité documentaire

- SPY Yahoo (541 190 octets) : SHA-256 `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52`.
- BIL Yahoo (522 516 octets) : SHA-256 `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2`.
- Protocole G3 gelé : SHA-256 `5caba8a67da6a8ceef721ad2ddc2dde1d9a3cee7780674d6d7cd40309afefd79` (texte de GitHub).
- Fenêtre : décisions 2025-06-02 → 2026-04-13, close terminal 2026-04-17 ; 46 décisions.

## Critère primaire gelé

| Politique | Richesse terminale USD | Volatilité annualisée | Drawdown maximal | Turnover cumulé |
|---|---:|---:|---:|---:|
| `D_G2_FROZEN` | 112 178,85 | 7,30 % | 4,40 % | 8,50 |
| `D_G3_LEARNED` | 117 476,70 | 11,25 % | 9,12 % | 0,50 |
| `M_G3_LEARNED` | 117 476,70 | 11,25 % | 9,12 % | 0,50 |

**Différence appariée G3A : +5 297,85 USD**, dépassant le seuil préfigé de +250 USD ; donc verdict du critère primaire, **`G3_LEARNING_VALUE_POSITIVE`** sous reproduction indépendante.

Attention : la volatilité de la stratégie apprise est plus élevée d'environ 3,95 points et son maximum drawdown d'environ 4,72 points. Aucune dominance générale en risque n'est démontrée.

## Diagnostic bloquant pour toute revendication de valeur RL

Après quatre décisions de warm-up communes à 50/50, `D_G3_LEARNED` bascule à **100 % SPY le 30 juin 2025 et y reste pendant les 42 décisions restantes**. Les actions, les coûts et la richesse sont rigoureusement identiques pour `D_G3_LEARNED`, `M_G3_LEARNED` et un contrôleur statique 100 % SPY après warm-up. L'écart positif ne révèle donc **aucune valeur additionnelle observée de la programmation dynamique, de la transition de Markov apprise, ni de la complexité RL**. La différence ne concerne que le contrôleur stylisé G2.

## Reproductibilité et limitations

La reproduction indépendante a produit quatre CSV, dont les SHA-256 sont consignés dans [l'inventaire](../results/g3_learning_value/independent_replication_audit.json). Les 17 contrôles d'audit supplémentaires vérifient l'identité des sources, le calendrier, le warm-up, l'absence de fuite à travers la période G2, les chocs futurs, l'égalité myope/dynamique et la reproductibilité octet pour octet.

**Ne pas lire ces chiffres comme un backtest investissable** : proxy close-à-close de prix Yahoo non ajustés pour les distributions, sans exécution effective, bid/ask, parts entières ou règlement. Le signal utilise le close courant et le rendement démarre sur ce même close. Ce résultat n'autorise pas PPO ni une conclusion de généralisation.

## Action requise

Exécuter le script officiel `RL/scripts/g3_learning_value.py` sur le clone possédant les deux JSON vérifiés ; comparer les quatre CSV aux empreintes publiées. Ne convertir le statut en `G3A_CANONICAL_VALIDATED` qu'en cas de concordance exacte, puis décider séparément si G3B apporte une question scientifique nouvelle.
