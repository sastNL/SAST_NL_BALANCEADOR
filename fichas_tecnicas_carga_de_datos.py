import streamlit as st
import os
from utils_asignacion.file_upload_utils import procesar_archivos_subidos

if 'paso carga de datos fichas tecnicas' not in st.session_state: 
    st.session_state['paso carga de datos fichas tecnicas'] = False

def CargarDatos():

    disponibilidad_archivo_MP = os.path.exists(path="ResultadosEstaticos/Resultados/df_materia_prima.xlsx")
    
    if disponibilidad_archivo_MP == False:
        st.warning("Es necesario generar archivo en página **Materia prima** para utilizar en página de **Fichas técnicas**.", icon="⚠️")
    
    else: 
        col_1_1, col_1_2, col_1_3, col_1_4= st.columns([4,1,2,1])

    # Botón para descargar ejemplo
        with col_1_4:
            st.download_button(
                label="Descargar ejemplo",
                data=open("Plantillas\Fichas tecnicas\Fichas_tecnicas_cargar_datos.zip", "rb").read(),
                file_name="FichasTecnicas.zip",
                mime="application/zip"
            )
        with col_1_1:
            
            uploaded_files = st.file_uploader(
                'Archivos necesarios: **Base Brasil BAP.xlsx, Base Brasil CVP.xlsx, Ficha tecnica Chile y Peru Original.xlsx, Ficha tecnica Mexico Original.xlsx**', 
                type=["csv", "xlsx"], 
                accept_multiple_files=True
            )

            if uploaded_files:
                nombres_esperados = [
                    'Ficha tecnica Chile Original.xlsx', 
                    'Ficha tecnica Peru Original.xlsx', 
                    'Ficha tecnica Mexico Original.xlsx', 
                    'Base Brasil BAP.xlsx', 
                    'Base Brasil CVP.xlsx'
                ]
                carpeta = 'ResultadosEstaticos\Inputs\Fichas tecnicas'
                
                procesar_archivos_subidos(
                    uploaded_files,
                    nombres_esperados,
                    carpeta,
                    session_state_key='paso carga de datos fichas tecnicas listo'
                )
