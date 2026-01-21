import pandas as pd

def algoritmo_validacion_forecast_ordenes_abiertas(nombre_corrida, df_homologaciones, df_forecast, df_ordenes_abiertas):
    """
    El Algoritmo contempla nomás aquellas homologaciones de SKUs que están en el forecast
    Se obtiene df_homologaciones_filtrado y df_homologaciones_sin_forecast para indicar aquellas que no fueron contempladas
    """
    # Obtener SKUs únicos de cada fuente
    skus_con_forecast = set(df_forecast['COD_SKU_SIN_V'].unique())
    skus_con_ordenes_abiertas = set(df_ordenes_abiertas['COD_SKU_SIN_V'].unique())
    skus_con_homologaciones = set(df_homologaciones['COD_SKU_SIN_V'].unique())
    
    # Unir ambos conjuntos (SKUs que están en forecast O en órdenes abiertas)
    skus_con_demanda = skus_con_forecast.union(skus_con_ordenes_abiertas)
    
    # VALIDACIÓN 1: Homologaciones que tienen demanda
    df_homologaciones_con_demanda = df_homologaciones[
        df_homologaciones['COD_SKU_SIN_V'].isin(skus_con_demanda)
    ]
    
    # Homologaciones sin demanda
    df_homologaciones_sin_demanda = df_homologaciones[
        ~df_homologaciones['COD_SKU_SIN_V'].isin(skus_con_demanda)
    ]
    df_homologaciones_sin_demanda['MOTIVO_ERROR'] = 'El SKU no está en el forecast ni en órdenes abiertas'
    
    # VALIDACIÓN 2: SKUs con demanda que no tienen homologaciones (camino inverso)
    skus_sin_homologaciones = skus_con_demanda - skus_con_homologaciones
    
    # Crear DataFrame de errores de SKUs con demanda sin homologaciones
    df_skus_demanda_sin_homologaciones = pd.DataFrame()
    
    if skus_sin_homologaciones:
        registros_errores = []
        
        for sku in skus_sin_homologaciones:
            # Determinar en qué fuente(s) está el SKU
            en_forecast = sku in skus_con_forecast
            en_ordenes = sku in skus_con_ordenes_abiertas
            
            if en_forecast and en_ordenes:
                fuente = 'Está en forecast y órdenes abiertas'
            elif en_forecast:
                fuente = 'Está solo en forecast'
            else:  # en_ordenes
                fuente = 'Está solo en órdenes abiertas'
            
            registros_errores.append({
                'COD_SKU_SIN_V': sku,
                'MOTIVO_ERROR': f'SKU con demanda sin homologaciones válidas - {fuente}'
            })
        
        df_skus_demanda_sin_homologaciones = pd.DataFrame(registros_errores)
    
    # Exportar archivos
    df_homologaciones_sin_demanda.to_excel(f'Corridas/{nombre_corrida}/Errores/errores_homologaciones_sin_demanda.xlsx', index=False)
    df_homologaciones_con_demanda.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_homologaciones_con_demanda.xlsx', index=False)
    
    # Exportar nuevo reporte de SKUs con demanda sin homologaciones
    if not df_skus_demanda_sin_homologaciones.empty:
        df_skus_demanda_sin_homologaciones.to_excel(f'Corridas/{nombre_corrida}/Errores/errores_skus_demanda_sin_homologaciones.xlsx', index=False)
    
    return df_homologaciones_con_demanda

def algoritmo_validacion_produccion(nombre_corrida, df_homologaciones, df_costos_indirectos, df_turnos, df_velocidades):
    """
    El Algoritmo filtra las homologaciones según si hay costo de produccion para los sku, y las lineas contempladas tienen turnos asignados y velocidades de produccion
    """
    # Costos indirectos
    skus_con_costos_indirectos = df_costos_indirectos['COD_SKU_SIN_V'].unique()
    
    df_homologaciones_con_costos = df_homologaciones[df_homologaciones['COD_SKU_SIN_V'].isin(skus_con_costos_indirectos)]

    df_homologaciones_sin_costos = df_homologaciones[~df_homologaciones['COD_SKU_SIN_V'].isin(skus_con_costos_indirectos)]
    df_homologaciones_sin_costos['MOTIVO_ERROR'] = 'El SKU no tiene costo de producción'
    
    # Lineas turnos
    lineas_con_turnos = df_turnos['LINEA'].unique()

    df_homologaciones_con_turnos = df_homologaciones_con_costos[df_homologaciones_con_costos['LINEA'].isin(lineas_con_turnos)]

    df_homologaciones_sin_turnos = df_homologaciones_con_costos[~df_homologaciones_con_costos['LINEA'].isin(lineas_con_turnos)]
    df_homologaciones_sin_turnos['MOTIVO_ERROR'] = 'El SKU no tiene turnos asignados'

    # Lineas velocidades
    lineas_con_velocidades = df_velocidades['LINEA'].unique()

    df_homologaciones_con_velocidades = df_homologaciones_con_turnos[df_homologaciones_con_turnos['LINEA'].isin(lineas_con_velocidades)]
    
    df_homologaciones_sin_velocidades = df_homologaciones_con_turnos[~df_homologaciones_con_turnos['LINEA'].isin(lineas_con_velocidades)]
    df_homologaciones_sin_velocidades['MOTIVO_ERROR'] = 'El SKU no tiene velocidades asignadas'

    # Exportar archivo de errores de produccion
    df_homologaciones_sin_datos_produccion = pd.concat([
        df_homologaciones_sin_costos,
        df_homologaciones_sin_turnos,
        df_homologaciones_sin_velocidades
    ])

    df_homologaciones_sin_datos_produccion.to_excel(f'Corridas/{nombre_corrida}/Errores/errores_homologaciones_sin_datos_produccion.xlsx', index=False)
    
    # Generación de homologaciones validas
    df_homologaciones_con_datos_produccion = df_homologaciones_con_velocidades.copy()

    return df_homologaciones_con_datos_produccion

