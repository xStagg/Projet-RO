# -*- coding: utf-8 -*-
"""
=============================================================
  Fonctions de lecture et d'affichage - Probleme de Transport
  Efrei Paris - Recherche Operationnelle S6
=============================================================
"""

import sys
import os


# ==============================================================
#  1. LECTURE ET STOCKAGE EN MEMOIRE
# ==============================================================

def lire_probleme(chemin):
    """
    Lit un fichier .txt de probleme de transport.

    Format :
        n m
        a[1,1] ... a[1,m]  P1
        ...
        a[n,1] ... a[n,m]  Pn
        C1 C2 ... Cm

    Retourne : (n, m, couts, provisions, commandes)
    """
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


# ==============================================================
#  UTILITAIRES
# ==============================================================

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


# ==============================================================
#  CONSTRUCTION D'UN TABLEAU AVEC ESPACES UNIQUEMENT
#
#  Rendu vise :
#
#       C1     C2     C3    Provision
#  P1    30     20     20      450
#  P2    10     50     20      250
#  P3    50     40     30      250
#  P4    30     20     30      450
#       500    600    300
#
# ==============================================================

def _tableau(titre,
             lignes_donnees,
             entete_cols,
             entete_lignes,
             largeurs_cols,
             largeur_lbl,
             pied_ligne=None):
    """
    Affiche un tableau aligne avec espaces uniquement.

    Parametres :
      titre         -- chaine affichee en titre au-dessus
      lignes_donnees-- liste de listes de chaines (les cellules)
      entete_cols   -- liste de chaines pour l'en-tete des colonnes
      entete_lignes -- liste de chaines pour les etiquettes de ligne (P1, P2...)
      largeurs_cols -- liste de largeurs pour chaque colonne de donnees
      largeur_lbl   -- largeur de la colonne etiquette (Px / Commande)
      pied_ligne    -- liste de chaines pour la derniere ligne (commandes), ou None
    """
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


# ==============================================================
#  2a. MATRICE DES COUTS
# ==============================================================

def afficher_matrice_couts(n, m, couts, provisions, commandes):
    """
    Affiche la matrice des couts unitaires.

    Exemple :
                C1     C2     C3    Provision
    ----------------------------------------
    P1          30     20     20       450
    P2          10     50     20       250
    P3          50     40     30       250
    P4          30     20     30       450
    ----------------------------------------
    Commande   500    600    300
    """
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


# ==============================================================
#  2b. PROPOSITION DE TRANSPORT
# ==============================================================

def afficher_proposition(n, m, proposition, provisions, commandes,
                         titre="PROPOSITION DE TRANSPORT"):
    """
    Affiche la proposition de transport.

    case vide  (0)  ->  "."
    degeneree (-1)  ->  "(0)"
    normale         ->  valeur

    Exemple :
               C1     C2     C3    Provision
    -----------------------------------------
    P1        450      .      .       450
    P2         50    200      .       250
    P3          .    250      .       250
    P4          .    150    300       450
    -----------------------------------------
    Commande  500    600    300
    """
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


# ==============================================================
#  2c. TABLE DES COUTS POTENTIELS
# ==============================================================

def afficher_table_potentiels(n, m, couts, proposition, u, v):
    """
    Affiche la table des couts potentiels : u_i + v_j.

    Cases de base   ->  entre crochets  [val]
    Cases hors base ->  valeur simple

    Exemple :
                v1=30   v2=70   v3=80
    ------------------------------------
    u1=0          [30]     70      80
    u2=-20        [10]    [50]     60
    u3=-30          0     [40]     50
    u4=-50        -20     [20]    [30]

    Legende : [val] = case de base
    """
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


# ==============================================================
#  2d. TABLE DES COUTS MARGINAUX
# ==============================================================

def afficher_table_marginaux(n, m, couts, proposition, u, v):
    """
    Affiche la table des couts marginaux : delta_ij = a_ij - u_i - v_j.

    Cases de base           ->  [BASE]
    Meilleure arete         ->  >>val<<
    Autres cases hors base  ->  valeur

    Retourne la meilleure arete ameliorante (i, j) ou None si optimal.

    Exemple :
               C1       C2       C3
    ------------------------------------
    P1       [BASE]     -50    >>-60<<
    P2       [BASE]    [BASE]    -40
    P3         50      [BASE]    -20
    P4         50      [BASE]   [BASE]
    ------------------------------------
    Legende : [BASE] = case de base  |  >>val<< = meilleure arete
    --> Arete ameliorante : (P1, C3)   delta = -60
    """
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


# ==============================================================
#  CALCUL DU COUT TOTAL
# ==============================================================

def cout_total(n, m, couts, proposition):
    total = 0
    for i in range(n):
        for j in range(m):
            if proposition[i][j] > 0:
                total += couts[i][j] * proposition[i][j]
    return total


