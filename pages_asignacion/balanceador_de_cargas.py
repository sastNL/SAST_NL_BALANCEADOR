import streamlit as st

from utils_asignacion.balanceador_cargar_datos import CargarDatos
from utils_asignacion.balanceador_pre_procesar import Preprocesar
from utils_asignacion.balanceador_parametrizar import Parametrizar
from utils_asignacion.balanceador_resolver_modelo import Resolver_modelo
from utils_asignacion.balanceador_post_procesar import Postprocesar

def asignador_de_cargas():

    icono_step1 = ":material/counter_1:"
    icono_step2 = ":material/counter_2:"
    icono_step3 = ":material/counter_3:" 
    icono_step4 = ":material/counter_4:"
    icono_step5 = ":material/counter_5:"

    nombre_step1 = "Cargar datos"
    nombre_step2 = "Pre-procesamiento"
    nombre_step3 = "Parametrización"
    nombre_step4 = "Optimización"
    nombre_step5 = "Post-procesamiento"



    st.set_page_config("Asignador de cargas", layout = "wide")


            
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.title("Asignación y balanceo de cargas")
    with col2:
        st.image("logos/Logo-cmpc_1.png", width=120)

    tabCargaDatos, tabPreProcess, tabParametrizacion, tabOptimizacion, tabPostProcess= st.tabs([f"{icono_step1} {nombre_step1}",
                                                            f"{icono_step2} {nombre_step2}",
                                                            f"{icono_step3} {nombre_step3}",
                                                            f"{icono_step4} {nombre_step4}",
                                                            f"{icono_step5} {nombre_step5}"])
    with tabCargaDatos:
            CargarDatos()
    with tabPreProcess:
            Preprocesar()
    with tabParametrizacion: 
            Parametrizar()
    with tabOptimizacion:
            Resolver_modelo() 
    with tabPostProcess: 
            Postprocesar()  



asignador_de_cargas()

