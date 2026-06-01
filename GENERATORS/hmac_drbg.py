import hmac
import hashlib

TAILLE_SORTIE = 32
TAILLE_GRAINE = 32

# Intervalle de reseed après un certain nombre de générations
INTERVALLE_RESEED = 2**48
MAX_OCTETS_PAR_REQUETE = 2**19 // 8


def hmac_sha256(cle, message):
    """
    Fonction de calcul du HMAC-SHA256, utilisée dans HMAC_DRBG.

    Args:
        cle (bytes): La clé pour le calcul du HMAC
        message (bytes): Le message à hasher

    Returns:
        bytes: Le résultat du HMAC-SHA256
    """
    return hmac.new(cle, message, hashlib.sha256).digest()


class HMAC_DRBG:

    def __init__(self):
        # Initialisation de HMAC_DRBG avec des valeurs par défaut pour K et V
        # K est la clé utilisée pour le calcul
        self.K = b'\x00' * TAILLE_SORTIE
        # V est al valeur utilisée pour la génération de nb
        self.V = b'\x00' * TAILLE_SORTIE
        self.compteur = 0

    def update(self, data):
        """
        Fonction de mise à jour de HMAC_DRBG.
        La mise à jour est effectuée en utilisant les données fournies pour recalculer K et V.
        K est mis à jour en utilisant V, un octet de contrôle (0x00 ou 0x01) et les données d'entrée, 
        tandis que V est mis à jour en utilisant le nouveau K.

        Args:
            data (bytes): Les données à intégrer dans la mise à jour
        """
        self.K = hmac_sha256(self.K, self.V + b'\x00' + data)
        self.V = hmac_sha256(self.K, self.V)

        if data == b"":
            return

        self.K = hmac_sha256(self.K, self.V + b'\x01' + data)
        self.V = hmac_sha256(self.K, self.V)

    def instantiate(self, entropie, nonce, personnalisation):
        """
        Fonction d'instanciation de HMAC_DRBG.
        La fonction d'instanciation initialise l'état interne de HMAC_DRBG en combinant les données d'entropie, 
        le nonce et les données de personnalisation pour créer une graine. 
        Cette graine est ensuite utilisée pour mettre à jour les valeurs de K et V, 
        préparant ainsi le générateur à produire des nombres pseudo-aléatoires.

        Args:
            entropie (bytes): La source d'entropie pour l'instanciation
            nonce (bytes): Le nonce
            personnalisation (bytes): Les données de personnalisation
        """
        seed = entropie + nonce + personnalisation
        self.K = b'\x00' * TAILLE_SORTIE
        self.V = b'\x00' * TAILLE_SORTIE
        self.update(seed)
        self.compteur = 1

    def generate(self, nbOctets, entree_additionnelle=b""):
        """
        Fonction de génération de HMAC_DRBG.
        La fonction de génération produit une séquence de nombres pseudo-aléatoires en utilisant l'état interne de HMAC_DRBG. 
        Si des données d'entrée supplémentaires sont fournies, elles sont intégrées dans le processus de génération pour renforcer la sécurité. 
        La fonction vérifie également si un reseed est nécessaire après un certain nombre de générations.

        Args:
            nbOctets (int): Le nombre d'octets à générer
            entree_additionnelle (bytes): Les données d'entrée supplémentaires
        """
        if self.compteur >= INTERVALLE_RESEED:
            raise Exception("Reseed nécessaire")

        if entree_additionnelle != b"":
            self.update(entree_additionnelle)

        output = b""
        while len(output) < nbOctets:
            self.V = hmac_sha256(self.K, self.V)
            output += self.V

        sortie = output[:nbOctets]
        self.update(entree_additionnelle)
        self.compteur += 1
        return sortie

    def reseed(self, entropie, entree_additionnelle=b""):
        """
        Fonction de reseed de HMAC_DRBG.
        La fonction de reseed permet de réinitialiser l'état interne de HMAC_DRBG 
        en utilisant de nouvelles données d'entropie et des données d'entrée supplémentaires. 

        Args:
            entropie (bytes): Les données d'entropie
            entree_additionnelle (bytes): Les données d'entrée supplémentaires
        """
        seed = entropie + entree_additionnelle
        self.update(seed)
        self.compteur = 1

def main():
    drbg = HMAC_DRBG()
    entropie = b"YanisLaMeilleurePersonneDuMonde"
    nonce = b"EwenLeMeilleur"
    personnalisation = b"LudoLePlusFort"

    # Instanciation de HMAC_DRBG avec les données d'entropie, le nonce et les données de personnalisations
    drbg.instantiate(entropie, nonce, personnalisation)

    # Génération de 64 octets de données pseudo-aléatoires
    nbOctets = 64

    # Génération de la sortie pseudo-aléatoire en utilisant HMAC_DRBG
    sortie = drbg.generate(nbOctets)
    print(f"Sortie générée (hex): {sortie.hex()}")

if __name__ == "__main__":
    main()