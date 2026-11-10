# Validation G2 — porte documentaire empirique

## Verdict courant

**`READY_FOR_G2_EXECUTION`**.

Le clone initial était `DOCUMENTARY_BLOCK`. L'archive de sauvegarde datée du
19 octobre 2026, qui contient également le sous-dossier du 20 octobre, a ensuite
été fournie. Les sept identifiants requis — dix fichiers physiques en comptant
les trois calendriers NYSE additionnels — ont été restaurés à leurs chemins du
manifeste et vérifiés octet par octet.

## Dépendances vérifiées

| Dépendance | Résultat |
|---|---|
| Yahoo SPY original | `VERIFIED` |
| Yahoo BIL original | `VERIFIED` |
| Audit dérivé Yahoo SPY–BIL | `VERIFIED` |
| Distributions State Street | `VERIFIED` |
| Calendriers NYSE 2022, 2023, 2024 et 2025 | `VERIFIED` |
| Règle SEC T+1 | `VERIFIED` |
| Guide DTCC T+1 | `VERIFIED` |
| Contrôles C1–C2 publiés | 4 sur 4 présents et hachés |

Le rapport machine se trouve sous
[`results/g2_empirical_sequentiality/readiness_report.json`](../results/g2_empirical_sequentiality/readiness_report.json).

## Mécanisme de restauration

Le restaurateur [`g2_restore_sources.py`](../scripts/g2_restore_sources.py) :

1. résout les identifiants et leurs fichiers additionnels dans le manifeste ;
2. effectue un précontrôle global des tailles et SHA-256 ;
3. ne copie rien si une dépendance manque ou diffère ;
4. refuse d'écraser une destination conflictuelle ;
5. vérifie encore chaque copie intermédiaire avant son déplacement atomique.

Le vérificateur [`g2_empirical_readiness.py`](../scripts/g2_empirical_readiness.py)
interdit toute performance si l'une de ces conditions échoue. Les artefacts
historiques publiés ne peuvent jamais remplacer les sources brutes.

## Correction de frontière

Le premier appel au moteur, encore bloqué avant performance, a révélé deux
dépendances qui n'étaient pas contrôlées assez finement par la première version
de la porte : le rapport dérivé d'audit Yahoo et les trois fichiers additionnels
du calendrier NYSE. La porte et le restaurateur ont été corrigés avant G2. Cette
correction ne change aucun choix analytique du protocole.

## Tests

Les tests couvrent l'original exact, l'absence, l'empreinte différente, les
fichiers additionnels, l'idempotence, les conflits de destination, l'interdiction
des sorties sous blocage et l'absence de substitution par des résultats dérivés.

La restauration ouvre uniquement la porte documentaire. Son résultat
scientifique est décrit séparément dans
[`VALIDATION_G2_MATERIALITE_EMPIRIQUE.md`](VALIDATION_G2_MATERIALITE_EMPIRIQUE.md).
