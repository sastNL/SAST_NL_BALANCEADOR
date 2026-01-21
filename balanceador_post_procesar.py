import streamlit as st  
import os
import subprocess


if 'paso post-procesamiento listo' not in st.session_state:
    st.session_state['paso post-procesamiento listo'] = False

#Inicializamos st.session_state
variables = ['modelo resuelto', 'paso_optimizacion_costo_global_listo', 'paso_optimizacion_balanceo_de_lineas', 'cantidad_de_sku_sin_procesar', 'utilizacion_de_lineas', 'costo_total_de_la_solucion']
for variable in variables:
    if variable not in st.session_state:
        st.session_state[variable] = None


def Postprocesar():

    if st.session_state['modelo resuelto'] == True: 

        col1_1, col1_2, col1_3 = st.columns([2,5,1])

        with col1_3: 
            st.markdown(f'**Escenario: {st.session_state["nombre del escenario"]}**')

        with col1_1:
                if st.button("Abrir carpeta de post-process", type="primary", key="abrir carpeta post-procesamiento"):
                    carpeta_post = os.path.join("Corridas", st.session_state["nombre del escenario"], "Resultados")
                    if os.path.exists(carpeta_post):
                        # Abrir carpeta en el explorador de archivos de Windows
                        subprocess.Popen(f'explorer "{os.path.abspath(carpeta_post)}"')
                    else:
                        st.warning("La carpeta de post-process aún no existe.", icon="⚠️")

        st.markdown('**Resumen de métricas**')

        col2_1, col2_2, col2_3, col2_4 = st.columns([1,1,1,1])
        with col2_1:
                st.metric("Costo total de la solución (MUSD)", f"{(st.session_state.kpi1['Costo_Total']/1000000):.2f}", border=True)
        with col2_2:
                utilizacion_promedio = sum(st.session_state.kpi1['Utilizacion_promedio_lineas'].values()) / len(st.session_state.kpi1['Utilizacion_promedio_lineas'])
                st.metric("Utilización promedio de las líneas", f'{(utilizacion_promedio*100):.2f}%', border=True)
        with col2_3:
                st.metric("Cantidad de SKU procesados", st.session_state.kpi1['SKUs_Optimizados'], border=True)


        col3_1, col3_2, col3_3 = st.columns([1,1,1])
        with col3_1:
                st.markdown("**Costos por línea**")
        #with col3_3:
                lineas_s = list(set(st.session_state.costos_lineas.keys()))
                lineas  =st.selectbox("Seleccionar línea", lineas_s, key="filtro SKU")

        col4_1, col4_2, col4_3 = st.columns([1,1,1])
        with col4_1:
                st.metric("Costo mano de obra (USD)", st.session_state.costos_lineas[lineas]['Costo fijo mano de obra [USD/mes]'], border=True)
        with col4_2:
                st.metric("Costo producción (USD)", st.session_state.costos_lineas[lineas]['Costo variable de produccion'], border=True)
        with col4_3:
                st.metric("Costo total (USD)", st.session_state.costos_lineas[lineas]['Costo Total de la línea'], border=True)

        st.pyplot(st.session_state.fig_utilizacion_x_linea)


        st.session_state['paso post-procesamiento listo'] = True
        
    else: 
        st.warning("Para visualizar resultados, primero debe resolver alguno de los problemas de optimización.", icon="⚠️")
        st.session_state['paso post-procesamiento listo'] = False