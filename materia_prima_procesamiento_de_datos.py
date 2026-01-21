
import streamlit as st
import os
import time

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.LimpiezaMP import limpieza_materia_prima

if 'paso pre-procesamiento listo MP' not in st.session_state:
    st.session_state['paso pre-procesamiento listo MP'] = False

def ProcesarDatos():
    
    if os.listdir('ResultadosEstaticos\Inputs\Materia prima') == []: 
        st.warning("No hay archivos cargados. Por favor, ve a la pestaña 'Carga de datos' para subir los archivos necesarios.", icon="⚠️")
        return
    
    else: 
        col_0_1, col_0_2 = st.columns(2)
        
        with col_0_1:
            boton_procesar_archivos = st.button("Procesar archivos", type="primary", key="procesar_datos")

            if boton_procesar_archivos:
                
                with st.spinner("Procesando archivos..."):
                    limpieza_materia_prima()
                    time.sleep(2)
                    st.session_state['paso pre-procesamiento listo MP'] = True

                    if st.session_state['paso pre-procesamiento listo MP'] == True:    
                        st.success("Procesamiento realizado con éxito!", icon="✅")
                    else: 
                        st.warning("Vuelva a cargar los datos.", icon="⚠️")

            if st.session_state['paso pre-procesamiento listo MP'] == True:
                st.download_button("Descargar archivo MP procesado", data=open('ResultadosEstaticos/Resultados/df_materia_prima.xlsx', 'rb'), file_name='Materia_prima_procesada.xlsx', key="descargar_datos_MP")