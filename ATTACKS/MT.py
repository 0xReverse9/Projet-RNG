
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from GENERATORS.mt import MT19937

# Le MT19937 produit ses nombres en deux phases :
#   1. twist()  — mélange le tableau interne X[0..623]
#   2. temper() — extrait X[cnt] et lui applique 4 transformations XOR+décalage
#
# Le temper améliore la distribution statistique mais est ENTIÈREMENT INVERSIBLE :
# chaque transformation est un XOR avec un décalage, ce qui se défait bit par bit.
#
# Idée de l'attaque : observer 624 sorties de temper(), inverser chacune,
# et reconstituer X[0..623] complet — l'état interne entier du générateur.
# La seed n'est jamais nécessaire.
# 

def get_bit(x, i):
    """
    Retourne le bit à la position i en partant du bit de de poids fort
    On travaille de gauche à droite pour traiter les bits dans l'ordre
    du décalage à droite, qui commence par les bits de poids fort

    pour w=32 :
        i=0  → bit 31 fort
        i=31 → bit 0  faible
    """
    return (x & (1 << (MT19937.w - i - 1)))

def reverse_bits(x):
	"""
    Retourne le miroir binaire de x sur 32 bits
    Le bit 31 devient le bit 0, le bit 0 devient le bit 31
 
    Utilité : les décalages à GAUCHE (inv_left) sont symétriques des décalages
    à droite. Plutôt que d'écrire un algorithme séparé pour inv_left, on
    retourne le nombre, on applique inv_right (qui sait traiter les décalages
    à droite), puis on retourne à nouveau le résultat.
    """

	rev = 0
	for i in range(MT19937.w):
		rev = (rev << 1)   # décale le résultat
		if(x > 0):
			if (x & 1 == 1): # si le bits de poids faibles vaut 1
				rev = (rev ^ 1) # on l'écrit dans le bits de poids faible de rev
			x = (x >> 1)
	return rev

def inv_left(y, a, b):
    """
    Inverse l'opération : y = x ^ ((x << a) & b)
    c'est-à-dire le symétrique de inv_right mais pour un décalage à GAUCHE
    """
    return reverse_bits(inv_right(reverse_bits(y), a, reverse_bits(b)))

def inv_right(y, a, b):

    """
    Inverse l'opération : y = x ^ ((x >> a) & b)
    c'est-à-dire retrouve x connaissant y, le décalage a et le masque b.
 
    Pourquoi c'est possible bit par bit :
        Les a premiers bits de poids fort de y sont IDENTIQUES à ceux de x
        (car (x >> a) décale de a positions, donc les a premiers bits ne sont
        pas affectés par le XOR). On les copie directement.
 
        Pour les bits suivants (position i >= a), on sait déjà x[i-a] (calculé
        au tour précédent), donc on peut isoler x[i] :
            y[i] = x[i] ^ (x[i-a] & b[i])
            x[i] = y[i] ^ (x[i-a] & b[i])    ← on XOR des deux côtés
 
    On reconstruit x de gauche à droite, bit par bit.
    """

    x = 0
    for i in range(MT19937.w):
        if (i < a):
            x |= get_bit(y, i)
        else:
            x |= (get_bit(y, i) ^ ((get_bit(x, i - a) >> a) & get_bit(b, i)))
    return x

def untemper(y):
	"""
    Inverse les 4 transformations du temper(), dans l'ordre INVERSE.
 
    Le temper applique dans l'ordre :
        1. y ^= (y >> u) & d      décalage droite, amplitude u=11, masque d
        2. y ^= (y << s) & b      décalage gauche, amplitude s=7,  masque b
        3. y ^= (y << t) & c      décalage gauche, amplitude t=15, masque c
        4. y ^= (y >> l)          décalage droite, amplitude l=18, masque 0xFFFFFFFF
 
    Pour inverser, on défait dans l'ordre inverse : 4 → 3 → 2 → 1.
    Chaque inv_right / inv_left retrouve l'entrée de l'étape correspondante.
 
    Résultat : on retrouve X[cnt], l'entier brut qui était dans le tableau
    interne APRÈS le twist, AVANT le temper.
    """

	x = y
	x = inv_right(x, MT19937.l, ((1 << MT19937.w) - 1))
	x = inv_left(x, MT19937.t, MT19937.c)
	x = inv_left(x, MT19937.s, MT19937.b)
	x = inv_right(x, MT19937.u, MT19937.d)
	return x

def compare_RNGs(r1, r2, lim = 100000):
	for i in range(lim):
		if(r1.temper() != r2.temper()):
			print("RNGs not the same; stopped at index ", i)
			return
	print("From inspecting the first ", lim, " numbers, the two RNGs are the same.")

def main():
	rng1 = MT19937(0) # victime
	rng2 = MT19937(1) # clone pour l'attaquant

	#On observe 624 sorties consécutives de rng1.
    # Pour chacune, untemper() inverse les 4 transformations du temper et
    # retrouve le X[i] post-twist exact. On l'écrit directement dans rng2.X[i].
    # Après cette boucle, rng2.X[] est identique au X[] de rng1 après son twist.

	for i in range(MT19937.n):
		rng2.X[i] = untemper(rng1.temper())

	# on à l'état interne, on peut donc twister et retrouver la même chose
	rng2.twist()
	compare_RNGs(rng1, rng2)

if __name__ == '__main__':
	main()
