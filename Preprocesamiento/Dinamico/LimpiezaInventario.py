import pandas as pd

def limpieza_inventario_inicial(nombre_corrida):
    
    df_inventario_inicial = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Inventario inicial', usecols='C:F', skiprows = 2)

    # Que las columnas COD_SKU_SIN_V, PLANTA e INVENTARIO_DISPONIBLE no tengan valores nulos. Armar archivo de errores
    df_inventario_errores_columnas_vacias = df_inventario_inicial[(df_inventario_inicial['COD_SKU_SIN_V'].isna()) | (df_inventario_inicial['PLANTA'].isna()) | (df_inventario_inicial['INVENTARIO_DISPONIBLE'].isna())]
    df_inventario_errores_columnas_vacias['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas (COD_SKU_SIN_V, PLANTA, INVENTARIO_DISPONIBLE)'

    df_inventario_inicial = df_inventario_inicial[df_inventario_inicial['COD_SKU_SIN_V'].notna()]
    df_inventario_inicial = df_inventario_inicial[df_inventario_inicial['PLANTA'].notna()]
    df_inventario_inicial = df_inventario_inicial[df_inventario_inicial['INVENTARIO_DISPONIBLE'].notna()]

    # Que los datos en COD_SKU_SIN_V, DESCRIPCION_SKU, PLANTA sean string, y que INVENTARIO_DISPONIBLE sea float
    df_inventario_inicial['COD_SKU_SIN_V'] = df_inventario_inicial['COD_SKU_SIN_V'].astype(str)
    df_inventario_inicial['DESCRIPCION_SKU'] = df_inventario_inicial['DESCRIPCION_SKU'].astype(str)
    df_inventario_inicial['PLANTA'] = df_inventario_inicial['PLANTA'].astype(str)
    
    # Guardar valores originales antes de la conversión
    df_inventario_inicial['INVENTARIO_ORIGINAL'] = df_inventario_inicial['INVENTARIO_DISPONIBLE']

    # Para INVENTARIO_DISPONIBLE: conversión segura
    df_inventario_inicial['INVENTARIO_DISPONIBLE'] = pd.to_numeric(
        df_inventario_inicial['INVENTARIO_DISPONIBLE'], 
        errors='coerce'  # Convierte valores inválidos a NaN
    )
    # Identificar errores de conversión (donde se convirtió a NaN)
    df_inventario_errores_conversion = df_inventario_inicial[
        df_inventario_inicial['INVENTARIO_DISPONIBLE'].isna()
    ].copy()
    
    if not df_inventario_errores_conversion.empty:
        df_inventario_errores_conversion['MOTIVO_ERROR'] = 'INVENTARIO_DISPONIBLE no es numérico: ' + df_inventario_errores_conversion['INVENTARIO_ORIGINAL'].astype(str)
        
    # Eliminar columna auxiliar del dataset limpio
    df_inventario_inicial = df_inventario_inicial.drop(columns=['INVENTARIO_ORIGINAL'])

    # Eliminar columna auxiliar del dataset de errores
    df_inventario_errores_conversion.drop(columns=['INVENTARIO_DISPONIBLE'], inplace=True)
    df_inventario_errores_conversion.rename(columns={'INVENTARIO_ORIGINAL': 'INVENTARIO_DISPONIBLE'}, inplace=True)

    df_inventario_inicial.dropna(subset=['INVENTARIO_DISPONIBLE'], inplace=True)
    
    # Determinar que INVENTARIO_DISPONIBLE sea mayor o igual a 0
    df_inventario_errores_inventario_negativo = df_inventario_inicial[df_inventario_inicial['INVENTARIO_DISPONIBLE'] < 0].copy()
    if not df_inventario_errores_inventario_negativo.empty:
        df_inventario_errores_inventario_negativo['MOTIVO_ERROR'] = 'INVENTARIO_DISPONIBLE es negativo'
    df_inventario_inicial = df_inventario_inicial[df_inventario_inicial['INVENTARIO_DISPONIBLE'] >= 0]
    
    # Eliminar duplicados
    df_inventario_inicial.drop_duplicates(inplace = True)
    df_inventario_inicial = df_inventario_inicial[~df_inventario_inicial.duplicated(subset=['COD_SKU_SIN_V', 'PLANTA'], keep='first')]

    # Unificar errores
    df_inventario_errores = pd.concat([
        df_inventario_errores_columnas_vacias,
        df_inventario_errores_conversion,
        df_inventario_errores_inventario_negativo
    ], ignore_index=True)
    
    # Exportar a excel
    df_inventario_errores.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_inventario_inicial.xlsx', index=False)
    df_inventario_inicial.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_inventario_inicial.xlsx', index=False)
