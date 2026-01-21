import pandas as pd
import numpy as np

def algoritmo_gh_combinaciones_validas(df_lineas, df_ficha_tecnica):
    """
    EL Algoritmo Generador de Homologaciones crea el universo de posibles asignaciones de SKUs a lineas productivas
    """
    
    #Si en ficha tecnica TIPO_ENVASE es BAC, no considerar restricciones de fondera

    # Crear cross join entre ficha técnica y líneas
    df_ficha_tecnica['key'] = 1
    df_lineas['key'] = 1
    
    valvulas_validas = [
    '14-TUBULAR CON CHARNELA',
    '15-TUBULAR REDUCIDA CON CHARNELA',
    '16-TUBULAR SOBRE INSERTA',
    '17-TUBULAR DOBLE',
    '18-TUBULAR DOBLE (3 Capas)',
    '19-TUBULAR DOBLE (4 Capas)',
    '22-TUBULAR REDUCIDA SOBREINSERTA',
    'TUBULAR SOBRE INSERTA',
    'DOBLE (4 CAPAS)',
    'TUBULAR CON CHARNELA',
    'TUBULAR REDUCIDA CON CHARNELA',
    'TUBULAR DOBLE',
    'DOBLE (3 CAPAS)',
    'TUBULAR CON REDUCIDA CON CHARNELA',
    'TUBULAR DOBLE (4 CAPAS)',
    'TUBULAR DOBLE (3 CAPAS)',
    '17 -TUBULAR DOBLE'
]
    
    df_combinaciones = pd.merge(df_ficha_tecnica, df_lineas, on='key', suffixes=('', '_linea'))
    df_combinaciones = df_combinaciones.drop('key', axis=1)

    # Filtrar por restricciones de número de hojas
    df_combinaciones_validas = df_combinaciones[
        (df_combinaciones['TUBERA NRO HOJAS PAPEL MIN'].isna() | (df_combinaciones['HOJAS'] >= df_combinaciones['TUBERA NRO HOJAS PAPEL MIN'])) &
        (df_combinaciones['TUBERA NRO HOJAS PAPEL MAX'].isna() | (df_combinaciones['HOJAS'] <= df_combinaciones['TUBERA NRO HOJAS PAPEL MAX']))
    ]
    
    df_combinaciones_validas = df_combinaciones_validas[
        (df_combinaciones_validas['TUBERA ANCHO PAPEL MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL'] >= df_combinaciones_validas['TUBERA ANCHO PAPEL MIN (MM)'])) &
        (df_combinaciones_validas['TUBERA ANCHO PAPEL MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL'] <= df_combinaciones_validas['TUBERA ANCHO PAPEL MAX (MM)']))
    ]
    
    df_combinaciones_validas = df_combinaciones_validas[
    (
        (df_combinaciones_validas['TIPO_CORTE'] == 'RECTO') &
        (df_combinaciones_validas['TUBERA LARGO TUBO RECTO MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_TUBO'] >= df_combinaciones_validas['TUBERA LARGO TUBO RECTO MIN (MM)'])) &
        (df_combinaciones_validas['TUBERA LARGO TUBO RECTO MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_TUBO'] <= df_combinaciones_validas['TUBERA LARGO TUBO RECTO MAX (MM)']))
    ) |
    (
        (df_combinaciones_validas['TIPO_CORTE'] == 'ESCALONADO') &
        (df_combinaciones_validas['TUBERA LARGO TUBO ESCALONADO MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_TUBO'] >= df_combinaciones_validas['TUBERA LARGO TUBO ESCALONADO MIN (MM)'])) &
        (df_combinaciones_validas['TUBERA LARGO TUBO ESCALONADO MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_TUBO'] <= df_combinaciones_validas['TUBERA LARGO TUBO ESCALONADO MAX (MM)']))
    )
    ]

    #Si TIPO_ENVASE contiene "c/ FLL", LA LINEA DEBE SER TUBERA FUELLE = SI o sino nan

    df_combinaciones_validas['TUBERA FUELLE'] = df_combinaciones_validas['TIPO_ENVASE'].apply(lambda x: 'SI' if isinstance(x, str) and 'c/ FLL' in x else np.nan)


    # Filtrar ANCHO_SACO si es RECTO
    #ANCHO SACO = ANCHO TUBO
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['TIPO_CORTE'] == 'RECTO') &
        (df_combinaciones_validas['TUBERA ANCHO TUBO RECTO MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] >= df_combinaciones_validas['TUBERA ANCHO TUBO RECTO MIN (MM)'])) &
        (df_combinaciones_validas['TUBERA ANCHO TUBO RECTO MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] <= df_combinaciones_validas['TUBERA ANCHO TUBO RECTO MAX (MM)']))) |
        (df_combinaciones_validas['TIPO_CORTE'] != 'RECTO')
    ]
    
    df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'] = pd.to_numeric(
    df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'], errors='coerce'
)
    df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)'] = pd.to_numeric(
    df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)'], errors='coerce'
)
    # Filtrar ANCHO_SACO si es RECTO con FUELLE
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['TIPO_CORTE'] == 'RECTO') &
        (df_combinaciones_validas['TUBERA FUELLE'] == 'SI') & (df_combinaciones_validas['TIPO_ENVASE'].str.contains('c/ FLL', case=False, na=False)) &
        (df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] >= df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'])) &
        (df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] <= df_combinaciones_validas['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)']))) |
        (df_combinaciones_validas['TIPO_CORTE'] != 'RECTO') |
        ((df_combinaciones_validas['TIPO_CORTE'] == 'RECTO') &
        (df_combinaciones_validas['TUBERA FUELLE'].isna()))
    ]
        
    
    # Filtrar por colores según impresión en línea y antideslizante
    # Determinar si SKU tiene film (cualquier descripción de hoja contiene "film")
    df_combinaciones_validas['tiene_film'] = (
        df_combinaciones_validas['DESCRIPCION_HOJA_1'].str.contains('film', case=False, na=False) |
        df_combinaciones_validas['DESCRIPCION_HOJA_2'].str.contains('film', case=False, na=False) |
        df_combinaciones_validas['DESCRIPCION_HOJA_3'].str.contains('film', case=False, na=False) |
        df_combinaciones_validas['DESCRIPCION_HOJA_4'].str.contains('film', case=False, na=False)
    )
    
    # Filtrar por colores considerando impresión en línea, film y estación antideslizante
    df_combinaciones_validas = df_combinaciones_validas[
        (
            # Si se imprime en línea (PREIMPRESION es NaN)
            (df_combinaciones_validas['PREIMPRESION'].isna()) &
            (
                # Si tiene film y NO hay estación antideslizante independiente: +1 color
                (
                    (df_combinaciones_validas['tiene_film']) &
                    (df_combinaciones_validas['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'] == 'NO') &
                    (df_combinaciones_validas['TUBERA NRO TINTEROS'] >= df_combinaciones_validas['CANTIDAD_COLORES'] + 1)
                ) |
                # Si NO tiene film O SÍ hay estación antideslizante: mismo número de colores
                (
                    (~df_combinaciones_validas['tiene_film'] | 
                     (df_combinaciones_validas['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'] == 'SI')) &
                    (df_combinaciones_validas['TUBERA NRO TINTEROS'] >= df_combinaciones_validas['CANTIDAD_COLORES'])
                )
            )
        ) |
        # Si NO se imprime en línea: mismo número de colores
        (~df_combinaciones_validas['PREIMPRESION'].isna()) |
        (df_combinaciones_validas['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'].isna() | (df_combinaciones_validas['TUBERA NRO TINTEROS'].isna()))
    ]
    
    # Filtrar que si el SKU es preimpreso, la tubera debe tener lector de tacas
    df_combinaciones_validas = df_combinaciones_validas[
        ((~df_combinaciones_validas['PREIMPRESION'].isna()) &
        (df_combinaciones_validas['TUBERA LECTOR DE TACAS'] == 'SI')) |
        (df_combinaciones_validas['PREIMPRESION'].isna()) |
        (df_combinaciones_validas['TUBERA LECTOR DE TACAS'].isna())
    ]
    
    # Filtrar que si tiene film, necesita desbobinador 4Q
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['tiene_film']) &
        (df_combinaciones_validas['TUBERA DESBOBINADOR 4Q'] == 'SI')) |
        (~df_combinaciones_validas['tiene_film']) |
        (df_combinaciones_validas['TUBERA DESBOBINADOR 4Q'].isna())
    ]
    
    # Filtrar que si el TIPO_ENVASE es BAP con MANGA>0 o PY, la tubera debe tener Rotaliner
    df_combinaciones_validas = df_combinaciones_validas[
        (((df_combinaciones_validas['TIPO_ENVASE'] == 'BAP') & (df_combinaciones_validas['MANGA'] > 0)) &
        (df_combinaciones_validas['TUBERA ROTALINER'] == 'SI')) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'PY') &
        (df_combinaciones_validas['TUBERA ROTALINER'] == 'SI')) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAP') & (df_combinaciones_validas['MANGA'].isna() | (df_combinaciones_validas['MANGA'] == 0))) |
        ((df_combinaciones_validas['TIPO_ENVASE'] != 'BAP') & (df_combinaciones_validas['TIPO_ENVASE'] != 'PY')) |
        (df_combinaciones_validas['TUBERA ROTALINER'].isna())
    ]
