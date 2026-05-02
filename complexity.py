import numpy as np
import time
import gc
import sys
import os
import pickle
from nordouest import nord_ouest
from balashammer import balas_hammer
from marchepied import marche_pied_complet
import matplotlib.pyplot as plt
import psutil
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION ADAPTATIVE SELON LA MÉMOIRE DISPONIBLE
# ============================================================================

def get_memory_usage():
    """Retourne l'utilisation mémoire en Mo"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)

def verifier_memoire_disponible():
    """Vérifie la mémoire RAM disponible et configure les paramètres"""
    ram_total = psutil.virtual_memory().total / (1024**3)
    ram_disponible = psutil.virtual_memory().available / (1024**3)
    
    print(f"RAM totale: {ram_total:.1f} Go")
    print(f"RAM disponible: {ram_disponible:.1f} Go")
    
    if ram_total < 8:
        print("⚠️  Configuration: Faible mémoire (<8 Go)")
        return {
            'max_n': 100,
            'iterations_defaut': 20,
            'iterations_par_n': {10: 100, 40: 100, 100: 100,  400: 100}
        }
    elif ram_total < 16:
        print("✅ Configuration: Mémoire moyenne (8-16 Go)")
        return {
            'max_n': 400,
            'iterations_defaut': 30,
            'iterations_par_n': {10: 100, 40: 100, 100: 100, 400: 100}
        }
    else:
        print("🚀 Configuration: Haute mémoire (>16 Go)")
        return {
            'max_n': 1000,
            'iterations_defaut': 50,
            'iterations_par_n': {10: 100, 40: 100, 100: 100, 400: 100}
        }

# Détection automatique
CONFIG = verifier_memoire_disponible()
MAX_N = CONFIG['max_n']
N_VALUES = [10, 40, 100, 400]
N_VALUES = [n for n in N_VALUES if n <= MAX_N]

print(f"\n📊 Tailles à tester: {N_VALUES}")
print(f"📈 Itérations par taille: {CONFIG['iterations_par_n']}")
print("="*70)

# ============================================================================
# VERSION ÉCONOME EN MÉMOIRE DES FONCTIONS
# ============================================================================

def generer_probleme_aleatoire_econome(n):
    """
    Génère un problème de transport aléatoire avec une mémoire minimale.
    Utilise uint8 pour les matrices (1 octet au lieu de 4).
    """
    # Matrice des coûts: entiers entre 1 et 100 -> uint8 (0-255 parfait)
    cout = np.random.randint(1, 101, (n, n), dtype=np.uint8)
    
    # Matrice temporaire pour générer provisions et commandes
    temp = np.random.randint(1, 101, (n, n), dtype=np.uint8)
    
    # Provisions = somme sur les lignes (peut dépasser 255 -> int32)
    P = np.sum(temp, axis=1, dtype=np.int32)
    
    # Commandes = somme sur les colonnes
    C = np.sum(temp, axis=0, dtype=np.int32)
    
    return cout, P, C

def generer_probleme_aleatoire_ultra_econome(n):
    """
    Version encore plus économique : génère ligne par ligne sans stocker
    toute la matrice temporaire en mémoire.
    """
    # Matrice des coûts (nécessaire pour les algorithmes)
    cout = np.random.randint(1, 101, (n, n), dtype=np.uint8)
    
    # Génération des provisions et commandes sans stocker temp complète
    P = np.zeros(n, dtype=np.int32)
    C = np.zeros(n, dtype=np.int32)
    
    # On génère ligne par ligne
    for i in range(n):
        ligne = np.random.randint(1, 101, n, dtype=np.uint8)
        P[i] = np.sum(ligne)
        C += ligne
    
    return cout, P, C

# ============================================================================
# FONCTIONS DE MESURE AVEC LIBÉRATION MÉMOIRE
# ============================================================================

def mesurer_temps_NO_econome(n, cout, P, C):
    """Mesure le temps d'exécution de Nord-Ouest"""
    gc.collect()  # Nettoyage avant mesure
    t0 = time.perf_counter()
    prop = nord_ouest(n, n, cout, P, C)
    t1 = time.perf_counter()
    return t1 - t0, prop

