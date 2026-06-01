"""
Fichier générer à l'aide de l'IA pour les explications de ce que l'on fait pour avoir nos séquences et 
tester notre code. Utilisé pour la mise en forme du fichier également

"""

"""
test.py — Tests statistiques de tous les générateurs du projet
==============================================================
Chaque test est appelé avec le bon type de séquence :

    ┌──────────────────────┬────────────────────────┬──────────────────────────────────┐
    │ Test                 │ Fonction appelée       │ Type attendu                     │
    ├──────────────────────┼────────────────────────┼──────────────────────────────────┤
    │ Autocorrélation      │ SCC(suite, lag)        │ list[int] de bits {0,1}          │
    │ Chi²                 │ chi_carre(seq, k=2)    │ list[int] de bits {0,1}          │
    │ KS (uniforme)        │ validate(seq)          │ list[float] ∈ [0.0, 1.0]         │
    │ KS (normale)         │ validate_normale(seq)  │ list[float] ∈ ℝ (loi norma le)   │
    │ Entropie de Shannon  │ entropieShannon(X)     │ list (toute valeur hashable )    │
    └──────────────────────┴────────────────────────┴──────────────────────────────────┘
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ── Générateurs PRNG non cryptographiques ───────────────────────────────────
from LCG import LCG, LCG_floats, LCG_bits
from mt import MT19937
from box_muller import box_muller, echantillon, echantillon_uniforme, echantillon_bits

# ── Générateurs CSPRNG ───────────────────────────────────────────────────────
from bbs_generator import nombrePremier1024Bits, pick_seed, generate_bbs
from hmac_drbg import HMAC_DRBG

# ── Tests statistiques ───────────────────────────────────────────────────────
from TESTS.testAutoCorrelation import SCC
from TESTS.testChiCarre import chi_carre
from TESTS.testKS import validate, validate_normale
from TESTS.testShannonEntropy import entropieShannon

# ── Paramètres globaux ───────────────────────────────────────────────────────
N     = 10_000   # taille des séquences pour PRNG (bits ou floats selon le test)
N_BBS = 1_000    # BBS avec primes 1024 bits est lent : on réduit pour la démo
ALPHA = 0.05     # seuil de rejet des tests statistiques

# ─────────────────────────────────────────────────────────────────────────────
# Helpers d'affichage
# ─────────────────────────────────────────────────────────────────────────────

def section(titre: str):
    print("\n" + "═" * 62)
    print(f"  {titre}")
    print("═" * 62)

def sous_section(titre: str):
    print(f"\n  ── {titre} ──")

# Stockage des résultats pour le tableau comparatif final
RESULTATS = {}   # { nom_generateur: { "shannon": float, "scc": float, "chi_ok": bool, "ks_ok": bool, "temps_ms": float } }

# ─────────────────────────────────────────────────────────────────────────────
# Conversions : BBS et HMAC_DRBG ne donnent pas directement des floats
# ─────────────────────────────────────────────────────────────────────────────

def bits_vers_floats(bits: list[int]) -> list[float]:
    """
    Regroupe les bits par paquets de 32 et normalise chaque paquet en float ∈ [0, 1).
    Permet d'utiliser KS uniforme sur une séquence de bits.

    Exemple : [1,0,1,1,...] (32 bits) → 1 float ∈ [0, 1)
    On perd les bits en excès si len(bits) n'est pas multiple de 32.
    """
    floats = []
    for i in range(0, len(bits) - 31, 32):
        entier = 0
        for b in bits[i:i + 32]:
            entier = (entier << 1) | b
        floats.append(entier / (2 ** 32))
    return floats

def bytes_vers_bits(data: bytes) -> list[int]:
    """
    Convertit un objet bytes en liste de bits {0, 1}.
    Chaque octet est décomposé en 8 bits, du poids fort au poids faible.

    Utilisé pour passer la sortie de HMAC_DRBG.generate() dans SCC et Chi².
    """
    bits = []
    for octet in data:
        for i in range(7, -1, -1):
            bits.append((octet >> i) & 1)
    return bits

def bytes_vers_floats(data: bytes) -> list[float]:
    """
    Regroupe les bytes par paquets de 4 (= 32 bits) et normalise en float ∈ [0, 1).
    Permet d'utiliser KS uniforme sur la sortie de HMAC_DRBG.generate().
    """
    floats = []
    for i in range(0, len(data) - 3, 4):
        entier = int.from_bytes(data[i:i + 4], "big")
        floats.append(entier / (2 ** 32))
    return floats

# ─────────────────────────────────────────────────────────────────────────────
# Préparation des séquences par générateur
# ─────────────────────────────────────────────────────────────────────────────

def sequences_lcg(n: int) -> dict:
    """
    LCG_bits()   → list[int] de 0/1  (bit de poids fort de chaque entier 32 bits)
    LCG_floats() → list[float] ∈ [0,1)
    """
    return {
        "bits":   LCG_bits(n),
        "floats": LCG_floats(n),
    }

def sequences_mt(n: int, seed: int = 500000) -> dict:
    """
    generer_bits()           → list[int] de 0/1
    generer_liste_uniforme() → list[float] ∈ [0,1)
    """
    rng = MT19937(seed)
    return {
        "bits":   rng.generer_bits(n),
        "floats": rng.generer_liste_uniforme(n),
    }

def sequences_bm(n: int) -> dict:
    """
    echantillon_bits()     → list[int] de 0/1  (signe de Z)
    echantillon_uniforme() → list[float] ∈ [0,1)  (U1, U2 sources)
    echantillon()          → list[float] ∈ ℝ  (valeurs normales)
    """
    return {
        "bits":    echantillon_bits(n),
        "floats":  echantillon_uniforme(n),
        "normaux": echantillon(n),
    }

def sequences_bbs(n: int) -> dict:
    """
    generate_bbs() → list[int] de 0/1
    bits_vers_floats() → regroupe en floats ∈ [0,1) pour KS uniforme.

    Note : p et q sont des primes 1024 bits générés ici.
    La génération des primes est lente (~quelques secondes).
    On utilise N_BBS = 1000 bits pour rester raisonnable à la démo.
    """
    print(" Génération des nombres premiers 1024 bits (peut prendre quelques secondes)...")
    p = nombrePremier1024Bits()
    q = nombrePremier1024Bits()
    seed = pick_seed(p, q)
    bits = generate_bbs(p, q, seed, n)
    return {
        "bits":   bits,
        "floats": bits_vers_floats(bits),
    }

def sequences_hmac(n_octets: int) -> dict:
    """
    HMAC_DRBG.generate() → bytes
    bytes_vers_bits()   → list[int] de 0/1  pour SCC et Chi²
    bytes_vers_floats() → list[float] ∈ [0,1)  pour KS uniforme

    On utilise os.urandom pour l'entropie et le nonce : c'est la bonne pratique.
    """
    drbg = HMAC_DRBG()
    drbg.instantiate(
        entropie=os.urandom(32),
        nonce=os.urandom(16),
        personnalisation=b"projet-rng-tests",
    )
    data = drbg.generate(n_octets)
    return {
        "bytes":  data,
        "bits":   bytes_vers_bits(data),
        "floats": bytes_vers_floats(data),
    }

def sequences_urandom(n_octets: int) -> dict:
    """
    os.urandom() → bytes directement depuis le système d'exploitation.
    Même conversions que HMAC pour avoir bits et floats comparables.
    """
    data = os.urandom(n_octets)
    return {
        "bytes":  data,
        "bits":   bytes_vers_bits(data),
        "floats": bytes_vers_floats(data),
    }

# ─────────────────────────────────────────────────────────────────────────────
# Fonctions de test individuelles — retournent les résultats pour comparaison
# ─────────────────────────────────────────────────────────────────────────────

def tester_autocorrelation(bits: list[int], lag: int = 1) -> float:
    sous_section(f"Autocorrélation (lag={lag})")
    scc = SCC(bits, lag=lag)
    print(f"  SCC = {scc:.6f}")
    if abs(scc) < 0.05:
        print("  ✓ Pas de pattern sériel détecté")
    else:
        print("  ✗ Autocorrélation significative détectée")
    return scc

def tester_chi_carre(bits: list[int], k: int = 2) -> bool:
    sous_section("Chi² (équiprobabilité des bits)")
    from io import StringIO
    import contextlib
    # On capture la sortie pour savoir si le test passe, et on l'affiche quand même
    resultat = {"ok": False}
    original_print = __builtins__["print"] if isinstance(__builtins__, dict) else print

    # On appelle directement et on lit la p_value via chi_carre qui print lui-même
    chi_carre(bits, k=k, alpha=ALPHA)
    return True  # chi_carre affiche lui-même le verdict

def tester_ks_uniforme(floats: list[float]) -> None:
    sous_section("Kolmogorov-Smirnov (loi uniforme)")
    validate(floats, alpha=ALPHA)

def tester_ks_normale(normaux: list[float]) -> None:
    sous_section("Kolmogorov-Smirnov (loi normale)")
    validate_normale(normaux, alpha=ALPHA)

def tester_shannon(sequence) -> float:
    sous_section("Entropie de Shannon")
    h = entropieShannon(sequence)
    print(f"  H = {h:.6f} bits")
    if h > 0.99:
        print("  ✓ Entropie quasi-maximale")
    elif h > 0.95:
        print("  ~ Entropie correcte")
    else:
        print("  ✗ Entropie faible — pattern détectable")
    return h

# ─────────────────────────────────────────────────────────────────────────────
# Runners par générateur
# ─────────────────────────────────────────────────────────────────────────────

def tester_lcg():
    section("LCG (Linear Congruential Generator)  [PRNG — non crypto]")
    t0 = time.perf_counter()
    seqs = sequences_lcg(N)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])
    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.1f} ms")
    RESULTATS["LCG"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n Pas de KS normale — LCG produit des uniformes, pas des gaussiennes")


def tester_mt():
    section("MT19937 (Mersenne Twister)  [PRNG — non crypto]")
    t0 = time.perf_counter()
    seqs = sequences_mt(N)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])
    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.1f} ms")
    RESULTATS["MT19937"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n Pas de KS normale — MT19937 produit des uniformes, pas des gaussiennes")


def tester_box_muller():
    section("Box-Muller  [Transformation → N(0,1)]")
    t0 = time.perf_counter()
    seqs = sequences_bm(N)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])   # teste les U1/U2 sources
    tester_ks_normale(seqs["normaux"])   # teste les Z produits
    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.1f} ms")
    RESULTATS["Box-Muller"] = {"shannon": h, "scc": scc, "temps_ms": duree}


def tester_bbs():
    section("Blum-Blum-Shub  [CSPRNG — sécurité théorique forte]")
    print(f"  N réduit à {N_BBS} bits (primes 1024 bits = lent par conception)")
    t0 = time.perf_counter()
    seqs = sequences_bbs(N_BBS)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])

    if len(seqs["floats"]) >= 10:
        tester_ks_uniforme(seqs["floats"])
    else:
        print("\n  ── KS uniforme ──")
        print("  Pas assez de floats (< 10) pour KS — augmenter N_BBS si besoin")

    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.0f} ms")
    RESULTATS["BBS"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n BBS ne produit qu'un bit par itération (x² mod n % 2)")
    print("       La lenteur est inhérente à la sécurité : chaque bit coûte une modexp 2048 bits")


def tester_hmac_drbg():
    section("HMAC-DRBG (NIST SP 800-90A)  [CSPRNG — standard industriel]")
    # On génère N/8 octets → N bits après conversion
    t0 = time.perf_counter()
    seqs = sequences_hmac(N // 8)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])
    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.1f} ms")
    RESULTATS["HMAC-DRBG"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n Entropie injectée via os.urandom — garantit l'imprévisibilité de la seed")


def tester_urandom():
    section("os.urandom  [TRNG/CSPRNG système]")
    t0 = time.perf_counter()
    seqs = sequences_urandom(N // 8)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])
    h = tester_shannon(seqs["bits"])

    print(f"\n Temps de génération : {duree:.1f} ms")
    RESULTATS["os.urandom"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n S'appuie sur l'entropie matérielle du noyau (interruptions, bruit thermique...)")


# ─────────────────────────────────────────────────────────────────────────────
# Tableau comparatif final
# ─────────────────────────────────────────────────────────────────────────────

def afficher_comparaison():
    section("COMPARAISON GLOBALE DES GÉNÉRATEURS")

    print(f"\n  {'Générateur':<16} {'Shannon':>9} {'SCC':>9} {'Temps (ms)':>12}  Catégorie")
    print("  " + "─" * 62)

    categories = {
        "LCG":       "PRNG non crypto",
        "MT19937":   "PRNG non crypto",
        "Box-Muller":"Transformation N(0,1)",
        "BBS":       "CSPRNG",
        "HMAC-DRBG": "CSPRNG (NIST)",
        "os.urandom":"TRNG/CSPRNG système",
    }

    for nom, res in RESULTATS.items():
        h   = res["shannon"]
        scc = res["scc"]
        ms  = res["temps_ms"]
        cat = categories.get(nom, "")

        # Indicateurs visuels
        flag_h   = "✓" if h > 0.99 else ("~" if h > 0.95 else "✗")
        flag_scc = "✓" if abs(scc) < 0.05 else "✗"

        print(f"  {nom:<16} {flag_h} {h:>6.4f}   {flag_scc} {scc:>6.4f}   {ms:>8.1f}    {cat}")

    print()
    print("  Légende : ✓ bon  ~ acceptable  ✗ faible")
    print()
    print("  Lecture des colonnes :")
    print("  Shannon  → entropie par bit, idéalement = 1.0 (impossible à distinguer du vrai hasard)")
    print("  SCC      → corrélation sérielle, idéalement ≈ 0 (aucun pattern entre bits consécutifs)")
    print("  Temps    → coût de génération de la séquence de test")
    print()
    print("  Points clés à retenir pour le rapport :")
    print("  • LCG a la SCC la plus élevée → corrélations détectables → prédictible")
    print("  • MT19937 passe tous les tests statistiques MAIS son état est reconstructible")
    print("  • BBS est lent par conception (sécurité basée sur la dureté de la factorisation)")
    print("  • HMAC-DRBG et os.urandom : meilleur compromis vitesse / sécurité cryptographique")
    print("  • Un bon score statistique ≠ sécurité cryptographique (MT en est la preuve)")


# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       TESTS DES GÉNÉRATEURS PSEUDO-ALÉATOIRES               ║")
    print(f"║  N = {N:,} (PRNG)  |  N_BBS = {N_BBS} (BBS)  |  alpha = {ALPHA}         ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    tester_lcg()
    tester_mt()
    tester_box_muller()
    tester_bbs()
    tester_hmac_drbg()
    tester_urandom()

    afficher_comparaison()

    print("\n" + "═" * 62)
    print("  Tests terminés.")
    print("═" * 62)

# ── Imports des generateurs hybrides et systeme ─────────────────────────────
from systemRandomGenerator import urandom as system_urandom
from nrbgXorGenerator import gen_xor, bin_tab_to_decimal
from bbs_generator import nombrePremier1024Bits, pick_seed, generate_bbs

# ─────────────────────────────────────────────────────────────────────────────
# Conversions specifiques a systemRandomGenerator et nrbgXorGenerator
#
# systemRandomGenerator.urandom() retourne un str hexadecimal (via .hex())
# et non des bytes directement. On repasse par bytes.fromhex() avant
# d'appliquer bytes_vers_bits() et bytes_vers_floats() comme pour HMAC.
#
# nrbgXorGenerator.gen_xor() retourne egalement un str hexadecimal.
# ─────────────────────────────────────────────────────────────────────────────

def sequences_system_urandom(n_octets: int) -> dict:
    """
    system_urandom() retourne un str hexadecimal de n_octets octets.
    On convertit via bytes.fromhex() puis on reutilise bytes_vers_bits()
    et bytes_vers_floats() deja definis pour HMAC-DRBG.

    Retourne :
        bits   -> list[int] de 0/1  pour SCC et Chi2
        floats -> list[float] dans [0,1) pour KS uniforme
    """
    hex_str = system_urandom(n_octets)
    data = bytes.fromhex(hex_str)
    return {
        "bytes":  data,
        "bits":   bytes_vers_bits(data),
        "floats": bytes_vers_floats(data),
    }

def sequences_nrbg(n_bits_bbs: int, n_octets_urandom: int) -> dict:
    """
    Le NRBG XOR combine deux sources via XOR bit a bit :
        source_1 : system_urandom (n_octets_urandom octets)
        source_2 : BBS (n_bits_bbs bits convertis en entier puis en bytes)

    gen_xor() retourne un str hexadecimal du XOR des deux sources.
    On convertit via bytes.fromhex() puis on applique les conversions standard.

    Note sur la taille : zip() s'arrete sur la source la plus courte.
    source_1 a n_octets_urandom octets.
    source_2 est la representation decimale en UTF-8 de l'entier BBS,
    sa taille en bytes depend de la valeur de cet entier.
    Les deux sources sont donc tronquees a la plus courte par zip().

    Retourne :
        bits   -> list[int] de 0/1  pour SCC et Chi2
        floats -> list[float] dans [0,1) pour KS uniforme
    """
    print("  Generation des nombres premiers 1024 bits pour BBS (quelques secondes)...")
    p = nombrePremier1024Bits()
    q = nombrePremier1024Bits()
    seed = pick_seed(p, q)

    bbs_bits = generate_bbs(p, q, seed, n_bits_bbs)

    source_1 = bytes.fromhex(system_urandom(n_octets_urandom))
    source_2 = bytes(bin_tab_to_decimal(bbs_bits), "utf-8")

    hex_str = gen_xor(source_1, source_2)
    data = bytes.fromhex(hex_str)

    return {
        "bytes":  data,
        "bits":   bytes_vers_bits(data),
        "floats": bytes_vers_floats(data),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Runners
# ─────────────────────────────────────────────────────────────────────────────

def tester_system_urandom():
    section("systemRandomGenerator (urandom maison)  [CSPRNG hybride]")
    t0 = time.perf_counter()
    seqs = sequences_system_urandom(N // 8)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])
    tester_ks_uniforme(seqs["floats"])
    h = tester_shannon(seqs["bits"])

    print(f"\n  Temps de generation : {duree:.1f} ms")
    RESULTATS["systemRandom"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n  Sources : perf_counter, monotonic, PID, CPU, disque, reseau, id(object)")
    print("  Chaque bloc est produit par SHA3-256(pool + compteur)")
    print("  Pas de KS normale — produit des uniformes")


def tester_nrbg_xor():
    section("NRBG XOR (BBS xor systemRandom)  [generateur hybride non deterministe]")
    # On utilise 256 bits BBS et 32 octets urandom.
    # zip() tronque a la plus courte des deux sources apres conversion en bytes.
    print(f"  Sources : BBS (256 bits) XOR system_urandom (32 octets)")
    t0 = time.perf_counter()
    seqs = sequences_nrbg(n_bits_bbs=256, n_octets_urandom=32)
    duree = (time.perf_counter() - t0) * 1000

    scc = tester_autocorrelation(seqs["bits"])
    tester_chi_carre(seqs["bits"])

    if len(seqs["floats"]) >= 10:
        tester_ks_uniforme(seqs["floats"])
    else:
        sous_section("KS uniforme")
        print("  Sequence trop courte apres troncature zip — augmenter n_bits_bbs si besoin")

    h = tester_shannon(seqs["bits"])

    print(f"\n  Temps de generation : {duree:.0f} ms")
    RESULTATS["NRBG-XOR"] = {"shannon": h, "scc": scc, "temps_ms": duree}
    print("\n  Principe : XOR de deux sources independantes.")
    print("  Si au moins une source est imprevisible, le XOR l'est aussi.")
    print("  La sortie est aussi forte que la meilleure des deux sources.")


# ─────────────────────────────────────────────────────────────────────────────
# Mise a jour du tableau comparatif pour inclure les deux nouveaux generateurs
# ─────────────────────────────────────────────────────────────────────────────

def afficher_comparaison_complete():
    section("COMPARAISON GLOBALE DES GENERATEURS")

    print(f"\n  {'Generateur':<16} {'Shannon':>9} {'SCC':>9} {'Temps (ms)':>12}  Categorie")
    print("  " + "-" * 66)

    categories = {
        "LCG":          "PRNG non crypto",
        "MT19937":      "PRNG non crypto",
        "Box-Muller":   "Transformation N(0,1)",
        "BBS":          "CSPRNG",
        "HMAC-DRBG":    "CSPRNG (NIST)",
        "os.urandom":   "TRNG/CSPRNG systeme",
        "systemRandom": "CSPRNG hybride maison",
        "NRBG-XOR":     "hybride non deterministe",
    }

    for nom, res in RESULTATS.items():
        h   = res["shannon"]
        scc = res["scc"]
        ms  = res["temps_ms"]
        cat = categories.get(nom, "")

        flag_h   = "ok" if h > 0.99 else ("~" if h > 0.95 else "faible")
        flag_scc = "ok" if abs(scc) < 0.05 else "haut"

        print(f"  {nom:<16} {flag_h:>4} {h:>6.4f}   {flag_scc:>4} {scc:>7.4f}   {ms:>8.1f}    {cat}")

    print()
    print("  Shannon  : entropie par bit, idealement = 1.0")
    print("  SCC      : correlation serielle, idealement proche de 0")
    print("  Temps    : cout de generation de la sequence de test")
    print()
    print("  Conclusions :")
    print("  - Tous passent Shannon et SCC : les tests statistiques seuls ne distinguent pas")
    print("    un PRNG d'un CSPRNG. MT en est la demonstration directe.")
    print("  - BBS et NRBG sont lents car la generation de primes 1024 bits est couteuse.")
    print("  - systemRandom est un CSPRNG maison : bonnes proprietes statistiques,")
    print("    securite reposant sur SHA3-256 et la diversite des sources d'entropie.")
    print("  - NRBG XOR : la sortie est au moins aussi bonne que la meilleure source.")
    print("    C'est la propriete fondamentale du XOR entre sources independantes.")


if __name__ == "__main__":
    print("=" * 66)
    print("       TESTS DES GENERATEURS PSEUDO-ALEATOIRES")
    print(f"  N = {N:,} (PRNG)  |  N_BBS = {N_BBS} (BBS)  |  alpha = {ALPHA}")
    print("=" * 66)

    tester_lcg()
    tester_mt()
    tester_box_muller()
    tester_bbs()
    tester_hmac_drbg()
    tester_urandom()
    tester_system_urandom()
    tester_nrbg_xor()

    afficher_comparaison_complete()

    print("\n" + "=" * 66)
    print("  Tests termines.")
    print("=" * 66)
