# %%
import pandas as pd

def limpieza_plantas():
    
    df_plantas = pd.read_excel('ResultadosEstaticos/Inputs/Planilla datos estaticos/Planilla de datos - Estatico.xlsx', sheet_name='Plantas', skiprows=2, usecols='C:G')
    
    # Armar df_errores_plantas en caso de que haya algun dato faltante
    df_errores_plantas = df_plantas[df_plantas.isnull().any(axis=1)]
    df_errores_plantas['MOTIVO_ERROR'] = 'Valores nulos en columnas criticas'
    
    # Filtrar que no haya ninguna fila como NaN
    df_plantas = df_plantas.dropna(axis=0, how='all')
    
    # Exportar df_plantas a excel filtrado
    df_plantas.to_excel('ResultadosEstaticos/Resultados/df_plantas.xlsx', index=False)

    # Exportar df_errores_plantas a excel
    df_errores_plantas.to_excel('ResultadosEstaticos/Errores/df_errores_plantas.xlsx', index=False)
    
if __name__ == "__main__":
    limpieza_plantas()
