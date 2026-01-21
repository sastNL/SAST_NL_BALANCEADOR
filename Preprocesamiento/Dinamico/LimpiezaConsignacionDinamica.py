# %%
import pandas as pd
import numpy as np

def limpieza_stock_cliente_consignacion(nombre_corrida):
    """Limpieza de la consignación.
    """
    df_stock_cliente_consignacion = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Planilla de datos - Dinamico.xlsx', sheet_name='Stock consignacion clientes', skiprows=2, usecols='C:F')
    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx', usecols=['COD_SKU_SIN_V', 'PAIS_DESTINO']).drop_duplicates()
    
    # Unir con df_ficha_tecnica para obtener PAIS_DESTINO
    df_stock_cliente_consignacion = df_stock_cliente_consignacion.merge(df_ficha_tecnica, on='COD_SKU_SIN_V', how='left')

    # Determinar columnas críticas dinámicamente
    columnas_criticas = ['ID_CLIENTE', 'COD_SKU_SIN_V', 'MILES_SACOS']
    if 'PAIS_DESTINO' in df_stock_cliente_consignacion.columns:
        columnas_criticas.append('PAIS_DESTINO')
    
    # Crear máscara de registros válidos (incluyendo PAIS_DESTINO si existe)
    mask_valido = (
        df_stock_cliente_consignacion['ID_CLIENTE'].notna() & 
        (df_stock_cliente_consignacion['ID_CLIENTE'] != '') &
        df_stock_cliente_consignacion['COD_SKU_SIN_V'].notna() & 
        (df_stock_cliente_consignacion['COD_SKU_SIN_V'] != '') &
        df_stock_cliente_consignacion['MILES_SACOS'].notna()
    )
    
    # NUEVO: Agregar validación de PAIS_DESTINO si la columna existe
    if 'PAIS_DESTINO' in df_stock_cliente_consignacion.columns:
        mask_valido = mask_valido & (
            df_stock_cliente_consignacion['PAIS_DESTINO'].notna() & 
            (df_stock_cliente_consignacion['PAIS_DESTINO'] != '') &
            (df_stock_cliente_consignacion['PAIS_DESTINO'] != 'NAN')
        )
    
    # Convertir MILES_SACOS a numérico para registros no vacíos
    df_temp = df_stock_cliente_consignacion[mask_valido].copy()
    df_temp['MILES_SACOS'] = pd.to_numeric(df_temp['MILES_SACOS'], errors='coerce')
    
    # Actualizar máscara con validaciones numéricas
    mask_numerico_positivo = (df_temp['MILES_SACOS'].notna()) & (df_temp['MILES_SACOS'] > 0)
    
    # DataFrame filtrado final
    df_stock_cliente_consignacion_filtrado = df_temp[mask_numerico_positivo].copy()
    
    # ====== ACTUALIZACIÓN: Crear reporte de errores mejorado ======
    df_errores = df_stock_cliente_consignacion.copy()

    # Actualizar condiciones de error para incluir PAIS_DESTINO
    condiciones = [
        ~mask_valido,  # Campos vacíos (ahora incluye PAIS_DESTINO)
        mask_valido & (~df_temp['MILES_SACOS'].notna()),  # No numérico
        mask_valido & (df_temp['MILES_SACOS'].notna()) & (df_temp['MILES_SACOS'] <= 0)  # No positivo
    ]
    
    # Actualizar motivos de error
    columnas_obligatorias_str = ', '.join(columnas_criticas)
    motivos = [
        f'Campos obligatorios vacíos ({columnas_obligatorias_str})',
        'MILES_SACOS no numérico',
        'MILES_SACOS no positivo'
    ]
    
    df_errores['MOTIVO_ERROR'] = np.select(condiciones, motivos, default='')
    df_errores = df_errores[df_errores['MOTIVO_ERROR'] != '']
    
    # ====== NUEVO: Eliminar duplicados considerando PAIS_DESTINO ======
    if 'PAIS_DESTINO' in df_stock_cliente_consignacion_filtrado.columns:
        # Eliminar duplicados por ID_CLIENTE, COD_SKU_SIN_V y PAIS_DESTINO
        df_stock_cliente_consignacion_filtrado = df_stock_cliente_consignacion_filtrado[
            ~df_stock_cliente_consignacion_filtrado.duplicated(
                subset=['ID_CLIENTE', 'COD_SKU_SIN_V', 'PAIS_DESTINO'], 
                keep='first'
            )
        ]
    else:
        # Eliminar duplicados por ID_CLIENTE y COD_SKU_SIN_V
        df_stock_cliente_consignacion_filtrado = df_stock_cliente_consignacion_filtrado[
            ~df_stock_cliente_consignacion_filtrado.duplicated(
                subset=['ID_CLIENTE', 'COD_SKU_SIN_V'], 
                keep='first'
            )
        ]
    
    # Exportar archivos
    if not df_errores.empty:
        df_errores.to_excel(f'Corridas/{nombre_corrida}/Errores/df_errores_stock_cliente_consignacion.xlsx', index=False)
    
    df_stock_cliente_consignacion_filtrado.to_excel(f'Corridas/{nombre_corrida}/Preprocesamiento/df_stock_cliente_consignacion.xlsx', index=False)
