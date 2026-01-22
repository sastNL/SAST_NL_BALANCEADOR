import streamlit as st
import os

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Dinamico.CreacionCorrida import  generar_corrida
from utils_asignacion.file_upload_utils import crear_file_uploader_con_validacion


if 'paso carga de datos listo' not in st.session_state: 
    st.session_state['paso carga de datos listo'] = False 

if 'nombre del escenario' not in st.session_state:  
    st.session_state['nombre del escenario'] = None

if "datos_estaticos_procesados" not in st.session_state:
    st.session_state["datos_estaticos_procesados"] = False

def CargarDatos():

    col_1_1, col_1_2, col_1_3 = st.columns([1,2,1])

    with col_1_1:
            st.session_state.nombre_escenario = st.text_input("Nombre del escenario", key = "nombre del escenario")
            if st.button("Generar corrida", key = "boton generar corrida"):
                generar_corrida(st.session_state.nombre_escenario)
                st.success(f"Corrida '{st.session_state.nombre_escenario}' generada con éxito.", icon="✅")

    col_2_1, col_2_2, col_2_3 = st.columns([6,2,1])

    with col_2_3:
        st.download_button(
        label="Descargar ejemplos",
        #data=os.path.join("Plantillas", "Balanceador de cargas", "Cargar datos", "Forecast+Planilla de datos - Dinamico.zip"),
        data=open("Plantillas\Balanceador de cargas\Cargar datos\Forecast+Planilla de datos - Dinamico.zip", "rb").read(),
        file_name= 'Forecast+Planilla de datos - Dinamico.zip',
        mime="application/zip"
    )

         
    with col_2_1:
            
            uploaded_files = st.file_uploader(
                'Archivos necesarios: **"Forecast.xlsx", "Planilla de datos - Dinamico.xlsx"**', 
                type=["csv", "xlsx"], 
                accept_multiple_files=True
            )

            if uploaded_files and st.session_state.nombre_escenario:
                carpeta = os.path.join("Corridas",  st.session_state.nombre_escenario, "Inputs")
                nombres_esperados = ["Forecast.xlsx", "Planilla de datos - Dinamico.xlsx"]
                
                from utils_asignacion.file_upload_utils import procesar_archivos_subidos
                procesar_archivos_subidos(
                    uploaded_files,
                    nombres_esperados,
                    carpeta,
                    session_state_key='paso carga de datos listo'
                )
