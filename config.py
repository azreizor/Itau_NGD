import os, pandas as pd

def traer_config():
    archivo_conf = os.path.join(os.getcwd(), './server_conf.ini')
    # print(archivo_conf)
    df = pd.read_csv(archivo_conf, delimiter="=", header=None, names=["dato", "valor"])
    server = df['valor'][2]
    database = df['valor'][3]
    uid = df['valor'][4]
    pwd = df['valor'][5]
    config = "Driver={SQL Server}; Server="+server+"; Database="+database+"; UID="+uid+"; PWD="+pwd+";"
    return config