import pandas as pd

def limpieza_costos_produccion(nombre_corrida):

    ## Costo fijo por línea
    df_costos_fijos_lineas = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Costo fijo produccion', skiprows = 2, usecols = 'C:F')
    
    ## Costos indirectos
    df_costos_indirectos = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Costo produccion indirecto', skiprows = 2, usecols = 'C:F')
    
    # Que no haya filas con valores nan y armar reporte de errores
    df_errores_costos_indirectos = df_costos_indirectos[df_costos_indirectos.isna().any(axis=1)]
    df_errores_costos_indirectos['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas'
    df_costos_indirectos = df_costos_indirectos.dropna()
    
    # Intentar convertir volumen y costos a float
    df_costos_indirectos['VOLUMEN (M SACOS)'] = pd.to_numeric(df_costos_indirectos['VOLUMEN (M SACOS)'], errors='coerce')
    df_costos_indirectos['COSTO INDIRECTO (MUS$)'] = pd.to_numeric(df_costos_indirectos['COSTO INDIRECTO (MUS$)'], errors='coerce')

    # Primero si las columnas VOLUMEN (M SACOS) y COSTO INDIRECTO (MUS$) no son float, sacar y meter en reporte errores
    df_errores_costos_indirectos_no_float = df_costos_indirectos[(~df_costos_indirectos['VOLUMEN (M SACOS)'].apply(lambda x: isinstance(x, float))) | (~df_costos_indirectos['COSTO INDIRECTO (MUS$)'].apply(lambda x: isinstance(x, float)))]
    df_errores_costos_indirectos_no_float['MOTIVO_ERROR'] = 'Valores no numéricos en VOLUMEN y/o COSTO INDIRECTO'
    df_errores_costos_indirectos = pd.concat([df_errores_costos_indirectos, df_errores_costos_indirectos_no_float])

    df_costos_indirectos = df_costos_indirectos[(df_costos_indirectos['VOLUMEN (M SACOS)'].apply(lambda x: isinstance(x, float))) & (df_costos_indirectos['COSTO INDIRECTO (MUS$)'].apply(lambda x: isinstance(x, float)))]

    # Que el volumen y los costo sean mayores a 0
    df_errores_costos_indirectos_no_positivos = df_costos_indirectos[(df_costos_indirectos['VOLUMEN (M SACOS)'] <= 0) | (df_costos_indirectos['COSTO INDIRECTO (MUS$)'] <= 0)]
    df_errores_costos_indirectos_no_positivos['MOTIVO_ERROR'] = 'Valores no positivos en VOLUMEN y/o COSTO INDIRECTO'
    df_errores_costos_indirectos = pd.concat([df_errores_costos_indirectos, df_errores_costos_indirectos_no_positivos])

    df_costos_indirectos = df_costos_indirectos[(df_costos_indirectos['VOLUMEN (M SACOS)'] > 0) & (df_costos_indirectos['COSTO INDIRECTO (MUS$)'] > 0)]
    
    # Calcular costo como US$ / saco
    df_costos_indirectos['COSTO INDIRECTO (US$/SACO)'] = df_costos_indirectos['COSTO INDIRECTO (MUS$)'] / df_costos_indirectos['VOLUMEN (M SACOS)']
    
    # Eliminar columnas VOLUMEN y COSTO INDIRECTO
    df_costos_indirectos.drop(columns=['VOLUMEN (M SACOS)', 'COSTO INDIRECTO (MUS$)'], inplace=True)
    
    # Calculo de COD_SKU_SIN_V solo considerando la parte izquiera antes del "-" si lo hubiera, y renombrar SKU a COD_SKU
    df_costos_indirectos['COD_SKU'] = df_costos_indirectos['SKU']
    df_costos_indirectos.drop(columns=['SKU'], inplace=True)
    df_costos_indirectos['COD_SKU_SIN_V'] = df_costos_indirectos['COD_SKU'].apply(lambda x: x.split('-')[0] if '-' in x else x)

    df_costos_indirectos = df_costos_indirectos[[
        'COD_SKU', 'COD_SKU_SIN_V', 'DESCRIPCION_SKU', 'COSTO INDIRECTO (US$/SACO)'
    ]]
    
    # Eliminar duplicados
    df_costos_indirectos.drop_duplicates(inplace=True)

    # Exportar a Excel
    df_costos_indirectos.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costos_indirectos.xlsx')
    df_errores_costos_indirectos.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_costos_indirectos.xlsx')

    #################################################
    # Costo fijo por línea
    #chequear que el costo sea mayor a 0
    df_costos_fijos_lineas = df_costos_fijos_lineas[df_costos_fijos_lineas['COSTO_TOTAL_LINEA'] > 0]
    # Exportar a Excel
    df_costos_fijos_lineas.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costos_fijos_lineas.xlsx')