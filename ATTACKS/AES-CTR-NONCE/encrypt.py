"""
Implémentation de l'attaque AES-CTR par réutilisation de nonce (nonce reuse)
avec connaissance partielle du plaintext (magic bytes PNG/JPEG).

Implémentation d'AES-CTR par dessus d'AES-ECB 
https://crypto.stackexchange.com/questions/44648/implement-aes-ctr-on-top-of-aes-ecb

Scénario :
    - Un fichier image a été chiffré avec AES en mode CTR
    - Le même nonce a été réutilisé pour chiffrer plusieurs messages avec la même clé
    - On sait que le fichier chiffré est une image au format PNG ou JPEG
    - Les formats PNG et JPEG commencent toujours par une séquence fixe et connue (magic bytes)

Principe de l'attaque :
    - AES-CTR chiffre via : C = P ^ AES(clé, nonce || compteur)
    - Si le nonce est réutilisé, le keystream est identique pour tous les messages
    - Comme on connaît P[0:n] (magic bytes), on récupère K[0:n] = C[0:n] ^ P[0:n]
    - Ce keystream permet ensuite de déchiffrer les n premiers bytes de tout autre
      ciphertext chiffré avec le même nonce
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """Effectue l'opération XOR octet par octet entre deux séquences de bytes
    Utilisé pour chiffrer/déchiffrer un bloc de plaintext avec le keystream AES-CTR

    Args:
        a (bytes): Premier opérande du XOR
        b (bytes): Deuxième opérande du XOR

    Raises:
        AssertionError: Si a et b n'ont pas la même longueur

    Returns:
        bytes: Résultat de a ^ b, de même longueur que les entrées
    """
   
    if len(a) != len(b):
        raise Exception('Les deux sources doivent avoir la même taille')
    return bytes(x ^ y for x,y in zip(a,b))

def make_counter_block(nonce: bytes, counter: int) -> bytes:
    """Construit le bloc de 16 bytes donné en entrée à AES en mode CTR
    Ce bloc est la concaténation du nonce et du compteur,
    il est chiffré par AES-ECB pour générer le keystream

    Args:
        nonce (bytes): Nombre utilisé une seule fois, doit faire exactement 8 bytes
        counter (int): Compteur de bloc, incrémenté à chaque nouveau bloc de plaintext

    Raises:
        Exception: Si le nonce ne fait pas exactement 8 bytes

    Returns:
        bytes: Bloc de 16 bytes (nonce || counter) prêt à être chiffré par AES
    """
    if len(nonce) != 8:
        raise Exception('La longueur du nonce doit être de 8 bytes')
    counter_bytes = counter.to_bytes(8, byteorder='little')
    return nonce + counter_bytes

def aes_ecb_encrypt(key: bytes, block: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(block)

def aes_ctr_encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Chiffre un plaintext avec AES en mode CTR.
    Le chiffrement et le déchiffrement sont la même opération (XOR symétrique).

    Args:
        plaintext (bytes): Le message à chiffrer.
        key (bytes): La clé secrète AES de 16 bytes.
        nonce (bytes): Le nonce de 8 bytes, doit être unique par message.

    Returns:
        bytes: Le ciphertext chiffré de même longueur que le plaintext.
    """
    ciphertext = b''
    blocs = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
    
    for i, bloc in enumerate(blocs):
        counter_block = make_counter_block(nonce, i)
        keystream = aes_ecb_encrypt(key, counter_block)
        ciphertext += xor_bytes(keystream[:len(bloc)], bloc)
    
    return ciphertext

