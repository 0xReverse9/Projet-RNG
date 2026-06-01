class MT19937:
    """ Génrère une séquence de période de 2^{19937}-1$ tirages
    Son état interne peut être reconstruit après observation de 624 sorties donc il n'est pas cryptographiquement sur
    https://github.com/anneouyang/MT19937/blob/master/code/clone_mt19937.py
    """ 

    # Constantes optimisés sur 32 bits
    w, n = 32, 624 # w = largeur de mots en bits n = taille du tableau n*w-r = 19937 nb premier de mersenne
    f = 1812433253 # multpilicateur de knuth, couvre l'espace de 32 bits avant le premier twist
    m, r = 397, 31 # r = point de coupure dans le twist, la valeur de m assure que les bits se mélangent bien
    a = 0x9908B0DF # matrice de twist
    d, b, c = 0xFFFFFFFF, 0x9D2C5680, 0xEFC60000 # d masque de tempering    b et c calculé par ordinateur pour optimiser le problème
    u, s, t, l = 11, 7, 15, 18 # amplitude de décalage dans le temper

    def __init__(self, seed):
        # Initialise le générateur avec une graine H0
        self.X = [0] * MT19937.n # tableau interne de l'état
        self.cnt = 0
        self.initialize(seed)

    def initialize(self, seed):
        """remplit un tableau initial à partir de la seed 
        """
        self.X[0] = seed
        for i in range(1, MT19937.n):
            # application de la formule de réccurrence sur toute la séquence
            self.X[i] = (MT19937.f * (self.X[i - 1] ^ (self.X[i - 1] >> (MT19937.w - 2))) + i) & ((1 << MT19937.w) - 1)
        self.twist() # On effetcure un mélange avant de tirer des nombres

    def twist(self):
        """ Mélange les nombres en appliquant une transformation linéaire sur tous les nombres.
        Génère le futur échantillon de 624 
        """
        for i in range(MT19937.n):
            lower_mask = (1 << MT19937.r) - 1
            upper_mask =  (~lower_mask) & ((1 << MT19937.w) - 1)

            # Concaténation du bit de poids fort de X[i] avec les bits de poids faible de X[i+1]
            tmp = (self.X[i] & upper_mask) + (self.X[(i + 1) % MT19937.n] & lower_mask)
            # Décalle d'un bit à droite
            tmpA = tmp >> 1

            # Application de la matrice avec un XOR (^) avec la constante a si le bit de poids faible était 1
            if (tmp % 2):
                tmpA = tmpA ^ MT19937.a
            # Recombinaison avec le nombre situé m  pas plus loin
            self.X[i] = self.X[(i + MT19937.m) % MT19937.n] ^ tmpA
        self.cnt = 0

    def temper(self):
        """
        Extrait un nombre de l'état interne et applique une série de transformations
        bit à bit, le Tempering, pour améliorer la distribution statistique
        """
        if self.cnt == MT19937.n:
            self.twist()
        y = self.X[self.cnt]

        # opération de tempering 
        y = y ^ ((y >> MT19937.u) & MT19937.d) # Décalage à droite
        y = y ^ ((y << MT19937.s) & MT19937.b) # Décalage à gauche 
        y = y ^ ((y << MT19937.t) & MT19937.c) # Décalaage à gauche et masque c
        y = y ^ (y >> MT19937.l) # Décalage à droite
        self.cnt += 1
        return y & ((1 << MT19937.w) - 1)
	
    def random(self) -> float:
        """
        Génère un nombre et le normalise pour qu'il soit entre 0.0 et 1.0
        pour le test de ks
        """
        nombre_brut = self.temper()
        
        return nombre_brut / (2**32)

    def generer_liste_uniforme(self, taille: int) -> list[float]:
        """
        Génère une liste complète de nombres pour les tests
        """
        liste_nombres = []
        for _ in range(taille):
            liste_nombres.append(self.random())
        return liste_nombres
    
    def gener_liste(self, taille : int) -> list[float]:
        liste = [] 
        for _ in range(taille):
            liste.append(self.temper())
        return liste
    
    # commentaires fait par l'IA pour cette fonction
    def generer_bits(self, taille: int) -> list[int]:
        """
        Génère une liste de bits (0 ou 1) depuis le bit de poids fort de chaque sortie brute.
 
        Utilisé par :
            - testAutoCorrelation.SCC()  → attend list[int] de bits
            - testChiCarre.chi_carre()   → fonctionne avec list[int] de bits
 
        Returns:
            list[int]: séquence de 0 et de 1
        """
        return [(self.temper() >> 31) & 1 for _ in range(taille)]


def main():
    rng = MT19937(5489)
    
    taille_echantillon = 10000
    print(f"Génération de {taille_echantillon} nombres avec MT19937")
    ma_sequence = rng.generer_liste_uniforme(taille_echantillon)
    
    print(f"Aperçu des nombres générés : {ma_sequence[:3]}")

    sequence = rng.gener_liste(taille_echantillon)
    print(f"Aperçu des nombres générés : {sequence[:3]}")


if __name__ == '__main__':
    main()
