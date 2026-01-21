import pandas as pd
import pyomo.environ as pyo
import numpy as np
import os
import time
import pickle

from .utils import get_model_set_dictionary

def export_model_results(model: pyo.Model, scenario_name: str, nombre_corrida: str) -> None:
    start_time = time.time() 
    model_set_dictionary = get_model_set_dictionary(model)
    model_params = {str(par): {key: par[key] for key in par.keys()} if par.index_set().dimen > 0 else par.value for par in model.component_objects(pyo.Param)}
    model_vars = {str(var): {key: var[key].value for key in var.keys()} if var.index_set().dimen > 0 else var.value for var in model.component_objects(pyo.Var)}
    
    set_dataFrames = {}
    var_dataFrames = {}
    par_dataFrames = {}

    for set in model.component_objects(pyo.Set):
        if len(set) == 0:
            continue
        first_instance = list(set)[0]
        if type(first_instance) == tuple:
            set_items = [i for i in list(set)]
            set_columns = [model_set_dictionary[key] for key in first_instance]
        else:
            set_items = [i for i in list(set)]
            set_columns = [model_set_dictionary[first_instance]]
        df = pd.DataFrame(columns=set_columns, data=set_items)
        set_dataFrames[set.name] = df
        
    for var in model_vars.keys():
        if model_vars[var] is None:          # ← ignora variables sin datos
            #print(f"[WARN] '{var}' llegó como None; se omite.")
            continue
        
        if type(model_vars[var]) != float:
            var_items = [sets + (value,) if type(sets) == tuple else (sets, value) for sets, value in model_vars[var].items()]
            
            first_key = list(model_vars[var].keys())[0]

            if isinstance(first_key, str):
            # Para strings, usar directamente como una sola columna
                var_columns = [model_set_dictionary.get(first_key, first_key)] + ["Value"]
            elif type(first_key) != int:
                # Para tuplas, iterar sobre los elementos de la tupla
                var_columns = [model_set_dictionary[key] for key in first_key] + ["Value"]
            else:
                # Para int, usar directamente
                var_columns = [model_set_dictionary[first_key]] + ["Value"]
        else:
            var_items = [model_vars[var]]
            var_columns = ["Value"]
        
        df = pd.DataFrame(columns=var_columns, data=var_items)
        df.dropna(axis='columns')
        df = df[(df["Value"] >= 0.01) & (df["Value"] != "")]
        var_dataFrames[var] = df

    for par in model_params.keys():
        if type(model_params[par]) not in [int, float, np.float64]:
            par_items = [sets + (value,) if type(sets) == tuple else (sets, value) for sets, value in model_params[par].items()]
            keys = list(model_params[par].keys())
            if type(keys[0]) == tuple:
                par_columns = [model_set_dictionary[key] for key in keys[0]] + ["Value"]
            else:
                par_columns = [model_set_dictionary[keys[0]]] + ["Value"]
        else:
            par_items = [model_params[par]]
            par_columns = ["Value"]
        
        df = pd.DataFrame(columns=par_columns, data=par_items)
        df.dropna(axis='columns')
        df = df[(df["Value"] != 0) & (df["Value"] != "")]
        par_dataFrames[par] = df

    end_time1 = time.time()  # End timer
    elapsed_time = end_time1 - start_time  # Time in seconds

    #print(f"GDX: {elapsed_time:.2f}")
    ##################################################
    ## tablas consolidadas ###########################
    ##################################################

    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx')
    df_materia_prima = pd.read_excel('ResultadosEstaticos/Resultados/df_materia_prima.xlsx')

    df_composicion_sku_mp = pd.read_excel('ResultadosEstaticos/Resultados/df_composicion_sku_mp.xlsx')
    
    with open(f'Corridas/{nombre_corrida}/Preprocesamiento/datos_completos.pkl', 'rb') as f:
        inputs_modelo = pickle.load(f)
        
    factor_conversion_modelo = inputs_modelo['factor_conversion']

    ####### balance inventario sheet ###########################
    asignacion_sku = []
    #vars
    asignacion_fabrica = var_dataFrames['asignacion_fabrica']
    asignacion_linea = var_dataFrames['asignacion_linea']
    cant_producida = var_dataFrames['CANT_PRODUCIDA_SKU']
    cant_entregada = var_dataFrames['CANT_ENTREGADA_SKU']
    inventario = var_dataFrames['INVENTARIO_SKU']
    #pars
    demands = par_dataFrames['demanda']
    inventario_inicial = par_dataFrames['inventario_inicial_sku_fabrica']
    SS_faltantes = par_dataFrames['SS_faltante']
    ordenes_abiertas = par_dataFrames['ordenes_abiertas']

    #renaming
    asignacion_linea.columns = ['SKU', 'T_d', 'L', 'TP', 'Value']

    for sku in model.SKU:
        for factory in model.F:
            #df por sku-factory, sin t
            inventory_rows = inventario[
                (inventario['F']==factory) & 
                (inventario['SKU']==sku)
            ]
            produced_rows = asignacion_fabrica[
                (asignacion_fabrica['SKU'] == sku) & 
                (asignacion_fabrica['F'] == factory)
            ]
            delivered_rows = cant_entregada[
                (cant_entregada['SKU'] == sku) & 
                (cant_entregada['F'] == factory)
            ]

            if ((produced_rows['Value'] != 0).any() or (delivered_rows['Value'] != 0).any()): #sku-factory con inventario, producción o entrega != 0
                for t in model.T:
                    II = None
                    SSf = None
                    if t==1:
                        # inventario inicial
                        II_rows = inventario_inicial[
                            (inventario_inicial['F']==factory) &
                            (inventario_inicial['SKU']==sku) &
                            (inventario_inicial['Value'] > 0.5)
                        ]
                        if not II_rows.empty:
                            II = II_rows.iloc[0]['Value']

                        SSf_rows = SS_faltantes[
                            (SS_faltantes['SKU']==sku)
                        ]
                        if not SSf_rows.empty:
                            SSf = SSf_rows.iloc[0]['Value']

                    # Buscar ordenes abiertas
                    OA = None
                    OA_rows = ordenes_abiertas[
                        (ordenes_abiertas['SKU']==sku) &
                        (ordenes_abiertas['T']==t)
                    ]
                    if not OA_rows.empty:
                        OA = OA_rows.iloc[0]['Value']
                    
                    # Buscar la línea y la cantidad producida
                    line = None
                    linea_rows = asignacion_linea[
                        (asignacion_linea['SKU'] == sku) & 
                        (asignacion_linea['TP'] == t) & # estoy buscando el momento en que se produce
                        (asignacion_linea['Value'] > 0.5)
                    ]

                    lines = None
                    production_qty = 0                    
                    if not linea_rows.empty:
                        #### puede tener más de una línea. no se debería reportar así (Gabriela no estaría orgullosa)####
                        lines = ', '.join(linea_rows['L'].unique()) 
                        # Iterate through each line
                        for line in linea_rows['L'].unique():
                            if (factory, line) in model.F_L:
                                prod_rows = cant_producida[
                                    (cant_producida['L'] == line) & 
                                    (cant_producida['SKU'] == sku) & 
                                    (cant_producida['T'] == t)
                                ]
                                if not prod_rows.empty:
                                    production_qty += prod_rows['Value'].sum()
                                
                    
                    delivered_qty = None
                    delivered_row = delivered_rows[
                        (delivered_rows['T'] == t)
                    ]
                    if not delivered_row.empty:
                        delivered_qty = delivered_row.iloc[0]['Value']

                    inventory_qty = None
                    inventory_row = inventory_rows[
                        (inventory_rows['T']==t)
                        ]
                    if not inventory_row.empty:
                        inventory_qty = inventory_row.iloc[0]['Value']        

                    demand_val = None
                    demand_rows = demands[
                        (demands['SKU']==sku) &
                        (demands['T']==t)
                        ]
                    if not demand_rows.empty:
                        demand_val = demand_rows.iloc[0]['Value']

                    # Buscar información complementaria del SKU 
                    sku_info_rows = df_ficha_tecnica[
                        (df_ficha_tecnica['COD_SKU_SIN_V'] == sku)
                    ]
                    descripcion_sku = sku_info_rows.iloc[0]['PRODUCTO'] if not sku_info_rows.empty else ''
                    cliente = sku_info_rows.iloc[0]['COD_CLIENTE'] if not sku_info_rows.empty else ''
                    descripcion_cliente = sku_info_rows.iloc[0]['CLIENTE'] if not sku_info_rows.empty else ''
                    pais = sku_info_rows.iloc[0]['PAIS_DESTINO'] if not sku_info_rows.empty else ''

                    # Agregar resultados a la lista
                    asignacion_sku.append({
                        'SKU': sku,
                        'Descripción SKU': descripcion_sku,
                        'Cliente': cliente,
                        'Descripción Cliente': descripcion_cliente,
                        'País Destino': pais,
                        'Planta que lo produce': factory,
                        'Mes en que produce': t,
                        'Linea/s en que produce': lines if lines else '',
                        'Cantidad Producida': production_qty if (production_qty != 0) else '',
                        'Cantidad Entregada': delivered_qty if delivered_qty else '',
                        'Demanda': demand_val if demand_val else '',
                        'Inventario inicial': II if II else '',
                        'Safety stock faltante': SSf if SSf else '',
                        'Órdenes abiertas': OA if OA else '',
                        'Inventario': inventory_qty if inventory_qty else ''
                    })

    end_time2 = time.time()  # End timer
    elapsed_time = end_time2 - end_time1  # Time in seconds

    #print(f"Balance_Inventario: {elapsed_time:.2f}")

    ####### utilizacion de lineas sheet ###########################
    utilizacion_lineas = []
    #vars
    carga_linea = var_dataFrames['CARGA_LINEA'] # miles de saco
    horas_extras = var_dataFrames['HORAS_EXTRAS'] # horas
    #pars
    velocidad_linea = par_dataFrames['velocidad_produccion']  # ¿sacos por hora?
    capacidad_linea = par_dataFrames['capacidad_linea'] # horas?

    for (f,l) in model.F_L:
        for t in model.T:

            CP = None
            CP_rows = cant_producida[
                (cant_producida['L']==l) &
                (cant_producida['T']==t)
            ]
            if not CP_rows.empty:
                CP = CP_rows['Value'].sum()
                CL = None
                CL_rows = carga_linea[
                    (carga_linea['L'] == l) &
                    (carga_linea['T'] == t)
                ]
                if not CL_rows.empty:
                    CL=CL_rows.iloc[0]['Value']

                HE = None
                HE_rows = horas_extras[
                    (horas_extras['L'] == l) &
                    (horas_extras['T'] == t)
                ]
                if not HE_rows.empty:
                    HE=HE_rows.iloc[0]['Value']

                capL = None
                capL_rows = capacidad_linea[
                    (capacidad_linea['L'] == l) &
                    (capacidad_linea['T'] == t)
                ]
                if not capL_rows.empty:
                    capL=capL_rows.iloc[0]['Value']

                Utilizacion = ((CL or 0)) / capL

                if CL:
                    VL = CP / CL
                    Ociosidad_horas = capL - CL if (CL is not None) and (capL - CL > 0) else 0
                    Ociosidad_sacos = Ociosidad_horas * VL if (Ociosidad_horas and VL) else 0
                else:
                    VL = None
                    Ociosidad_sacos = 0
            
                utilizacion_lineas.append({
                    'Planta': f,
                    'Linea': l,
                    'Mes': t,
                    'Sacos producidos [miles]' : round(CP,2) if CP is not None else None,
                    'Velocidad promedio línea [miles sacos/hora]': round(VL,6) if VL is not None else None,
                    'Carga línea [horas]': round(CL, 2) if CL is not None else None,
                    'Capacidad Línea [horas]': capL,
                    'Horas extras [horas]': HE,
                    'Utilización [%]': round(Utilizacion * 100, 2) if (Utilizacion != 0) else None,
                    'Ociosidad [miles de sacos]': round(Ociosidad_sacos,2) if (Ociosidad_sacos != 0) else None
                    })
    
    end_time3 = time.time()  # End timer
    elapsed_time = end_time3 - end_time2  # Time in seconds

    #print(f"Utilizacion_Lineas: {elapsed_time:.2f}")

    ####### abastecimiento sheet ###########################
    abastecimiento_data = []
    #vars
    cant_abastecida = var_dataFrames['CANT_ABASTECIDA_MP'] 
    #pars
    factor_conversion = par_dataFrames['factor_conversion'] 
    factor_conversion_dict = {(row['MP'], row['SKU']): row['Value'] for _, row in factor_conversion.iterrows()}
                
    # # # Iterate over rows in cant_abastecida DataFrame where Value is non-zero
    for _, row in cant_abastecida[cant_abastecida['Value'] != 0].iterrows():
        mp, p, f, t, value = row['MP'], row['P'], row['F'], row['T'], row['Value']
        # Find associated SKUs via model.MP_SKU
        remanente = value
        for sku in model.SKU:
            if (mp, sku) in model.MP_SKU:
                # Get factor_conversion and CANT_PRODUCIDA_SKU for each relevant (l, sku, t)
                for l in model.L:
                    if (f, l) in model.F_L:
                        # Filter cant_producida for the specific (l, sku, t)
                        prod_subset = cant_producida[
                            (cant_producida['L'] == l) & 
                            (cant_producida['SKU'] == sku) & 
                            (cant_producida['T'] == t)
                        ]
                        # Only proceed if there is a non-zero CANT_PRODUCIDA_SKU
                        if not prod_subset.empty and prod_subset['Value'].iloc[0] != 0:
                            prod_value = prod_subset['Value'].iloc[0]
                            
                            # Filter factor_conversion for the specific (mp, sku)
                            conv_value = factor_conversion_dict.get((mp, sku), 0)

                            #conv_value = round(conv_value,1)
                            
                            convertido = prod_value * conv_value / 1000
                            remanente = remanente - convertido

                            MP_rows = df_materia_prima[(df_materia_prima['COD_MP_CORTO']==mp)]
                            descripcion_MP = MP_rows.iloc[0]['DESCRIPCION'] if not MP_rows.empty else ''

                            # Append the data to the list
                            abastecimiento_data.append({
                                'Materia Prima': mp,
                                'Descripción MP': descripcion_MP,
                                'Proveedor': p,
                                'Fábrica': f,
                                'Periodo': t,
                                'Cantidad Abastecida [Toneladas] (CA)': round(value,6),
                                'SKU asociado': sku,
                                'Factor de Conversion [gramos/saco] (FC)': conv_value,
                                'Produccion [miles de sacos] (P)': round(prod_value,6),
                                'Consumo en toneladas (C) [P * FC / 1000]': round(convertido,6),
                                "Balance  [CA - C]": round(remanente,6)
                            })

    ####### DESAGREGACIÓN DE abastecimiento_data ###########################
    
    # NUEVO: Crear mapeo para desagregar COD_MP_CORTO a COD_MP individuales
    def crear_mapeo_desagregacion():
        """
        Crea un mapeo que permite desagregar datos de COD_MP_CORTO a COD_MP individuales
        usando las proporciones basadas en factor_conversion
        """
        mapeo_desagregacion = {}
        
        # Agrupar por COD_MP_CORTO y COD_SKU_SIN_V para obtener todos los COD_MP asociados
        for _, row in df_composicion_sku_mp.iterrows():
            cod_sku = row['COD_SKU_SIN_V']
            cod_mp = row['COD_MP']
            cod_mp_corto = row['COD_MP_CORTO']
            factor_individual = row['FACTOR_CONVERSION']
            capa = row['CAPA']
            
            key = (cod_mp_corto, cod_sku)
            
            if key not in mapeo_desagregacion:
                mapeo_desagregacion[key] = []
            
            mapeo_desagregacion[key].append({
                'COD_MP': cod_mp,
                'FACTOR_CONVERSION_INDIVIDUAL': factor_individual,
                'CAPA': capa
            })
        
        # Calcular proporciones para cada grupo
        for key in mapeo_desagregacion:
            cod_mp_corto, cod_sku = key
            
            # Obtener factor_conversion_modelo total para este COD_MP_CORTO y SKU
            factor_total_modelo = factor_conversion_modelo.get((cod_mp_corto, cod_sku), 0)
            
            # Calcular proporción para cada COD_MP individual
            for item in mapeo_desagregacion[key]:
                if factor_total_modelo > 0:
                    item['PROPORCION'] = item['FACTOR_CONVERSION_INDIVIDUAL'] / factor_total_modelo
                else:
                    item['PROPORCION'] = 0
        
        return mapeo_desagregacion

    # Crear mapeo de desagregación
    mapeo_desagregacion = crear_mapeo_desagregacion()
    
    # NUEVO: Desagregar abastecimiento_data
    abastecimiento_data_detallado = []
    
    for item in abastecimiento_data:
        mp_corto = item['Materia Prima']
        sku = item['SKU asociado']
        
        # Buscar desagregación para este MP_CORTO y SKU
        desagregacion_items = mapeo_desagregacion.get((mp_corto, sku), [])
        
        if not desagregacion_items:
            # Sin desagregación disponible: mantener registro original con información adicional
            item_modificado = item.copy()
            item_modificado['Materia Prima Corta'] = mp_corto
            item_modificado['Materia Prima Completa'] = mp_corto  # Mismo valor
            item_modificado['Capa'] = 'N/A'
            item_modificado['Proporción'] = 1.0
            abastecimiento_data_detallado.append(item_modificado)
        else:
            # Con desagregación: crear registros por cada COD_MP individual
            for detalle in desagregacion_items:
                cod_mp_largo = detalle['COD_MP']
                factor_individual = detalle['FACTOR_CONVERSION_INDIVIDUAL']
                proporcion = detalle['PROPORCION']
                capa = detalle['CAPA']
                
                # Crear nuevo registro con valores desagregados
                item_desagregado = {
                    'Materia Prima Corta': mp_corto,  # COD_MP_CORTO original
                    'Materia Prima Completa': cod_mp_largo,  # COD_MP completo
                    'Capa': capa,  # MP1, MP2, MP3, MP4
                    'Descripción MP': item['Descripción MP'],
                    'Proveedor': item['Proveedor'],
                    'Fábrica': item['Fábrica'],
                    'Periodo': item['Periodo'],
                    'Cantidad Abastecida (CA)': round(item['Cantidad Abastecida [Toneladas] (CA)'] * proporcion, 2),
                    'SKU asociado': sku,
                    'Factor de Conversion (FC)': factor_individual,
                    'Produccion (P)': round(item['Produccion [miles de sacos] (P)'] * proporcion, 2),
                    'Consumo (C) [P * FC]': round(item['Produccion [miles de sacos] (P)'] * proporcion * factor_individual, 2),
                    'Balance [CA - C]': round(
                        (item['Cantidad Abastecida [Toneladas] (CA)'] * proporcion) - 
                        (item['Produccion [miles de sacos] (P)'] * proporcion * factor_individual), 2
                    ),
                    'Proporción': proporcion
                }
                
                abastecimiento_data_detallado.append(item_desagregado)

    end_time4 = time.time()  # End timer
    elapsed_time = end_time4 - end_time3  # Time in seconds

    #print(f"Abastecimiento: {elapsed_time:.2f}")

    ####### costos por línea sheet ###########################
    costo_lineas = []
    costo_plantas = []

    for f in model.F:
        for t in model.T:
            CAbast = sum(model.costo_abastecimiento[mp, p, f] * model.CANT_ABASTECIDA_MP[mp, p, f, t].value for mp in model.MP for p in model.P if(mp, p, f) in model.MP_P_F)
            
            CDistr = sum(model.costo_distribucion[c, f] * model.CANT_ENTREGADA_SKU[f, sku, t].value  * 1000
                         for c in model.C for sku in model.SKU if (sku, t, f, c) in model.SKU_T_F_C if (f, sku, t) in model.F_SKU_T)
        
            #CInv = sum(model.INVENTARIO_SKU[f,sku,t] for (sku) in model.SKU)
            CLT = 0 #acumulador del costo de las lineas
            for f_l, l in model.F_L:  # Iterate over F_L directly
                if f_l == f:  # Match the current factory
                    CFL = model.costo_fijo_lineas[l] 
                    UL = model.uso_linea[l, t].value
                    CMO = CFL * UL  # costo mano de obra
                    boolean_UL = bool(UL)
                    HE = model.HORAS_EXTRAS[l,t].value
                    CHE = model.costo_hora_extra[l] * HE
                    CProd=sum(model.CANT_PRODUCIDA_SKU[l, sku, t].value * model.costo_produccion[sku] for sku in model.SKU if (l,sku) in model.L_SKU) #costo de producción
                    CT = CMO+CHE+CProd
                    CLT = CLT + CT 
                    costo_lineas.append({
                        'Planta': f,
                        'Linea': l,
                        'Costo fijo mano de obra [USD/mes]': CFL,
                        'Mes': t,
                        'Línea utilizada': boolean_UL,
                        'Costo variable de produccion': CProd,
                        'Horas Extra': HE,
                        'Costo Horas Extras': CHE,
                        'Costo Total de la línea': CT
                        })
                    
            costo_plantas.append({
                'Planta': f,
                'Mes': t,
                'Costo Abastecimiento': round(CAbast,1),
                #'Costo Inventario': round(CInv,1),
                'Costo Producción': round(CLT,1),
                'Costo Distribución': round(CDistr,1),
                'Costo Total': round(CAbast+CDistr+CLT,1)
            })
            
    end_time5 = time.time()  # End timer
    elapsed_time = end_time5 - end_time4  # Time in seconds

    #print(f"Costos: {elapsed_time:.2f}")


    ####### costos unitarios por sku sheet ###########################

    # Transformamos los costos de abastecimiento a dict
    df_abast = pd.DataFrame(abastecimiento_data)

    costo_abast_dict = {(mp, p, f): model.costo_abastecimiento[mp, p, f]
                        for mp, p, f in model.MP_P_F}


    # -------------------------------
    # Inicializamos diccionarios
    # -------------------------------
    costo_abast_sku = {}
    costo_prod_sku = {}
    costo_dist_sku = {}
    planta_sku = {}

    # Transformamos los costos de abastecimiento a dict para acceso rápido
    costo_abast_dict = {(mp, p, f): model.costo_abastecimiento[mp, p, f]
                        for mp, p, f in model.MP_P_F}

    # -------------------------------
    # Loop por cada SKU
    # -------------------------------
    for (sku,c) in model.SKU_C:
        costo_total_abast = 0.0
        costo_total_prod = 0.0
        periodos_count = 0
        planta_asignada = None  # variable temporal

        for (s, t_d) in model.SKU_T_completo:
            if s != sku:
                continue

            for (f,l) in model.F_L:
                for t_p in model.T:
                    key_asig = (sku, t_d, l, t_p)
                    if key_asig in model.SKU_T_L_T and model.asignacion_linea[key_asig].value > 0.5:
                        # Guardar planta si aún no la tenemos
                        if planta_asignada is None:
                            planta_asignada = f
                        # -----------------------
                        # Costo de abastecimiento
                        # -----------------------
                        df_sku_f = df_abast[(df_abast['SKU asociado'] == sku) & 
                                                    (df_abast['Fábrica'] == f)]
                        for _, row in df_sku_f.iterrows():
                            mp = row['Materia Prima']
                            p = row['Proveedor']
                            fc = row['Factor de Conversion [gramos/saco] (FC)']
                            costo_unit = costo_abast_dict.get((mp, p, f), 0)
                            costo_total_abast += fc * costo_unit / 1_000_000

                        # -----------------------
                        # Costo de producción
                        # -----------------------
                        total_prod_linea = sum(
                            model.CANT_PRODUCIDA_SKU[l, sku2, t_p].value or 0
                            for sku2 in model.SKU if (l, sku2) in model.L_SKU
                        )
                        if total_prod_linea > 0:
                            costo_total_prod += model.costo_fijo_lineas[l] / (total_prod_linea * 1000)

                        # -----------------------
                        # Costo de distribución
                        # -----------------------
                        costo_dist_unitario = model.costo_distribucion[c, f]
                        
            periodos_count += 1

        # -----------------------
        # Guardar resultados por SKU
        # -----------------------
        planta_sku[sku] = planta_asignada
        costo_abast_sku[sku] = costo_total_abast / max(periodos_count, 1)
        costo_prod_sku[sku] = costo_total_prod / max(periodos_count, 1)
        costo_dist_sku[sku] = costo_dist_unitario  # ya es USD/SC unitario

    # -------------------------------
    # TABLA FINAL
    # -------------------------------
    df_final = pd.DataFrame({
        "SKU": list(costo_abast_sku.keys()),
        "Planta": [planta_sku[sku] for sku in costo_abast_sku],
        "Costo unitario abastecimiento (USD/SC)": [costo_abast_sku[sku] for sku in costo_abast_sku],
        "Costo unitario produccion (USD/SC)": [costo_prod_sku[sku] for sku in costo_abast_sku],
        "Costo unitario distribucion (USD/SC)": [costo_dist_sku[sku] for sku in costo_abast_sku],
        "Costo unitario del SKU (USD/SC)": [
        costo_abast_sku[sku] + costo_prod_sku[sku] + costo_dist_sku[sku] 
        for sku in costo_abast_sku
    ]
    })




    # Opcional: Convertir a DataFrame
    asignacion_sku_df = pd.DataFrame(asignacion_sku)
    utilizacion_lineas_df = pd.DataFrame(utilizacion_lineas)
    abastecimiento_df = pd.DataFrame(abastecimiento_data)
    abastecimiento_detallado_df = pd.DataFrame(abastecimiento_data_detallado)
    costo_lineas_df = pd.DataFrame(costo_lineas)
    costo_plantas_df = pd.DataFrame(costo_plantas)
    df_costo_sku_mes = pd.DataFrame(df_final)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    # results_dir = os.path.join(root_dir, f"./Corridas/{nombre_corrida}/Resultados", scenario_name) 
    # results_dir_2 = os.path.join(root_dir, f"./Corridas/{nombre_corrida}/Resultados", "Tablas_consolidadas.xlsx") 
    results_dir = os.path.join(f"./Corridas/{nombre_corrida}/Resultados", scenario_name) 
    results_dir_2 = os.path.join(f"./Corridas/{nombre_corrida}/Resultados", "Tablas_consolidadas.xlsx") 

    with pd.ExcelWriter(results_dir, engine="xlsxwriter") as writer:


        for idx, set in enumerate(set_dataFrames):
            set_dataFrames[set].to_excel(writer, index=False, sheet_name=f"{set}")
            worksheet = writer.sheets[f"{set}"]
            worksheet.set_tab_color('#ADD8E6')

        for idx, par in enumerate(par_dataFrames):
            par_dataFrames[par].to_excel(writer, index=False, sheet_name=f"{par}")
            worksheet = writer.sheets[f"{par}"]
            worksheet.set_tab_color('#C6EFCE')

        for idx, var in enumerate(var_dataFrames):
            var_dataFrames[var].to_excel(writer, index=False, sheet_name=f"{var}")
            worksheet = writer.sheets[f"{var}"]
            worksheet.set_tab_color('#FFEB9C')


    with pd.ExcelWriter(results_dir_2, engine="xlsxwriter") as writer:
        asignacion_sku_df.to_excel(writer, sheet_name='Balance_Inventario', index=False)
        utilizacion_lineas_df.to_excel(writer, sheet_name='Utilizacion_Lineas', index=False)
        abastecimiento_df.to_excel(writer, sheet_name='Abastecimiento', index=False)
        abastecimiento_detallado_df.to_excel(writer, sheet_name='Abastecimiento_Detallado', index=False)
        costo_lineas_df.to_excel(writer, sheet_name='Costo_Lineas', index=False)
        costo_plantas_df.to_excel(writer, sheet_name='Costo_Plantas', index=False)
        df_costo_sku_mes.to_excel(writer, sheet_name='Costo_Unitario_SKU', index=False)
        
        # Obtener el workbook y la worksheet de Costo_Plantas
        workbook = writer.book
        worksheet_CP = writer.sheets['Costo_Plantas']
        worksheet_L = writer.sheets['Costo_Lineas']

        
        # Definir formato monetario
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        
        # Aplicar formato a las columnas de costos (asumiendo que son las columnas 2 a 5: 'Costo Abastecimiento', 'Costo Producción', 'Costo Distribución', 'Costo Total')
        worksheet_CP.set_column('C:F', None, money_format)
        worksheet_L.set_column('C:C', None, money_format)
        worksheet_L.set_column('F:F', None, money_format)
        worksheet_L.set_column('H:I', None, money_format)


    end_time6 = time.time()  # End timer
    elapsed_time = end_time6 - end_time5   # Time in seconds

    #print(f"Construcción y Escritura de reportes: {elapsed_time:.2f}")