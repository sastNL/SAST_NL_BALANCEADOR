# %%
from re import L
import pyomo.environ as pyo
from pyomo.environ import *
import gc
gc.collect()
import pickle
from pyomo.common.timing import report_timing

def modelo_SC(path_pickle, nombre_corrida: str, regla_asignacion = 'demanda_interna', aplicar_aranceles = True, max_horas_extra = 10, gap = 0.1, tiempo_computo = 1000):
    report_timing()
    
    # Cargar inputs desde pickle
    with open(path_pickle, 'rb') as f:
        inputs_modelo = pickle.load(f)

    # Armado del modelo
    model = pyo.ConcreteModel()
    
    # Conjuntos Unidimensionales
    model.T = pyo.Set(initialize=inputs_modelo['set_meses'])
    model.T0 = pyo.Set(initialize=inputs_modelo['set_mes_inicial'])
    model.MP = pyo.Set(initialize=inputs_modelo['set_materias_primas'])
    model.P = pyo.Set(initialize = inputs_modelo['set_proveedores'])
    model.F = pyo.Set(initialize=inputs_modelo['set_fabricas'])
    model.L = pyo.Set(initialize=inputs_modelo['set_lineas'])
    model.SKU = pyo.Set(initialize=inputs_modelo['set_sku'])
    model.C = pyo.Set(initialize=inputs_modelo['set_clientes'])
    
    # Conjuntos Multidimensionales
    model.SKU_T = pyo.Set(within=model.SKU * model.T, initialize=inputs_modelo['set_sku_meses'], dimen=2)
    model.SKU_T_1 = pyo.Set(within=model.SKU * model.T, initialize=inputs_modelo['set_sku_meses1'], dimen=2)
    model.SKU_T_completo = pyo.Set(within=model.SKU * model.T, initialize=inputs_modelo['set_sku_meses_completo'], dimen=2)
    model.MP_P = pyo.Set(within=model.MP * model.P, initialize=inputs_modelo['set_materias_primas_proveedores'], dimen=2)
    model.MP_F = pyo.Set(within=model.MP * model.F, initialize=inputs_modelo['set_materias_primas_fabricas'], dimen=2)
    model.MP_P_F = pyo.Set(within=model.MP * model.P * model.F, initialize=inputs_modelo['set_materias_primas_proveedores_fabricas'], dimen=3)
    model.P_F = pyo.Set(within=model.P * model.F, initialize=inputs_modelo['set_proveedores_fabricas'], dimen=2)
    model.F_L = pyo.Set(within=model.F * model.L, initialize=inputs_modelo['set_fabricas_lineas'], dimen=2)
    model.F_L_SKU = pyo.Set(within=model.F * model.L * model.SKU, initialize=inputs_modelo['set_fabricas_lineas_sku'], dimen=3)
    model.L_SKU = pyo.Set(within=model.L * model.SKU, initialize=inputs_modelo['set_lineas_sku'], dimen=2)
    model.MP_SKU = pyo.Set(within=model.MP * model.SKU, initialize=inputs_modelo['set_materias_primas_sku'], dimen=2)
    model.F_C = pyo.Set(within=model.F * model.C, initialize=inputs_modelo['set_fabricas_clientes'], dimen=2)
    model.SKU_C = pyo.Set(within=model.SKU * model.C, initialize=inputs_modelo['set_sku_cliente'], dimen=2)
    model.F_SKU = pyo.Set(within=model.F * model.SKU, initialize=inputs_modelo['set_fabricas_sku'], dimen=2)
    model.SKU_T_F_C = pyo.Set(within=model.SKU * model.T * model.F * model.C, initialize=inputs_modelo['set_sku_mes_planta_cliente'], dimen=4)
    model.L_SKU_T_F_C = pyo.Set(within=model.L * model.SKU * model.T * model.F * model.C, initialize=inputs_modelo['set_linea_sku_mes_planta_cliente'], dimen=5)
    model.F_SKU_T = pyo.Set(within=model.F * model.SKU * model.T, initialize=inputs_modelo['set_fabrica_sku_mes'], dimen=3)
    model.F_SKU_T_2 = pyo.Set(within=model.F * model.SKU * model.T, initialize=inputs_modelo['set_fabrica_sku_mes2'], dimen=3)
    model.SKU_T_L = pyo.Set(within=model.SKU * model.T * model.L, initialize=inputs_modelo['set_sku_mes_linea'], dimen=3)
    model.SKU_T_L_T = pyo.Set(within=model.SKU_T_L * model.T, initialize=inputs_modelo['set_sku_mes_linea_mes'], dimen=4)
    model.dem_int_F_SKU = pyo.Set(within=model.F * model.SKU, initialize=inputs_modelo['set_demanda_interna'], dimen=2)
    model.dem_int_SKU = pyo.Set(within=model.SKU, initialize=inputs_modelo['set_sku_dem_int'], dimen=1)
    # model.SKU_T_L_T_FIX = pyo.Set(within=model.SKU_T_L * model.T, initialize=inputs_modelo['set_decisiones_fijas'], dimen=4)
    
    # Parametros
    model.demanda = pyo.Param(model.SKU,  model.T, within=pyo.NonNegativeReals, initialize=inputs_modelo['demanda'])
    model.inventario_inicial_sku_fabrica = pyo.Param(model.F_SKU, model.T0, within=pyo.NonNegativeReals, initialize=inputs_modelo['inventario_inicial_sku_fabrica'])
    model.SS_faltante = pyo.Param(model.SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['SS_faltante'])
    model.ordenes_abiertas = pyo.Param(model.SKU, model.T, within=pyo.NonNegativeReals, initialize=inputs_modelo['ordenes_abiertas'])
    #model.stock_seguridad_minimo = pyo.Param(model.C, model.SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['stock_seguridad_minimo'])
    #model.stock_seguridad_maximo = pyo.Param(model.C, model.SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['stock_seguridad_maximo'])
    model.lead_time_entrega = pyo.Param(model.F_C, within=pyo.NonNegativeReals, initialize=inputs_modelo['lead_time_entrega'])
    model.turnos_disponibles = pyo.Param(model.L, model.T, within=pyo.NonNegativeReals, initialize=inputs_modelo['turnos_disponibles'])
    model.capacidad_linea = pyo.Param(model.L, model.T, within=pyo.NonNegativeReals, initialize=inputs_modelo['capacidad_linea'])
    model.velocidad_produccion = pyo.Param(model.L_SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['velocidad_produccion'])
    model.factor_conversion = pyo.Param(model.MP_SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['factor_conversion'])
    model.max_plantas_asignadas = 1
    model.aranceles = pyo.Param(model.F_SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['arancel_sku_planta'])
    #model.inventario_minimo_sku_fabrica = pyo.Param(model.SKU, model.F, within=pyo.NonNegativeReals, initialize=inputs_modelo['inventario_minimo_sku_fabrica'])
    #model.inventario_maximo_sku_fabrica = pyo.Param(model.SKU, model.F, within=pyo.NonNegativeReals, initialize=inputs_modelo['inventario_maximo_sku_fabrica'])
    model.costo_produccion = pyo.Param(model.SKU, within=pyo.NonNegativeReals, initialize=inputs_modelo['costo_produccion'])
    model.costo_fijo_lineas = pyo.Param(model.L, within=pyo.NonNegativeReals, initialize=inputs_modelo['costos_fijos_lineas'])
    model.costo_abastecimiento = pyo.Param(model.MP_P_F,within=pyo.NonNegativeReals, initialize=inputs_modelo['costo_abastecimiento'])
    model.costo_distribucion = pyo.Param(model.C, model.F, within=pyo.NonNegativeReals, initialize=inputs_modelo['costo_distribucion'])
    # model.costo_hora_extra = pyo.Param(within=pyo.NonNegativeReals, initialize=1e8)
    model.costo_hora_extra = pyo.Param(model.L, within=pyo.NonNegativeReals, initialize=inputs_modelo['costo_hora_extra'])
    model.max_horas_extra = pyo.Param(within=pyo.NonNegativeReals, initialize=max_horas_extra)   
    
    ##############################################
    # VARIABLES
    ##############################################
    
    ##############################################
    # Variables Binarias
    ##############################################

    # Produccion

    model.asignacion_fabrica = pyo.Var(model.F_SKU_T, within=pyo.Binary)
    # 1 si la demanda del sku para el período t es fabricada en la planta f

    #model.asignacion_linea = pyo.Var(model.SKU_T_L, model.T, within=pyo.Binary)
    model.asignacion_linea = pyo.Var(model.SKU_T_L_T, within=pyo.Binary)
    # 1 si la demanda del sku solicitada para el período t es producida en la línea l en el período t'    

    model.uso_linea = pyo.Var(model.L, model.T, within=pyo.Binary)
    # 1 si es usada la línea l en el período t

    ##############################################
    # Variables Continuas
    ##############################################

    # Abastecimiento

    model.CANT_ABASTECIDA_MP = pyo.Var(model.MP_P_F, model.T, within=pyo.NonNegativeReals)
    #cantidad de materia prima mp abastecida por el proveedor p a la fábrica f en el período t (TON/MES)

    model.COSTO_ABASTECIMIENTO_MENSUAL = pyo.Var(model.T, within=pyo.NonNegativeReals)
    #costo mensual de abastecimiento
    
    ##############################################
    # Produccion
    model.CANT_PRODUCIDA_SKU = pyo.Var(model.L_SKU, model.T, within=pyo.NonNegativeReals)
    # cantidad de producto sku fabricado en la línea l en el período t (MSC/MES)

    model.INVENTARIO_SKU = pyo.Var(model.F_SKU, model.T, within=pyo.NonNegativeReals)
    # inventario de producto sku en la fábrica f en el período t (MSC/MES)

    model.COSTO_MANO_OBRA_LINEAS = pyo.Var(model.T, within=pyo.NonNegativeReals)
    # costo de mano de obra en la línea l en el período t

    model.COSTO_PRODUCCION_MENSUAL = pyo.Var(model.T, within=pyo.NonNegativeReals)
    #costo mensual de produccion
     
    model.COSTO_INVENTARIO = pyo.Var(model.T,within=pyo.NonNegativeReals)

    model.CARGA_LINEA = pyo.Var(model.L, model.T, within=pyo.NonNegativeReals)

    model.FO1_Var = pyo.Var(within=pyo.NonNegativeReals)
    
    model.COSTO_INVENTARIO = pyo.Var(model.T,within=pyo.NonNegativeReals)
    #costo mensual de inventario

    model.HORAS_EXTRAS = pyo.Var(model.L, model.T, within=pyo.NonNegativeReals)

    model.COSTO_HORAS_EXTRAS = pyo.Var(model.T, within=pyo.NonNegativeReals)

    ##############################################
    # Distribucion
    
    model.CANT_ENTREGADA_SKU = pyo.Var(model.F_SKU_T, within=pyo.NonNegativeReals)
    # cantidad de producto sku a enviar desde la fábrica f en el período t (MSC/MES)

    model.COSTO_DISTRIBUCION_MENSUAL = pyo.Var(model.T, within=pyo.NonNegativeReals)
    #costo mensual de distribucion
    
    ##############################################
    #FIXEOS
    # for key in model.SKU_T_L_T:
    #     if key in model.SKU_T_L_T_FIX:
    #         model.asignacion_linea[key].fix(1)
    #     else:
    #         model.asignacion_linea[key].fix(0)
    
    ##############################################

    ##############################################
    # Restricciones Abastecimiento
    ##############################################

    @model.Constraint(model.MP_F, model.T, name="balance_masa_abastecimiento") # CANT_ABASTECIDA_MP TON/MES 
    def balance_masa_abastecimiento(model, mp, f, t):
        return  sum(model.CANT_ABASTECIDA_MP[mp, p, f, t] for p in model.P if (mp, p, f) in model.MP_P_F) >= \
                   (sum(model.factor_conversion[mp, sku] * model.CANT_PRODUCIDA_SKU[l, sku, t] for (l, sku) in model.L_SKU if (f,l,sku) in model.F_L_SKU and (mp, sku) in model.MP_SKU) / 1000)
                    # /1000 porque CANT_PRODUCIDA_SKU está en miles, factor_conversion en gramos y CANT_ABASTECIDA_MP en toneladas
    
                  
    ##############################################
    # Restricciones Produccion
    ##############################################

    #R1: La demanda del producto sku para el período t debe ser asignada a una fábrica
    @model.Constraint(model.SKU_T_completo, name="asignacion_ordenes_fabrica")
    def asignacion_ordenes_fabrica(model, sku, t):
        if regla_asignacion=='demanda_interna' and sku in model.dem_int_SKU: #si el sku es de demanda interna, se asigna a fábricas del país perteneciente
            return sum(model.asignacion_fabrica[f,sku,t] for f in model.F if (f,sku) in model.dem_int_F_SKU) == 1 
        else:
            return sum(model.asignacion_fabrica[f, sku, t] for f in model.F if (f, sku) in model.F_SKU) == 1
    
    #R2: Asignar los pedidos del sku siempre a la misma planta
    @model.Constraint(model.F_SKU_T_2, name="asignacion_ordenes_fabrica2")
    def asignacion_ordenes_fabrica2(model, f, sku, t):
        return model.asignacion_fabrica[f, sku, t] <= sum(model.asignacion_fabrica[f, sku, tt] for tt in model.T if tt > t and (sku, tt) in model.SKU_T)
         
    #R3: Si se usa la linea l en el peridodo t, se debe asignar algun sku en dicha linea y periodo
    @model.Constraint(model.L, model.T, name="uso_linea1")
    def uso_linea1(model, l, t):
        return model.uso_linea[l, t] <= sum(model.asignacion_linea[sku, tt, l, t] 
                                            for sku in model.SKU 
                                            for tt in model.T if tt <= t
                                            if (sku, tt, l, t) in model.SKU_T_L_T) 
        
    #R4: si se asigna sku en l, entonces se debe activar uso_linea
    @model.Constraint(model.SKU_T_L_T, name="uso_linea2")
    def uso_linea2(model, sku, tt, l, t):
        return model.uso_linea[l, t] >= model.asignacion_linea[sku, tt, l, t] 
    
    #R5: La demanda del producto sku para el período t debe ser asignada a una línea y período
    @model.Constraint(model.SKU_T_F_C, name="asignacion_ordenes_lineas") 
    def asignacion_ordenes_lineas(model, sku, t, f, c):
        return sum(model.asignacion_linea[sku, t, l, tt] 
                   for l in model.L 
                   for tt in model.T \
                   if tt<=t-model.lead_time_entrega[f, c] and 
                   (f,l) in model.F_L and 
                   (l, sku) in model.L_SKU)   \
                == model.asignacion_fabrica[f, sku, t]
        
    #R6: La cantidad producida de cada sku en la linea l y periodo t debe ser mayor o igual a la demanda asignada a producir en dicha linea y periodo
    @model.Constraint(model.L_SKU_T_F_C, name="cant_prod_minima")
    def cant_prod_minima(model, l, sku, tt, f, c): 
        if tt==1:
            return model.CANT_PRODUCIDA_SKU[l, sku, tt] >= \
        sum((model.demanda[sku, t] + model.SS_faltante[sku] + model.ordenes_abiertas[sku, t] 
             - model.inventario_inicial_sku_fabrica[f,sku,t]) * model.asignacion_linea[sku, t, l, tt] for t in model.T  \
            if tt<=t-model.lead_time_entrega[f, c] and (sku,t) in model.SKU_T_1)
        else:
            return model.CANT_PRODUCIDA_SKU[l, sku, tt] >= \
        sum((model.demanda[sku, t] + model.ordenes_abiertas[sku, t]) * model.asignacion_linea[sku, t, l, tt] for t in model.T  \
                if tt<=t-model.lead_time_entrega[f, c] and (sku,t) in model.SKU_T)

    #R7: La cantidad producida en cada línea y periodo no debe excede la máxima producción posible
    @model.Constraint(model.L_SKU_T_F_C, name="cant_prod_maxima")
    def cant_prod_maxima(model, l, sku, tt, f, c):
        return model.CANT_PRODUCIDA_SKU[l, sku, tt] <=  \
    (sum(model.demanda[sku, t]+model.ordenes_abiertas[sku, t]+ (model.SS_faltante[sku] if t == 1 else 0) 
        for t in model.T if tt <= t and (sku, t) in model.SKU_T_completo))* \
    sum(model.asignacion_linea[sku, t, l, tt] 
        for t in model.T if tt <= t - model.lead_time_entrega[f, c] and (sku, t) in model.SKU_T_completo)

    #R8: Balance de masa (inventario_actual+producción=demanda+inventario_futuro+stock_seguridad)
    @model.Constraint(model.F_SKU, model.T) #están bien esos set, NO es F_SKU_T
    def balance_masa_produccion(model, f, sku, t):
        if t == 1:#model.T0:  
            return  model.inventario_inicial_sku_fabrica[f,sku,t] + sum(model.CANT_PRODUCIDA_SKU[l, sku, t] for l in model.L if (f,l) in model.F_L and (l,sku) in model.L_SKU) == \
                   model.INVENTARIO_SKU[f, sku, t] + (model.CANT_ENTREGADA_SKU[f, sku, t] if (f, sku, t) in model.F_SKU_T else 0)
        else:
            return model.INVENTARIO_SKU[f, sku, t-1] + sum(
                model.CANT_PRODUCIDA_SKU[l, sku, t] for l in model.L if (f,l) in model.F_L and (l,sku) in model.L_SKU) == \
                   model.INVENTARIO_SKU[f, sku, t] + (model.CANT_ENTREGADA_SKU[f, sku, t] if (f, sku, t) in model.F_SKU_T else 0)
        
    #R9: Cálculo de la utilización de cada línea
    @model.Constraint(model.L, model.T)
    def calculo_carga_linea(model, l, t):
        return model.CARGA_LINEA[l,t] == sum(model.CANT_PRODUCIDA_SKU[l, sku, t]/(model.velocidad_produccion[l,sku]/1000) for sku in model.SKU if (l, sku) in model.L_SKU)
    
    #R10: La cantidad de producto sku producido en la línea l en el período t debe satisfacer la capacidad de la línea l en el período t
    @model.Constraint(model.L, model.T)
    def capacidad_carga_linea(model, l, t):             
        return model.CARGA_LINEA[l,t] <= model.capacidad_linea[l, t] + model.HORAS_EXTRAS[l,t] #horas/mes
       
    @model.Constraint(model.L, model.T)
    def max_horas_extras(model,l,t):
        return model.HORAS_EXTRAS[l,t] <= model.max_horas_extra * model.capacidad_linea[l, t]
    

    ##############################################
    # Restricciones Distribución
    ##############################################
    
    #R1: 
    @model.Constraint(model.F_SKU_T)
    def balance_masa_distribucion(model, f, sku, t):
        if (sku, t) in model.SKU_T_1 and t==1:
            return model.CANT_ENTREGADA_SKU[f, sku, t] == (model.demanda[sku, t] + model.ordenes_abiertas[sku, t] + model.SS_faltante[sku])* model.asignacion_fabrica[f, sku, t]
        if (sku, t) in model.SKU_T and t>1:
            return model.CANT_ENTREGADA_SKU[f, sku, t] == (model.demanda[sku, t] + model.ordenes_abiertas[sku, t])* model.asignacion_fabrica[f, sku, t]
        else:
            return Constraint.Skip
        
    ##############################################
    # Costos
    ##############################################
    
    @model.Constraint(model.T)
    def ec_costo_abastecimiento(model, t):
        return model.COSTO_ABASTECIMIENTO_MENSUAL[t] == sum(model.costo_abastecimiento[mp, p, f] * model.CANT_ABASTECIDA_MP[mp, p, f, t] for (mp, p, f) in model.MP_P_F)

    @model.Constraint(model.T)
    def ec_costo_mano_obra_lineas(model, t):
        return model.COSTO_MANO_OBRA_LINEAS[t] == sum(model.costo_fijo_lineas[l]*model.uso_linea[l, t] 
             for l in model.L)

    if aplicar_aranceles:
        @model.Constraint(model.T)
        def ec_costo_produccion(model, t):
            return model.COSTO_PRODUCCION_MENSUAL[t] == sum((1+model.aranceles[f, sku])*model.costo_produccion[sku]*model.CANT_PRODUCIDA_SKU[l, sku, t] 
                for (f, l, sku) in model.F_L_SKU for t in model.T)
        #(1+model.aranceles[f, sku])*
        @model.Constraint(model.T)
        def ec_costo_distribucion(model, t):
            return model.COSTO_DISTRIBUCION_MENSUAL[t] == sum(
                (1 + model.aranceles[f, sku]) * model.costo_distribucion[c, f] * 
                model.CANT_ENTREGADA_SKU[f, sku, t] * 1000
                
                for (f, sku) in model.F_SKU
                for c in model.C
                if (f, sku, t) in model.F_SKU_T and (sku, c) in model.SKU_C
            )
    else:
        @model.Constraint(model.T)
        def ec_costo_produccion(model, t):
            return model.COSTO_PRODUCCION_MENSUAL[t] == sum(model.costo_produccion[sku]*model.CANT_PRODUCIDA_SKU[l, sku, t] 
                for (f, l, sku) in model.F_L_SKU for t in model.T)
        #(1+model.aranceles[f, sku])*
        @model.Constraint(model.T)
        def ec_costo_distribucion(model, t):
            return model.COSTO_DISTRIBUCION_MENSUAL[t] == sum(model.costo_distribucion[c, f] * 
                model.CANT_ENTREGADA_SKU[f, sku, t] * 1000
                
                for (f, sku) in model.F_SKU
                for c in model.C
                if (f, sku, t) in model.F_SKU_T and (sku, c) in model.SKU_C
            )
            
    @model.Constraint(model.T)
    def ec_costo_inventario(model, t):
        return model.COSTO_INVENTARIO[t] == sum(model.INVENTARIO_SKU[f,sku,t] 
             for (f,sku) in model.F_SKU)
    
    @model.Constraint(model.T)
    def ec_costo_horas_extras(model, t):
        return model.COSTO_HORAS_EXTRAS[t] == sum(model.HORAS_EXTRAS[l,t] * model.costo_hora_extra[l]
             for l in model.L)

    ##############################################
    # Funcion objetivo
    ##############################################
    @model.Constraint()
    def funcion_objetivo_primaria(model):                                                                      #model.COSTO_PRODUCCION_MENSUAL[t] +
        return model.FO1_Var == sum(model.COSTO_ABASTECIMIENTO_MENSUAL[t] + model.COSTO_MANO_OBRA_LINEAS[t] + model.COSTO_DISTRIBUCION_MENSUAL[t] + model.COSTO_INVENTARIO[t] + model.COSTO_HORAS_EXTRAS[t] for t in model.T)

    model.objetivo1 = pyo.Objective(expr=model.FO1_Var, sense=pyo.minimize)
     
    solver = pyo.SolverFactory('gurobi')
    solver.options['MIPGap'] = gap
    
    solver.options['TimeLimit'] = tiempo_computo #tiempo de computo en segundos

    # Definir el archivo de log
    MODEL2_LOG = f'./Corridas/{nombre_corrida}/Resultados/LOG_solucion.log'

    result = solver.solve(model, tee = True, logfile = MODEL2_LOG)
    #result = solver.solve(model, tee = True)

    MODEL2_LP = f'./Corridas/{nombre_corrida}/Resultados/LP_problema.lp'
    
    #**Generar el archivo LP** 

    model.symbolic_solver_labels = True  

    #Escribir el archivo LP
    with open(MODEL2_LP, "w") as f:
        from pyomo.repn.plugins.lp_writer import LPWriter
        writer = LPWriter()
        writer.write(model, f, symbolic_solver_labels=True)

    MODEL2_SOL = f'./Corridas/{nombre_corrida}/Resultados/LP_problema.sol'
    # Abrir el archivo de salida para escribir los resultados
    with open(MODEL2_SOL, "w") as f:
        for v in model.component_objects(pyo.Var, active=True):
            f.write(f"Variable {v}: \n")
            
            # Iterar sobre los índices de la variable
            for index in v:
                value = v[index].value
                if value is not None:
                    f.write(f"  {index} = {value}\n")
                else:
                    f.write(f"  {index} = No value assigned\n")
                    

    infeasible = False
    if result.solver.termination_condition == TerminationCondition.infeasible:
        infeasible = True
        
    return model, infeasible