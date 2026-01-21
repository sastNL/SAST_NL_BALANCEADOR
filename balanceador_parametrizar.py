from narwhals import col
import streamlit as st


if 'paso parametrizacion listo' not in st.session_state: 
    st.session_state['paso parametrizacion listo'] = False
if 'paso pre-procesamiento listo' not in st.session_state: 
    st.session_state['paso pre-procesamiento listo'] = False



def Parametrizar():

    if st.session_state['paso pre-procesamiento listo'] == True:
        col1_1, col1_2, col1_4 = st.columns([2,1,1])

        with col1_4: 
            st.markdown(f'**Escenario: {st.session_state["nombre del escenario"]}**')

        parametros = {}

        # col_2_1, col_2_2 = st.columns([1,1])

        with col1_1:    

            considerar = st.toggle("Considerar **aranceles**", key = "consider")
            if considerar:
                st.session_state['considerar aranceles'] = True
                parametros['considerar aranceles'] = True
            else:
                st.session_state['considerar aranceles'] = False
                parametros['considerar aranceles'] = False
            
   
            st.session_state['permitir satisfacer demanda interna'] = st.toggle(
                "Forzar la producción de **demanda interna** en el mismo país", 
                help = "Si la opción está activada se impone producir la demanda interna de un país en líneas del mismo país",
                key="permitir otro pais"
            )

            parametros['permitir satisfacer demanda interna'] = st.session_state['permitir satisfacer demanda interna']

        col_hora_extra, _ = st.columns([1,3])
        with col_hora_extra:
            max_horas_extras = st.number_input("Máximo porcentaje de horas extras [%]", min_value=0.00, max_value=500.00, step = 1.00, help = "**Ejemplo**: 20 implica un 20% más de la capacidad de cada línea", key = "maximo horas extras")
            parametros['maximo horas extras'] = max_horas_extras

        col_3_1, col_3_2, col_3_3, col_3_4 = st.columns([1,1,1,1])
        
        with col_3_1:
            parametros['GAP'] = st.number_input("GAP [%]", min_value=0.0, max_value=100.0, value=5.0, step=1.0, key = "GAP")

            if parametros['GAP'] < 0 or parametros['GAP']> 100:
                st.error("El GAP debe estar entre 0 y 100")
  
        with col_3_2:
            parametros['tiempo computo maximo']= st.number_input("Tiempo de cómputo máximo [segundos]", min_value=0, max_value=10000, value=1800, step=1, key = "tiempo computo maximo")
            
        col_4_1, col_4_2, col_4_3 = st.columns([1,1,1])
        
        with col_4_1:
            
            correr_modelo_lexicografico = st.toggle('Correr modelo de balanceo de líneas', help= "Si la opción está activada se resuelve un segundo modelo en el cual se balancea la utilización de todas las líneas." , key = "correr modelo lexicografico")
            
            if correr_modelo_lexicografico:
                parametros['lexicografico'] = True
                parametros['porcentaje_degradacion'] = st.number_input("Porcentaje de degradación del costo total obtenido [%]", min_value=0.0, max_value=100.0, value=20.0, step=0.5, help= 'Este parámetro controla el nivel de degradación aceptable en el costo total del modelo.', key = "porcentaje_degradacion")
            
            else:
                parametros['lexicografico'] = False

            st.session_state['parametros'] = parametros
            st.session_state['paso parametrizacion listo'] = True

        
    else: 
        st.warning("Primero debe pre-procesar los datos.", icon="⚠️")
        st.session_state['paso parametrizacion listo'] = False