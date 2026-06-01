import click
from typing import Optional

def SCC(suite, lag=1):
    """
    Fonction pour calculer le coefficient de corrélation sérielle.
    Possibilité de choisir le décalage

    Args:
        suite (list): Liste of bits [0,1,0,1,0]
        lag (int, optional):  Décalage entre les deux éléments comparés, Defaults to 1.

    Returns:
        float: Renvoie le coefficient de corrélation sérielle
    """
    sum_x, sum_x2, sum_product = 0, 0, 0
    n = len(suite)

    for i in range(n):
        x_courrant = suite[i]
        x_suivant = suite[(i + lag) % n]

        sum_x += x_courrant
        sum_x2 += x_courrant**2
        sum_product += x_courrant * x_suivant

    numerateur = n * sum_product - sum_x**2
    denominateur = n * sum_x2 - sum_x**2

    return numerateur / denominateur


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--suite",
    "suite_str",
    default=None,
    help="Suite de bits au format '[1,0,1,0]' ou '1,0,1,0'. Sinon lance les exemples prédéfinis.",
)
@click.option(
    "--lag",
    default=1,
    show_default=True,
    type=int,
    help="Décalage utilisé pour le SCC.",
)
def test(suite_str: Optional[str], lag: int):
    """
        Fonction qui permet aux autres membres du groupes de visualiser le test d'autocorrélation.
        Des plages d'interprétations sont mise vaguement à disposition pour comprendre le concept de ce test
        
        Auteur de la fonction test() : Yanis & Claude(IA) pour la mise en page du print afin d'avoir un affichage facile à lire et intuitif
        Prompt "Améliore la foncion de test afin d'avoir un affichage amélioré et interprétable en te basant sur la fonction de test déjà présente"
    """
    interpretations = [
        ("+1", "Bits consécutifs très similaires (forte autocorrélation positive)"),
        ("0 à +0.5", "Ressemblance modérée"),
        ("0", "Pas de pattern sériel détectable"),
        ("-0.5 à 0", "Légère alternance"),
        ("-1", "Bits alternent parfaitement (forte autocorrélation négative)"),
    ]
    
    # Affichage avec formatage
    print("┌─────────────┬──────────────────────────────────────────────────────┐")
    print("│ SCC         │ Interprétation                                       │")
    print("├─────────────┼──────────────────────────────────────────────────────┤")

    for scc_range, description in interpretations:
        print(f"│ {scc_range:<11} │ {description:<56} │")

    print("└─────────────┴──────────────────────────────────────────────────────┘")
    print("\n-----Test auto correlation-----\n")
    
    # Fonction d'interprétation
    def interpreter_scc(scc_value):
        if scc_value == 1.0:
            return "+1 -> Bits consécutifs très similaires (forte autocorrélation positive)"
        elif 0 < scc_value < 0.5:
            return f"{scc_value:.2f} -> Ressemblance modérée"
        elif 0 <= scc_value <= 0.01:
            return f"{scc_value:.2f} -> Pas de pattern sériel détectable"
        elif -0.5 < scc_value < 0:
            return f"{scc_value:.2f} -> Légère alternance"
        elif scc_value == -1.0:
            return "-1 -> Bits alternent parfaitement (forte autocorrélation négative)"
        else:
            return f"{scc_value:.2f} -> Hors plage standard"
    
    # Test des séries
    if suite_str:
        cleaned = suite_str.strip().strip("[]")
        serie = [int(x.strip()) for x in cleaned.split(",") if x.strip() != ""]
        series_test = [("Suite fournie", serie)]
    else:
        series_test = [
            ("Série 1", [1, 0, 1, 0, 1, 0, 1, 0]),
            ("Série 2", [1, 1, 0, 0, 1, 1, 0, 0]),
            ("Série 3", [1, 1, 1, 0, 0, 0, 1, 1]),
        ]
    
    for nom_serie, serie in series_test:
        scc_result = SCC(serie, lag=lag)
        print(f"{nom_serie}: {serie}")
        print(f"  SCC = {scc_result:.4f}")
        print(f"  Interprétation: {interpreter_scc(scc_result)}\n")

if __name__ == "__main__":
    test()
    click.echo("Test d'autocorrélation terminé.")