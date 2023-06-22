import os, envio, pyodbc
import pandas as pd
from flask import redirect, url_for
from definitions import ROOT_DIR_STATIC


d_f = pd.read_excel(os.path.join(ROOT_DIR_STATIC, 'pandas_cliente.xlsx'),
                engine='openpyxl')

d_f["rut_cliente"] = d_f["rut_cliente"].astype("string")
d_f["rut_cliente"] = d_f["rut_cliente"].str.upper()

print(len(d_f))
d_f = d_f.drop_duplicates(["rut_cliente"], keep='first')
d_f = d_f.sort_values(by=['rut_cliente'], ascending=True)

# d_f.to_excel('clientes_no_repetidos.xlsx', index=False, header=True)

d_f = d_f.drop_duplicates(["rut_cliente"], keep='first')

d_f["nombre_cliente"] = d_f["nombre_cliente"].astype("string")

print(d_f.dtypes)
d_f.convert_dtypes()
print(d_f.dtypes)

print(len(d_f))