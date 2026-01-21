import pandas as pd
from unidecode import unidecode
from datetime import datetime
    
def algoritmo_limpieza_forecast(nombre_corrida, df_forecast, df_ficha_tecnica, mes_inicio, año_inicio, mes_fin, año_fin):
    """
    Limpieza del Forecast original.
    """
    
    # Crear copia para evitar warnings por vista
    df_forecast = df_forecast.copy()
    
    # ====== 0. Calcular meses a considerar y su numeración ======
    meses_esp = {
        1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
        7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE',
        11: 'NOVIEMBRE', 12: 'DICIEMBRE'
    }
    
    # Crear diccionario inverso para convertir nombres a números
    nombres_a_numero = {v: k for k, v in meses_esp.items()}
    
    # Convertir nombres de meses a números si vienen como string
    if isinstance(mes_inicio, str):
        mes_inicio = nombres_a_numero[mes_inicio.upper()]
    if isinstance(mes_fin, str):
        mes_fin = nombres_a_numero[mes_fin.upper()]
    
    # Crear fechas de inicio y fin
    fecha_inicio = datetime(año_inicio, mes_inicio, 1)
    fecha_fin = datetime(año_fin, mes_fin, 1)
    
    # Generar secuencia de meses CON AÑO para evitar duplicados
    meses_considerados = []
    mapa_fechas_a_numero = {}  
    mapa_numero_a_fecha = {}   
    
    fecha_actual = fecha_inicio
    numero_mes = 1
    
    while fecha_actual <= fecha_fin:
        mes_nombre = meses_esp[fecha_actual.month]
        año_actual = fecha_actual.year
        
        # Agregar mes y año a la consideración
        meses_considerados.append((año_actual, mes_nombre))
        mapa_fechas_a_numero[(año_actual, fecha_actual.month)] = numero_mes
        mapa_numero_a_fecha[numero_mes] = (año_actual, fecha_actual.month)
        
        # Avanzar al siguiente mes
        if fecha_actual.month == 12:
            fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
        else:
            fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)
        
        numero_mes += 1
    
    print(f"Fechas consideradas: {meses_considerados}")
    print(f"Mapeo de fechas: {mapa_fechas_a_numero}")
    
    #Se renombran las columnas para unificar el formato
    df_forecast['COD_SKU_SIN_V'] = df_forecast['SKU SIN VERSION']
    df_forecast['DESCRIPCION_SKU'] = df_forecast['Producto']
    df_forecast['COD_CLIENTE'] = df_forecast['Cod. Cliente']
    df_forecast['CLIENTE'] = df_forecast['Cliente']
    df_forecast['PLANTA'] = df_forecast['Planta']

    # Determinar PAIS_DESTINO usando ficha tecnica
    df_forecast = df_forecast.merge(df_ficha_tecnica[['COD_SKU_SIN_V', 'PAIS_DESTINO']].drop_duplicates(), on='COD_SKU_SIN_V', how='left')
    
    # ====== Reporte Errores =========
    # NUEVO: Reporte de errores - campos obligatorios
    df_reporte_errores = df_forecast.copy()
    
    # IMPORTANTE: Primero identificar si el SKU existe en ficha técnica
    skus_en_ficha = set(df_ficha_tecnica['COD_SKU_SIN_V'].dropna().unique())
    df_reporte_errores['SKU_EXISTE_EN_FICHA'] = df_reporte_errores['COD_SKU_SIN_V'].isin(skus_en_ficha)
    
    # Identificar registros con campos críticos nulos
    campos_criticos = ['COD_SKU_SIN_V', 'COD_CLIENTE', 'PLANTA', 'PAIS_DESTINO']
    
    # Crear máscara para registros con errores
    mask_errores = (
        df_reporte_errores['COD_SKU_SIN_V'].isna() |
        (df_reporte_errores['COD_SKU_SIN_V'] == '') |
        df_reporte_errores['COD_CLIENTE'].isna() |
        (df_reporte_errores['COD_CLIENTE'] == '') |
        df_reporte_errores['PLANTA'].isna() |
        (df_reporte_errores['PLANTA'] == '') |
        df_reporte_errores['PAIS_DESTINO'].isna() |
        (df_reporte_errores['PAIS_DESTINO'] == '') |
        ~df_reporte_errores['SKU_EXISTE_EN_FICHA']  # NUEVO: También es error si no existe en ficha
    )
    
    # Filtrar registros con errores
    df_errores = df_reporte_errores[mask_errores].copy()
    
    if not df_errores.empty:
        # Agregar columna de motivo de error específico
        def identificar_error(row):
            errores = []
            
            # PRIMERO verificar si el SKU existe en ficha técnica
            if not row['SKU_EXISTE_EN_FICHA']:
                errores.append('SKU no tiene ficha técnica')
            else:
                # Solo validar otros campos si el SKU SÍ existe en ficha
                if pd.isna(row['COD_SKU_SIN_V']) or row['COD_SKU_SIN_V'] == '':
                    errores.append('COD_SKU_SIN_V vacío')
                if pd.isna(row['COD_CLIENTE']) or row['COD_CLIENTE'] == '':
                    errores.append('COD_CLIENTE vacío')
                if pd.isna(row['PLANTA']) or row['PLANTA'] == '':
                    errores.append('PLANTA vacía')
                if pd.isna(row['PAIS_DESTINO']) or row['PAIS_DESTINO'] == '':
                    errores.append('PAIS_DESTINO vacío (SKU existe en ficha pero sin país)')
            
            return '; '.join(errores)
        
        df_errores['MOTIVO_ERROR'] = df_errores.apply(identificar_error, axis=1)
        
        # Exportar errores
        df_errores.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_forecast.xlsx', index=False)
        print(f"Errores encontrados en forecast: {len(df_errores)} registros con problemas")
    
    # Filtrar solo registros válidos para continuar procesamiento
    df_forecast = df_forecast[~mask_errores].copy()
    
    # ====== 1. Eliminar filas innecesarias ====== 
    df_forecast = df_forecast[~df_forecast['COD_SKU_SIN_V'].str.startswith('FA')]
       
    # ====== 2. Renombrar columnas datetime a NÚMEROS (CONSIDERANDO AÑO) ======
    nuevos_nombres = {}

    # Detectar columnas datetime
    for col in df_forecast.columns:
        if isinstance(col, pd.Timestamp):
            año_col = col.year
            mes_col = col.month
            
            # Solo renombrar si está en el rango considerado
            if (año_col, mes_col) in mapa_fechas_a_numero:
                nuevo_numero = mapa_fechas_a_numero[(año_col, mes_col)]
                nuevos_nombres[col] = nuevo_numero

    # Detectar columnas que pandas pueda interpretar como fechas
    for col in df_forecast.columns:
        if not isinstance(col, pd.Timestamp):
            try:
                fecha = pd.to_datetime(col, format='%Y-%m-%d', errors='raise')
                año_col = fecha.year
                mes_col = fecha.month
                
                # Solo renombrar si está en el rango considerado
                if (año_col, mes_col) in mapa_fechas_a_numero:
                    nuevo_numero = mapa_fechas_a_numero[(año_col, mes_col)]
                    nuevos_nombres[col] = nuevo_numero
            except:
                continue

    print(f"Columnas a renombrar: {nuevos_nombres}")
    
    # Renombrar columnas
    df_forecast.rename(columns=nuevos_nombres, inplace=True)

    # ====== 3. Limpiar y convertir valores numéricos SOLO para meses considerados ======
    def limpiar_y_convertir(valor):
        if isinstance(valor, str):
            valor = valor.replace('.', '').replace(',', '.').replace(' ', '')
        try:
            return float(valor)
        except:
            return None

    # Aplicar limpieza SOLO a los números de meses considerados que existan en el DataFrame
    numeros_meses_presentes = [num for num in mapa_numero_a_fecha.keys() if num in df_forecast.columns]
    
    print(f"Números de meses presentes en DataFrame: {numeros_meses_presentes}")
    
    if numeros_meses_presentes:
        # Procesar columna por columna para evitar problemas con duplicados
        for num_mes in numeros_meses_presentes:
            df_forecast[num_mes] = df_forecast[num_mes].apply(limpiar_y_convertir)
            df_forecast[num_mes] = df_forecast[num_mes].fillna(0)
        
        # Eliminar columnas de meses considerados que están completamente en 0
        numeros_meses_presentes = [col for col in numeros_meses_presentes if df_forecast[col].sum() > 0]
        
        # ====== 4. Filtrar filas con al menos un valor > 0 en los meses considerados ======
        if numeros_meses_presentes:
            df_forecast = df_forecast[df_forecast[numeros_meses_presentes].gt(0).any(axis=1)]
    else:
        print("ADVERTENCIA: No se encontraron columnas de meses considerados en el DataFrame")
        numeros_meses_presentes = []

    #Agregar una columna que se llame COD_SKU_V y que se complete buscando COD_SKU si COD_SKU DE ficha tecnica comienza con COD_SKU en df_ficha_tecnica
    # Función para buscar match en ficha técnica (empieza o contiene)
    def buscar_cod_sku_v(cod_sku_forecast, codigos_ficha):
        # Buscamos códigos en ficha técnica que empiecen con el código de forecast
        matches = [cod for cod in codigos_ficha if cod.startswith(cod_sku_forecast) or cod_sku_forecast in cod]
        return matches[0] if matches else cod_sku_forecast  # Si no hay match, queda el mismo código

    # Crear lista de códigos únicos de ficha técnica para buscar (más eficiente)
    codigos_ficha_unicos = df_ficha_tecnica['COD_SKU'].dropna().unique()

    # Aplicar para cada fila de df_forecast
    df_forecast['COD_SKU'] = df_forecast['COD_SKU_SIN_V'].apply(lambda x: buscar_cod_sku_v(x, codigos_ficha_unicos))

    # ====== 5. Dejar sólo columnas necesarias ======
    columnas_finales = ['COD_SKU', 'COD_SKU_SIN_V', 'DESCRIPCION_SKU', 'COD_CLIENTE', 'CLIENTE',
                        'PLANTA', 'PAIS_DESTINO'] + numeros_meses_presentes
    df_forecast = df_forecast[columnas_finales]
    
    agg_dict = {col: 'sum' for col in numeros_meses_presentes}
    df_forecast = df_forecast.groupby(['COD_SKU', 'COD_SKU_SIN_V', 'DESCRIPCION_SKU', 'COD_CLIENTE', 'CLIENTE', 'PLANTA', 'PAIS_DESTINO']).agg(agg_dict).reset_index()

    # ====== 6. Guardar resultado ======
    df_forecast.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_forecast.xlsx', index=False)

    # Crear set_meses con números para compatibilidad y mapeo simple
    set_meses = set(numeros_meses_presentes)
    mapa_meses_simple = {meses_esp[mapa_numero_a_fecha[num][1]]: num for num in numeros_meses_presentes}
    
    return df_forecast, set_meses, mapa_meses_simple