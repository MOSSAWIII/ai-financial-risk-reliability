# Fiabilité des prévisions du risque financier sous changement d'environnement

Ce dépôt porte sur la fiabilité conditionnelle des prévisions du risque de
marché : précision, incertitude, robustesse temporelle et utilité financière
lorsque l'environnement change.

Le développement est versionné publiquement sur GitHub afin que les décisions,
protocoles et résultats — y compris négatifs — restent traçables. La présence
publique du code ne vaut pas encore octroi d'une licence de réutilisation : le
choix d'une licence est une décision ouverte.

## État du projet

**Phase 0 — cadrage scientifique : validée le 15 octobre 2026.** La Phase 1
n'est pas encore engagée. Aucune donnée n'a été téléchargée et aucun modèle n'a
été entraîné.

Le projet cherche à comprendre comment les changements d'environnement
économique affectent la fiabilité des prévisions du risque financier et dans
quelle mesure les méthodes prédictives peuvent reconnaître leurs limites,
quantifier leur incertitude et maintenir ou retrouver une fiabilité acceptable.
L'objet empirique initial reste la volatilité réalisée future à cinq séances du
marché américain Fama–French ; sa définition exacte doit encore être validée.
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

Les notebooks et le code de la Phase 1 ne seront créés qu'après validation du
cadrage. Les notebooks seront alors l'environnement principal d'analyse ; des
modules Python ne seront ajoutés que pour les fonctions réutilisées ou les tests
qui protègent l'alignement temporel.

Les données brutes, secrets et environnements locaux sont exclus de Git. Les
métadonnées de provenance et checksums des données pourront en revanche être
versionnés.

