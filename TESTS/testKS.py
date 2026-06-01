import math
from scipy import stats

def cdf_uniforme(x: float) -> float:
    """
    cdf théorique pour une loi uniforme renvoi x
    """
    if x < 0.0:
        return 0.0
    elif x > 1.0:
        return 1.0
    else:
        return float(x)
    
    import math

def cdf_normale(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """
    cdf théorique pour une gautienne
    On prends des valeurs pour une loi centrée
    mu = moyenne
    sigma = écart type
    """
    return (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0)))) / 2.0


def ks(sequence : list[float]):
    n = len(sequence)
    donnees_triees = sorted(sequence)
    distance_max = 0.0

    for i in range(n):
        # on trie la séquence pour débuter le test
        x = donnees_triees[i]

        # on calcul P(X < x)
        cdf_theo = cdf_uniforme(x)
        #print(f"cdf théorique = {cdf_theo}")

        # on pars de i = 0 donc pour la première séquence 0/n
        ecdf_avant = i / n
        #print(f"\n ecdf avant {ecdf_avant}")

        # Fn(x) = (nb_observations <= x) / n
        ecdf_apres = (i + 1) / n
        #print(f"\n ecdf après {ecdf_apres}")

        # Calcul des distances absolues
        distance_bas = abs(ecdf_avant - cdf_theo)
        distance_haut = abs(ecdf_apres - cdf_theo)
        
        distance_max = max(distance_max, distance_bas, distance_haut)
        
    return distance_max

def ks_normale(sequence : list[float]):
    n = len(sequence)
    donnees_triees = sorted(sequence)
    distance_max = 0.0

    for i in range(n):
        # on trie la séquence pour débuter le test
        x = donnees_triees[i]

        # on calcul P(X < x)
        cdf_theo = cdf_normale(x)
        #print(f"cdf théorique = {cdf_theo}")

        # on pars de i = 0 donc pour la première séquence 0/n
        ecdf_avant = i / n
        #print(f"\n ecdf avant {ecdf_avant}")

        # Fn(x) = (nb_observations <= x) / n
        ecdf_apres = (i + 1) / n
        #print(f"\n ecdf après {ecdf_apres}")

        # Calcul des distances absolues
        distance_bas = abs(ecdf_avant - cdf_theo)
        distance_haut = abs(ecdf_apres - cdf_theo)
        
        distance_max = max(distance_max, distance_bas, distance_haut)
        
    return distance_max

def validate(sequence : list[float], alpha : float = 0.05):
    D = ks(sequence)
    print(f"Statistique D calculée : {D}")
    n = len(sequence)

    p_value = stats.kstwo.sf(D, n)

    print(f"P-value associé : {p_value:.4f}")

    if p_value < alpha:
        print("Conclusion : valeur-p < alpha-> On rejette H0. Le générateur est biaisé.")
    else:
        print("Conclusion : valeur-p > alpha -> On ne rejette pas H0. La distribution semble uniforme.")

def validate_normale(sequence : list[float], alpha : float = 0.05):
    D = ks_normale(sequence)
    print(f"Statistique D calculée : {D}")
    n = len(sequence)

    p_value = stats.kstwo.sf(D, n)

    print(f"P-value associé : {p_value:.4f}")

    if p_value < alpha:
        print("Conclusion : valeur-p < alpha-> On rejette H0. Le générateur est biaisé.")
    else:
        print("Conclusion : valeur-p > alpha -> On ne rejette pas H0. La distribution semble normale.")

echantillon = [0.2, 0.4, 0.5, 0.7]

#validate(echantillon)
#validate_normale(echantillon)

