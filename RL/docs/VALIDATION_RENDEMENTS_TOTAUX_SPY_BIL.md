# Validation de la reconstruction des rendements totaux SPY–BIL

**Millésime :** 19 octobre 2026

**Statut final de la paire :** `AUDITED` — BIL est `VALIDATED_FOR_USE` pour l'usage NAV étroit décrit ci-dessous; SPY reste `AUDITED`.

## Conclusion

Deux séries quotidiennes de rendement total à la NAV ont été reconstruites hors ligne à partir des NAV et distributions officielles State Street. Les identités comptables, l'alignement temporel, l'intégration unique des distributions et la reproductibilité binaire sont vérifiés. La période commune va du **30 mai 2007 au 15 octobre 2026** : 4 880 dates de NAV et 4 879 rendements pour chacun des deux instruments.

Les deux réserves documentaires antérieures ont été examinées. Le fractionnement inversé BIL est désormais confirmé par un dépôt SEC et, pour le ratio exact, par le formulaire fiscal officiel State Street. Les performances officielles State Street permettent quatre contrôles hors ligne. BIL satisfait les deux contrôles avec la tolérance préenregistrée de 0,01 point de pourcentage. SPY dépasse cette tolérance sur les deux fenêtres; sa série n'est donc pas promue. La paire reste `AUDITED` et n'est pas une base autorisée de backtest.

## Sources vérifiées avant transformation

| Objet | Couverture utilisée | SHA-256 |
|---|---|---|
| NAV SPY State Street | 2003-12-01–2026-10-15 | `80deb8db0ca46881dbec2b521487389d7c2290233ffe40b45c46b9c33699565f` |
| NAV BIL State Street | 2007-05-30–2026-10-15 | `13ac00ae7dd64308bd1e548386a5fe8ae51c0f3983b51d2f2dd3789bbc3ae68a` |
| Distributions SPDR | SPY depuis 1993; BIL depuis 2007 | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |
| Clôtures Nasdaq SPY, contrôle partiel | 2016-10-17–2026-10-16 | `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5` |
| Premium/discount SPY, contrôle partiel | 2025-01-02–2026-10-16 | `afac89e371da667234881bb5a7e6607c9105061540576e3667f91d2f63ba12a9` |
| Dépôt SEC 497 BIL | déposé le 2017-11-28; opération du 2017-11-30 | `529262f6cf2a70f689fa87480285ceae6e16bd98a03d493584208621c236ec3e` |
| Form 8937 State Street BIL | fractionnement du 2017-11-30 | `e1b28c61ea9e73051cd7f34a8b8d310cb37e6b54aaa2b5793805784c9308fb55` |
| Factsheet SPY | performances au 2026-09-30 | `b4daa578ceb976dc6debab7e7b202ccf282f17d291fe31d9fe2240d4becbdcfa` |
| Factsheet BIL | performances au 2026-09-30 | `78502b312a73942fcb24e412624c176e6e910165e24dec3d43c78d1bcca28d7c` |

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

La documentation clôt l'ambiguïté des unités :

- le dépôt SEC 497 identifie le fonds BIL et un *reverse stock split* programmé le 30 novembre 2017;
- le Form 8937 State Street indique `1:2 Reverse Share Split`, précise que deux anciennes parts deviennent automatiquement une nouvelle part et que la base par part double tandis que l'investissement total reste inchangé.

Le ratio est donc **une nouvelle part pour deux anciennes parts**, soit `q_t = parts_courantes / parts_précédentes = 1/2 = 0,5`. Ce n'est ni une division du prix par deux ni une division de la valeur agrégée par deux. L'absence d'autre événement détecté ne prouve toutefois pas l'absence historique de toute autre opération sur titres.

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

Cette confrontation n'est **pas** une validation externe du rendement total : elle compare un prix de marché à la NAV et réutilise les distributions State Street.

### Contrôle par les performances officielles State Street

La règle a été fixée avant le calcul : tolérance absolue de **0,01 point de pourcentage**, soit un point de base et le dernier chiffre affiché dans les factsheets. Les pages officielles fournissent en plus des valeurs non arrondies. Les fenêtres vont de la date anniversaire exacte au 30 septembre 2026; un an est un rendement cumulé et les horizons pluriannuels sont annualisés géométriquement. Le code ne cherche aucune fenêtre voisine et ne réajuste pas la tolérance après observation.

| Instrument | Fenêtre | Performance NAV officielle | Reconstruction à l'ex-date | Écart absolu (point) | Verdict |
|---|---:|---:|---:|---:|---|
| SPY | 1 an | 15,5984 % | 15,6348 % | 0,0364 | échec |
| SPY | 5 ans annualisé | 13,6521 % | 13,6866 % | 0,0345 | échec |
| BIL | 1 an | 3,6619 % | 3,6635 % | 0,0016 | réussite |
| BIL | 10 ans annualisé | 2,2932 % | 2,2945 % | 0,0013 | réussite |

