"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: comparison of active and passive investments in the NAFTRAC ETF                             -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: ramirezdiana                                                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_if706976_lab1.git                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import pandas as pd
import numpy as np
import math

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

"""
Funcion rendimiento:
--Recibe:
    port_val: DataFrame con valor del portafolio para cada acción en el tiempo,
    cash: lista o dato de valor a sumar de efectivo en la inversión
    inversión: inversion incial
--Retorna: 
    df: DataFrame con el capital de la inversión en el tiempo, su rendimiento y rendimeinto acumulado
"""


def rendimiento(port_val, cash, inversion):
    first = pd.DataFrame({"capital": inversion}, index=["2018-01-30 00:00:00"])
    pd.to_datetime(first.index)
    info = pd.DataFrame(port_val.sum(), columns=["capital"])
    info["capital"] = (info["capital"] + cash).astype('float')
    info = first.append(info)
    ret = info.pct_change()
    ret["rend_acum"] = ret.cumsum()
    ret.columns = ["rend", "rend_acum"]
    df = pd.merge(info, ret, on=ret.index)
    df.columns = ["timestamp", "capital", "rend", "rend_acum"]
    df.index = df.timestamp
    df = df.drop(['timestamp'], axis=1)
    pd.options.display.float_format = '{:.4f}'.format
    return df


"""
Funcion inversion_activa:

--Recibe: 
    active_open:Dataframe con precios diarios de inicio del día, 
    active_closed: Dataframe con precios diarios de cierre del día
    comision: porcentaje de comision
    dates: lista de fechas mensuales
    cash: cash inicial para inversión activa
--Retorna: 
    cash_val:DataFrame con valores de cash en el tiempo
    titulos_hist: DataFrame con titulos de cada acción en cada día del periodo
    precio: lista de precios a los que se compró
    com: lista de comision de compra
    titles_c: lista de titulos compradps
"""


def inversion_activa(active_open, active_closed, comision, dates, cash):
    com = [0]
    precio = [0]
    titles_c = [0]
    titulos_hist = pd.DataFrame(columns=active_open.columns, index=active_closed.index)
    titulos_hist.iloc[:, 0] = active_closed['acciones']
    cash_val = pd.DataFrame(index=active_open.columns, columns=["Cash"])
    for column in range(0, (len(active_open.columns)) - 1):
        cash_val.iloc[column, 0] = cash
        close = active_closed[active_open.columns[column]]["AMXL.MX"]
        opened = active_open[active_open.columns[column]]["AMXL.MX"]
        rend = (close - opened) / close
        if rend <= -.01:
            price = active_open[active_open.columns[column + 1]]["AMXL.MX"]
            if cash >= price * (1 + comision):
                for_buy = cash * .1
                titles = for_buy // (price * (1 + comision))
                titles_c.append(titles)
                comi = titles * price * comision
                cash = cash - (titles * price) - comi
                precio.append(price)
                com.append(comi)
            else:
                titles = 0
                titles_c.append(titles)
                precio.append(0)
                com.append(0)
        else:
            titles = 0
            precio.append(0)
            com.append(0)
            titles_c.append(titles)
        active_closed["acciones"]["AMXL.MX"] = active_closed["acciones"]["AMXL.MX"] + titles
        titulos_hist.iloc[:, column + 1] = active_closed['acciones']
    cash_val.iloc[len(cash_val) - 1, 0] = cash_val.iloc[len(cash_val) - 2, 0]
    cash_val = cash_val[cash_val.index.isin(dates)]
    return cash_val, titulos_hist, precio, com, titles_c


"""
Funcion active_change:

--Recibe: 
    titulos_hist: DataFrame con titulos de cada acción en cada día del periodo
    active_open:Dataframe con precios diarios de inicio del día, 
    precio: lista de precios a los que se compró
    com: lista de comision de compra
    titles_c: lista de titulos compradps
--Retorna: 
    active_changes: DataFrame con operaciones realizadas, acciones que se tienen, que se compran,
    el precio, su comisión y la comisión acumulada
"""


def active_change(titulos_hist, active_open, precio, com, titles_c):
    historical = titulos_hist.transpose()
    hist = pd.DataFrame(historical["AMXL.MX"])
    active_changes = pd.DataFrame(titles_c, columns=['Titles_c'])
    active_changes["precio"] = precio
    active_changes["comision"] = com
    active_changes["comision_acum"] = active_changes["comision"].cumsum()
    active_changes.index = active_open.columns
    active_changes = pd.concat([hist, active_changes], axis=1, sort=False)
    active_changes.iloc[0, 1] = active_changes.iloc[0, 0]
    active_changes = active_changes[(active_changes.Titles_c != 0)]
    return active_changes


"""
Función desempeno:

--Recibe: 
    df:  Dataframe con rendimientos de la inversión deseada a medir
    ret: Dataframe con rendimientos del mercado
--Retorna: 
    Lista con las medidas de desempeño para la inversión deseada a medir
"""


def desempeno(df, ret):
    merc_rend = ret.mean()
    merc_desv = ret.std()
    lr = .077 / 12
    rend_annual = df.mean()
    acum = df.astype("float").cumsum().iloc[-1]
    desv_annual = df.std()
    risk_award = rend_annual - lr
    cor = (np.corrcoef(df, ret.Close)[0, 1])
    if math.isnan(cor):
        beta = 1
    else:
        beta = ((desv_annual / merc_desv) * (cor)).item()
    sharpe = risk_award / desv_annual
    traynor = risk_award / beta
    alfa_jensen = (rend_annual - (lr + beta * (merc_rend - lr))).item()
    m2 = (lr * (1 - (merc_desv / beta)) + rend_annual * (merc_desv / beta)).item()
    t2 = ((risk_award / beta) - (merc_rend - lr)).item()
    return np.round([rend_annual, acum, sharpe, traynor, alfa_jensen, m2, t2], 4)
