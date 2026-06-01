def LCG(n: int, seed: int = 1, a: int = 1664525, c: int = 1013904223, m: int = 2**32) -> list[int]:
    """
    
    Génère une séquence de n nombres pseudo-aléatoires avec un LCG
    La relation suivante dépend de l'actuel, on peut obtenir des valeurs pour lesquels on maximise la taille des séquences
    Args:
        n (int): nb de nombres
        seed (int, optional): seed
        a (int, optional): nombre optimisé pour le problème . Defaults to 1664525.
        c (int, optional): nb optimisé pour le problème. Defaults to 1013904223.
        m (int, optional): valeur du modulo optimisé pour le pb Defaults to 2**32.

    Returns:
        list[int]: _description_
    """
    sequence = []
    etat_actuel = seed
    
    for _ in range(n):
        etat_actuel = (a * etat_actuel + c) % m
        sequence.append(etat_actuel)
        
    return sequence

# Commentaires fait par l'IA pour ces 2 fonctions
def LCG_floats(n: int, seed: int = 1, a: int = 1664525,
               c: int = 1013904223, m: int = 2**32) -> list[float]:
    """
    Génère n nombres pseudo-aléatoires normalisés dans [0.0, 1.0).
 
    Utilisé par :
        - testKS.validate() → attend list[float] ∈ [0,1]
        - testShannonEntropy → fonctionne avec float
        - testChiCarre (après binarisation)
 
    Returns:
        list[float]: séquence de floats ∈ [0.0, 1.0)
    """
    bruts = LCG(n, seed=seed, a=a, c=c, m=m)
    return [x / m for x in bruts]
 
 
def LCG_bits(n: int, seed: int = 1, a: int = 1664525,
             c: int = 1013904223, m: int = 2**32) -> list[int]:
    """
    Génère n bits (0 ou 1) en seuillant le bit de poids fort de chaque entier.
 
    Utilisé par :
        - testAutoCorrelation.SCC()  → attend list[int] de bits
        - testChiCarre.chi_carre()   → fonctionne avec list[int] de bits
 
    Returns:
        list[int]: séquence de 0 et de 1
    """
    bruts = LCG(n, seed=seed, a=a, c=c, m=m)
    # On prend le bit de poids fort (bit 31) comme bit pseudo-aléatoire
    return [(x >> 31) & 1 for x in bruts]


ma_sequence = LCG(10)
print(ma_sequence)