import math
import matplotlib.pyplot as plt
import random

def box_muller():
    """
    Génère  2* n_paires de variables aléatoires independantes qui suivent une loi uniforme,
    Transforme celles-ci en 2 * n_paires de varianles aléatoires qui suivent une loi normale centrée réduite
    Affiche les courbes
    """
    # On tire U1 et U2 selon une loi uniforme 
    # U1 ou U2 ne doit pas être égale à 0 car sinon on ne pourra pas appliquer la fonction ln
    U1 = random.random()
    U2 = random.random()
    while U1 == 0.0:
        U1 = random.random()


    # On créer nos 2 variables aléatoires normales 
    r = math.sqrt(-2.0 * math.log(U1)) # Rayon (décroissance exponetielle représentant la cloche avec ln)
    theta = 2.0 * math.pi * U2
    
    Z1 = r * math.cos(theta) # Passage en coordonées cartésiennes et non polaires 
    Z2 = r * math.sin(theta) # Angle uniforme, on calcul l'angle au hasard

    return Z1, Z2

def tracer_méthode() -> list[float]:
    """
    Fonction pour tracer la courbe en cloche
    """
    valeurs = []

    for _ in range(15000):
        Z1, Z2 = box_muller()
        valeurs.append(Z1)
        valeurs.append(Z2)

    plt.hist(valeurs, bins=100, density=True, alpha=0.6, color='blue', edgecolor='black')

    plt.title("Distribution des nombres générés par Box-Muller")
    plt.xlabel("Valeur")
    plt.ylabel("Fréquence (Probabilité)")

    plt.grid(axis='y', alpha=0.75)

    plt.show()

tracer_méthode()

def echantillon(n: int = 15000):
    """
    Générer un échantillon pour tester nos fonction de test
    """
    valeurs = []

    for _ in range(n//2):
        Z1, Z2 = box_muller()
        valeurs.append(Z1)
        valeurs.append(Z2)

    return valeurs


# Les commentaires ont été fait avec l'IA afin de facilliter les explications de ces fonctions
def echantillon_uniforme(n: int = 15000) -> list[float]:
    """
    Génère n valeurs uniformes dans [0.0, 1.0)
    
    Utilisé par :
        - testKS.validate()
 
    Note : Box-Muller consomme des U1/U2 uniformes pour produire des normales.
    Cette fonction expose directement ces uniformes.
 
    Returns:
        list[float]: séquence de floats ∈ [0.0, 1.0)
    """
    return [random.random() for _ in range(n)]
 
 
def echantillon_bits(n: int = 15000) -> list[int]:
    """
    Génère n bits depuis les valeurs normales produites par Box-Muller,
    en seuillant à 0 (Z >= 0 → 1, Z < 0 → 0).
 
    Utilisé par :
        - testAutoCorrelation.SCC() → attend list[int] de bits
        - testChiCarre.chi_carre() → fonctionne avec list[int] de bits
 
    Returns:
        list[int]: séquence de 0 et de 1
    """
    bits = []
    for i in range((n + 1) // 2):
        Z1, Z2 = box_muller()
        bits.append(1 if Z1 >= 0 else 0)
        bits.append(1 if Z2 >= 0 else 0)
    return bits[:n]


sequence = echantillon()



