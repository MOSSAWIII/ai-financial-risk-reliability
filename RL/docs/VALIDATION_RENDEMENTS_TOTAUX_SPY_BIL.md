# Validation de la reconstruction des rendements totaux SPY–BIL

**Millésime :** 19 octobre 2026

**Statut final :** `AUDITED`

## Conclusion

Deux séries quotidiennes de rendement total à la NAV ont été reconstruites hors ligne à partir des NAV et distributions officielles State Street. Les identités comptables, l'alignement temporel, l'intégration unique des distributions et la reproductibilité binaire sont vérifiés. La période commune va du **30 mai 2007 au 15 octobre 2026** : 4 880 dates de NAV et 4 879 rendements pour chacun des deux instruments.

Le statut reste `AUDITED`, et non `VALIDATED_FOR_USE`, pour deux raisons :

1. le fractionnement inversé BIL du 30 novembre 2017 est fortement corroboré par les trois champs du fichier officiel, mais aucune seconde source locale ne le confirme explicitement;
2. aucune référence indépendante locale de rendement total à la NAV, construite selon la même convention, n'est disponible.

Ces réserves n'invalident pas les calculs. Elles limitent la force de la validation et interdisent de présenter les séries comme des rendements exécutables ou comme la base déjà autorisée d'un backtest.

## Sources vérifiées avant transformation

| Objet | Couverture utilisée | SHA-256 |
|---|---|---|
| NAV SPY State Street | 2003-12-01–2026-10-15 | `80deb8db0ca46881dbec2b521487389d7c2290233ffe40b45c46b9c33699565f` |
| NAV BIL State Street | 2007-05-30–2026-10-15 | `13ac00ae7dd64308bd1e548386a5fe8ae51c0f3983b51d2f2dd3789bbc3ae68a` |
| Distributions SPDR | SPY depuis 1993; BIL depuis 2007 | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| Clôtures Nasdaq SPY, contrôle partiel | 2016-10-17–2026-10-16 | `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5` |
| Premium/discount SPY, contrôle partiel | 2025-01-02–2026-10-16 | `afac89e371da667234881bb5a7e6607c9105061540576e3667f91d2f63ba12a9` |

La procédure échoue avant tout calcul si un fichier, sa taille ou son empreinte diffère du manifeste. Aucun téléchargement, écrasement du brut ou remplissage de date n'est effectué.

## Convention économique et mathématique

Pour une part détenue à la fin de `t-1`, notons :

- `N_t` la NAV par part courante;
- `D_t` la somme du dividende, du gain en capital court terme et du gain en capital long terme attribuée à l'ex-date;
- `q_t` le nombre de parts courantes obtenu par part précédente après une opération sur titres.

Le rendement de prix ajusté d'une opération sur titres et le rendement total sont :

\[
R_t^{prix}=\frac{q_tN_t}{N_{t-1}}-1,
\qquad
R_t^{TR}=\frac{q_t(N_t+D_t)}{N_{t-1}}-1.
\]

Le facteur de croissance vaut `1 + R_t^{TR}` et l'indice commence à 100 à la première NAV. La première ligne ne possède donc pas de rendement; le premier rendement est défini à la NAV suivante.

L'indice suppose le réinvestissement conventionnel de la distribution à la NAV de l'ex-date. Il mesure correctement la performance économique sous cette convention, mais ne simule pas la trésorerie d'un investisseur : le cash n'est réellement versé qu'à la date de paiement. Les frais internes déjà incorporés à la NAV ne sont pas déduits une seconde fois. Aucun spread, slippage, commission ou impôt n'est inclus.

## Résultats quantitatifs

| Série | Dates NAV | Rendements | Distributions utilisées | Indice terminal, base 100 | Rendement quotidien min/max |
|---|---:|---:|---:|---:|---:|
| SPY | 5 758 | 5 757 | 93 | 1 091,5413 | −11,9231 % / +11,5606 % |
| BIL | 4 880 | 4 879 | 232 | 130,8906 | −0,1631 % / +0,0998 % |

Les 43 distributions SPY antérieures au début de la NAV locale sont conservées dans le brut, mais ne sont pas utilisées. Toutes les distributions situées dans les fenêtres NAV correspondent à une date de NAV : zéro date non appariée pour SPY et BIL. Les sommes par part intégrées correspondent exactement aux sources dans chaque fenêtre : 98,604857 USD pour SPY et 22,480954 USD pour BIL.

Les 232 lignes BIL comprennent 105 enregistrements dont le montant total est nul, surtout pendant les années de taux proches de zéro. Le fichier dérivé distingue donc l'existence d'un enregistrement de distribution de la positivité de son montant.

Dans le fichier de distributions, chaque instrument conserve un CUSIP unique sur toute la période (`78462F103` pour SPY, `78468R663` pour BIL); la fréquence déclarée reste trimestrielle pour SPY et mensuelle pour BIL. Aucun changement de structure supplémentaire n'est donc documenté par ces champs. Cela ne constitue pas une preuve qu'aucun autre événement sur titres n'a existé.

## Contrôles comptables et temporels

- Dates NAV dupliquées : 0 pour SPY et BIL.
- NAV manquantes ou non positives : 0.
- Dates ex-dividende dupliquées ou sans NAV dans la fenêtre : 0.
- Erreur maximale de l'identité `facteur = 1 + rendement` : 0.
- Erreur maximale entre ratio de l'indice cumulatif et facteur de croissance : `3,33 × 10⁻¹⁶` pour SPY et `2,22 × 10⁻¹⁶` pour BIL.
- Calendriers SPY et BIL sur la période commune : 4 880 dates communes, 0 date propre à un seul instrument.
- Dates calendaires ajoutées artificiellement : 0.
- Trois productions indépendantes à partir des mêmes sources donnent les mêmes quatre empreintes de sortie.

