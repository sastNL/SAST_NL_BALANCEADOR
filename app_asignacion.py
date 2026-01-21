import streamlit as st

def app_asignacion():
    st.logo(
        image="logos/Logo-normal.png",
        size="small",
        icon_image="logos/Logo-normal.png"
    )

    # Menú con grupos usando diccionarios
    pg = st.navigation({
        "Carga y procesamiento de datos": [
            st.Page("./pages_asignacion/planilla_datos_estaticos.py", title="Planilla de datos estáticos", icon=":material/grid_on:"),
            st.Page("./pages_asignacion/materia_prima.py", title="Materia prima", icon=":material/inventory_2:"),
            st.Page("./pages_asignacion/fichas_tecnicas.py", title="Ficha técnica", icon=":material/perm_data_setting:")
        ],
        "Herramientas": [
            st.Page("./pages_asignacion/homologador.py", title="Homologador", icon=":material/offline_pin:"),
            st.Page("./pages_asignacion/balanceador_de_cargas.py", title="Balanceador de cargas", icon=":material/factory:")
        ],
        "Documentación":[ 
            st.Page("./pages_asignacion/documentacion.py", title="Documentación", icon=":material/menu_book:")
        ]
    })

    pg.run()


app_asignacion()