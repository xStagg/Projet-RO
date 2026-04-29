
import sys
import os
from nordouest   import nord_ouest
from balashammer import balas_hammer

#  1. LECTURE ET STOCKAGE EN MEMOIRE


def lire_probleme(chemin):

    if not os.path.isfile(chemin):
        print("[ERREUR] Fichier introuvable : " + chemin)
        sys.exit(1)

    with open(chemin, 'r') as f:
        lignes = [l.strip() for l in f if l.strip()]

    n, m = int(lignes[0].split()[0]), int(lignes[0].split()[1])

    couts, provisions = [], []
    for i in range(1, n + 1):
        valeurs = list(map(int, lignes[i].split()))
        couts.append(valeurs[:m])
        provisions.append(valeurs[m])

    commandes = list(map(int, lignes[n + 1].split()))

    if sum(provisions) != sum(commandes):
        print("[AVERTISSEMENT] Probleme non equilibre : "
              "somme(P)=" + str(sum(provisions)) +
              "  somme(C)=" + str(sum(commandes)))

    return n, m, couts, provisions, commandes




def _col_width(valeurs_max, extra=2, minimum=6):
    """Largeur de colonne selon la valeur maximale a afficher."""
    return max(len(str(valeurs_max)) + extra, minimum)


def _c(texte, w):
    """Centre un texte dans une largeur w."""
    return str(texte).center(w)


def _max_abs(liste_2d):
    """Valeur absolue maximale dans une liste 2D (ignore None)."""
    m = 0
    for row in liste_2d:
        for v in row:
            if v is not None:
                m = max(m, abs(int(v)))
    return m


def _tableau(titre,
             lignes_donnees,
             entete_cols,
             entete_lignes,
             largeurs_cols,
             largeur_lbl,
             pied_ligne=None):

    # Ligne de titre
    total = largeur_lbl + sum(largeurs_cols)
    print()
    print(_c(titre, total))
    print("-" * total)

    # En-tete des colonnes
    ligne_h = " " * largeur_lbl
    for val, w in zip(entete_cols, largeurs_cols):
        ligne_h += _c(val, w)
    print(ligne_h)
    print("-" * total)

    # Lignes de donnees
    for lbl, row in zip(entete_lignes, lignes_donnees):
        ligne = _c(lbl, largeur_lbl)
        for val, w in zip(row, largeurs_cols):
            ligne += _c(val, w)
        print(ligne)

    # Pied de tableau (commandes)
    if pied_ligne is not None:
        print("-" * total)
        ligne_p = " " * largeur_lbl
        for val, w in zip(pied_ligne, largeurs_cols):
            ligne_p += _c(val, w)
        print(ligne_p)

    print()


#  2a. MATRICE DES COUTS


def afficher_matrice_couts(n, m, couts, provisions, commandes):

    val_max  = _max_abs(couts + [provisions] + [commandes])
    w        = _col_width(val_max, extra=2, minimum=6)
    w_prov   = max(w, len("Provision") + 2)
    w_lbl    = max(len("Commande") + 2, 10)

    largeurs = [w] * m + [w_prov]

    entete_cols   = ["C" + str(j+1) for j in range(m)] + ["Provision"]
    entete_lignes = ["P" + str(i+1) for i in range(n)]
    donnees       = [
        [str(couts[i][j]) for j in range(m)] + [str(provisions[i])]
        for i in range(n)
    ]
    pied = [str(commandes[j]) for j in range(m)] + [""]

    _tableau(
        titre          = "MATRICE DES COUTS",
        lignes_donnees = donnees,
        entete_cols    = entete_cols,
        entete_lignes  = entete_lignes,
        largeurs_cols  = largeurs,
        largeur_lbl    = w_lbl,
        pied_ligne     = pied
    )

#  2b. PROPOSITION DE TRANSPORT