def algoritmo_validacion_abastecimiento(nombre_corrida, df_materia_prima, df_homologaciones, df_ficha_tecnica):
    """
    El Algoritmo Generador de Validaciones crea el universo de posibles relaciones entre 
    Materia Prima, Proveedor, SKU y Planta.
    """

    # Filtrar solo los SKU que están en las combinaciones válidas
    df_filtrado_SKU = df_ficha_tecnica[
        df_ficha_tecnica['COD_SKU_SIN_V'].isin(df_homologaciones['COD_SKU_SIN_V'])
    ][['COD_SKU', 'COD_SKU_SIN_V'] + [col for col in df_ficha_tecnica.columns if col.startswith('ID_HOJA_')]].copy()
    
    # Hacer un melt de todas las columnas ID_HOJA_x
    df_melted = pd.melt(
        df_filtrado_SKU,
        id_vars=['COD_SKU', 'COD_SKU_SIN_V'],  
        value_vars=[col for col in df_ficha_tecnica.columns if col.startswith('ID_HOJA_')],
        var_name='VARIABLE',
        value_name='COD_MP'
    )

    # Eliminar filas con COD_MP nulo (NaN)
    df_melted = df_melted.dropna(subset=['COD_MP'])

    df_combinaciones_MP_PL_SKU_PROV = df_melted.merge(
    df_homologaciones[['COD_SKU_SIN_V', 'PLANTA']],  
    how='left',
    on='COD_SKU_SIN_V'
)


    df_combinaciones_MP_PL_SKU_PROV = df_combinaciones_MP_PL_SKU_PROV[['COD_MP', 'PLANTA', 'COD_SKU', 'COD_SKU_SIN_V']] 

    # Normalizar columnas clave para evitar duplicados por espacios o tipos distintos
    for col in ['COD_MP', 'PLANTA', 'COD_SKU_SIN_V']:
        df_combinaciones_MP_PL_SKU_PROV[col] = df_combinaciones_MP_PL_SKU_PROV[col].astype(str).str.strip().str.upper()

    # Eliminar duplicados exactos
    df_combinaciones_MP_PL_SKU_PROV.drop_duplicates(inplace=True)

    # Lista de COD_MP válidos desde df_materia_prima (solo COD_MP)
    codigos_mp_validos = df_materia_prima['COD_MP'].dropna().astype(str).str.strip().str.upper().unique()

    # Agregar datos desde df_materia_prima (solo usando COD_MP)
    df_aux = df_materia_prima[['COD_MP', 'COD_MP_CORTO', 'PLANTA', 'PROVEEDOR', 'COSTO ABASTECIMIENTO (USD/TON)']].copy()
    df_aux[['COD_MP', 'COD_MP_CORTO', 'PLANTA']] = df_aux[['COD_MP', 'COD_MP_CORTO', 'PLANTA']].astype(str).apply(lambda x: x.str.strip().str.upper())

    # Merge usando solo COD_MP
    df_combinaciones_MP_PL_SKU_PROV = df_combinaciones_MP_PL_SKU_PROV.merge(
        df_aux, on=['COD_MP', 'PLANTA'], how='left'
    )
    
    #####################################################
    # Clasificar proveedor considerando solo COD_MP
    def clasificar_proveedor(row):
        if row['COD_MP'] not in codigos_mp_validos:
            return "No está el MP en el listado"
        elif pd.isna(row['PROVEEDOR']):
            return "No tiene proveedor asociado"
        elif pd.isna(row['COSTO ABASTECIMIENTO (USD/TON)']):
            return "No hay costo asociado"
        else:
            return row['PROVEEDOR']
    
        
    df_combinaciones_MP_PL_SKU_PROV['PROVEEDOR'] = df_combinaciones_MP_PL_SKU_PROV.apply(clasificar_proveedor, axis=1)

    # Definir errores
    errores = [
        "No está el MP en el listado",
        "No tiene proveedor asociado",
        "No hay costo asociado",
        "No está el COD_SKU en Ficha técnica"
    ]

    # Crear df_reporte_errores_abastecimiento con filas que contienen errores
    df_reporte_errores_abastecimiento = df_combinaciones_MP_PL_SKU_PROV[
        df_combinaciones_MP_PL_SKU_PROV['PROVEEDOR'].isin(errores)
    ].copy()

    # Eliminar errores del principal
    df_combinaciones_MP_PL_SKU_PROV = df_combinaciones_MP_PL_SKU_PROV[
        ~df_combinaciones_MP_PL_SKU_PROV['PROVEEDOR'].isin(errores)
    ].copy()
    
    df_reporte_errores_abastecimiento = df_reporte_errores_abastecimiento.drop(
    columns=["COSTO ABASTECIMIENTO (USD/TON)"]
)
    #####################################################
    
    #Verificación de SKUs incompletos
    registros = []
    max_faltantes = 0  

    for _, fila in df_homologaciones.iterrows():
        sku = str(fila['COD_SKU_SIN_V']).strip().upper()
        planta = str(fila['PLANTA']).strip().upper()

        fila_ft = df_ficha_tecnica[df_ficha_tecnica['COD_SKU_SIN_V'] == sku]
        if fila_ft.empty:
            continue

        mps_esperadas = [
            str(mp).strip().upper()
            for col in fila_ft.columns if col.startswith('ID_HOJA_')
            for mp in [fila_ft[col].values[0]]
            if pd.notna(mp)
        ]

        mps_encontradas = df_combinaciones_MP_PL_SKU_PROV[
            (df_combinaciones_MP_PL_SKU_PROV['COD_SKU_SIN_V'] == sku) &
            (df_combinaciones_MP_PL_SKU_PROV['PLANTA'] == planta)
        ]['COD_MP'].unique()

        mps_faltantes = [mp for mp in mps_esperadas if mp not in mps_encontradas]

        if mps_faltantes:
            max_faltantes = max(max_faltantes, len(mps_faltantes))
            registro = {
                'COD_SKU_SIN_V': sku,
                'PLANTA': planta,
                'CANTIDAD_FALTANTES': len(mps_faltantes),
                'CANTIDAD_TOTAL_ESPERADA': len(mps_esperadas)
            }
            # Agregar cada MP faltante en una columna separada
            for i, mp in enumerate(mps_faltantes, start=1):
                registro[f'MP_FALTANTE_{i}'] = mp
            registros.append(registro)

    # Convertir a DataFrame
    df_skus_incompletos = pd.DataFrame(registros)
    if not df_skus_incompletos.empty:
        # Asegurar que todas las columnas MP_FALTANTE_n existan aunque no todos tengan el mismo número
        for i in range(1, max_faltantes + 1):
            col = f'MP_FALTANTE_{i}'
            if col not in df_skus_incompletos.columns:
                df_skus_incompletos[col] = None

        # Reordenar columnas para que queden prolijas
        cols_base = ['COD_SKU_SIN_V', 'PLANTA', 'CANTIDAD_FALTANTES', 'CANTIDAD_TOTAL_ESPERADA']
        cols_mps = [f'MP_FALTANTE_{i}' for i in range(1, max_faltantes + 1)]
        df_skus_incompletos = df_skus_incompletos[cols_base + cols_mps]
        # Eliminar duplicados de filas completas
        df_skus_incompletos = df_skus_incompletos.drop_duplicates()

        
        df_skus_incompletos = df_skus_incompletos.reset_index(drop=True)


    # Eliminar columna auxiliar y duplicados
    df_materia_prima_filtrado = df_combinaciones_MP_PL_SKU_PROV.copy()
    df_combinaciones_MP_PL_SKU_PROV.drop(columns=['COSTO ABASTECIMIENTO (USD/TON)'], inplace=True)
    df_combinaciones_MP_PL_SKU_PROV.drop_duplicates(inplace=True)

    # Guardar resultados
    df_combinaciones_MP_PL_SKU_PROV.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_combinaciones_MP_PL_SKU_PROV.xlsx', index=False)
    df_materia_prima_filtrado.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_materia_prima_filtrado.xlsx', index=False)
    df_reporte_errores_abastecimiento.to_excel(f'Corridas/{nombre_corrida}/Errores/df_reporte_errores_abastecimiento.xlsx', index=False)
    df_skus_incompletos.to_excel(f'Corridas/{nombre_corrida}/Errores/df_skus_incompletos.xlsx', index=False)

    return df_combinaciones_MP_PL_SKU_PROV, df_reporte_errores_abastecimiento, df_skus_incompletos

