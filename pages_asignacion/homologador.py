import streamlit as st

from utils_asignacion.homologador_procesamiento_de_datos import ProcesarDatos
from utils_asignacion.homologador_ver_metricas import VerMetricas



def homologador():
    st.set_page_config("Homologador", layout="wide")

    icono_tab1 = ":material/auto_fix_high:"
    icono_tab2 = ":material/dashboard_customize:"


    nombre_tab1 ="Procesamiento de datos"
    nombre_tab2 = "Métricas"

    
    col1, col2 = st.columns([6, 1])

    with col1:
        st.title("Homologador")

    with col2:
        st.image("logos/Logo-cmpc_1.png", width=120)

    tabProcesamiento, tabMetricas, = st.tabs([f'{icono_tab1} {nombre_tab1}', 
                                            f'{icono_tab2} {nombre_tab2}'])

    with tabProcesamiento:
        ProcesarDatos()

    with tabMetricas:
        VerMetricas()



    # st.markdown("**Procesamiento de datos**")
    # ProcesarDatos()

homologador()
