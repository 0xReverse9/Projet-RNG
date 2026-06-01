"""
Génération du challenge CTF - réutilisation de nonce en AES-CTR.

AES-CTR est implémenté par dessus AES-ECB :
    keystream_i = AES-ECB(clé, nonce || compteur_i)
    C_i = P_i ^ keystream_i
https://crypto.stackexchange.com/questions/44648/implement-aes-ctr-on-top-of-aes-ecb

Scénario :
    - Deux images (l'image flag et une image blanche) sont chiffrées avec la même
      clé et le même nonce fixe, introduisant volontairement la vulnérabilité.
    - Le joueur reçoit les deux fichiers .bin et doit retrouver l'image flag
      en exploitant la réutilisation de nonce.
"""

from encrypt import aes_ctr_encrypt
from PIL import Image
import os


def build_white_image(reference_image_path, output_path):
    """Crée une image blanche RGB de la même taille que l'image de référence.

    L'image blanche (pixels à 0xFF) sert de plaintext entièrement connu,
    ce qui permet à l'attaquant de récupérer le keystream complet lors de l'exploitation.

    Args:
        reference_image_path (str): Chemin vers l'image dont on copie les dimensions.
        output_path (str): Chemin de sauvegarde de l'image blanche générée.
    """
    img = Image.open(reference_image_path).convert("RGB")
    W, H = img.size

    white = Image.new("RGB", (W, H), (255, 255, 255))
    white.save(output_path)

    print("Image blanche creee :", output_path, f"({W}x{H})")


def generate_challenge(image_path, key, nonce):
    """Chiffre une image en pixels bruts avec AES-CTR et sauvegarde le ciphertext.

    Les pixels sont lus en mode RGB brut (sans header de fichier image) afin que
    les deux images chiffrées aient exactement la même taille, condition nécessaire
    pour que l'attaque par plaintext connu fonctionne sur l'intégralité du fichier.
    Le ciphertext est sauvegardé à côté de l'image source avec l'extension .bin.

    Args:
        image_path (str): Chemin vers l'image à chiffrer.
        key (bytes): Clé secrète AES de 16 bytes.
        nonce (bytes): Nonce de 8 bytes, identique pour toutes les images du challenge.
    """
    # on lit les pixels bruts pour avoir une taille identique entre les deux images
    img = Image.open(image_path).convert("RGB")
    plaintext = img.tobytes()

    ciphertext = aes_ctr_encrypt(plaintext, key, nonce)
    cipher_path = image_path + '.bin'

    with open(cipher_path, 'wb') as f:
        f.write(ciphertext)

    print("Image chiffree :", cipher_path)
    print("Taille :", len(ciphertext), "bytes")


if __name__ == '__main__':
    # une seule cle et un nonce fixe pour les deux images - c'est la vuln
    key   = os.urandom(16)
    nonce = b'\x00' * 8

    build_white_image('CHALLENGE_FILES/image_flag.png', 'CHALLENGE_FILES/image_white.png')

    generate_challenge('CHALLENGE_FILES/image_white.png', key, nonce)
    generate_challenge('CHALLENGE_FILES/image_flag.png',  key, nonce)

    print("Cle (secrete) :", key.hex())