def algoritmo_validacion_distribucion(nombre_corrida, df_homologaciones, df_costo_distribucion, df_tiempo_transito):
    """
    Algoritmo de validación de distribución, retornando posibles asignaciones de Planta - SKU - Clientes tal que dicho SKU puede entregarse al cliente (costo asociado)
    y tiene lead times de entrega (meses de tránsito asociados)
    """
    
    # Validar que el trío (COD_CLIENTE, COD_SKU_SIN_V, PLANTA) esté presente como fila completa en df_costo_distribucion
    df_con_costo_distribucion = df_homologaciones.merge(
        df_costo_distribucion[['ID_CLIENTE', 'SKU_SIN_VERSION', 'ID_PLANTA']].drop_duplicates(),
        left_on=['COD_CLIENTE', 'COD_SKU_SIN_V', 'PLANTA'],
        right_on=['ID_CLIENTE', 'SKU_SIN_VERSION', 'ID_PLANTA'],
        how='left',
        indicator='tiene_costo_distribucion'
    )

    # Validar que el par (COD_CLIENTE, PLANTA) esté presente como fila completa en df_tiempo_transito - directamente desde df_homologaciones
    df_con_tiempo_transito = df_homologaciones.merge(
        df_tiempo_transito[['ID_CLIENTE', 'ID_PLANTA']].drop_duplicates(),
        left_on=['COD_CLIENTE', 'PLANTA'],
        right_on=['ID_CLIENTE', 'ID_PLANTA'],
        how='left',
        indicator='tiene_tiempo_transito'
    )

    # Unir ambas validaciones
    df_completo = df_con_costo_distribucion.merge(
        df_con_tiempo_transito[['COD_SKU_SIN_V', 'COD_CLIENTE', 'PLANTA', 'tiene_tiempo_transito']],
        on=['COD_SKU_SIN_V', 'COD_CLIENTE', 'PLANTA'],
        how='left'
    )

    
    # Homologaciones válidas: tienen tanto costo de distribución como tiempo de tránsito
    df_homologaciones_validas_distribucion = df_completo[
        (df_completo['tiene_costo_distribucion'] == 'both') &
        (df_completo['tiene_tiempo_transito'] == 'both')
    ].copy()
    
    # Eliminar duplicados en todas las columnas
    df_homologaciones_validas_distribucion = df_homologaciones_validas_distribucion.drop_duplicates()
    
    # Limpiar columnas auxiliares
    columnas_a_eliminar = [col for col in df_homologaciones_validas_distribucion.columns 
                          if col.startswith('ID_') or col.startswith('tiene_')]
    df_homologaciones_validas_distribucion = df_homologaciones_validas_distribucion.drop(columns=columnas_a_eliminar)
    
    # Crear reporte de errores - TODOS LOS CASOS SIN DUPLICAR
    df_errores = df_completo[
        (df_completo['tiene_costo_distribucion'] != 'both') |
        (df_completo['tiene_tiempo_transito'] != 'both')
    ].copy()
    
    # Asignar motivo de error según el caso
    def asignar_motivo_error(row):
        sin_costo = row['tiene_costo_distribucion'] != 'both'
        sin_tiempo = row['tiene_tiempo_transito'] != 'both'
        
        if sin_costo and sin_tiempo:
            return 'No tiene canal de distribución en costo de distribución Y no tiene tiempo de tránsito'
        elif sin_costo:
            return 'No tiene canal de distribución en costo de distribución'
        elif sin_tiempo:
            return 'No tiene tiempo de tránsito'
        else:
            return 'Error desconocido'  # Este caso no debería ocurrir
    
    df_errores['MOTIVO_ERROR'] = df_errores.apply(asignar_motivo_error, axis=1)
    
    # Limpiar columnas auxiliares del reporte de errores
    columnas_a_eliminar_errores = [col for col in df_errores.columns if col.startswith('tiene_')]
    df_reporte_errores_distribucion = df_errores.drop(columns=columnas_a_eliminar_errores)
    
    df_reporte_errores_distribucion = df_reporte_errores_distribucion.drop(
    columns=["ID_CLIENTE", "SKU_SIN_VERSION", "ID_PLANTA"],
    errors="ignore"
)
    df_homologaciones_validas_distribucion.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_homologaciones_validas_distribucion.xlsx', index=False)
    
    df_reporte_errores_distribucion.to_excel(f'Corridas/{nombre_corrida}/Errores/df_reporte_errores_validacion_distribucion.xlsx', index=False)
    
    return df_homologaciones_validas_distribucion, df_reporte_errores_distribucion

