import numpy as np
import time
from nordouest import nord_ouest
from balashammer import balas_hammer
from marchepied import marche_pied_complet
from main import lire_probleme
import matplotlib.pyplot as plt

# ============================================================================
# PARAMÈTRES
# ============================================================================
N_VALUES = [10, 40]
NB_ITERATIONS = 100  # 100 réalisations par taille n

# ============================================================================
# FONCTIONS DE MESURE
# ============================================================================

def generer_probleme_aleatoire(n):
    """
    Génère un problème de transport aléatoire de taille n x n.
    Retourne: (cout, P, C)
    """
    # 1. Matrice des coûts: entiers entre 1 et 100
    cout = np.random.randint(1, 101, (n, n), dtype=np.int32)
    
    # 2. Matrice temporaire pour générer les provisions et commandes
    temp = np.random.randint(1, 101, (n, n), dtype=np.int32)
    
    # 3. Provisions = somme sur les lignes de temp
    P = np.sum(temp, axis=1)
    
    # 4. Commandes = somme sur les colonnes de temp
    C = np.sum(temp, axis=0)
    
    return cout, P, C


def mesurer_temps_NO(n, cout, P, C):
    """Mesure le temps d'exécution de Nord-Ouest"""
    t0 = time.perf_counter()
    prop = nord_ouest(n, n, cout, P, C)
    t1 = time.perf_counter()
    return t1 - t0, prop


def mesurer_temps_BH(n, cout, P, C):
    """Mesure le temps d'exécution de Balas-Hammer"""
    t0 = time.perf_counter()
    prop = balas_hammer(n, n, cout, P, C)
    t1 = time.perf_counter()
    return t1 - t0, prop


def mesurer_temps_marchepied(n, cout, P, C, prop_initiale):
    """
    Mesure le temps d'exécution de la méthode du marche-pied
    à partir d'une proposition initiale donnée.
    """
    t0 = time.perf_counter()
    # Note: adapter les paramètres selon la signature réelle de marche_pied_complet
    # La fonction semble attendre (n, m, cout, P, C, prop, r2, r)
    # r et r2 sont probablement des fonctions callback pour l'affichage
    # On peut passer des fonctions vides si elles ne sont pas essentielles
    def fonction_vide(*args, **kwargs):
        pass
    
    prop_finale = marche_pied_complet(n, n, cout, P, C, prop_initiale, 
                                       fonction_vide, fonction_vide)
    t1 = time.perf_counter()
    return t1 - t0, prop_finale


def mesurer_tout_pour_n(n):
    """
    Pour une taille n donnée, effectue NB_ITERATIONS mesures.
    Retourne: (temps_NO, temps_BH, temps_MPNO, temps_MPBH)
    où chaque élément est une liste de NB_ITERATIONS valeurs.
    """
    temps_NO = []
    temps_BH = []
    temps_MPNO = []
    temps_MPBH = []
    
    for i in range(NB_ITERATIONS):
        # Génération du problème aléatoire
        cout, P, C = generer_probleme_aleatoire(n)
        
        # Mesure de Nord-Ouest
        t_no, prop_no = mesurer_temps_NO(n, cout, P, C)
        temps_NO.append(t_no)
        
        # Mesure de Balas-Hammer
        t_bh, prop_bh = mesurer_temps_BH(n, cout, P, C)
        temps_BH.append(t_bh)
        
        # Mesure du marche-pied avec proposition NO
        t_mpno, _ = mesurer_temps_marchepied(n, cout, P, C, prop_no)
        temps_MPNO.append(t_mpno)
        
        # Mesure du marche-pied avec proposition BH
        t_mpbh, _ = mesurer_temps_marchepied(n, cout, P, C, prop_bh)
        temps_MPBH.append(t_mpbh)
        
        # Affichage de la progression
        if (i + 1) % 10 == 0:
            print(f"  n={n}: {i+1}/{NB_ITERATIONS} réalisations effectuées")
    
    return temps_NO, temps_BH, temps_MPNO, temps_MPBH


# ============================================================================
# COLLECTE DES DONNÉES
# ============================================================================

