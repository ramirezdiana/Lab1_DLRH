"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: comparison of active and passive investments in the NAFTRAC ETF                             -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: ramirezdiana                                                                                -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/ramirezdiana/myst_if706976_lab1.git                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import numpy as np
import data as dt
import functions as fc
import visualizations as vis

# fechas mensuales de la lista de archivos--------------------------------------------------------------paso 1 #
dates = dt.dates

# datos iniciales, pesos y tickers de enero 2018 -------------------------------------------------------paso 2 #
data, tickers = dt.dat, dt.ticker

# obtener valor del portafolio pasivo con precios de Yahoo Finance----------------------------------------paso 3 #
port_val, prices = dt.port_va, dt.pri

# cash global y rendimiento pasivo------------------------------------------------------------------------paso 4 #
cash = dt.inversion-np.sum(prices['comision'])-port_val.sum()[0]
df_pasiva = fc.rendimiento(port_val, cash, dt.inversion)
print(df_pasiva)

# datos inciales inversion activa ------------------------------------------------------------------------paso 5 #
active_open, active_closed, init_cash = dt.active_op, dt.active_clo, dt.init_cash

# creación dataframe de cash, valores de precios, comisiones, ty titulos comrpados------------------------paso 6 #
cash_val, titulos_hist, p1, c1, t1 = fc.inversion_activa(active_open, active_closed, dt.comision, dates, init_cash)

# valores de amxl a traves de los meses--------------------------------------------------------------------paso 7 #
amxl = dt.def_amxl(titulos_hist, active_closed, dates)

# portafolio inversion activa y rendimiento --------------------------------------------------------------paso 8 #
port_active = port_val.transpose()
port_active["AMXL.MX"] = amxl
port_active = port_active.transpose()
df_activa = fc.rendimiento(port_active, cash_val["Cash"], dt.inversion)
print(df_activa)

# compras historicas--------------------------------------------------------------------------------------paso 9 #
df_operaciones = fc.active_change(titulos_hist, active_open, p1, c1, t1)
print(df_operaciones)
# comparación de pasivo y activo vs naftrac--------------------------------------------------------------paso 10 #
rend_merc, mercado = dt.naftrac_rend(dates)
comparacion = dt.df_comp(rend_merc, mercado, df_pasiva, df_activa)
print(comparacion)

# extra para notebook

vis.comp_vis(df_activa, df_pasiva, "capital")
vis.comp_vis(df_activa, df_pasiva, "rendimientos")
vis.pie(data["Ticker"],data["Peso (%)"])




