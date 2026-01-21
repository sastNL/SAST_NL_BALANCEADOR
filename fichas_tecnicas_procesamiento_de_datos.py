import streamlit as st
import os
import time

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.LimpiezaFichaTecnica import limpieza_ficha_tecnica

if 'paso_preprocesamiento_listo' not in st.session_state:
    st.session_state['paso_preprocesamiento_listo'] = False

def ProcesarDatos():
    # carpeta = 'ResultadosEstaticos\Resultados\Fichas tecnicas'
    # if not os.path.exists(carpeta):
    #     os.makedirs(carpeta)
        
    RUTA = R"ResultadosEstaticos\Inputs\Fichas tecnicas"
    archivos = [f for f in os.listdir(RUTA)]
    
    if archivos:
        boton_procesar_archivos = st.button(
            "Procesar archivos",
            type="primary",
            key="procesar_datos"
        )
        col_0_1, col_0_2 = st.columns(2)  

        with col_0_1: 
            if boton_procesar_archivos:
                with st.spinner("Procesando archivos..."):
                    time.sleep(2)
                    limpieza_ficha_tecnica()
                
                # Guardar flag para indicar que ya se procesó
                st.session_state['paso_preprocesamiento_listo'] = True

        # Mostrar siempre los botones si ya se procesó
        if st.session_state.get('paso_preprocesamiento_listo', False):
            st.success("Archivos procesados con éxito!", icon="✅")
            st.download_button(
                label='Descargar archivos procesados', 
                data=open('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx', 'rb').read(),
                file_name='Fichas tecnicas.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key='descargar_fichas_tecnicas'
            )
        
    else: 
        st.warning("Vuelva a cargar los datos en la página anterior, no hay archivos para procesar.", icon="⚠️")