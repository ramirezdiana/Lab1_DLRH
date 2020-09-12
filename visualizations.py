"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: comparison of active and passive investments in the NAFTRAC ETF                             -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: ramirezdiana                                                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_if706976_lab1.git                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import plotly.graph_objects as go

"""
Funcion com_vis:

--Recibe: 
    activa: Dataframe con rendimientos de inversion activa 
    pasiva: Dataframe con rendimientos de inversion pasiva 
   code,: string para saber que visualizacion se espera ("capital" o "rendimientos"
--Retorna: 
    una gráfica según el code que puede regresar una visualización de ambas inversiones en su capital
    o en sus rendimientos
"""


def comp_vis(activa, pasiva, code):
    ambas = pd.merge(activa, pasiva, on=activa.index)
    ambas.columns = ["Timestamp", "capital inv_activa", "rend inv_activa", "rend_acum inv_activa",
                     "capital inv_pasiva", "rend inv_pasiva", "rend_acum inv_pasiva"]
    ambas.index = ambas["Timestamp"]
    fig = go.Figure()
    if code == "capital":
        caps = ambas.loc[:, ["capital inv_activa", "capital inv_pasiva"]]
        fig.add_trace(go.Scatter(x=caps.index, y=caps["capital inv_activa"],mode='lines',name='inv_activa'))
        fig.add_trace(go.Scatter(x=caps.index, y=caps["capital inv_pasiva"], mode='lines', name='inv_pasiva'))
        fig.update_layout(title='Capital inversiones')
    elif code == "rendimientos":
        ret = ambas.loc[:, ["rend inv_activa", "rend inv_pasiva"]]
        fig.add_trace(go.Scatter(x=ret.index, y=ret["rend inv_activa"],mode='lines',name='inv_activa'))
        fig.add_trace(go.Scatter(x=ret.index, y=ret["rend inv_pasiva"], mode='lines', name='inv_pasiva'))
        fig.update_layout(title='Rendimiento inversiones')
    fig.show()

"""
Funcion pie:

--Recibe: 
    x: serie de etiquetas para un pie chart
    y: serie de datos para el pie chart
--Retorna: 
    la visualización de un pie chart
"""

def pie(x, y):
    fig = go.Figure(data=[go.Pie(labels=x, values=y)])
    fig.update_traces(textposition='inside')
    fig.update_layout(title='Ponderaciones 31 de enero 2018 NAFTRAC')
    fig.show()



