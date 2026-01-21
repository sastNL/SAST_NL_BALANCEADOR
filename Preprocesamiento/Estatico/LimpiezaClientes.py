import pandas as pd
from unidecode import unidecode

def limpieza_clientes():
    ## Datos clientes
    # Leer datos
    df_clientes = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Clientes', usecols='C:E', skiprows=2)
    df_clientes.columns = ['ID_CLIENTE', 'DESCRIPCION_CLIENTE', 'PAIS_DESTINO']

    df_clientes['ID_CLIENTE'] = pd.to_numeric(df_clientes['ID_CLIENTE'], errors='coerce').astype('Int64')
    
    # Filtrar filas con ID_CLIENTE o PAIS_DESTINO nulos
    df_reporte_errores_clientes = df_clientes.copy()
    df_reporte_errores_clientes = df_reporte_errores_clientes[df_reporte_errores_clientes['ID_CLIENTE'].isna() | df_reporte_errores_clientes['PAIS_DESTINO'].isna()]
    df_reporte_errores_clientes['MOTIVO_ERROR'] = 'ID_CLIENTE o PAIS_DESTINO nulo'
    df_clientes = df_clientes[df_clientes['ID_CLIENTE'].notna() & df_clientes['PAIS_DESTINO'].notna()]
    
    # Limpiar PAIS_DESTINO: quitar acentos, pasar a mayúsculas, aplicar reemplazos
    df_clientes['PAIS_DESTINO'] = df_clientes['PAIS_DESTINO'].apply(lambda x: unidecode(str(x)).upper())

    reemplazos_paises = {
        'GRAN BRETAÑA': 'REINO UNIDO',
        'GRAN BRETANA': 'REINO UNIDO',
        'EE.UU': 'USA',
        'E.E.U.U.': 'USA',
        'E.E.U.U': 'USA',
        'EEUU': 'USA',
        'EE UU': 'USA',
        'ESTADOS UNIDOS': 'USA',
        'USA.': 'USA',
        'REP. DOMINICANA': 'REPUBLICA DOMINICANA',
        'REP.DOMINICANA': 'REPUBLICA DOMINICANA',
        'REPUBLICA DOM.': 'REPUBLICA DOMINICANA',
        'REP DOMINICANA': 'REPUBLICA DOMINICANA',
        'PARAGUAI': 'PARAGUAY',
        'URUGUAI': 'URUGUAY',
        'TRIN.Y TOBAGO': 'TRINIDAD & TOBAGO',
        'TRIN. Y TOBAGO': 'TRINIDAD & TOBAGO',
        'TRINIDAD Y TOBAGO': 'TRINIDAD & TOBAGO',
        'TRIN Y TOBAGO': 'TRINIDAD & TOBAGO',
        'TRINIDAD TOBAGO': 'TRINIDAD & TOBAGO'
    }
    for original, nuevo in reemplazos_paises.items():
        df_clientes['PAIS_DESTINO'] = df_clientes['PAIS_DESTINO'].str.replace(original, nuevo, regex=False)
        
    ## Codigos clientes
    df_codigos_clientes = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Codigos clientes', usecols='C:D', skiprows=2)
    df_codigos_clientes.columns = ['ID_CLIENTE_FORSAC', 'ID_CLIENTE_CMPC_USA']
    
    # CAMBIO: Reportar errores por NaN primero
    df_reporte_errores_codigos = df_codigos_clientes.copy()
    mask_nan = (
        df_reporte_errores_codigos['ID_CLIENTE_FORSAC'].isna() | 
        df_reporte_errores_codigos['ID_CLIENTE_CMPC_USA'].isna()
    )
    df_errores_nan = df_reporte_errores_codigos[mask_nan].copy()
    df_errores_nan['MOTIVO_ERROR'] = 'ID_CLIENTE_FORSAC o ID_CLIENTE_CMPC_USA nulo'
    
    # Filtrar solo registros válidos (sin NaN)
    df_codigos_clientes = df_codigos_clientes[
        df_codigos_clientes['ID_CLIENTE_FORSAC'].notna() & 
        df_codigos_clientes['ID_CLIENTE_CMPC_USA'].notna()
    ]
    
    # NUEVO: Convertir a numérico y detectar errores
    df_codigos_clientes_temp = df_codigos_clientes.copy()
    
    # Convertir a numérico con coerce
    df_codigos_clientes_temp['ID_CLIENTE_FORSAC_NUM'] = pd.to_numeric(
        df_codigos_clientes_temp['ID_CLIENTE_FORSAC'], errors='coerce'
    )
    df_codigos_clientes_temp['ID_CLIENTE_CMPC_USA_NUM'] = pd.to_numeric(
        df_codigos_clientes_temp['ID_CLIENTE_CMPC_USA'], errors='coerce'
    )
    
    # NUEVO: Identificar registros que no se pudieron convertir
    mask_no_numerico = (
        df_codigos_clientes_temp['ID_CLIENTE_FORSAC_NUM'].isna() | 
        df_codigos_clientes_temp['ID_CLIENTE_CMPC_USA_NUM'].isna()
    )
    
    df_errores_no_numerico = df_codigos_clientes_temp[mask_no_numerico].copy()
    df_errores_no_numerico['MOTIVO_ERROR'] = 'ID_CLIENTE_FORSAC o ID_CLIENTE_CMPC_USA no numérico'
    df_errores_no_numerico = df_errores_no_numerico[['ID_CLIENTE_FORSAC', 'ID_CLIENTE_CMPC_USA', 'MOTIVO_ERROR']]
    
    # NUEVO: Combinar todos los errores
    df_reporte_errores_codigos = pd.concat([
        df_errores_nan,
        df_errores_no_numerico
    ], ignore_index=True)
    
    # Filtrar solo registros que se convirtieron correctamente
    df_codigos_clientes = df_codigos_clientes_temp[~mask_no_numerico].copy()
    
    # Asignar las columnas convertidas correctamente
    df_codigos_clientes['ID_CLIENTE_FORSAC'] = df_codigos_clientes['ID_CLIENTE_FORSAC_NUM'].astype('Int64')
    df_codigos_clientes['ID_CLIENTE_CMPC_USA'] = df_codigos_clientes['ID_CLIENTE_CMPC_USA_NUM'].astype('Int64')
    
    # Limpiar columnas temporales
    df_codigos_clientes = df_codigos_clientes[['ID_CLIENTE_FORSAC', 'ID_CLIENTE_CMPC_USA']]

    # Exportar archivos
    df_clientes.to_excel('ResultadosEstaticos/Resultados/df_clientes.xlsx', index=False)
    df_codigos_clientes.to_excel('ResultadosEstaticos/Resultados/df_codigos_clientes.xlsx', index=False)
    
    # Exportar errores
    if not df_reporte_errores_clientes.empty:
        df_reporte_errores_clientes.to_excel('ResultadosEstaticos/Errores/reporte_errores_clientes.xlsx', index=False)
    
    if not df_reporte_errores_codigos.empty:
        df_reporte_errores_codigos.to_excel('ResultadosEstaticos/Errores/reporte_errores_codigos_clientes.xlsx', index=False)