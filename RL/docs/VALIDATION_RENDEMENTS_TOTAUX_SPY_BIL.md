# Validation de la reconstruction des rendements totaux SPY–BIL

**Millésime :** 19 octobre 2026

**Statut final de la paire :** `AUDITED` — BIL est `VALIDATED_FOR_USE` sous la convention à l'ex-date; la nouvelle série SPY est `VALIDATED_FOR_USE` sous la convention de détention avec réinvestissement au paiement. La série SPY historique à l'ex-date reste `AUDITED`.

## Conclusion

Deux séries quotidiennes de rendement total à la NAV ont été reconstruites hors ligne à partir des NAV et distributions officielles State Street. Les identités comptables, l'alignement temporel, l'intégration unique des distributions et la reproductibilité binaire sont vérifiés. La période commune va du **30 mai 2007 au 15 octobre 2026** : 4 880 dates de NAV et 4 879 rendements pour chacun des deux instruments.

Les réserves documentaires antérieures ont été examinées. Le fractionnement inversé BIL est confirmé par un dépôt SEC et, pour le ratio exact, par le formulaire fiscal officiel State Street. BIL satisfait ses deux contrôles officiels avec la tolérance préenregistrée de 0,01 point de pourcentage.

Pour SPY, les dépôts réglementaires établissent que le détenteur acquiert le droit à distribution à l'ex-date, que la NAV retranche les dividendes payables et que les rendements réglementaires réinvestissent à la NAV des dates de paiement. Une nouvelle série, distincte de la reconstruction historique, suit donc `parts × NAV + cash + créances`. Elle satisfait les contrôles officiels à un et cinq ans sans changer les dates ni la tolérance. Cette validation est limitée à l'analyse de rendement total NAV selon cette convention; elle ne transforme pas la NAV en prix exécutable et ne valide pas encore une paire SPY–BIL aux conventions temporelles homogènes.

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
| SEC SPY 485BPOS | déposé et effectif le 2026-01-26 | `864cfc2f626765959edc73738ef150655bb82dfa4f024a8aa013cb31218d9a94` |
| SEC SPY 497 | déposé le 2025-01-28 | `52dc9a232dbdeb7fbb2c635032b5db65b34256cc93cc7b834d72e088d5bea68a` |
| SEC SPY 485BPOS | déposé et effectif le 2025-01-27 | `fc3ecd1be6b9fa3ec5083edbeb84f81c381c6f55de6365207cca548709bdfb1b` |

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

### Convention B — détention, créance et paiement

Pour SPY, la variante sépare à chaque clôture :

\[
W_t = n_tN_t + C_t + A_t,
\]

où `n_t` est le nombre de parts, `N_t` la NAV, `C_t` le cash disponible et `A_t` les distributions acquises mais non encore payées.

L'ordre des opérations est fixé avant comparaison :

1. les parts déjà détenues à l'ex-date créent une créance `n × D`;
2. cette créance reste distincte du cash et ne peut acheter aucune part;
3. à la date de paiement, la créance correspondante devient du cash sans modifier la richesse;
4. ce cash est immédiatement réinvesti à la NAV du paiement en fractions de part;
5. la richesse finale inclut toute créance encore impayée.

Une entrée à la NAV de la date initiale n'obtient aucune distribution détachée antérieurement, même si son paiement survient dans la fenêtre. Une distribution détachée pendant la fenêtre mais payée après la date finale reste en créance dans la richesse finale. Cette construction diffère donc d'un simple ratio d'un indice ancien lorsque celui-ci porte déjà une créance à la date initiale.

Les tests synthétiques vérifient la conservation de richesse lors du détachement et du transfert créance → cash → parts, l'absence de cash fictif, l'extinction des créances, les fractions de part, plusieurs créances simultanées et l'exclusion d'un droit antérieur au départ. L'erreur maximale de transfert dans les données SPY est `2,27 × 10⁻¹³` USD; le bilan cumulé `créances créées = paiements réinvestis + créance finale` ferme à `3,06 × 10⁻¹⁴` USD.

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

### Preuve documentaire SPY et portée

Les trois soumissions SEC originales ont été conservées localement. Les passages contrôlés établissent que :

- le rendement total réglementaire achète à la NAV du premier jour, vend à la NAV du dernier jour et réinvestit les distributions à la NAV des dates de paiement;
- le détenteur inscrit à l'ex-date, qui est aussi la record date dans la documentation récente, acquiert le droit à la distribution;
- les dividendes payables sont des passifs retranchés dans la NAV;
- le paiement régulier intervient le dernier jour ouvré du mois suivant l'ex-date;
- pour la dernière distribution d'une année civile présentée, certains tableaux réglementaires utilisent exceptionnellement la NAV du 31 décembre au lieu de la NAV réelle de paiement de janvier. Cette exception n'est pas appliquée aux fenêtres terminées en septembre.

Ces textes documentent la méthode du **SPDR S&P 500 ETF Trust**. La factsheet de septembre 2026 affirme un rendement NAV net de frais avec réinvestissement, mais ne renvoie pas explicitement à l'algorithme de date de paiement. L'identité parfaite des méthodologies ne peut donc pas être prouvée par une phrase de la factsheet seule. La concordance empirique obtenue avec la convention réglementaire apporte une preuve convergente, sans transformer cette inférence en certitude documentaire absolue.

### Comparaison officielle des conventions A et B

La règle a été fixée avant le calcul : tolérance absolue de **0,01 point de pourcentage**. Les fenêtres restent exactement du 30 septembre 2025 au 30 septembre 2026 et du 30 septembre 2021 au 30 septembre 2026. Un an est cumulé; cinq ans sont annualisés géométriquement.

