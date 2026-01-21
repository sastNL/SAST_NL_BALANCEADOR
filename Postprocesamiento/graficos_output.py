import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


def heatmap_produccion(nombre_corrida, inicio_horizonte):
    """
    Heatmap de producción en miles de sacos por línea y planta.
    Guarda el gráfico como PNG en ruta_guardado.
    """

    ruta_excel = f"./Corridas/{nombre_corrida}/Resultados/soluciones_salida.xlsx"
    ruta_guardado = f"./Corridas/{nombre_corrida}/Resultados"

    # Leer datos
    df_produccion = pd.read_excel(ruta_excel, sheet_name="CANT_PRODUCIDA_SKU")
    df_produccion = df_produccion.rename(columns={"Value": "Produccion"})
    df_produccion["T"] = df_produccion["T"].astype(int)
    
    # ============================================
    # FILTRO: SOLO PRIMEROS 6 MESES (T=1 a T=6)
    # ============================================
    df_produccion = df_produccion[df_produccion["T"] <= 6]

    df_fl = pd.read_excel(ruta_excel, sheet_name="F_L")
    
    # Agrupar y unir con planta
    df_prod_agg = df_produccion.groupby(["L", "T"], as_index=False)["Produccion"].sum()
    df_prod_agg = df_prod_agg.merge(df_fl, on="L", how="left")
    df_prod_agg["Planta_Línea"] = df_prod_agg["F"] + " - " + df_prod_agg["L"]

    # Pivot para heatmap
    pivot_prod = df_prod_agg.pivot(index="Planta_Línea", columns="T", values="Produccion").fillna(0)

    # Etiquetas de meses 
    meses = sorted(pivot_prod.columns)
    cant_meses = len(meses)
    inicio_dt = datetime.strptime(inicio_horizonte, "%Y-%m")
    etiquetas_meses = [(inicio_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(cant_meses)]
    pivot_prod.columns = etiquetas_meses

    # Crear figura
    fig = plt.figure(figsize=(10,6))
    sns.heatmap(pivot_prod, cmap="Blues", annot=True, fmt=".1f", linewidths=0.5)
    plt.title("Producción en miles de sacos por línea y planta")
    plt.xlabel("Mes")
    plt.ylabel("Planta - Línea")

    # Guardar gráfico
    os.makedirs(ruta_guardado, exist_ok=True)
    fig.savefig(os.path.join(ruta_guardado, "heatmap_produccion.png"), bbox_inches="tight")

    return fig

def heatmap_utilizacion(nombre_corrida, inicio_horizonte):
    """
    Heatmap de % de utilización de capacidad por línea y planta.
    Calcula horas usadas como Produccion*1000/Velocidad y luego el %
    Guarda el gráfico como PNG en ruta_guardado.
    """
    ruta_excel = f"./Corridas/{nombre_corrida}/Resultados/soluciones_salida.xlsx"
    ruta_guardado = f"./Corridas/{nombre_corrida}/Resultados"

    # Leer datos
    # df_produccion = pd.read_excel(ruta_excel, sheet_name="CANT_PRODUCIDA_SKU")
    # df_produccion = df_produccion.rename(columns={"Value": "Produccion"})
    # df_produccion["T"] = df_produccion["T"].astype(int)
    
    # df_velocidad = pd.read_excel(ruta_excel, sheet_name="velocidad_produccion")
    # df_velocidad = df_velocidad.rename(columns={"Value": "Velocidad"})
    
    df_carga_linea = pd.read_excel(ruta_excel, sheet_name="CARGA_LINEA")
    df_carga_linea = df_carga_linea.rename(columns={"Value": "Carga"})
    df_carga_linea["T"] = df_carga_linea["T"].astype(int)
    
    df_carga_linea = df_carga_linea[df_carga_linea["T"] <= 6]
    
    df_capacidad = pd.read_excel(ruta_excel, sheet_name="capacidad_linea")
    df_capacidad = df_capacidad.rename(columns={"Value": "Capacidad"})
    df_capacidad["T"] = df_capacidad["T"].astype(int)
    
    df_capacidad = df_capacidad[df_capacidad["T"] <= 6]
    
    df_fl = pd.read_excel(ruta_excel, sheet_name="F_L")
    
    # Calcular horas usadas
    # df_util = df_produccion.merge(df_velocidad, on=["L", "SKU"], how="left")
    # df_util["Horas_usadas"] = df_util["Produccion"] * 1000 / df_util["Velocidad"]

    # # Agrupar por línea y mes
    # df_util_agg = df_util.groupby(["L","T"], as_index=False)["Horas_usadas"].sum()

    # # Unir con capacidad
    # df_util_agg = df_util_agg.merge(df_capacidad, on=["L","T"], how="left")
    
    # # Calcular % de utilización
    # df_util_agg["%Utilizacion"] = df_util_agg["Horas_usadas"] / df_util_agg["Capacidad"] * 100
    
    df_util_agg = df_carga_linea.merge(df_capacidad, on=["L", "T"], how="left")
    df_util_agg["%Utilizacion"] = (df_util_agg["Carga"] / df_util_agg["Capacidad"]) * 100

    # Unir con planta
    df_util_agg = df_util_agg.merge(df_fl, on="L", how="left")
    df_util_agg["Planta_Línea"] = df_util_agg["F"] + " - " + df_util_agg["L"]

    # Pivot
    pivot_util = df_util_agg.pivot(index="Planta_Línea", columns="T", values="%Utilizacion").fillna(0)

    # --- NUEVO: Etiquetas de meses ---
    # Determinar cantidad de meses
    meses = sorted(pivot_util.columns)
    cant_meses = len(meses)
    # Generar lista de etiquetas de meses
    inicio_dt = datetime.strptime(inicio_horizonte, "%Y-%m")
    etiquetas_meses = [(inicio_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(cant_meses)]
    # Asignar las etiquetas a las columnas
    pivot_util.columns = etiquetas_meses

    # Crear colormap personalizado
    colors = [(0, 'green'), (50/500, 'yellow'), (80/500, 'red'), (150/500, 'darkred'), (1, 'black')]  # Escala de 0 a 200%
    cmap_name = 'custom_utilization'
    custom_cmap = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=256)

    # Heatmap
    fig = plt.figure(figsize=(12,6))
    sns.heatmap(
        pivot_util,
        cmap=custom_cmap,
        annot=True, fmt=".1f",
        linewidths=0.5,
        vmin=0, vmax=500
    )
    plt.title("% de utilización de capacidad por línea y planta")
    plt.xlabel("Mes")
    plt.ylabel("Planta - Línea")

    # Guardar gráfico
    os.makedirs(ruta_guardado, exist_ok=True)
    fig.savefig(os.path.join(ruta_guardado, "heatmap_utilizacion.png"), bbox_inches="tight")

    return fig

def heatmap_produccion_planta(nombre_corrida, inicio_horizonte):
    """
    Heatmap de producción en miles de sacos por planta (agrupando todas las líneas).
    Guarda el gráfico como PNG en ruta_guardado.
    """
    ruta_excel = f"./Corridas/{nombre_corrida}/Resultados/soluciones_salida.xlsx"
    ruta_guardado = f"./Corridas/{nombre_corrida}/Resultados"

    # Leer datos
    df_produccion = pd.read_excel(ruta_excel, sheet_name="CANT_PRODUCIDA_SKU")
    df_produccion = df_produccion.rename(columns={"Value": "Produccion"})
    df_produccion["T"] = df_produccion["T"].astype(int)
    
    df_produccion = df_produccion[df_produccion["T"] <= 6]
    
    df_fl = pd.read_excel(ruta_excel, sheet_name="F_L")
    
    # Unir con planta y agrupar por planta y mes
    df_prod_planta = df_produccion.merge(df_fl, on="L", how="left")
    df_prod_agg = df_prod_planta.groupby(["F", "T"], as_index=False)["Produccion"].sum()

    # Pivot para heatmap
    pivot_prod = df_prod_agg.pivot(index="F", columns="T", values="Produccion").fillna(0)

    # Etiquetas de meses 
    meses = sorted(pivot_prod.columns)
    cant_meses = len(meses)
    inicio_dt = datetime.strptime(inicio_horizonte, "%Y-%m")
    etiquetas_meses = [(inicio_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(cant_meses)]
    pivot_prod.columns = etiquetas_meses

    # Crear figura
    fig = plt.figure(figsize=(12, 5))
    sns.heatmap(pivot_prod, cmap="Blues", annot=True, fmt=".1f", linewidths=0.5, cbar_kws={'label': 'Miles de sacos'})
    plt.title("Producción total por planta (miles de sacos)", fontsize=14, fontweight='bold')
    plt.xlabel("Mes", fontsize=12)
    plt.ylabel("Planta", fontsize=12)
    plt.tight_layout()

    # Guardar gráfico
    os.makedirs(ruta_guardado, exist_ok=True)
    fig.savefig(os.path.join(ruta_guardado, "heatmap_produccion_planta.png"), bbox_inches="tight", dpi=300)

    return fig


def grafico_barras_asignacion_planta(nombre_corrida, inicio_horizonte):
    """
    Gráfico de barras apiladas mostrando la asignación de producción por planta a lo largo del tiempo.
    Permite ver la distribución de producción entre plantas mes a mes.
    Guarda el gráfico como PNG en ruta_guardado.
    """
    ruta_excel = f"./Corridas/{nombre_corrida}/Resultados/soluciones_salida.xlsx"
    ruta_guardado = f"./Corridas/{nombre_corrida}/Resultados"

    # Leer datos
    df_produccion = pd.read_excel(ruta_excel, sheet_name="CANT_PRODUCIDA_SKU")
    df_produccion = df_produccion.rename(columns={"Value": "Produccion"})
    df_produccion["T"] = df_produccion["T"].astype(int)
    
    df_produccion = df_produccion[df_produccion["T"] <= 6]
    
    df_fl = pd.read_excel(ruta_excel, sheet_name="F_L")
    
    # Unir con planta y agrupar por planta y mes
    df_prod_planta = df_produccion.merge(df_fl, on="L", how="left")
    df_prod_agg = df_prod_planta.groupby(["F", "T"], as_index=False)["Produccion"].sum()

    # Pivot para gráfico de barras
    pivot_prod = df_prod_agg.pivot(index="T", columns="F", values="Produccion").fillna(0)

    # Etiquetas de meses 
    meses = sorted(pivot_prod.index)
    cant_meses = len(meses)
    inicio_dt = datetime.strptime(inicio_horizonte, "%Y-%m")
    etiquetas_meses = [(inicio_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(cant_meses)]
    pivot_prod.index = etiquetas_meses

    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfico 1: Barras apiladas
    pivot_prod.plot(kind='bar', stacked=True, ax=ax1, colormap='Set3', edgecolor='black', linewidth=0.5)
    ax1.set_title("Asignación de producción por planta (apilado)", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Mes", fontsize=12)
    ax1.set_ylabel("Producción (miles de sacos)", fontsize=12)
    ax1.legend(title="Planta", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(axis='y', alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico 2: Barras agrupadas (para comparar plantas lado a lado)
    pivot_prod.plot(kind='bar', stacked=False, ax=ax2, colormap='Set3', edgecolor='black', linewidth=0.5)
    ax2.set_title("Comparación de producción por planta", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Mes", fontsize=12)
    ax2.set_ylabel("Producción (miles de sacos)", fontsize=12)
    ax2.legend(title="Planta", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()

    # Guardar gráfico
    os.makedirs(ruta_guardado, exist_ok=True)
    fig.savefig(os.path.join(ruta_guardado, "asignacion_produccion_planta.png"), bbox_inches="tight", dpi=300)

    return fig


def heatmap_utilizacion_planta(nombre_corrida, inicio_horizonte):
    """
    Heatmap de % de utilización de capacidad agregada por planta.
    Suma la carga y capacidad de todas las líneas de cada planta.
    Guarda el gráfico como PNG en ruta_guardado.
    """
    ruta_excel = f"./Corridas/{nombre_corrida}/Resultados/soluciones_salida.xlsx"
    ruta_guardado = f"./Corridas/{nombre_corrida}/Resultados"

    # Leer datos
    df_carga_linea = pd.read_excel(ruta_excel, sheet_name="CARGA_LINEA")
    df_carga_linea = df_carga_linea.rename(columns={"Value": "Carga"})
    df_carga_linea["T"] = df_carga_linea["T"].astype(int)
    
    df_carga_linea = df_carga_linea[df_carga_linea["T"] <= 6]
    
    df_capacidad = pd.read_excel(ruta_excel, sheet_name="capacidad_linea")
    df_capacidad = df_capacidad.rename(columns={"Value": "Capacidad"})
    df_capacidad["T"] = df_capacidad["T"].astype(int)
    
    df_capacidad = df_capacidad[df_capacidad["T"] <= 6]
    
    df_fl = pd.read_excel(ruta_excel, sheet_name="F_L")
    
    # Unir con planta
    df_carga_planta = df_carga_linea.merge(df_fl, on="L", how="left")
    df_capacidad_planta = df_capacidad.merge(df_fl, on="L", how="left")
    
    # Agrupar por planta y mes
    df_carga_agg = df_carga_planta.groupby(["F", "T"], as_index=False)["Carga"].sum()
    df_capacidad_agg = df_capacidad_planta.groupby(["F", "T"], as_index=False)["Capacidad"].sum()
    
    # Calcular utilización
    df_util_agg = df_carga_agg.merge(df_capacidad_agg, on=["F", "T"], how="left")
    df_util_agg["%Utilizacion"] = (df_util_agg["Carga"] / df_util_agg["Capacidad"]) * 100

    # Pivot
    pivot_util = df_util_agg.pivot(index="F", columns="T", values="%Utilizacion").fillna(0)

    # Etiquetas de meses
    meses = sorted(pivot_util.columns)
    cant_meses = len(meses)
    inicio_dt = datetime.strptime(inicio_horizonte, "%Y-%m")
    etiquetas_meses = [(inicio_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(cant_meses)]
    pivot_util.columns = etiquetas_meses

    # Crear colormap personalizado
    colors = [(0, 'green'), (50/500, 'yellow'), (80/500, 'red'), (150/500, 'darkred'), (1, 'black')]
    cmap_name = 'custom_utilization'
    custom_cmap = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=256)

    # Heatmap
    fig = plt.figure(figsize=(12, 5))
    sns.heatmap(
        pivot_util,
        cmap=custom_cmap,
        annot=True, fmt=".1f",
        linewidths=0.5,
        vmin=0, vmax=500,
        cbar_kws={'label': '% Utilización'}
    )
    plt.title("% de utilización de capacidad por planta", fontsize=14, fontweight='bold')
    plt.xlabel("Mes", fontsize=12)
    plt.ylabel("Planta", fontsize=12)
    plt.tight_layout()

    # Guardar gráfico
    os.makedirs(ruta_guardado, exist_ok=True)
    fig.savefig(os.path.join(ruta_guardado, "heatmap_utilizacion_planta.png"), bbox_inches="tight", dpi=300)

    return fig