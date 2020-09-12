"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: comparison of active and passive investments in the NAFTRAC ETF                             -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: ramirezdiana                                                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_if706976_lab1.git                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import numpy as np
import yfinance as yf
from functions import desempeno
import os

inversion = 1000000
comision = .00125
filenames = os.listdir(r'files\NAFTRAC_holdings') #leer nobres de archivos
dates = pd.DataFrame(index=[x.replace('NAFTRAC_', '').replace('.csv', '') for x in filenames]) #limpiar nombres
dates = pd.to_datetime(dates.index).sort_values() #convertir a fechas y ordenarlas


"""
Funcion data_clean:
--Retorna: 
    data: DataFrame del 31 de enero con la informacion de excel limpia
    tickers: lista de los tickers para ser descargados  
"""


def data_clean():
    data = pd.read_csv(r'files\NAFTRAC_holdings\NAFTRAC_310118.csv', skiprows=2)
    data.drop(data.tail(2).index, inplace=True)
    data.drop([10, 16], inplace=True)
    data = data.replace('GFREGIOO', "RA").replace('MEXCHEM*', "ORBIA").replace("LIVEPOLC.1", "LIVEPOLC-1")
    ticker_list = data["Ticker"].tolist()
    tickers = [i.replace('*', '') + ".MX" for i in ticker_list]
    return data, tickers


dat, ticker = data_clean()


"""
Funcion portafolio:
--Recibe:
    prices1: Dataframe con precios de yfinance
    tickers: Lista de tickers
    data: DataFrame del 31 de enero con la informacion de excel limpia
    inversion: Cantidad de dinero para inversion inicial
    comision: porcentaje de comision
    dates: Lista de fechas mensuales
--Retorna: 
    port_val: DataFrame con valor del portafolio para cada acción en el tiempo,
    prices:  DataFrame con valor del precios para cada acción en el tiempo, junto con el peso de la inversión, 
            el dinero disponible para la misma, la cantidad de acciones a comprar y la comsion
"""


def portafolio(prices2, tickers, data, inv, com, date):
    prices = prices2.drop(['Open', 'High', 'Low', 'Volume', "Adj Close"], axis=1, level=1).droplevel(1, axis=1)
    prices = prices[prices.index.isin(date)].transpose()
    data["Tickers"] = tickers
    data = data.set_index("Tickers")
    prices['peso'] = pd.DataFrame(data['Peso (%)'] / 100)
    prices['Money'] = (prices['peso'] * inv) - (prices['peso'] * inv * com)
    prices['acciones'] = prices['Money'] // prices.iloc[:, 0]
    prices['comision'] = prices.iloc[:, 0] * prices['acciones'] * com
    port_val = pd.DataFrame(prices.iloc[:, 0:32].mul(prices.acciones, axis=0))
    return port_val, prices


prices1 = yf.download(ticker, start="2018-01-31", end="2020-08-22", actions=False,
                      group_by="close", interval="1d", auto_adjust=False, prepost=False, threads=True)
port_va, pri = portafolio(prices1, ticker, dat, inversion, comision, dates)

"""
Funcion data_activo_clean:
--Recibe:
    prices1: Dataframe con precios de yfinance
    prices:  DataFrame con valor del precios para cada acción en el tiempo, junto con el peso de la inversión, 
            el dinero disponible para la misma, la cantidad de acciones a comprar y la comsion que fueron
            utilizadas en la inversión pasiva
    inversion: Cantidad de dinero para inversion inicial
    comision: porcentaje de comision
--Retorna: 
    active_open: Dataframe con precios de yfinance de abertura
    active_closed: Dataframe con precios de yfinance de cierre
    cash_init: La cantidad de dinero que se usará para comprar acciones de AMXL,
"""


def data_activo_clean(prices_des, prices_v, com_v, inversion_v):
    active_closed = prices_des.drop(['Open', 'High', 'Low', 'Volume', "Adj Close"],
                                 axis=1, level=1).droplevel(1,axis=1).transpose()
    active_open = prices_des.drop(['Close', 'High', 'Low', 'Volume', "Adj Close"],
                               axis=1, level=1).droplevel(1,axis=1).transpose()
    active_closed['acciones'] = prices_v['acciones']
    active_closed["acciones"]["AMXL.MX"] = active_closed["acciones"]["AMXL.MX"]/2
    active_closed['comision'] = active_closed.iloc[:, 0]*active_closed['acciones']*com_v
    cash_init = inversion_v-np.sum(active_closed['comision'])-sum(active_closed.iloc[:, 0].mul(active_closed.acciones,
                                                                                               axis=0))
    return active_open, active_closed, cash_init


active_op, active_clo, init_cash = data_activo_clean(prices1, pri, comision, inversion)

"""
Funcion def_amxl:
--Recibe:
    titulos_hist: DataFrame con titulos de cada acción en cada día del periodo
    active_closed: Dataframe con precios de yfinance de cierre
    dates: Lista de fechas mensuales
--Retorna: 
    DataFrame con valores de amxl en inversión activa a traves de los meses
"""


def def_amxl(titulos_hist, active_closed, dates):
    historical = titulos_hist.transpose()
    historical = historical[historical.index.isin(dates)]
    act_closed = active_closed.transpose()
    amxl = act_closed[act_closed.index.isin(dates)]
    amxl = amxl["AMXL.MX"]
    hist = historical["AMXL.MX"]
    return hist.mul(amxl)


"""
Funcion naftrac_rend:
--Recibe:
    dates: Lista de fechas mensuales
--Retorna: 
    ret_merc: DataFrame con rendimiento del naftrac
    mercado: DataFrame con precios del naftrac
"""


def naftrac_rend(dates):
    mercado1 = yf.download(["NAFTRAC.MX"], start="2018-01-30", end="2020-08-22", actions=False,
                           group_by="close", interval="1d", auto_adjust=False, prepost=False, threads=True)
    mercado = mercado1.drop(['Open', 'High', 'Low', 'Volume', "Adj Close"], axis=1)
    mercado = pd.DataFrame(mercado[mercado.index.isin(dates)])
    ret_merc = mercado.pct_change()
    ret_merc.iloc[0] = 0
    return ret_merc, mercado


"""
Funcion df_comp:
--Recibe:
    ret_merc: DataFrame con rendimiento del naftrac
    mercado: DataFrame con precios del naftrac
    df_activa: Dataframe con el capital, rendimiento y rendimiento acumulado de la inversión activa
    df_pasiva: Dataframe con el capital, rendimiento y rendimiento acumulado de la inversión pasiva
--Retorna: 
    comparacion: DataFrame con las medidas de desempeno de la inversión activa, inversión pasiva y del mercado
"""


def df_comp(ret_merc, mercado, df_pasiva, df_activa):
    explicacion = ["Rendimiento Promedio Mensual", "Rendimiento mensual acumulado", "Sharpe Ratio", "Ratio de Traynor",
                   "Alfa de Jensen", "M2", "T2"]
    comparacion = pd.DataFrame(explicacion, columns=['Descripcion'])
    comparacion["Mercado"] = desempeno(mercado.Close.pct_change(), ret_merc)
    comparacion.iloc[4:7, 1] = 0
    comparacion["Inv_pasiva"] = desempeno(df_pasiva.rend.dropna(), ret_merc)
    comparacion["Inv_activa"] = desempeno(df_activa.rend.dropna(), ret_merc)
    comparacion.index = ["Rend mensual", "Rend acum", "Sharpe", "Traynor", "Alfa_jensen", "M2", "T2"]
    return comparacion
