import pandas as pd
from unidecode import unidecode
from datetime import datetime

def limpieza_ordenes_abiertas(nombre_corrida, mes_inicio, año_inicio, mes_fin, año_fin):
    
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
    mapa_fechas_a_numero = {}  # (año, mes) -> numero_secuencial
    mapa_numero_a_fecha = {}   # numero_secuencial -> (año, mes)
    
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
    
    print(f"Fechas consideradas para órdenes abiertas: {meses_considerados}")
    print(f"Mapeo de fechas: {mapa_fechas_a_numero}")

    # ====== 1. Leer datos ======
    df_ordenes_abiertas = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Ordenes abiertas', usecols='C:F', skiprows=2)
    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx', usecols=['COD_SKU_SIN_V', 'PAIS_DESTINO']).drop_duplicates()
    
    df_ordenes_abiertas = df_ordenes_abiertas.merge(df_ficha_tecnica, on='COD_SKU_SIN_V', how='left')
    
    # Crear DataFrame para consolidar errores
    df_errores_ordenes_abiertas = pd.DataFrame()
   
    # ====== 3. Validaciones de columnas críticas ======
    columnas_criticas = ['COD_SKU_SIN_V', 'MES', 'MILES_SACOS']
    if 'PAIS_DESTINO' in df_ordenes_abiertas.columns:
        columnas_criticas.append('PAIS_DESTINO')
    
    df_errores_nulos = df_ordenes_abiertas[df_ordenes_abiertas[columnas_criticas].isna().any(axis=1)].copy()
    if not df_errores_nulos.empty:
        df_errores_nulos['MOTIVO_ERROR'] = f'Valores nulos en columnas críticas ({", ".join(columnas_criticas)})'
        df_errores_ordenes_abiertas = pd.concat([df_errores_ordenes_abiertas, df_errores_nulos], ignore_index=True)
    
    # Filtrar filas con valores nulos en columnas críticas
    df_ordenes_abiertas = df_ordenes_abiertas.dropna(subset=columnas_criticas, how='any')
    
    # ====== 4. Procesar columna MES (datetime o formato fecha) ======
    df_ordenes_abiertas['MES_ORIGINAL'] = df_ordenes_abiertas['MES']  # Guardar original para errores
    
    # Procesar columna MES para convertir a número secuencial
    mes_validos = []
    
    for index, row in df_ordenes_abiertas.iterrows():
        mes_col = row['MES']
        mes_numero = None
        
        # Caso 1: Si es datetime/Timestamp
        if isinstance(mes_col, pd.Timestamp):
            año_col = mes_col.year
            mes_col_num = mes_col.month
            if (año_col, mes_col_num) in mapa_fechas_a_numero:
                mes_numero = mapa_fechas_a_numero[(año_col, mes_col_num)]
        
        # Caso 2: Si es string que se puede convertir a fecha
        elif isinstance(mes_col, str):
            try:
                fecha = pd.to_datetime(mes_col, format='%Y-%m-%d', errors='raise')
                año_col = fecha.year
                mes_col_num = fecha.month
                if (año_col, mes_col_num) in mapa_fechas_a_numero:
                    mes_numero = mapa_fechas_a_numero[(año_col, mes_col_num)]
            except:
                # Caso 3: Si es nombre de mes (ENERO, FEBRERO, etc.)
                mes_normalizado = unidecode(str(mes_col)).upper()
                if mes_normalizado in nombres_a_numero:
                    # Asumir año más reciente en el rango para nombres sin año
                    mes_num = nombres_a_numero[mes_normalizado]
                    # Buscar en el mapeo si existe este mes en algún año del rango
                    for (año, mes), numero in mapa_fechas_a_numero.items():
                        if mes == mes_num:
                            mes_numero = numero
                            break
        
        mes_validos.append(mes_numero)
    
    df_ordenes_abiertas['MES_NUM'] = mes_validos
    
    # Identificar errores de mes inválido (fuera del rango)
    df_errores_mes_invalido = df_ordenes_abiertas[df_ordenes_abiertas['MES_NUM'].isna()].copy()
    if not df_errores_mes_invalido.empty:
        df_errores_mes_invalido['MOTIVO_ERROR'] = 'MES no está en el rango de fechas considerado'
        df_errores_ordenes_abiertas = pd.concat([df_errores_ordenes_abiertas, df_errores_mes_invalido], ignore_index=True)
    
    # Filtrar solo meses válidos
    df_ordenes_abiertas = df_ordenes_abiertas[df_ordenes_abiertas['MES_NUM'].notna()]
    
    # Reemplazar columna MES por MES_NUM
    df_ordenes_abiertas['MES'] = df_ordenes_abiertas['MES_NUM']
    df_ordenes_abiertas = df_ordenes_abiertas.drop(columns=['MES_NUM'])
    
    # ====== 5. Validar MILES_SACOS ======
    # Guardar valores originales de MILES_SACOS antes de conversión
    df_ordenes_abiertas['MILES_SACOS_ORIGINAL'] = df_ordenes_abiertas['MILES_SACOS']

    df_ordenes_abiertas['PAIS_DESTINO'] = df_ordenes_abiertas['PAIS_DESTINO'].str.upper()

    # Convertir MILES_SACOS a numérico
    df_ordenes_abiertas['MILES_SACOS'] = pd.to_numeric(df_ordenes_abiertas['MILES_SACOS'], errors='coerce')
    
    # Identificar errores de conversión numérica
    df_errores_no_numerico = df_ordenes_abiertas[df_ordenes_abiertas['MILES_SACOS'].isna()].copy()
    if not df_errores_no_numerico.empty:
        df_errores_no_numerico['MOTIVO_ERROR'] = 'MILES_SACOS no es numérico: ' + df_errores_no_numerico['MILES_SACOS_ORIGINAL'].astype(str)
        df_errores_ordenes_abiertas = pd.concat([df_errores_ordenes_abiertas, df_errores_no_numerico], ignore_index=True)
    
    # Filtrar valores no numéricos
    df_ordenes_abiertas = df_ordenes_abiertas.dropna(subset=['MILES_SACOS'])
    
    # Chequear que MILES_SACOS sea mayor a 0
    df_errores_cantidad_invalida = df_ordenes_abiertas[df_ordenes_abiertas['MILES_SACOS'] <= 0].copy()
    if not df_errores_cantidad_invalida.empty:
        df_errores_cantidad_invalida['MOTIVO_ERROR'] = 'MILES_SACOS debe ser mayor a 0'
        df_errores_ordenes_abiertas = pd.concat([df_errores_ordenes_abiertas, df_errores_cantidad_invalida], ignore_index=True)
    
    # Filtrar solo cantidades positivas
    df_ordenes_abiertas = df_ordenes_abiertas[df_ordenes_abiertas['MILES_SACOS'] > 0]
    
    # ====== 6. Limpiar columnas auxiliares del dataset final ======
    df_ordenes_abiertas = df_ordenes_abiertas.drop(columns=['MILES_SACOS_ORIGINAL', 'MES_ORIGINAL'])
    
    # ====== 7. Eliminar duplicados ======
    df_ordenes_abiertas = df_ordenes_abiertas.drop_duplicates()
    
    # Eliminar duplicados por COD_SKU_SIN_V, MES y PAIS_DESTINO (si existe)
    if 'PAIS_DESTINO' in df_ordenes_abiertas.columns:
        df_ordenes_abiertas = df_ordenes_abiertas[~df_ordenes_abiertas.duplicated(subset=['COD_SKU_SIN_V', 'MES', 'PAIS_DESTINO'], keep='first')]
    else:
        df_ordenes_abiertas = df_ordenes_abiertas[~df_ordenes_abiertas.duplicated(subset=['COD_SKU_SIN_V', 'MES'], keep='first')]

    # ====== 8. Preparar archivo de errores ======
    if not df_errores_ordenes_abiertas.empty:
        # Limpiar columnas auxiliares del archivo de errores
        columnas_a_dropear = ['MES_NUM', 'MES_ORIGINAL']
        columnas_existentes = [col for col in columnas_a_dropear if col in df_errores_ordenes_abiertas.columns]
        if columnas_existentes:
            df_errores_ordenes_abiertas = df_errores_ordenes_abiertas.drop(columns=columnas_existentes)
        
        # Renombrar columnas para el reporte
        if 'MILES_SACOS_ORIGINAL' in df_errores_ordenes_abiertas.columns:
            df_errores_ordenes_abiertas.rename(columns={'MILES_SACOS_ORIGINAL': 'MILES_SACOS'}, inplace=True)
        #if 'MES_ORIGINAL' in df_errores_ordenes_abiertas.columns:
        #    df_errores_ordenes_abiertas.rename(columns={'MES_ORIGINAL': 'MES'}, inplace=True)
        
        # Ordenar columnas para el reporte
        columnas_reporte = ['COD_SKU_SIN_V', 'DESCRIPCION_SKU', 'MES', 'MILES_SACOS', 'MOTIVO_ERROR']
        if 'PAIS_DESTINO' in df_errores_ordenes_abiertas.columns:
            columnas_reporte.insert(-1, 'PAIS_DESTINO')  # Agregar antes de MOTIVO_ERROR
        
        columnas_existentes_reporte = [col for col in columnas_reporte if col in df_errores_ordenes_abiertas.columns]
        df_errores_ordenes_abiertas = df_errores_ordenes_abiertas[columnas_existentes_reporte]

    # ====== 9. Exportar archivos ======
    if not df_errores_ordenes_abiertas.empty:
        df_errores_ordenes_abiertas.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_ordenes_abiertas.xlsx', index=False)
    df_ordenes_abiertas.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_ordenes_abiertas.xlsx', index=False)
    
