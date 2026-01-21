import os

def generar_corrida(nombre_corrida):
    # Crear carpeta Corridas si no existe, y dentro la carpeta llamada nombre_corrida
    if not os.path.exists(f'./Corridas'):
        os.makedirs(f'./Corridas')
    if not os.path.exists(f'./Corridas/{nombre_corrida}'):
        os.makedirs(f'./Corridas/{nombre_corrida}')
    if not os.path.exists(f'./Corridas/{nombre_corrida}/Inputs'):
        os.makedirs(f'./Corridas/{nombre_corrida}/Inputs')
    if not os.path.exists(f'./Corridas/{nombre_corrida}/Preprocesamiento'):
        os.makedirs(f'./Corridas/{nombre_corrida}/Preprocesamiento')
    if not os.path.exists(f'./Corridas/{nombre_corrida}/Errores'):
        os.makedirs(f'./Corridas/{nombre_corrida}/Errores')
    if not os.path.exists(f'./Corridas/{nombre_corrida}/Resultados'):
        os.makedirs(f'./Corridas/{nombre_corrida}/Resultados')