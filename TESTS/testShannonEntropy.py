from math import log2


def entropieShannon(X):
    """
    Auteurs : Arhiman Ludovic : Code & Claude : Correction grammaticale
    Prompt: "Corrige les fautes de français (orthographe, grammaire, etc ...) dans les docstrings, mais garde le sens tel que je les ai écrites"

    Implementation de l'entropie de Shannon avec une boucle qui va récupérer le nombre d'occurrence de l'élément
    définit comme la division de l'occurrence d'apparition de l'élément dans la liste sur la longueur de la liste
    puis multiplie p par le log base 2 de p et soustrait à l'entropie précédente à chaque itération de la boucle
    et quand la liste n'a plus d'éléments renvoie l'entropie
    """
    n = len(X)
    entropie = 0
    for val in set(X):
        p = X.count(val) / n
        if p > 0:
            entropie -= p * log2(p)
    return entropie


def test():
    """
    Auteurs : Arhiman Ludovic : Code & Claude : Correction grammaticale
    Prompt: "Corrige les fautes de français (orthographe, grammaire, etc ...) dans les docstrings, mais garde le sens tel que je les ai écrites"

    Permet de lancer des tests avec une série de valeur pour étudier l'entropie en fonction
    """

    INTERPRETATION = {
        "Série avec éléments de probabilité équiprobable" : "Entropie maximale : tous les symboles sont équiprobables, série parfaitement uniforme.",
        "Série avec éléments dupliqués, les éléments sont tous répétés en 2 fois" : "Entropie réduite : les doublons diminuent l'incertitude, la série est moins aléatoire.",
        "Serie avec les mêmes éléments" : "Entropie nulle : un seul symbole, aucune information, série totalement prévisible."
    }

    TEST = [1, 2, 3, 4, 5, 6, 7, 8]
    TEST2 = [1, 1, 2, 2, 3, 3, 4, 4]
    TEST3 = [1, 1, 1, 1, 1, 1, 1, 1]

    for (nom, interpretation), serie in zip(INTERPRETATION.items(), [TEST, TEST2, TEST3]):
        print(f"{nom}")
        print(f"  Entropie : {entropieShannon(serie):.4f} bits")
        print(f"  => {interpretation}\n")