Les factsheets qualifient ces chiffres de rendements totaux NAV, nets de frais, avec dividendes et plus-values réinvestis; les périodes inférieures à un an ne sont pas annualisées. Ils distinguent explicitement NAV, valeur de marché et indice. Ils ne précisent cependant pas la date ni le prix exacts de réinvestissement. Notre série attribue les distributions à l'ex-date. Cette différence de convention est une explication plausible de l'écart SPY, mais elle n'est pas démontrée par les factsheets seules. Le pipeline et ses quatre sorties antérieures restent donc inchangés.

Ce contrôle est officiel mais **pas indépendant de l'émetteur** : State Street fournit aussi les NAV et distributions sources. Il vérifie une concordance agrégée avec une publication distincte, pas l'exactitude par un second producteur de données.

## Cinq niveaux de validation

1. **Intégrité et provenance des sources — réussi.** Fichiers locaux, tailles, SHA-256, URLs et conditions d'usage sont documentés.
2. **Cohérence comptable, temporelle et reproductibilité — réussi.** Les identités, calendriers et productions binaires sont contrôlés.
3. **Opération sur titres BIL — réussi.** Fonds, date, ratio et unité sont confirmés par documentation officielle.
4. **Concordance avec les performances officielles — partielle.** Deux fenêtres BIL réussissent; deux fenêtres SPY échouent au seuil préenregistré.
5. **Adéquation à l'usage exact — non validée pour la paire.** BIL est validé pour des analyses de rendement total NAV hors exécution sous la convention documentée; SPY et donc la paire restent `AUDITED`.

Cette graduation évite de transformer une provenance vérifiée ou une identité comptable correcte en validation générale de performance financière.

## Résultats dérivés locaux

Les fichiers restent exclus de GitHub sous `data/processed/rl/`.

| Fichier | Taille (octets) | SHA-256 |
|---|---:|---|
| `spy_nav_total_returns.csv` | 840 057 | `37d60ca45a1f98cdfd844bccbe176c8b6c6f5e59e5a95b1cbdf78a4d686f741f` |
| `bil_nav_total_returns.csv` | 736 496 | `55d9f6ba856fb219e5be6b870f11c36a550a7f99def9bb3099ce0127979e8ad2` |
| `validation_report.json` | 5 576 | `175fead1bd95d3e4f77cbe53515c3ab34484e5025eca98bb8f88e3c653a114ed` |
| `reconstruction_metadata.json` | 3 799 | `15dd2c11f8d3574efab0dd94e71e17d723d3cda7ab713d7b5a1b039cac96932e` |
| `official_performance_validation.json` | 4 832 | `3856d3623ebb81517d35fa1e2cbf6c7fc16be1d0d02969930c153b9495b4916d` |

Les cinq résultats et les six nouvelles preuves brutes ont également été copiés sous `D:\ai-financial-risk-reliability-data-backup\2026-10-19\`, sur le disque physique distinct déjà audité. Les empreintes des onze copies de données ou d'artefacts documentaires, ainsi que celles des fichiers suivis sauvegardés, correspondent aux originaux : zéro discordance. Avec 25 fichiers bruts et 5 résultats dérivés, la sauvegarde contrôlée contient désormais 30 fichiers de données pour 70 147 710 octets.

La commande de reproduction est :

```powershell
python RL/scripts/reconstruct_total_returns.py
python RL/scripts/validate_official_performance.py
python RL/scripts/verify_local_data.py
```

## Usages autorisés et interdits

Usage validé pour **BIL seulement** : analyses financières hors exécution et hors coûts externes, fondées sur le rendement total quotidien à la NAV sous la convention à l'ex-date documentée. SPY, et par conséquent la paire SPY–BIL, restent seulement `AUDITED` tant que l'écart aux performances officielles n'est pas expliqué ou résolu sans déplacer le seuil.

Restent interdits sans étape scientifique supplémentaire :

- traiter la NAV comme un prix auquel un ordre aurait été exécuté;
- revendiquer une performance nette de transaction;
- simuler un portefeuille ou lancer un backtest;
- ignorer le délai entre ex-date et paiement;
- redistribuer les fichiers bruts ou dérivés sans clarification des droits;
- qualifier les séries de validation indépendante complète;
- utiliser le statut BIL pour promouvoir silencieusement SPY ou la paire.

Pour passer à un portefeuille négociable, il manque encore une convention d'exécution, des prix exécutables horodatés, spreads, commissions et slippage, ainsi qu'une comptabilité des distributions aux dates de paiement. La chronologie anormale de la distribution BIL du 3 mars 2008 et l'écart SPY doivent rester visibles; ni le formulaire de split ni les factsheets ne les résolvent.