def algoritmo_validacion_leadtimes_entrega(nombre_corrida, df_tiempo_transito, df_forecast, df_consignacion, df_inventario_inicial, df_homologaciones, df_ordenes_abiertas, df_stock_cliente_consignacion):
    """
    Algoritmo de validación de lead times de entrega considerando inventario inicial, demanda y órdenes abiertas por mes
    """
    
    # 1. Preparar datos base
    df_homologaciones_con_lt = df_homologaciones.merge(
        df_tiempo_transito[['ID_CLIENTE', 'ID_PLANTA', 'MESES_TRANSITO']].drop_duplicates(),
        left_on=['COD_CLIENTE', 'PLANTA'],
        right_on=['ID_CLIENTE', 'ID_PLANTA'],
        how='left'
    ).drop(columns=['ID_CLIENTE', 'ID_PLANTA'])
    
    # 2. Filtrar datos por SKUs en homologaciones válidas
    skus_validos = df_homologaciones['COD_SKU_SIN_V'].unique()
    df_forecast_filtrado = df_forecast[df_forecast['COD_SKU_SIN_V'].isin(skus_validos)]
    df_inventario_filtrado = df_inventario_inicial[df_inventario_inicial['COD_SKU_SIN_V'].isin(skus_validos)].copy()
    
    # CAMBIO: Obtener columnas numéricas directamente del forecast
    columnas_numericas = [col for col in df_forecast.columns if isinstance(col, (int, float))]
    print(f"Columnas numéricas encontradas en forecast: {sorted(columnas_numericas)}")
    
    # 3. Calcular stock_consignacion_target - SIMPLIFICADO
    df_demanda_real = (
        df_forecast_filtrado.melt(
            id_vars=['COD_SKU_SIN_V'], 
            value_vars=columnas_numericas,  # CAMBIO: usar columnas numéricas
            var_name='MES', 
            value_name='DEMANDA'
        )
        .query('DEMANDA > 0')
        # YA NO NECESITA mapeo: los números ya están listos
    )
    
    stock_consignacion_target = (
        df_homologaciones
        .merge(df_consignacion[['ID_CLIENTE', 'CONSIGNACION']], left_on='COD_CLIENTE', right_on='ID_CLIENTE')
        .merge(df_demanda_real.groupby('COD_SKU_SIN_V', as_index=False)['DEMANDA'].mean(), on='COD_SKU_SIN_V')
        .assign(STOCK=lambda d: d['DEMANDA'] * d['CONSIGNACION']/30)
        .groupby('COD_SKU_SIN_V')['STOCK'].mean()
        .to_dict()
    )
    
    # 4. Calcular stock_actual_cliente
    set_sku = set(skus_validos)
    stock_por_sku = df_stock_cliente_consignacion.groupby('COD_SKU_SIN_V')['MILES_SACOS'].sum()
    stock_actual_cliente = {sku: stock_por_sku.get(sku, 0) for sku in set_sku}
    
    # 5. Calcular SS_faltante
    SS_faltante = {
        sku: max(0, round(stock_consignacion_target.get(sku, 0) - stock_actual_cliente.get(sku, 0)))
        for sku in skus_validos
    }
    
    # 6. Preparar inventario inicial por planta y SKU
    inventario_inicial_sku_fabrica = {}
    for _, row in df_inventario_filtrado.iterrows():
        key = (row['PLANTA'], row['COD_SKU_SIN_V'])
        inventario_inicial_sku_fabrica[key] = row['INVENTARIO_DISPONIBLE']
    
    # Rellenar con 0 para combinaciones no existentes
    set_fabricas_sku = set(zip(df_homologaciones['PLANTA'], df_homologaciones['COD_SKU_SIN_V']))
    for (fabrica, sku) in set_fabricas_sku:
        key = (fabrica, sku)
        if key not in inventario_inicial_sku_fabrica:
            inventario_inicial_sku_fabrica[key] = 0
    
    # 7. Convertir forecast a formato largo - SIMPLIFICADO
    df_forecast_largo = df_forecast_filtrado.melt(
        id_vars=['COD_SKU_SIN_V', 'PLANTA'],
        value_vars=columnas_numericas,  # CAMBIO: usar columnas numéricas
        var_name='MES_NUM',
        value_name='MILES_SACOS_FORECAST'
    )

    # Agregar órdenes abiertas por mes - SIMPLIFICADO
    df_ordenes_largo = df_ordenes_abiertas[df_ordenes_abiertas['COD_SKU_SIN_V'].isin(skus_validos)].copy()
    df_ordenes_largo.rename(columns={'MES': 'MES_NUM'}, inplace=True)  # Solo renombrar columna
    # YA NO NECESITA mapeo: MES ya contiene números
    df_ordenes_largo = df_ordenes_largo.groupby(['COD_SKU_SIN_V', 'MES_NUM'], as_index=False)['MILES_SACOS'].sum()
    df_ordenes_largo.rename(columns={'MILES_SACOS': 'MILES_SACOS_ORDENES'}, inplace=True)
    
    # 8. Identificar homologaciones INVÁLIDAS - CAMBIO PRINCIPAL
    homologaciones_invalidas = []
    
    # CAMBIO: Iterar sobre las columnas numéricas del forecast
    for mes_num in sorted(columnas_numericas):
        print(f"Procesando mes número: {mes_num}")
        
        # CREAR UNIVERSO COMPLETO DE SKU-PLANTA para el mes
        df_universo_mes = pd.DataFrame(list(set_fabricas_sku), columns=['PLANTA', 'COD_SKU_SIN_V'])
        df_universo_mes['MES_NUM'] = mes_num
        
        # MERGEAR con forecast del mes (outer para mantener todo)
        df_forecast_mes = df_forecast_largo[df_forecast_largo['MES_NUM'] == mes_num]
        df_demanda_mes = df_universo_mes.merge(
            df_forecast_mes[['COD_SKU_SIN_V', 'PLANTA', 'MILES_SACOS_FORECAST']],
            on=['COD_SKU_SIN_V', 'PLANTA'],
            how='left'
        )
        df_demanda_mes['MILES_SACOS_FORECAST'] = df_demanda_mes['MILES_SACOS_FORECAST'].fillna(0)
        
        # MERGEAR con órdenes abiertas del mes (outer para mantener todo)
        df_ordenes_mes = df_ordenes_largo[df_ordenes_largo['MES_NUM'] == mes_num]
        df_demanda_mes = df_demanda_mes.merge(
            df_ordenes_mes[['COD_SKU_SIN_V', 'MILES_SACOS_ORDENES']],
            on=['COD_SKU_SIN_V'],
            how='left'
        )
        df_demanda_mes['MILES_SACOS_ORDENES'] = df_demanda_mes['MILES_SACOS_ORDENES'].fillna(0)
        
        # Calcular demanda total
        df_demanda_mes['DEMANDA_TOTAL'] = df_demanda_mes['MILES_SACOS_FORECAST'] + df_demanda_mes['MILES_SACOS_ORDENES']
        
        # Agregar SS_faltante SOLO al mes 1
        if mes_num == 1:
            df_demanda_mes['SS_FALTANTE'] = df_demanda_mes['COD_SKU_SIN_V'].map(lambda sku: SS_faltante.get(sku, 0))
            df_demanda_mes['DEMANDA_TOTAL'] += df_demanda_mes['SS_FALTANTE']
        
        # Filtrar solo demanda total > 0
        df_demanda_mes = df_demanda_mes[df_demanda_mes['DEMANDA_TOTAL'] > 0]
        
        if df_demanda_mes.empty:
            continue
        
        # Mergear con homologaciones y lead times
        df_mes_completo = df_demanda_mes.merge(
            df_homologaciones_con_lt,
            on=['COD_SKU_SIN_V', 'PLANTA'],
            how='inner'
        )
        
        if df_mes_completo.empty:
            continue

        for _, row in df_mes_completo.iterrows():
            lt = float(row['MESES_TRANSITO'])
            demanda_total = float(row['DEMANDA_TOTAL'])
            inventario = float(inventario_inicial_sku_fabrica.get((row['PLANTA'], row['COD_SKU_SIN_V']), 0))
            
            # Identificar casos INVÁLIDOS
            es_invalido = False
            motivo_error = ""
            
            if lt > mes_num:
                # Lead time muy grande: no se puede entregar a tiempo
                es_invalido = True
                motivo_error = f"Lead time ({lt} meses) muy grande para entregar en mes {mes_num}"
                
            elif lt == mes_num:
                # Lead time igual al mes: necesita inventario suficiente
                if inventario < demanda_total:
                    es_invalido = True
                    motivo_error = f"Inventario insuficiente (tiene {inventario}, necesita {demanda_total}) para entregar en mes {mes_num} con LT={lt}"
            
            # Si es inválido, agregar a la lista
            if es_invalido:
                homologaciones_invalidas.append({
                    'COD_SKU_SIN_V': row['COD_SKU_SIN_V'],
                    'PLANTA': row['PLANTA'],
                    'MES_PROBLEMA': mes_num,
                    'LEAD_TIME': lt,
                    'DEMANDA_TOTAL': demanda_total,
                    'INVENTARIO_DISPONIBLE': inventario,
                    'MOTIVO_ERROR': motivo_error
                })
    
    # 9. Crear DataFrame de homologaciones inválidas
    if homologaciones_invalidas:
        df_homologaciones_invalidas = pd.DataFrame(homologaciones_invalidas)
        df_homologaciones_invalidas.to_clipboard()
        
        # Consolidar por dupla (COD_SKU_SIN_V, PLANTA) para evitar duplicados
        df_homologaciones_invalidas_consolidado = df_homologaciones_invalidas.groupby(
            ['COD_SKU_SIN_V', 'PLANTA']
        ).agg({
            'MES_PROBLEMA': lambda x: ', '.join(map(str, sorted(set(x)))),
            'LEAD_TIME': 'first',
            'MOTIVO_ERROR': lambda x: ' | '.join(set(x))
        }).reset_index()
        
        # Obtener duplas inválidas únicas
        sku_planta_invalidos = set(zip(
            df_homologaciones_invalidas_consolidado['COD_SKU_SIN_V'],
            df_homologaciones_invalidas_consolidado['PLANTA']
        ))
    else:
        df_homologaciones_invalidas_consolidado = pd.DataFrame()
        sku_planta_invalidos = set()
    
    # 10. Filtrar homologaciones válidas (quitar las inválidas)
    if sku_planta_invalidos:
        # Crear máscara para homologaciones válidas
        mask_validas = ~df_homologaciones_con_lt.apply(
            lambda row: (row['COD_SKU_SIN_V'], row['PLANTA']) in sku_planta_invalidos,
            axis=1
        )
        df_homologaciones_finales = df_homologaciones_con_lt[mask_validas].copy()
        
        # Crear reporte de errores con datos completos de las homologaciones
        df_errores_leadtime = df_homologaciones_con_lt[~mask_validas].merge(
            df_homologaciones_invalidas_consolidado[['COD_SKU_SIN_V', 'PLANTA', 'MES_PROBLEMA', 'MOTIVO_ERROR']],
            on=['COD_SKU_SIN_V', 'PLANTA'],
            how='left'
        )
    else:
        # Todas las homologaciones son válidas
        df_homologaciones_finales = df_homologaciones_con_lt.copy()
        df_errores_leadtime = pd.DataFrame()
    
    # Limpiar columnas auxiliares del resultado final
    df_homologaciones_finales = df_homologaciones_finales.drop(columns=['MESES_TRANSITO'], errors='ignore')
    
    # 11. Crear DataFrame de inventario para reporte
    df_inventario_reporte = []
    for (planta, sku), inventario in inventario_inicial_sku_fabrica.items():
        df_inventario_reporte.append({
            'COD_SKU_SIN_V': sku,
            'PLANTA': planta,
            'INVENTARIO_INICIAL': inventario,
            'SS_TARGET': stock_consignacion_target.get(sku, 0),
            'SS_ACTUAL': stock_actual_cliente.get(sku, 0),
            'SS_FALTANTE': SS_faltante.get(sku, 0)
        })
    
    df_inventario_reporte = pd.DataFrame(df_inventario_reporte)
    
    # 12. Exportar archivos
    if not df_errores_leadtime.empty:
        df_errores_leadtime.to_excel(f'Corridas/{nombre_corrida}/Errores/errores_leadtime_entrega.xlsx', index=False)
    
    if not df_homologaciones_finales.empty:
        df_homologaciones_finales.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/homologaciones_validas_leadtime.xlsx', index=False)
    
    df_inventario_reporte.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/reporte_inventario_ss.xlsx', index=False)
    
    return df_homologaciones_finales

