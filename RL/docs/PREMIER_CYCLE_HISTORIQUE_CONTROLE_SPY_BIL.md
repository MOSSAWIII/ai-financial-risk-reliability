# Premier cycle historique contrôlé SPY–BIL

Date : 20 octobre 2026

Point de départ : `b3c17544ab3ed06185a3e095a541c963e070b66d`

Verdict : **`HISTORICAL_CYCLE_VALIDATED`**

## 1. Périmètre exact autorisé

Ce contrôle relie une seule fois quatre observations historiques déjà auditées au
registre strict : les clôtures SPY et BIL du 28 mai 2024, puis les ouvertures du
29 mai. Il se termine au règlement du 30 mai. Il ne parcourt aucun historique,
ne choisit aucune date ou allocation et ne calcule aucune performance.

La frontière dédiée
[`historical_spy_bil_single_cycle.py`](../scripts/historical_spy_bil_single_cycle.py)
accepte exclusivement `historical_spy_bil_single_cycle/v1` et la provenance
`HISTORICAL_AUDITED_PROXY`. Le contrat synthétique existant reste inchangé.

## 2. Conventions fixées avant lecture des prix

Le fixture versionné impose : compte stylisé USD sans marge, 100 000 USD de cash
réglé, aucune position, poids 50 %/50 %, parts entières, `H_FIN_NET`, frais nuls,
cash résiduel non rémunéré et `strict_temporal=True`. Le Yahoo `Close` est le
prix de décision conditionnel et le Yahoo `Open` la référence d'exécution
hypothétique. Ces choix ne peuvent être adaptés au résultat.

La frontière ne génère aucun poids et n'expose aucun mode non strict. Le fixture
a pour SHA-256 `1b1022a3fb224e68ad6b38fd73dba3e3067bba1e2d7d08323512aaacf49aa764`.

## 3. Dates et qualification

| Étape | Instant ou date | Qualification |
|---|---:|---|
| Prix de décision | clôture du 2024-05-28 | séance présente dans les deux fichiers Yahoo |
| Décision | 2024-05-29 08:00, `America/New_York` | avant l'ouverture, offset `-04:00` explicite |
| Exécution hypothétique | ouverture du 2024-05-29 | séance présente dans les deux fichiers Yahoo |
| Règlement | 2024-05-30 | T+1 explicitement documenté pour le 29 mai |

Les calendriers minimaux versionnés ne couvrent que les dates nécessaires :
28–29 mai pour la négociation et 29–30 mai pour le règlement.

## 4. Sources et empreintes

| Usage | Entrée du manifeste | SHA-256 |
|---|---|---|
| OHLCV SPY | `yahoo_spy_chart_ohlcv_20261019` | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| OHLCV BIL | `yahoo_bil_chart_ohlcv_20261019` | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| Audit des prix | `yahoo_spy_bil_market_audit_v1_20261019` | `e33ba4c2b5b962e6f46b7f37853eb73fc5bdc27269456830dbc77fb72274fe89` |
| Distributions | `ssga_spdr_distributions_20261019` | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| Règle SEC T+1 | `sec_settlement_cycle_t1_2023_20261019` | `e214bf80244fe9107c867d7abeb6a6b969029c519566036e42b081977a9b575a` |
| Guide DTCC | `dtcc_t1_conversion_guide_may2024_20261020` | `1655962c57e5a1459cf0d29c853b0bf924c3255aba5be0e0d04c4a7d2536b7f2` |

La frontière résout chaque identifiant dans le manifeste, puis vérifie taille et
empreinte avant lecture. Le PDF DTCC brut reste exclu de GitHub ; sa sauvegarde
indépendante présente la même empreinte.

## 5. Preuves point-in-time et limites

Les timestamps Yahoo situent les observations aux dates attendues. `Close` et
`Open` restent néanmoins des `MARKET_OBSERVABLE_PROXY` acquis ultérieurement :
ce ne sont ni des observations archivées le jour même, ni des fills garantis, ni
les prix officiels d'une enchère. `Adj Close` ne sert pas au dimensionnement et
la NAV ne sert pas de prix de transaction.

L'audit ne signale aucune anomalie les 28 et 29 mai. Les événements Yahoo ne
contiennent ni split ni distribution du 28 au 30 mai ; le fichier State Street
ne contient aucune ex-date, record date ou pay date SPY/BIL dans cette fenêtre.
Ce constat n'attribue aucune annonce historique connue d'avance.

## 6. Vérification du calendrier de règlement

La règle finale SEC rend le cycle standard T+1 applicable le 28 mai 2024. Elle
n'est pas utilisée seule comme calendrier. Le guide primaire DTCC de conversion
de mai 2024 distingue Memorial Day, le dernier lot T+2 et le premier lot T+1 ;
surtout, il attribue explicitement aux transactions regular-way reçues le
mercredi 29 mai une date de règlement au jeudi 30 mai.

