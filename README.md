# Código de la tesis sobre capital de trabajo y rentabilidad de Compañía Minera Poderosa S.A. (2020-2025)

Este repositorio reúne el código y los datos con los que se hicieron los cálculos de la tesis *Gestión del capital de trabajo y su relación con la rentabilidad de Compañía Minera Poderosa S.A., 2020-2025*, presentada en la Facultad de Negocios de la Universidad Privada del Norte (Trujillo, 2026).

Autor: Eder Cedano Bustos.

Cualquier persona puede repetir el análisis y comprobar que las tablas de la tesis salen de estos datos.

## Qué contiene

| Ruta | Contenido |
|---|---|
| `src/01_analisis_estadistico.py` | Anexo 4 de la tesis. Calcula PPI, PPC, PPP, CCE, ROA y ROE, la estadística descriptiva, la prueba de Shapiro-Wilk y las correlaciones de Pearson o Spearman. Genera las Tablas 1 a 5 y las Figuras 1 y 2. |
| `src/02_analisis_sensibilidad.py` | Anexo 6 de la tesis. Intervalos de confianza, Spearman, ajuste de Holm, exclusión de un año a la vez, primeras diferencias y descomposición del PPC. Genera las Tablas 6 a 9. |
| `src/03_verificacion_cifras_eeff.py` | Comprueba que cada cifra de base aparece, con su nombre de partida, en una página del estado financiero auditado del mismo año. Indica archivo y página. |
| `EEFF Poderosa 2020-2025/` | PDF de los estados financieros separados auditados (fuente SMV), que lee el script 03. |
| `data/Ficha_Registro_Datos_Poderosa.xlsx` | Ficha de registro de datos. Incluye una hoja que contrasta cada cifra con la página del estado financiero auditado. |
| `resultados/` | Salidas de ambos scripts (tablas en CSV, figuras en PNG y el texto que imprime cada script). |

## Cómo ejecutarlo

Se necesita Python 3.11 o superior.

```bash
pip install -r requirements.txt
python src/01_analisis_estadistico.py
python src/02_analisis_sensibilidad.py
python src/03_verificacion_cifras_eeff.py "EEFF Poderosa 2020-2025"
```

Ejecuta los comandos desde la carpeta raíz del repositorio. El primer script crea la carpeta `resultados/` si no existe. El segundo imprime sus tablas en pantalla; para guardarlas:

```bash
python src/02_analisis_sensibilidad.py > resultados/salida_02_analisis_sensibilidad.txt
```

El script 03 necesita que los PDF tengan el año en el nombre (por ejemplo `estados-financieros-2023.pdf`), y guarda su resultado en `resultados/verificacion_cifras_eeff.csv`. Termina con error si alguna cifra no aparece.

Los resultados incluidos en `resultados/` se generaron con Python 3.12, numpy 2.4, pandas 3.0, scipy 1.17, matplotlib 3.10 y seaborn 0.13.

## Datos

Las cifras provienen de los estados financieros separados auditados de Compañía Minera Poderosa S.A. de los ejercicios 2020 a 2025, publicados en el portal de la Superintendencia del Mercado de Valores (SMV). Están en miles de soles. El saldo de 2019 solo se usa como apertura para calcular los saldos promedio de 2020.

Las cifras están escritas en los propios scripts, igual que en los Anexos 4 y 6 de la tesis, y se encuentran ordenadas por año en la ficha de la carpeta `data/`.

Criterios de cálculo:

- PPI, PPC y PPP usan saldos promedio (saldo inicial más saldo final, dividido entre 2) y una base de 360 días.
- ROA y ROE usan el saldo de cierre de cada ejercicio.
- Cada saldo es el que reportó el estado financiero de su propio cierre. Dos saldos comparativos fueron reexpresados en estados posteriores (cuentas por pagar comerciales de 2022 y otras cuentas por cobrar de 2024). El efecto se evalúa en el apartado 3.7 de la tesis.

## Resultados principales

Con seis observaciones anuales, solo el período promedio de cobro (PPC) muestra una correlación negativa significativa con el ROA (r = -0.859; p = 0.028) y con el ROE (r = -0.816; p = 0.048). Esa asociación no resiste el ajuste de Holm y proviene sobre todo de las otras cuentas por cobrar, no de las cuentas comerciales. El detalle está en los capítulos 3 y 4 de la tesis.

## Limitaciones

El estudio analiza una sola empresa durante seis años. Las correlaciones se leen como asociaciones y no como causalidad.

## Cómo citar

Cedano Bustos, E. (2026). *Gestión del capital de trabajo y su relación con la rentabilidad de Compañía Minera Poderosa S.A., 2020-2025* [Tesis de pregrado, Universidad Privada del Norte].

## Licencia

Código bajo licencia MIT (archivo `LICENSE`). Los estados financieros originales pertenecen a la empresa y están disponibles públicamente en la SMV.
