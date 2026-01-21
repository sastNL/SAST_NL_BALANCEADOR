import pandas as pd
from unidecode import unidecode

def limpieza_datos_distribucion(nombre_corrida):

    ## COSTOS DISTRIBUCION
    df_costo_distribucion = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Costo distribucion', usecols='C:H', skiprows = 2)
    df_costo_distribucion['COSTO (US$/SACO)'] = pd.to_numeric(df_costo_distribucion['COSTO (US$/SACO)'],errors='coerce')
    # Crear DataFrame con errores antes de la limpieza
    df_errores_costo_distribucion_VALORES_NULOS = df_costo_distribucion[df_costo_distribucion[['ID_PLANTA', 'SKU_SIN_VERSION', 'ID_CLIENTE', 'COSTO (US$/SACO)']].isna().any(axis=1)].copy()
    df_errores_costo_distribucion_VALORES_NULOS['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas (ID_PLANTA, SKU_SIN_VERSION, ID_CLIENTE, COSTO (US$/SACO))'
    df_errores_costo_distribucion = df_errores_costo_distribucion_VALORES_NULOS
    # Dropear nans
    df_costo_distribucion = df_costo_distribucion.dropna(subset=['ID_PLANTA', 'SKU_SIN_VERSION', 'ID_CLIENTE', 'COSTO (US$/SACO)'], how='any')
    # Chequear que el costo sea mayor que 0
    df_errores_costo_distribucion_COSTO_ERRONEO = df_costo_distribucion[df_costo_distribucion['COSTO (US$/SACO)'] <= 0]
    df_errores_costo_distribucion_COSTO_ERRONEO['MOTIVO_ERROR'] = 'Costo erróneo (menor o igual a 0)'
    df_errores_costo_distribucion = pd.concat([df_errores_costo_distribucion, df_errores_costo_distribucion_COSTO_ERRONEO], ignore_index=True)
    df_costo_distribucion = df_costo_distribucion[df_costo_distribucion['COSTO (US$/SACO)'] > 0]
    # Eliminar duplicados
    df_costo_distribucion = df_costo_distribucion.drop_duplicates()
    
    ## TIEMPOS DE TRANSITO
    df_tiempo_transito = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Tiempos de transito', usecols='C:F', skiprows = 2)
    # Crear DataFrame con errores antes de la limpieza
    df_errores_tiempo_transito_VALORES_NULOS = df_tiempo_transito[df_tiempo_transito[['ID_PLANTA', 'ID_CLIENTE', 'DIAS_TRANSITO']].isna().any(axis=1)].copy()
    df_errores_tiempo_transito_VALORES_NULOS['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas (ID_PLANTA, ID_CLIENTE, DIAS_TRANSITO)'
    df_errores_tiempo_transito = df_errores_tiempo_transito_VALORES_NULOS
    # Dropear nans
    df_tiempo_transito = df_tiempo_transito.dropna(subset=['ID_PLANTA', 'ID_CLIENTE', 'DIAS_TRANSITO'], how='any')
    # Chequear que el tiempo sea mayor que 0
    df_errores_tiempo_transito_TIEMPO_ERRONEO = df_tiempo_transito[df_tiempo_transito['DIAS_TRANSITO'] <= 0]
    df_errores_tiempo_transito_TIEMPO_ERRONEO['MOTIVO_ERROR'] = 'Tiempo de transito erróneo (menor o igual a 0)'
    df_errores_tiempo_transito = pd.concat([df_errores_tiempo_transito, df_errores_tiempo_transito_TIEMPO_ERRONEO], ignore_index=True)
    df_tiempo_transito = df_tiempo_transito[df_tiempo_transito['DIAS_TRANSITO'] > 0]
    # Eliminar duplicados
    df_tiempo_transito = df_tiempo_transito.drop_duplicates()
    df_tiempo_transito['MESES_TRANSITO'] = pd.cut(df_tiempo_transito['DIAS_TRANSITO'], bins=[0, 30, 60, 90, 120, 150, 180], labels=[0, 1, 2, 3, 4, 5], right=False)
    
    df_tiempo_transito['MESES_TRANSITO'] = df_tiempo_transito['MESES_TRANSITO'].astype(dtype=int)
    
    
    ## ARANCELES
    df_aranceles = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Aranceles', usecols='C:AN', skiprows=2)
    
    # Obtener todas las columnas que son países (excluyendo 'PAIS ORIGEN' y 'PLANTA')
    columnas_paises = [col for col in df_aranceles.columns if col not in ['PAIS ORIGEN', 'PLANTA']]
    
    # Aplicar melt para convertir las columnas de países en filas
    df_aranceles_melted = pd.melt(
        df_aranceles,
        id_vars=['PAIS ORIGEN', 'PLANTA'],
        value_vars=columnas_paises,
        var_name='PAIS_DESTINO',
        value_name='ARANCEL'
    )
    
    # Convertir PAIS DESTINO a mayúsculas sin acentos
    df_aranceles_melted['PAIS_DESTINO'] = df_aranceles_melted['PAIS_DESTINO'].apply(lambda x: unidecode(str(x)).upper())
    
    # Crear reporte de errores de aranceles
    df_errores_aranceles = pd.DataFrame()
    
    # Guardar valores originales para reporte de errores
    df_aranceles_melted['ARANCEL_ORIGINAL'] = df_aranceles_melted['ARANCEL']
    
    # Limpiar aranceles: quitar '%' si está presente
    df_aranceles_melted['ARANCEL'] = df_aranceles_melted['ARANCEL'].astype(str).str.replace('%', '', regex=False)
    
    # Convertir a numérico
    df_aranceles_melted['ARANCEL'] = pd.to_numeric(df_aranceles_melted['ARANCEL'], errors='coerce')
    
    # Identificar errores por valores no numéricos (que se convirtieron a NaN)
    df_errores_aranceles_no_numerico = df_aranceles_melted[df_aranceles_melted['ARANCEL'].isna()].copy()
    if not df_errores_aranceles_no_numerico.empty:
        df_errores_aranceles_no_numerico['MOTIVO_ERROR'] = 'Arancel no numérico'
        df_errores_aranceles = pd.concat([df_errores_aranceles, df_errores_aranceles_no_numerico], ignore_index=True)
    
    # Identificar errores por valores negativos
    df_errores_aranceles_negativo = df_aranceles_melted[df_aranceles_melted['ARANCEL'] < 0].copy()
    if not df_errores_aranceles_negativo.empty:
        df_errores_aranceles_negativo['MOTIVO_ERROR'] = 'Arancel negativo'
        df_errores_aranceles = pd.concat([df_errores_aranceles, df_errores_aranceles_negativo], ignore_index=True)
    
    # Filtrar aranceles válidos (>= 0 y no nulos)
    df_aranceles_clean = df_aranceles_melted[
        (df_aranceles_melted['ARANCEL'].notnull()) & 
        (df_aranceles_melted['ARANCEL'] >= 0)
    ].copy()
    
    # Eliminar columna auxiliar del dataset limpio
    df_aranceles_clean = df_aranceles_clean.drop(columns=['ARANCEL_ORIGINAL'])

    # Unificar errores en un solo DataFrame
    df_errores_limpieza_distribucion = pd.concat([
        df_errores_costo_distribucion_VALORES_NULOS,
        df_errores_costo_distribucion_COSTO_ERRONEO,
        df_errores_tiempo_transito_VALORES_NULOS,
        df_errores_tiempo_transito_TIEMPO_ERRONEO,
        df_errores_aranceles
    ], ignore_index=True)

    df_costo_distribucion.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costo_distribucion.xlsx', index=False)
    df_tiempo_transito.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_tiempo_transito.xlsx', index=False)
    df_aranceles_clean.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_aranceles.xlsx', index=False)
    df_errores_limpieza_distribucion.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_limpieza_distribucion.xlsx', index=False)

    return df_costo_distribucion, df_tiempo_transito, df_aranceles_clean, df_errores_limpieza_distribucion