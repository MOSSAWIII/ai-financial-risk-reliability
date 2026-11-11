# Validation G4.2 - impl�mentation des transitions

## Verdict

**`G4_2_IMPLEMENTATION_VALIDATED_AWAITING_EMPIRICAL_FREEZE`.**

Le constructeur point-in-time et la transition de l'�tat contr�l� sont
impl�ment�s. Cette validation porte sur la causalit�, la comptabilit� du budget
de rotation et la reproductibilit� synth�tique. Elle ne constitue ni un
backtest, ni une comparaison de politiques.

## Contr�les ex�cut�s

Les sept contr�les synth�tiques suivants r�ussissent :

1. la grille simplexe contient exactement 35 actions distinctes ;
2. la rotation vaut la demi-norme L1 et consomme irr�versiblement le budget ;
3. une action d�passant le minimum du plafond par d�cision et du budget restant
   est rejet�e ;
4. une distribution post�rieure � la cl�ture de d�cision ne modifie pas l'�tat
   courant et n'est cr�dit�e que dans la r�alisation suivante ;
5. un choc futur ne modifie aucun �tat ni covariance ant�rieur ;
6. les d�cisions utilisent la derni�re s�ance commune de chaque semaine ISO ;
7. la s�rialisation JSONL est d�terministe octet par octet.

Commande :

```text
python -m unittest discover -s RL/tests -p test_g4_transition_builder.py -v
```

R�sultat local du 11 novembre 2026 : `Ran 7 tests ... OK`.

## Fronti�re causale

Les caract�ristiques r�trospectives � 1, 4, 13 et 52 semaines se terminent �
la cl�ture de d�cision. La r�alisation de march� commence strictement apr�s
cette cl�ture. Les distributions sont comptabilis�es � l'ex-date et `Adj Close`
n'est pas utilis� comme niveau d'�tat.

Le budget cumulatif et les poids h�rit�s sont propag�s par une transition
s�par�e du jeu de march�. Cette s�paration emp�che de traiter comme exog�ne une
ressource consomm�e par les actions pass�es.

## Travail encore requis

Les quatre fichiers bruts audit�s restent exclus de GitHub. Ils doivent �tre
restaur�s localement avec leurs SHA-256 gel�s avant de produire le JSONL
empirique et son rapport. Tant que ce gel empirique n'est pas reproduit :

- aucune comparaison oracle-myope n'est autoris�e ;
- aucun benchmark de performance n'est autoris� ;
- PPO, CQL et IQL restent interdits ;
- rien ne doit �tre fusionn� dans `main`.
