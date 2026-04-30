def _calculer_penalites(n, m, couts, lignes_actives, cols_actives):
    pen_lignes = []
    for i in range(n):
        if not lignes_actives[i]:
            pen_lignes.append(None)
            continue
        vals = sorted(couts[i][j] for j in range(m) if cols_actives[j])
        if len(vals) >= 2:
            pen_lignes.append(vals[1] - vals[0])
        elif len(vals) == 1:
            pen_lignes.append(vals[0])
        else:
            pen_lignes.append(None)

    pen_cols = []
    for j in range(m):
        if not cols_actives[j]:
            pen_cols.append(None)
            continue
        vals = sorted(couts[i][j] for i in range(n) if lignes_actives[i])
        if len(vals) >= 2:
            pen_cols.append(vals[1] - vals[0])
        elif len(vals) == 1:
            pen_cols.append(vals[0])
        else:
            pen_cols.append(None)

    return pen_lignes, pen_cols


#  AFFICHAGE DES PENALITES

def _afficher_penalites(n, m, pen_lignes, pen_cols,
                        lignes_actives, cols_actives,
                        prov_r, cmd_r):
    """
    Affiche les penalites courantes de toutes les lignes et colonnes actives.
    """
    print()
    print("  Penalites des lignes actives :")
    for i in range(n):
        if lignes_actives[i] and pen_lignes[i] is not None:
            print("    P" + str(i+1).ljust(3)
                  + "  provision=" + str(prov_r[i]).ljust(6)
                  + "  penalite = " + str(pen_lignes[i]))

    print("  Penalites des colonnes actives :")
    for j in range(m):
        if cols_actives[j] and pen_cols[j] is not None:
            print("    C" + str(j+1).ljust(3)
                  + "  commande= " + str(cmd_r[j]).ljust(6)
                  + "  penalite = " + str(pen_cols[j]))


# ==============================================================
#  ALGORITHME BALAS-HAMMER
# ==============================================================

def balas_hammer(n, m, couts, provisions, commandes):
    print()
    print("-" * 10)
    print("   ALGORITHME DE BALAS-HAMMER")
    print("-" * 10)

    prop           = [[0] * m for _ in range(n)]
    prov_r         = provisions[:]
    cmd_r          = commandes[:]
    lignes_actives = [True] * n
    cols_actives   = [True] * m
    etape          = 1

    while any(lignes_actives) and any(cols_actives):

        print()
        print("  --- Etape " + str(etape) + " " + "-" * 40)

        # 1. Calcul des penalites
        pen_lignes, pen_cols = _calculer_penalites(
            n, m, couts, lignes_actives, cols_actives)

        # 2. Affichage des penalites
        _afficher_penalites(n, m, pen_lignes, pen_cols,
                            lignes_actives, cols_actives,
                            prov_r, cmd_r)

        # 3. Penalite maximale
        max_pen = -1
        for i in range(n):
            if lignes_actives[i] and pen_lignes[i] is not None:
                if pen_lignes[i] > max_pen:
                    max_pen = pen_lignes[i]
        for j in range(m):
            if cols_actives[j] and pen_cols[j] is not None:
                if pen_cols[j] > max_pen:
                    max_pen = pen_cols[j]

        # 4. Lignes et colonnes a penalite maximale
        lignes_max = [i for i in range(n)
                      if lignes_actives[i] and pen_lignes[i] == max_pen]
        cols_max   = [j for j in range(m)
                      if cols_actives[j] and pen_cols[j] == max_pen]

        print()
        print("  Penalite maximale = " + str(max_pen))
        if lignes_max:
            print("  Ligne(s) a penalite maximale   : "
                  + "  ".join("P" + str(i+1) for i in lignes_max))
        if cols_max:
            print("  Colonne(s) a penalite maximale : "
                  + "  ".join("C" + str(j+1) for j in cols_max))

        # 5. Choisir la case de cout minimal parmi les candidats
        meilleur_cout = None
        best_i, best_j = -1, -1

        for i in lignes_max:
            for j in range(m):
                if cols_actives[j]:
                    if meilleur_cout is None or couts[i][j] < meilleur_cout:
                        meilleur_cout = couts[i][j]
                        best_i, best_j = i, j

        for j in cols_max:
            for i in range(n):
                if lignes_actives[i]:
                    if meilleur_cout is None or couts[i][j] < meilleur_cout:
                        meilleur_cout = couts[i][j]
                        best_i, best_j = i, j

        print("  --> Arete choisie : (P" + str(best_i+1) + ", C" + str(best_j+1) + ")"
              + "   cout unitaire = " + str(meilleur_cout))

        # 6. Affectation
        quantite = min(prov_r[best_i], cmd_r[best_j])
        prop[best_i][best_j] = quantite
        prov_r[best_i] -= quantite
        cmd_r[best_j]  -= quantite

        print("      Quantite affectee = " + str(quantite))
        print("      Provision restante P" + str(best_i+1) + " = " + str(prov_r[best_i])
              + "   Commande restante C" + str(best_j+1) + " = " + str(cmd_r[best_j]))

        # 7. Desactiver ligne ou colonne epuisee
        if prov_r[best_i] == 0 and cmd_r[best_j] == 0:
            lignes_actives[best_i] = False
            cols_actives[best_j]   = False
            nb_lignes_rest = sum(lignes_actives)
            nb_cols_rest   = sum(cols_actives)



        elif prov_r[best_i] == 0:
            lignes_actives[best_i] = False
            print("      P" + str(best_i+1) + " epuisee  ->  ligne desactivee")

        else:
            cols_actives[best_j] = False
            print("      C" + str(best_j+1) + " epuisee  ->  colonne desactivee")

        etape += 1

    print()
    print("  Proposition Balas-Hammer construite.")
    print()

    return prop
