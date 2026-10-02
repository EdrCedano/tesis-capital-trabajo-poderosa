# -*- coding: utf-8 -*-
"""
Análisis estadístico — Tesis: "Gestión del Capital de Trabajo y su Relación
con la Rentabilidad de Compañía Minera Poderosa S.A. 2020-2025"
Autor de la tesis: Eder Cedano Bustos
Etapas (según el capítulo 2.4 "Análisis de Datos" de la tesis):
 1. Estadística descriptiva (media, DE, mínimo, máximo, coeficiente de variación) por indicador.
 2. Prueba de normalidad de Shapiro-Wilk por serie (n=6).
 3. Correlación de Pearson (si ambas variables son normales) o de Spearman (si alguna no lo es),
    con criterios de magnitud de Cohen (1988) y significancia alfa = 0.05.
Todas las cifras de balance/resultados están en miles de soles (S/000) y provienen de los
Estados Financieros Separados Auditados de Compañía Minera Poderosa S.A. 2019-2025
(ver el Anexo 5 para el detalle
línea por línea y las fuentes de cada año).
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("./resultados", exist_ok=True)  # crea la carpeta de salida
pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

# --------------------------------------------------------------------- #
# 1. DATOS FUENTE (S/000), "as originally reported" por año de cierre.
#    2019 solo se usa para construir el saldo PROMEDIO de 2020 (no es parte
#    de la serie de 6 años analizada).
# --------------------------------------------------------------------- #
years = [2020, 2021, 2022, 2023, 2024, 2025]
inventario = {
    2019: 44353,
    2020: 50084,
    2021: 59856,
    2022: 70544,
    2023: 68270,
    2024: 97619,
    2025: 102859,
}
cxc_total = {
    2019: 9622 + 23718,
    2020: 12787 + 16688,
    2021: 10183 + 16592,
    2022: 12630 + 62109,
    2023: 14628 + 87810,
    2024: 19293 + 104314,
    2025: 34281 + 83432,
}
cxp_comercial = {
    2019: 70981,
    2020: 85609,
    2021: 86042,
    2022: 103394,
    2023: 210432,
    2024: 221961,
    2025: 303688,
}
costo_ventas = {
    2020: 866319,
    2021: 1101480,
    2022: 1205403,
    2023: 1324474,
    2024: 1708130,
    2025: 2104355,
}
ventas_netas = {
    2020: 1663261,
    2021: 2102747,
    2022: 2090683,
    2023: 1992610,
    2024: 2624541,
    2025: 3474265,
}
utilidad_neta = {
    2020: 385559,
    2021: 552792,
    2022: 407345,
    2023: 295664,
    2024: 415128,
    2025: 719907,
}
activo_total = {
    2020: 1708321,
    2021: 2072248,
    2022: 2100877,
    2023: 2327495,
    2024: 2542791,
    2025: 3188844,
}
patrimonio_total = {
    2020: 1196378,
    2021: 1517920,
    2022: 1594982,
    2023: 1645610,
    2024: 1883522,
    2025: 2206979,
}
DAYS = 360  # convención señalada explícitamente en el capítulo 2.3.4 de la tesis

# --------------------------------------------------------------------- #
# 2. CONSTRUCCIÓN DE LA FICHA DE REGISTRO — DOS VERSIONES
#    (A) Saldo de cierre de cada ejercicio
#    (B) Saldo promedio (inicio + fin)/2 — criterio principal adoptado en
#        esta tesis, por ser la definición estándar de Ross, Westerfield
#        & Jordan (2019), citada como base teórica del CCE en el
#        capítulo 1.2.2 de la tesis (véase también el Anexo 2).
# --------------------------------------------------------------------- #
rows_end, rows_avg = [], []

for y in years:
    inv_end, cxc_end, cxp_end = inventario[y], cxc_total[y], cxp_comercial[y]
    inv_avg = (inventario[y - 1] + inventario[y]) / 2
    cxc_avg = (cxc_total[y - 1] + cxc_total[y]) / 2
    cxp_avg = (cxp_comercial[y - 1] + cxp_comercial[y]) / 2
    ppi_end = inv_end / costo_ventas[y] * DAYS
    ppc_end = cxc_end / ventas_netas[y] * DAYS
    ppp_end = cxp_end / costo_ventas[y] * DAYS
    cce_end = ppi_end + ppc_end - ppp_end
    ppi_avg = inv_avg / costo_ventas[y] * DAYS
    ppc_avg = cxc_avg / ventas_netas[y] * DAYS
    ppp_avg = cxp_avg / costo_ventas[y] * DAYS
    cce_avg = ppi_avg + ppc_avg - ppp_avg
    roa = utilidad_neta[y] / activo_total[y] * 100
    roe = utilidad_neta[y] / patrimonio_total[y] * 100
    rows_end.append(
        dict(
            Anio=y,
            Inventario=inv_end,
            CtasCobrar=cxc_end,
            CtasPagar=cxp_end,
            CostoVentas=costo_ventas[y],
            VentasNetas=ventas_netas[y],
            PPI=ppi_end,
            PPC=ppc_end,
            PPP=ppp_end,
            CCE=cce_end,
            UtilidadNeta=utilidad_neta[y],
            ActivoTotal=activo_total[y],
            PatrimonioTotal=patrimonio_total[y],
            ROA=roa,
            ROE=roe,
        )
    )
    rows_avg.append(
        dict(
            Anio=y,
            InventarioProm=inv_avg,
            CtasCobrarProm=cxc_avg,
            CtasPagarProm=cxp_avg,
            CostoVentas=costo_ventas[y],
            VentasNetas=ventas_netas[y],
            PPI=ppi_avg,
            PPC=ppc_avg,
            PPP=ppp_avg,
            CCE=cce_avg,
            UtilidadNeta=utilidad_neta[y],
            ActivoTotal=activo_total[y],
            PatrimonioTotal=patrimonio_total[y],
            ROA=roa,
            ROE=roe,
        )
    )
df_end = pd.DataFrame(rows_end).set_index("Anio")
df_avg = pd.DataFrame(rows_avg).set_index("Anio")
print("=" * 100)
print(
    "FICHA DE REGISTRO (A) — saldos de CIERRE de cada año (criterio de contraste, Tabla 2)"
)
print("=" * 100)
print(df_end[["PPI", "PPC", "PPP", "CCE", "ROA", "ROE"]].round(2))
print()
print("=" * 100)
print(
    "FICHA DE REGISTRO (B) — saldos PROMEDIO (inicio+fin)/2 (Ross et al., 2019) -> VERSIÓN PRINCIPAL"
)
print("=" * 100)
print(df_avg[["PPI", "PPC", "PPP", "CCE", "ROA", "ROE"]].round(2))
df_end.round(2).to_csv("./resultados/ficha_saldo_cierre.csv")
df_avg.round(2).to_csv("./resultados/ficha_saldo_promedio.csv")

# We adopt the AVERAGE-balance version as the primary analytical dataset.
df = df_avg[["PPI", "PPC", "PPP", "CCE", "ROA", "ROE"]].copy()

# --------------------------------------------------------------------- #
# 3. ESTADÍSTICA DESCRIPTIVA
# --------------------------------------------------------------------- #
desc = pd.DataFrame(
    {
        "n": df.count(),
        "Media": df.mean(),
        "Desv.Est.": df.std(ddof=1),
        "Mínimo": df.min(),
        "Máximo": df.max(),
    }
)
desc["CV (%)"] = (desc["Desv.Est."] / desc["Media"]).abs() * 100
print()
print("=" * 100)
print("ESTADÍSTICA DESCRIPTIVA (2020-2025, n=6) — sobre la versión de saldos PROMEDIO")
print("=" * 100)
print(desc.round(2))
desc.round(3).to_csv("./resultados/descriptivos.csv")

# --------------------------------------------------------------------- #
# 4. PRUEBA DE NORMALIDAD DE SHAPIRO-WILK
# --------------------------------------------------------------------- #
print()
print("=" * 100)
print(
    "PRUEBA DE NORMALIDAD DE SHAPIRO-WILK (H0: la serie proviene de una distribución normal)"
)
print("=" * 100)
normalidad = {}

for col in df.columns:
    stat, p = stats.shapiro(df[col])
    normal = p > 0.05
    normalidad[col] = dict(W=stat, p=p, Normal=normal)
    print(
        f"{col:6s}  W = {stat:0.4f}   p = {p:0.4f}   -> {'Normal (p>0.05)' if normal else 'NO normal (p<=0.05)'}"
    )
df_normalidad = pd.DataFrame(normalidad).T
df_normalidad.round(4).to_csv("./resultados/shapiro_wilk.csv")


# --------------------------------------------------------------------- #
# 5. CORRELACIONES: Pearson si ambas variables son normales, Spearman si no
# --------------------------------------------------------------------- #
def cohen_magnitud(r):
    ar = abs(r)
    if ar < 0.10:
        return "trivial / nula"
    elif ar < 0.30:
        return "débil"
    elif ar < 0.50:
        return "moderada"
    else:
        return "fuerte"


pares = [
    ("PPI", "ROA", "HE1"),
    ("PPI", "ROE", "HE1"),
    ("PPC", "ROA", "HE2"),
    ("PPC", "ROE", "HE2"),
    ("PPP", "ROA", "HE3"),
    ("PPP", "ROE", "HE3"),
    ("CCE", "ROA", "HG"),
    ("CCE", "ROE", "HG"),
]
print()
print("=" * 100)
print("CORRELACIONES BIVARIADAS (alfa = 0.05) — criterios de magnitud de Cohen (1988)")
print("=" * 100)
resultados = []

for x, y, hip in pares:
    normal_x, normal_y = normalidad[x]["Normal"], normalidad[y]["Normal"]
    if normal_x and normal_y:
        r, p = stats.pearsonr(df[x], df[y])
        metodo = "Pearson"
    else:
        r, p = stats.spearmanr(df[x], df[y])
        metodo = "Spearman"
    sig = "Significativa" if p < 0.05 else "No significativa"
    direccion = "positiva" if r > 0 else "negativa"
    resultados.append(
        dict(
            Hipotesis=hip,
            Var1=x,
            Var2=y,
            Metodo=metodo,
            r=r,
            p=p,
            Magnitud=cohen_magnitud(r),
            Direccion=direccion,
            Significancia=sig,
        )
    )
    print(
        f"[{hip}] {x:4s} vs {y:4s}  ({metodo:8s})  r = {r:+.3f}   p = {p:.4f}   "
        f"-> {sig}, asociación {direccion} {cohen_magnitud(r)}"
    )
df_resultados = pd.DataFrame(resultados)
df_resultados.round(4).to_csv("./resultados/correlaciones.csv", index=False)

# --------------------------------------------------------------------- #
# 6. MATRIZ DE CORRELACIONES Y MAPA DE CALOR (Pearson, para visualización
#    conjunta tal como especifica el capítulo 2.4; el resultado inferencial
#    formal de cada hipótesis se toma de la tabla de la sección 5).
# --------------------------------------------------------------------- #
corr_matrix = df.corr(method="pearson")
corr_matrix.round(3).to_csv("./resultados/matriz_correlacion_pearson.csv")
plt.figure(figsize=(7, 5.5))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    square=True,
    linewidths=0.5,
    cbar_kws={"label": "Coeficiente de correlación"},
)
plt.title(
    "Matriz de correlación de Pearson\nIndicadores de capital de trabajo y rentabilidad\n"
    "Compañía Minera Poderosa S.A., 2020-2025",
    fontsize=10,
)
plt.tight_layout()
plt.savefig("./resultados/mapa_calor_correlaciones.png", dpi=200)
plt.close()

# --------------------------------------------------------------------- #
# 7. GRÁFICO DE EVOLUCIÓN ANUAL (CCE vs ROA/ROE) — apoyo visual adicional
# --------------------------------------------------------------------- #
fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.plot(
    df.index, df["CCE"], marker="o", color="#1F3864", label="CCE (días)", linewidth=2
)
ax1.set_xlabel("Año")
ax1.set_ylabel("Ciclo de Conversión de Efectivo (días)", color="#1F3864")
ax1.tick_params(axis="y", labelcolor="#1F3864")
ax1.axhline(0, color="gray", linewidth=0.8, linestyle="--")
ax2 = ax1.twinx()
ax2.plot(df.index, df["ROA"], marker="s", color="#C00000", label="ROA (%)", linewidth=2)
ax2.plot(df.index, df["ROE"], marker="^", color="#548235", label="ROE (%)", linewidth=2)
ax2.set_ylabel("Rentabilidad (%)", color="#C00000")
ax2.tick_params(axis="y", labelcolor="#C00000")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper center", ncol=3, fontsize=8)
plt.title(
    "Evolución del CCE y la rentabilidad (ROA, ROE)\nCompañía Minera Poderosa S.A., 2020-2025",
    fontsize=10,
)
plt.xticks(df.index)
plt.tight_layout()
plt.savefig("./resultados/evolucion_cce_rentabilidad.png", dpi=200)
plt.close()
print()
print("Archivos generados en ./resultados/:")
print(" - ficha_saldo_cierre.csv, ficha_saldo_promedio.csv")
print(
    " - descriptivos.csv, shapiro_wilk.csv, correlaciones.csv, matriz_correlacion_pearson.csv"
)
print(" - mapa_calor_correlaciones.png, evolucion_cce_rentabilidad.png")
