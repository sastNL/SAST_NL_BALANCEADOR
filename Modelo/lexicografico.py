import pyomo.environ as pyo
from pyomo.environ import *
import copy

def balancear_lineas(model, porcentaje_degradacion, tiempo_computo = 100):

    # Crear copia profunda del model_copyo para no modificar el original
    model_copy = copy.deepcopy(model)
    
    ##############################################
    # Enfoque lexicográfico
    ##############################################
    
    obj1_value = pyo.value(model_copy.objetivo1) #tomo valor de la FO anterior
    
    model_copy.objetivo1.deactivate() #desactivo FO anterior

    # Incorporo FO anterior como constraint y la degrado
    @model_copy.Constraint()
    def degradacion(model_copy):
        return model_copy.FO1_Var <= ( 1 + (porcentaje_degradacion/100) ) * obj1_value


    model_copy.L_T = pyo.Set(within=model_copy.L * model_copy.T, initialize=lambda m: [
        (l, t) for l in m.L for t in m.T if m.capacidad_linea[l, t] > 0], dimen=2)

    # Defino y calculo CARGA_RELATIVA
    model_copy.CARGA_RELATIVA_LINEA = pyo.Var(model_copy.L_T, within=pyo.Reals)

    @model_copy.Constraint(model_copy.L_T)
    def carga_por_linea_rule(model_copy, l, t):       
        return model_copy.CARGA_RELATIVA_LINEA[l,t] >= ( model_copy.CARGA_LINEA[l,t] / model_copy.capacidad_linea[l,t] )
        
    model_copy.CARGA_POR_PLANTA = pyo.Var(model_copy.F, within=pyo.Reals)

    @model_copy.Constraint(model_copy.F_L, model_copy.L_T)
    def carga_maxima_por_planta_rule(model_copy, f,l1, l2, t):
        if l1==l2:
            return model_copy.CARGA_POR_PLANTA[f] >= model_copy.CARGA_RELATIVA_LINEA[l1,t]
        return pyo.Constraint.Skip

    #Nueva FO
    model_copy.FO2 = pyo.Objective(expr=sum(model_copy.CARGA_POR_PLANTA[f] for f in model_copy.F), sense=pyo.minimize)
    solver = pyo.SolverFactory('gurobi')
    # solver.options['FeasibilityTol'] = 0.001 
    solver.options['TimeLimit'] = tiempo_computo 
    solver.solve(model_copy, tee=True, warmstart=True)
                    
    return model_copy
    