SPY possède 628 dates, de décembre 2003 à mai 2006, où les champs `Shares Outstanding` et `Total Net Assets` contiennent `-`. La NAV reste complète. Ces champs auxiliaires sont conservés comme manquants et n'entrent pas dans le rendement.

## Opération sur titres BIL

Le 30 novembre 2017 présente simultanément :

- ratio de NAV : `2,000123805`;
- ratio des parts en circulation : `0,5`;
- ratio de l'actif net : `1,000061909`.

Cette combinaison est celle d'un fractionnement inversé 1-pour-2. La procédure fixe donc `q_t = 0,5` ce jour-là. Le rendement NAV brut proche de +100 % devient un rendement de prix ajusté proche de +0,0062 %. La règle est fondée sur un saut de NAV supérieur à 50 %, sa réciproque dans les parts à 2 % près et une variation d'actif net inférieure à 10 %. Elle ne s'active sur aucune autre date.

Il s'agit d'une inférence interne très forte, pas d'une confirmation documentaire indépendante. L'absence d'autre événement détecté ne prouve pas l'absence historique de toute autre opération sur titres.

## Anomalies conservées

### 7 octobre 2014

| Instrument | NAV | Parts publiées | Parts impliquées par actif net / NAV | Écart publié − impliqué |
|---|---:|---:|---:|---:|
| SPY | 193,307002 | 716 082 116 | 904 482 115,44 | −188 399 999,44 |
| BIL | 45,746902 | 21 800 461 | 22 000 460,89 | −199 999,89 |

L'actif net et la NAV sont mutuellement cohérents avec un nombre de parts proche des jours voisins; la rupture concerne donc le champ publié des parts. Les deux fonds sont touchés le même jour. La NAV est continue et aucune preuve ne justifie de la corriger ou de l'exclure. L'observation reste dans les rendements; seuls les champs auxiliaires sont signalés comme incohérents.

### Distribution BIL du 3 mars 2008

La ligne indique une record date au 5 février et un paiement au 11 février, donc antérieurs de 21 jours à l'ex-date. La NAV baisse bien le 3 mars, ce qui soutient l'ex-date inscrite, mais ne permet pas de corriger les deux autres dates. L'ex-date et le montant sont utilisés pour l'indice conventionnel; la ligne est interdite pour une future comptabilité du cash tant que sa chronologie n'est pas confirmée indépendamment.

## Validation indépendante réellement obtenue

Sur 2 512 rendements communs entre octobre 2016 et octobre 2026, la variation de NAV SPY et celle du prix de clôture Nasdaq présentent :

- corrélation : `0,998430`;
- écart moyen signé : `0,0057` point de base;
- écart absolu moyen : `3,5260` points de base;
- RMSE : `6,3935` points de base;
- écart absolu maximal : `99,10` points de base.

Ce contrôle soutient la cohérence générale des variations de NAV, mais le maximum illustre précisément que NAV et dernier prix Nasdaq ne sont pas interchangeables. Sur les 448 dates également couvertes par le fichier premium/discount State Street, l'écart médian entre le ratio clôture Nasdaq/NAV et le champ officiel est de `0,00835` point de pourcentage; le maximum, `0,95361`, survient le 9 avril 2025. Les horaires et définitions du prix de marché peuvent différer.

Cette confrontation n'est **pas** une validation externe du rendement total : elle compare un prix de marché à la NAV et réutilise les distributions State Street. Aucune référence indépendante comparable n'existe localement pour BIL.

## Résultats dérivés locaux

Les fichiers restent exclus de GitHub sous `data/processed/rl/`.

| Fichier | Taille (octets) | SHA-256 |
|---|---:|---|
| `spy_nav_total_returns.csv` | 840 057 | `37d60ca45a1f98cdfd844bccbe176c8b6c6f5e59e5a95b1cbdf78a4d686f741f` |
| `bil_nav_total_returns.csv` | 736 496 | `55d9f6ba856fb219e5be6b870f11c36a550a7f99def9bb3099ce0127979e8ad2` |
| `validation_report.json` | 5 576 | `175fead1bd95d3e4f77cbe53515c3ab34484e5025eca98bb8f88e3c653a114ed` |
| `reconstruction_metadata.json` | 3 799 | `15dd2c11f8d3574efab0dd94e71e17d723d3cda7ab713d7b5a1b039cac96932e` |

Les quatre résultats ont également été copiés sous `D:\ai-financial-risk-reliability-data-backup\2026-10-19\data\processed\rl\`, sur le disque physique distinct déjà audité. Les empreintes des quatre copies correspondent aux originaux : zéro discordance. Avec les 19 fichiers bruts, la sauvegarde contrôlée contient désormais 23 fichiers de données pour 66 577 864 octets.

La commande de reproduction est :

```powershell
python RL/scripts/reconstruct_total_returns.py
python RL/scripts/verify_local_data.py
```

## Usages autorisés et interdits

Usage possible après acceptation explicite des réserves : analyses financières hors exécution et hors coûts externes, fondées sur des rendements totaux quotidiens à la NAV sous la convention documentée.

Restent interdits sans étape scientifique supplémentaire :

- traiter la NAV comme un prix auquel un ordre aurait été exécuté;
- revendiquer une performance nette de transaction;
- simuler un portefeuille ou lancer un backtest;
- ignorer le délai entre ex-date et paiement;
- redistribuer les fichiers bruts ou dérivés sans clarification des droits;
- qualifier les séries de validation externe complète.

Pour passer à un portefeuille négociable, il manque encore une convention d'exécution, des prix exécutables horodatés, spreads, commissions et slippage, une comptabilité des distributions aux dates de paiement, ainsi qu'une validation explicite de l'opération sur titres BIL.