def collecter_toutes_donnees():
    """Collecte les temps pour toutes les valeurs de n"""
    
    toutes_donnees = {
        'n': [],
        't_NO': [],
        't_BH': [],
        't_MPNO': [],
        't_MPBH': [],
        'pire_NO': [],
        'pire_BH': [],
        'pire_MPNO': [],
        'pire_MPBH': [],
        'pire_NO_plus_MPNO': [],
        'pire_BH_plus_MPBH': []
    }
    
    for n in N_VALUES:
        print(f"\n--- Traitement de n = {n} ---")
        
        # Collecte des 100 réalisations
        temps_NO, temps_BH, temps_MPNO, temps_MPBH = mesurer_tout_pour_n(n)
        
        # Stockage des 100 valeurs (pour le nuage de points)
        toutes_donnees['n'].extend([n] * NB_ITERATIONS)
        toutes_donnees['t_NO'].extend(temps_NO)
        toutes_donnees['t_BH'].extend(temps_BH)
        toutes_donnees['t_MPNO'].extend(temps_MPNO)
        toutes_donnees['t_MPBH'].extend(temps_MPBH)
        
        # Calcul des pires cas (enveloppe supérieure)
        pire_NO = max(temps_NO)
        pire_BH = max(temps_BH)
        pire_MPNO = max(temps_MPNO)
        pire_MPBH = max(temps_MPBH)
        pire_NO_plus_MPNO = max([temps_NO[i] + temps_MPNO[i] for i in range(NB_ITERATIONS)])
        pire_BH_plus_MPBH = max([temps_BH[i] + temps_MPBH[i] for i in range(NB_ITERATIONS)])
        
        toutes_donnees['pire_NO'].append((n, pire_NO))
        toutes_donnees['pire_BH'].append((n, pire_BH))
        toutes_donnees['pire_MPNO'].append((n, pire_MPNO))
        toutes_donnees['pire_MPBH'].append((n, pire_MPBH))
        toutes_donnees['pire_NO_plus_MPNO'].append((n, pire_NO_plus_MPNO))
        toutes_donnees['pire_BH_plus_MPBH'].append((n, pire_BH_plus_MPBH))
        
        # Affichage des résultats pour ce n
        print(f"  n={n} - Pire cas:")
        print(f"    θ_NO = {pire_NO:.6f} s")
        print(f"    θ_BH = {pire_BH:.6f} s")
        print(f"    t_MPNO = {pire_MPNO:.6f} s")
        print(f"    t_MPBH = {pire_MPBH:.6f} s")
        
        # Sauvegarde intermédiaire (optionnelle)
        np.savez(f"donnees_n_{n}.npz", 
                 temps_NO=temps_NO, temps_BH=temps_BH,
                 temps_MPNO=temps_MPNO, temps_MPBH=temps_MPBH)
    
    return toutes_donnees


# ============================================================================
# TRACÉ DES GRAPHIQUES
# ============================================================================

