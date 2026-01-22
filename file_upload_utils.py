"""
Utilidades generales para la carga de archivos.
Contiene funciones reutilizables para evitar duplicación de código.
"""
import streamlit as st
import os


def procesar_archivos_subidos(uploaded_files, nombres_esperados, carpeta_destino, session_state_key=None):
    """
    Procesa archivos subidos, validando sus nombres y guardándolos en una carpeta.
    
    Args:
        uploaded_files: Lista de archivos subidos por streamlit file_uploader
        nombres_esperados: Lista de nombres de archivos esperados
        carpeta_destino: Ruta de la carpeta donde se guardarán los archivos
        session_state_key: (Opcional) Clave del session_state para marcar como completado
        
    Returns:
        tuple: (nombres_subidos, nombres_no_validos, todos_archivos_validos)
    """
    nombres_subidos = []
    nombres_no_validos = []
    
    # Crear la carpeta si no existe
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Procesar cada archivo subido
    for uploaded_file in uploaded_files:
        if uploaded_file.name in nombres_esperados:
            file_path = os.path.join(carpeta_destino, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            nombres_subidos.append(uploaded_file.name)
        else:
            nombres_no_validos.append(uploaded_file.name)
    
    # Mostrar errores si hay archivos no válidos
    if nombres_no_validos:
        st.error(f"Los siguientes archivos no son válidos: {', '.join(nombres_no_validos)}")
    
    # Comparar y mostrar resultados con checkmarks
    for esperado in nombres_esperados:
        if esperado in nombres_subidos:
            st.markdown(f"<span style='color:green'>{esperado} &#10003;</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'>{esperado}</span>", unsafe_allow_html=True)
    
    # Verificar si todos los archivos esperados están presentes
    todos_archivos_validos = set(nombres_esperados) == set(nombres_subidos) and not nombres_no_validos
    
    # Actualizar session_state si se proporcionó la clave
    if session_state_key:
        st.session_state[session_state_key] = todos_archivos_validos
    
    return nombres_subidos, nombres_no_validos, todos_archivos_validos


def crear_file_uploader_con_validacion(label, nombres_esperados, carpeta_destino, 
                                       file_types=None, session_state_key=None):
    """
    Crea un file_uploader con validación automática de archivos.
    
    Args:
        label: Etiqueta para el file_uploader
        nombres_esperados: Lista de nombres de archivos esperados
        carpeta_destino: Ruta de la carpeta donde se guardarán los archivos
        file_types: Lista de extensiones permitidas (ej: ["xlsx", "csv"])
        session_state_key: (Opcional) Clave del session_state para marcar como completado
        
    Returns:
        tuple: (nombres_subidos, nombres_no_validos, todos_archivos_validos)
    """
    if file_types is None:
        file_types = ["csv", "xlsx"]
    
    uploaded_files = st.file_uploader(
        label, 
        type=file_types, 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        return procesar_archivos_subidos(
            uploaded_files, 
            nombres_esperados, 
            carpeta_destino, 
            session_state_key
        )
    
    return [], [], False
