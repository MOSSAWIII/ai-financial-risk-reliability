# Audit du patrimoine local de données académiques et institutionnelles

**Date de l'audit :** 19 octobre 2026

**Périmètre :** acquisition, conservation, traçabilité et contrôle; aucune expérience, sélection de signal, simulation, politique ou modélisation.

**Règle :** **DATA FIRST — NO EXPERIMENT WITHOUT VERIFIED LOCAL DATA.**

## 1. Conclusion opérationnelle

Le projet possède désormais **19 fichiers bruts locaux**, soit **64 991 936 octets (61,98 MiB)**. Parmi eux, 6 fichiers existaient déjà et ont été réaudités; 13 fichiers (60,23 MiB) ont été acquis auprès de sources académiques ou institutionnelles. Tous sont exclus de Git. Le registre public `RL/data_manifest.json` contient leurs chemins, tailles, empreintes SHA-256, conventions, statuts et usages admissibles. Le script `RL/scripts/verify_local_data.py` reproduit hors ligne les contrôles d'intégrité et de structure.

Ce résultat ne suffit pas à autoriser un backtest SPY–BIL. Nous disposons de briques complémentaires — prix incomplets, NAV, distributions, taux et indices de conditions financières — mais pas encore d'une série longue et validée de rendements de détention négociables, alignée avec les distributions, événements sur titres, coûts et dates d'information.

## 2. Niveaux de preuve

- `IDENTIFIED` : source localisée, aucun fichier acquis.
- `ACQUIRED` : fichier brut présent et empreinte vérifiée, sans audit complet.
- `AUDITED` : structure, couverture et anomalies contrôlées.
- `VALIDATED_FOR_USE` : validation limitée à un usage scientifique explicitement nommé.
- `BLOCKED` : acquisition empêchée et cause documentée.

`AUDITED` ne signifie donc ni « utilisable pour tout », ni « disponible historiquement en temps réel ». Les fichiers bruts n'ont été ni corrigés, ni imputés, ni transformés.

## 3. Inventaire physique et empreintes

Le tableau résume les fichiers réellement présents. Les chemins, noms d'origine et empreintes complètes sont également lisibles automatiquement dans le manifeste.

