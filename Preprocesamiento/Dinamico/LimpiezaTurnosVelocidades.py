import pandas as pd
from datetime import datetime

def limpieza_turnos_velocidades(nombre_corrida, mes_inicio, año_inicio, mes_fin, año_fin):
    
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
      
    ## ====== 1. Limpieza de turnos de lineas ======
    df_turnos = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Turnos', skiprows=2, usecols="C:AE")
    
    # Crear reporte de errores para turnos
    df_reporte_errores_turnos = pd.DataFrame()
    
    # Errores por valores nulos en columnas críticas de turnos
    columnas_criticas_turnos = ['PLANTA', 'NRO LINEA', 'LINEA']
    df_errores_nulos_turnos = df_turnos[df_turnos[columnas_criticas_turnos].isna().any(axis=1)].copy()
    if not df_errores_nulos_turnos.empty:
        df_errores_nulos_turnos['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas (PLANTA, NRO LINEA, LINEA)'
        df_reporte_errores_turnos = pd.concat([df_reporte_errores_turnos, df_errores_nulos_turnos], ignore_index=True)
    
    # Filtrar que PLANTA, NRO LINEA y LINEA no sean nulos
    df_turnos = df_turnos.dropna(subset=columnas_criticas_turnos, how='any')
    
    # ====== 2. PRIMERO: Identificar columnas que NO deben ser dropeadas ======
    columnas_renombradas = set()  # Para trackear qué columnas se renombraron exitosamente
    
    # ====== 3. Renombrar columnas datetime Y formato "HORAS/TURNO {MES}{AÑO}" a NÚMEROS ======
    nuevos_nombres_turnos = {}

    # Detectar columnas datetime
    for col in df_turnos.columns:
        if isinstance(col, pd.Timestamp):
            año_col = col.year
            mes_col = col.month
            
            # Solo renombrar si está en el rango considerado
            if (año_col, mes_col) in mapa_fechas_a_numero:
                nuevo_numero = mapa_fechas_a_numero[(año_col, mes_col)]
                nuevos_nombres_turnos[col] = nuevo_numero
                columnas_renombradas.add(col)

    # Detectar columnas que pandas pueda interpretar como fechas
    for col in df_turnos.columns:
        if not isinstance(col, pd.Timestamp):
            try:
                fecha = pd.to_datetime(col, format='%Y-%m-%d', errors='raise')
                año_col = fecha.year
                mes_col = fecha.month
                
                # Solo renombrar si está en el rango considerado
                if (año_col, mes_col) in mapa_fechas_a_numero:
                    nuevo_numero = mapa_fechas_a_numero[(año_col, mes_col)]
                    nuevos_nombres_turnos[col] = nuevo_numero
                    columnas_renombradas.add(col)
            except:
                continue
    
    # ====== NUEVO: Detectar columnas formato "HORAS/TURNO {MES}{AÑO}" ======
    for col in df_turnos.columns:
        if isinstance(col, str) and col.upper().startswith('HORAS/TURNO'):
            # Extraer la parte después de "HORAS/TURNO "
            parte_fecha = col.upper().replace('HORAS/TURNO', '').strip()
            
            # Intentar diferentes formatos
            año_detectado = None
            mes_detectado = None
            
            # Formato: ENERO25, FEBRERO26, etc.
            for mes_nombre, mes_num in nombres_a_numero.items():
                if parte_fecha.startswith(mes_nombre):
                    mes_detectado = mes_num
                    # Extraer año (últimos 2 dígitos)
                    año_str = parte_fecha.replace(mes_nombre, '').strip()
                    try:
                        if len(año_str) == 2:  # Formato 25, 26
                            año_detectado = 2000 + int(año_str)
                        elif len(año_str) == 4:  # Formato 2025, 2026
                            año_detectado = int(año_str)
                    except:
                        continue
                    break
            
            # Si se detectó mes y año, verificar si está en el rango
            if año_detectado and mes_detectado:
                if (año_detectado, mes_detectado) in mapa_fechas_a_numero:
                    nuevo_numero = mapa_fechas_a_numero[(año_detectado, mes_detectado)]
                    # CAMBIO: Renombrar a "HORAS/TURNO {número}" en lugar de solo número
                    nuevos_nombres_turnos[col] = f"HORAS/TURNO {nuevo_numero}"
                    columnas_renombradas.add(col)  # Marcar como renombrada exitosamente

    # Renombrar columnas
    df_turnos.rename(columns=nuevos_nombres_turnos, inplace=True)
    
    # ====== 4. DROPEAR SOLO columnas que NO se renombraron (fuera del rango) ======
    columnas_a_dropear = []
    
    # Detectar columnas datetime que no fueron renombradas
    for col in df_turnos.columns:
        if isinstance(col, pd.Timestamp):
            columnas_a_dropear.append(col)
    
    # Detectar columnas que parecen fechas pero no fueron renombradas
    for col in df_turnos.columns:
        if not isinstance(col, pd.Timestamp):
            try:
                pd.to_datetime(col, format='%Y-%m-%d', errors='raise')
                # Si llegamos aquí, es una fecha pero no fue renombrada
                columnas_a_dropear.append(col)
            except:
                # CAMBIO: Solo dropear columnas "HORAS/TURNO" que NO fueron renombradas
                if isinstance(col, str) and col.upper().startswith('HORAS/TURNO'):
                    # Verificar si esta columna específica fue renombrada exitosamente
                    # Buscar en las columnas originales si esta columna estaba en columnas_renombradas
                    # Como ya renombramos, buscar la original en el mapeo inverso
                    columna_original = None
                    for orig, nuevo in nuevos_nombres_turnos.items():
                        if nuevo == col:  # Si esta columna es resultado de un renombrado
                            columna_original = orig
                            break
                    
                    # Si no es resultado de un renombrado exitoso, dropearla
                    if columna_original is None:
                        columnas_a_dropear.append(col)
                continue
    
    if columnas_a_dropear:
        df_turnos = df_turnos.drop(columns=columnas_a_dropear)
    
    # ====== 5. Validar y limpiar columnas de meses considerados ======
    # CAMBIO: Buscar tanto números como "HORAS/TURNO {número}"
    numeros_meses_presentes_turnos = []
    
    for num in mapa_numero_a_fecha.keys():
        # Buscar columnas con número directo
        if num in df_turnos.columns:
            numeros_meses_presentes_turnos.append(num)
        # Buscar columnas con formato "HORAS/TURNO {número}"
        elif f"HORAS/TURNO {num}" in df_turnos.columns:
            numeros_meses_presentes_turnos.append(num)

    # Chequear que las columnas de meses no tengan valor nan ni negativo
    for num_mes in numeros_meses_presentes_turnos:
        # Determinar el nombre real de la columna
        if num_mes in df_turnos.columns:
            col_name = num_mes
        elif f"HORAS/TURNO {num_mes}" in df_turnos.columns:
            col_name = f"HORAS/TURNO {num_mes}"
        else:
            continue
            
        df_errores_mes = df_turnos[df_turnos[col_name].isna() | (df_turnos[col_name] < 0)].copy()
        if not df_errores_mes.empty:
            año_mes, mes_num = mapa_numero_a_fecha[num_mes]
            mes_nombre = meses_esp[mes_num]
            df_errores_mes['MOTIVO_ERROR'] = f'Valores nulos o negativos en columna {mes_nombre} {año_mes} (columna {col_name})'
            df_reporte_errores_turnos = pd.concat([df_reporte_errores_turnos, df_errores_mes], ignore_index=True)
        
        # Filtrar valores válidos
        df_turnos = df_turnos[df_turnos[col_name].notnull() & (df_turnos[col_name] >= 0)]
    
    ## ====== 6. Limpieza de velocidades (sin cambios significativos) ======
    df_velocidades = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Velocidades', skiprows=2, usecols="C:J")

    # Crear reporte de errores para velocidades
    df_reporte_errores_velocidades = pd.DataFrame()
    
    # Errores por valores nulos en columnas críticas de velocidades
    columnas_criticas_velocidades = ['PLANTA', 'NRO LINEA', 'LINEA', 'CATEGORIA']
    df_errores_nulos_velocidades = df_velocidades[df_velocidades[columnas_criticas_velocidades].isna().any(axis=1)].copy()
    if not df_errores_nulos_velocidades.empty:
        df_errores_nulos_velocidades['MOTIVO_ERROR'] = 'Valores nulos en columnas críticas (PLANTA, NRO LINEA, LINEA, CATEGORIA)'
        df_reporte_errores_velocidades = pd.concat([df_reporte_errores_velocidades, df_errores_nulos_velocidades], ignore_index=True)
    
    # Errores por velocidad nula o negativa
    df_errores_velocidad = df_velocidades[df_velocidades['VELOCIDAD (SC/MIN)'].isna() | (df_velocidades['VELOCIDAD (SC/MIN)'] < 0)].copy()
    if not df_errores_velocidad.empty:
        df_errores_velocidad['MOTIVO_ERROR'] = 'Velocidad nula o negativa'
        df_reporte_errores_velocidades = pd.concat([df_reporte_errores_velocidades, df_errores_velocidad], ignore_index=True)

    # Filtrar que PLANTA, NRO LINEA, LINEA y CATEGORIA no sean nulos
    df_velocidades = df_velocidades.dropna(subset=columnas_criticas_velocidades, how='any')
    
    # Filtrar que la columna 'VELOCIDAD (SC/MIN)' no sea nulo ni negativo
    df_velocidades = df_velocidades[df_velocidades['VELOCIDAD (SC/MIN)'].notnull() & (df_velocidades['VELOCIDAD (SC/MIN)'] >= 0)]

    df_velocidades['VELOCIDAD (SC/H)'] = df_velocidades['VELOCIDAD (SC/MIN)'] * 60

    ## ====== 7. Exportar a excel ======
    df_turnos.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_turnos.xlsx', index=False)
    df_velocidades.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_velocidades.xlsx', index=False)
    df_reporte_errores_turnos.to_excel(f'Corridas/{nombre_corrida}/Errores/df_reporte_errores_turnos.xlsx', index=False)
    df_reporte_errores_velocidades.to_excel(f'Corridas/{nombre_corrida}/Errores/df_reporte_errores_velocidades.xlsx', index=False)