from collections import Counter
from scipy.stats import chi2


# Fonction pour extraire les patterns d'une séquence d'octet ou de chiffre afin d'en sortir les statistiques
def count_patterns(sequence : str) -> tuple[dict, int]:
    frequences = Counter(sequence)
    return frequences, len(sequence)
 
def chi_carre(sequence: str, k: int = 2, alpha : int = 0.05) -> float:
    compteur, taille = count_patterns(sequence)

    # E = nombre d'occurrences attendu par catégorie pour un hasard parfait
    E = taille / k 
    X = 0.0
    for occurrences in compteur.values():
        # formule de chi carré
        X += ((occurrences - E)**2) / E 

    categories_manquantes = k - len(compteur)

    # on gère le cas ou une suite à été générée mais une ou plusieurs valeurs n'apparaissent pas dedans 
    X += categories_manquantes * (((0 - E)**2) / E)

    # dégrés de liberté
    v = k - 1

    # calcul de la p_value avec la bibliothèque scipy
    p_value = chi2.sf(X, v)

    # Comparaison de la p-value calculé avec notre seuil alpha
    if p_value < alpha:
        print("On rejette H0, générateur non aléatoire")
    else:
        print("Correct, le générateur est aléatoire")
    return X

tab = "1111111111000000000"
frequence, taille = count_patterns(tab)
#print(f"{frequence.keys()}")

#X = chi_carre(tab)
#print(X)
