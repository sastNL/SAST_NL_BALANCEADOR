import pandas as pd

from Preprocesamiento.Dinamico.LimpiezaDistribucion import limpieza_datos_distribucion
from Preprocesamiento.Dinamico.LimpiezaForecast import algoritmo_limpieza_forecast
from Preprocesamiento.Dinamico.LimpiezaCostosProduccion import limpieza_costos_produccion
from Preprocesamiento.Dinamico.LimpiezaTurnosVelocidades import limpieza_turnos_velocidades
from Preprocesamiento.Dinamico.LimpiezaInventario import limpieza_inventario_inicial
from Preprocesamiento.Dinamico.LimpiezaOrdenesAbiertas import limpieza_ordenes_abiertas
from Preprocesamiento.Dinamico.LimpiezaConsignacionDinamica import limpieza_stock_cliente_consignacion

def limpieza_datos(nombre_corrida, mes_inicio, año_inicio, mes_fin, año_fin):

    forecast = pd.read_excel(f'Corridas/{nombre_corrida}/Inputs/Forecast.xlsx')
    df_ficha_tecnica = pd.read_excel('ResultadosEstaticos/Resultados/df_ficha_tecnica.xlsx')

    algoritmo_limpieza_forecast(nombre_corrida, forecast, df_ficha_tecnica, mes_inicio, año_inicio, mes_fin, año_fin)
    print('Ejecución exitosa de limpieza de forecast')
    
    limpieza_datos_distribucion(nombre_corrida)
    print('Ejecución exitosa de limpieza de distribución')

    limpieza_costos_produccion(nombre_corrida)
    print('Ejecución exitosa de limpieza de costos de producción')

    limpieza_turnos_velocidades(nombre_corrida, mes_inicio, año_inicio, mes_fin, año_fin)
    print('Ejecución exitosa de limpieza de turnos y velocidades')

    limpieza_inventario_inicial(nombre_corrida)
    print('Ejecución exitosa de limpieza de inventario inicial')

    limpieza_ordenes_abiertas(nombre_corrida, mes_inicio, año_inicio, mes_fin, año_fin)
    print('Ejecución exitosa de limpieza de ordenes abiertas')
    
    limpieza_stock_cliente_consignacion(nombre_corrida)
    print('Ejecución exitosa de limpieza de stock cliente consignación')