| Identifiant | Taille (octets) | SHA-256 | Statut |
|---|---:|---|---|
| Ken French facteurs quotidiens 202608 | 178 184 | `2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db` | `VALIDATED_FOR_USE` |
| Nasdaq SPY OHLCV | 273 179 | `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5` | `AUDITED` |
| Nasdaq IVV OHLCV | 270 399 | `c928b60ec8b251245cfbe84e0e28573b15a519068dc5e5a824c40e689fcf718c` | `AUDITED` |
| Nasdaq VTI OHLCV | 270 872 | `ceb5de9a643db8f1eb01c23e95b8931195214b4d790c1fb2206ba94049dd7aac` | `AUDITED` |
| FRED DTB3/DGS3MO | 365 856 | `bbc3b7b92549b50828e568d373da384fe89eb2d14d04b405b66bd6016e27fa70` | `AUDITED` |
| Cboe VIX | 473 839 | `a9742d4deab98f7644bda10df92db0b6afbca17ccc8b64139c52ad2ca0963d42` | `AUDITED` |
| Goyal–Welch–Zafirov, millésimes 2025 | 28 530 345 | `43c0ab21c4ecd175aa13d1d69038d082d3b681df1b631a33d8c1076008a6022f` | `AUDITED` |
| Goyal–Welch–Zafirov, classeur 2025 | 1 060 718 | `be74347c37d387fcdeeaf1f24a1332a6382f47943dd331906a5f9de0a30fe480` | `AUDITED` |
| AQR BAB Equity Factors Daily | 31 458 570 | `c34f1ac4130f69dd73440dd62a53caf22df47bc7cc50f5cf544f8e522c28a8c6` | `AUDITED` |
| State Street SPY NAV | 277 895 | `80deb8db0ca46881dbec2b521487389d7c2290233ffe40b45c46b9c33699565f` | `AUDITED` |
| State Street BIL NAV | 223 252 | `13ac00ae7dd64308bd1e548386a5fe8ae51c0f3983b51d2f2dd3789bbc3ae68a` | `AUDITED` |
| State Street SPY premium/discount | 30 775 | `afac89e371da667234881bb5a7e6607c9105061540576e3667f91d2f63ba12a9` | `AUDITED` |
| State Street BIL premium/discount | 30 534 | `02ff4c15ca843643e95fb2223d184d14ba9d312b403d2caad5f85726ea52a1f2` | `AUDITED` |
| State Street distributions SPDR | 581 216 | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` | `VALIDATED_FOR_USE` |
| New York Fed SOFR Averages/Index | 109 642 | `c0120c0bcf46c586968b72776303c146d5f1add23451636fd437410e83d53ae8` | `VALIDATED_FOR_USE` |
| New York Fed Markets API YAML | 143 746 | `5dbb331d86b91bfc115be9b5fe9c46735833a4f7280d33e4327e8acf7ad30d2b` | `ACQUIRED` |
| OFR Financial Stress Index | 516 429 | `cb851148775b0ef35be4d46776ab2bb5e5230924b5b25addb0a622dc0ae9dda2` | `AUDITED` |
| OFR FSI Revision History | 125 482 | `f59409523075f5b8224e148f828e6138a988814fe753c3e72366b220b0696585` | `AUDITED` |
| Chicago Fed NFCI/ANFCI via FRED | 71 003 | `7b452a51e1ac2a0458062bd97870e7afe59cea5345521c32a12c779730c0adc6` | `AUDITED` |

## 4. Ce que les audits ont réellement établi

### 4.1 Socle historique déjà utilisé

Le ZIP Fama–French est lisible, son CRC est valide, et contient 26 317 dates du 1er juillet 1926 au 31 août 2026 sans doublon, valeur manquante ni valeur infinie. Les quatre colonnes sont en pourcentage quotidien. Le rendement agrégé précédemment utilisé est `Mkt-RF + RF`; il reste validé pour reproduire les analyses de volatilité déjà menées, mais ce portefeuille académique n'est pas SPY et n'incorpore ni prix d'exécution ni coûts.

Les trois réponses Nasdaq contiennent chacune 2 514 séances du 17 octobre 2016 au 16 octobre 2026. IVV et VTI ne présentent pas de valeur OHLCV manquante; SPY présente une valeur de volume manquante. Ces fichiers ne documentent pas les distributions ni une convention de prix ajusté et ne couvrent qu'environ dix ans.

Le VIX couvre 9 296 séances du 2 janvier 1990 au 16 octobre 2026, sans date dupliquée ni valeur OHLC absente. En revanche, **47 lignes** violent l'invariant usuel `low ≤ open, close ≤ high`, surtout dans l'historique ancien, avec quelques cas manifestement extrêmes. Aucune correction automatique n'est autorisée.

### 4.2 Goyal–Welch–Zafirov

Le ZIP de millésimes contient **46 CSV** lisibles et sans erreur CRC. Aucun libellé temporel invalide, doublon ou infini n'a été détecté. Les matrices de millésimes ont une structure triangulaire attendue : leurs nombreuses cellules absentes ne sont pas assimilables à des erreurs et ne doivent pas être imputées mécaniquement.

Le classeur agrégé contient 1 860 mois (1871-01–2025-12), 620 trimestres et 155 années, avec 57 colonnes dans chaque table. Les historiques sont fortement hétérogènes : la table mensuelle contient 51 390 cellules numériques absentes. Par exemple, `ret`/`retx` commencent en 1926, `svar` en 1885, `vp` en 1990, `impvar` en 1996 et `tail` en 1926. Le classeur agrégé courant peut avoir été révisé; seuls les fichiers de millésimes permettent d'envisager une analyse de disponibilité historique, variable par variable.

### 4.3 AQR

Le classeur comporte 12 feuilles, dont les méthodes, sources et avertissements. Les séries quotidiennes auditées couvrent notamment BAB (25 369 observations, décembre 1930–juillet 2026), MKT/SMB/HML (26 678 observations, juillet 1926–juillet 2026) et RF (27 266 observations, juillet 1926–août 2026). Les colonnes américaines clés sont complètes, sans dates dupliquées ni infinis. Les dates de week-end détectées correspondent principalement aux séances historiques du samedi et ne sont pas supprimées. AQR précise que l'historique peut être reconstruit lors des mises à jour : il ne constitue pas une archive de ce qu'un chercheur aurait vu à chaque date.

### 4.4 SPY, BIL, distributions et référence monétaire

Les NAV officielles couvrent SPY du 1er décembre 2003 au 15 octobre 2026 (5 758 dates) et BIL du 30 mai 2007 au 15 octobre 2026 (4 880 dates). Pour SPY, `Shares Outstanding` et `Total Net Assets` valent `-` pendant 628 dates chacun, du 1er décembre 2003 au 30 mai 2006, soit 1 256 valeurs manquantes après lecture numérique. Les NAV elles-mêmes sont complètes.

Le contrôle `NAV × parts ≈ actif net` révèle, pour les deux ETF, une anomalie commune au **7 octobre 2014** : écart relatif maximal de 20,83 % pour SPY et de 0,91 % pour BIL. Hors cette observation, les écarts maximaux vus dans les dix lignes suivantes sont de l'ordre de `10⁻⁸`; cette rupture isolée doit être expliquée ou exclue par une règle préétablie avant tout calcul de portefeuille.

Les fichiers premium/discount ne contiennent que 449 dates, du 2 janvier 2025 au 16 octobre 2026. L'unité exacte du champ doit être confirmée avant transformation. Ils ne permettent pas de mesurer le coût NAV–marché sur l'historique profond.

Le classeur de distributions contient 136 événements SPY entre mars 1993 et septembre 2026 et 232 événements BIL entre juillet 2007 et octobre 2026, sans dividende manquant, négatif ou date ex-dividende dupliquée au sein de chaque ticker. Il est validé uniquement pour contrôler les événements de distribution. Une série de rendement total exige encore une convention explicite de réinvestissement et une série de prix ou de NAV validée.

Le SOFR Index acquis contient 1 656 jours publiés du 2 mars 2020 au 16 octobre 2026. Les quatre champs sont complets, sans doublon, infini, indice non positif ni baisse de l'indice. C'est une référence officielle de capitalisation monétaire; ce n'est ni le rendement de marché de BIL, ni un prix négociable.

### 4.5 Taux et conditions financières

Le fichier FRED comporte 18 989 dates. `DTB3` a 18 188 valeurs du 4 janvier 1954 au 15 octobre 2026; `DGS3MO` en a 11 280 du 1er septembre 1981 au 15 octobre 2026. Les valeurs absentes viennent notamment des calendriers et de leurs dates de démarrage différentes. Ces séries sont des taux annuels cotés, pas des rendements quotidiens réalisés.

Le FSI de l'OFR contient 6 780 jours ouvrés du 3 janvier 2000 au 14 octobre 2026, neuf mesures numériques complètes, sans doublon ni infini. Il est publié avec un délai annoncé de deux jours ouvrés et peut être révisé. Le classeur séparé documente quatre feuilles de révisions, mais ne prouve pas l'existence d'un millésime pour chaque jour.

NFCI et ANFCI contiennent 2 910 vendredis hebdomadaires du 8 janvier 1971 au 9 octobre 2026, exactement espacés de sept jours, complets et sans doublon. La date de référence du vendredi n'est pas sa date de disponibilité : la publication intervient ultérieurement, et l'historique courant est révisé. Sans vintages, ces indices ne sont pas validés pour une décision historique point-in-time.

## 5. Sources explorées mais non acquises

### Open Source Asset Pricing — `BLOCKED`

La page officielle annonce la version 2.0.0 d'octobre 2025, avec des données généralement prolongées jusqu'en décembre 2024 et certaines caractéristiques optionnelles jusqu'en décembre 2022. Les liens directs visés (`PredictorLSretWide.csv`, `SignalDoc.csv`) ont répondu **Google Drive — Quota exceeded** à toutes les variantes de téléchargement testées le 19 octobre 2026. Aucun fichier, aucune taille et aucune empreinte n'ont donc été enregistrés.

### VOLARE — `BLOCKED`

Le portail et sa documentation ont été inspectés. L'application appelle des endpoints de téléchargement exigeant un jeton `Bearer`; aucun compte autorisé n'était disponible. Les droits attachés aux données de marché sous-jacentes doivent aussi être clarifiés. Aucun fichier VOLARE n'est présent localement.

Des dépôts généralistes (Dataverse, Zenodo, OSF) n'ont pas été utilisés pour remplacer une source primaire officielle déjà accessible. Aucune archive de réplication ouverte, suffisamment documentée et autorisant à la fois l'historique complet des prix ajustés, distributions, splits et validation de SPY–BIL, n'a été établie pendant cet audit. Cette absence de preuve n'est pas une preuve d'inexistence.

## 6. Limites de licence et de reproductibilité

- Les fichiers bruts restent sous `data/raw/`, que `.gitignore` exclut. Seuls le manifeste, le vérificateur et cette documentation sont publiables.
- Les conditions propres à Nasdaq, Cboe, AQR et State Street continuent de s'appliquer. Le classeur AQR inclut ses sources, disclosures et conditions d'usage. Aucun fichier brut n'est redistribué.
- Une empreinte garantit l'identité binaire de la copie, pas l'exactitude économique de son contenu.
- Les fichiers courants de Goyal–Welch, AQR, OFR, FRED et Chicago Fed peuvent contenir des révisions rétrospectives. Le manifeste distingue une archive de millésimes d'un historique courant.
- Le script requiert Python, `pandas` et `openpyxl`. Il ne contacte aucun serveur, n'impute rien et échoue si un fichier, une taille, une empreinte ou un invariant attendu diffère.

Commande de contrôle depuis la racine :

```powershell
python RL/scripts/verify_local_data.py
```

## 7. Sauvegarde indépendante

Une seconde copie contrôlée a été créée sous :

`D:\ai-financial-risk-reliability-data-backup\2026-10-19\`

Le volume principal `C:` est porté par le disque physique 1 (NVMe `SSSTC CL1-4D256`) et la sauvegarde `D:` par le disque physique 0 (`ST2000LM007-1R8174`). Ce ne sont donc pas deux dossiers du même disque. Les 19 fichiers bruts, 64 991 936 octets, ont été copiés et leurs SHA-256 comparés fichier par fichier : **0 discordance**. La copie n'est ni un service distant ni une protection contre un sinistre affectant toute la machine; une stratégie hors site resterait un renforcement facultatif soumis aux licences.

## 8. Réponses aux quatre questions de décision

### A. Quelles données possédons-nous réellement ?

Nous possédons physiquement : le marché académique Fama–French quotidien; dix ans d'OHLCV Nasdaq pour SPY, IVV et VTI; VIX et deux taux du Trésor; les classeurs agrégé et de millésimes Goyal–Welch–Zafirov; un classeur AQR quotidien; les NAV, premium/discount et distributions officielles State Street de SPY/BIL; le SOFR Index et sa spécification API; le FSI de l'OFR avec son historique partiel de révisions; NFCI/ANFCI. Les 19 fichiers ont une empreinte vérifiée et une seconde copie indépendante. Nous ne possédons ni fichier Open Source Asset Pricing ni fichier VOLARE.

### B. Lesquelles sont suffisamment fiables, et pour quels usages ?

Trois ensembles sont `VALIDATED_FOR_USE`, toujours avec un usage étroit : Fama–French pour reproduire les analyses agrégées déjà validées; les distributions State Street pour valider descriptivement les événements SPY/BIL; le SOFR Index pour une référence officielle de capitalisation sur 2020–2026. Les autres fichiers présents sont `AUDITED` ou `ACQUIRED` : ils peuvent soutenir une discussion de données, mais exigent une décision scientifique supplémentaire avant toute variable expérimentale. Aucun ensemble n'est validé à ce stade pour un backtest SPY–BIL net.

### C. Que manque-t-il pour un portefeuille actions–monétaire cohérent ?

Il manque surtout une chaîne complète et validée de rendements de détention : prix de marché ajustables et événements sur titres SPY sur un historique suffisamment profond; cohérence quotidienne prix–distribution–split; équivalent BIL depuis 2007 ou une composante pré-2007 explicitement différente; spreads, coûts, convention d'exécution et réinvestissement; calendrier commun; preuve de disponibilité point-in-time des éventuels états économiques. Les NAV et distributions réduisent le manque, mais une NAV n'est pas un prix exécuté et SOFR n'est pas BIL.

### D. Quelles conditions restent à remplir avant une première expérience ?

1. Choisir explicitement l'instrument actions, la composante monétaire et la période commune; accepter ou résoudre la limitation historique de BIL.
2. Acquérir ou construire, sans invention, des rendements totaux vérifiables à partir de prix/NAV et distributions, puis les valider indépendamment.
3. Définir les coûts, le moment d'exécution, le réinvestissement, les poids et le calendrier comptable.
4. Résoudre ou encadrer l'anomalie du 7 octobre 2014, les 47 anomalies OHLC du VIX et toute valeur manquante pertinente.
5. Pour chaque information d'état retenue ultérieurement, établir sa date de publication et ses révisions; obtenir des vintages si l'usage point-in-time l'exige.
6. Faire valider par le responsable scientifique l'usage précis de chaque dataset et le protocole minimal avant toute expérience.

En conséquence, **aucune première expérience n'est autorisée par ce seul audit**. La prochaine décision porte sur les instruments et la reconstruction validable des rendements, pas sur un algorithme.