Références primaires : [règle finale SEC](https://www.sec.gov/files/rules/final/2023/34-96930.pdf),
[confirmation SEC de l'entrée en vigueur](https://www.sec.gov/newsroom/press-releases/2024-62),
[URL d'origine du guide DTCC](https://www.dtcc.com/-/media/Files/PDFs/T2/T1-Conversion-Document-March-2024.pdf)
et [capture antérieure au cycle](https://web.archive.org/web/20240514125627id_/https://www.dtcc.com/-/media/Files/PDFs/T2/T1-Conversion-Document-March-2024.pdf).

L'URL DTCC d'origine n'étant plus servie lors de l'acquisition, le PDF a été
obtenu depuis la capture Internet Archive du 14 mai 2024, antérieure au cycle.
Cette preuve valide le calendrier minimal, pas un calendrier annuel exhaustif ni
les conditions contractuelles d'un courtier.

## 7. Quantités calculées au close

Les prix lus avant toute ouverture sont `529.8099975585938` USD pour SPY et
`91.76000213623047` USD pour BIL. Ainsi :

\[
q_{SPY}=\lfloor 50000/529.8099975585938\rfloor=94,
\qquad
q_{BIL}=\lfloor 50000/91.76000213623047\rfloor=544.
\]

Le notionnel au close vaut `99 719.58093261719288` USD et le résiduel
`280.41906738280712` USD. L'intention figée porte le SHA-256
`392857b4375dd4b2a6913be0dd5d7e2ff076189de4441dff9c8cb5544b4dc06d`.

## 8. Traitement de l'open

La trace impose : vérification du contrat et des documents, chargement des seuls
closes, scellement de l'intention, puis seulement chargement des opens. Les
références du 29 mai sont `525.6799926757812` USD pour SPY et
`91.7699966430664` USD pour BIL. Les coûts sont respectivement
`49 413.9193115234328` et `49 922.8781738281216` USD.

Le coût total, `99 336.7974853515544` USD, reste inférieur au cash réglé. Le lot
complet est accepté comme `EXECUTED_HYPOTHETICAL`. Les quantités restent 94 et
544 : aucune jambe ou quantité n'est modifiée après l'open.

## 9. Résultat comptable du lot

À la trade date, 94 SPY et 544 BIL deviennent positions économiques, avec deux
mouvements en attente et une dette d'achat de `99 336.7974853515544` USD. Le
cash réglé reste 100 000 USD et aucune position n'est encore réglée.

Le 30 mai, la dette tombe à zéro, les positions réglées deviennent 94 SPY et
544 BIL, et le cash réglé vaut `663.2025146484456` USD. Les règlements portent
les identifiants 1 et 2. Il n'existe ni vente, ni créance de distribution, ni
frais. Le mécanisme vente–achat `H_FIN_NET` n'est donc pas sollicité.

## 10. Conservation de richesse et invariants

Au prix d'exécution constant, la richesse vaut exactement `100000` USD avant et
après le transfert de règlement. Sont aussi vérifiés : cash non négatif,
positions économiques inchangées, transfert exact vers les positions réglées,
extinction unique des dettes, aucune créance ou dette dupliquée, zéro frais et
zéro mouvement résiduel. Cette identité comptable n'est pas un rendement.

## 11. Rejets exercés et causes

Le cycle réel n'est ni rejeté ni bloqué. Les tests isolés démontrent néanmoins
les arrêts prescrits : document ou calendrier manquant et prix contesté donnent
`HISTORICAL_CYCLE_NOT_EVALUABLE` avant mutation ; empreinte erronée, date
incohérente ou open futur utilisé pour décider donnent
`HISTORICAL_CYCLE_FAILED`. Une intention altérée est refusée atomiquement comme
`INVALID_INPUT`.

## 12. Limites scientifiques et opérationnelles

Cette preuve ne valide qu'un chemin sur un cycle présélectionné. Elle ne valide
ni l'allocation 50/50, ni une performance, ni un fill, ni spread, impact, taxes,
frais ou courtier. Elle ne teste pas historiquement vente, rééquilibrage,
distribution, opération sur titres, gap non finançable ou reprise après incident.
Elle ne complète pas le calendrier 2018–2026 et n'autorise aucun second cycle,
benchmark, politique ou modèle RL.

## 13. Verdict sur la faisabilité de l'intégration historique

Le verdict est **`HISTORICAL_CYCLE_VALIDATED`**. Pour le seul cycle prescrit, les
sources et le règlement sont suffisamment documentés, les quantités sont
calculées avec l'information admissible et scellées avant l'open, puis le lot
traverse correctement l'adaptateur et le registre strict jusqu'au règlement.

La conclusion est volontairement modeste : une observation historique qualifiée
peut alimenter une intention figée puis une comptabilité temporelle cohérente,
sans fuite future détectée. Toute étape suivante devra être autorisée séparément.
