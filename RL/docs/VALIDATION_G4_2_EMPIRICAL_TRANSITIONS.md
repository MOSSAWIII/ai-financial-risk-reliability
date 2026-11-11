# Validation G4.2 - gel empirique des transitions point-in-time

## Verdict

**`G4_2_EMPIRICAL_TRANSITIONS_FROZEN`.**

Le constructeur causal a produit 959 transitions hebdomadaires sur les quatre
poches SPY-IEF-GLD-BIL. La premi�re d�cision est dat�e du 30 mai 2008, apr�s 52
semaines compl�tes de pass� observable. La derni�re d�cision est dat�e du 9
octobre 2026 et sa r�alisation se termine � la derni�re cl�ture commune du 16
octobre 2026.

Le SHA-256 du JSONL obtenu est :

```text
dd95e2bd438fca90f9636cda3b8c7c86c1ab3b4e0c0834cc171f4af95fde9a0d
```

## Gel causal des sources

Les r�ponses Yahoo brutes contiennent des m�tadonn�es de march� en direct et
un `Adj Close` r�vis� par des distributions post�rieures � la p�riode demand�e.
Leur SHA brut change donc sans modification de l'information consomm�e par G4.

Le gel causal porte uniquement sur les dates, cl�tures et �v�nements de
distribution/split r�ellement utilis�s par le constructeur :

| Actif | SHA-256 causal |
|---|---|
| SPY | `1a5113d3ef96d4681bf6045ab34cb3d287ae37fe2a8ca186f890ddba71641948` |
| IEF | `da6a037ec2b2b927874d991b4254019c3073b31566fc798818b28a6d2797f267` |
| GLD | `f1aa5a7075feb3c33a9a3de88c38f0cad8e21d7a89277a436250bdd9f4722305` |
| BIL | `bd1b75b96dd83c07d54a1b115114a162a7b4f5f16471f947f406d26f0656cb02` |

Pour SPY et BIL, ces empreintes ont �t� reproduites exactement � partir des
octets gel�s dans la sauvegarde du 19 octobre puis � partir d'une nouvelle
acquisition Yahoo. Cela d�montre que la transformation �limine les champs
r�visables sans masquer une modification des cl�tures ou �v�nements utilis�s.

## Contr�les

- 4 878 s�ances communes du 30 mai 2007 au 16 octobre 2026 ;
- 35 actions long-only pleinement investies ;
- 52 semaines de pass� avant le premier �tat ;
- distributions cr�dit�es uniquement � l'ex-date ;
- aucune utilisation de `Adj Close` dans l'�tat ou la r�alisation ;
- aucun calcul de performance de politique ;
- aucun entra�nement RL.

La reconstruction a r�ussi dans GitHub Actions, ex�cution `43056193204`. Les
fichiers bruts et canoniques restent hors Git ; le code, les contrats, les
empreintes et le rapport sont versionn�s.

## �tape suivante autoris�e

Le laboratoire structurel G4.2 peut maintenant comparer, sur un environnement
synth�tique pr�specifi�, une programmation dynamique oracle et une politique
myope sous le m�me budget cumulatif. Les comparaisons historiques de politiques
et PPO/CQL/IQL restent interdits.
