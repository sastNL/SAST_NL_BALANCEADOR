import streamlit as st
import os
import pandas as pd

if 'archivo_estatico_cargado' not in st.session_state:
    st.session_state['archivo_estatico_cargado'] = None
    
def CargarDatosEstaticos():
    col_1_1, col_1_2, col_1_3, col_1_4 = st.columns([4,1,2,1])

    # Botón para descargar ejemplo
    with col_1_4:
        st.download_button(
            label="Descargar ejemplo",
            data=open("Plantillas\Planilla datos estaticos\Planilla de datos - Estatico.xlsx", "rb").read(),
            file_name="Planilla de datos - Estatico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col_1_1:
        uploaded_file = st.file_uploader(
            'Archivo necesario: **Planilla de datos - Estatico.xlsx**', 
            type=["xlsx"], 
            accept_multiple_files=False
        )

        if uploaded_file:
            # Definir carpetas
            carpeta_raw = os.path.join("ResultadosEstaticos", "Inputs", "Planilla datos estaticos")
            os.makedirs(carpeta_raw, exist_ok=True)

            # Guardar archivo en la carpeta
            file_path = os.path.join(carpeta_raw, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Verificar que tenga las sheets requeridas
            nombres_esperados = ["Plantas", "Lineas", "Consignacion", "Clientes", "Codigos clientes", "Costos abastecimiento"]
            try:
                xls = pd.ExcelFile(file_path)
                sheets_en_archivo = xls.sheet_names
            except Exception as e:
                st.error(f"Error al leer el Excel: {e}")
                return

            # Mostrar checks
            for esperado in nombres_esperados:
                if esperado in sheets_en_archivo:
                    st.markdown(f"<span style='color:green'>{esperado} &#10003;</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:red'>{esperado}</span>", unsafe_allow_html=True)
            
            if all(esperado in sheets_en_archivo for esperado in nombres_esperados):
                st.success("Ya puede pasar al procesamiento.", icon="✅")
                
                # Guardar en session_state que el archivo está cargado
                st.session_state['archivo_estatico_cargado'] = file_path
                return