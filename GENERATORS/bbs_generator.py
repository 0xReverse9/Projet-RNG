import os
import random
import math

def nombrePremier1024Bits(taille=1024):
    """
    Function pour générer des nombre premier de 1024 bits
    Cette fonction est extraite d'un TP de Cryptographie fait en SEMESTRE 5

    Args:
        taille (int, optional): La taille souhaité en bits. Defaults to 1024.

    Returns:
        int: Un nombre premier de la taille spécifiée. Respectant les contraintes nécessaires pour le générateur BBS (p et q doivent être congrus à 3 mod 4).
    """
    isPrime = False

    def miller_rabin(n, k=40):  # k est le nombre de tests
        if n < 2:
            return False
        if n != 2 and n % 2 == 0:
            return False

        # Écrire n-1 comme d*2^r
        r, d = 0, n - 1
        while d % 2 == 0:
            d //= 2
            r += 1

        # Effectuer k tests
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)  # a^d mod n
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)  # x^2 mod n
                if x == n - 1:
                    break
            else:
                return False
        return True

    while not isPrime:
        # Générer un candidat de 1024 bits
        candidat = random.getrandbits(taille)
        # S'assurer que le premier bit n'est pas 0 pour garantir la taille de 1024 bits
        candidat = candidat + 2**(taille - 1)
        # S'assurer que le dernier bit est 1 pour garantir que le nombre est impair car les nombres pairs > 2 ne sont pas premiers
        if candidat % 2 == 0:
            candidat += 1

        # Contrainte BBS : p ≡ 3 (mod 4)
        # Si candidat % 4 == 1, on ajoute 2 pour passer à ≡ 3 (mod 4), en gardant le nombre impair
        if candidat % 4 != 3:
            candidat += 2

        #Vérifier divisibilité par petits nombres premiers
        petits_premiers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        if any(candidat % p == 0 for p in petits_premiers):
            continue

        # Test de primalité de Miller-Rabin
        isPrime = miller_rabin(candidat)

    return candidat

def rng():
    """
    Function pour générer un octet aléatoire.

    Returns:
        int: Un octet aléatoire.
    """
    return os.urandom(1)[0]

def random_int(bits):
    """
    Function pour générer un entier aléatoire de la taille spécifiée en bits.

    Args:
        bits (int): La taille de l'entier en bits.

    Returns:
        int: Un entier aléatoire de la taille spécifiée.
    """
    size = bits // 8
    data = bytes(rng() for _ in range(size))
    return int.from_bytes(data, "big")

def pick_seed(p, q, bits=128):
    """
    Fonction pour choisir une graine pour le générateur BBS.
    La graine doit être un entier aléatoire de la même taille que p et q, et doit être coprime à p et q.

    Args:
        p (int): Un nombre premier.
        q (int): Un nombre premier.
        bits (int, optional): La taille de la graine en bits. Par défault to 128.

    Returns:
        int: Une graine valide pour le générateur BBS.
    """
    while True:
        seed = random_int(bits)

        if seed in (0, 1):
            continue

        if math.gcd(seed, p) == 1 and math.gcd(seed, q) == 1:
            return seed
        
def generate_bbs(p, q, seed, n):
    """
    Fonction pour générer une suite de bits à l'aide du générateur BBS.

    Args:
        p (int): Un nombre premier.
        q (int): Un nombre premier.
        seed (int): Une graine valide pour le générateur BBS.
        n (int): Le nombre de bits à générer.

    Returns:
        list: Une liste de bits générés par le générateur BBS.
    """
    m = p * q
    x = seed
    result = []

    for _ in range(n):
        x = pow(x, 2, m)
        result.append(x % 2)

    return result

def main():
    # Génére des nombres premiers p et q
    p = nombrePremier1024Bits()
    q = nombrePremier1024Bits()

    # Choisir une seed pour le générateur BBS
    seed = pick_seed(p, q)
    n = 100

    # Générer une suite de bits avec le générateur BBS
    bbs_output = generate_bbs(p, q, seed, n)
    print("Bits générés par BBS:", bbs_output)

if __name__ == "__main__":
    main()
