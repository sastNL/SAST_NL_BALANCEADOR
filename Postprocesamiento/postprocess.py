from Postprocesamiento.export_model import export_model_results
from Postprocesamiento.graficos_output import heatmap_produccion, heatmap_utilizacion, heatmap_produccion_planta, grafico_barras_asignacion_planta, heatmap_utilizacion_planta
from Postprocesamiento.kpis import calculo_kpis

def postprocess(modelo, nombre_archivo, nombre_corrida, inicio_horizonte):
    export_model_results(modelo, nombre_archivo, nombre_corrida)
    fig_produccion_x_linea = heatmap_produccion(nombre_corrida, inicio_horizonte)
    fig_utilizacion_x_linea = heatmap_utilizacion(nombre_corrida, inicio_horizonte)
    fig1 = heatmap_produccion_planta(nombre_corrida, inicio_horizonte)
    fig2 = grafico_barras_asignacion_planta(nombre_corrida, inicio_horizonte)
    fig3 = heatmap_utilizacion_planta(nombre_corrida, inicio_horizonte)
    reporte_kpis, costo_lineas = calculo_kpis(modelo)

    return reporte_kpis, costo_lineas, fig_produccion_x_linea, fig_utilizacion_x_linea, fig1, fig2, fig3