import pandas as pd
import numpy as np


def limpieza_materia_prima():
    """Limpieza de la materia prima.
    """
    df_materia_prima = pd.read_excel('ResultadosEstaticos/Inputs/Materia prima/Materia prima.xlsx', sheet_name = 'MMPP_PLANTA', usecols = 'A:S')
    df_costos_abastecimiento = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Costos abastecimiento', skiprows=2, usecols='C:I')
    #Cambio de nombres de columnas
    df_materia_prima['COD_MP']  = df_materia_prima['Material'] 
    
    df_materia_prima['DESCRIPCION']  = df_materia_prima['Texto breve de material'] 
    df_materia_prima['COD_MP_CORTO']  = df_materia_prima['PB Corto']
    
    #Las filas que correspondan a PLANTA=SKAR deben eliminarse
    df_materia_prima = df_materia_prima[df_materia_prima['PLANTA'] != 'SKAR']
    
    #Si en DESCRIPCION aparece 'Duplicado', 'Nulo', 'Malo, (alguna de esas palabras y sin distringuir entre may y min) eliminar toda la fila
    df_materia_prima = df_materia_prima[~df_materia_prima['DESCRIPCION'].str.contains('Duplicado|Nulo|Malo', case=False, na=False)]
    
    #Filtrar PLANTA=SKBR y CO_MP y no comienza con 'PK' o PLANTA=SKCL, SKMX, SKPE y COD_MP y comienza con 'PB'
    # df_materia_prima = df_materia_prima[
    #     ((df_materia_prima['PLANTA'] == 'SKBR') & (df_materia_prima['COD_MP'].str.startswith('PK'))) |
    #     ((df_materia_prima['PLANTA'].isin(['SKCL', 'SKMX', 'SKPE'])) & (df_materia_prima['COD_MP'].str.startswith('PB')))
    # ]

    #Si PROVEEDOR es 'SMURFITKAPPA', reescribir esa misma celda a 'SMURFIT'
    df_materia_prima.loc[df_materia_prima['PROVEEDOR'] == 'SMURFITKAPPA', 'PROVEEDOR'] = 'SMURFIT'
    
    df_materia_prima = df_materia_prima[[
        'PLANTA', 'COD_MP', 'DESCRIPCION', 'PAPEL/FILM/MANGA', 'COLOR', 'EXT-LISO-CAÑO', 'GRAMAJE', 'PROVEEDOR',
        'ANCHO', 'COD_MP_CORTO'
    ]]
    
    # 🔹 Duplicar filas para ciertas plantas
    # SKBR -> SKBR-CN y SKBR-PS
    df_skbr = df_materia_prima[df_materia_prima['PLANTA'] == 'SKBR']
    if not df_skbr.empty:
        df_skbr_cn = df_skbr.copy()
        df_skbr_cn['PLANTA'] = 'SKBR-CN'
        df_skbr_ps = df_skbr.copy()
        df_skbr_ps['PLANTA'] = 'SKBR-PS'
        df_materia_prima = df_materia_prima[df_materia_prima['PLANTA'] != 'SKBR']
        df_materia_prima = pd.concat([df_materia_prima, df_skbr_cn, df_skbr_ps], ignore_index=True)

    # SKMX -> SKMX-I y SKMX-G
    df_skmx = df_materia_prima[df_materia_prima['PLANTA'] == 'SKMX']
    if not df_skmx.empty:
        df_skmx_i = df_skmx.copy()
        df_skmx_i['PLANTA'] = 'SKMX-I'
        df_skmx_g = df_skmx.copy()
        df_skmx_g['PLANTA'] = 'SKMX-G'
        df_materia_prima = df_materia_prima[df_materia_prima['PLANTA'] != 'SKMX']
        df_materia_prima = pd.concat([df_materia_prima, df_skmx_i, df_skmx_g], ignore_index=True)

    # Clasificar gramaje temporalmente
    df_materia_prima['TMP'] = df_materia_prima['GRAMAJE'].apply(lambda x: '≤70' if x <= 70 else '>70')
    df_costos_abastecimiento['TMP'] = df_costos_abastecimiento['GRAMAJE'].apply(lambda x: '≤70' if x <= 70 else '>70')

    # Reorganizar tabla de costos (PLANTA en una sola columna)
    costos = df_costos_abastecimiento.melt(
        id_vars=['PROVEEDOR', 'PAPEL/FILM/MANGA', 'COLOR', 'EXT-LISO-CAÑO', 'TMP', 'COSTO (USD/TON)'],
        value_vars=['PLANTA SK'],
        var_name='_', value_name='PLANTA'
    )

    # Merge sin dejar columnas auxiliares
    df_materia_prima = df_materia_prima.merge(
        costos,
        how='left',
        on=['PLANTA', 'PAPEL/FILM/MANGA', 'COLOR', 'EXT-LISO-CAÑO', 'TMP', 'PROVEEDOR']
    ).drop(columns=['TMP', '_'])

    # Renombrar columna de costo
    df_materia_prima.rename(columns={'COSTO (USD/TON)': 'COSTO ABASTECIMIENTO (USD/TON)'}, inplace=True)

    # Eliminar filas duplicadas en todas las columnas
    df_materia_prima = df_materia_prima.drop_duplicates()
    
    #Convertir df_ficha_tecnica_multiwall_chile a excel
    df_materia_prima.to_excel('ResultadosEstaticos/Resultados/df_materia_prima.xlsx', index=False)
    
    return df_materia_prima