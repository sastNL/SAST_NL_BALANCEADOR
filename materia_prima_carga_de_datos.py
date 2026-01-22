import streamlit as st
import os
from utils_asignacion.file_upload_utils import procesar_archivos_subidos

def CargarDatos():
    
    col_1_1, col_1_2, col_1_3, col_1_4= st.columns([4,1,2,1])

    with col_1_4:
        st.download_button(
                label="Descargar ejemplo",
                data=open("Plantillas\Materia prima\Materia prima.xlsx", "rb").read(),
                file_name="Materia prima.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col_1_1:
        uploaded_files = st.file_uploader(
            'Archivos necesarios: **Materia prima.xlsx**', 
            type=["xlsx"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            nombres_esperados = ["Materia prima.xlsx"]
            carpeta = 'ResultadosEstaticos\Inputs\Materia prima'
            
            _, _, todos_validos = procesar_archivos_subidos(
                uploaded_files,
                nombres_esperados,
                carpeta
            )
            
            if todos_validos:
                st.success("Ya puede pasar al procesamiento.", icon="✅")
