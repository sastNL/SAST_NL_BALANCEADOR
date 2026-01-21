def calculo_kpis(model):

    # usd?
    costo_total = sum(model.COSTO_ABASTECIMIENTO_MENSUAL[t].value +
                       model.COSTO_MANO_OBRA_LINEAS[t].value +
                         model.COSTO_PRODUCCION_MENSUAL[t].value +
                           model.COSTO_DISTRIBUCION_MENSUAL[t].value +
                             model.COSTO_HORAS_EXTRAS[t].value for t in model.T)

    utilizacion_lineas = {}

    for l in model.L:
        ratios = []
        for t in model.T:
            if model.capacidad_linea[l,t]>0:
                CL = model.CARGA_LINEA[l,t].value          
                CapL = model.capacidad_linea[l,t]
                ratios.append(CL / CapL)

        utilizacion_lineas[l] = sum(ratios) / len(ratios)

    non_zero_skus = set(sku for f, sku, t in model.F_SKU_T if model.asignacion_fabrica[f, sku, t].value != 0)
    count_non_zero_skus = len(non_zero_skus)

    report_dict = {
        'Costo_Total': costo_total,
        'Utilizacion_promedio_lineas': utilizacion_lineas,
        'SKUs_Optimizados': count_non_zero_skus
    }

    # Initialize dictionaries for each line
    line_costs = {l: {
        'Costo fijo mano de obra [USD/mes]': 0,
        'Costo variable de produccion': 0,
        'Costo Horas Extras': 0,
        'Costo Total de la línea': 0
    } for l in model.L}

    # Calculate costs for each line, factory, and time period
    for f in model.F:
        for t in model.T:
            for f_l, l in model.F_L:  # Iterate over F_L directly
                if f_l == f:  # Match the current factory
                    CFL = model.costo_fijo_lineas[l]  # Fixed labor cost
                    UL = model.uso_linea[l, t].value
                    CMO = CFL * UL  # Labor cost based on usage
                    HE = model.HORAS_EXTRAS[l, t].value
                    CHE = model.costo_hora_extra[l] * HE  # Overtime cost
                    CProd = sum(model.CANT_PRODUCIDA_SKU[l, sku, t].value * model.costo_produccion[sku] 
                                for sku in model.SKU if (l, sku) in model.L_SKU)  # Production cost
                    # CT = CMO + CHE + CProd  # Total line cost
                    CT = CMO + CProd  # Total line cost

                    # Aggregate costs into the line's dictionary
                    line_costs[l]['Costo fijo mano de obra [USD/mes]'] += CMO
                    line_costs[l]['Costo variable de produccion'] += CProd
                    line_costs[l]['Costo Horas Extras'] += CHE
                    line_costs[l]['Costo Total de la línea'] += CT

    # Round values for cleaner output
    for l in line_costs:
        for key in line_costs[l]:
            line_costs[l][key] = round(line_costs[l][key], 1)

    return report_dict, line_costs