# -*- coding: utf-8 -*-
"""
Verificación de las cifras de base contra los estados financieros separados auditados.

Para cada cifra que usan los scripts 01 y 02 (miles de soles) busca, en los PDF de la
carpeta indicada, una página del año correspondiente que contenga a la vez el nombre de la
partida y el número. Imprime una tabla con el archivo y la página donde la encontró y guarda
el resultado en resultados/verificacion_cifras_eeff.csv.

Uso (desde la raíz del repositorio):
    python src/03_verificacion_cifras_eeff.py "EEFF Poderosa 2020-2025"

Requisitos:
  - Los PDF deben tener el año del estado financiero en el nombre del archivo
    (por ejemplo estados-financieros-2023.pdf). Se ignoran los que dicen "eng" (versión en inglés).
  - Para 2020 se usa la memoria anual, que incluye los estados financieros y la columna 2019.
  - Lee los PDF con pdftotext (poppler) si está instalado; si no, con la librería pypdf.
"""

import os
import re
import shutil
import subprocess
import sys

import pandas as pd

CARPETA = sys.argv[1] if len(sys.argv) > 1 else "EEFF Poderosa 2020-2025"

# Cifras en miles de soles, tal como las reportó cada estado financiero de cierre.
# (partida, patrón de la etiqueta que debe estar en la página, {año: cifra})
PARTIDAS = [
    (
        "Inventarios",
        r"Inventarios",
        {
            2019: 44353,
            2020: 50084,
            2021: 59856,
            2022: 70544,
            2023: 68270,
            2024: 97619,
            2025: 102859,
        },
    ),
    (
        "Cuentas por cobrar comerciales",
        r"Cuentas por cobrar comerciales",
        {
            2019: 9622,
            2020: 12787,
            2021: 10183,
            2022: 12630,
            2023: 14628,
            2024: 19293,
            2025: 34281,
        },
    ),
    (
        "Otras cuentas por cobrar",
        r"Otras cuentas por cobrar",
        {
            2019: 23718,
            2020: 16688,
            2021: 16592,
            2022: 62109,
            2023: 87810,
            2024: 104314,
            2025: 83432,
        },
    ),
    (
        "Cuentas por pagar comerciales",
        r"Cuentas por pagar comerciales",
        {
            2019: 70981,
            2020: 85609,
            2021: 86042,
            2022: 103394,
            2023: 210432,
            2024: 221961,
            2025: 303688,
        },
    ),
    (
        "Costo de ventas",
        r"Costo de ventas",
        {
            2020: 866319,
            2021: 1101480,
            2022: 1205403,
            2023: 1324474,
            2024: 1708130,
            2025: 2104355,
        },
    ),
    (
        "Ventas netas",
        r"Ingresos de actividades ordinarias",
        {
            2020: 1663261,
            2021: 2102747,
            2022: 2090683,
            2023: 1992610,
            2024: 2624541,
            2025: 3474265,
        },
    ),
    # La utilidad se busca en la página del estado de resultados (la que tiene "Costo de ventas").
    (
        "Utilidad neta",
        r"Costo de ventas",
        {
            2020: 385559,
            2021: 552792,
            2022: 407345,
            2023: 295664,
            2024: 415128,
            2025: 719907,
        },
    ),
    (
        "Activo total",
        r"Total activo(?! corriente| no corriente)",
        {
            2020: 1708321,
            2021: 2072248,
            2022: 2100877,
            2023: 2327495,
            2024: 2542791,
            2025: 3188844,
        },
    ),
    (
        "Patrimonio total",
        r"Total patrimonio",
        {
            2020: 1196378,
            2021: 1517920,
            2022: 1594982,
            2023: 1645610,
            2024: 1883522,
            2025: 2206979,
        },
    ),
]

