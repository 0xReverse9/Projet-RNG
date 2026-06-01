# Projet RNG

Projet d'étude et d'implémentation de générateurs de nombres pseudo-aléatoires (PRNG), incluant des tests statistiques et des attaques cryptographiques associées.

## Générateurs

```bash
python GENERATORS/LCG.py              # Linear Congruential Generator
python GENERATORS/mt.py               # Mersenne Twister
python GENERATORS/bbs_generator.py    # Blum Blum Shub
python GENERATORS/hmac_drbg.py        # HMAC-DRBG (NIST SP 800-90A)
python GENERATORS/box_muller.py       # Box-Muller (distribution normale)
python GENERATORS/nrbgXorGenerator.py # XOR-based NRBG
python GENERATORS/systemRandomGenerator.py # Générateur système
```

## Tests statistiques

```bash
python TESTS/testChiCarre.py          # Test du Chi²
python TESTS/testKS.py                # Test de Kolmogorov-Smirnov
python TESTS/testShannonEntropy.py    # Test d'entropie de Shannon
python TESTS/testAutoCorrelation.py   # Test d'autocorrélation
```

## Attaques

```bash
python ATTACKS/MT.py                  # Attaque sur Mersenne Twister
python ATTACKS/LCG_SEEDKEEPER.py      # Récupération de graine LCG
python ATTACKS/AES-CTR-NONCE/exploit.py  # Exploit AES-CTR (réutilisation de nonce)
```
