"""
Implémentation de os.urandom : Utilise des sources d'aléas matérielles pour pouvoir générer un nombre pseudo-aléatoire en combinant ces source pour former un pool d'entropie
"""
import os
import hashlib
import psutil
import time
import hashlib
import sys

def get_hardware_randomness():
    """
    Permet de récupérer des nombres aléatoires à partir du pc comme source d'entropie 
    Sources d'aléa utilisées :
        - Horloges haute résolution (jitter du processeur via perf_counter et monotonic).
        - Métadonnées système (PID du processus, identifiant d'objet en mémoire).
        - Activité matérielle (cycles CPU, accès disque, trafic réseau).
    """ 
    randomness = []
    randomness.append(time.perf_counter_ns())
    randomness.append(time.monotonic_ns())
    randomness.append(os.getpid())
    randomness.append(psutil.cpu_times().user)
    randomness.append(psutil.disk_io_counters().read_time)
    randomness.append(psutil.cpu_freq().current)
    randomness.append(psutil.net_io_counters().packets_sent)
    randomness.append(id(object()))
    return randomness


def gen_entropy_pool(size):
    """
    Initialise un pool d'entropie par mélange itératif des sources matérielles.

    La fonction génère un pool de taille fixe (via SHA-256) en appliquant un hachage en chaîne : 
    chaque source d'aléa issue de la fonction get_hardware_randomness() est combinée au hash précédent. 
    Ce processus de cascade garantit que chaque bit du pool final dépend de l'intégralité 
    des sources de bruit collectées.
    """

    # On initialise le pool d'entropie à 0 au début pour après réaliser les opérations de hash entre ce pool et les valeurs de départ
    pool = bytes(size)

    # on récupère notre tableau avec les éléments aléatoire
    randomness_src = get_hardware_randomness()

    # premier hash entre le pool de 0 et le premier élément aléatoire
    h = hashlib.sha3_256()
    h.update(pool)
    h.update(str(randomness_src[0]).encode())
    pool = h.digest()

    # on hash le pool résultant avec chaque source suivante
    for src in randomness_src[1:]:
        h = hashlib.sha3_256()
        h.update(pool)
        h.update(str(src).encode())
        pool = h.digest()

    return pool


def urandom(random_size):
    """
    Génère une séquence pseudo-aléatoire en exploitant un pool d'entropie système.

    Le pool est constitué par le hachage successif de diverses sources d'aléa matérielles. 
    Chaque bloc de sortie est produit en combinant ce pool avec un compteur incrémentiel selon la taille demandée.
    """
    entropy_pool = gen_entropy_pool(32)

    output = b""
    counter = 0
    while len(output) < random_size:
        h = hashlib.sha3_256()
        h.update(entropy_pool)
        h.update(counter.to_bytes(4, "big"))
        output += h.digest()
        counter += 1
    
    return output[:random_size].hex()