def algoritmo_validacion_asignaciones_posibles(nombre_corrida):
    
    df_homologaciones = pd.read_excel('ResultadosEstaticos/Resultados/df_homologaciones.xlsx')
    n_homologados = df_homologaciones['COD_SKU_SIN_V'].nunique()

    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx')
    df_materia_prima = pd.read_excel('ResultadosEstaticos/Resultados/df_materia_prima.xlsx')

    df_costo_distribucion = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costo_distribucion.xlsx')
    df_tiempo_transito = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_tiempo_transito.xlsx')

    df_forecast = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_forecast.xlsx')
    df_ordenes_abiertas = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_ordenes_abiertas.xlsx')
    df_stock_cliente_consignacion = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_stock_cliente_consignacion.xlsx')

    df_costos_indirectos = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_costos_indirectos.xlsx')
    df_turnos = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_turnos.xlsx')
    df_velocidades = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_velocidades.xlsx')

    df_consignacion = pd.read_excel(f'ResultadosEstaticos/Resultados/df_consignacion.xlsx')
    df_inventario_inicial = pd.read_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_inventario_inicial.xlsx')

    df_homologaciones = algoritmo_validacion_forecast_ordenes_abiertas(nombre_corrida, df_homologaciones, df_forecast, df_ordenes_abiertas)
    
    df_homologaciones = algoritmo_validacion_produccion(nombre_corrida, df_homologaciones, df_costos_indirectos, df_turnos, df_velocidades)

    df_combinaciones_MP_PL_SKU_PROV, df_reporte_errores_abastecimiento, df_skus_incompletos = algoritmo_validacion_abastecimiento(nombre_corrida, df_materia_prima, df_homologaciones, df_ficha_tecnica)

    df_homologaciones_validas_distribucion, df_reporte_errores_distribucion = algoritmo_validacion_distribucion(nombre_corrida, df_homologaciones, df_costo_distribucion, df_tiempo_transito)
    
    df_homologaciones_validas_distribucion = algoritmo_validacion_leadtimes_entrega(nombre_corrida, df_tiempo_transito, df_forecast, df_consignacion, df_inventario_inicial, df_homologaciones_validas_distribucion,df_ordenes_abiertas, df_stock_cliente_consignacion)

    # Mergear df_combinaciones_MP_PL_SKU_PROV y df_homologaciones_validas_distribucion para determinar los COD_SKU y PLANTA de homologaciones validas, tanto con abastecimiento como distribucion
    df_homologaciones_validas = df_combinaciones_MP_PL_SKU_PROV.merge(df_homologaciones_validas_distribucion, on=['COD_SKU', 'COD_SKU_SIN_V', 'PLANTA'], how='inner')
    
    # Obtener todas las combinaciones únicas de COD_SKU y PLANTA de homologaciones originales
    df_homologaciones_sku_planta = df_homologaciones[['COD_SKU_SIN_V', 'PLANTA']].drop_duplicates()
    
    # Obtener las que SÍ entraron en homologaciones válidas
    df_validas_sku_planta = df_homologaciones_validas[['COD_SKU_SIN_V', 'PLANTA']].drop_duplicates()

    # Identificar las que NO entraron
    df_no_validas = df_homologaciones_sku_planta.merge(
        df_validas_sku_planta,
        on=['COD_SKU_SIN_V', 'PLANTA'],
        how='left',
        indicator=True
    )
    df_no_validas = df_no_validas[df_no_validas['_merge'] == 'left_only'].drop('_merge', axis=1)
    
    # Verificar si tienen abastecimiento válido
    df_con_abastecimiento = df_combinaciones_MP_PL_SKU_PROV[['COD_SKU_SIN_V', 'PLANTA']].drop_duplicates()
    df_no_validas = df_no_validas.merge(
        df_con_abastecimiento,
        on=['COD_SKU_SIN_V', 'PLANTA'],
        how='left',
        indicator='tiene_abastecimiento'
    )
    
    # Verificar si tienen distribución válida
    df_con_distribucion = df_homologaciones_validas_distribucion[['COD_SKU_SIN_V', 'PLANTA']].drop_duplicates()
    df_no_validas = df_no_validas.merge(
        df_con_distribucion,
        on=['COD_SKU_SIN_V', 'PLANTA'],
        how='left',
        indicator='tiene_distribucion'
    )
    
    # Asignar motivo de error
    def asignar_motivo_error_logistico(row):
        sin_abastecimiento = row['tiene_abastecimiento'] == 'left_only'
        sin_distribucion = row['tiene_distribucion'] == 'left_only'
        
        if sin_abastecimiento and sin_distribucion:
            return 'No tiene abastecimiento válido Y no tiene distribución válida'
        elif sin_abastecimiento:
            return 'No tiene abastecimiento válido'
        elif sin_distribucion:
            return 'No tiene distribución válida'
        else:
            return 'Error desconocido en validación logística'
    
    df_no_validas['MOTIVO_ERROR'] = df_no_validas.apply(asignar_motivo_error_logistico, axis=1)
    
    # Limpiar columnas auxiliares
    df_errores_logisticos = df_no_validas.drop(columns=['tiene_abastecimiento', 'tiene_distribucion'])
    
    # Eliminar COD_MP de df_homologaciones_validas y dropear duplicados
    df_homologaciones_validas = df_homologaciones_validas.drop(columns=['COD_MP', 'PROVEEDOR']).drop_duplicates()

    n_homologados_valid = df_homologaciones_validas['COD_SKU_SIN_V'].nunique()

    metrica = {'sku_homologados': n_homologados, 'sku_homologados_validos': n_homologados_valid}

    # Exportar archivos excel
    df_homologaciones_validas.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/homologaciones_validas.xlsx', index=False)
    df_errores_logisticos.to_excel(f'Corridas/{nombre_corrida}/Errores/errores_logisticos.xlsx', index=False)

    return metrica