def afficher_cout_total(n, m, couts, proposition):
    ct = cout_total(n, m, couts, proposition)
    print("  Cout total de transport : " + str(ct))
    print()
    return ct


# ==============================================================
#  CALCUL DES POTENTIELS
# ==============================================================

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


# ==============================================================
#  PROPOSITION INITIALE NORD-OUEST
# ==============================================================

def nord_ouest(n, m, provisions, commandes):
    prop   = [[0] * m for _ in range(n)]
    prov_r = provisions[:]
    cmd_r  = commandes[:]
    ii, jj = 0, 0
    while ii < n and jj < m:
        q            = min(prov_r[ii], cmd_r[jj])
        prop[ii][jj] = q
        prov_r[ii]  -= q
        cmd_r[jj]   -= q
        if prov_r[ii] == 0 and cmd_r[jj] == 0:
            if ii + 1 < n and jj + 1 < m:
                prop[ii][jj + 1] = -1
            ii += 1
            jj += 1
        elif prov_r[ii] == 0:
            ii += 1
        else:
            jj += 1
    return prop


# ==============================================================
#  AFFICHAGE COMPLET D'UN PROBLEME
# ==============================================================

def afficher_tout(n, m, couts, provisions, commandes):
    """Affiche les 4 tableaux pour un probleme charge."""

    print()
    print("=" * 60)
    print("  Dimensions  : " + str(n) + " fournisseurs  x  " + str(m) + " clients")
    print("  Provisions  : " + str(provisions) + "   somme = " + str(sum(provisions)))
    print("  Commandes   : " + str(commandes)  + "   somme = " + str(sum(commandes)))
    print("=" * 60)

    # 1 - Matrice des couts
    afficher_matrice_couts(n, m, couts, provisions, commandes)

    # 2 - Proposition initiale Nord-Ouest
    prop = nord_ouest(n, m, provisions, commandes)
    afficher_proposition(n, m, prop, provisions, commandes,
                         "PROPOSITION INITIALE  (Nord-Ouest)")
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


# ==============================================================
#  MENU INTERACTIF
# ==============================================================

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
    "2": "Proposition de transport (Nord-Ouest)",
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

        # --- Choix du fichier ---
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

        # Chargement
        n, m, couts, provisions, commandes = lire_probleme(fichier)
        prop = nord_ouest(n, m, provisions, commandes)
        u, v = calculer_potentiels(n, m, couts, prop)

        print()
        print("  Fichier charge : " + fichier +
              "  (" + str(n) + " x " + str(m) + ")")

        # --- Choix de l'affichage ---
        print()
        print("  Que voulez-vous afficher ?")
        for k, label in AFFICHAGES.items():
            print("    " + k + "  ->  " + label)
        print("    0  ->  Changer de probleme")
        print()
        choix_aff = input("  Votre choix : ").strip()

        if choix_aff == "0":
            continue

        if choix_aff == "1":
            afficher_matrice_couts(n, m, couts, provisions, commandes)

        elif choix_aff == "2":
            afficher_proposition(n, m, prop, provisions, commandes,
                                 "PROPOSITION INITIALE  (Nord-Ouest)")
            afficher_cout_total(n, m, couts, prop)

        elif choix_aff == "3":
            afficher_table_potentiels(n, m, couts, prop, u, v)

        elif choix_aff == "4":
            afficher_table_marginaux(n, m, couts, prop, u, v)

        elif choix_aff == "5":
            afficher_tout(n, m, couts, provisions, commandes)

        else:
            print("  [!] Choix invalide.")

        # --- Continuer sur le meme probleme ? ---
        encore = input("  Afficher autre chose pour ce probleme ? (o/n) : ").strip().lower()
        if encore == "o":
            # reboucle sans rechoisir le fichier
            while encore == "o":
                print()
                print("  Que voulez-vous afficher ?")
                for k, label in AFFICHAGES.items():
                    print("    " + k + "  ->  " + label)
                print("    0  ->  Changer de probleme")
                print()
                choix_aff = input("  Votre choix : ").strip()

                if choix_aff == "0":
                    break
                elif choix_aff == "1":
                    afficher_matrice_couts(n, m, couts, provisions, commandes)
                elif choix_aff == "2":
                    afficher_proposition(n, m, prop, provisions, commandes,
                                         "PROPOSITION INITIALE  (Nord-Ouest)")
                    afficher_cout_total(n, m, couts, prop)
                elif choix_aff == "3":
                    afficher_table_potentiels(n, m, couts, prop, u, v)
                elif choix_aff == "4":
                    afficher_table_marginaux(n, m, couts, prop, u, v)
                elif choix_aff == "5":
                    afficher_tout(n, m, couts, provisions, commandes)
                else:
                    print("  [!] Choix invalide.")

                encore = input("  Afficher autre chose pour ce probleme ? (o/n) : ").strip().lower()


# ==============================================================
#  POINT D'ENTREE
# ==============================================================

if __name__ == "__main__":
    menu()