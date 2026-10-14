# Fiabilité des prévisions du risque financier sous changement de régime

Ce dépôt porte sur la fiabilité conditionnelle des prévisions du risque de
marché : précision, calibration, robustesse temporelle et, dans une phase
ultérieure, utilité financière lorsque l'environnement change.

Le développement est versionné publiquement sur GitHub afin que les décisions,
protocoles et résultats — y compris négatifs — restent traçables. La présence
publique du code ne vaut pas encore octroi d'une licence de réutilisation : le
choix d'une licence est une décision ouverte.

## État du projet

**Phase 0 — cadrage scientifique : proposition terminée, en attente de
validation humaine.** Aucune donnée n'a été téléchargée et aucun modèle n'a été
entraîné.

Le périmètre initial recommandé est la prévision, après la date de marché `t`,
d'un proxy de variance du portefeuille de marché américain sur les cinq séances
`t+1, ..., t+5`. Le projet ne présume ni la supériorité du machine learning, ni
une interprétation causale des changements de régime.

## Documents actuels

- `CADRAGE_PROJET_RECHERCHE_IA_FINANCE_CODEX.txt` : mandat fondateur fourni par
  le porteur du projet ;
- `docs/PHASE_0_CADRAGE_SCIENTIFIQUE.md` : question, hypothèses, données,
  littérature, protocole, risques et première expérience proposée ;
- `docs/JOURNAL_DECISIONS.md` : décisions, recommandations et points encore à
  valider.

Les notebooks et le code de la Phase 1 ne seront créés qu'après validation du
cadrage. Les notebooks seront alors l'environnement principal d'analyse ; des
modules Python ne seront ajoutés que pour les fonctions réutilisées ou les tests
qui protègent l'alignement temporel.

Les données brutes, secrets et environnements locaux sont exclus de Git. Les
métadonnées de provenance et checksums des données pourront en revanche être
versionnés.