def afficher_proposition(n, m, proposition, provisions, commandes,
                         titre="PROPOSITION DE TRANSPORT"):

    affichage = []
    for i in range(n):
        row = []
        for j in range(m):
            v = proposition[i][j]
            if v == -1:
                row.append("(0)")
            elif v == 0:
                row.append(".")
            else:
                row.append(str(v))
        affichage.append(row)

    vals_pos = [proposition[i][j]
                for i in range(n) for j in range(m)
                if proposition[i][j] > 0]
    val_max  = max(vals_pos) if vals_pos else 0
    val_max  = max(val_max, max(provisions), max(commandes))

    w      = _col_width(val_max, extra=2, minimum=6)
    w      = max(w, len("(0)") + 2)
    w_prov = max(w, len("Provision") + 2)
    w_lbl  = max(len("Commande") + 2, 10)

    largeurs = [w] * m + [w_prov]

    entete_cols   = ["C" + str(j+1) for j in range(m)] + ["Provision"]
    entete_lignes = ["P" + str(i+1) for i in range(n)]
    donnees       = [affichage[i] + [str(provisions[i])] for i in range(n)]
    pied          = [str(commandes[j]) for j in range(m)] + [""]

    _tableau(
        titre          = titre,
        lignes_donnees = donnees,
        entete_cols    = entete_cols,
        entete_lignes  = entete_lignes,
        largeurs_cols  = largeurs,
        largeur_lbl    = w_lbl,
        pied_ligne     = pied
    )



#  2c. TABLE DES COUTS POTENTIELS


def afficher_table_potentiels(n, m, couts, proposition, u, v):

    table = [[u[i] + v[j] for j in range(m)] for i in range(n)]

    val_max   = _max_abs(table)
    lbl_u_max = max(len("u" + str(i+1) + "=" + str(u[i])) for i in range(n))
    lbl_v_max = max(len("v" + str(j+1) + "=" + str(v[j])) for j in range(m))

    w_crochet = len("[" + str(val_max) + "]") + 2
    w         = max(_col_width(val_max, extra=2, minimum=6),
                    lbl_v_max + 2,
                    w_crochet,
                    8)
    w_lbl     = max(lbl_u_max + 2, 10)

    largeurs      = [w] * m
    entete_cols   = ["v" + str(j+1) + "=" + str(v[j]) for j in range(m)]
    entete_lignes = ["u" + str(i+1) + "=" + str(u[i]) for i in range(n)]

    donnees = []
    for i in range(n):
        row = []
        for j in range(m):
            pot     = u[i] + v[j]
            en_base = (proposition[i][j] > 0 or proposition[i][j] == -1)
            row.append("[" + str(pot) + "]" if en_base else str(pot))
        donnees.append(row)

    _tableau(
        titre          = "TABLE DES COUTS POTENTIELS  ( u_i + v_j )",
        lignes_donnees = donnees,
        entete_cols    = entete_cols,
        entete_lignes  = entete_lignes,
        largeurs_cols  = largeurs,
        largeur_lbl    = w_lbl,
        pied_ligne     = None
    )
    print("  Legende : [val] = case de base")
    print()



#  2d. TABLE DES COUTS MARGINAUX


def afficher_table_marginaux(n, m, couts, proposition, u, v):

    marginaux = []
    meilleur  = None
    val_min   = 0

    for i in range(n):
        row = []
        for j in range(m):
            en_base = (proposition[i][j] > 0 or proposition[i][j] == -1)
            if en_base:
                row.append(None)
            else:
                delta = couts[i][j] - u[i] - v[j]
                row.append(delta)
                if delta < val_min:
                    val_min  = delta
                    meilleur = (i, j)
        marginaux.append(row)

    vals_num = [v2 for row in marginaux for v2 in row if v2 is not None]
    val_max  = max(abs(v2) for v2 in vals_num) if vals_num else 0
    marqueur = ">>" + str(val_min) + "<<"

    w     = max(_col_width(val_max, extra=2, minimum=6),
                len("[BASE]") + 2,
                len(marqueur) + 2,
                8)
    w_lbl = max(len("Commande") + 2, 10)

    largeurs      = [w] * m
    entete_cols   = ["C" + str(j+1) for j in range(m)]
    entete_lignes = ["P" + str(i+1) for i in range(n)]

    donnees = []
    for i in range(n):
        row = []
        for j in range(m):
            if marginaux[i][j] is None:
                row.append("[BASE]")
            elif meilleur and (i, j) == meilleur:
                row.append(">>" + str(marginaux[i][j]) + "<<")
            else:
                row.append(str(marginaux[i][j]))
        donnees.append(row)

    _tableau(
        titre          = "TABLE DES COUTS MARGINAUX  ( a_ij - u_i - v_j )",
        lignes_donnees = donnees,
        entete_cols    = entete_cols,
        entete_lignes  = entete_lignes,
        largeurs_cols  = largeurs,
        largeur_lbl    = w_lbl,
        pied_ligne     = None
    )

    print("  Legende : [BASE] = case de base  |  >>val<< = meilleure arete ameliorante")
    print()
    if meilleur:
        i, j = meilleur
        print("  --> Arete ameliorante : (P" + str(i+1) + ", C" + str(j+1)
              + ")   delta = " + str(val_min))
    else:
        print("  OK : Aucun cout marginal negatif  -->  solution OPTIMALE.")
    print()

    return meilleur



