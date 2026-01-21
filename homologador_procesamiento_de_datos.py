
import streamlit as st
import os
import time
import subprocess

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.AlgoritmoGH import algoritmo_gh

if 'homologador generado' not in st.session_state:
    st.session_state['homologador generado'] = False

if 'hay ficha tecnica generada' not in st.session_state:
    st.session_state['hay ficha tecnica generada'] = False

if 'paso_preprocesamiento_listo' not in st.session_state:
    st.session_state['paso_preprocesamiento_listo'] = False

if 'resultados_homologador' not in st.session_state:
    st.session_state['resultados_homologador'] = None

    
def verificar_que_haya_ficha_tecnica_generada():
    RUTA = "ResultadosEstaticos\Resultados"
    
    # Verificar si existe archivo df_ficha_tecnica.xlsx
    archivo = os.path.join(RUTA, "df_ficha_tecnica.xlsx")
    if os.path.exists(archivo):
        st.session_state['hay ficha tecnica generada'] = True
    else: 
        st.session_state['hay ficha tecnica generada'] = False

def ProcesarDatos():

    verificar_que_haya_ficha_tecnica_generada()
    
    if st.session_state['hay ficha tecnica generada']:

        boton_procesar_archivos = st.button(
            "Procesar archivos",
            type="primary",
            key="procesar_datos"
        )
        
        col_0_1, col_0_2 = st.columns(2)

        with col_0_1: 
            if boton_procesar_archivos:
                with st.spinner('Procesando archivos...'):
                    resultados_homologador = algoritmo_gh()
                    time.sleep(1)  # simula tiempo de procesamiento

                st.session_state['resultados_homologador'] = resultados_homologador
                st.session_state['paso_preprocesamiento_listo'] = True
                st.session_state['homologador generado'] = True

        # Mostrar siempre los botones de descarga si el homologador ya se generó
        if st.session_state["homologador generado"] == True:
            st.success("Archivos procesados con éxito!", icon="✅")
            
            with open("ResultadosEstaticos/Resultados/df_homologaciones.xlsx", "rb") as f:
                st.download_button(
                    label="Descargar homologador",
                    data=f,
                    file_name="df_homologaciones.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descargar_homologador"
                )

            with open("ResultadosEstaticos/Errores/df_homologacion_seguimiento.xlsx", "rb") as f:
                st.download_button(
                    label="Descargar seguimiento de homologaciones",
                    data=f,
                    file_name="df_homologacion_seguimiento.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descargar_seguimiento"
                )
                
            
            if st.button(
                "Abrir carpeta de errores", 
                type="primary", 
                key="abrir_carpeta_errores"
            ):
                carpeta_errores = os.path.join("ResultadosEstaticos", "Errores")
                if os.path.exists(carpeta_errores):
                    # Abrir carpeta en el explorador de archivos de Windows
                    subprocess.Popen(f'explorer "{os.path.abspath(carpeta_errores)}"')
                else:
                    st.warning(
                        "La carpeta de errores aún no existe.", 
                        icon="⚠️"
                    )

    else: 
        st.warning(
            "Para poder usar el Homologador, debes generar la ficha técnica primero. Vuelva a la página de Ficha técnica.",
            icon="⚠️"
        )