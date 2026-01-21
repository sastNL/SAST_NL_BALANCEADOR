import pandas as pd
import numpy as np

def limpieza_ficha_tecnica():
    """Limpieza de la ficha técnica de los productos.
    """
    
    df_ficha_tecnica_multiwall_chile = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Chile Original.xlsx', sheet_name = 'Fichas Técnicas Multiwall SKCL', usecols = 'A:UV')
    df_ficha_tecnica_preimpresos_chile = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Chile Original.xlsx', sheet_name = 'Fichas Técnicas Preimpresos SKC', usecols = 'A:NB')[['COD_MATERIAL', 'B20CODIGOSAP115']].rename(columns={'COD_MATERIAL': 'COD_PREIMPRESO','B20CODIGOSAP115': 'CODIGO_MP'})
    
    df_ficha_tecnica_multiwall_peru = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Peru Original.xlsx', sheet_name = 'Fichas Técnicas Multiwall SKPE', usecols = 'A:QO')
    df_ficha_tecnica_preimpresos_peru = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Peru Original.xlsx', sheet_name = 'Fichas Técnicas Preimpresos SKP', usecols = 'A:EF')[['COD_MATERIAL', 'B20CODIGOSAP115']].rename(columns={'COD_MATERIAL': 'COD_PREIMPRESO','B20CODIGOSAP115': 'CODIGO_MP'})
    
    df_ficha_tecnica_multiwall_mexico_1 = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Mexico Original.xlsx', sheet_name = 'Fichas Técnicas Multiwall SKMX', usecols = 'A:QV')
    df_ficha_tecnica_multiwall_mexico_2 = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Mexico Original.xlsx', sheet_name = 'Fichas Técnicas Multiwall S (2)', usecols = 'A:NX')
    df_ficha_tecnica_preimpresos_mexico_1 = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Mexico Original.xlsx', sheet_name = 'Fichas Técnicas Preimpresos SKM', usecols = 'A:EL')[['COD_MATERIAL', 'B20CODIGOSAP115']].rename(columns={'COD_MATERIAL': 'COD_PREIMPRESO','B20CODIGOSAP115': 'CODIGO_MP'})
    df_ficha_tecnica_preimpresos_mexico_2 = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Ficha tecnica Mexico Original.xlsx', sheet_name = 'Fichas Técnicas Preimpresos (2)', usecols = 'A:DM')[['COD_MATERIAL', 'B20CODIGOSAP115']].rename(columns={'COD_MATERIAL': 'COD_PREIMPRESO','B20CODIGOSAP115': 'CODIGO_MP'})
    
    df_ficha_tecnica = pd.concat([df_ficha_tecnica_multiwall_chile, df_ficha_tecnica_multiwall_peru, df_ficha_tecnica_multiwall_mexico_1, df_ficha_tecnica_multiwall_mexico_2], ignore_index=True)
    df_ficha_tecnica_preimpresos = pd.concat([df_ficha_tecnica_preimpresos_chile, df_ficha_tecnica_preimpresos_peru, df_ficha_tecnica_preimpresos_mexico_1, df_ficha_tecnica_preimpresos_mexico_2], ignore_index=True)
    
    df_ficha_tecnica_materia_prima = pd.read_excel('ResultadosEstaticos/Resultados/df_materia_prima.xlsx', usecols=['COD_MP', 'GRAMAJE'])
    # df_ficha_tecnica_materia_prima['COD_MP'] = df_ficha_tecnica_materia_prima['COD_MP'].apply(
    # lambda x: str(x).strip() if pd.notna(x) else '')   
    
    df_clientes = pd.read_excel('ResultadosEstaticos/Resultados/df_clientes.xlsx', usecols=['ID_CLIENTE', 'PAIS_DESTINO']).rename(columns={'ID_CLIENTE': 'COD_CLIENTE'}).drop_duplicates()
    df_codigos_clientes = pd.read_excel('ResultadosEstaticos/Resultados/df_codigos_clientes.xlsx').drop_duplicates()

    #Eliminar filas COD_PREIMPRESO en preimpresos que sean nan
    df_ficha_tecnica_preimpresos = df_ficha_tecnica_preimpresos.dropna(subset=['COD_PREIMPRESO'])
    df_ficha_tecnica_preimpresos['COD_PREIMPRESO_SIN_V'] = df_ficha_tecnica_preimpresos['COD_PREIMPRESO'].str.split('-').str[0]


    #Eliminar COD_SKU que empieza con letra C
    df_ficha_tecnica['COD_SKU']  = df_ficha_tecnica['COD_MATERIAL'] 
    df_ficha_tecnica = df_ficha_tecnica[~df_ficha_tecnica['COD_SKU'].str.startswith('C')]
    
    #Agregar una columna que se llame COD_SKU_SIN_V que sea igual a COD_SKU pero eliminado el guion y todo lo que sigue luego
    df_ficha_tecnica['COD_SKU_SIN_V'] = df_ficha_tecnica['COD_SKU'].str.split('-').str[0]

    # Unificar columnas
    df_ficha_tecnica['ANCHO_CARA_5'] = df_ficha_tecnica.filter(regex='DIMANCHOCARA5').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['ANCHO_CARA_6'] = df_ficha_tecnica.filter(regex='DIMANCHOCARA6').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    
    
    df_ficha_tecnica['ANCHO_SACO'] = df_ficha_tecnica.filter(regex='DIMANCHOSACO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['LARGO_SACO'] = df_ficha_tecnica.filter(regex='DIMLARGOSACO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['LARGO_TUBO'] = df_ficha_tecnica.filter(regex='DIMLARGOTUBO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['TIPO_CORTE'] = df_ficha_tecnica.filter(regex='DIMTIPOCORTE').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['MANGA'] = df_ficha_tecnica.filter(regex='MANGA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]

    #df_ficha_tecnica['LARGO_TUBO'] = df_ficha_tecnica.filter(regex='DIMLARGOSACO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['LARGO_TUBO'] = np.where(
    df_ficha_tecnica['TIPO_ENVASE'] == 'BAP',
    df_ficha_tecnica.filter(regex='DIMLARGOSACO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0],
    df_ficha_tecnica.filter(regex='DIMLARGOTUBO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
)
        
    #     # --- Identificar filas que se eliminarían por NaN en variables dimensionales ---
    cols_dim = ['ANCHO_SACO', 'LARGO_SACO', 'LARGO_TUBO', 'TIPO_CORTE']

    # Filas con al menos un NaN en esas columnas
    df_faltantes = df_ficha_tecnica[df_ficha_tecnica[cols_dim].isna().any(axis=1)].copy()

    # Crear columna con las variables que tienen NaN
    df_faltantes['MOTIVO_ELIMINACION'] = df_faltantes[cols_dim].apply(
        lambda row: ', '.join([col for col in cols_dim if pd.isna(row[col])]), axis=1
    )

    # --- Filas con HOJAS inválidas o faltantes ---
    df_hojas_invalidas = df_ficha_tecnica[
        df_ficha_tecnica['HOJAS'].isna() | 
        (df_ficha_tecnica['HOJAS'] <= 0) | 
        (df_ficha_tecnica['HOJAS'] >= 5)
    ].copy()

    df_hojas_invalidas['MOTIVO_ELIMINACION'] = df_hojas_invalidas.apply(
        lambda row: 'HOJAS=' + str(row['HOJAS']), axis=1
    )

    # --- Unir ambos conjuntos ---
    df_eliminados = pd.concat([df_faltantes, df_hojas_invalidas], ignore_index=True)

    # --- Eliminar duplicados si alguno cae en ambas categorías ---
    df_eliminados = df_eliminados.drop_duplicates(subset=['COD_SKU'])

    # # --- Exportar a Excel ---
    df_eliminados.to_excel('ResultadosEstaticos/Errores/SKUs_eliminados_por_datos_faltantes_en_FT_CH_MX_PE.xlsx', index=False)
##################################################3

    df_ficha_tecnica['LARGO_PAPEL'] = df_ficha_tecnica.filter(regex='B2LARGOPAPEL').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]

    df_ficha_tecnica['ANCHO_PAPEL'] = df_ficha_tecnica.filter(regex='B2ANCHOPAPEL').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    
    # Para registros donde TIPO_ENVASE contiene 'BAC', asignar LARGO_PAPEL a LARGO_TUBO
    df_ficha_tecnica.loc[
        df_ficha_tecnica['TIPO_ENVASE'].str.contains('BAC', case=False, na=False), 
        'LARGO_TUBO'
    ] = df_ficha_tecnica.loc[
        df_ficha_tecnica['TIPO_ENVASE'].str.contains('BAC', case=False, na=False), 
        'LARGO_PAPEL'
    ]
    
    #Filtrar columnas por B16IMPFONDERA, luego unificar en una sola columna "IMPRESION_FONDERA" si dice on sino nan
    df_ficha_tecnica['IMPRESION_FONDERA'] = df_ficha_tecnica \
    .filter(regex='B16IMPFONDERA') \
    .replace([0, 'off', 'OFF', 'Off', '-', 'NO', 'No', 'no', 'nO'], np.nan) \
    .applymap(lambda x: 'on' if str(x).lower() == 'on' else np.nan) \
    .bfill(axis=1) \
    .iloc[:, 0]

    
    df_ficha_tecnica = df_ficha_tecnica.dropna(
    subset=['ANCHO_SACO', 'LARGO_SACO', 'LARGO_TUBO', 'TIPO_CORTE'],
    how='any')


    df_ficha_tecnica['UNERO_VALVULA'] = df_ficha_tecnica.filter(regex='UNEROVALVULA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]

    df_ficha_tecnica['ANCHO_PAPEL_VALVULA'] = df_ficha_tecnica.filter(regex='B6ANCHOPAPEL').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    df_ficha_tecnica['ANCHO_VALVULA'] = df_ficha_tecnica.filter(regex='B6VALANCHO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    
    df_ficha_tecnica['LARGO_PAPEL_VALVULA'] = df_ficha_tecnica.filter(regex='B6LARGOPAPEL').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    df_ficha_tecnica['LARGO_VALVULA'] = df_ficha_tecnica.filter(regex='B6VALLARGO116').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    
    
    df_ficha_tecnica['TIPO_VALVULA'] = df_ficha_tecnica.filter(regex='VALTIPO').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0].str.replace(r'[\d-]', '', regex=True).str.upper()
    # Puede ser que tenga 0 colores para imprimir
    #df_ficha_tecnica['CANTIDAD_COLORES'] = df_ficha_tecnica.filter(regex='IMPNUMEROCOLORES').replace([np.nan, 'NO', 'No', 'no', 'nO', '-'], 0).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['CANTIDAD_COLORES'] = (
    df_ficha_tecnica
    .filter(regex='IMPNUMEROCOLORES')
    .applymap(lambda x: x.strip() if isinstance(x, str) else x)
    .replace(['-', 'NO', 'No', 'no', 'nO', ''], np.nan)
    .apply(pd.to_numeric, errors='coerce')
    .max(axis=1)
    .fillna(0)
    .astype(int)
)

    
    df_ficha_tecnica['LARGO_TOMA'] = df_ficha_tecnica.filter(regex='VALTOMA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).astype(float).max(axis=1)
    
    df_ficha_tecnica['ANCHO_PAPEL_ID_HOJA_1'] = df_ficha_tecnica.filter(regex='B20ANCHOPAPEL114').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['ANCHO_PAPEL_ID_HOJA_2'] = df_ficha_tecnica.filter(regex='B20ANCHOPAPEL124').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['ANCHO_PAPEL_ID_HOJA_3'] = df_ficha_tecnica.filter(regex='B20ANCHOPAPEL134').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['ANCHO_PAPEL_ID_HOJA_4'] = df_ficha_tecnica.filter(regex='B20ANCHOPAPEL144').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]


    df_ficha_tecnica['TIPO_REFUERZO_CARA5'] = df_ficha_tecnica.filter(regex='REFTIPOREFUERZO211').replace([0, 'NO', 'No', 'no', 'nO', '-', 'SIN REFUERZO'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['TIPO_REFUERZO_CARA6'] = df_ficha_tecnica.filter(regex='REFTIPOREFUERZO221').replace([0, 'NO', 'No', 'no', 'nO', '-', 'SIN REFUERZO'], np.nan).bfill(axis=1).iloc[:, 0]

    df_ficha_tecnica['PREIMPRESION'] = df_ficha_tecnica.filter(regex='IMPPREIMPRESO').replace([0, 'NO', 'No', 'no', 'nO', '-', 'off'], np.nan).bfill(axis=1).iloc[:, 0]
    
    df_ficha_tecnica['LARGO_PAPEL_CARA5'] = df_ficha_tecnica.filter(regex='B4LARGOPAPEL213').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['LARGO_PAPEL_CARA6'] = df_ficha_tecnica.filter(regex='B4LARGOPAPEL223').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]

    df_ficha_tecnica['ANCHO_PAPEL_CARA5'] = df_ficha_tecnica.filter(regex='B4ANCHOPAPEL212').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    df_ficha_tecnica['ANCHO_PAPEL_CARA6'] = df_ficha_tecnica.filter(regex='B4ANCHOPAPEL222').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    
    df_ficha_tecnica['PROTOCOLO'] = df_ficha_tecnica['PROTOCOLO'].replace('Alimento', 'ALIMENTO')
    df_ficha_tecnica['PROTOCOLO'] = df_ficha_tecnica['PROTOCOLO'].replace('no alimento', 'NO ALIMENTO')

    df_ficha_tecnica['ID_HOJA_1'] = df_ficha_tecnica['B20CODIGOSAP115'].str.split('-').str[0]
    df_ficha_tecnica['ID_HOJA_2'] = df_ficha_tecnica['B20CODIGOSAP125'].str.split('-').str[0]
    df_ficha_tecnica['ID_HOJA_3'] = df_ficha_tecnica['B20CODIGOSAP135'].str.split('-').str[0]
    df_ficha_tecnica['ID_HOJA_4'] = df_ficha_tecnica['B20CODIGOSAP145'].str.split('-').str[0]
    
    
    df_ficha_tecnica['DESCRIPCION_HOJA_1'] = df_ficha_tecnica['B20DESCRIPCIONSAP117']
    df_ficha_tecnica['DESCRIPCION_HOJA_2'] = df_ficha_tecnica['B20DESCRIPCIONSAP127']
    df_ficha_tecnica['DESCRIPCION_HOJA_3'] = df_ficha_tecnica['B20DESCRIPCIONSAP137']
    df_ficha_tecnica['DESCRIPCION_HOJA_4'] = df_ficha_tecnica['B20DESCRIPCIONSAP147']
    
    # df_ficha_tecnica['ID_HOJA_1'] = df_ficha_tecnica['B20CODIGOSAP115'].apply(
    # lambda x: str(x).strip() if pd.notna(x) else '')
    # df_ficha_tecnica['ID_HOJA_2'] = df_ficha_tecnica['B20CODIGOSAP125'].apply(
    # lambda x: str(x).strip() if pd.notna(x) else '')
    # df_ficha_tecnica['ID_HOJA_3'] = df_ficha_tecnica['B20CODIGOSAP135'].apply(
    # lambda x: str(x).strip() if pd.notna(x) else '')
    # df_ficha_tecnica['ID_HOJA_4'] = df_ficha_tecnica['B20CODIGOSAP145'].apply(
    # lambda x: str(x).strip() if pd.notna(x) else '')
    
    df_ficha_tecnica['TIENE_FILM'] = (
        df_ficha_tecnica['DESCRIPCION_HOJA_1'].str.contains('film', case=False, na=False) |
        df_ficha_tecnica['DESCRIPCION_HOJA_2'].str.contains('film', case=False, na=False) |
        df_ficha_tecnica['DESCRIPCION_HOJA_3'].str.contains('film', case=False, na=False) |
        df_ficha_tecnica['DESCRIPCION_HOJA_4'].str.contains('film', case=False, na=False)
    )
    
    df_ficha_tecnica['ID_CARA_5'] = df_ficha_tecnica['B22CODIGOSAP113'].fillna(df_ficha_tecnica['B22CODIGOSAP213']).str.split('-').str[0]
    df_ficha_tecnica['ID_CARA_6'] = df_ficha_tecnica['B22CODIGOSAP123'].str.split('-').str[0]
    
    # REFUERZO_PREIMPRESO: verificar si ID_CARA_5 o ID_CARA_6 contienen 'PRP' en el string
    df_ficha_tecnica['REFUERZO_PREIMPRESO'] = np.where(
        (df_ficha_tecnica['ID_CARA_5'].str.contains('PRP', case=False, na=False) |
        df_ficha_tecnica['ID_CARA_6'].str.contains('PRP', case=False, na=False)),
        'on','') 
    
    df_ficha_tecnica['PESO_HOJA_1'] = df_ficha_tecnica['B20PESO116']
    df_ficha_tecnica['PESO_HOJA_2'] = df_ficha_tecnica['B20PESO126']
    df_ficha_tecnica['PESO_HOJA_3'] = df_ficha_tecnica['B20PESO136']
    df_ficha_tecnica['PESO_HOJA_4'] = df_ficha_tecnica['B20PESO146']
    
    # Limpieza
    df_ficha_tecnica.dropna(subset=['HOJAS'], inplace=True)
    df_ficha_tecnica = df_ficha_tecnica[(df_ficha_tecnica['HOJAS'] > 0) & (df_ficha_tecnica['HOJAS'] < 5)]
    
    df_ficha_tecnica['ANCHO_PAPEL'] = df_ficha_tecnica['ANCHO_PAPEL'].astype(float)

    # # Actualizar ID_HOJA con valores de preimpresos si coincide COD_MATERIAL
    # for i in range(1, 5):
    #     # Merge para obtener el CODIGO_MP correspondiente
    #     merge_col = f'ID_HOJA_{i}'
    #     df_ficha_tecnica = df_ficha_tecnica.merge(
    #         df_ficha_tecnica_preimpresos, 
    #         left_on=merge_col, 
    #         right_on='COD_PREIMPRESO_SIN_V', 
    #         how='left'
    #     )

    #     # Actualizar con el valor de CODIGO_MP si existe match
    #     df_ficha_tecnica[merge_col] = df_ficha_tecnica['CODIGO_MP'].fillna(df_ficha_tecnica[merge_col])
        
    #     # Eliminar las columnas temporales del merge
    #     df_ficha_tecnica = df_ficha_tecnica.drop(columns=['COD_PREIMPRESO_SIN_V', 'CODIGO_MP'])
    
    # Actualizar ID_HOJA con valores de preimpresos si coincide COD_MATERIAL
    for i in range(1, 5):
        merge_col = f'ID_HOJA_{i}'
        
        # Hacer merge temporal para evitar duplicar columnas
        temp_merge = df_ficha_tecnica.merge(
            df_ficha_tecnica_preimpresos[['COD_PREIMPRESO_SIN_V', 'CODIGO_MP']], 
            left_on=merge_col, 
            right_on='COD_PREIMPRESO_SIN_V', 
            how='left'
        )
        
        # Actualizar valores: si hay match, reemplazar ID_HOJA_i por CODIGO_MP
        temp_merge[merge_col] = temp_merge['CODIGO_MP'].fillna(temp_merge[merge_col])
        
        # Eliminar columnas temporales y devolver al df principal
        df_ficha_tecnica = temp_merge.drop(columns=['COD_PREIMPRESO_SIN_V', 'CODIGO_MP'])
    ######
    # Actualizar ID_CARA_5 y ID_CARA_6 con valores de preimpresos si coincide COD_MATERIAL
    for cara in ['ID_CARA_5', 'ID_CARA_6']:
        # Merge para obtener el CODIGO_MP correspondiente
        df_ficha_tecnica = df_ficha_tecnica.merge(
            df_ficha_tecnica_preimpresos, 
            left_on=cara, 
            right_on='COD_PREIMPRESO', 
            how='left'
        )

        # Actualizar con el valor de CODIGO_MP si existe match
        df_ficha_tecnica[cara] = df_ficha_tecnica['CODIGO_MP'].fillna(df_ficha_tecnica[cara])
        
        # Eliminar las columnas temporales del merge
        df_ficha_tecnica = df_ficha_tecnica.drop(columns=['COD_PREIMPRESO', 'CODIGO_MP'])
   
    df_gramaje_unico = df_ficha_tecnica_materia_prima[['COD_MP', 'GRAMAJE']].drop_duplicates(subset='COD_MP', keep='first')
    map_gramaje = dict(zip(df_gramaje_unico['COD_MP'], df_gramaje_unico['GRAMAJE']))
    for i in range(1, 5):
        col_id = f'ID_HOJA_{i}'
        col_gramaje = f'GRAMAJE_ID_HOJA_{i}' #GRAMOS
        df_ficha_tecnica[col_gramaje] = df_ficha_tecnica[col_id].map(map_gramaje)

    #AREA M2: PRODUCTO ENTRE LARGO_PAPEL Y ANCHO_PAPEL_ID_HOJA_#
    for i in range(1, 5):
        df_ficha_tecnica[f'AREA_M2_ID_HOJA_{i}'] = df_ficha_tecnica['LARGO_PAPEL'] * df_ficha_tecnica[f'ANCHO_PAPEL_ID_HOJA_{i}']/1000000
        
    # Forzar a numérico (convierte strings a float, NaN si no puede)
    df_ficha_tecnica['AREA_M2_ID_HOJA_1'] = pd.to_numeric(df_ficha_tecnica['AREA_M2_ID_HOJA_1'], errors='coerce')
    df_ficha_tecnica['GRAMAJE_ID_HOJA_1'] = pd.to_numeric(df_ficha_tecnica['GRAMAJE_ID_HOJA_1'], errors='coerce')
    
    #FACTOR_CONVERSION_ID_HOJA_# IGUAL AL PRODUCTO ENTRE AREA Y GRAMAJE (G/MSC)
    for i in range(1, 5):
        df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'] = df_ficha_tecnica[f'AREA_M2_ID_HOJA_{i}'] * df_ficha_tecnica[f'GRAMAJE_ID_HOJA_{i}']

    df_ficha_tecnica = df_ficha_tecnica[[
        'TIPO_ENVASE', 'COD_SKU', 'COD_SKU_SIN_V', 'HOJAS', 'COD_CLIENTE', 'CLIENTE', 'PRODUCTO', 'CAPACIDAD', 'VOLUMEN', 'PESO','PROTOCOLO',
        'ANCHO_PAPEL', 'ANCHO_CARA_5', 'ANCHO_CARA_6','LARGO_PAPEL', 'ANCHO_SACO', 'LARGO_SACO', 'LARGO_TUBO', 'TIPO_CORTE', 'UNERO_VALVULA',
        'ANCHO_VALVULA', 'LARGO_VALVULA', 'TIPO_VALVULA', 'MANGA', 'CANTIDAD_COLORES', 'TIPO_REFUERZO_CARA5', 'TIPO_REFUERZO_CARA6', 'PREIMPRESION', 'IMPRESION_FONDERA', 'LARGO_TOMA',
        'LARGO_PAPEL_VALVULA', 'ANCHO_PAPEL_VALVULA',
        'LARGO_PAPEL_CARA5', 'LARGO_PAPEL_CARA6', 'ANCHO_PAPEL_CARA5', 'ANCHO_PAPEL_CARA6',
        'ID_HOJA_1',  'DESCRIPCION_HOJA_1', 'PESO_HOJA_1', 'GRAMAJE_ID_HOJA_1', 'ANCHO_PAPEL_ID_HOJA_1', 'AREA_M2_ID_HOJA_1', 'FACTOR_CONVERSION_ID_HOJA_1',
        'ID_HOJA_2', 'DESCRIPCION_HOJA_2', 'PESO_HOJA_2', 'GRAMAJE_ID_HOJA_2', 'ANCHO_PAPEL_ID_HOJA_2', 'AREA_M2_ID_HOJA_2', 'FACTOR_CONVERSION_ID_HOJA_2',
        'ID_HOJA_3', 'DESCRIPCION_HOJA_3', 'PESO_HOJA_3', 'GRAMAJE_ID_HOJA_3', 'ANCHO_PAPEL_ID_HOJA_3', 'AREA_M2_ID_HOJA_3', 'FACTOR_CONVERSION_ID_HOJA_3',
        'ID_HOJA_4', 'DESCRIPCION_HOJA_4', 'PESO_HOJA_4', 'GRAMAJE_ID_HOJA_4', 'ANCHO_PAPEL_ID_HOJA_4', 'AREA_M2_ID_HOJA_4', 'FACTOR_CONVERSION_ID_HOJA_4',
        'ID_CARA_5', 'ID_CARA_6', 'REFUERZO_PREIMPRESO',
        #'ID_CARA_5', 'DESCRIPCION_CARA_5', 'PESO_CARA_5',
        #'ID_CARA_6', 'DESCRIPCION_CARA_6', 'PESO_CARA_6',
        'TIENE_FILM', 'CATEGORIA_SKU_SKCL', 'CATEGORIA_SKU_SKBR-CN', 'CATEGORIA_SKU_SKBR-PS', 'CATEGORIA_SKU_SKPE', 'CATEGORIA_SKU_SKMX-G', 'CATEGORIA_SKU_SKMX-I'
    ]]
        
    # Fichas tecnicas de Brasil
    ficha_tecnica_brasil_bap = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Base Brasil BAP.xlsx')
    ficha_tecnica_brasil_cvp = pd.read_excel('ResultadosEstaticos/Inputs/Fichas tecnicas/Base Brasil CVP.xlsx')

    # Unir las fichas tecnicas de Brasil
    ficha_tecnica_brasil = pd.concat([ficha_tecnica_brasil_bap, ficha_tecnica_brasil_cvp], ignore_index=True)
    
    # Crear columnas necesarias
    ficha_tecnica_brasil['TIPO_ENVASE'] = ficha_tecnica_brasil['TIPO DE ENVASE'].str.replace('SK-', '', regex=False)
    ficha_tecnica_brasil['COD_SKU'] = ficha_tecnica_brasil['Número de material']
    ficha_tecnica_brasil['COD_SKU_SIN_V'] = ficha_tecnica_brasil['COD_SKU'].str.split('-').str[0]
    
    # Separar la versión (parte después del '-') y convertir a numérico
    ficha_tecnica_brasil['VERSION'] = ficha_tecnica_brasil['COD_SKU'].str.split('-').str[1]
    ficha_tecnica_brasil['VERSION_NUM'] = pd.to_numeric(ficha_tecnica_brasil['VERSION'], errors='coerce')

    # Obtener el índice del registro con mayor versión para cada COD_SKU_SIN_V
    idx_max_version = ficha_tecnica_brasil.groupby('COD_SKU_SIN_V')['VERSION_NUM'].idxmax()

    # Filtrar solo los registros con mayor versión
    ficha_tecnica_brasil = ficha_tecnica_brasil.loc[idx_max_version].reset_index(drop=True)

    # Eliminar columnas auxiliares
    ficha_tecnica_brasil = ficha_tecnica_brasil.drop(columns=['VERSION', 'VERSION_NUM'])
    
    ficha_tecnica_brasil['HOJAS'] = ficha_tecnica_brasil['NUMERO DE HOJAS']
    ficha_tecnica_brasil['COD_CLIENTE'] = ficha_tecnica_brasil['CODIGO DE CLIENTE']
    ficha_tecnica_brasil['CLIENTE'] = ficha_tecnica_brasil['NOMBRE DEL CLIENTE']
    ficha_tecnica_brasil['PRODUCTO'] = ficha_tecnica_brasil['NOMBRE DEL PRODUCTO']
    ficha_tecnica_brasil['CAPACIDAD'] = ficha_tecnica_brasil['CAPACIDAD']
    ficha_tecnica_brasil['VOLUMEN'] = ficha_tecnica_brasil['VOLUMEN']
    ficha_tecnica_brasil['PESO'] = ficha_tecnica_brasil['PESO TEORICO']
    ficha_tecnica_brasil['PROTOCOLO'] = ficha_tecnica_brasil['PROTOCOLO']
    ficha_tecnica_brasil['ANCHO_PAPEL'] = ficha_tecnica_brasil['ANCHO PAPEL']
    ficha_tecnica_brasil['ANCHO_PAPEL_ID_HOJA_1'] = ficha_tecnica_brasil.filter(regex='ANCHO PLIEGO HOJA 1').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    ficha_tecnica_brasil['ANCHO_PAPEL_ID_HOJA_2'] = ficha_tecnica_brasil.filter(regex='ANCHO PLIEGO HOJA 2').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    ficha_tecnica_brasil['ANCHO_PAPEL_ID_HOJA_3'] = ficha_tecnica_brasil.filter(regex='ANCHO PLIEGO HOJA 3').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    ficha_tecnica_brasil['ANCHO_PAPEL_ID_HOJA_4'] = ficha_tecnica_brasil.filter(regex='ANCHO PLIEGO HOJA 4').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).bfill(axis=1).iloc[:, 0]
    ficha_tecnica_brasil['ANCHO_CARA_5'] = ficha_tecnica_brasil['ANCHO CARA 5']
    ficha_tecnica_brasil['ANCHO_CARA_6'] = ficha_tecnica_brasil['ANCHO CARA 6']
    ficha_tecnica_brasil['LARGO_PAPEL'] = ficha_tecnica_brasil['LARGO PAPEL']
    ficha_tecnica_brasil['ANCHO_SACO'] = ficha_tecnica_brasil['ANCHO SACO']
    ficha_tecnica_brasil['LARGO_SACO'] = ficha_tecnica_brasil['LARGO SACO']
    ficha_tecnica_brasil['LARGO_TUBO'] = ficha_tecnica_brasil['LARGO TUBO']
    ficha_tecnica_brasil['TIPO_CORTE'] = ficha_tecnica_brasil['TIPO DE CORTE']
    ficha_tecnica_brasil['UNERO_VALVULA'] = ficha_tecnica_brasil['VALVULA UNERO'].apply(lambda x: 'Si' if str(x).upper() in ['X', 'SI'] else np.nan)
    ficha_tecnica_brasil['ANCHO_VALVULA'] = ficha_tecnica_brasil.filter(regex='ANCHO VALVULA HOJA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    ficha_tecnica_brasil['LARGO_VALVULA'] = ficha_tecnica_brasil.filter(regex='LARGO VALVULA HOJA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    ficha_tecnica_brasil['TIPO_VALVULA'] = ficha_tecnica_brasil['TIPO VALVULA'].fillna('').str.replace(r'[\d-]', '', regex=True).str.upper()
    ficha_tecnica_brasil['MANGA'] = np.nan  # Brasil no tiene esta columna, queda vacía
    ficha_tecnica_brasil['CANTIDAD_COLORES'] = ficha_tecnica_brasil['NUMERO COLORES']
    ficha_tecnica_brasil['TIPO_REFUERZO_CARA5'] = ficha_tecnica_brasil['TIPO REFUERZO CARA 5']
    ficha_tecnica_brasil['TIPO_REFUERZO_CARA6'] = ficha_tecnica_brasil['TIPO REFUERZO CARA 6']
    ficha_tecnica_brasil['PREIMPRESION'] = np.where(
        (ficha_tecnica_brasil['CARA 5 PREIMPRESO'] == 'S') | 
        (ficha_tecnica_brasil['CARA 6 PREIMPRESO'] == 'S'),
        'on',
        ''
    )
    
    ficha_tecnica_brasil['IMPRESION_FONDERA'] = np.where(
    ~ficha_tecnica_brasil['TIPO REFUERZO CARA 5'].isna() | ~ficha_tecnica_brasil['TIPO REFUERZO CARA 6'].isna(),
    np.where(
        (ficha_tecnica_brasil['CARA 5 IMPRESO EN LINEA'] == 'S') | 
        (ficha_tecnica_brasil['CARA 6 IMPRESO EN LINEA'] == 'S'),
        'on',
        ''
    ), '')
    
    ficha_tecnica_brasil['LARGO_TOMA'] = ficha_tecnica_brasil.filter(regex='VH\d TOMA').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    ficha_tecnica_brasil['LARGO_PAPEL_VALVULA'] = ficha_tecnica_brasil.filter(regex='VH\d LARGO P').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    ficha_tecnica_brasil['ANCHO_PAPEL_VALVULA'] = ficha_tecnica_brasil.filter(regex='VH\d ANCHO P').replace([0, 'NO', 'No', 'no', 'nO', '-'], np.nan).apply(pd.to_numeric, errors='coerce').max(axis=1)
    ficha_tecnica_brasil['LARGO_PAPEL_CARA5'] = ficha_tecnica_brasil['LP CARA 5']
    ficha_tecnica_brasil['LARGO_PAPEL_CARA6'] = ficha_tecnica_brasil['LP CARA 6']
    ficha_tecnica_brasil['ANCHO_PAPEL_CARA5'] = ficha_tecnica_brasil['AP CARA 5']
    ficha_tecnica_brasil['ANCHO_PAPEL_CARA6'] = ficha_tecnica_brasil['AP CARA 6']
    ficha_tecnica_brasil['PROTOCOLO'] = ficha_tecnica_brasil['PROTOCOLO'].replace(['Alimento', 'ALIMENTO Y FSC'], 'ALIMENTO')
    ficha_tecnica_brasil['PROTOCOLO'] = ficha_tecnica_brasil['PROTOCOLO'].replace('no alimento', 'NO ALIMENTO')
    ficha_tecnica_brasil['ID_HOJA_1'] = ficha_tecnica_brasil['CODIGO PLIEGO HOJA 1']
    ficha_tecnica_brasil['ID_HOJA_2'] = ficha_tecnica_brasil['CODIGO PLIEGO HOJA 2']
    ficha_tecnica_brasil['ID_HOJA_3'] = ficha_tecnica_brasil['CODIGO PLIEGO HOJA 3']
    ficha_tecnica_brasil['ID_HOJA_4'] = ficha_tecnica_brasil['CODIGO PLIEGO HOJA 4']
    ficha_tecnica_brasil['DESCRIPCION_HOJA_1'] = ficha_tecnica_brasil['DESCRIPCION PLIEGO HOJA 1']
    ficha_tecnica_brasil['DESCRIPCION_HOJA_2'] = ficha_tecnica_brasil['DESCRIPCION PLIEGO HOJA 2']
    ficha_tecnica_brasil['DESCRIPCION_HOJA_3'] = ficha_tecnica_brasil['DESCRIPCION PLIEGO HOJA 3']
    ficha_tecnica_brasil['DESCRIPCION_HOJA_4'] = ficha_tecnica_brasil['DESCRIPCION PLIEGO HOJA 4']
    
    ficha_tecnica_brasil['TIENE_FILM'] = (
        ficha_tecnica_brasil['DESCRIPCION_HOJA_1'].str.contains('film', case=False, na=False) |
        ficha_tecnica_brasil['DESCRIPCION_HOJA_2'].str.contains('film', case=False, na=False) |
        ficha_tecnica_brasil['DESCRIPCION_HOJA_3'].str.contains('film', case=False, na=False) |
        ficha_tecnica_brasil['DESCRIPCION_HOJA_4'].str.contains('film', case=False, na=False)
    )
    
    ficha_tecnica_brasil['PESO_HOJA_1'] = ficha_tecnica_brasil['PESO TEORICO HOJA 1']
    ficha_tecnica_brasil['PESO_HOJA_2'] = ficha_tecnica_brasil['PESO TEORICO HOJA 2']
    ficha_tecnica_brasil['PESO_HOJA_3'] = ficha_tecnica_brasil['PESO TEORICO HOJA 3']
    ficha_tecnica_brasil['PESO_HOJA_4'] = ficha_tecnica_brasil['PESO TEORICO HOJA 4']
    
    for i in range(1, 5):
        col_id = f'ID_HOJA_{i}'
        col_gramaje = f'GRAMAJE_ID_HOJA_{i}' #GRAMOS
        ficha_tecnica_brasil[col_gramaje] = ficha_tecnica_brasil[col_id].map(map_gramaje)

    #AREA M2: PRODUCTO ENTRE LARGO_PAPEL Y ANCHO_PAPEL_ID_HOJA_#
    for i in range(1, 5):
        ficha_tecnica_brasil[f'AREA_M2_ID_HOJA_{i}'] = ficha_tecnica_brasil['LARGO_PAPEL'] * ficha_tecnica_brasil[f'ANCHO_PAPEL_ID_HOJA_{i}']/1000000

    # Forzar a numérico (convierte strings a float, NaN si no puede)
    ficha_tecnica_brasil['AREA_M2_ID_HOJA_1'] = pd.to_numeric(ficha_tecnica_brasil['AREA_M2_ID_HOJA_1'], errors='coerce')
    ficha_tecnica_brasil['GRAMAJE_ID_HOJA_1'] = pd.to_numeric(ficha_tecnica_brasil['GRAMAJE_ID_HOJA_1'], errors='coerce')
    
    #FACTOR_CONVERSION_ID_HOJA_# IGUAL AL PRODUCTO ENTRE AREA Y GRAMAJE (G/MSC)
    for i in range(1, 5):
        ficha_tecnica_brasil[f'FACTOR_CONVERSION_ID_HOJA_{i}'] = ficha_tecnica_brasil[f'AREA_M2_ID_HOJA_{i}'] * ficha_tecnica_brasil[f'GRAMAJE_ID_HOJA_{i}']


    ficha_tecnica_brasil = ficha_tecnica_brasil[[
        'TIPO_ENVASE', 'COD_SKU', 'COD_SKU_SIN_V', 'HOJAS', 'COD_CLIENTE', 'CLIENTE', 'PRODUCTO', 'CAPACIDAD', 'VOLUMEN', 'PESO','PROTOCOLO',
        'ANCHO_PAPEL', 'ANCHO_CARA_5', 'ANCHO_CARA_6','LARGO_PAPEL', 'ANCHO_SACO', 'LARGO_SACO', 'LARGO_TUBO', 'TIPO_CORTE', 'UNERO_VALVULA',
        'ANCHO_VALVULA', 'LARGO_VALVULA', 'TIPO_VALVULA', 'MANGA', 'CANTIDAD_COLORES', 'TIPO_REFUERZO_CARA5', 'TIPO_REFUERZO_CARA6', 'PREIMPRESION','IMPRESION_FONDERA', 'LARGO_TOMA',
        'LARGO_PAPEL_VALVULA', 'ANCHO_PAPEL_VALVULA',
        'LARGO_PAPEL_CARA5', 'LARGO_PAPEL_CARA6', 'ANCHO_PAPEL_CARA5', 'ANCHO_PAPEL_CARA6',
        'ID_HOJA_1',  'DESCRIPCION_HOJA_1', 'PESO_HOJA_1', 'GRAMAJE_ID_HOJA_1', 'ANCHO_PAPEL_ID_HOJA_1', 'AREA_M2_ID_HOJA_1', 'FACTOR_CONVERSION_ID_HOJA_1',
        'ID_HOJA_2', 'DESCRIPCION_HOJA_2', 'PESO_HOJA_2', 'GRAMAJE_ID_HOJA_2', 'ANCHO_PAPEL_ID_HOJA_2', 'AREA_M2_ID_HOJA_2', 'FACTOR_CONVERSION_ID_HOJA_2',
        'ID_HOJA_3', 'DESCRIPCION_HOJA_3', 'PESO_HOJA_3', 'GRAMAJE_ID_HOJA_3', 'ANCHO_PAPEL_ID_HOJA_3', 'AREA_M2_ID_HOJA_3', 'FACTOR_CONVERSION_ID_HOJA_3',
        'ID_HOJA_4', 'DESCRIPCION_HOJA_4', 'PESO_HOJA_4', 'GRAMAJE_ID_HOJA_4', 'ANCHO_PAPEL_ID_HOJA_4', 'AREA_M2_ID_HOJA_4', 'FACTOR_CONVERSION_ID_HOJA_4',
        'TIENE_FILM', 'CATEGORIA_SKU_SKCL', 'CATEGORIA_SKU_SKBR-CN', 'CATEGORIA_SKU_SKBR-PS', 'CATEGORIA_SKU_SKPE', 'CATEGORIA_SKU_SKMX-G', 'CATEGORIA_SKU_SKMX-I'
    ]]
    
    df_ficha_tecnica = pd.concat([df_ficha_tecnica, ficha_tecnica_brasil], ignore_index=True)
    
# ============= REPORTE DE ERRORES (INCLUYE BRASIL) =============
    # --- Identificar filas que se eliminarían por NaN en variables dimensionales ---
    cols_dim = ['ANCHO_SACO', 'LARGO_SACO', 'LARGO_TUBO', 'TIPO_CORTE']

    # Filas con al menos un NaN en esas columnas (SOLO BRASIL)
    df_faltantes_BR = ficha_tecnica_brasil[ficha_tecnica_brasil[cols_dim].isna().any(axis=1)].copy()

    # Crear columna con las variables que tienen NaN
    df_faltantes_BR['MOTIVO_ELIMINACION'] = df_faltantes_BR[cols_dim].apply(
        lambda row: 'Falta información dimensional: ' + ', '.join([col for col in cols_dim if pd.isna(row[col])]), axis=1
    )

    # --- Filas con HOJAS inválidas o faltantes (SOLO BRASIL) ---
    df_hojas_invalidas_BR = ficha_tecnica_brasil[
        ficha_tecnica_brasil['HOJAS'].isna() | 
        (ficha_tecnica_brasil['HOJAS'] <= 0) | 
        (ficha_tecnica_brasil['HOJAS'] >= 5)
    ].copy()

    df_hojas_invalidas_BR['MOTIVO_ELIMINACION'] = df_hojas_invalidas_BR.apply(
        lambda row: 'HOJAS inválida (valor: ' + str(row['HOJAS']) + ')', axis=1
    )

    # --- Unir errores de BRASIL ---
    df_eliminados_BR = pd.concat([df_faltantes_BR, df_hojas_invalidas_BR], ignore_index=True)

    # --- Eliminar duplicados si alguno cae en ambas categorías ---
    df_eliminados_BR = df_eliminados_BR.drop_duplicates(subset=['COD_SKU'])

    # --- Exportar a Excel BRASIL ---
    df_eliminados_BR.to_excel('ResultadosEstaticos/Errores/SKUs_eliminados_por_datos_faltantes_en_FT_BR.xlsx', index=False)
    # ================================================================
    
    # Convertir COD_CLIENTE a numerico (int)
    df_ficha_tecnica['COD_CLIENTE'] = pd.to_numeric(df_ficha_tecnica['COD_CLIENTE'], errors='coerce').astype('Int64')
    
    # Definir codigo cliente Forsac y de CMPC USA
    df_codigos_clientes['ID_CLIENTE_CMPC_USA'] = pd.to_numeric(df_codigos_clientes['ID_CLIENTE_CMPC_USA'], errors='coerce').astype('Int64')
    df_codigos_clientes['ID_CLIENTE_FORSAC'] = pd.to_numeric(df_codigos_clientes['ID_CLIENTE_FORSAC'], errors='coerce').astype('Int64')
    
    df_ficha_tecnica['COD_CLIENTE_FORSAC'] = df_ficha_tecnica['COD_CLIENTE']

    df_ficha_tecnica = df_ficha_tecnica.merge(df_codigos_clientes, right_on = 'ID_CLIENTE_FORSAC', left_on='COD_CLIENTE_FORSAC', how='left')
    df_ficha_tecnica['COD_CLIENTE'] = df_ficha_tecnica['ID_CLIENTE_CMPC_USA'].fillna(df_ficha_tecnica['COD_CLIENTE_FORSAC'])

    df_ficha_tecnica['COD_CLIENTE_FORSAC_USA'] = np.where(
        df_ficha_tecnica['ID_CLIENTE_CMPC_USA'].notna(),
        'CMPC USA',
        'Forsac'
    )

    # Determinar el PAIS_DESTINO de cada sku segun el COD_CLIENTE
    df_ficha_tecnica = df_ficha_tecnica.merge(df_clientes, on='COD_CLIENTE', how='left')
    
    # Reporte de errores de SKUs sin PAIS_DESTINO
    df_sin_pais_destino = df_ficha_tecnica[df_ficha_tecnica['PAIS_DESTINO'].isna()]
    if not df_sin_pais_destino.empty:
        df_sin_pais_destino.to_excel('ResultadosEstaticos/Errores/df_ficha_tecnica_sin_pais_destino.xlsx', index=False)
                
    df_ficha_tecnica = df_ficha_tecnica[~df_ficha_tecnica['PAIS_DESTINO'].isna()]
    
    # Armar columna SKU_DEMANDA_INTERNA
    def es_demanda_interna(row):
        sku = str(row['COD_SKU_SIN_V'])
        pais = str(row['PAIS_DESTINO']).upper()
        if sku.startswith('PR') and pais == 'CHILE':
            return 'on'
        elif sku.startswith('FO') and pais == 'PERU':
            return 'on'
        elif sku.startswith('FX') and pais == 'MEXICO':
            return 'on'
        elif sku.startswith('SK') and pais == 'BRASIL':
            return 'on'
        else:
            return ''
    df_ficha_tecnica['SKU_DEMANDA_INTERNA'] = df_ficha_tecnica.apply(es_demanda_interna, axis=1)
    
    # NUEVO: Reporte de errores para SKUs sin Factor de Conversión válido
    df_errores_factor_conversion = []
    
    for i in range(1, 5):
        # Identificar registros con problemas en el cálculo
        mask_error = (
            df_ficha_tecnica[f'ID_HOJA_{i}'].notna() &  # Tiene ID_HOJA pero...
            (
                df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'].isna() |  # Factor de conversión es NaN
                (df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'] == 0) |   # Factor de conversión es 0
                (df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'] <= 0)     # Factor de conversión es negativo
            )
        )
        
        if mask_error.any():
            df_temp_error = df_ficha_tecnica[mask_error].copy()
            df_temp_error['CAPA_ERROR'] = f'MP{i}'
            df_temp_error['ID_HOJA_ERROR'] = df_temp_error[f'ID_HOJA_{i}']
            df_temp_error['GRAMAJE_ERROR'] = df_temp_error[f'GRAMAJE_ID_HOJA_{i}']
            df_temp_error['ANCHO_PAPEL_ERROR'] = df_temp_error[f'ANCHO_PAPEL_ID_HOJA_{i}']
            df_temp_error['AREA_M2_ERROR'] = df_temp_error[f'AREA_M2_ID_HOJA_{i}']
            df_temp_error['FACTOR_CONVERSION_ERROR'] = df_temp_error[f'FACTOR_CONVERSION_ID_HOJA_{i}']
            
            # Identificar motivo específico del error
            def identificar_motivo_error(row):
                motivos = []
                if pd.isna(row[f'GRAMAJE_ID_HOJA_{i}']):
                    motivos.append('GRAMAJE no encontrado en materia prima')
                if pd.isna(row[f'ANCHO_PAPEL_ID_HOJA_{i}']):
                    motivos.append('ANCHO_PAPEL_ID_HOJA vacío')
                if pd.isna(row['LARGO_PAPEL']):
                    motivos.append('LARGO_PAPEL vacío')
                if pd.isna(row[f'AREA_M2_ID_HOJA_{i}']):
                    motivos.append('AREA_M2 no calculable')
                if row[f'FACTOR_CONVERSION_ID_HOJA_{i}'] == 0:
                    motivos.append('FACTOR_CONVERSION calculado como 0')
                if pd.isna(row[f'FACTOR_CONVERSION_ID_HOJA_{i}']):
                    motivos.append('FACTOR_CONVERSION no calculable (NaN)')
                return '; '.join(motivos) if motivos else 'Error no identificado'
            
            df_temp_error['MOTIVO_ERROR'] = df_temp_error.apply(identificar_motivo_error, axis=1)
            
            # Seleccionar columnas relevantes para el reporte
            df_temp_error = df_temp_error[[
                'COD_SKU', 'COD_SKU_SIN_V', 'CAPA_ERROR', 'ID_HOJA_ERROR',
                'LARGO_PAPEL', 'ANCHO_PAPEL_ERROR', 'AREA_M2_ERROR', 
                'GRAMAJE_ERROR', 'FACTOR_CONVERSION_ERROR', 'MOTIVO_ERROR'
            ]]
            
            df_errores_factor_conversion.append(df_temp_error)

    # Combinar todos los errores y filtrar DataFrame principal
    if df_errores_factor_conversion:
        df_reporte_errores_factor_conversion = pd.concat(df_errores_factor_conversion, ignore_index=True)
        
        # CAMBIO: Obtener SKUs problemáticos directamente del reporte de errores
        skus_con_errores = set(df_reporte_errores_factor_conversion['COD_SKU_SIN_V'].unique())
        
        # Filtrar df_ficha_tecnica excluyendo SKUs problemáticos
        df_ficha_tecnica = df_ficha_tecnica[~df_ficha_tecnica['COD_SKU_SIN_V'].isin(skus_con_errores)]
    
    # Armado de composicion 
    df_composicion_sku_mp = df_ficha_tecnica[['COD_SKU_SIN_V', 'ID_HOJA_1', 'ID_HOJA_2', 'ID_HOJA_3', 'ID_HOJA_4', 'FACTOR_CONVERSION_ID_HOJA_1', 'FACTOR_CONVERSION_ID_HOJA_2', 'FACTOR_CONVERSION_ID_HOJA_3', 'FACTOR_CONVERSION_ID_HOJA_4']].drop_duplicates().rename(columns={'ID_HOJA_1': 'MP1', 'ID_HOJA_2': 'MP2', 'ID_HOJA_3': 'MP3', 'ID_HOJA_4': 'MP4'})

    # CHANGE: Melt both MP and FACTOR_CONVERSION columns together
    df_composicion_sku_mp_melted = []

    for i in range(1, 5):
        mp_col = f'MP{i}'
        factor_col = f'FACTOR_CONVERSION_ID_HOJA_{i}'
        
        # Create temporary dataframe for each MP
        temp_df = df_composicion_sku_mp[['COD_SKU_SIN_V', mp_col, factor_col]].copy()
        temp_df = temp_df.dropna(subset=[mp_col])  # Remove rows where MP is NaN
        temp_df['CAPA'] = f'MP{i}'
        temp_df = temp_df.rename(columns={mp_col: 'COD_MP', factor_col: 'FACTOR_CONVERSION'})
        
        df_composicion_sku_mp_melted.append(temp_df)

    # Combine all melted dataframes
    df_composicion_sku_mp = pd.concat(df_composicion_sku_mp_melted, ignore_index=True)
    df_composicion_sku_mp['COD_MP_CORTO'] = df_composicion_sku_mp['COD_MP'].apply(
        lambda x: x[:-4] if pd.notna(x) and str(x).startswith('PB') else x
    )
    #Convertir df_ficha_tecnica a excel
    df_ficha_tecnica.to_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx', index=False)

    df_composicion_sku_mp.to_excel('ResultadosEstaticos/Resultados/df_composicion_sku_mp.xlsx', index=False)
    
    # Exportar reporte de errores
    if not df_reporte_errores_factor_conversion.empty:
        df_reporte_errores_factor_conversion.to_excel(
            'ResultadosEstaticos/Errores/df_errores_factor_conversion.xlsx', 
            index=False
        )

    return df_ficha_tecnica

