# Validation G3A — état d'implémentation

## Objet

Le protocole [G3 gelé](PROTOCOLE_G3_VALEUR_APPRENTISSAGE.md) a été poussé avant toute observation de performance G3. L'implémentation se trouve dans [g3_learning_value.py](../scripts/g3_learning_value.py).

Le contrôle de document initial est **non satisfaisable dans cet environnement de travail distant** : les deux réponses Yahoo originales SPY/BIL sont exclues de GitHub. Elles ne doivent pas être remplacées par des téléchargements actuels, une reconstitution de prix, ou les seules sorties publiées de G2. Tant que les deux SHA-256 du manifeste et le close terminal admissible ne sont pas vérifiés sur un poste où les originaux existent, aucun verdict numérique G3 ne peut être déclaré.

**Statut scientifique : \`G3A_IMPLEMENTED_NOT_EMPIRICALLY_EVALUATED\`.** Ce statut ne vaut ni \`G3_LEARNING_VALUE_POSITIVE\`, ni \`G3_LEARNING_VALUE_NEGATIVE\`, ni \`G3_LEARNING_VALUE_NOT_MATERIAL\`.

## Structure des calculs

1. Porte documentaire : SHA-256, tailles, métadonnées et prix closés bruts originaux de Yahoo SPY et BIL.
2. Première séance commune de chaque semaine ISO, signal à quatre semaines, états binaires conservés.
3. Pour chaque décision de la fenêtre gelée, estimation croissante à partir des paires dont le rendement final est **strictement antérieur** à la décision.
4. Programmation dynamique à horizon 12 avec le même solveur et les mêmes actions que G2 ; contrôle myope appris secondaire.
5. Warm-up de quatre décisions à 50/50, puis décision avec poids hérité propre à la politique.
6. Comptabilité de comparaison G3A : log-rendements close-à-close, coût de 10 pb sur le changement de cible et richesse initiale de 100 000 USD.
7. À la dernière décision (13 avril 2026), close terminal du vendredi 17 avril 2026, sans usage de l'open contesté du 20 avril.

Les quatre CSV et le JSON définis par le protocole sont écrits **uniquement après** la porte documentaire. Les fichiers de sortie et les sources reçoivent des empreintes SHA-256.

## Limites à préserver

- Le solveur historique G2 reçoit les moyennes de log-rendements apprises comme paramètres de rendement pour conserver l'implémentation du contrôleur. L'optimisation du solveur demeure fondée sur \`log(1 + rendement de portefeuille simple)\`, alors que la richesse G3A est calculée sous la formule prespécifiée des log-rendements pondérés. Cette approximation du critère de décision doit être gardée visible dans l'interprétation et évaluée avant toute prétention d'optimalité économique.
- Les closes Yahoo non ajustés ne constituent pas un rendement total avec distributions réinvesties.
- G3A n'inclut ni exécution au prochain open, ni lots entiers, ni bid/ask, ni règlement/livraison, et **ne représente pas le registre financier complet**.
- Les résultats rétrospectifs 2024–2025 étaient déjà connus ; la validation temporelle ultérieure reste exploratoire et n'autorise pas à elle seule PPO.

## Contrôles automatisés

La suite [test_g3_learning_value.py](../tests/test_g3_learning_value.py) comprend six contrôles sans données de marché : séparation temporelle, identité du contrôleur G2, résistance à la modification d'un prix terminal futur, warm-up/calendriers communs, CSV identiques octet pour octet, refus d'exécution sans originaux. Ces contrôles ne remplacent **pas** l'exécution avec sources originales ni l'audit du rapport G3A.

Depuis la racine du dépôt :

\`\`\`sh
python -m unittest discover -s RL/tests -p 'test_g3_learning_value.py' -v
python RL/scripts/g3_learning_value.py
\`\`\`

La seconde commande doit refuser l'évaluation en l'absence des fichiers originaux à leur emplacement déclaré dans \`RL/data_manifest.json\`. Toute exécution empirique exige le protocole inchangé et un journal de vérification de la porte documentaire.
