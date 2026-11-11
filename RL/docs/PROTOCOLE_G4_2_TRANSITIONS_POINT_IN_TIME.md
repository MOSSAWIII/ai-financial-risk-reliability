# G4.2 - transitions point-in-time et �tat contr�l�

## D�cision gel�e

G4.2 s�pare deux objets qui ne doivent pas �tre confondus :

1. l'�tat de march� observable � la cl�ture de d�cision ;
2. l'�tat contr�l� h�rit� des d�cisions ant�rieures.

� la derni�re s�ance commune de chaque semaine ISO, l'information admissible
s'arr�te � la cl�ture du jour. La r�alisation associ�e � l'action commence
strictement apr�s cette cl�ture et se termine � la cl�ture de d�cision suivante.
Le rendement de cette r�alisation ne peut donc jamais entrer dans l'�tat qui la
pr�c�de.

## Rendements et distributions

Pour l'actif \(i\), le facteur journalier est

\[
G_{i,d}=\frac{P_{i,d}+D_{i,d}}{P_{i,d^-}},
\]

o� \(P\) est la cl�ture Yahoo normalis�e des splits et \(D\) la distribution
Yahoo dat�e ex-dividende. Les distributions sont ajout�es une seule fois, le
jour ex-dividende. `Adj Close` n'est pas utilis� dans les variables d'�tat :
cela �vite qu'un ajustement r�trospectif fournisse un niveau artificiellement
r�vis� par un �v�nement futur.

Le facteur hebdomadaire est le produit des facteurs journaliers apr�s la
cl�ture de d�cision jusqu'� la cl�ture suivante, bornes respectivement exclue
et incluse.

## �tat contr�l�

Avant l'action, l'�tat contient les poids d�riv�s par le march�
\(w_{t^-}\), le budget restant \(B_t\), la richesse \(W_t\) et son maximum
historique. Pour une cible \(a_t\),

\[
\tau_t=\tfrac12\lVert a_t-w_{t^-}\rVert_1,
\qquad
\tau_t\leq\min(0.25,B_t),
\]

\[
B_{t+1}=B_t-\tau_t.
\]

Apr�s la r�alisation de march� \(G_{t+1}\), les poids h�rit�s suivants sont

\[
w_{i,(t+1)^-}=\frac{a_{i,t}G_{i,t+1}}
{\sum_j a_{j,t}G_{j,t+1}}.
\]

Cette d�rive et la consommation irr�versible du budget rendent les d�cisions
interd�pendantes. Une politique myope ne peut pas r�cup�rer demain le budget
qu'elle d�pense aujourd'hui.

## Variables point-in-time

L'�tat de march� retient, pour chaque poche, les log-rendements r�trospectifs �
1, 4 et 13 semaines, les volatilit�s � 13 et 52 semaines, ainsi que la matrice
de covariance � 52 semaines. Toutes les fen�tres se terminent � la cl�ture de
d�cision. Le premier �tat utilisable exige 52 semaines compl�tes.

## Limite de ce jalon

Le code construit des transitions et v�rifie leur causalit�. Il ne choisit
aucune politique, ne compare aucune performance et n'autorise ni PPO, ni CQL,
ni IQL. L'exp�rience de s�quentialit� oracle-versus-myope vient apr�s le gel
empirique de ces transitions.
