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
