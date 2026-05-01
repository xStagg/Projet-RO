import numpy as np
import time
from nordouest import nord_ouest
from balashammer import balas_hammer
from marchepied import marche_pied_complet
from main import lire_probleme
import matplotlib.pyplot as plt

n = 8

cost = np.random.randint(1, 101, (n, n), dtype=np.int32)

print(cost)

temp = np.random.randint(1, 101, (n, n), dtype=np.int32)

print(temp)


test = np.asarray([[30, 20, 20],
                [10, 50, 20],
                [50, 40, 30],
                [30, 20, 30]])
print(test)



P = np.sum(temp, axis=1)
C = np.sum(temp, axis=0)

print(P)
print(C)

prblm = lire_probleme("pb1.txt")

def test_NO(n, cost, P, C):
    t0 = time.perf_counter()
    nord_ouest(n, n, cost, P, C)
    t1 = time.perf_counter()
    return t1-t0

def test_BH(n, cost, P, C):
    t0 = time.perf_counter()
    balas_hammer(n, n, cost, P, C)
    t1 = time.perf_counter()
    return t1-t0

def test_MPNO(n, cost, P, C):
    prop = nord_ouest(n, n, cost, P, C)
    t0 = time.perf_counter()
    marche_pied_complet(n, n, cost, P, C, prop, r2, r)
    t1 = time.perf_counter()
    return t1-t0

def test_MPBH(n, cost, P, C):
    prop = balas_hammer(n, n, cost, P, C)
    t0 = time.perf_counter()
    marche_pied_complet(n, n, cost, P, C, prop, r2, r)
    t1 = time.perf_counter()
    return t1-t0

def test_all(n):
    cost = np.random.randint(1, 101, (n, n), dtype=np.int32)
    temp = np.random.randint(1, 101, (n, n), dtype=np.int32)
    P, C = np.sum(temp, axis=1), np.sum(temp, axis=0)
    

    print(cost)
    print(P, C)

    tno = test_NO(n, cost, P, C)
    tbh = test_BH(n, cost, P, C)
    tmpno = test_MPNO(n, cost, P, C)
    tmpbh = test_MPBH(n, cost, P, C)
    return tno, tbh, tmpno, tmpbh

def r(a):
    pass

def r2(a, b):
    pass

def nuage_point(n):
    T_no = []
    T_bh = []
    T_mpno = []
    T_mpbh = []
    for _ in range(100):
        T = test_all(n)
        T_no.append(T[0])
        T_bh.append(T[1])
        T_mpno.append(T[2])
        T_mpbh.append(T[3])
    return T_no, T_bh, T_mpno, T_mpbh

# Les valeurs de n à tester (suivant l’énoncé)
N_values = [10]

all_no   = []
all_bh   = []
all_mpno = []
all_mpbh = []
all_n_no   = []
all_n_bh   = []
all_n_mpno = []
all_n_mpbh = []

for n in N_values:
    T_no, T_bh, T_mpno, T_mpbh = nuage_point(n)
    # répéter n 100 fois pour avoir les abscisses
    all_n_no.extend([n] * len(T_no))
    all_n_bh.extend([n] * len(T_bh))
    all_n_mpno.extend([n] * len(T_mpno))
    all_n_mpbh.extend([n] * len(T_mpbh))

    all_no.extend(T_no)
    all_bh.extend(T_bh)
    all_mpno.extend(T_mpno)
    all_mpbh.extend(T_mpbh)

all_n_no   = np.array(all_n_no)
all_n_bh   = np.array(all_n_bh)
all_n_mpno = np.array(all_n_mpno)
all_n_mpbh = np.array(all_n_mpbh)

all_no     = np.array(all_no)
all_bh     = np.array(all_bh)
all_mpno   = np.array(all_mpno)
all_mpbh   = np.array(all_mpbh)

all_no_mpno = all_no + all_mpno
all_bh_mpbh = all_bh + all_mpbh

print(all_no_mpno)
print(all_bh_mpbh)

rng = np.random.default_rng(42)

def jitter_x(x, scale=0.04):
    # bruit multiplicatif adapté à une échelle log
    return x * np.exp(rng.uniform(-scale, scale, size=len(x)))


fig, ax = plt.subplots()

ax.scatter(jitter_x(all_n_no),   all_no,   c="r", s=10, alpha=0.6, label="t_NO(n)")
ax.scatter(jitter_x(all_n_bh),   all_bh,   c="g", s=10, alpha=0.6, label="t_BH(n)")
ax.scatter(jitter_x(all_n_mpno), all_mpno, c="w", s=10, alpha=0.6, label="t_MPNO(n)")
ax.scatter(jitter_x(all_n_mpbh), all_mpbh, c="k", s=10, alpha=0.6, label="t_MPBH(n)")
ax.scatter(jitter_x(all_n_no), all_no_mpno, c="m", s=10, label="t_NOMPNO(n)")
ax.scatter(jitter_x(all_n_bh), all_bh_mpbh, c="c", s=10, label="t_BHMPBH(n)")

ax.set_xscale("log")   # utile vu les valeurs de n (10 à 10^4)
ax.set_xlabel("n")
ax.set_ylabel("Temps d'exécution (s)")
ax.set_title("Nuages de points des temps mesurés")
ax.legend()

plt.show()