def tracer_nuage_points(donnees):
    """Trace le nuage de points des 100 réalisations"""
    
    # Conversion en tableaux numpy
    n_array = np.array(donnees['n'])
    t_NO = np.array(donnees['t_NO'])
    t_BH = np.array(donnees['t_BH'])
    t_MPNO = np.array(donnees['t_MPNO'])
    t_MPBH = np.array(donnees['t_MPBH'])
    t_NO_MPNO = t_NO + t_MPNO
    t_BH_MPBH = t_BH + t_MPBH
    
    # Génération de jitter pour éviter la superposition
    rng = np.random.default_rng(42)
    
    def jitter(x, scale=0.03):
        # Jitter multiplicatif en échelle log
        return x * np.exp(rng.uniform(-scale, scale, size=len(x)))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Tracé des nuages de points
    ax.scatter(jitter(n_array), t_NO, c='red', s=8, alpha=0.5, label='$t_{NO}(n)$')
    ax.scatter(jitter(n_array), t_BH, c='green', s=8, alpha=0.5, label='$t_{BH}(n)$')
    ax.scatter(jitter(n_array), t_MPNO, c='blue', s=8, alpha=0.5, label='$t_{MPNO}(n)$')
    ax.scatter(jitter(n_array), t_MPBH, c='orange', s=8, alpha=0.5, label='$t_{MPBH}(n)$')
    ax.scatter(jitter(n_array), t_NO_MPNO, c='magenta', s=8, alpha=0.5, label='$t_{NOMPNO}(n)$')
    ax.scatter(jitter(n_array), t_BH_MPBH, c='cyan', s=8, alpha=0.5, label='$t_{BHMPBH}(n)$')
    
    # Configuration des axes
    ax.set_xscale('log')
    ax.set_yscale('log')  # Échelle log pour mieux visualiser les temps
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel('Temps d\'exécution (s)', fontsize=12)
    ax.set_title('Nuages de points des temps mesurés pour 100 réalisations par taille n', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('nuage_points_temps.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig


def tracer_enveloppes_superieures(donnees):
    """Trace les enveloppes supérieures (pire cas) en fonction de n"""
    
    # Extraction des pires cas
    n_vals = [p[0] for p in donnees['pire_NO']]
    pire_NO = [p[1] for p in donnees['pire_NO']]
    pire_BH = [p[1] for p in donnees['pire_BH']]
    pire_MPNO = [p[1] for p in donnees['pire_MPNO']]
    pire_MPBH = [p[1] for p in donnees['pire_MPBH']]
    pire_NO_plus = [p[1] for p in donnees['pire_NO_plus_MPNO']]
    pire_BH_plus = [p[1] for p in donnees['pire_BH_plus_MPBH']]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(n_vals, pire_NO, 'ro-', linewidth=2, markersize=8, label='$\\theta_{NO}(n)$ (pire cas)')
    ax.plot(n_vals, pire_BH, 'gs-', linewidth=2, markersize=8, label='$\\theta_{BH}(n)$ (pire cas)')
    ax.plot(n_vals, pire_MPNO, 'b^-', linewidth=2, markersize=8, label='$t_{MPNO}(n)$ (pire cas)')
    ax.plot(n_vals, pire_MPBH, 'm^-', linewidth=2, markersize=8, label='$t_{MPBH}(n)$ (pire cas)')
    ax.plot(n_vals, pire_NO_plus, 'cD-', linewidth=2, markersize=8, label='$\\theta_{NO}+t_{MPNO}$ (pire cas)')
    ax.plot(n_vals, pire_BH_plus, 'yD-', linewidth=2, markersize=8, label='$\\theta_{BH}+t_{MPBH}$ (pire cas)')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel('Temps d\'exécution (s) - Pire cas', fontsize=12)
    ax.set_title('Enveloppes supérieures - Complexité dans le pire des cas', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Ajout de courbes de référence pour la complexité théorique
    # Normalisation basée sur le dernier point
    ref_n = n_vals[-1]
    ref_t = pire_NO[-1]
    
    n_theo = np.array([10, 100, 1000, 10000])
    # O(n) - linéaire
    t_lin = ref_t * (n_theo / ref_n)
    # O(n²) - quadratique
    t_quad = ref_t * (n_theo / ref_n) ** 2
    
    ax.plot(n_theo, t_lin, 'k--', alpha=0.5, label='$O(n)$ (référence)')
    ax.plot(n_theo, t_quad, 'k:', alpha=0.5, label='$O(n^2)$ (référence)')
    
    plt.tight_layout()
    plt.savefig('enveloppes_superieures.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig


def tracer_rapport_comparaison(donnees):
    """Trace le rapport (θ_NO + t_MPNO) / (θ_BH + t_MPBH)"""
    
    # Calcul du rapport pour chaque réalisation
    n_array = np.array(donnees['n'])
    t_NO = np.array(donnees['t_NO'])
    t_BH = np.array(donnees['t_BH'])
    t_MPNO = np.array(donnees['t_MPNO'])
    t_MPBH = np.array(donnees['t_MPBH'])
    
    rapport = (t_NO + t_MPNO) / (t_BH + t_MPBH)
    
    # Calcul du rapport pour le pire cas à chaque n
    rapports_pire_cas = []
    n_vals_pire = []
    
    for n in N_VALUES:
        indices = np.where(n_array == n)[0]
        rapports_n = [(t_NO[i] + t_MPNO[i]) / (t_BH[i] + t_MPBH[i]) for i in indices]
        rapports_pire_cas.append(max(rapports_n))
        n_vals_pire.append(n)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Nuage de points des rapports individuels (avec jitter)
    rng = np.random.default_rng(42)
    x_jitter = n_array * np.exp(rng.uniform(-0.03, 0.03, size=len(n_array)))
    ax.scatter(x_jitter, rapport, c='purple', s=8, alpha=0.3, label='Rapport par réalisation')
    
    # Courbe du pire cas
    ax.plot(n_vals_pire, rapports_pire_cas, 'ro-', linewidth=2, markersize=8, 
            label='Pire cas par taille n')
    
    # Ligne de référence à 1 (équivalence)
    ax.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='Équivalence (rapport = 1)')
    
    ax.set_xscale('log')
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel('$R(n) = \\frac{\\theta_{NO} + t_{MPNO}}{\\theta_{BH} + t_{MPBH}}$', fontsize=14)
    ax.set_title('Comparaison Nord-Ouest vs Balas-Hammer', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Valeur moyenne finale
    rapport_moyen_final = np.mean([r for i, r in enumerate(rapport) if n_array[i] == N_VALUES[-1]])
    ax.text(0.05, 0.95, f'Rapport moyen pour n={N_VALUES[-1]}: {rapport_moyen_final:.3f}', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('rapport_comparaison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig


def analyser_complexite(donnees):
    """Analyse et affiche la complexité algorithmique"""
    
    print("\n" + "="*70)
    print("ANALYSE DE LA COMPLEXITÉ DANS LE PIRE DES CAS")
    print("="*70)
    
    # Extraction des pires cas
    pire_NO = dict(donnees['pire_NO'])
    pire_BH = dict(donnees['pire_BH'])
    pire_MPNO = dict(donnees['pire_MPNO'])
    pire_MPBH = dict(donnees['pire_MPBH'])
    pire_NO_plus = dict(donnees['pire_NO_plus_MPNO'])
    pire_BH_plus = dict(donnees['pire_BH_plus_MPBH'])
    
    print("\n--- Pires cas mesurés ---")
    print(f"{'n':>6} | {'θ_NO(s)':>12} | {'θ_BH(s)':>12} | {'t_MPNO(s)':>12} | {'t_MPBH(s)':>12} | {'θ_NO+t_MPNO':>14} | {'θ_BH+t_MPBH':>14}")
    print("-" * 90)
    
    for n in N_VALUES:
        print(f"{n:6d} | {pire_NO[n]:12.6f} | {pire_BH[n]:12.6f} | {pire_MPNO[n]:12.6f} | {pire_MPBH[n]:12.6f} | {pire_NO_plus[n]:14.6f} | {pire_BH_plus[n]:14.6f}")
    
    # Estimation des rapports de croissance
    print("\n--- Estimation des rapports de croissance (pire cas) ---")
    print("\nRapport θ_NO(n_max)/θ_NO(n_min):")
    print(f"  {pire_NO[N_VALUES[-1]] / pire_NO[N_VALUES[0]]:.2f}")
    
    print("\nRapport θ_BH(n_max)/θ_BH(n_min):")
    print(f"  {pire_BH[N_VALUES[-1]] / pire_BH[N_VALUES[0]]:.2f}")
    
    # Sauvegarde des résultats
    np.savez("resultats_complexite.npz",
             n=N_VALUES,
             pire_NO=list(pire_NO.values()),
             pire_BH=list(pire_BH.values()),
             pire_MPNO=list(pire_MPNO.values()),
             pire_MPBH=list(pire_MPBH.values()),
             pire_NO_plus=list(pire_NO_plus.values()),
             pire_BH_plus=list(pire_BH_plus.values()))


# ============================================================================
# EXÉCUTION PRINCIPALE
# ============================================================================

def main():
    print("="*70)
    print("ÉTUDE DE COMPLEXITÉ - PROBLÈME DE TRANSPORT")
    print("="*70)
    print(f"\nTailles testées: {N_VALUES}")
    print(f"Nombre de réalisations par taille: {NB_ITERATIONS}")
    print("\nATTENTION: L'exécution peut être très longue (plusieurs heures) pour n=10000")
    print("Il est recommandé de réduire NB_ITERATIONS pour les tests, ou de lancer l'exécution\n")
    
    # Vérification de la configuration
    reponse = input("Voulez-vous lancer la collecte des données ? (o/n): ")
    if reponse.lower() != 'o':
        print("Exécution annulée.")
        return
    
    # Collecte des données
    donnees = collecter_toutes_donnees()
    
    # Sauvegarde des données brutes
    np.savez("donnees_completes.npz", **donnees)
    print("\nDonnées sauvegardées dans 'donnees_completes.npz'")
    
    # Analyse et tracés
    analyser_complexite(donnees)
    tracer_nuage_points(donnees)
    tracer_enveloppes_superieures(donnees)
    tracer_rapport_comparaison(donnees)
    
    print("\n" + "="*70)
    print("ANALYSE TERMINÉE")
    print("="*70)


if __name__ == "__main__":
    main()