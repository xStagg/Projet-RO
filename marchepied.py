from collections import deque


def _est_case_de_base(val):

    return val > 0 or val == -1


def _construire_graphe(n, m, proposition):

    adj = [[] for _ in range(n + m)]
    for i in range(n):
        for j in range(m):
            if _est_case_de_base(proposition[i][j]):
                adj[i].append(n + j)
                adj[n + j].append(i)
    return adj


# test acyclicité (BFS)

def tester_acyclique(n, m, proposition):

    adj    = _construire_graphe(n, m, proposition)
    N      = n + m
    visite = [False] * N
    parent = [-1]    * N

    def _noeud_label(s):
        return "P" + str(s + 1) if s < n else "C" + str(s - n + 1)

    cycle_noeuds = None

    for depart in range(N):
        if visite[depart]:
            continue

        if not adj[depart]:
            continue

        file = deque([depart])
        visite[depart] = True

        while file and cycle_noeuds is None:
            u = file.popleft()
            for v in adj[u]:
                if not visite[v]:
                    visite[v] = True
                    parent[v] = u
                    file.append(v)
                elif v != parent[u]:

                    cycle_noeuds = _reconstruire_cycle(u, v, parent)
                    break

    if cycle_noeuds is None:
        return True, None


    print()
    print("  [CYCLE DETECTE]  La proposition N'EST PAS acyclique.")
    print("  Cycle : " + " -> ".join(_noeud_label(s) for s in cycle_noeuds)
          + " -> " + _noeud_label(cycle_noeuds[0]))
    print()
    return False, cycle_noeuds


def _reconstruire_cycle(u, v, parent):

    chemin_u, chemin_v = [], []
    cu, cv = u, v

    while cu != -1:
        chemin_u.append(cu)
        cu = parent[cu]
    while cv != -1:
        chemin_v.append(cv)
        cv = parent[cv]

    set_u = {s: k for k, s in enumerate(chemin_u)}
    ancetre = None
    for s in chemin_v:
        if s in set_u:
            ancetre = s
            break

    if ancetre is None:
        return chemin_u  # fallback

    idx_u = set_u[ancetre]
    idx_v = chemin_v.index(ancetre)

    cycle = chemin_u[:idx_u] + list(reversed(chemin_v[:idx_v + 1]))
    return cycle


# maximisation sur un cycle

def _cases_du_cycle_graphe(cycle_noeuds, n):

    cases = []
    for k in range(len(cycle_noeuds)):
        a = cycle_noeuds[k]
        b = cycle_noeuds[(k + 1) % len(cycle_noeuds)]
        if a < n and b >= n:
            cases.append((a, b - n))
        elif b < n and a >= n:
            cases.append((b, a - n))
    return cases


def maximiser_sur_cycle(n, m, proposition, cycle_noeuds):

    cases = _cases_du_cycle_graphe(cycle_noeuds, n)

    print("  Maximisation sur le cycle :")
    print("  Cases du cycle et leurs conditions :")

    cycle_signe = []
    for k, (i, j) in enumerate(cases):
        signe = +1 if k % 2 == 0 else -1
        cycle_signe.append(((i, j), signe))
        s = "+" if signe == 1 else "-"
        qte = proposition[i][j]
        if qte == -1:
            qte = 0
        print("    (P" + str(i + 1) + ", C" + str(j + 1) + ")  "
              + s + "  quantite=" + str(qte))
        
    delta = None
    for (i, j), signe in cycle_signe:
        if signe == -1:
            qte = proposition[i][j]
            if qte == -1:
                qte = 0
            if delta is None or qte < delta:
                delta = qte

    if delta is None:
        delta = 0

    print("  Delta = " + str(delta))

    nouvelle = [ligne[:] for ligne in proposition]
    sorties = []

    for (i, j), signe in cycle_signe:
        if signe == +1:
            v = nouvelle[i][j]
            if v == -1 or v == 0:
                nouvelle[i][j] = delta
            else:
                nouvelle[i][j] += delta
        else:
            v = nouvelle[i][j]
            if v == -1:
                v = 0
            v -= delta
            if v > 0:
                nouvelle[i][j] = v
            else:
                sorties.append((i, j))
                nouvelle[i][j] = 0

    if sorties:

        for idx, (i, j) in enumerate(sorties):
            if idx == 0:
                nouvelle[i][j] = 0
            else:
                nouvelle[i][j] = -1

        print("  Arete(s) supprimee(s) du cycle :")
        for i, j in sorties:
            print("    (P" + str(i + 1) + ", C" + str(j + 1) + ")")
    else:
        print("  Aucune arete supprimee (delta=0).")

    print()
    return nouvelle

