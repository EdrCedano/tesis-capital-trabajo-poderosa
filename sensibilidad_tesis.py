# -*- coding: utf-8 -*-
"""
Análisis de sensibilidad — Tesis: Gestión del Capital de Trabajo y su Relación
con la Rentabilidad de Compañía Minera Poderosa S.A., 2020-2025
Autor de la tesis: Eder Cedano Bustos

Complementa el Anexo 4 (mismos datos de base, en S/ miles). Verificaciones:
  (a) IC 95 % de r (transformación z de Fisher), Spearman y p ajustado de Holm.
  (b) Exclusión secuencial de cada año (leave-one-out) para PPC-ROA y PPC-ROE.
  (c) Primeras diferencias (n = 5), para atenuar la tendencia común.
  (d) Descomposición del PPC: cuentas por cobrar comerciales vs. otras cuentas por cobrar.
  (e) Diagnóstico de tendencia y autocorrelación (Durbin-Watson de ROA ~ PPC).

Requiere: numpy, pandas, scipy.  Ejecución:  python sensibilidad_tesis.py
"""
import numpy as np
import pandas as pd
from scipy import stats

DAYS = 360
years = [2020, 2021, 2022, 2023, 2024, 2025]

# --- Datos de base (S/ miles) --------------------------------------------------
inventario = {2019: 44353, 2020: 50084, 2021: 59856, 2022: 70544, 2023: 68270, 2024: 97619, 2025: 102859}
# Cuentas por cobrar: (comerciales, otras cuentas por cobrar) según el Anexo 4
cxc_com = {2019: 9622, 2020: 12787, 2021: 10183, 2022: 12630, 2023: 14628, 2024: 19293, 2025: 34281}
cxc_otr = {2019: 23718, 2020: 16688, 2021: 16592, 2022: 62109, 2023: 87810, 2024: 104314, 2025: 83432}
cxp_com = {2019: 70981, 2020: 85609, 2021: 86042, 2022: 103394, 2023: 210432, 2024: 221961, 2025: 303688}
costo_ventas = {2020: 866319, 2021: 1101480, 2022: 1205403, 2023: 1324474, 2024: 1708130, 2025: 2104355}
ventas_netas = {2020: 1663261, 2021: 2102747, 2022: 2090683, 2023: 1992610, 2024: 2624541, 2025: 3474265}
utilidad_neta = {2020: 385559, 2021: 552792, 2022: 407345, 2023: 295664, 2024: 415128, 2025: 719907}
activo_total = {2020: 1708321, 2021: 2072248, 2022: 2100877, 2023: 2327495, 2024: 2542791, 2025: 3188844}
patrimonio = {2020: 1196378, 2021: 1517920, 2022: 1594982, 2023: 1645610, 2024: 1883522, 2025: 2206979}


def prom(d, y):
    """Saldo promedio (inicial + final) / 2."""
    return (d[y - 1] + d[y]) / 2


rows = []
for y in years:
    ppi = prom(inventario, y) / costo_ventas[y] * DAYS
    ppc_com = prom(cxc_com, y) / ventas_netas[y] * DAYS
    ppc_otr = prom(cxc_otr, y) / ventas_netas[y] * DAYS
    ppp = prom(cxp_com, y) / costo_ventas[y] * DAYS
    rows.append(dict(Anio=y, PPI=ppi, PPC=ppc_com + ppc_otr, PPC_com=ppc_com, PPC_otras=ppc_otr,
                     PPP=ppp, CCE=ppi + ppc_com + ppc_otr - ppp,
                     ROA=utilidad_neta[y] / activo_total[y] * 100,
                     ROE=utilidad_neta[y] / patrimonio[y] * 100))
df = pd.DataFrame(rows).set_index("Anio")
pd.set_option("display.width", 160)
print("Serie base (saldos promedio):\n", df.round(2), "\n")

X = ["PPI", "PPC", "PPP", "CCE"]
Y = ["ROA", "ROE"]


def ic95(r, n):
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)


def holm(pvals):
    order = np.argsort(pvals)
    m, adj, prev = len(pvals), [0.0] * len(pvals), 0.0
    for k, i in enumerate(order):
        prev = max(prev, min(1.0, (m - k) * pvals[i]))
        adj[i] = prev
    return adj


# (a) IC 95 %, Spearman y Holm ------------------------------------------------
pares = [(x, y) for x in X for y in Y]
res = []
for x, y in pares:
    r, p = stats.pearsonr(df[x], df[y])
    rho, ps = stats.spearmanr(df[x], df[y])
    lo, hi = ic95(r, len(df))
    res.append(dict(Relacion=f"{x} - {y}", r=r, IC_inf=lo, IC_sup=hi, p=p, rho=rho, p_spearman=ps))
tabla_a = pd.DataFrame(res)
tabla_a["p_Holm"] = holm(tabla_a["p"].tolist())
print("(a) IC 95 %, Spearman y Holm:\n", tabla_a.round(3), "\n")

# (b) Leave-one-out para PPC ----------------------------------------------------
loo = []
for yr in years:
    s = df.drop(yr)
    r1, p1 = stats.pearsonr(s["PPC"], s["ROA"])
    r2, p2 = stats.pearsonr(s["PPC"], s["ROE"])
    loo.append(dict(Anio_excluido=yr, r_ROA=r1, p_ROA=p1, r_ROE=r2, p_ROE=p2))
tabla_b = pd.DataFrame(loo)
print("(b) Leave-one-out (PPC):\n", tabla_b.round(3), "\n")

# (c) Primeras diferencias (n = 5) ---------------------------------------------
d1 = df[X + Y].diff().dropna()
dif = []
for x, y in pares:
    r, p = stats.pearsonr(d1[x], d1[y])
    dif.append(dict(Relacion=f"d{x} - d{y}", r=r, p=p))
tabla_c = pd.DataFrame(dif)
print("(c) Primeras diferencias (n = 5):\n", tabla_c.round(3), "\n")

# (d) Descomposición del PPC ---------------------------------------------------
dec = []
for comp in ["PPC_com", "PPC_otras"]:
    fila = {"Componente": comp}
    for y in Y:
        r, p = stats.pearsonr(df[comp], df[y])
        fila[f"r_{y}"], fila[f"p_{y}"] = r, p
    dec.append(fila)
tabla_d = pd.DataFrame(dec)
print("(d) Descomposición del PPC:\n", tabla_d.round(3), "\n")
print("PPC vs PPP: r = %.3f (p = %.3f)" % stats.pearsonr(df["PPC"], df["PPP"]))

# (e) Tendencia y autocorrelación ----------------------------------------------
anio = np.array(years, dtype=float)
for v in ["PPC", "PPP", "ROA"]:
    r, p = stats.pearsonr(df[v], anio)
    print(f"Tendencia: r({v}, año) = {r:+.3f} (p = {p:.3f})")
A = np.c_[np.ones(len(df)), df["PPC"].values]
beta = np.linalg.lstsq(A, df["ROA"].values, rcond=None)[0]
e = df["ROA"].values - A @ beta
dw = np.sum(np.diff(e) ** 2) / np.sum(e ** 2)
print(f"Durbin-Watson (ROA ~ PPC) = {dw:.3f}")
