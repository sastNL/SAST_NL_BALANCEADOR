import streamlit as st
import os

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
            
            uploaded_files = st.file_uploader('Archivos necesarios: **Base Brasil BAP.xlsx, Base Brasil CVP.xlsx, Ficha tecnica Chile y Peru Original.xlsx, Ficha tecnica Mexico Original.xlsx**', type=["csv", "xlsx"], accept_multiple_files=True)

    
            if uploaded_files:
                nombres_esperados = ['Ficha tecnica Chile Original.xlsx', 'Ficha tecnica Peru Original.xlsx', 'Ficha tecnica Mexico Original.xlsx', 'Base Brasil BAP.xlsx', 'Base Brasil CVP.xlsx']
                nombres_subidos = []
                nombres_no_validos = []

                carpeta = 'ResultadosEstaticos\Inputs\Fichas tecnicas'

                # Crear la carpeta si no existe
                if not os.path.exists(carpeta):
                    os.makedirs(carpeta)

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
                
                if len(nombres_subidos) == len(nombres_esperados):
                    st.session_state['paso carga de datos fichas tecnicas listo'] = True


    # %%
    # %%