# test connexité (BFS)

def tester_connexe(n, m, proposition):

    adj    = _construire_graphe(n, m, proposition)
    N      = n + m
    visite = [False] * N

    actifs = set()
    for i in range(n):
        for j in range(m):
            if _est_case_de_base(proposition[i][j]):
                actifs.add(i)
                actifs.add(n + j)

    composantes = []

    for depart in range(N):
        if visite[depart] or depart not in actifs:
            continue
        composante = []
        file = deque([depart])
        visite[depart] = True
        while file:
            u = file.popleft()
            composante.append(u)
            for v in adj[u]:
                if not visite[v]:
                    visite[v] = True
                    file.append(v)
        composantes.append(composante)

    def _label(s):
        return "P" + str(s + 1) if s < n else "C" + str(s - n + 1)

    if len(composantes) <= 1:
        return True, composantes

    print("  [NON CONNEXE]  La proposition est non connexe.")
    print("  Sous-graphes connexes :")
    for k, comp in enumerate(composantes):
        labels = [_label(s) for s in sorted(comp)]
        print("    Composante " + str(k + 1) + " : " + "  ".join(labels))
    print()

    return False, composantes


# correctino connexité 

def corriger_connexite(n, m, couts, proposition):

    nouvelle = [ligne[:] for ligne in proposition]
    iteration = 0

    while True:
        connexe, composantes = tester_connexe(n, m, nouvelle)
        if connexe:
            break

        iteration += 1
        print("  Correction connexite - passage " + str(iteration) + " :")

        comp_de = {}
        for k, comp in enumerate(composantes):
            for s in comp:
                comp_de[s] = k

        meilleur_cout = None
        best_i, best_j = -1, -1

        for i in range(n):
            for j in range(m):
                if _est_case_de_base(nouvelle[i][j]):
                    continue
                ci = comp_de.get(i, -1)
                cj = comp_de.get(n + j, -2)
                if ci != cj:
                    if meilleur_cout is None or couts[i][j] < meilleur_cout:
                        meilleur_cout = couts[i][j]
                        best_i, best_j = i, j

        if best_i == -1:
            print("  [!] Impossible de connecter les composantes.")
            break

        nouvelle[best_i][best_j] = -1
        print("    Arete ajoutee (base a zero) : (P" + str(best_i + 1)
              + ", C" + str(best_j + 1) + ")"
              + "   cout = " + str(couts[best_i][best_j]))
        print()

    return nouvelle

# calcul potentiels

def calculer_potentiels(n, m, couts, proposition):

    u = [None] * n
    v = [None] * m
    u[0] = 0

    modifie = True
    while modifie:
        modifie = False
        for i in range(n):
            for j in range(m):
                if _est_case_de_base(proposition[i][j]):
                    if u[i] is not None and v[j] is None:
                        v[j] = couts[i][j] - u[i]
                        modifie = True
                    elif v[j] is not None and u[i] is None:
                        u[i] = couts[i][j] - v[j]
                        modifie = True

    u = [x if x is not None else 0 for x in u]
    v = [x if x is not None else 0 for x in v]
    return u, v


def afficher_potentiels(n, m, u, v):
    print("  Potentiels u : "
          + "  ".join("u" + str(i + 1) + "=" + str(u[i]) for i in range(n)))
    print("  Potentiels v : "
          + "  ".join("v" + str(j + 1) + "=" + str(v[j]) for j in range(m)))
    print()


# table couts potentiels et marginaux

def _c(texte, w):
    return str(texte).center(w)


def _col_width(val_max, extra=2, minimum=6):
    return max(len(str(val_max)) + extra, minimum)


def afficher_table_potentiels(n, m, couts, proposition, u, v):

    table = [[u[i] + v[j] for j in range(m)] for i in range(n)]
    val_max = max(abs(table[i][j]) for i in range(n) for j in range(m))

    lbl_u_max = max(len("u" + str(i + 1) + "=" + str(u[i])) for i in range(n))
    lbl_v_max = max(len("v" + str(j + 1) + "=" + str(v[j])) for j in range(m))

    w = max(_col_width(val_max, extra=2, minimum=6),
            lbl_v_max + 2,
            len("[" + str(val_max) + "]") + 2,
            8)
    w_lbl = max(lbl_u_max + 2, 10)

    entete_cols   = ["v" + str(j + 1) + "=" + str(v[j]) for j in range(m)]
    entete_lignes = ["u" + str(i + 1) + "=" + str(u[i]) for i in range(n)]
    largeurs      = [w] * m

    total = w_lbl + sum(largeurs)
    titre = "TABLE DES COUTS POTENTIELS  ( u_i + v_j )"
    print()
    print(_c(titre, total))
    print("-" * total)

    ligne_h = " " * w_lbl
    for val, wc in zip(entete_cols, largeurs):
        ligne_h += _c(val, wc)
    print(ligne_h)
    print("-" * total)

    for i in range(n):
        ligne = _c(entete_lignes[i], w_lbl)
        for j in range(m):
            pot     = u[i] + v[j]
            en_base = _est_case_de_base(proposition[i][j])
            ligne  += _c("[" + str(pot) + "]" if en_base else str(pot), w)
        print(ligne)

    print()
    print("  Legende : [val] = case de base")
    print()


