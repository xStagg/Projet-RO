def nord_ouest(n, m, couts, provisions, commandes):

    print()
    print("-" * 10)
    print("Algorithme Nord-Ouest")
    print("-" * 10)

    prop   = [[0] * m for _ in range(n)]
    prov_r = provisions[:]
    cmd_r  = commandes[:]

    i, j = 0, 0

    while i < n and j < m:

        quantite = min(prov_r[i], cmd_r[j])
        prop[i][j] = quantite
        prov_r[i] -= quantite
        cmd_r[j]  -= quantite

        print()
        print("  Etape (" + str(i+1) + "," + str(j+1) + ")"
              + "  ->  affectation (P" + str(i+1) + ", C" + str(j+1) + ") = " + str(quantite))
        print("         Provision restante P" + str(i+1) + " = " + str(prov_r[i])
              + "   Commande restante C" + str(j+1) + " = " + str(cmd_r[j]))

        if prov_r[i] == 0 and cmd_r[j] == 0:
            # Degenerescence : les deux s'epuisent en meme temps
            if i + 1 < n and j + 1 < m:

                # Deux cases candidates possibles :
                # - la case a droite : (i, j+1)
                # - la case en bas   : (i+1, j)

                cout_droite = couts[i][j + 1]
                cout_bas = couts[i + 1][j]

                if cout_droite <= cout_bas:
                    prop[i][j + 1] = -1
                    print("  [!] Degenerescence : case (P" + str(i + 1) + ", C" + str(j + 2)
                          + ") ajoutee comme base a zero car son cout est le plus faible")
                else:
                    prop[i + 1][j] = -1
                    print("  [!] Degenerescence : case (P" + str(i + 2) + ", C" + str(j + 1)
                          + ") ajoutee comme base a zero car son cout est le plus faible")
            i += 1
            j += 1

        elif prov_r[i] == 0:
            print("         Provision P" + str(i+1) + " epuisee  ->  on descend a P" + str(i+2))
            i += 1

        else:
            print("         Commande C" + str(j+1) + " epuisee  ->  on avance a C" + str(j+2))
            j += 1

    print()
    print("  Proposition Nord-Ouest construite.")
    print()

    return prop


if __name__ == "__main__":

    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    from affichage import (lire_probleme, afficher_matrice_couts,
                           afficher_proposition, afficher_cout_total)

    FICHIERS = {str(k): "pb" + str(k) + ".txt" for k in range(1, 13)}

    print()
    print("-" * 10)
    print(" test Algorithme Nord-Ouest")
    print("-" * 10)
    print()
    print("  Problemes disponibles :")
    for k in range(1, 13):
        print("    " + str(k).rjust(2) + "  ->  pb" + str(k) + ".txt")
    print()

    choix = input("  Choisissez un probleme (1-12) : ").strip()
    if choix not in FICHIERS:
        print("  Choix invalide.")
    else:
        fichier = FICHIERS[choix]
        if not os.path.isfile(fichier):
            print("  Fichier '" + fichier + "' introuvable.")
        else:
            n, m, couts, provisions, commandes = lire_probleme(fichier)
            afficher_matrice_couts(n, m, couts, provisions, commandes)

            prop = nord_ouest(n, m, provisions, commandes)

            afficher_proposition(n, m, prop, provisions, commandes,
                                 "proposition initial  (Nord-Ouest)")
            afficher_cout_total(n, m, couts, prop)