#  5. CALCUL DU COUT TOTAL


def cout_total(n, m, couts, proposition):

    Z = 0
    for i in range(n):
        for j in range(m):
            if proposition[i][j] > 0:
                Z += couts[i][j] * proposition[i][j]
    return Z


def afficher_cout_total(n, m, couts, proposition):

    print()
    print("  CALCUL DU COUT TOTAL")
    print("  " + "-" * 44)

    Z = 0
    for i in range(n):
        for j in range(m):
            if proposition[i][j] > 0:
                contrib  = couts[i][j] * proposition[i][j]
                Z       += contrib
                print("  (P" + str(i+1) + ", C" + str(j+1) + ")"
                      + "   :   cout=" + str(couts[i][j]).rjust(4)
                      + "  x  qte=" + str(proposition[i][j]).rjust(5)
                      + "   =  " + str(contrib).rjust(7))

    print("  " + "-" * 44)
    print("  Cout total   Z  =  " + str(Z))
    print()
    return Z



#  CALCUL DES POTENTIELS


def calculer_potentiels(n, m, couts, proposition):
    u = [None] * n
    v = [None] * m
    u[0] = 0
    modifie = True
    while modifie:
        modifie = False
        for i in range(n):
            for j in range(m):
                en_base = (proposition[i][j] > 0 or proposition[i][j] == -1)
                if en_base:
                    if u[i] is not None and v[j] is None:
                        v[j] = couts[i][j] - u[i]
                        modifie = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = couts[i][j] - v[j]
                        modifie = True
    u = [x if x is not None else 0 for x in u]
    v = [x if x is not None else 0 for x in v]
    return u, v

#  AFFICHAGE COMPLET D'UN PROBLEME


def afficher_tout(n, m, couts, provisions, commandes, prop, titre_prop):
    """Affiche les 4 tableaux pour un probleme charge."""

    print()
    print("=" * 60)
    print("  Dimensions  : " + str(n) + " fournisseurs  x  " + str(m) + " clients")
    print("  Provisions  : " + str(provisions) + "   somme = " + str(sum(provisions)))
    print("  Commandes   : " + str(commandes)  + "   somme = " + str(sum(commandes)))
    print("=" * 60)

    # 1 - Matrice des couts
    afficher_matrice_couts(n, m, couts, provisions, commandes)

    # 2 - Proposition initiale
    afficher_proposition(n, m, prop, provisions, commandes, titre_prop)
    afficher_cout_total(n, m, couts, prop)

    # 3 - Potentiels
    u, v = calculer_potentiels(n, m, couts, prop)
    print("  Potentiels u : " + "  ".join("u"+str(i+1)+"="+str(u[i]) for i in range(n)))
    print("  Potentiels v : " + "  ".join("v"+str(j+1)+"="+str(v[j]) for j in range(m)))
    print()

    # 4 - Table des couts potentiels
    afficher_table_potentiels(n, m, couts, prop, u, v)

    # 5 - Table des couts marginaux
    afficher_table_marginaux(n, m, couts, prop, u, v)

#  MENU

FICHIERS = {
    "1":  "pb1.txt",
    "2":  "pb2.txt",
    "3":  "pb3.txt",
    "4":  "pb4.txt",
    "5":  "pb5.txt",
    "6":  "pb6.txt",
    "7":  "pb7.txt",
    "8":  "pb8.txt",
    "9":  "pb9.txt",
    "10": "pb10.txt",
    "11": "pb11.txt",
    "12": "pb12.txt",
}