| Fenêtre SPY | Officiel NAV | A : ex-date | Écart A | B : paiement/créances | Écart B | Verdict B |
|---|---:|---:|---:|---:|---:|---|
| 1 an | 15,5984 % | 15,6348 % | +0,0364 pt | 15,5981 % | −0,0003 pt | réussite |
| 5 ans annualisé | 13,6521 % | 13,6866 % | +0,0345 pt | 13,6574 % | +0,0053 pt | réussite |

Quatre distributions sont acquises dans la fenêtre d'un an, dont trois payées avant la fin; sur cinq ans, vingt sont acquises, dont dix-neuf payées. Dans chaque fenêtre :

- une distribution détachée avant le départ mais payée après celui-ci est exclue (`2025-09-19`, 1,831114 USD, ou `2021-09-17`, 1,428117 USD);
- la distribution du 18 septembre 2026, payable le 30 octobre, reste une créance finale de 1,903857 USD sur un an et 2,012230 USD sur cinq ans, compte tenu des parts accumulées;
- omettre cette créance réduirait la performance à 15,3124 % sur un an et 13,6012 % annualisé sur cinq ans : elle ne peut être ignorée;
- le calendrier de réinvestissement des distributions déjà payées réduit A de 0,03659 point sur un an et de 0,02911 point annualisé sur cinq ans;
- le non-réinvestissement immédiat de la créance finale explique encore −0,00010 et −0,00002 point.

La convention B réduit l'écart absolu initial de **99,21 %** sur un an et **84,49 %** sur cinq ans. Elle ne reproduit pas artificiellement les valeurs officielles : des écarts résiduels de 0,0003 et 0,0053 point demeurent, mais ils respectent le seuil fixé.

Un indice global de détenteur commencé en 2003 produit, par simple ratio aux frontières, 15,5909 % et 13,6525 %. Il diffère de la reconstruction d'un nouvel entrant de 0,0072 et 0,0049 point, car l'indice global possède déjà une créance issue d'une ex-date antérieure au début. Cette différence confirme pourquoi le contrôle officiel doit reconstruire chaque fenêtre plutôt que diviser silencieusement deux niveaux d'un indice ancien.

Le pipeline A et ses quatre sorties antérieures restent inchangés. Le contrôle officiel est issu du même émetteur que les NAV et distributions : il est officiel, mais pas indépendant d'un second fournisseur.

## Cinq niveaux de validation

1. **Intégrité et provenance des sources — réussi.** Fichiers locaux, tailles, SHA-256, URLs et conditions d'usage sont documentés.
2. **Cohérence comptable, temporelle et reproductibilité — réussi.** Les identités, calendriers et productions binaires sont contrôlés.
3. **Opération sur titres BIL — réussi.** Fonds, date, ratio et unité sont confirmés par documentation officielle.
4. **Concordance avec les performances officielles — réussie par série validée.** Les deux fenêtres BIL réussissent sous A; les deux fenêtres SPY réussissent sous B. La série SPY A échoue et conserve son statut propre.
5. **Adéquation à l'usage exact — validée séparément, pas pour un portefeuille.** BIL-A et SPY-B sont utilisables pour leurs analyses NAV étroites. Leur association en portefeuille n'est pas validée : conventions temporelles différentes, absence de prix d'exécution et de coûts.

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
| `spy_nav_total_returns_payment_date_v1.csv` | 613 077 | `d7bb1e838070256636eb73b02db9486bb4410ba580550ae50581d50f2fcfd001` |
| `spy_payment_date_validation_v1.json` | 10 592 | `7b6b67cc15eeec3304733e39c12a15b42849cff70a325da7d7f257cfc2a97ad8` |

Les sept résultats et les vingt-huit sources brutes ou documentaires ont également été copiés sous `D:\ai-financial-risk-reliability-data-backup\2026-10-19\`, sur le disque physique distinct déjà audité. Les empreintes des nouvelles copies et des fichiers suivis sauvegardés correspondent aux originaux : zéro discordance. La sauvegarde contrôlée contient désormais 35 fichiers de données référencés par le manifeste pour 75 361 820 octets.

La commande de reproduction est :

```powershell
python RL/scripts/reconstruct_total_returns.py
python RL/scripts/validate_official_performance.py
python RL/scripts/reconstruct_spy_payment_date_returns.py
python RL/scripts/verify_local_data.py
```

## Usages autorisés et interdits

Usages validés séparément :

- **BIL-A** : analyses hors exécution du rendement total NAV sous la convention à l'ex-date;
- **SPY-B** : analyses hors exécution du rendement total NAV sous la comptabilité de détention, créances et réinvestissement à la date de paiement.

La série historique **SPY-A** reste `AUDITED`. Les statuts ne sont pas transférables d'une version à l'autre. La paire SPY–BIL reste `AUDITED` pour tout usage conjoint tant qu'une convention économiquement compatible n'est pas validée pour les deux jambes.

Restent interdits sans étape scientifique supplémentaire :

- traiter la NAV comme un prix auquel un ordre aurait été exécuté;
- revendiquer une performance nette de transaction;
- simuler un portefeuille ou lancer un backtest;
- ignorer le délai entre ex-date et paiement ou traiter une créance comme du cash;
- redistribuer les fichiers bruts ou dérivés sans clarification des droits;
- qualifier les séries de validation indépendante complète;
- utiliser le statut d'une version pour promouvoir silencieusement une autre série ou la paire.

Pour passer à un portefeuille négociable, il manque encore une convention commune de détention et de distribution pour SPY et BIL, des prix exécutables horodatés, spreads, commissions, slippage et fiscalité. La chronologie anormale de la distribution BIL du 3 mars 2008 interdit actuellement de reconstruire BIL-B de manière documentaire; la validation NAV ne résout donc pas la compatibilité de portefeuille. Les différences NAV/prix de marché demeurent également pertinentes.
