import streamlit as st
import os

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
        uploaded_files = st.file_uploader('Archivos necesarios: **Materia prima.xlsx**', type=["xlsx"], accept_multiple_files=True)

 
        if uploaded_files:

            nombres_esperados = ["Materia prima.xlsx"]
            nombres_subidos = []
            nombres_no_validos = []

            carpeta = 'ResultadosEstaticos\Inputs\Materia prima'

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
                    st.success("Ya puede pasar al procesamiento.", icon="✅")
                else:
                    st.markdown(f"<span style='color:red'>{esperado}</span>", unsafe_allow_html=True)