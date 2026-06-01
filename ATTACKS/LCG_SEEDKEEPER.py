"""
Attaque LCG - Récupération de graine par résolution linéaire

LCG : x_{n+1} = (a * x_n + c) % m

Si les paramètres a, c, m sont connus, une seule sortie suffit :
    seed = (x_1 - c) * a^{-1}  (mod m)
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'GENERATORS'))
from LCG import LCG


A = 1664525
C = 1013904223
M = 2**32


# --- Inverse modulaire (Euclide étendu) ---

def modinv(a, m):
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"Pas d'inverse : gcd({a}, {m}) = {g}")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


# --- Attaque ---

def recover_seed(x1):
    """Retrouve la graine depuis la première sortie observée."""
    return (modinv(A, M) * (x1 - C)) % M


# --- Démonstration ---
def demo_interception_x3():
    """
    Démonstration de l'attaque LCG Seed Keeper.
    DISCLAIMER: L'affichage de la démonstration à été améliorer via un assitant de développement IA.

    """
    A = 1664525
    C = 1013904223
    M = 2**32
    secret_seed = 450963

    print("\n" + "="*60)
    print("  ATTAQUE LCG : MACHINE À REMONTER LE TEMPS")
    print("="*60 + "\n")

    print(f"[>] Paramètres publics :")
    print(f"    A = {A} | C = {C} | M = 2^32\n")

    outputs = LCG(5, seed=secret_seed)
    
    print(f"[*] Séquence à retrouver : {outputs}")
    print("[*] Cible : Récupérer la graine (x0) à partir de x3 (index 2)")
    input("\n    [Appuyez sur Entrée pour isoler x3...]") 

    x3 = outputs[2]
    print(f"\n[!] VALEUR ISOLÉE : x3 = {x3}")
    
    inv_A = modinv(A, M)
    
    # Mise en forme lisible des formules
    print("\n--- FORMULE DE ROLLBACK ---")
    print("      x_{n-1} = (x_n - C) * A^-1  mod M")

    input("    [Appuyez sur Entrée pour remonter à x2...]")
    x2 = ((x3 - C) * inv_A) % M
    print(f"    Calcul : ({x3} - {C}) * {inv_A} % {M}  =>  x2 = {x2}")

    input("    [Appuyez sur Entrée pour remonter à x1...]")
    x1 = ((x2 - C) * inv_A) % M
    print(f"    Calcul : ({x2} - {C}) * {inv_A} % {M}  =>  x1 = {x1}")

    input("    [Appuyez sur Entrée pour extraire la Graine (x0)...]")
    seed_recuperee = ((x1 - C) * inv_A) % M
    print(f"\n GRAINE TROUVÉE : {seed_recuperee}")

    input("\n    [Appuyez sur Entrée pour vérifier le clonage...]")
    
    regen = LCG(5, seed=seed_recuperee)
    
    print("\n" + "="*60)
    print(f"[+] SUCCÈS : Clonage parfait de la séquence")
    print(f"    Originale : {outputs}")
    print(f"    Régénérée : {regen}")
    print(f"    La graine récupérée correspond à la graine secrète : {seed_recuperee == secret_seed}")
    print("="*60 + "\n")

if __name__ == "__main__":
    demo_interception_x3()