def afficher_table_marginaux(n, m, couts, proposition, u, v):

    marginaux = []
    meilleur  = None
    val_min   = 0

    for i in range(n):
        row = []
        for j in range(m):
            en_base = _est_case_de_base(proposition[i][j])
            if en_base:
                row.append(None)
            else:
                delta = couts[i][j] - u[i] - v[j]
                row.append(delta)
                if delta < val_min:
                    val_min  = delta
                    meilleur = (i, j)
        marginaux.append(row)

    vals_num = [x for row in marginaux for x in row if x is not None]
    val_max  = max(abs(x) for x in vals_num) if vals_num else 0
    marqueur = ">>" + str(val_min) + "<<"

    w = max(_col_width(val_max, extra=2, minimum=6),
            len("[BASE]") + 2,
            len(marqueur) + 2,
            8)
    w_lbl = max(len("Commande") + 2, 10)

    entete_cols   = ["C" + str(j + 1) for j in range(m)]
    entete_lignes = ["P" + str(i + 1) for i in range(n)]
    largeurs      = [w] * m

    total = w_lbl + sum(largeurs)
    titre = "TABLE DES COUTS MARGINAUX  ( a_ij - u_i - v_j )"
    print()
    print(_c(titre, total))
    print("-" * total)

    ligne_h = " " * w_lbl
    for val, wc in zip(entete_cols, largeurs):
        ligne_h += _c(val, wc)
    print(ligne_h)
    print("-" * total)

    for i in range(n):
        ligne = _c(entete_lignes[i], w_lbl)
        for j in range(m):
            if marginaux[i][j] is None:
                ligne += _c("[BASE]", w)
            elif meilleur and (i, j) == meilleur:
                ligne += _c(">>" + str(marginaux[i][j]) + "<<", w)
            else:
                ligne += _c(str(marginaux[i][j]), w)
        print(ligne)

    print()
    print("  Legende : [BASE] = case de base  |  >>val<< = meilleure arete ameliorante")
    print()

    if meilleur:
        i, j = meilleur
        print("  --> Arete ameliorante : (P" + str(i + 1) + ", C" + str(j + 1)
              + ")   cout marginal = " + str(val_min))
    else:
        print("  OK : Aucun cout marginal negatif  -->  solution OPTIMALE.")
    print()

    return meilleur


# ajout arete ameliorante

def _trouver_cycle_ameliorant(n, m, proposition, i_entree, j_entree):
   
    adj     = _construire_graphe(n, m, proposition)
    depart  = i_entree
    arrivee = n + j_entree

    parent = [-1] * (n + m)
    parent[depart] = depart
    file = deque([depart])

    while file and parent[arrivee] == -1:
        u = file.popleft()
        for vv in adj[u]:
            if parent[vv] == -1:
                parent[vv] = u
                file.append(vv)

    if parent[arrivee] == -1:
        return None

    noeuds = []
    cur = arrivee
    while cur != depart:
        noeuds.append(cur)
        cur = parent[cur]
    noeuds.append(depart)
    noeuds.reverse()

    chemin_cases = []
    for k in range(len(noeuds) - 1):
        a, b = noeuds[k], noeuds[k + 1]
        if a < n and b >= n:
            chemin_cases.append((a, b - n))
        elif b < n and a >= n:
            chemin_cases.append((b, a - n))
        else:
            return None

    cycle = [((i_entree, j_entree), +1)]
    signe = -1
    for i, j in reversed(chemin_cases):
        cycle.append(((i, j), signe))
        signe *= -1

    return cycle