# Saldos comparativos que un estado posterior reexpresó (ver apartado 3.7 de la tesis):
# (partida, etiqueta, año del estado que muestra la cifra reexpresada, cifra)
REEXPRESADOS = [
    (
        "Cuentas por pagar comerciales 2022 (reexpresado)",
        r"Cuentas por pagar comerciales",
        2023,
        160155,
    ),
    (
        "Otras cuentas por cobrar 2024 (reexpresado)",
        r"Otras cuentas por cobrar",
        2025,
        98899,
    ),
]


def paginas_pdf(ruta):
    """Devuelve el texto de cada página del PDF."""
    if shutil.which("pdftotext"):
        txt = subprocess.run(
            ["pdftotext", "-layout", ruta, "-"],
            capture_output=True,
            text=True,
            errors="ignore",
        ).stdout
        pags = txt.split("\f")
        return pags[:-1] if pags and not pags[-1].strip() else pags
    from pypdf import PdfReader

    return [(p.extract_text() or "") for p in PdfReader(ruta).pages]


def pdf_por_anio(carpeta):
    """Agrupa los PDF por el año que figura en su nombre."""
    por_anio = {}
    for raiz, _, archivos in os.walk(carpeta):
        for a in sorted(archivos):
            if not a.lower().endswith(".pdf") or "eng" in a.lower():
                continue
            m = re.search(r"(20[12]\d)", a)
            if m:
                por_anio.setdefault(int(m.group(1)), []).append(os.path.join(raiz, a))
    return por_anio


cache = {}


def texto(ruta):
    if ruta not in cache:
        cache[ruta] = paginas_pdf(ruta)
    return cache[ruta]


def buscar(anio, etiqueta, cifra, por_anio):
    """Busca una página del año con la etiqueta y la cifra (con separador de miles)."""
    num = f"{cifra:,}"
    for ruta in por_anio.get(anio, []):
        for i, pag in enumerate(texto(ruta), 1):
            if re.search(etiqueta, pag, re.IGNORECASE) and re.search(
                rf"(?<![\d,]){re.escape(num)}(?![\d,])", pag
            ):
                return os.path.basename(ruta), i
    return None, None


def main():
    if not os.path.isdir(CARPETA):
        sys.exit(f"No se encontró la carpeta de estados financieros: {CARPETA!r}")
    por_anio = pdf_por_anio(CARPETA)
    faltan = [a for a in range(2020, 2026) if a not in por_anio]
    if faltan:
        sys.exit(f"Faltan PDF con estos años en el nombre del archivo: {faltan}")

    filas = []
    for nombre, etiqueta, valores in PARTIDAS:
        for anio, cifra in valores.items():
            # El saldo de 2019 se verifica en el estado de 2020, que trae la columna comparativa.
            origen = 2020 if anio == 2019 else anio
            arch, pag = buscar(origen, etiqueta, cifra, por_anio)
            filas.append(
                dict(
                    Anio=anio,
                    Partida=nombre,
                    Cifra=cifra,
                    Archivo=arch,
                    Pagina=pag,
                    Resultado="Encontrada" if arch else "NO ENCONTRADA",
                )
            )
    for nombre, etiqueta, anio_estado, cifra in REEXPRESADOS:
        arch, pag = buscar(anio_estado, etiqueta, cifra, por_anio)
        filas.append(
            dict(
                Anio=anio_estado,
                Partida=nombre,
                Cifra=cifra,
                Archivo=arch,
                Pagina=pag,
                Resultado="Encontrada" if arch else "NO ENCONTRADA",
            )
        )

    df = pd.DataFrame(filas)
    os.makedirs("resultados", exist_ok=True)
    df.to_csv("resultados/verificacion_cifras_eeff.csv", index=False)
    pd.set_option("display.width", 200)
    print(df.to_string(index=False))
    n_ok = (df["Resultado"] == "Encontrada").sum()
    print(f"\nCifras verificadas: {n_ok} de {len(df)}")
    if n_ok != len(df):
        sys.exit(1)


if __name__ == "__main__":
    main()
