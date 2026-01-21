import streamlit as st

from utils_asignacion.materia_prima_procesamiento_de_datos import ProcesarDatos
from utils_asignacion.materia_prima_carga_de_datos import CargarDatos

def materia_prima():
    st.set_page_config("Materia prima", layout="wide")

    icono_tab1 = ":material/cloud_upload:"
    icono_tab2 = ":material/auto_fix_high:"

    nombre_tab1 = "Carga de datos"
    nombre_tab2 = "Procesamiento de datos"
    
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Materia prima")
    with col2:
        st.image("logos/Logo-cmpc_1.png", width=120)

    tabCargarDatos,tabProcesamiento = st.tabs([f'{icono_tab1} {nombre_tab1}', 
                                            f'{icono_tab2} {nombre_tab2}'])
    with tabCargarDatos:
        CargarDatos()

    with tabProcesamiento:
        ProcesarDatos()

materia_prima()