AFFICHAGES = {
    "1": "Matrice des couts",
    "2": "Proposition de transport + cout total",
    "3": "Table des couts potentiels",
    "4": "Table des couts marginaux",
    "5": "Tout afficher",
}


def menu():
    print()
    print("=" * 50)
    print("   PROBLEME DE TRANSPORT  -  Efrei Paris S6")
    print("=" * 50)

    while True:

        # --- Choix du probleme ---
        print()
        print("  Problemes disponibles :")
        for k, f in sorted(FICHIERS.items(), key=lambda x: int(x[0])):
            print("    " + k.rjust(2) + "  ->  " + f)
        print("     0  ->  Quitter")
        print()

        choix_pb = input("  Choisissez un probleme (0-12) : ").strip()

        if choix_pb == "0":
            print()
            print("  Au revoir !")
            print()
            break

        if choix_pb not in FICHIERS:
            print("  [!] Choix invalide, reessayez.")
            continue

        fichier = FICHIERS[choix_pb]
        if not os.path.isfile(fichier):
            print("  [!] Fichier '" + fichier + "' introuvable dans le dossier courant.")
            continue

        # --- Lecture et stockage ---
        n, m, couts, provisions, commandes = lire_probleme(fichier)

        print()
        print("  Fichier charge : " + fichier +
              "  (" + str(n) + " x " + str(m) + ")")

        # --- Choix de l'algorithme pour la proposition initiale ---
        print()
        print("  Choisissez l'algorithme pour fixer la proposition initiale :")
        print("    1  ->  Nord-Ouest")
        print("    2  ->  Balas-Hammer")
        print("    0  ->  Changer de probleme")
        print()

        choix_alg = input("  Votre choix : ").strip()

        if choix_alg == "0":
            continue

        if choix_alg == "1":
            prop = nord_ouest(n, m, provisions, commandes)
            titre_prop = "PROPOSITION INITIALE  (Nord-Ouest)"
        elif choix_alg == "2":
            prop = balas_hammer(n, m, couts, provisions, commandes)
            titre_prop = "PROPOSITION INITIALE  (Balas-Hammer)"
        else:
            print("  [!] Choix invalide.")
            continue

        # Calcul des potentiels sur la proposition obtenue
        u, v = calculer_potentiels(n, m, couts, prop)

        # --- Affichage des elements de base ---
        print()
        print("  Elements disponibles pour ce probleme :")
        print("    1  ->  Matrice des couts")
        print("    2  ->  Proposition de transport + cout total")
        print("    3  ->  Table des couts potentiels")
        print("    4  ->  Table des couts marginaux")
        print("    5  ->  Tout afficher")
        print("    0  ->  Changer de probleme")
        print()

        while True:
            choix_aff = input("  Votre choix : ").strip()

            if choix_aff == "0":
                break

            elif choix_aff == "1":
                afficher_matrice_couts(n, m, couts, provisions, commandes)

            elif choix_aff == "2":
                afficher_proposition(n, m, prop, provisions, commandes, titre_prop)
                afficher_cout_total(n, m, couts, prop)

            elif choix_aff == "3":
                afficher_table_potentiels(n, m, couts, prop, u, v)

            elif choix_aff == "4":
                afficher_table_marginaux(n, m, couts, prop, u, v)

            elif choix_aff == "5":
                afficher_matrice_couts(n, m, couts, provisions, commandes)
                afficher_proposition(n, m, prop, provisions, commandes, titre_prop)
                afficher_cout_total(n, m, couts, prop)
                afficher_table_potentiels(n, m, couts, prop, u, v)
                afficher_table_marginaux(n, m, couts, prop, u, v)

            else:
                print("  [!] Choix invalide.")

            print()
            rep = input("  Voulez-vous afficher autre chose pour ce probleme ? (o/n) : ").strip().lower()
            if rep != "o":
                break

        # --- Changer de probleme ou quitter ---
        print()
        rep_global = input("  Voulez-vous tester un autre probleme ? (o/n) : ").strip().lower()
        if rep_global != "o":
            print()
            print("  Au revoir !")
            print()
            break
if __name__ == "__main__":
    menu()