import pandas as pd
import pickle
from collections import defaultdict

def creacion_conjuntos_parametros(nombre_corrida, categorias_productividad = True):
    # Leer archivos
    #Estáticos
    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx')
    df_consignacion = pd.read_excel('ResultadosEstaticos/Resultados/df_consignacion.xlsx')
    #HARDCODEO FACTOR DE CONVERSION
    # for i in range(1,5):
    #     df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'] = df_ficha_tecnica[f'FACTOR_CONVERSION_ID_HOJA_{i}'].fillna(44) # Rellenar NaN con 44
    df_composicion_sku_mp = pd.read_excel('ResultadosEstaticos/Resultados/df_composicion_sku_mp.xlsx')

    df_homologaciones_validas = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/homologaciones_validas.xlsx')
    df_homologaciones_validas['COD_CLIENTE'] = (
    df_homologaciones_validas['COD_CLIENTE']
    .astype(str)
    .str.replace(r'[^0-9]', '', regex=True)
    .replace('', pd.NA)
    .astype(float)
)

    df_materia_prima_filtrado = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_materia_prima_filtrado.xlsx')

    #Dinámicos
    df_combinaciones_MP_PL_SKU_PROV = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_combinaciones_MP_PL_SKU_PROV.xlsx')
    
    df_forecast = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_forecast.xlsx')
    df_tiempo_transito = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_tiempo_transito.xlsx')
    df_tiempo_transito['ID_CLIENTE'] = (df_tiempo_transito['ID_CLIENTE'].astype(str).str.replace(r'[^0-9]', '', regex=True).replace('', pd.NA).astype(float))
    

    df_costos_fijos_lineas = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costos_fijos_lineas.xlsx')

    df_distribucion = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costo_distribucion.xlsx')
    df_distribucion['ID_CLIENTE'] = (
        df_distribucion['ID_CLIENTE']
        .astype(str)                               # todo a string
        .str.replace(r'[^0-9]', '', regex=True)    # dejar solo dígitos
        .replace('', pd.NA)                        # vacío -> NA
    )
    # Convertir a numérico (lo no convertible queda en NaN)
    df_distribucion['ID_CLIENTE'] = pd.to_numeric(
        df_distribucion['ID_CLIENTE'],
        errors='coerce'
    )
    # Eliminar filas inválidas
    df_distribucion = df_distribucion.dropna(subset=['ID_CLIENTE'])
   
    df_turnos = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_turnos.xlsx')
    df_velocidades = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_velocidades.xlsx')
    df_plantas = pd.read_excel('ResultadosEstaticos/Resultados/df_plantas.xlsx')
    df_costos_indirectos = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costos_indirectos.xlsx')
    df_aranceles = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_aranceles.xlsx')
    df_inventario_inicial = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_inventario_inicial.xlsx')
    df_ordenes_abiertas = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_ordenes_abiertas.xlsx')
    df_stock_cliente_consignacion = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_stock_cliente_consignacion.xlsx')

    # #Archivo de decisiones fijas
    # df_decisiones_fijas = pd.read_excel(f'Rawdata/df_decisiones_fijas.xlsx', sheet_name='Sheet1')
    
    
    #########  
    #SET DE SKU
    set_sku = set(df_homologaciones_validas['COD_SKU_SIN_V'].unique()) 
    print('CANT DE SKU PLANIFICADOS: ', len(set_sku))
   
    #SET PLANTA Y SKU
    set_fabricas_sku = set(
    tuple(x)
    for x in df_homologaciones_validas.loc[
        df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
        ['PLANTA', 'COD_SKU_SIN_V']
    ].to_numpy()
)
    
    # df_combinaciones_MP_PL_SKU_PROV_filtrado por COD_SKU_SIN_V y PLANTA QUE ESTÁN EN set_sku_cliente y cod_sku en set_sku
    df_combinaciones_MP_PL_SKU_PROV_filtrado = df_combinaciones_MP_PL_SKU_PROV[
        df_combinaciones_MP_PL_SKU_PROV.apply(
            lambda row: (row['PLANTA'], row['COD_SKU_SIN_V']) in set_fabricas_sku,
            axis=1
        )
    ].copy()
        


    ######### SETS

    ########UNIDIMENSIONALES

    # CAMBIO 1: SET DE PERIODOS DE TIEMPO - Obtener directamente de columnas numéricas
    columnas_numericas_forecast = [col for col in df_forecast.columns if isinstance(col, (int, float))]
    set_meses_num = sorted(columnas_numericas_forecast)

    set_mes_inicial = {1} 
    
    set_materias_primas = set(
        df_combinaciones_MP_PL_SKU_PROV_filtrado['COD_MP_CORTO'].dropna().values
    )

    #SET DE PROVEEDORES
    set_proveedores = set(
        df_combinaciones_MP_PL_SKU_PROV_filtrado.loc[
            df_combinaciones_MP_PL_SKU_PROV_filtrado['COD_SKU_SIN_V'].isin(set_sku),
            'PROVEEDOR'].dropna().values )                  


    #SET DE PLANTAS
    set_fabricas = set(df_homologaciones_validas["PLANTA"].unique())

    #SET DE LINEAS
    set_lineas = set(df_homologaciones_validas["LINEA"].unique())

    

    #SET DE CLIENTES
    set_clientes = set(
        df_homologaciones_validas.loc[
            df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
            'COD_CLIENTE'
        ].dropna().values
    )
    
    # SET DE PAIS (planta)
    set_paises = set(df_plantas['PLANTA-PAIS'].unique())

    ########MULTIDIMENSIONALES
    ordenes_abiertas = {
        (sku, mes): 0
        for sku in set_sku
        for mes in set_meses_num
    }

    ordenes_abiertas_real = {
        (row['COD_SKU_SIN_V'], row['MES']): row['MILES_SACOS']
        for _, row in df_ordenes_abiertas.iterrows()
        if row['COD_SKU_SIN_V'] in set_sku and row['MES'] in set_meses_num
    }
    
    # Completar todas las combinaciones (sku, mes) con 0 si faltan
    ordenes_abiertas = {
        (sku, mes): ordenes_abiertas_real.get((sku, mes), 0)
        for sku in set_sku
        for mes in set_meses_num
    }
    
    
    #SET SKU Y T 
    set_sku_meses = {
        (row['COD_SKU_SIN_V'], mes)
        for _, row in df_forecast.iterrows()
        for mes in set_meses_num
        if mes in df_forecast.columns and row[mes] > 0 and row['COD_SKU_SIN_V'] in set_sku
    } | {
        (sku, mes)
        for (sku, mes), orden in ordenes_abiertas.items()
        if sku in set_sku and orden > 0
    }

    #SET SKU Y CLIENTE
    set_sku_cliente = set(
        tuple(x)
        for x in df_homologaciones_validas.loc[
            df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
            ['COD_SKU_SIN_V', 'COD_CLIENTE']
        ].to_numpy()
    )
    # Set de MP y PROVEEDOR
    set_materias_primas_proveedores = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO', 'PROVEEDOR']].itertuples(index=False, name=None))

    # Set de MP, PLANTA, PROVEEDOR
    #set_materias_primas_proveedores_fabricas = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO', 'PROVEEDOR', 'PLANTA']].itertuples(index=False, name=None))
    set_materias_primas_proveedores_fabricas = [
    (mp, p, f) 
    for mp, p, f in df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO','PROVEEDOR','PLANTA']].itertuples(index=False, name=None)
    if mp in set_materias_primas and p in set_proveedores and f in set_fabricas
]

    # Set de MP y PLANTA
    set_materias_primas_fabricas = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO', 'PLANTA']].itertuples(index=False, name=None))

    # Set de MP, PLANTA, SKU, PROVEEDOR
    set_materias_primas_fabricas_sku_proveedores = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO', 'PLANTA', 'COD_SKU_SIN_V', 'PROVEEDOR']].itertuples(index=False, name=None))

    # Set de MP y SKU
    set_materias_primas_sku = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['COD_MP_CORTO', 'COD_SKU_SIN_V']].itertuples(index=False, name=None))

    # Set de PROVEEDOR y PLANTA
    set_proveedores_fabricas = set(df_combinaciones_MP_PL_SKU_PROV_filtrado[['PROVEEDOR', 'PLANTA']].itertuples(index=False, name=None))

    #SET DE SKU Y PLANTAS FIJOS
    planta_pais = {'SKCL': 'CHILE','SKPE': 'PERU','SKMX': 'MEXICO','SKBR': 'BRASIL'}
    filtro_planta_pais = df_forecast['PLANTA'].isin(planta_pais) & \
        (df_forecast['PAIS_DESTINO'] == df_forecast['PLANTA'].map(planta_pais))

    # Crear el set de (COD_SKU_V, PLANTA) directamente
    set_sku_planta_fijos = set(zip(df_forecast.loc[filtro_planta_pais, 'COD_SKU_SIN_V'], df_forecast.loc[filtro_planta_pais, 'PLANTA']))

    #SET DE PLANTAS Y LINEAS
    set_fabricas_lineas = set(zip(df_homologaciones_validas["PLANTA"], df_homologaciones_validas['LINEA']))

    #SET DE LINEAS Y SKU
    set_lineas_sku = set(
    tuple(x) 
    for x in df_homologaciones_validas.loc[
        df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
        ['LINEA', 'COD_SKU_SIN_V']
    ].to_numpy()
)
    # #SET PLANTA Y SKU
    # set_fabricas_sku = set(
    #     zip(
    #         df_homologaciones_validas.loc[df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku), 'PLANTA'],
    #         df_homologaciones_validas.loc[df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku), 'COD_SKU_SIN_V']
    #     )
    # )
    

    #SET PLANTA, LINEA Y SKU
    set_fabricas_lineas_sku = set(
    tuple(x)
    for x in df_homologaciones_validas.loc[
        df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
        ['PLANTA', 'LINEA', 'COD_SKU_SIN_V']
    ].to_numpy()
)

    
#     #SET PLANTA Y CLIENTE
#     set_fabricas_clientes = set(
#     tuple(x)
#     for x in df_homologaciones_validas.loc[
#         df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
#         ['PLANTA', 'COD_CLIENTE']
#     ].to_numpy()
# )
    set_fabricas_clientes = set(
    (row['PLANTA'], float(row['COD_CLIENTE']))
    for _, row in df_homologaciones_validas.loc[
        df_homologaciones_validas['COD_SKU_SIN_V'].isin(set_sku),
        ['PLANTA', 'COD_CLIENTE']
    ].iterrows()
)
 
    
    #####################################################################################
    #PARÁMETROS
    #DEMANDA MSC/MES
    df_demanda_real = (
        df_forecast.melt(id_vars=['COD_SKU_SIN_V'], value_vars=set_meses_num, var_name='MES', value_name='DEMANDA')
        .query('COD_SKU_SIN_V in @set_sku'))

    demanda_real = dict(zip(zip(df_demanda_real['COD_SKU_SIN_V'], df_demanda_real['MES']), df_demanda_real['DEMANDA']))
    
    #TIEMPO DE TRANSITO
    df_lead_time_entrega = df_tiempo_transito[
        df_tiempo_transito.apply(
            lambda row: (row['ID_PLANTA'], row['ID_CLIENTE']) in set_fabricas_clientes,
            axis=1)]

    # Armar diccionario lead_time_entrega solo con pares válidos
    lead_time_entrega = {
        (row['ID_PLANTA'], row['ID_CLIENTE']): row['MESES_TRANSITO']
        for _, row in df_lead_time_entrega.iterrows()}

    # ARANCELES
    # 1. SKUs y países del forecast (existente)
    df_sku_pais_forecast = df_forecast[
        df_forecast['COD_SKU_SIN_V'].isin(set_sku)
    ][['COD_SKU_SIN_V', 'PAIS_DESTINO']].drop_duplicates()
    
    # 2. NUEVO - SKUs y países de órdenes abiertas
    if 'PAIS_DESTINO' in df_ordenes_abiertas.columns:
        df_sku_pais_ordenes = df_ordenes_abiertas[
            df_ordenes_abiertas['COD_SKU_SIN_V'].isin(set_sku)
        ][['COD_SKU_SIN_V', 'PAIS_DESTINO']].drop_duplicates()
    else:
        df_sku_pais_ordenes = pd.DataFrame(columns=['COD_SKU_SIN_V', 'PAIS_DESTINO'])
    
    # 3. NUEVO - SKUs y países de stock consignación
    if 'PAIS_DESTINO' in df_stock_cliente_consignacion.columns:
        df_sku_pais_stock = df_stock_cliente_consignacion[
            df_stock_cliente_consignacion['COD_SKU_SIN_V'].isin(set_sku)
        ][['COD_SKU_SIN_V', 'PAIS_DESTINO']].drop_duplicates()
    else:
        df_sku_pais_stock = pd.DataFrame(columns=['COD_SKU_SIN_V', 'PAIS_DESTINO'])
    
    # 4. NUEVO - Combinar todas las fuentes de SKU-PAIS
    df_sku_pais_combinado = pd.concat([
        df_sku_pais_forecast,
        df_sku_pais_ordenes,
        df_sku_pais_stock
    ], ignore_index=True).drop_duplicates()
    
    # 5. Obtener plantas válidas para cada SKU
    df_sku_planta_validos = df_homologaciones_validas[['COD_SKU_SIN_V', 'PLANTA']].drop_duplicates()
    
    # 6. CAMBIO - Mergear combinación SKU-PAIS con plantas válidas
    df_skus_planta_pais_validos = pd.merge(
        df_sku_pais_combinado, 
        df_sku_planta_validos, 
        on='COD_SKU_SIN_V', 
        how='inner'  # Solo mantener SKUs que tienen plantas válidas
    )
    
    df_arancel_planta_pais = df_aranceles[['PLANTA', 'PAIS_DESTINO', 'ARANCEL']].drop_duplicates()
    
    df_sku_planta_pais_arancel = pd.merge(
        df_skus_planta_pais_validos, 
        df_arancel_planta_pais, 
        on=['PLANTA', 'PAIS_DESTINO'], 
        how='left'
    )
    df_sku_planta_pais_arancel['ARANCEL'] = df_sku_planta_pais_arancel['ARANCEL'].fillna(0)
    
    arancel_sku_planta = {
        (row['PLANTA'], row['COD_SKU_SIN_V']): row['ARANCEL']
        for _, row in df_sku_planta_pais_arancel.iterrows()
    }
   
    # DISPONIBILIDAD DE TURNOS POR LINEA (incluye descuentos por detenciones operacionales)
    turnos_disponibles = {
        (row['LINEA'], mes): row[mes]
        for _, row in df_turnos.iterrows()
        for mes in set_meses_num
        if row['LINEA'] in set_lineas and mes in df_turnos.columns
    }

    # HORAS POR TURNO POR LINEA
    horas_turno_mes = {
        (row['LINEA'], mes): row[f'HORAS/TURNO {mes}']
        for _, row in df_turnos.iterrows()
        for mes in set_meses_num
        if row['LINEA'] in set_lineas
    }

    #CAPACIDAD POR LINEA (HORAS/MES)
    capacidad_linea = {k: v * horas_turno_mes[k] for k, v in turnos_disponibles.items()} #horas/mes
    
    #PROMEDIO
    # velocidad_produccion = df_velocidades[df_velocidades['LINEA'].isin(set_lineas)].groupby('LINEA')['VELOCIDAD (SC/H)'].mean().to_dict()
    
    #VELOCIDAD DE PRODUCCION 
    if categorias_productividad:
        # Crear mapeo de planta a columna de categoría
        planta_to_categoria_col = {
            'SKCL': 'CATEGORIA_SKU_SKCL',
            'SKPE': 'CATEGORIA_SKU_SKPE', 
            'SKMX-G': 'CATEGORIA_SKU_SKMX_G',
            'SKMX-I': 'CATEGORIA_SKU_SKMX_I',
            'SKBR-CN': 'CATEGORIA_SKU_SKBR_CN',
            'SKBR-PS': 'CATEGORIA_SKU_SKBR_PS'
        }
        
        # Crear mapeo de línea a planta desde df_homologaciones_validas
        linea_to_planta = dict(zip(df_homologaciones_validas['LINEA'], df_homologaciones_validas['PLANTA']))
        
        # Crear velocidad_produccion con keys (linea, sku)
        velocidad_produccion = {}
        
        for (linea, sku) in set_lineas_sku:
            # Obtener planta de la línea
            planta = linea_to_planta.get(linea)
            
            # Obtener categorías disponibles para esta línea y planta
            categorias_disponibles = set(
                df_velocidades[
                    (df_velocidades['LINEA'] == linea) & 
                    (df_velocidades['PLANTA'] == planta)
                ]['CATEGORIA'].dropna().unique()
            )
            
            velocidad_asignada = False
            
            if planta and planta in planta_to_categoria_col and categorias_disponibles:
                # Obtener columna de categoría para esta planta
                col_categoria = planta_to_categoria_col[planta]
                
                # Buscar categoría del SKU en ficha técnica
                sku_rows = df_ficha_tecnica[df_ficha_tecnica['COD_SKU_SIN_V'] == sku]
                
                if not sku_rows.empty and col_categoria in sku_rows.columns:
                    categoria_sku = sku_rows.iloc[0][col_categoria]
                    
                    # Si hay categoría válida Y está disponible para la línea
                    if (pd.notna(categoria_sku) and 
                        categoria_sku != '' and 
                        categoria_sku in categorias_disponibles):
                        
                        velocidad_rows = df_velocidades[
                            (df_velocidades['LINEA'] == linea) &
                            (df_velocidades['CATEGORIA'] == categoria_sku) &
                            (df_velocidades['PLANTA'] == planta)
                        ]
                        
                        if not velocidad_rows.empty:
                            velocidad_especifica = velocidad_rows.iloc[0]['VELOCIDAD (SC/H)']
                            
                            if velocidad_especifica > 0:
                                velocidad_produccion[(linea, sku)] = velocidad_especifica
                                velocidad_asignada = True
            
            # Solo usar promedio si no se pudo asignar velocidad específica
            if not velocidad_asignada:
                velocidad_promedio = df_velocidades[
                    (df_velocidades['LINEA'] == linea) & 
                    (df_velocidades['PLANTA'] == planta)
                ]['VELOCIDAD (SC/H)'].mean()
                
                if pd.notna(velocidad_promedio):
                    velocidad_produccion[(linea, sku)] = velocidad_promedio
                else:
                    # Último fallback: valor por defecto
                    velocidad_produccion[(linea, sku)] = 1

    else:
        # CAMBIO: Caso categorias_productividad = False: promedio por línea para cada SKU
        velocidad_produccion = {}
        
        # Crear mapeo de línea a planta
        linea_to_planta = dict(zip(df_homologaciones_validas['LINEA'], df_homologaciones_validas['PLANTA']))
        
        # Calcular promedio por línea y planta
        velocidad_promedio_linea_planta = {}
        for linea in set_lineas:
            planta = linea_to_planta.get(linea)
            if planta:
                promedio = df_velocidades[
                    (df_velocidades['LINEA'] == linea) & 
                    (df_velocidades['PLANTA'] == planta)
                ]['VELOCIDAD (SC/H)'].mean()
                velocidad_promedio_linea_planta[linea] = promedio if pd.notna(promedio) else 1
        
        # Asignar a cada combinación (linea, sku) - ESTO ES LO CLAVE
        for (linea, sku) in set_lineas_sku:
            velocidad_produccion[(linea, sku)] = velocidad_promedio_linea_planta.get(linea, 1)

    #CONSIGNACION
    #Parametro que devuelva el promedio de la demanda de todos los sku_validos para el listado de clientes que está en df_consignacion[COD_CLIENTE] por df_consignacion[CONSIGNACION]
    stock_consignacion_target = (
    df_homologaciones_validas
    .merge(df_consignacion[['ID_CLIENTE', 'CONSIGNACION']], left_on='COD_CLIENTE', right_on='ID_CLIENTE')
    .merge(df_demanda_real.groupby('COD_SKU_SIN_V', as_index=False)['DEMANDA'].mean(), on='COD_SKU_SIN_V')
    .assign(STOCK=lambda d: d['DEMANDA'] * d['CONSIGNACION']/30)
    .groupby('COD_SKU_SIN_V')['STOCK'].mean()
    .to_dict())
    
    stock_consignacion_target = {sku: stock_consignacion_target.get(sku, 0) for sku in set_sku}
   
    
    # STOCK CLIENTE CONSIGNACION
    stock_por_sku = df_stock_cliente_consignacion.groupby('COD_SKU_SIN_V')['MILES_SACOS'].sum()
    stock_actual_cliente = {sku: stock_por_sku.get(sku, 0) for sku in set_sku}

    #INVENTARIO INICIAL DE SKU POR FABRICA SOLO PRIMER MES DEL HORIZONTE
    df_inventario_inicial['MES_INICIAL'] = 1 #set_mes_inicial
    df_sku_planta_inventario = df_inventario_inicial.groupby(['COD_SKU_SIN_V', 'PLANTA', 'MES_INICIAL']).agg({'INVENTARIO_DISPONIBLE':'sum'}).reset_index()
    
    inventario_inicial_sku_fabrica = {
        (fabrica, sku, mes_inicial): 0
        for (fabrica, sku) in set_fabricas_sku
        for mes_inicial in set_mes_inicial
    }
    
    inventario_inicial_sku_fabrica_real = {
        (row['PLANTA'], row['COD_SKU_SIN_V'],  row['MES_INICIAL']): row['INVENTARIO_DISPONIBLE']
        for _, row in df_sku_planta_inventario.iterrows()
    }
    
    inventario_inicial_sku_fabrica.update({
    k: v
    for k, v in inventario_inicial_sku_fabrica_real.items()
    if k in inventario_inicial_sku_fabrica
})
    #CÁLCULO DE SKUS A COMPLETAR SS TARGET
    SS_faltante = {
        sku: max(0, round(stock_consignacion_target[sku] - stock_actual_cliente[sku]))
        for sku in set_sku
    }

    #FACTOR DE CONVERSION g/saco
    # factor_conversion = {
    #     (id_hoja_corto, fila['COD_SKU_SIN_V']): factor
    #     for _, fila in df_ficha_tecnica.iterrows()
    #     for i in range(1, 5)
    #     for id_hoja, factor in [(fila.get(f'ID_HOJA_{i}'), fila.get(f'FACTOR_CONVERSION_ID_HOJA_{i}'))]
    #     for id_hoja_corto in [id_hoja[:-4] if str(id_hoja).startswith("PB") and len(str(id_hoja)) > 4 else str(id_hoja)]
    #     if (
    #         pd.notna(id_hoja) 
    #         and pd.notna(factor) 
    #         and id_hoja_corto in set_materias_primas  # Usar id_hoja_corto
    #         and fila['COD_SKU_SIN_V'] in set_sku
    #         and (id_hoja_corto, fila['COD_SKU_SIN_V']) in set_materias_primas_sku  # Usar id_hoja_corto
    #     )
    # }
    
    factor_conversion_grouped = (
        df_composicion_sku_mp
        .groupby(['COD_SKU_SIN_V', 'COD_MP_CORTO'])['FACTOR_CONVERSION']
        .sum()
        .reset_index()
    )
    
    factor_conversion = {
        (row['COD_MP_CORTO'], row['COD_SKU_SIN_V']): row['FACTOR_CONVERSION']
        for _, row in factor_conversion_grouped.iterrows()
        if (
            row['COD_MP_CORTO'] in set_materias_primas
            and row['COD_SKU_SIN_V'] in set_sku
            and (row['COD_MP_CORTO'], row['COD_SKU_SIN_V']) in set_materias_primas_sku
            and pd.notna(row['FACTOR_CONVERSION'])
            and pd.notna(row['COD_MP_CORTO'])
        )
    }

    
    #COSTO ABASTECIMIENTO USD/TON
    df_materia_prima_filtrado_filtrado_mp_corto = df_materia_prima_filtrado.groupby(['COD_MP_CORTO', 'PROVEEDOR', 'PLANTA']).agg({'COSTO ABASTECIMIENTO (USD/TON)': 'first'}).reset_index()
    costo_abastecimiento = {
        (mp, proveedor, fabrica): row['COSTO ABASTECIMIENTO (USD/TON)']
        for mp, proveedor, fabrica, row in [
            (*tup, df_materia_prima_filtrado_filtrado_mp_corto[
                (df_materia_prima_filtrado_filtrado_mp_corto['COD_MP_CORTO'] == tup[0]) &
                (df_materia_prima_filtrado_filtrado_mp_corto['PROVEEDOR'] == tup[1]) &
                (df_materia_prima_filtrado_filtrado_mp_corto['PLANTA'] == tup[2])
            ].iloc[0])
            for tup in set_materias_primas_proveedores_fabricas
        ]
    }
    #COSTO DISTRIBUCION US$/SACO
    costo_distribucion = {
        (cliente, fabrica): row['COSTO (US$/SACO)']
        for cliente in set_clientes
        for fabrica in set_fabricas
        for _, row in df_distribucion[
            (df_distribucion['ID_CLIENTE'] == cliente) &
            (df_distribucion['ID_PLANTA'] == fabrica)
        ].iterrows()
    }

    #COSTO PRODUCCION US$/SACO
    costo_produccion = { sku: row['COSTO INDIRECTO (US$/SACO)']
                        for sku in set_sku
                        for _, row in df_costos_indirectos[
                            (df_costos_indirectos['COD_SKU_SIN_V'] == sku)
                        ].iterrows()
    }

    #COSTO FIJO POR USO DE LA LINEA
    costos_fijos_lineas = {
    linea: costo 
    for linea, costo in zip(df_costos_fijos_lineas['LINEA'], df_costos_fijos_lineas['COSTO_TOTAL_LINEA'])
    if linea in set_lineas
}
    ######################################
    ####  AGREGADO COSTO HORA EXTRA   ####
    ######################################
    costo_hora_extra = {}

    for linea in set_lineas:
        # Obtener costo fijo de la línea
        costo_fijo = costos_fijos_lineas.get(linea, 0)
        
        # Calcular capacidad promedio mensual de la línea (en horas)
        capacidades_linea = [cap for (l, mes), cap in capacidad_linea.items() if l == linea]
        
        if capacidades_linea and sum(capacidades_linea) > 0:
            capacidad_promedio = sum(capacidades_linea) / len(capacidades_linea)
            costo_hora_extra[linea] = (costo_fijo / capacidad_promedio) * 2
        else:
            # Fallback: si no hay capacidad, usar 0
            costo_hora_extra[linea] = 0 
    
    #DEMANDA INTERNA
    # 1. SKUs candidatos: forecast, órdenes abiertas y SS_faltante
    skus_candidatos = (
        set(df_forecast['COD_SKU_SIN_V'])
        | set(df_ordenes_abiertas['COD_SKU_SIN_V'])
        | set(SS_faltante.keys())
    )

    # 2. Filtrar en ficha técnica: solo los que tienen 'on' en demanda interna
    skus_validos_ft = df_ficha_tecnica.loc[
        (df_ficha_tecnica['COD_SKU_SIN_V'].isin(skus_candidatos)),
        ['COD_SKU_SIN_V', 'PAIS_DESTINO']
    ]

    # 3. Traer la planta desde homologaciones
    skus_validos_planta = pd.merge(skus_validos_ft,df_homologaciones_validas[['COD_SKU_SIN_V', 'PLANTA']], on='COD_SKU_SIN_V', how='inner' )

    # Función de mapeo
    def map_planta_to_pais(planta):
        if planta in ['SKBR-CN', 'SKBR-PS']:
            return 'BRASIL'
        elif planta in ['SKMX-G', 'SKMX-I']:
            return 'MEXICO'
        elif planta in ['SKCL']:
            return 'CHILE'
        elif planta in ['SKPE']:
            return 'PERU'
        else:
            return planta
    
    # Agregar columna PAIS_PLANTA usando la función de mapeo
    skus_validos_planta['PAIS_PLANTA'] = skus_validos_planta['PLANTA'].apply(map_planta_to_pais)


    # 4. Crear el set (planta, sku)
    # Filtrar solo los registros donde PAIS_DESTINO coincide con PAIS_PLANTA
    df_filtrado = skus_validos_planta[
        skus_validos_planta['PAIS_DESTINO'] == skus_validos_planta['PAIS_PLANTA']
    ]

    # Crear el conjunto
    set_demanda_interna = set(
        zip(df_filtrado['PLANTA'], df_filtrado['COD_SKU_SIN_V'])
    )


    set_sku_dem_int = set(df_filtrado['COD_SKU_SIN_V'])
   
    
    #SET SKU Y T=1 (DEM, SS Y ORD_AB)
    set_sku_meses1 = {
        (row['COD_SKU_SIN_V'], mes)
        for _, row in df_forecast.iterrows()
        for mes in set_meses_num
        if mes in df_forecast.columns 
        and row[mes] > 0 
        and row['COD_SKU_SIN_V'] in set_sku
        and mes == 1
    } | {  # union con los pares de SS_faltante
        (sku, 1)
        for sku, faltante in SS_faltante.items()
        if sku in set_sku and faltante > 0
    } | {
        (sku, mes)
        for (sku, mes), orden in ordenes_abiertas.items()
        if sku in set_sku and mes == 1 and orden > 0
    }
    #SET SKU Y T QUE CONTEMPLA TODOS LOS PARES DEL HORIZONTE CONTEMPLADO (DEM, SS Y ORD_AB)
    set_sku_meses_completo = {
        (row['COD_SKU_SIN_V'], mes)
        for _, row in df_forecast.iterrows()
        for mes in set_meses_num
        if mes in df_forecast.columns 
        and row[mes] > 0 
        and row['COD_SKU_SIN_V'] in set_sku

    } | {  # union con los pares de SS_faltante
        (sku, 1)
        for sku, faltante in SS_faltante.items()
        if sku in set_sku and faltante > 0
    } | {
        (sku, mes)
        for (sku, mes), orden in ordenes_abiertas.items()
        if sku in set_sku and orden > 0
    }

    set_sku_mes_linea = {
    (sku, mes, linea)
    for (sku, mes) in set_sku_meses_completo   
    for (linea, sku2) in set_lineas_sku
    if sku == sku2
}
        
    #SET PLANTA SKU MES
    set_fabrica_sku_mes = {
    (planta, sku, mes)
    for (planta, sku) in set_fabricas_sku 
    for (sku2, mes) in set_sku_meses_completo
    if sku == sku2
    }
    
    
    set_sku_mes_linea_mes = {
        (sku, mes, linea, mes2)
        for (sku, mes, linea) in set_sku_mes_linea
        for mes2 in set_meses_num 
        for (f, c) in set_fabricas_clientes 
        if mes2 <= mes - lead_time_entrega[f, c] and (f, sku) in set_fabricas_sku
        and (sku, c) in set_sku_cliente and (f,linea) in set_fabricas_lineas
    }

        #SET DE SKU, MES, PLANTA Y CLIENTE
    set_sku_mes_planta_cliente = {
    (sku, mes, row['PLANTA'], row['COD_CLIENTE'])
    for (sku, mes) in set_sku_meses_completo  
    for _, row in df_homologaciones_validas[df_homologaciones_validas['COD_SKU_SIN_V'] == sku].iterrows()
}
    
    # 1. Contar meses por SKU
    sku_to_meses = defaultdict(set)
    for sku, mes in set_sku_meses_completo:
        sku_to_meses[sku].add(mes)

    # 2. Filtrar SKUs con más de 2 meses
    skus_validos_demanda = {sku for sku, meses in sku_to_meses.items() if len(meses) >= 2}
    
    # 3. Determinar último mes de cada SKU válido
    ultimo_mes = {sku: max(meses) for sku, meses in sku_to_meses.items() if sku in skus_validos_demanda}
    
    # 4. Armar set excluyendo el último mes de cada SKU
    set_fabrica_sku_mes2 = {
        (planta, sku, mes)
        for (planta, sku) in set_fabricas_sku
        for (sku2, mes) in set_sku_meses_completo
        if sku == sku2 and sku in skus_validos_demanda and mes != ultimo_mes[sku]
    }
    #SE ACTUALIZA LA DEMANDA PARA TODOS LOS PARES SKU,T EXISTENTES

    demanda_real = {
        k: demanda_real.get(k, 0)
        for k in set_sku_meses_completo
    }

    #SET DE LINEA, SKU, MES, PLANTA Y CLIENTE
    set_linea_sku_mes_planta_cliente = {
    (row['LINEA'], sku, mes, row['PLANTA'], row['COD_CLIENTE'])
    for sku in set_sku # todos los SKUs válidos
    for mes in set_meses_num 
    for _, row in df_homologaciones_validas[df_homologaciones_validas['COD_SKU_SIN_V'] == sku].iterrows()
    if (row['LINEA'], sku) in set_lineas_sku and
         (row['PLANTA'], row['LINEA']) in set_fabricas_lineas
}
    
