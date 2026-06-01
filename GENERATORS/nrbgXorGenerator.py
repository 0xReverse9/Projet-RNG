"""
Permet de faire le xor de plusieurs sources alétaoires afin d'améliorer la source d'aléa de ces dernières
"""
import sys
import os
from struct import *

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GENERATORS import systemRandomGenerator, bbs_generator
from TESTS.testShannonEntropy import entropieShannon

def bin_tab_to_decimal(arr) -> int:
    """Permet de transformer la suite binnaire dans le tableau retourné par le générateur bbs en un integer

    Args:
        arr (list): un tableau de 0 et de 1 généré par le générateur bbs

    Returns:
        int: l'integer en sortie
    """
    
    number = "" # le str qui va contenir la suite binaire (plus facile à cast par la suite)
    for i in arr:
        number+=str(i) # on ajoute dans le str ce qu'il y a à la position i

    return str(int(number,base=2)) # une fois tout ajouté on va faire une conversion du binnaire vers la base 10

def gen_xor(source_1, source_2) -> bytes:
    """Permet de faire un xor bit à bit entre 2 source

    Args:
        source_1 (bytes): notre première source d'aléa
        source_2 (bytes): notre deuxième source d'aléa

    Returns:
        bytes: retourne le résultat du xor bit à bit de nos deux sources
    """
    return bytes(a ^ b for a,b, in zip(source_1,source_2)).hex() # permet de faire un xor bit à bit via un tableau en compréhension en parcourant nos deux sources


def test():
    """Permet de générer un test avec deux sources d'aléa différente (bbs et urandom)
    """

    # Les paramètres pour le générateur BBS
    p = bbs_generator.nombrePremier1024Bits()
    q = bbs_generator.nombrePremier1024Bits()
    seed = bbs_generator.pick_seed(p,q)
    n = 100

    # On procède à la génération d'un nombre aléatoire avec bbs
    bbs_output = bbs_generator.generate_bbs(p, q, seed, n)



    # on convertit nos deux sources en bytes
    source_1 = bytes(systemRandomGenerator.urandom(32),"utf-8") # Issue du générateur Urandom
    source_2 = bytes(bin_tab_to_decimal(bbs_output),"utf-8") # Issue du générateur bbs

    return gen_xor(source_1,source_2)