import streamlit as st
import os
from utils_asignacion.utils_asignacion_back.Preprocesamiento.Dinamico.CreacionCorrida import  generar_corrida
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
            uploaded_files = st.file_uploader('Archivos necesarios: **"Forecast.xlsx", "Planilla de datos - Dinamico.xlsx"**', type=["csv", "xlsx"], accept_multiple_files=True)
            if uploaded_files and st.session_state.nombre_escenario:
                carpeta = os.path.join("Corridas",  st.session_state.nombre_escenario, "Inputs")
                os.makedirs(carpeta, exist_ok=True)
                nombres_esperados = ["Forecast.xlsx", "Planilla de datos - Dinamico.xlsx"]
                nombres_subidos = []
                nombres_no_validos = []
                for uploaded_file in uploaded_files:
                    if uploaded_file.name in nombres_esperados:
                        file_path = os.path.join(carpeta, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        nombres_subidos.append(uploaded_file.name)
                    else:
                        nombres_no_validos.append(uploaded_file.name)
                if nombres_no_validos:
                    st.error(f"Los siguientes archivos no son válidos: {', '.join(nombres_no_validos)}")
                # Comparar y mostrar resultados
                for esperado in nombres_esperados:
                    if esperado in nombres_subidos:
                        st.markdown(f"<span style='color:green'>{esperado} &#10003;</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color:red'>{esperado}</span>", unsafe_allow_html=True)
                if set(nombres_esperados) == set(nombres_subidos) and not nombres_no_validos:
                    st.session_state['paso carga de datos listo'] = True
                else:
                    st.session_state['paso carga de datos listo'] = False