#     ### Fondera ###
    
    df_combinaciones_validas = df_combinaciones_validas[
        # (((~df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) | (~df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna())) &
        ((~df_combinaciones_validas['REFUERZO_PREIMPRESO'].isna()) &
        (df_combinaciones_validas['FONDERA REFUERZOS PREIMPRESOS'] == 'SI')) |
        (df_combinaciones_validas['FONDERA REFUERZOS PREIMPRESOS'].isna()) |
        # ((df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) & (df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna())) |
        (df_combinaciones_validas['REFUERZO_PREIMPRESO'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    # Filtrar que si el tipo de corte es Recto, el largo de saco debe estar entre los limites largo de saco de la fondera, si es escalonado con su correspondiente
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['TIPO_CORTE'] == 'RECTO') &
        (df_combinaciones_validas['FONDERA LARGO SACO RECTO MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] >= df_combinaciones_validas['FONDERA LARGO SACO RECTO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO SACO RECTO MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] <= df_combinaciones_validas['FONDERA LARGO SACO RECTO MAX (MM)']))) |
        ((df_combinaciones_validas['TIPO_CORTE'] == 'ESCALONADO') &
        (df_combinaciones_validas['FONDERA LARGO SACO ESCALONADO MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] >= df_combinaciones_validas['FONDERA LARGO SACO ESCALONADO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO SACO ESCALONADO MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] <= df_combinaciones_validas['FONDERA LARGO SACO ESCALONADO MAX (MM)']))) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    #Filtrar que ANCHO_SACO debe estar entre los limites de FONDERA ANCHO SACO MIN (MM) y FONDERA ANCHO SACO MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA ANCHO SACO MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] >= df_combinaciones_validas['FONDERA ANCHO SACO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO SACO MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_SACO'] <= df_combinaciones_validas['FONDERA ANCHO SACO MAX (MM)']))) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]

    # Filtrar que ANCHO_CARA_5 si no es nan debe estar entre los limites de la fondera ancho fondo
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['ANCHO_CARA_5'].isna()) & (df_combinaciones_validas['ANCHO_CARA_6'].isna())) |
        ((~df_combinaciones_validas['ANCHO_CARA_5'].isna()) &
        (df_combinaciones_validas['FONDERA ANCHO FONDO MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_CARA_5'] >= df_combinaciones_validas['FONDERA ANCHO FONDO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO FONDO MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_CARA_5'] <= df_combinaciones_validas['FONDERA ANCHO FONDO MAX (MM)']))) |
        ((~df_combinaciones_validas['ANCHO_CARA_6'].isna()) &
        (df_combinaciones_validas['FONDERA ANCHO FONDO MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_CARA_6'] >= df_combinaciones_validas['FONDERA ANCHO FONDO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO FONDO MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_CARA_6'] <= df_combinaciones_validas['FONDERA ANCHO FONDO MAX (MM)'])))  |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]

    # Filtrar que si ancho cara 5 y ancho cara 6 no son nan, LARGO_SACO - 0.5*ANCHO_CARA_5 - 0.5*ANCHO_CARA_6 debe estar entre los limites de FONDERA DISTANCIA ENTRE CENTROS MIN y MAX
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['ANCHO_CARA_5'].isna()) & (df_combinaciones_validas['ANCHO_CARA_6'].isna())) |
        ((df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna()) & (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna())) |
        ((~df_combinaciones_validas['ANCHO_CARA_5'].isna()) & (~df_combinaciones_validas['ANCHO_CARA_6'].isna()) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 0.5*df_combinaciones_validas['ANCHO_CARA_5'] - 0.5*df_combinaciones_validas['ANCHO_CARA_6'] >= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 0.5*df_combinaciones_validas['ANCHO_CARA_5'] - 0.5*df_combinaciones_validas['ANCHO_CARA_6'] <= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((~df_combinaciones_validas['ANCHO_CARA_5'].isna()) & (df_combinaciones_validas['ANCHO_CARA_6'].isna()) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 1*df_combinaciones_validas['ANCHO_CARA_5'] >= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 1*df_combinaciones_validas['ANCHO_CARA_5'] <= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((df_combinaciones_validas['ANCHO_CARA_5'].isna()) & (~df_combinaciones_validas['ANCHO_CARA_6'].isna()) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 1*df_combinaciones_validas['ANCHO_CARA_6'] >= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_SACO'] - 1*df_combinaciones_validas['ANCHO_CARA_6'] <= df_combinaciones_validas['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
    ]
    
    # Filtrar que de ciertos TIPO_VALVULA deben pasar por fonderas con FONDERA NRO PAPELES POR EQ VAL mayor o igual a 2
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['TIPO_VALVULA'].str.upper().isin(['TUBULAR CON CHARNELA', 'TUBULAR REDUCIDA CON CHARNELA', 'TUBULAR SOBRE INSERTA', 'TUBULAR DOBLE', 'TUBULAR DOBLE (3 Capas)', 'TUBULAR DOBLE (4 Capas)', 'TUBULAR REDUCIDA', 'SOBREINSERTA'])) &
        (df_combinaciones_validas['FONDERA NRO PAPELES POR EQ VAL'] >= 2)) |
        (~df_combinaciones_validas['TIPO_VALVULA'].str.upper().isin(['TUBULAR CON CHARNELA', 'TUBULAR REDUCIDA CON CHARNELA', 'TUBULAR SOBRE INSERTA', 'TUBULAR DOBLE', 'TUBULAR DOBLE (3 Capas)', 'TUBULAR DOBLE (4 Capas)', 'TUBULAR REDUCIDA', 'SOBREINSERTA'])) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['FONDERA NRO PAPELES POR EQ VAL'].isna()) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
    ]   
    
    # Filtrar que LARGO_VALVULA este entre los limites de FONDERA LARGO PAPEL VAL MIN (MM) y FONDERA LARGO PAPEL VAL MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((~df_combinaciones_validas['TIPO_VALVULA'].isna()) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL VAL MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_VALVULA'] >= df_combinaciones_validas['FONDERA LARGO PAPEL VAL MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL VAL MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_VALVULA'] <= df_combinaciones_validas['FONDERA LARGO PAPEL VAL MAX (MM)']))) | 
        (df_combinaciones_validas['TIPO_VALVULA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
    ]
    
    # Si TIPO_VALVULA tiene adentro del str INSERTA CON MANGA (no importa mayus o minusc), LARGO_VALVULA debe ser mayor o igual a FONDERA LARGO VAL CON MANGA (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['TIPO_VALVULA'].str.contains('INSERTA CON MANGA', case=False, na=False)) &
        (df_combinaciones_validas['FONDERA LARGO VAL CON MANGA MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_VALVULA'] >= df_combinaciones_validas['FONDERA LARGO VAL CON MANGA MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO VAL CON MANGA MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_VALVULA'] <= df_combinaciones_validas['FONDERA LARGO VAL CON MANGA MAX (MM)']))) |
        (~df_combinaciones_validas['TIPO_VALVULA'].str.contains('INSERTA CON MANGA', case=False, na=False)) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
    ]
    
    # Filtrar que si LARGO_TOMA no es nan, entonces debe ser menor o igual a FONDERA LARGO TOMA MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
    (
        (~df_combinaciones_validas['LARGO_TOMA'].isna()) &
        (df_combinaciones_validas['FONDERA LARGO TOMA MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_TOMA'] <= df_combinaciones_validas['FONDERA LARGO TOMA MAX (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO TOMA MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_TOMA'] >= df_combinaciones_validas['FONDERA LARGO TOMA MIN (MM)']))
    ) |
    (df_combinaciones_validas['LARGO_TOMA'].isna()) |
    (
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')
    ) |
    (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
]

    # Filtrar si ANCHO_PAPEL_VALVULA no es nan, entonces debe estar entre los limites de FONDERA ANCHO ROLLO MIN (MM) y FONDERA ANCHO ROLLO MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((~df_combinaciones_validas['ANCHO_PAPEL_VALVULA'].isna()) &
        (df_combinaciones_validas['FONDERA ANCHO ROLLO MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_VALVULA'] >= df_combinaciones_validas['FONDERA ANCHO ROLLO MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO ROLLO MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_VALVULA'] <= df_combinaciones_validas['FONDERA ANCHO ROLLO MAX (MM)']))) |
        (df_combinaciones_validas['ANCHO_PAPEL_VALVULA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    # Filtrar si ANCHO_VALVULA no es nan, entonces debe estar entre los limites de FONDERA ANCHO VALVULA MIN (MM) y FONDERA ANCHO VALVULA MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((~df_combinaciones_validas['ANCHO_VALVULA'].isna()) & (df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas)) &
        (df_combinaciones_validas['FONDERA ANCHO VALVULA MIN (MM)'].isna() | (df_combinaciones_validas['ANCHO_VALVULA'] >= df_combinaciones_validas['FONDERA ANCHO VALVULA MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO VALVULA MAX (MM)'].isna() | (df_combinaciones_validas['ANCHO_VALVULA'] <= df_combinaciones_validas['FONDERA ANCHO VALVULA MAX (MM)']))) |
        (df_combinaciones_validas['ANCHO_VALVULA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP') |
        (~df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas))
    ]
    
    # Filtrar si LARGO_VALVULA no es nan, entonces debe estar entre los limites de FONDERA LARGO VALVULA MIN (MM) y FONDERA LARGO VALVULA MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((~df_combinaciones_validas['LARGO_VALVULA'].isna()) & (df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas)) &
        (df_combinaciones_validas['FONDERA LARGO VALVULA MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_VALVULA'] >= df_combinaciones_validas['FONDERA LARGO VALVULA MIN (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO VALVULA MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_VALVULA'] <= df_combinaciones_validas['FONDERA LARGO VALVULA MAX (MM)']))) |
        (df_combinaciones_validas['LARGO_VALVULA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP') |
        (~df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas))
    ]
    
    # Filtrar que si UNERO_VALVULA es SI (no importa mayuscula o minuscula), FONDERA DISPOSITIVO UÑERO debe ser SI (no importa mayuscula o minuscula)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA DISPOSITIVO UÑERO'].isna()) | ((df_combinaciones_validas['UNERO_VALVULA'].fillna('').str.lower() == 'si') & (df_combinaciones_validas['FONDERA DISPOSITIVO UÑERO'].fillna('').str.lower() == 'si'))) |
        (df_combinaciones_validas['UNERO_VALVULA'].fillna('').str.lower() != 'si') |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones_validas['TIPO_ENVASE'] == 'BAP')
    ]
    
    #Filtrar que LARGO_PAPEL esté entre los limites de FONDERA LONGITUD PAPEL MIN (MM) y FONDERA LONGITUD PAPEL MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA LONGITUD PAPEL MIN (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_VALVULA'] >= df_combinaciones_validas['FONDERA LONGITUD PAPEL MIN (MM)'])) & (df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas)) &
        (df_combinaciones_validas['FONDERA LONGITUD PAPEL MAX (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_VALVULA'] <= df_combinaciones_validas['FONDERA LONGITUD PAPEL MAX (MM)']))) |
        (df_combinaciones_validas['LARGO_PAPEL_VALVULA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (~df_combinaciones_validas['TIPO_VALVULA'].isin(valvulas_validas))
    ]
    
    #Filtrar si el saco tiene refuerzo de fondo no es nan, entonces FONDERA REFUERZO DE FONDO LADO ACCIONAMIENTO debe ser SI
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA REFUERZO DE FONDO LADO ACCIONAMIENTO'].isna()) | ((~df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) & (df_combinaciones_validas['FONDERA REFUERZO DE FONDO LADO ACCIONAMIENTO'] == 'SI'))) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    #Filtrar si el saco tiene refuerzo de fondo no es nan, entonces FONDERA REFUERZO DE FONDO LADO SERVICIO debe ser SI
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA REFUERZO DE FONDO LADO SERVICIO'].isna()) | ((~df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) & (df_combinaciones_validas['FONDERA REFUERZO DE FONDO LADO SERVICIO'] == 'SI'))) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    #Si TIPO_REFUERZO no es nan y LARGO_CARA5 es mayor a 0, entonces LARGO_CARA5 debe estar en los límites de FONDERA LARGO PAPEL REFUERZO FONDO MIN (MM) y FONDERA LARGO PAPEL REFUERZO FONDO MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        # Bloque 1: Validación técnica (Solo si hay un refuerzo real con medida positiva)
        ((~df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) & 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] != 0) & 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] != 'SIN Refuerzo') &
        (df_combinaciones_validas['LARGO_PAPEL_CARA5'] > 0) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'].isna() | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA5'] >= df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 5 (MM)'].isna() | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA5'] <= df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 5 (MM)']))) |
        
        # Bloque 2: Excepciones donde la restricción SE CONSIDERA CUMPLIDA
        (df_combinaciones_validas['LARGO_PAPEL_CARA5'].isna()) | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA5'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) | 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] == 'SIN Refuerzo') |
        (df_combinaciones_validas['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    ]

    #Si TIPO_REFUERZO no es nan y LARGO_CARA6 es mayor a 0, entonces LARGO_CARA6 debe estar en los límites de FONDERA LARGO PAPEL REFUERZO FONDO MIN (MM) y FONDERA LARGO PAPEL REFUERZO FONDO MAX (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        # Bloque 1: Validación técnica (Solo si hay un refuerzo real con medida positiva)
        ((~df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) & 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] != 0) & 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] != 'SIN Refuerzo') &
        (df_combinaciones_validas['LARGO_PAPEL_CARA6'] > 0) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'].isna() | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA6'] >= df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 6 (MM)'].isna() | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA6'] <= df_combinaciones_validas['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 6 (MM)']))) |
        
        # Bloque 2: Excepciones donde la restricción SE CONSIDERA CUMPLIDA
        (df_combinaciones_validas['LARGO_PAPEL_CARA6'].isna()) | 
        (df_combinaciones_validas['LARGO_PAPEL_CARA6'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) | 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] == 'SIN Refuerzo') |
        (df_combinaciones_validas['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    ]

    #Si TIPO_REFUERZO no es nan y ANCHO_CARA5 es mayor a 0, entonces ANCHO_CARA5 debe estar en los límites de FONDERA LARGO ANCHO PAPEL REFUERZO FONDO MIN CARA 5 (MM) y FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 5 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        # Bloque 1: Validación técnica (Solo si hay refuerzo real y ancho positivo)
        ((~df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) & 
         (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] != 0) & 
         (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] != 'SIN Refuerzo') & 
         (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] > 0) &
         (df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'].isna() | 
          (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] >= df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'])) &
         (df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 5 (MM)'].isna() | 
          (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] <= df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 5 (MM)']))) |
        
        # Bloque 2: Excepciones donde se considera cumplida la restricción
        (df_combinaciones_validas['ANCHO_PAPEL_CARA5'].isna()) | 
        (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'].isna()) | 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA5'] == 'SIN Refuerzo') |
        (df_combinaciones_validas['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    ]

    # #Si TIPO_REFUERZO no es nan y ANCHO_CARA6 es mayor a 0, entonces ANCHO_CARA6 debe estar en los límites de FONDERA LARGO ANCHO PAPEL REFUERZO FONDO MIN CARA 6 (MM) y FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 6 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        # Bloque 1: Validación técnica (Solo si hay refuerzo real y ancho positivo)
        ((~df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) & 
         (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] != 0) & 
         (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] != 'SIN Refuerzo') & 
         (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] > 0) &
         (df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'].isna() | 
          (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] >= df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'])) &
         (df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 6 (MM)'].isna() | 
          (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] <= df_combinaciones_validas['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 6 (MM)']))) |
        
        # Bloque 2: Excepciones donde se considera cumplida la restricción
        (df_combinaciones_validas['ANCHO_PAPEL_CARA6'].isna()) | 
        (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'].isna()) | 
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] == 0) |
        (df_combinaciones_validas['TIPO_REFUERZO_CARA6'] == 'SIN Refuerzo') |
        (df_combinaciones_validas['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    ]

    #Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA5 es distitno de nan, entonces FONDERA IMPRESION ACCIONAMIENTO debe ser SI
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA IMPRESIÓN LADO ACCIONAMIENTO'].isna()) | ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') & (df_combinaciones_validas['FONDERA IMPRESIÓN LADO ACCIONAMIENTO'] == 'SI'))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) ]
    
    #Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA6 es distitno de nan, entonces FONDERA IMPRESION SERVICIO debe ser SI
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['FONDERA IMPRESIÓN LADO SERVICIO'].isna()) | ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') & (df_combinaciones_validas['FONDERA IMPRESIÓN LADO SERVICIO'] == 'SI'))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) ]
    
    # Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA5 es distitno de nan, entonces LARGO_PAPEL_CARA5 debe estar entre los limites de FONDERA LARGO IMPRESIÓN MIN CARA 5 (MM) y FONDERA LARGO IMPRESIÓN MAX CARA 5 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') &
        (df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MIN CARA 5 (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_CARA5'] >= df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MIN CARA 5 (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MAX CARA 5 (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_CARA5'] <= df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MAX CARA 5 (MM)']))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    # Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA6 es distitno de nan, entonces LARGO_PAPEL_CARA6 debe estar entre los limites de FONDERA LARGO IMPRESIÓN MIN CARA 6 (MM) y FONDERA LARGO IMPRESIÓN MAX CARA 6 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') &
        (df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MIN CARA 6 (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_CARA6'] >= df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MIN CARA 6 (MM)'])) &
        (df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MAX CARA 6 (MM)'].isna() | (df_combinaciones_validas['LARGO_PAPEL_CARA6'] <= df_combinaciones_validas['FONDERA LARGO IMPRESIÓN MAX CARA 6 (MM)']))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    # Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA5 es distitno de nan, entonces ANCHO_PAPEL_CARA5 debe estar entre los limites de FONDERA ANCHO IMPRESIÓN MIN CARA 5 (MM) y FONDERA ANCHO IMPRESIÓN MAX CARA 5 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') &
        (df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MIN CARA 5 (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] >= df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MIN CARA 5 (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MAX CARA 5 (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_CARA5'] <= df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MAX CARA 5 (MM)']))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    # Si IMPRESION_FONDERA es on y TIPO_REFUERZO_CARA6 es distitno de nan, entonces ANCHO_PAPEL_CARA6 debe estar entre los limites de FONDERA ANCHO IMPRESIÓN MIN CARA 6 (MM) y FONDERA ANCHO IMPRESIÓN MAX CARA 6 (MM)
    df_combinaciones_validas = df_combinaciones_validas[
        ((df_combinaciones_validas['IMPRESION_FONDERA'] == 'on') &
        (df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MIN CARA 6 (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] >= df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MIN CARA 6 (MM)'])) &
        (df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MAX CARA 6 (MM)'].isna() | (df_combinaciones_validas['ANCHO_PAPEL_CARA6'] <= df_combinaciones_validas['FONDERA ANCHO IMPRESIÓN MAX CARA 6 (MM)']))) |
        (df_combinaciones_validas['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones_validas['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones_validas['TIPO_ENVASE'] == 'BAC s/FLL'))
    ]
    
    df_combinaciones_validas = df_combinaciones_validas[[
        'COD_SKU', 'COD_SKU_SIN_V', 'COD_CLIENTE', 'CLIENTE', 'PRODUCTO', 'PLANTA', 'PAIS', 'NRO LINEA', 'LINEA', 'DESCRIPCION TUBERA', 'DESCRIPCION FONDERA', 'TIPO LINEA'
    ]]
    
    return df_combinaciones_validas

def algoritmo_seguimiento(df_lineas, df_ficha_tecnica):
    """
    Función que evalúa todos los filtros para tracking sin aplicar filtrado secuencial
    """
    valvulas_validas = [
    '14-TUBULAR CON CHARNELA',
    '15-TUBULAR REDUCIDA CON CHARNELA',
    '16-TUBULAR SOBRE INSERTA',
    '17-TUBULAR DOBLE',
    '18-TUBULAR DOBLE (3 Capas)',
    '19-TUBULAR DOBLE (4 Capas)',
    '22-TUBULAR REDUCIDA SOBREINSERTA',
    'TUBULAR SOBRE INSERTA',
    'DOBLE (4 CAPAS)',
    'TUBULAR CON CHARNELA',
    'TUBULAR REDUCIDA CON CHARNELA',
    'TUBULAR DOBLE',
    'DOBLE (3 CAPAS)',
    'TUBULAR CON REDUCIDA CON CHARNELA',
    'TUBULAR DOBLE (4 CAPAS)',
    'TUBULAR DOBLE (3 CAPAS)',
    '17 -TUBULAR DOBLE'
]
    # Crear cross join entre ficha técnica y líneas
    df_ficha_tecnica['key'] = 1
    df_lineas['key'] = 1
    
    df_combinaciones = pd.merge(df_ficha_tecnica, df_lineas, on='key', suffixes=('', '_linea'))
    df_combinaciones = df_combinaciones.drop('key', axis=1)
    
    # Aplicar todas las modificaciones necesarias
    df_combinaciones['TUBERA FUELLE'] = df_combinaciones['TIPO_ENVASE'].apply(lambda x: 'SI' if isinstance(x, str) and 'c/ FLL' in x else np.nan)

    
    df_combinaciones['tiene_film'] = (
        df_combinaciones['DESCRIPCION_HOJA_1'].str.contains('film', case=False, na=False) |
        df_combinaciones['DESCRIPCION_HOJA_2'].str.contains('film', case=False, na=False) |
        df_combinaciones['DESCRIPCION_HOJA_3'].str.contains('film', case=False, na=False) |
        df_combinaciones['DESCRIPCION_HOJA_4'].str.contains('film', case=False, na=False)
    )
    
    # Inicializar seguimiento
    # linea_col = [col for col in df_combinaciones.columns if any(keyword in col.upper() for keyword in ['LINEA', 'TUBERA'])][0]
    df_seguimiento = df_combinaciones[['COD_SKU', 'COD_CLIENTE', 'LINEA', 'PLANTA']].copy()
    # df_seguimiento = df_seguimiento.rename(columns={linea_col: 'LINEA'})
    
    # Evaluar todos los filtros

    # 1. TUBERA - Rango de hojas
    df_seguimiento['TUBERA_RANGO_HOJAS'] = (
        ((df_combinaciones['TUBERA NRO HOJAS PAPEL MIN'].isna() | (df_combinaciones['HOJAS'] >= df_combinaciones['TUBERA NRO HOJAS PAPEL MIN'])) &
         (df_combinaciones['TUBERA NRO HOJAS PAPEL MAX'].isna() | (df_combinaciones['HOJAS'] <= df_combinaciones['TUBERA NRO HOJAS PAPEL MAX'])))
    )
    
    # 2. TUBERA - Ancho papel
    df_seguimiento['TUBERA_ANCHO_PAPEL'] = (
        ((df_combinaciones['TUBERA ANCHO PAPEL MIN (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL'] >= df_combinaciones['TUBERA ANCHO PAPEL MIN (MM)'])) &
         (df_combinaciones['TUBERA ANCHO PAPEL MAX (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL'] <= df_combinaciones['TUBERA ANCHO PAPEL MAX (MM)'])))
    )
    
    # 3. TUBERA - Largo tubo
    df_seguimiento['TUBERA_LARGO_TUBO'] = (
        (
            (df_combinaciones['TIPO_CORTE'] == 'RECTO') &
            (df_combinaciones['TUBERA LARGO TUBO RECTO MIN (MM)'].isna() | (df_combinaciones['LARGO_TUBO'] >= df_combinaciones['TUBERA LARGO TUBO RECTO MIN (MM)'])) &
            (df_combinaciones['TUBERA LARGO TUBO RECTO MAX (MM)'].isna() | (df_combinaciones['LARGO_TUBO'] <= df_combinaciones['TUBERA LARGO TUBO RECTO MAX (MM)']))
        ) |
        (
            (df_combinaciones['TIPO_CORTE'] == 'ESCALONADO') &
            (df_combinaciones['TUBERA LARGO TUBO ESCALONADO MIN (MM)'].isna() | (df_combinaciones['LARGO_TUBO'] >= df_combinaciones['TUBERA LARGO TUBO ESCALONADO MIN (MM)'])) &
            (df_combinaciones['TUBERA LARGO TUBO ESCALONADO MAX (MM)'].isna() | (df_combinaciones['LARGO_TUBO'] <= df_combinaciones['TUBERA LARGO TUBO ESCALONADO MAX (MM)']))
        )
    )
    
    # 4. TUBERA - Ancho saco recto
    df_seguimiento['TUBERA_ANCHO_SACO_RECTO'] = (
        ((df_combinaciones['TIPO_CORTE'] == 'RECTO') &
         (df_combinaciones['TUBERA ANCHO TUBO RECTO MIN (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] >= df_combinaciones['TUBERA ANCHO TUBO RECTO MIN (MM)'])) &
         (df_combinaciones['TUBERA ANCHO TUBO RECTO MAX (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] <= df_combinaciones['TUBERA ANCHO TUBO RECTO MAX (MM)']))) |
        (df_combinaciones['TIPO_CORTE'] != 'RECTO')
    )
    
    # 5. TUBERA - Ancho saco con fuelle
    df_seguimiento['TUBERA_ANCHO_SACO_FUELLE'] = (
        ((df_combinaciones['TIPO_CORTE'] == 'RECTO') &
         (df_combinaciones['TUBERA FUELLE'] == 'SI') & (df_combinaciones['TIPO_ENVASE'].str.contains('c/ FLL', case=False, na=False)) &
         (df_combinaciones['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] >= df_combinaciones['TUBERA ANCHO TUBO RECTO CON FUELLE MIN (MM)'])) &
         (df_combinaciones['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] <= df_combinaciones['TUBERA ANCHO TUBO RECTO CON FUELLE MAX (MM)']))) |
        (df_combinaciones['TIPO_CORTE'] != 'RECTO') |
        ((df_combinaciones['TIPO_CORTE'] == 'RECTO') & (df_combinaciones['TUBERA FUELLE'].isna()))
    )
    
    # 6. TUBERA - Colores con film
    df_seguimiento['TUBERA_COLORES_FILM'] = (
        (df_combinaciones['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'].isna() | df_combinaciones['TUBERA NRO TINTEROS'].isna()) |
        (
            (df_combinaciones['PREIMPRESION'].isna()) &
            (
                (
                    (df_combinaciones['tiene_film']) &
                    (df_combinaciones['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'] == 'NO') &
                    (df_combinaciones['TUBERA NRO TINTEROS'] >= df_combinaciones['CANTIDAD_COLORES'])
                ) |
                (
                    (~df_combinaciones['tiene_film'] | 
                     (df_combinaciones['TUBERA ESTACION ANTIDESLIZANTE INDEPENDIENTE'] == 'SI')) &
                    (df_combinaciones['TUBERA NRO TINTEROS'] >= df_combinaciones['CANTIDAD_COLORES'])
                )
            )
        ) |
        (~df_combinaciones['PREIMPRESION'].isna())
    )
    
    # 7. TUBERA - Lector de tacas
    df_seguimiento['TUBERA_LECTOR_TACAS'] = (
        (df_combinaciones['TUBERA LECTOR DE TACAS'].isna()) |
        ((~df_combinaciones['PREIMPRESION'].isna()) &
         (df_combinaciones['TUBERA LECTOR DE TACAS'] == 'SI')) |
        (df_combinaciones['PREIMPRESION'].isna())
    )
    
    # 8. TUBERA - Desbobinador 4Q
    df_seguimiento['TUBERA_DESBOBINADOR_4Q'] = (
        (df_combinaciones['TUBERA DESBOBINADOR 4Q'].isna()) |
        ((df_combinaciones['tiene_film']) &
         (df_combinaciones['TUBERA DESBOBINADOR 4Q'] == 'SI')) |
        (~df_combinaciones['tiene_film'])
    )
    
    # 9. TUBERA - Rotaliner BAP/PY con MANGA
    df_seguimiento['TUBERA_ROTALINER_BAP'] = (
        (df_combinaciones['TUBERA ROTALINER'].isna()) |
        (((df_combinaciones['TIPO_ENVASE'] == 'BAP') & (df_combinaciones['MANGA'] > 0)) &
         (df_combinaciones['TUBERA ROTALINER'] == 'SI')) |
        ((df_combinaciones['TIPO_ENVASE'] == 'PY') &
         (df_combinaciones['TUBERA ROTALINER'] == 'SI')) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAP') & (df_combinaciones['MANGA'].isna() | (df_combinaciones['MANGA'] == 0))) |
        ((df_combinaciones['TIPO_ENVASE'] != 'BAP') & (df_combinaciones['TIPO_ENVASE'] != 'PY'))
    )
    
    # 10. FONDERA - Refuerzos preimpresos
    df_seguimiento['FONDERA_REFUERZOS_PREIMPRESOS'] = (
        (df_combinaciones['FONDERA REFUERZOS PREIMPRESOS'].isna()) |
        (((~df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) | (~df_combinaciones['TIPO_REFUERZO_CARA6'].isna())) &
         (df_combinaciones['FONDERA REFUERZOS PREIMPRESOS'] == 'SI')) |
        ((df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) & (df_combinaciones['TIPO_REFUERZO_CARA6'].isna())) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 11. FONDERA - Largo saco
    df_seguimiento['FONDERA_LARGO_SACO'] = (
        ((df_combinaciones['TIPO_CORTE'] == 'RECTO') &
         (df_combinaciones['FONDERA LARGO SACO RECTO MIN (MM)'].isna() | (df_combinaciones['LARGO_SACO'] >= df_combinaciones['FONDERA LARGO SACO RECTO MIN (MM)'])) &
         (df_combinaciones['FONDERA LARGO SACO RECTO MAX (MM)'].isna() | (df_combinaciones['LARGO_SACO'] <= df_combinaciones['FONDERA LARGO SACO RECTO MAX (MM)']))) |
        ((df_combinaciones['TIPO_CORTE'] == 'ESCALONADO') &
         (df_combinaciones['FONDERA LARGO SACO ESCALONADO MIN (MM)'].isna() | (df_combinaciones['LARGO_SACO'] >= df_combinaciones['FONDERA LARGO SACO ESCALONADO MIN (MM)'])) &
         (df_combinaciones['FONDERA LARGO SACO ESCALONADO MAX (MM)'].isna() | (df_combinaciones['LARGO_SACO'] <= df_combinaciones['FONDERA LARGO SACO ESCALONADO MAX (MM)']))) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 12. FONDERA - Ancho saco
    df_seguimiento['FONDERA_ANCHO_SACO'] = (
        ((df_combinaciones['FONDERA ANCHO SACO MIN (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] >= df_combinaciones['FONDERA ANCHO SACO MIN (MM)'])) &
         (df_combinaciones['FONDERA ANCHO SACO MAX (MM)'].isna() | (df_combinaciones['ANCHO_SACO'] <= df_combinaciones['FONDERA ANCHO SACO MAX (MM)']))) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 13. FONDERA - Ancho fondo
    df_seguimiento['FONDERA_ANCHO_FONDO'] = (
        ((df_combinaciones['ANCHO_CARA_5'].isna()) & (df_combinaciones['ANCHO_CARA_6'].isna())) |
        ((~df_combinaciones['ANCHO_CARA_5'].isna()) &
         (df_combinaciones['FONDERA ANCHO FONDO MIN (MM)'].isna() | (df_combinaciones['ANCHO_CARA_5'] >= df_combinaciones['FONDERA ANCHO FONDO MIN (MM)'])) &
         (df_combinaciones['FONDERA ANCHO FONDO MAX (MM)'].isna() | (df_combinaciones['ANCHO_CARA_5'] <= df_combinaciones['FONDERA ANCHO FONDO MAX (MM)']))) |
        ((~df_combinaciones['ANCHO_CARA_6'].isna()) &
         (df_combinaciones['FONDERA ANCHO FONDO MIN (MM)'].isna() | (df_combinaciones['ANCHO_CARA_6'] >= df_combinaciones['FONDERA ANCHO FONDO MIN (MM)'])) &
         (df_combinaciones['FONDERA ANCHO FONDO MAX (MM)'].isna() | (df_combinaciones['ANCHO_CARA_6'] <= df_combinaciones['FONDERA ANCHO FONDO MAX (MM)']))) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 14. FONDERA - Distancia entre centros
    df_seguimiento['FONDERA_DISTANCIA_CENTROS'] = (
        ((df_combinaciones['ANCHO_CARA_5'].isna()) & (df_combinaciones['ANCHO_CARA_6'].isna())) |
        ((df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna()) & (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna())) |
        ((~df_combinaciones['ANCHO_CARA_5'].isna()) & (~df_combinaciones['ANCHO_CARA_6'].isna()) &
         (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 0.5*df_combinaciones['ANCHO_CARA_5'] - 0.5*df_combinaciones['ANCHO_CARA_6'] >= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
         (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 0.5*df_combinaciones['ANCHO_CARA_5'] - 0.5*df_combinaciones['ANCHO_CARA_6'] <= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((~df_combinaciones['ANCHO_CARA_5'].isna()) & (df_combinaciones['ANCHO_CARA_6'].isna()) &
        (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 1*df_combinaciones['ANCHO_CARA_5'] >= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
        (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 1*df_combinaciones['ANCHO_CARA_5'] <= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((df_combinaciones['ANCHO_CARA_5'].isna()) & (~df_combinaciones['ANCHO_CARA_6'].isna()) &
        (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 1*df_combinaciones['ANCHO_CARA_6'] >= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MIN (MM)'])) &
        (df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)'].isna() | (df_combinaciones['LARGO_SACO'] - 1*df_combinaciones['ANCHO_CARA_6'] <= df_combinaciones['FONDERA DISTANCIA ENTRE CENTROS MAX (MM)']))) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 15. FONDERA - Válvula equipos
    df_seguimiento['FONDERA_VALVULA_EQUIPOS'] = (
        (df_combinaciones['FONDERA NRO PAPELES POR EQ VAL'].isna()) |
        ((df_combinaciones['TIPO_VALVULA'].str.upper().isin(['TUBULAR CON CHARNELA', 'TUBULAR REDUCIDA CON CHARNELA', 'TUBULAR SOBRE INSERTA', 'TUBULAR DOBLE', 'TUBULAR DOBLE (3 Capas)', 'TUBULAR DOBLE (4 Capas)', 'TUBULAR REDUCIDA', 'SOBREINSERTA'])) &
         (df_combinaciones['FONDERA NRO PAPELES POR EQ VAL'] >= 2)) |
        (~df_combinaciones['TIPO_VALVULA'].str.upper().isin(['TUBULAR CON CHARNELA', 'TUBULAR REDUCIDA CON CHARNELA', 'TUBULAR SOBRE INSERTA', 'TUBULAR DOBLE', 'TUBULAR DOBLE (3 Capas)', 'TUBULAR DOBLE (4 Capas)', 'TUBULAR REDUCIDA', 'SOBREINSERTA'])) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 16. FONDERA - Largo papel válvula
    df_seguimiento['FONDERA_LARGO_PAPEL_VAL'] = (
        ((~df_combinaciones['TIPO_VALVULA'].isna()) &
         (df_combinaciones['FONDERA LARGO PAPEL VAL MIN (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_VALVULA'] >= df_combinaciones['FONDERA LARGO PAPEL VAL MIN (MM)'])) &
         (df_combinaciones['FONDERA LARGO PAPEL VAL MAX (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_VALVULA'] <= df_combinaciones['FONDERA LARGO PAPEL VAL MAX (MM)']))) | 
        (df_combinaciones['TIPO_VALVULA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 17. FONDERA - Válvula con manga
    df_seguimiento['FONDERA_VALVULA_MANGA'] = (
        ((df_combinaciones['TIPO_VALVULA'].str.contains('INSERTA CON MANGA', case=False, na=False)) &
        (df_combinaciones['FONDERA LARGO VAL CON MANGA MIN (MM)'].isna() | (df_combinaciones['LARGO_VALVULA'] >= df_combinaciones['FONDERA LARGO VAL CON MANGA MIN (MM)'])) &
        (df_combinaciones['FONDERA LARGO VAL CON MANGA MAX (MM)'].isna() | (df_combinaciones['LARGO_VALVULA'] <= df_combinaciones['FONDERA LARGO VAL CON MANGA MAX (MM)']))) |
        (~df_combinaciones['TIPO_VALVULA'].str.contains('INSERTA CON MANGA', case=False, na=False)) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 18. FONDERA - Largo toma
    df_seguimiento['FONDERA_LARGO_TOMA'] = (
        ((~df_combinaciones['LARGO_TOMA'].isna()) &
        (df_combinaciones['FONDERA LARGO TOMA MAX (MM)'].isna() | (df_combinaciones['LARGO_TOMA'] <= df_combinaciones['FONDERA LARGO TOMA MAX (MM)'])) &
        (df_combinaciones['FONDERA LARGO TOMA MIN (MM)'].isna() | (df_combinaciones['LARGO_TOMA'] >= df_combinaciones['FONDERA LARGO TOMA MIN (MM)']))) |
        (df_combinaciones['LARGO_TOMA'].isna()) |
        (
            (df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') |
            (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')
        ) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 19. FONDERA - Ancho papel válvula
    df_seguimiento['FONDERA_ANCHO_PAPEL_VAL'] = (
        ((~df_combinaciones['ANCHO_PAPEL_VALVULA'].isna()) &
         (df_combinaciones['FONDERA ANCHO ROLLO MIN (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_VALVULA'] >= df_combinaciones['FONDERA ANCHO ROLLO MIN (MM)'])) &
         (df_combinaciones['FONDERA ANCHO ROLLO MAX (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_VALVULA'] <= df_combinaciones['FONDERA ANCHO ROLLO MAX (MM)']))) |
        (df_combinaciones['ANCHO_PAPEL_VALVULA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 20. FONDERA - Ancho válvula
    df_seguimiento['FONDERA_ANCHO_VALVULA'] = (
        ((~df_combinaciones['ANCHO_VALVULA'].isna()) & (df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas)) &
         (df_combinaciones['FONDERA ANCHO VALVULA MIN (MM)'].isna() | (df_combinaciones['ANCHO_VALVULA'] >= df_combinaciones['FONDERA ANCHO VALVULA MIN (MM)'])) &
         (df_combinaciones['FONDERA ANCHO VALVULA MAX (MM)'].isna() | (df_combinaciones['ANCHO_VALVULA'] <= df_combinaciones['FONDERA ANCHO VALVULA MAX (MM)']))) |
        (df_combinaciones['ANCHO_VALVULA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP') |
        (~df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas))
    )
    
    # 21. FONDERA - Largo válvula
    df_seguimiento['FONDERA_LARGO_VALVULA'] = (
        ((~df_combinaciones['LARGO_VALVULA'].isna()) & (df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas)) &
         (df_combinaciones['FONDERA LARGO VALVULA MIN (MM)'].isna() | (df_combinaciones['LARGO_VALVULA'] >= df_combinaciones['FONDERA LARGO VALVULA MIN (MM)'])) &
         (df_combinaciones['FONDERA LARGO VALVULA MAX (MM)'].isna() | (df_combinaciones['LARGO_VALVULA'] <= df_combinaciones['FONDERA LARGO VALVULA MAX (MM)']))) |
        (df_combinaciones['LARGO_VALVULA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP') |
        (~df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas))
    )
    
    # 22. FONDERA - Dispositivo uñero
    df_seguimiento['FONDERA_DISPOSITIVO_UNERO'] = (
        (df_combinaciones['FONDERA DISPOSITIVO UÑERO'].isna()) |
        ((df_combinaciones['UNERO_VALVULA'].fillna('').str.lower() == 'si') & (df_combinaciones['FONDERA DISPOSITIVO UÑERO'].fillna('').str.lower() == 'si')) |
        (df_combinaciones['UNERO_VALVULA'].fillna('').str.lower() != 'si') |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP')
    )
    
    # 23. FONDERA - Longitud papel
    df_seguimiento['FONDERA_LONGITUD_PAPEL'] = (
        ((df_combinaciones['FONDERA LONGITUD PAPEL MIN (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_VALVULA'] >= df_combinaciones['FONDERA LONGITUD PAPEL MIN (MM)'])) & (df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas)) &
         (df_combinaciones['FONDERA LONGITUD PAPEL MAX (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_VALVULA'] <= df_combinaciones['FONDERA LONGITUD PAPEL MAX (MM)']))) |
        (df_combinaciones['LARGO_PAPEL_VALVULA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL')) |
        (df_combinaciones['TIPO_ENVASE'] == 'BAP') |
        (~df_combinaciones['TIPO_VALVULA'].isin(valvulas_validas))
    )
    
    # 24. FONDERA - Refuerzo accionamiento
    df_seguimiento['FONDERA_REFUERZO_ACCIONAMIENTO'] = (
        (df_combinaciones['FONDERA REFUERZO DE FONDO LADO ACCIONAMIENTO'].isna()) |
        ((~df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) & (df_combinaciones['FONDERA REFUERZO DE FONDO LADO ACCIONAMIENTO'] == 'SI')) |
        (df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 25. FONDERA - Refuerzo servicio
    df_seguimiento['FONDERA_REFUERZO_SERVICIO'] = (
        (df_combinaciones['FONDERA REFUERZO DE FONDO LADO SERVICIO'].isna()) |
        ((~df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) & (df_combinaciones['FONDERA REFUERZO DE FONDO LADO SERVICIO'] == 'SI')) |
        (df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 26. FONDERA - Largo papel refuerzo cara 5
    df_seguimiento['FONDERA_LARGO_PAPEL_REF_CARA5'] = (
        # Bloque 1: Validación técnica (Solo si hay un refuerzo real con medida)
        ((~df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) & 
         (df_combinaciones['TIPO_REFUERZO_CARA5'] != 0) & 
         (df_combinaciones['TIPO_REFUERZO_CARA5'] != 'SIN Refuerzo') &
         (df_combinaciones['LARGO_PAPEL_CARA5'] > 0) &
         (df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'].isna() | 
          (df_combinaciones['LARGO_PAPEL_CARA5'] >= df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'])) &
         (df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 5 (MM)'].isna() | 
          (df_combinaciones['LARGO_PAPEL_CARA5'] <= df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 5 (MM)']))) |
        
        # Bloque 2: Excepciones donde se considera cumplida la restricción
        (df_combinaciones['LARGO_PAPEL_CARA5'].isna()) | 
        (df_combinaciones['LARGO_PAPEL_CARA5'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) | 
        (df_combinaciones['TIPO_REFUERZO_CARA5'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA5'] == 'SIN Refuerzo') |
        (df_combinaciones['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    )
    
    # 27. FONDERA - Largo papel refuerzo cara 6
    df_seguimiento['FONDERA_LARGO_PAPEL_REF_CARA6'] = (
        # Bloque 1: Validación técnica (Solo si hay un refuerzo real con medida)
        ((~df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) & 
         (df_combinaciones['TIPO_REFUERZO_CARA6'] != 0) & 
         (df_combinaciones['TIPO_REFUERZO_CARA6'] != 'SIN Refuerzo') &
         (df_combinaciones['LARGO_PAPEL_CARA6'] > 0) &
         (df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'].isna() | 
          (df_combinaciones['LARGO_PAPEL_CARA6'] >= df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'])) &
         (df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 6 (MM)'].isna() | 
          (df_combinaciones['LARGO_PAPEL_CARA6'] <= df_combinaciones['FONDERA LARGO PAPEL REFUERZO FONDO MAX CARA 6 (MM)']))) |
        
        # Bloque 2: Excepciones donde se considera cumplida la restricción
        (df_combinaciones['LARGO_PAPEL_CARA6'].isna()) | 
        (df_combinaciones['LARGO_PAPEL_CARA6'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) | 
        (df_combinaciones['TIPO_REFUERZO_CARA6'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA6'] == 'SIN Refuerzo') |
        (df_combinaciones['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    )
    
    # 28. FONDERA - Ancho papel refuerzo cara 5
    df_seguimiento['FONDERA_ANCHO_PAPEL_REF_CARA5'] = (
        # Bloque 1: Validación técnica (Solo si hay refuerzo real y ancho positivo)
        ((~df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) & 
         (df_combinaciones['TIPO_REFUERZO_CARA5'] != 0) & 
         (df_combinaciones['TIPO_REFUERZO_CARA5'] != 'SIN Refuerzo') & 
         (df_combinaciones['ANCHO_PAPEL_CARA5'] > 0) &
         (df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'].isna() | 
          (df_combinaciones['ANCHO_PAPEL_CARA5'] >= df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 5 (MM)'])) &
         (df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 5 (MM)'].isna() | 
          (df_combinaciones['ANCHO_PAPEL_CARA5'] <= df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 5 (MM)']))) |
        
        # Bloque 2: Excepciones (Restricción cumplida)
        (df_combinaciones['ANCHO_PAPEL_CARA5'].isna()) | 
        (df_combinaciones['ANCHO_PAPEL_CARA5'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA5'].isna()) | 
        (df_combinaciones['TIPO_REFUERZO_CARA5'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA5'] == 'SIN Refuerzo') |
        (df_combinaciones['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    )
    
    # 29. FONDERA - Ancho papel refuerzo cara 6
    df_seguimiento['FONDERA_ANCHO_PAPEL_REF_CARA6'] = (
        # Bloque 1: Validación técnica (Solo si hay refuerzo real y ancho positivo)
        ((~df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) & 
         (df_combinaciones['TIPO_REFUERZO_CARA6'] != 0) & 
         (df_combinaciones['TIPO_REFUERZO_CARA6'] != 'SIN Refuerzo') & 
         (df_combinaciones['ANCHO_PAPEL_CARA6'] > 0) &
         (df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'].isna() | 
          (df_combinaciones['ANCHO_PAPEL_CARA6'] >= df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MIN CARA 6 (MM)'])) &
         (df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 6 (MM)'].isna() | 
          (df_combinaciones['ANCHO_PAPEL_CARA6'] <= df_combinaciones['FONDERA ANCHO PAPEL REFUERZO FONDO MAX CARA 6 (MM)']))) |
        
        # Bloque 2: Excepciones (Restricción cumplida)
        (df_combinaciones['ANCHO_PAPEL_CARA6'].isna()) | 
        (df_combinaciones['ANCHO_PAPEL_CARA6'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA6'].isna()) | 
        (df_combinaciones['TIPO_REFUERZO_CARA6'] == 0) |
        (df_combinaciones['TIPO_REFUERZO_CARA6'] == 'SIN Refuerzo') |
        (df_combinaciones['TIPO_ENVASE'].isin(['BAC c/FLL', 'BAC s/FLL']))
    )
    
    # 30. FONDERA - Impresión accionamiento
    df_seguimiento['FONDERA_IMP_ACCIONAMIENTO'] = (
        (df_combinaciones['FONDERA IMPRESIÓN LADO ACCIONAMIENTO'].isna()) |
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') & (df_combinaciones['FONDERA IMPRESIÓN LADO ACCIONAMIENTO'] == 'SI')) |
        (df_combinaciones['IMPRESION_FONDERA'].isna())
    )
    
    # 31. FONDERA - Impresión servicio
    df_seguimiento['FONDERA_IMP_SERVICIO'] = (
        (df_combinaciones['FONDERA IMPRESIÓN LADO SERVICIO'].isna()) |
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') & (df_combinaciones['FONDERA IMPRESIÓN LADO SERVICIO'] == 'SI')) |
        (df_combinaciones['IMPRESION_FONDERA'].isna())
    )
    
    # 32. FONDERA - Impresión largo cara 5
    df_seguimiento['FONDERA_IMP_LARGO_CARA5'] = (
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') &
         (df_combinaciones['FONDERA LARGO IMPRESIÓN MIN CARA 5 (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_CARA5'] >= df_combinaciones['FONDERA LARGO IMPRESIÓN MIN CARA 5 (MM)'])) &
         (df_combinaciones['FONDERA LARGO IMPRESIÓN MAX CARA 5 (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_CARA5'] <= df_combinaciones['FONDERA LARGO IMPRESIÓN MAX CARA 5 (MM)']))) |
        (df_combinaciones['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 33. FONDERA - Impresión largo cara 6
    df_seguimiento['FONDERA_IMP_LARGO_CARA6'] = (
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') &
         (df_combinaciones['FONDERA LARGO IMPRESIÓN MIN CARA 6 (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_CARA6'] >= df_combinaciones['FONDERA LARGO IMPRESIÓN MIN CARA 6 (MM)'])) &
         (df_combinaciones['FONDERA LARGO IMPRESIÓN MAX CARA 6 (MM)'].isna() | (df_combinaciones['LARGO_PAPEL_CARA6'] <= df_combinaciones['FONDERA LARGO IMPRESIÓN MAX CARA 6 (MM)']))) |
        (df_combinaciones['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 34. FONDERA - Impresión ancho cara 5
    df_seguimiento['FONDERA_IMP_ANCHO_CARA5'] = (
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') &
         (df_combinaciones['FONDERA ANCHO IMPRESIÓN MIN CARA 5 (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_CARA5'] >= df_combinaciones['FONDERA ANCHO IMPRESIÓN MIN CARA 5 (MM)'])) &
         (df_combinaciones['FONDERA ANCHO IMPRESIÓN MAX CARA 5 (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_CARA5'] <= df_combinaciones['FONDERA ANCHO IMPRESIÓN MAX CARA 5 (MM)']))) |
        (df_combinaciones['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # 35. FONDERA - Impresión ancho cara 6
    df_seguimiento['FONDERA_IMP_ANCHO_CARA6'] = (
        ((df_combinaciones['IMPRESION_FONDERA'] == 'on') &
         (df_combinaciones['FONDERA ANCHO IMPRESIÓN MIN CARA 6 (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_CARA6'] >= df_combinaciones['FONDERA ANCHO IMPRESIÓN MIN CARA 6 (MM)'])) &
         (df_combinaciones['FONDERA ANCHO IMPRESIÓN MAX CARA 6 (MM)'].isna() | (df_combinaciones['ANCHO_PAPEL_CARA6'] <= df_combinaciones['FONDERA ANCHO IMPRESIÓN MAX CARA 6 (MM)']))) |
        (df_combinaciones['IMPRESION_FONDERA'].isna()) |
        ((df_combinaciones['TIPO_ENVASE'] == 'BAC c/FLL') | (df_combinaciones['TIPO_ENVASE'] == 'BAC s/FLL'))
    )
    
    # Calcular estadísticas
    filtro_cols = [col for col in df_seguimiento.columns if col.startswith(('TUBERA_', 'FONDERA_'))]
    df_seguimiento['TOTAL_FILTROS_PASADOS'] = df_seguimiento[filtro_cols].sum(axis=1)
    df_seguimiento['TOTAL_FILTROS'] = len(filtro_cols)
    df_seguimiento['PORCENTAJE_EXITO'] = (df_seguimiento['TOTAL_FILTROS_PASADOS'] / df_seguimiento['TOTAL_FILTROS'] * 100).round(2)
    
    return df_seguimiento

def algoritmo_demanda_interna(df_seguimiento):

    # Definir las condiciones de match entre COD_SKU y PLANTA
    conditions = [
        # PR con SKCL
        ((df_seguimiento['COD_SKU'].str.startswith('PR')) & (df_seguimiento['PLANTA'] == 'SKCL')),
        # SK con SKBR-CN o SKBR-PS
        ((df_seguimiento['COD_SKU'].str.startswith('SK')) & (df_seguimiento['PLANTA'].isin(['SKBR-CN', 'SKBR-PS']))),
        # FX con SKMX-G o SKMX-I
        ((df_seguimiento['COD_SKU'].str.startswith('FX')) & (df_seguimiento['PLANTA'].isin(['SKMX-G', 'SKMX-I']))),
        # FO con SKPE
        ((df_seguimiento['COD_SKU'].str.startswith('FO')) & (df_seguimiento['PLANTA'] == 'SKPE'))
    ]

    # Combinar todas las condiciones con OR
    mask = pd.concat(conditions, axis=1).any(axis=1)

    # Filtrar el dataframe con las condiciones de match
    df_filtered = df_seguimiento[mask]

    # Crear una columna auxiliar para mapear plantas a países o mantener la planta
    def map_planta_to_pais(planta):
        if planta in ['SKBR-CN', 'SKBR-PS']:
            return 'BRASIL'
        elif planta in ['SKMX-G', 'SKMX-I']:
            return 'MÉXICO'
        else:
            return planta  # Mantener SKCL y SKPE como están

    df_filtered['PAIS'] = df_filtered['PLANTA'].apply(map_planta_to_pais)

    # Agrupar por COD_SKU y PAIS, y verificar si todos los PORCENTAJE_EXITO < 100
    # Para BRASIL y MÉXICO, verificamos que todas las líneas de ambas plantas cumplan
    df_result = df_filtered.groupby(['COD_SKU', 'PAIS']).filter(
        lambda x: (x['PORCENTAJE_EXITO'] < 100).all()
    )[['COD_SKU', 'PAIS']].drop_duplicates()

    # Renombrar la columna PAIS a PLANTA para mantener el formato solicitado
    df_demanda_interna_infactible = df_result.rename(columns={'PAIS': 'PLANTA/S'})

    return df_demanda_interna_infactible

def algoritmo_demanda_interna_pais(df_seguimiento, df_ficha_tecnica):

    
    # Filtrar por demanda interna
    df_ficha_tecnica = df_ficha_tecnica[df_ficha_tecnica['SKU_DEMANDA_INTERNA'] == 'on']
    
    #Filtrar por porcentaje exito = 100
    df_seguimiento = df_seguimiento[df_seguimiento['PORCENTAJE_EXITO'] < 100]

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
            return planta  # por si aparece alguna planta inesperada


    # Crear columna auxiliar en df_seguimiento con el país mapeado
    df_seguimiento['PAIS_PRODUCCION'] = df_seguimiento['PLANTA'].apply(map_planta_to_pais)

    # Hacer merge para cruzar info entre ficha técnica y seguimiento
    df_merged = df_seguimiento.merge(
        df_ficha_tecnica[['COD_SKU', 'PAIS_DESTINO']], 
        on='COD_SKU',
        how='inner'
    )

    # Filtrar solo los que cumplen con la coincidencia
    df_filtrado = df_merged[df_merged['PAIS_PRODUCCION'] == df_merged['PAIS_DESTINO']]

    # Quedarse solo con COD_SKU y PLANTA (únicos)
    df_resultado = df_filtrado[['COD_SKU', 'PAIS_DESTINO', 'PLANTA']].drop_duplicates()


    return df_resultado

def algoritmo_gh():
    df_lineas = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Lineas', skiprows=2, usecols='C:BW')
    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx')    
    
    df_combinaciones_validas = algoritmo_gh_combinaciones_validas(df_lineas, df_ficha_tecnica)
    df_seguimiento = algoritmo_seguimiento(df_lineas, df_ficha_tecnica)
    
    df_demanda_interna_infactible = algoritmo_demanda_interna(df_seguimiento)
    df_demanda_interna_infactible_pais = algoritmo_demanda_interna_pais(df_seguimiento, df_ficha_tecnica)
    
    df_combinaciones_validas.to_excel('ResultadosEstaticos/Resultados/df_homologaciones.xlsx', index=False)
    df_seguimiento.to_excel('ResultadosEstaticos/Errores/df_homologacion_seguimiento.xlsx', index=False)
    df_demanda_interna_infactible.to_excel('ResultadosEstaticos/Errores/df_demanda_interna_infactible.xlsx', index=False)
    df_demanda_interna_infactible_pais.to_excel('ResultadosEstaticos/Errores/df_demanda_interna_infactible_pais.xlsx', index=False)    
    
    cantidad_skus_homologados = df_combinaciones_validas['COD_SKU'].nunique()
    cantidad_skus_totales = df_seguimiento['COD_SKU'].nunique()
    porcentaje_homologacion = round((cantidad_skus_homologados / cantidad_skus_totales * 100), 2)
    cantidad_skus_sin_asignacion_planta_actual = df_demanda_interna_infactible['COD_SKU'].nunique()
    
    dict_metricas_homologador = {
        'cantidad_skus_homologados': cantidad_skus_homologados,
        'porcentaje_homologacion': porcentaje_homologacion,
        'cantidad_skus_sin_asignacion_planta_actual': cantidad_skus_sin_asignacion_planta_actual
    }
    
    
    return dict_metricas_homologador