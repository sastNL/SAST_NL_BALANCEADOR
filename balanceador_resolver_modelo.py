import streamlit as st  
import time

from utils_asignacion.utils_asignacion_back.Modelo.modelo_SC import modelo_SC
from utils_asignacion.utils_asignacion_back.Modelo.lexicografico import balancear_lineas
from utils_asignacion.utils_asignacion_back.Postprocesamiento.postprocess import postprocess

if 'paso optimizacion listo' not in st.session_state: 
    st.session_state['paso optimizacion listo'] = False

if 'modelo resuelto' not in st.session_state:
    st.session_state['modelo resuelto'] = False

if 'nombre del escenario' not in st.session_state:  
    st.session_state['nombre del escenario'] = None

if 'paso parametrizacion listo' not in st.session_state: 
    st.session_state['paso parametrizacion listo'] = False
    
if 'modelo_infactible' not in st.session_state: 
    st.session_state['modelo_infactible'] = False

def Resolver_modelo():
    
    nombre_corrida = st.session_state['nombre del escenario']

    if st.session_state['paso parametrizacion listo'] == True:

        parametros = st.session_state['parametros']

        TabCostoGlobal, tabBalanceoLineas = st.tabs (['Costo global', 'Balanceo de líneas'])

        with TabCostoGlobal:

            col_1_1, col_1_2, col_1_3 = st.columns([2,5,1])

            with col_1_3: 
                st.markdown(f'**Escenario: {st.session_state["nombre del escenario"]}**')

            with col_1_1:
                resolver_modelo_boton =st.button("Resolver modelo", key = "boton resolver modelo", type = "primary")
                
                if resolver_modelo_boton:
                    with st.spinner("Resolviendo modelo..."):

                        time.sleep(1)
                        if st.session_state['permitir satisfacer demanda interna'] == True:
                            regla_asignacion = 'demanda_interna'
                        else:
                            regla_asignacion = False
                        modelo, infeasible = modelo_SC(f'Corridas/{nombre_corrida}/Preprocesamiento/datos_completos.pkl', nombre_corrida, regla_asignacion, parametros['considerar aranceles'], parametros['maximo horas extras']/100, parametros['GAP']/100, parametros['tiempo computo maximo'])
                        
                        st.session_state['modelo'] = modelo

                        if infeasible:
                            st.error("El modelo es infactible. Por favor, revise la parametrización y los reportes de errores.", icon="🚨")
                            st.session_state['modelo_infactible'] = True
                        
                        else:
                            if parametros['lexicografico'] == False:
                                st.session_state.kpi1, st.session_state.costos_lineas, st.session_state.fig_produccion_x_linea, st.session_state.fig_utilizacion_x_linea = postprocess(st.session_state['modelo'], 'soluciones_salida.xlsx', nombre_corrida, st.session_state['inicio_horizonte'])
                                st.session_state['paso optimizacion costo global listo'] = True
                                st.session_state['modelo resuelto'] = True
                                st.success("Modelo resuelto con éxito!", icon="✅")
                            else:
                                st.success("Modelo resuelto con éxito! Resuelva **Balanceo de Lineas**.", icon="✅")
                        

        with tabBalanceoLineas:
            
            
            if parametros['lexicografico'] == True:
                
                if st.session_state['modelo_infactible'] == True:
                    st.error("El modelo es infactible. No se puede proceder al balanceo de líneas.", icon="🚨")
                else: 
                    col_2_1, col_2_2, col_2_3 = st.columns([2,5,1])

                    with col_2_3: 
                        st.markdown(f'**Escenario: {st.session_state["nombre del escenario"]}**')

                    with col_2_1:
                        resolver_modelo_boton =st.button("Resolver modelo", key = "boton resolver modelo 2", type = "primary")
                        
                        if resolver_modelo_boton:
                            with st.spinner("Resolviendo modelo..."):
                                time.sleep(1)                           
                                modelo_1 = balancear_lineas(st.session_state['modelo'], parametros['porcentaje_degradacion'], tiempo_computo = parametros['tiempo computo maximo']) 
                                
                                st.session_state.kpi1, st.session_state.costos_lineas, st.session_state.fig_produccion_x_linea, st.session_state.fig_utilizacion_x_linea = postprocess(modelo_1, 'soluciones_salida.xlsx', nombre_corrida, st.session_state['inicio_horizonte'])
                                
                                st.success("Modelo resuelto con éxito!", icon="✅")
                                st.session_state['paso optimizacion balanceo de lineas listo'] = True
                                st.session_state['modelo resuelto'] = True
                                
            else:
                st.warning("Debe activar la opción de correr modelo lexicográfico en la parametrización para acceder a esta pestaña.", icon="⚠️")
        

    else: 
        st.warning("Primero debe parametrizar el problema.", icon="⚠️")
        st.session_state['paso optimizacion listo'] = False