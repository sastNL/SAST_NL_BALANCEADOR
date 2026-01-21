import streamlit as st
import base64

pdf = "Inputs_Homologador_Sack_Kraft_CMPC.pdf"
st.session_state['pdf'] = pdf

def Explicar_documentacion():
    tab1 = 'Carga de datos'
    tab2 = 'Homologador'
    tab3 = 'Parametrización'
    tab4 = 'Errores'
    tab5 = 'Balanceador de cargas'
    
    st.set_page_config("Documentación", layout="wide")
    
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Documentación")
    with col2:
        st.image("logos/Logo-cmpc_1.png", width=120)
    
    tabCargaDatos, tabHomologador, tabParametrizacion, tabErrores, tabBalanceador = st.tabs([
        tab1, tab2, tab3, tab4, tab5
    ])
    
    # Contenido de cada tab
    with tabCargaDatos:
        st.write("En esta sección se mencionan consideraciones importantes sobre cómo cargar los datos iniciales para el homologador y el balanceador.")
        st.download_button(
            "Descargar guía de carga de datos", 
            data=open("Documentacion/Inputs_Homologador_Sack_Kraft_CMPC.pdf", "rb").read(),
            file_name="Inputs_Homologador_Sack_Kraft_CMPC.pdf", 
            mime="application/pdf", 
            key="doc1"
        )

    with tabHomologador:
        st.write("En esta sección se mencionan.")
        st.download_button(
            "Descargar documentación homologador", 
            data=open("Documentacion/Output_Homologador_Sack_Kraft_CMPC.pdf", "rb").read(),
            file_name="Output_Homologador_Sack_Kraft_CMPC.pdf", 
            mime="application/pdf", 
            key="doc2"
        )
    with tabParametrizacion:
        st.write("En esta sección se mencionan consideraciones importantes sobre la parametrización requerida para ejecutar correctamente el balanceador.")
        st.download_button(
            "Descargar documentación de parametrización", 
            data=open("Documentacion/Parametrizacion_Balanceador_Sack_Kraft_CMPC.pdf", "rb").read(),
            file_name="Parametrizacion_Balanceador_Sack_Kraft_CMPC.pdf", 
            mime="application/pdf", 
            key="doc3"
        )

    with tabErrores:
        st.write("En esta sección se detallan los diferentes **reportes de errores** que se generan a lo largo del proceso de optimización del módulo de balanceo.")
        st.download_button(
            "Descargar documentación de reporte de errores", 
            data=open("Documentacion/Documentacion_Reporte_Errores_CMPC.pdf", "rb").read(), 
            file_name="Documentacion_Reporte_Errores_CMPC.pdf", 
            mime="application/pdf", 
            key="doc4"
        )
        

    with tabBalanceador:
        st.write("Se describe el balanceador de cargas y su funcionamiento dentro del homologador.")
        st.download_button(
            "Descargar documentación",
            data=open("Documentacion/Modelo_Matematico_Balanceador_CMPC.pdf", "rb").read(), 
            file_name="Documentacion_Modelo_Matematico_Balanceador_CMPC.pdf",  
            mime="application/pdf", 
            key="doc5"
        )

Explicar_documentacion()


# import streamlit as st
# import base64

# pdf = "Inputs_Homologador_Sack_Kraft_CMPC.pdf"
# st.session_state['pdf'] = pdf

# def Explicar_documentacion():

#     tab1 = 'Carga de datos'
#     icon1 = ":material/cloud_upload:"

#     tab2 = 'Parametrización'
#     icon2 = ":material/settings:"

#     tab3 = 'Errores'
#     icon3 = ":material/error_outline:"

#     tab4 = 'Balanceador de cargas'
#     icon4 = ":material/factory:"
    
#     import streamlit as st
#     st.set_page_config("Documentación", layout = "wide")
            
#     col1, col2 = st.columns([6, 1])
    
#     with col1:
#         st.title("Documentación")
#     with col2:
#         st.image("logos/Logo-cmpc_1.png", width=120)

    
    
#     tabCargaDatos, tabParametrizacion, tabErrores, tabBalanceador = st.tabs([
#                                                                                 f'{icon1} {tab1} ',
#                                                                                 f' {icon2} {tab2}',
#                                                                                 f'{icon3} {tab3}',
#                                                                                 f'{icon4} {tab4}'
#                                                                                 ])

#     with tabCargaDatos:
#         with open(pdf, "rb") as f:
#             base64_pdf = base64.b64encode(f.read()).decode("utf-8")

#         # Mostrar el PDF en un iframe
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)
#         st.download_button("Descargar documentación", data=pdf, file_name="Inputs_Homologador_Sack_Kraft_CMPC.pdf", mime="application/pdf", key = "doc1")
            

#     with tabParametrizacion:
#         with open(pdf, "rb") as f:
#             base64_pdf = base64.b64encode(f.read()).decode("utf-8")

#         # Mostrar el PDF en un iframe
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)
#         st.download_button("Descargar documentación", data=pdf, file_name="Inputs_Homologador_Sack_Kraft_CMPC.pdf", mime="application/pdf", key = "doc2")
    

#     with tabErrores:    
#         with open(pdf, "rb") as f:
#             base64_pdf = base64.b64encode(f.read()).decode("utf-8")

#         # Mostrar el PDF en un iframe
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)
#         st.download_button("Descargar documentación", data=pdf, file_name="Documentacion_Reporte_Errores_CMPC.pdf", mime="application/pdf", key = "doc3")


#     with tabBalanceador:
#         with open(pdf, "rb") as f:
#             base64_pdf = base64.b64encode(f.read()).decode("utf-8")

#         # Mostrar el PDF en un iframe
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)
#         st.download_button("Descargar documentación", data=pdf, file_name="Inputs_Homologador_Sack_Kraft_CMPC.pdf", mime="application/pdf", key = "doc4")
    

# Explicar_documentacion()