def mesurer_temps_BH_econome(n, cout, P, C):
    """Mesure le temps d'exécution de Balas-Hammer"""
    gc.collect()
    t0 = time.perf_counter()
    prop = balas_hammer(n, n, cout, P, C)
    t1 = time.perf_counter()
    return t1 - t0, prop

def mesurer_temps_marchepied_econome(n, cout, P, C, prop_initiale):
    """Mesure le temps d'exécution du marche-pied"""
    gc.collect()
    
    def fonction_vide(*args, **kwargs):
        pass
    
    t0 = time.perf_counter()
    prop_finale = marche_pied_complet(n, n, cout, P, C, prop_initiale, 
                                       fonction_vide, fonction_vide)
    t1 = time.perf_counter()
    return t1 - t0, prop_finale

def mesurer_tout_pour_n(n, nb_iterations):
    """
    Pour une taille n donnée, effectue nb_iterations mesures.
    Version avec libération mémoire explicite.
    """
    temps_NO = []
    temps_BH = []
    temps_MPNO = []
    temps_MPBH = []
    
    print(f"\n--- n={n} ({nb_iterations} itérations) ---")
    print(f"Mémoire initiale: {get_memory_usage():.1f} Mo")
    
    for i in range(nb_iterations):
        # Affichage progression
        if (i + 1) % max(1, nb_iterations // 5) == 0:
            print(f"  Progression: {i+1}/{nb_iterations} - Mémoire: {get_memory_usage():.1f} Mo")
        
        try:
            # Génération du problème (version économique)
            cout, P, C = generer_probleme_aleatoire_econome(n)
            
            # Mesure Nord-Ouest
            t_no, prop_no = mesurer_temps_NO_econome(n, cout, P, C)
            temps_NO.append(t_no)
            
            # Mesure Balas-Hammer
            t_bh, prop_bh = mesurer_temps_BH_econome(n, cout, P, C)
            temps_BH.append(t_bh)
            
            # Mesure Marche-pied avec NO
            t_mpno, _ = mesurer_temps_marchepied_econome(n, cout, P, C, prop_no)
            temps_MPNO.append(t_mpno)
            
            # Mesure Marche-pied avec BH
            t_mpbh, _ = mesurer_temps_marchepied_econome(n, cout, P, C, prop_bh)
            temps_MPBH.append(t_mpbh)
            
            # Libération explicite
            del cout, P, C, prop_no, prop_bh
            gc.collect()
            
        except MemoryError:
            print(f"  ❌ MemoryError à l'itération {i+1} pour n={n}")
            break
        except Exception as e:
            print(f"  ⚠️  Erreur à l'itération {i+1}: {e}")
            continue
    
    print(f"Terminé pour n={n} - Mémoire finale: {get_memory_usage():.1f} Mo")
    
    return temps_NO, temps_BH, temps_MPNO, temps_MPBH

# ============================================================================
# FONCTION AVEC SAUVEGARDE ET REPRISE
# ============================================================================

def mesurer_avec_reprise():
    """Permet de reprendre l'exécution après un crash"""
    
    fichier_sauvegarde = "mesures_complexite.pkl"
    
    # Charger les résultats déjà obtenus
    resultats = {}
    if os.path.exists(fichier_sauvegarde):
        try:
            with open(fichier_sauvegarde, 'rb') as f:
                resultats = pickle.load(f)
            print(f"✅ Résultats partiels chargés: {list(resultats.keys())}")
        except:
            print("⚠️  Fichier de sauvegarde corrompu, nouveau départ")
    
    for n in N_VALUES:
        if n in resultats:
            print(f"⏭️  n={n} déjà traité, passage à la suite")
            continue
        
        nb_iter = CONFIG['iterations_par_n'].get(n, CONFIG['iterations_defaut'])
        
        try:
            temps_NO, temps_BH, temps_MPNO, temps_MPBH = mesurer_tout_pour_n(n, nb_iter)
            
            resultats[n] = {
                't_NO': temps_NO,
                't_BH': temps_BH,
                't_MPNO': temps_MPNO,
                't_MPBH': temps_MPBH
            }
            
            # Sauvegarde après chaque n
            with open(fichier_sauvegarde, 'wb') as f:
                pickle.dump(resultats, f)
            print(f"💾 Sauvegarde effectuée pour n={n}")
            
        except MemoryError:
            print(f"❌ Crash mémoire pour n={n}, arrêt de la progression")
            break
        except KeyboardInterrupt:
            print(f"⏸️  Interruption utilisateur, sauvegarde des résultats pour n={n}")
            break
        except Exception as e:
            print(f"❌ Erreur pour n={n}: {e}")
            continue
    
    return resultats

# ============================================================================
# TRACÉ DES GRAPHIQUES (VERSION ADAPTÉE)
# ============================================================================

def tracer_nuage_points(donnees):
    """
    Trace le nuage de points avec jitter.
    Séries tracées (conformément à la section 3.3.3 du projet) :
      - t_NO(n)  : temps de l'algorithme Nord-Ouest seul
      - t_BH(n)  : temps de l'algorithme Balas-Hammer seul
      - \theta_{MPNO}(n): temps du marche-pied initialisé par Nord-Ouest
      - \theta_{MPBH}(n): temps du marche-pied initialisé par Balas-Hammer
      - (t_NO + \theta_{MPNO})(n) : temps total côté Nord-Ouest
      - (t_BH + \theta_{MPBH})(n) : temps total côté Balas-Hammer
    """
    if not donnees:
        print("Aucune donnée à tracer")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rng = np.random.default_rng(42)
    
    # Clé interne -> (couleur, label affiché, style de marqueur)
    # Les algorithmes d'initialisation sont θ (pas t) selon la nomenclature du projet
    series = [
        ('t_NO',   'red',    '$t_{NO}(n)$',           None),
        ('t_BH',   'green',  '$t_{BH}(n)$',           None),
        ('t_MPNO', 'blue',   r'$\theta_{MPNO}(n)$',         None),
        ('t_MPBH', 'orange', r'$\theta_{MPBH}(n)$',         None),
        ('sum_NO', 'darkred',    r'$(t_{NO}+\theta_{MPNO})(n)$', '+'),
        ('sum_BH', 'darkgreen',  r'$(t_{BH}+\theta_{MPBH})(n)$', 'x'),
    ]
    
    n_sorted = sorted(donnees.keys())
    premiere_n = n_sorted[0]
    
    for n in n_sorted:
        d = donnees[n]
        t_no   = np.array(d['t_NO'])
        t_bh   = np.array(d['t_BH'])
        t_mpno = np.array(d['t_MPNO'])
        t_mpbh = np.array(d['t_MPBH'])
        
        # Calcul des sommes si les longueurs correspondent
        k = min(len(t_no), len(t_bh), len(t_mpno), len(t_mpbh))
        sums = {
            't_NO':   t_no[:k],
            't_BH':   t_bh[:k],
            't_MPNO': t_mpno[:k],
            't_MPBH': t_mpbh[:k],
            'sum_NO': t_no[:k] + t_mpno[:k],
            'sum_BH': t_bh[:k] + t_mpbh[:k],
        }
        
        for key, couleur, label, marker in series:
            vals = sums.get(key, [])
            if len(vals) == 0:
                continue
            x_vals = np.full(len(vals), n)
            x_jitter = x_vals * np.exp(rng.uniform(-0.03, 0.03, size=len(vals)))
            mk = marker if marker else 'o'
            ax.scatter(x_jitter, vals, c=couleur, s=8, alpha=0.5, marker=mk,
                       label=label if n == premiere_n else "")
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel("Temps d'exécution (s)", fontsize=12)
    ax.set_title('Nuages de points des temps mesurés', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('nuage_points_temps.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig

def tracer_enveloppes_superieures(donnees):
    """
    Trace les enveloppes supérieures (pire cas) conformément à la section 3.3.4.
    Séries : t_NO, t_BH, \theta_{MPNO}, \theta_{MPBH}, (t_NO+\theta_{MPNO}), (t_BH+\theta_{MPBH}).
    """
    if not donnees:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    series = [
        ('t_NO',   r'$t_{NO}(n)$',              'o', 'red'),
        ('t_BH',   r'$t_{BH}(n)$',              's', 'green'),
        ('t_MPNO', r'$\theta_{MPNO}(n)$',                 '^', 'blue'),
        ('t_MPBH', r'$\theta_{MPBH}(n)$',                 'v', 'orange'),
        ('sum_NO', r'$(t_{NO}+\theta_{MPNO})(n)$',   'D', 'darkred'),
        ('sum_BH', r'$(t_{BH}+\theta_{MPBH})(n)$',   'P', 'darkgreen'),
    ]
    
    for key, label, marker, color in series:
        n_vals = []
        max_vals = []
        for n in sorted(donnees.keys()):
            d = donnees[n]
            if key == 'sum_NO':
                t_no   = np.array(d['t_NO'])
                t_mpno = np.array(d['t_MPNO'])
                k = min(len(t_no), len(t_mpno))
                vals = (t_no[:k] + t_mpno[:k]).tolist()
            elif key == 'sum_BH':
                t_bh   = np.array(d['t_BH'])
                t_mpbh = np.array(d['t_MPBH'])
                k = min(len(t_bh), len(t_mpbh))
                vals = (t_bh[:k] + t_mpbh[:k]).tolist()
            else:
                vals = d[key]
            
            if vals:
                n_vals.append(n)
                max_vals.append(max(vals))
        
        if n_vals:
            ax.plot(n_vals, max_vals, marker=marker, color=color, linewidth=2,
                    markersize=8, label=f'{label} (pire cas)')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel("Temps d'exécution (s) - Pire cas", fontsize=12)
    ax.set_title('Enveloppes supérieures - Complexité dans le pire des cas', fontsize=14)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('enveloppes_superieures.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig

def tracer_rapport_comparaison(donnees):
    """
    Trace R(n) = (t_NO + \theta_{MPNO}) / (t_BH + \theta_{MPBH}) conformément à la section 3.3.5.
    Affiche le nuage de points de toutes les réalisations + l'enveloppe supérieure (pire cas).
    """
    if not donnees:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rng = np.random.default_rng(42)
    
    rapports_pire = []
    n_vals_pire = []
    
    for n in sorted(donnees.keys()):
        d = donnees[n]
        t_NO   = np.array(d['t_NO'])
        t_BH   = np.array(d['t_BH'])
        t_MPNO = np.array(d['t_MPNO'])
        t_MPBH = np.array(d['t_MPBH'])
        
        k = min(len(t_NO), len(t_BH), len(t_MPNO), len(t_MPBH))
        if k == 0:
            continue
        
        denominateur = t_BH[:k] + t_MPBH[:k]
        # Éviter la division par zéro
        masque = denominateur > 0
        if not np.any(masque):
            continue
        
        rapport = (t_NO[:k][masque] + t_MPNO[:k][masque]) / denominateur[masque]
        
        # Nuage de points
        x_vals = np.full(len(rapport), n)
        x_jitter = x_vals * np.exp(rng.uniform(-0.03, 0.03, size=len(rapport)))
        ax.scatter(x_jitter, rapport, c='purple', s=8, alpha=0.3)
        
        # Pire cas (enveloppe supérieure)
        rapports_pire.append(max(rapport))
        n_vals_pire.append(n)
    
    if n_vals_pire:
        ax.plot(n_vals_pire, rapports_pire, 'ro-', linewidth=2, markersize=8,
                label='Pire cas par taille n')
    
    ax.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='Équivalence')
    
    ax.set_xscale('log')
    # Pas d'échelle log sur Y : les valeurs de R peuvent être < 1 et l'échelle linéaire
    # est plus lisible pour interpréter le rapport autour de 1.
    ax.set_xlabel('n (taille du problème)', fontsize=12)
    ax.set_ylabel(
        r'$R(n) = \dfrac{t_{NO} + \theta_{MPNO}}{t_{BH} + \theta_{MPBH}}$',
        fontsize=14
    )
    ax.set_title('Comparaison Nord-Ouest vs Balas-Hammer', fontsize=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('rapport_comparaison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return fig

# ============================================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================================

def afficher_resultats(donnees):
    """Affiche les résultats de façon lisible"""
    
    print("\n" + "="*80)
    print("RÉSULTATS DES MESURES DE COMPLEXITÉ")
    print("="*80)
    
    print(f"\n{'n':>6} | {'itérations':>10} | {'t_NO (s)':>12} | {'t_BH (s)':>12} | {'θ_MPNO (s)':>12} | {'θ_MPBH (s)':>12} | {'t_NO+θ_MPNO':>14} | {'t_BH+θ_MPBH':>14}")
    print("-" * 100)
    
    for n in sorted(donnees.keys()):
        nb_iter = len(donnees[n]['t_NO'])
        if nb_iter > 0:
            moy_NO   = np.mean(donnees[n]['t_NO'])
            moy_BH   = np.mean(donnees[n]['t_BH'])
            moy_MPNO = np.mean(donnees[n]['t_MPNO'])
            moy_MPBH = np.mean(donnees[n]['t_MPBH'])
            k = min(len(donnees[n]['t_NO']), len(donnees[n]['t_MPNO']))
            moy_sum_NO = np.mean(np.array(donnees[n]['t_NO'][:k]) + np.array(donnees[n]['t_MPNO'][:k]))
            k2 = min(len(donnees[n]['t_BH']), len(donnees[n]['t_MPBH']))
            moy_sum_BH = np.mean(np.array(donnees[n]['t_BH'][:k2]) + np.array(donnees[n]['t_MPBH'][:k2]))
            
            print(f"{n:6d} | {nb_iter:10d} | {moy_NO:12.6f} | {moy_BH:12.6f} | {moy_MPNO:12.6f} | {moy_MPBH:12.6f} | {moy_sum_NO:14.6f} | {moy_sum_BH:14.6f}")
    
    print("\n" + "="*80)

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    print("="*70)
    print("📊 ÉTUDE DE COMPLEXITÉ - PROBLÈME DE TRANSPORT")
    print("="*70)
    
    print(f"\nConfiguration détectée:")
    print(f"  - RAM totale: {psutil.virtual_memory().total / (1024**3):.1f} Go")
    print(f"  - RAM disponible: {psutil.virtual_memory().available / (1024**3):.1f} Go")
    print(f"  - CPU: {psutil.cpu_count()} cœurs")
    print(f"\nTailles à tester: {N_VALUES}")
    
    # Vérification
    if MAX_N < 100:
        print("\n⚠️  Configuration basse mémoire détectée")
        print("   Seules les petites tailles seront testées")
        print("   Pour les grandes tailles, une extrapolation théorique sera utilisée")
    
    reponse = input("\n🚀 Lancer la collecte des données ? (o/n): ")
    if reponse.lower() != 'o':
        print("Exécution annulée.")
        return
    
    # Collecte avec reprise
    donnees = mesurer_avec_reprise()
    
    if not donnees:
        print("❌ Aucune donnée collectée")
        return
    
    # Sauvegarde finale
    with open("donnees_complexite_finales.pkl", 'wb') as f:
        pickle.dump(donnees, f)
    print("\n💾 Données sauvegardées dans 'donnees_complexite_finales.pkl'")
    
    # Affichage des résultats
    afficher_resultats(donnees)
    
    # Tracés des graphiques
    print("\n📈 Génération des graphiques...")
    tracer_nuage_points(donnees)
    tracer_enveloppes_superieures(donnees)
    tracer_rapport_comparaison(donnees)
    
    print("\n✅ Analyse terminée!")
    print("   Graphiques sauvegardés:")
    print("   - nuage_points_temps.png")
    print("   - enveloppes_superieures.png")
    print("   - rapport_comparaison.png")

if __name__ == "__main__":
    main()