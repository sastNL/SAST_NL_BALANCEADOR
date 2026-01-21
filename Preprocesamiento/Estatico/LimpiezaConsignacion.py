# %%
import pandas as pd


def limpieza_consignacion():
    """Limpieza de la consignación.
    """
    df_consignacion = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Consignacion', skiprows=2, usecols='C:E')

    #Chequear que la columna CONSIGNACION SEA MAYOR A 0
    df_consignacion = df_consignacion[df_consignacion['CONSIGNACION'] > 0]

    # Exportar df_consignacion a excel filtrado
    df_consignacion.to_excel('ResultadosEstaticos/Resultados/df_consignacion.xlsx', index=False)

if __name__ == "__main__":
    limpieza_consignacion()
