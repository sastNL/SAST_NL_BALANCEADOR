import streamlit as st


if 'homologador generado' not in st.session_state:
    st.session_state['homologador generado'] = False

if 'resultados_homologador' not in st.session_state:
    st.session_state['resultados_homologador'] = None

def VerMetricas():

    if st.session_state['homologador generado'] == False:
        st.warning("Vuelva a generar el homologador.", icon="⚠️")
        
    else: 
        col_1_1, col_1_2, col_1_3= st.columns([1,1,1])

        with col_1_1:
            st.metric("Cantidad de SKU homolgados", value = st.session_state.get('resultados_homologador', {}).get('cantidad_skus_homologados', 0), border=True)

        with col_1_2:
            st.metric("Porcentaje de SKU homologados", value = st.session_state['resultados_homologador'].get('porcentaje_homologacion',0), border=True)

        with col_1_3:
            st.metric("Cantidad de SKU sin asignación en planta actual", value = st.session_state['resultados_homologador'].get('cantidad_skus_sin_asignacion_planta_actual',0), border=True)