import streamlit as st
import os
import time
import pandas as pd

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.LimpiezaConsignacion import limpieza_consignacion
from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.LimpiezaPlantas import limpieza_plantas
from utils_asignacion.utils_asignacion_back.Preprocesamiento.Estatico.LimpiezaClientes import limpieza_clientes

def PreprocesarDatosEstaticos():
    
    if "datos_estaticos_procesados" not in st.session_state:
        st.session_state["datos_estaticos_procesados"] = False


    if os.listdir('ResultadosEstaticos/Inputs/Planilla datos estaticos') == []: 
        st.warning(
            "No hay archivos cargados. Por favor, ve a la pestaña 'Carga de datos' para subir los archivos necesarios.",
            icon="⚠️"
        )
        return
    
    col_0_1, col_0_2 = st.columns(2)

    with col_0_1:
        boton_procesar = st.button(
            "Preprocesar datos estáticos",
            type="primary",
            key="procesar_datos_estaticos"
        )

        if boton_procesar:
            with st.spinner("Procesando archivo..."):
                time.sleep(5)
                limpieza_plantas()
                limpieza_consignacion()
                limpieza_clientes()
                st.session_state["datos_estaticos_procesados"] = True
                st.success("Procesamiento realizado con éxito.", icon="✅")

    #Mostrar botones de descarga si los archivos existen o si ya se procesó
    if st.session_state["datos_estaticos_procesados"]:
        output_files = {
            "Plantas": "ResultadosEstaticos/Resultados/df_plantas.xlsx",
            "Consignacion": "ResultadosEstaticos/Resultados/df_consignacion.xlsx",
            "Clientes": "ResultadosEstaticos/Resultados/df_clientes.xlsx"
        }

        for nombre, ruta in output_files.items():
            if os.path.exists(ruta):
                with open(ruta, "rb") as f:
                    st.download_button(
                        label=f"Descargar archivo {nombre}",
                        data=f.read(),
                        file_name=f"{nombre}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"descargar_{nombre.lower()}"

                    )