def ajouter_arete_ameliorante(n, m, couts, proposition, meilleur):

    i_e, j_e = meilleur
    print("  Ajout de l'arete ameliorante : (P" + str(i_e + 1)
          + ", C" + str(j_e + 1) + ")")

    cycle = _trouver_cycle_ameliorant(n, m, proposition, i_e, j_e)

    if cycle is None:
        print("  [!] Impossible de trouver le cycle pour cette arete.")
        return proposition

    print("  Cycle forme :")
    for (i, j), signe in cycle:
        s = "+" if signe == 1 else "-"
        print("    (P" + str(i + 1) + ", C" + str(j + 1) + ")  " + s
              + "  quantite=" + str(max(0, proposition[i][j])))

    # delta
    delta = None
    for (i, j), signe in cycle:
        if signe == -1:
            qte = proposition[i][j]
            if qte == -1:
                qte = 0
            if delta is None or qte < delta:
                delta = qte

    if delta is None:
        delta = 0

    print("  Delta = " + str(delta))

    # pivot
    nouvelle = [ligne[:] for ligne in proposition]
    sorties  = []

    for (i, j), signe in cycle:
        if signe == +1:
            v = nouvelle[i][j]
            nouvelle[i][j] = delta if (v <= 0) else v + delta
        else:
            v = nouvelle[i][j]
            if v == -1:
                v = 0
            v -= delta
            if v > 0:
                nouvelle[i][j] = v
            else:
                sorties.append((i, j))
                nouvelle[i][j] = 0

    if sorties:
        print("  Arete(s) sortante(s) :")
        for i, j in sorties:
            print("    (P" + str(i + 1) + ", C" + str(j + 1) + ")  -> sortie de la base")
    else:
        print("  Delta nul : aucune modification apportee.")

    print()
    return nouvelle


# une itération complète du marche-pied 

def iteration_marchepied(n, m, couts, proposition,
                         afficher_prop_fn, afficher_cout_fn):
    prop = [ligne[:] for ligne in proposition]

    # 1 : acyclicite
    print("  [1] Test d'acyclicite :")
    acyclique, cycle_noeuds = tester_acyclique(n, m, prop)
    while not acyclique:
        prop = maximiser_sur_cycle(n, m, prop, cycle_noeuds)
        afficher_prop_fn(prop, "PROPOSITION (apres suppression du cycle)")
        afficher_cout_fn(prop)
        acyclique, cycle_noeuds = tester_acyclique(n, m, prop)

    print("  La proposition est acyclique.")
    print()

    # 2 : connexite
    print("  [2] Test de connexite :")
    connexe, _ = tester_connexe(n, m, prop)
    if not connexe:
        prop = corriger_connexite(n, m, couts, prop)
        afficher_prop_fn(prop, "PROPOSITION (apres correction connexite)")
        afficher_cout_fn(prop)
    else:
        print("  La proposition est connexe.")
    print()

    # 3 : potentiels
    print("  [3] Calcul des potentiels :")
    u, v = calculer_potentiels(n, m, couts, prop)
    afficher_potentiels(n, m, u, v)

    # 4 : tables
    print("  [4] Table des couts potentiels :")
    afficher_table_potentiels(n, m, couts, prop, u, v)

    print("  [5] Table des couts marginaux :")
    meilleur = afficher_table_marginaux(n, m, couts, prop, u, v)

    # 5 : ajout arete ameliorante
    if meilleur is None:
        return prop, True   # solution optimale

    print("  [6] Ajout de l'arete ameliorante :")
    prop = ajouter_arete_ameliorante(n, m, couts, prop, meilleur)
    return prop, False


# boucle principale du marchepied

def marche_pied_complet(n, m, couts, provisions, commandes, proposition,
                        afficher_prop_fn, afficher_cout_fn):
    
    prop      = [ligne[:] for ligne in proposition]
    iteration = 1

    print()
    print("=" * 60)
    print("  METHODE DU MARCHE-PIED AVEC POTENTIEL")
    print("=" * 60)

    while True:
        print()
        print("  " + "=" * 56)
        print("  ITERATION " + str(iteration))
        print("  " + "=" * 56)

        afficher_prop_fn(prop, "PROPOSITION COURANTE  (iteration " + str(iteration) + ")")
        afficher_cout_fn(prop)

        prop, optimal = iteration_marchepied(
            n, m, couts, prop,
            afficher_prop_fn,
            afficher_cout_fn
        )

        if optimal:
            print()
            print("  --> Solution OPTIMALE atteinte a l'iteration " + str(iteration))
            break

        iteration += 1

    print()
    print("=" * 60)
    print("  PROPOSITION OPTIMALE FINALE")
    print("=" * 60)
    afficher_prop_fn(prop, "PROPOSITION OPTIMALE")
    afficher_cout_fn(prop)

    return prop