#     #SET DE SKU - T_D - L - TP 
#     set_decisiones_fijas = set(
#     tuple(row) for row in df_decisiones_fijas[['SKU', 'T_d', 'L', 'TP']].values if (row[0], row[1], row[2]) in set_sku_mes_linea
# )
    
    # Agrupamos todo en un diccionario
    datos_a_guardar = {
        'set_meses': set_meses_num,
        'set_mes_inicial': set_mes_inicial,
        'set_materias_primas': set_materias_primas,
        'set_proveedores': set_proveedores,
        'set_fabricas': set_fabricas,
        'set_lineas': set_lineas,
        'set_sku': set_sku,
        'set_clientes': set_clientes,
        'set_paises': set_paises,
        'set_fabricas_sku': set_fabricas_sku,
        'set_fabrica_sku_mes': set_fabrica_sku_mes,
        'set_sku_mes_linea': set_sku_mes_linea,
        'set_sku_meses': set_sku_meses,
        'set_sku_meses1': set_sku_meses1,
        'set_sku_meses_completo': set_sku_meses_completo,
        'set_materias_primas_proveedores': set_materias_primas_proveedores,
        'set_materias_primas_fabricas': set_materias_primas_fabricas,
        'set_materias_primas_sku': set_materias_primas_sku,
        'set_materias_primas_proveedores_fabricas': set_materias_primas_proveedores_fabricas,
        'set_materias_primas_fabricas_sku_proveedores': set_materias_primas_fabricas_sku_proveedores,
        'set_proveedores_fabricas': set_proveedores_fabricas,
        'set_sku_planta_fijos': set_sku_planta_fijos,
        'set_fabrica_sku_mes2': set_fabrica_sku_mes2,
        'set_fabricas_lineas': set_fabricas_lineas,
        'set_lineas_sku': set_lineas_sku,
        'set_demanda_interna':set_demanda_interna,
        'set_sku_dem_int' : set_sku_dem_int,
        'set_fabricas_lineas_sku': set_fabricas_lineas_sku,
        'set_fabricas_clientes': set_fabricas_clientes,
        'set_sku_mes_planta_cliente': set_sku_mes_planta_cliente,
        'set_linea_sku_mes_planta_cliente': set_linea_sku_mes_planta_cliente,
        # 'set_decisiones_fijas': set_decisiones_fijas,
        'costos_fijos_lineas': costos_fijos_lineas,
        'costo_hora_extra': costo_hora_extra,
        'set_sku_cliente': set_sku_cliente,
        'set_sku_mes_linea_mes': set_sku_mes_linea_mes,
        'demanda': demanda_real,
        'arancel_sku_planta': arancel_sku_planta,
        'lead_time_entrega': lead_time_entrega,
        'SS_faltante': SS_faltante,
        'ordenes_abiertas': ordenes_abiertas,
        'inventario_inicial_sku_fabrica': inventario_inicial_sku_fabrica,
        'turnos_disponibles': turnos_disponibles,
        'horas_turno_mes': horas_turno_mes,
        'capacidad_linea': capacidad_linea,
        'velocidad_produccion': velocidad_produccion,
        'factor_conversion': factor_conversion,
        'costo_abastecimiento': costo_abastecimiento,
        'costo_produccion': costo_produccion,
        'costo_distribucion': costo_distribucion,
    }

    # Guardar en pickle
    with open(f'Corridas/{nombre_corrida}/Preprocesamiento/datos_completos.pkl', 'wb') as f:
        pickle.dump(datos_a_guardar, f)

    return datos_a_guardar