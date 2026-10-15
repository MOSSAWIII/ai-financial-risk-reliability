# Fiabilité des prévisions du risque financier sous changement d'environnement

Ce dépôt porte sur la fiabilité conditionnelle des prévisions du risque de
marché : précision, incertitude, robustesse temporelle et utilité financière
lorsque l'environnement change.

Le développement est versionné publiquement sur GitHub afin que les décisions,
protocoles et résultats — y compris négatifs — restent traçables. La présence
publique du code ne vaut pas encore octroi d'une licence de réutilisation : le
choix d'une licence est une décision ouverte.

## État du projet

**Phase 0 — cadrage scientifique : validée le 15 octobre 2026.** Trois étapes
limitées de la Phase 1 ont été exécutées : audit de la cible, compréhension
descriptive, puis comparaison exploratoire de deux prévisions simples. Aucun
modèle ML n'a été entraîné.

Le projet cherche à comprendre comment les changements d'environnement
économique affectent la fiabilité des prévisions du risque financier et dans
quelle mesure les méthodes prédictives peuvent reconnaître leurs limites,
quantifier leur incertitude et maintenir ou retrouver une fiabilité acceptable.
L'objet empirique initial reste la volatilité réalisée future à cinq séances du
marché américain Fama–French. Sa définition mathématique, ses unités et sa
construction temporelle ont été validées et auditées. Sa pertinence économique
comme mesure suffisante du risque n'est pas établie par cet audit technique.
La priorité permanente est la solution la plus simple compatible avec la
question active. Aucune extension scientifique ne sera intégrée sans validation
explicite du porteur du projet.

## Documents actuels

- `CADRAGE_PROJET_RECHERCHE_IA_FINANCE_CODEX.txt` : mandat fondateur fourni par
  le porteur du projet ;
- `docs/PHASE_0_CADRAGE_SCIENTIFIQUE.md` : audit de périmètre, question,
  hypothèses, objet empirique et protocole initial simplifié ;
- `docs/JOURNAL_DECISIONS.md` : décisions, recommandations et points encore à
  valider.
- `notebooks/01_audit_cible_fama_french.ipynb` : import officiel, contrôle des
  unités et des dates, construction et audit temporel de la cible à cinq
  séances.
- `notebooks/02_comprendre_volatilite_realisee.ipynb` : comportement historique,
  distribution, périodes extrêmes, persistance et limites de cette cible comme
  mesure du risque.
- `notebooks/03_previsibilite_simple.ipynb` : comparaison exploratoire sur
  2016–2019 entre une constante apprise sur 1990–2015 et la volatilité historique
  des 20 séances connues à `t`.

Les notebooks constituent l'environnement principal de la Phase 1 ; des
modules Python ne seront ajoutés que pour les fonctions réutilisées ou les tests
qui protègent l'alignement temporel.

Les données brutes, secrets et environnements locaux sont exclus de Git. Une
copie brute immuable du millésime analysé est conservée localement sous
`data/raw/` et vérifiée par SHA-256 par les notebooks ; elle n'est pas publiée.
Les métadonnées de provenance et l'empreinte sont versionnées.

