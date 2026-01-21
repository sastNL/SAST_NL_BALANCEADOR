import streamlit as st
import time
import pandas as pd

from utils_asignacion.utils_asignacion_back.Preprocesamiento.Dinamico.LimpiezaDatos import limpieza_datos
from utils_asignacion.utils_asignacion_back.Preprocesamiento.Dinamico.AlgoritmoValidacionAbPrDis import algoritmo_validacion_asignaciones_posibles
from utils_asignacion.utils_asignacion_back.Preprocesamiento.Sets.creacion_conjuntos import creacion_conjuntos_parametros

if 'paso pre-procesamiento listo' not in st.session_state: 
    st.session_state['paso pre-procesamiento listo'] = False
if 'paso carga de datos listo' not in st.session_state: 
    st.session_state['paso carga de datos listo'] = False
if 'nombre del escenario' not in st.session_state: 
    st.session_state['nombre del escenario'] = None
if 'Horizontes' not in st.session_state:
    st.session_state['Horizontes'] = None


def procesar_fecha(fecha):
    meses = {1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO", 6: "JUNIO",
             7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"}
    año, mes = fecha.split("-")
    año = int(año)
    mes_numerico = int(mes)
    mes = meses[mes_numerico]
    return año, mes

def Preprocesar():
    

    if st.session_state['paso carga de datos listo'] == False: 
        st.warning("Primero debe cargar los datos.", icon="⚠️")
        st.session_state['paso pre-procesamiento listo'] = False

    else:
        Horizontes = pd.read_excel('ResultadosEstaticos\Inputs\Horizontes.xlsx', sheet_name='Horizontes')
        st.session_state['Horizontes'] = Horizontes
        horizonte = list(Horizontes['Horizontes'])

        col_1_1, col1_2, col1_3, col1_4 = st.columns([1,1,1,1])

        with col_1_1:

            st.session_state['inicio_horizonte'] = st.selectbox("Seleccionar horizonte de planificación (mes)", horizonte, key = "horizonte de planificacion", index=0)
            year_inicio, mes_inicio = procesar_fecha(st.session_state['inicio_horizonte'])

            st.session_state['categorizacion_productividades'] = st.toggle("Utilizar categorización de **productividades**")

        with col1_2:
            
            st.session_state['fin_horizonte'] = st.selectbox("Seleccionar horizonte de planificación (mes)", horizonte, key = "horizonte de planificacion fin", index=5)
            year_fin, mes_fin = procesar_fecha(st.session_state['fin_horizonte'])
        
        with col1_3:
            st.markdown(f'**Escenario: {st.session_state["nombre del escenario"]}**')

        if st.session_state['inicio_horizonte'] > st.session_state['fin_horizonte']:
            st.error("El horizonte de planificación inicial debe ser menor al horizonte de planificación final")
            
        boton_realizar_pre_procesamiento = st.button("Realizar pre-procesamiento", type = "primary", key = "realizar pre-procesamiento")
            
        if boton_realizar_pre_procesamiento:
            with st.spinner(text="Realizando pre-procesamiento",  show_time=True):
                time.sleep(2)
                
                limpieza_datos(st.session_state['nombre del escenario'],  mes_inicio, year_inicio, mes_fin,  year_fin)
                algoritmo_validacion_asignaciones_posibles(st.session_state['nombre del escenario'])
                creacion_conjuntos_parametros(st.session_state['nombre del escenario'], st.session_state['categorizacion_productividades'])
                
                st.success("Pre-procesamiento realizado con éxito!", icon="✅")
                st.session_state['paso pre-procesamiento listo'] = True