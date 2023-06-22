import os, envio, pyodbc
import pandas as pd
from flask import redirect, url_for
from definitions import ROOT_DIR_LECTURA

#------------------------------------------------------------------------------------
def carga_findur(archivo): #finalizado
    """carga_findur"""
    # guardado = os.path.join(dir_lectura, archivo.filename

    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))

    df_columnas = list(d_f.columns)
    columnas = ['Deal No.', 'Tipo Instrumento* *', 'Trade Date *', 'Maturity Date', 'Ext Lentity', 'Nombre Cliente* *',
                'Currency', 'Position', 'Price', 'Buy/Sell', 'Int Contact *']
    n_coincidencias = len(set(df_columnas) & set(columnas)) ### campos findur == 11
    if n_coincidencias == 11:
        df_columnas = d_f[d_f.columns.intersection(columnas)]
        df_columnas.columns = ('num_operacion', 'nombre_producto', 'fecha_operacion', 'fecha_vencimiento', 'rut_cliente',
                            'nombre_cliente', 'divisa_inicial', 'monto_inicial', 'tasa_cambio', 'compra_venta', 'codigo_trader')
        df_columnas[["nombre_producto","rut_cliente","nombre_cliente","divisa_inicial","compra_venta","codigo_trader"]] = df_columnas[["nombre_producto","rut_cliente","nombre_cliente","divisa_inicial","compra_venta","codigo_trader"]].astype("string")
        status, cambios = envio.envio_findur(df_columnas)
        return status, cambios
    status = "400"
    cambios = {"Error":"El formato no Corresponde"}
    return status, cambios

#------------------------------------------------------------------------------------

def carga_murex(archivo): #finalizado
    """carga_murex"""
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = d_f.rename(columns={d_f.columns[6]:"venc1", d_f.columns[7]:"venc2"})
    df_columnas = list(d_f.columns)
    columnas = ['G.ID', 'NAME', 'COUNTERPART', 'TRN.DATE', 'venc1', 'venc2',
                'B/S', 'CUR 0', 'NOMINAL 0', 'RATE 0', 'CUR 1', 'NOMINAL 1','TRADER', 'CNT.TYPOLOGY']
    n_coincidencias = len(set(df_columnas) & set(columnas)) ### campos findur == 14
    if n_coincidencias == 14:
        df_columnas = d_f[d_f.columns.intersection(columnas)]
        vencimiento = pd.DataFrame()
        vencimiento = df_columnas["venc2"].fillna(df_columnas["venc1"])
        df_columnas = df_columnas.drop(columns=['venc1', 'venc2'])
        df_columnas["vencimiento"] = vencimiento
        df_columnas.columns = ('num_operacion', 'nombre_cliente', 'rut_cliente', 'fecha_operacion', 'compra_venta', 'divisa_inicial',
                    'monto_inicial', 'tasa_cambio', 'divisa_final', 'monto_final', 'codigo_trader', 'nombre_producto', 'fecha_vencimiento')
        status, cambios = envio.envio_murex(df_columnas)
        return status, cambios
    status = "400"
    cambios = {"Error":"El formato no Corresponde"}
    return status, cambios

#------------------------------------------------------------------------------------

def carga_contraparte(archivo):
    """carga_contraparte"""
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    num_columnas = len(d_f.keys())
    if num_columnas != 30:
        status = "400"
        cambios = {"Error":"El formato no Corresponde"}
        return status, cambios
    columnas = ['M_DSP_LBL', 'M_DESC','M_EJECUTIVO','M_JEFE_GRUPO','M_DIVISION','M_ENABLE_OPT','M_ENABLE_FWD','M_SUIT_RISK']
    df_columnas = d_f[d_f.columns.intersection(columnas)]
    df_columnas.columns = ('nombre_cliente', 'rut_cliente','nombre_ejecutivo','nombre_jefe_grupo','nombre_segmento','habilitado_opt','habilitado_fwd','riesgo')
    df_columnas[['habilitado_opt','habilitado_fwd']] = df_columnas[['habilitado_opt','habilitado_fwd']].fillna('N')
    df_columnas["riesgo"] = df_columnas["riesgo"].replace(0,3)
    df_columnas[['nombre_cliente', 'rut_cliente','nombre_ejecutivo','nombre_jefe_grupo','nombre_segmento','habilitado_opt','habilitado_fwd']] = df_columnas[['nombre_cliente', 'rut_cliente','nombre_ejecutivo','nombre_jefe_grupo','nombre_segmento','habilitado_opt','habilitado_fwd']].astype("string")
    status, cambios = envio.envio_contraparte(df_columnas)
    return status, cambios

#------------------------------------------------------------------------------------
def carga_confirmaciones(archivo):
    """carga_confirmaciones"""
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    df_columnas1 = list(d_f.columns)

    columnas1 = ['G.ID','TRN.TIME','CONTRATA POR ','MEDIO DE CONFIRMACION ', 'COUNTERPART','CONTRAPARTE'] #MUREX
    columnas2 = ['Deal No.','RESPUESTA DE CONTRAPARTE','MEDIO DE SUSCRIPCION','MEDIO DE CONFIRMACION','CONFIRMACION ENVIADA', 'Ext Lentity', 'TIPO CLIENTE'] #FINDUR
    n_coincidencias1 = len(set(df_columnas1) & set(columnas1))
    # print(f"numero de coincidencias \n\n\n {n_coincidencias1} \n\n\n")
    if n_coincidencias1 == 6:
        d_f2 = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),engine='openpyxl', sheet_name="SWAP")
        os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
        df_columnas2 = list(d_f2.columns)
        n_coincidencias2 = len(set(df_columnas2) & set(columnas2))
        # print(f"numero de coincidencias \n\n\n {n_coincidencias2} \n\n\n")
        if n_coincidencias2 == 7:
            df_columnas = d_f[d_f.columns.intersection(columnas1)]
            df_columnas2 = d_f2[d_f2.columns.intersection(columnas2)]
            df_columnas.columns = ('rut_cliente', 'num_operacion', 'status_operacion', 'tipo_cliente', 'medio_suscripcion', 'medio_confirmacion')
            df_columnas["envio_confirmacion"] = ""

            df_columnas2.columns = ('num_operacion', 'rut_cliente', 'tipo_cliente', 'medio_confirmacion', 'envio_confirmacion', 'status_operacion',
                                    'medio_suscripcion')

            df_columnas = df_columnas.reindex(columns=['num_operacion', 'status_operacion', 'medio_suscripcion',
                                                         'medio_confirmacion', 'envio_confirmacion', 'rut_cliente', 'tipo_cliente'])

            df_columnas2 = df_columnas2.reindex(columns=['num_operacion', 'status_operacion', 'medio_suscripcion',
                                                         'medio_confirmacion', 'envio_confirmacion', 'rut_cliente', 'tipo_cliente'])
            operaciones = pd.concat([df_columnas, df_columnas2])
            status, cambios = envio.envio_confirmaciones(operaciones)
            return status, cambios
        status = "400"
        cambios = {"Error":"El formato no Corresponde"}
        return status, cambios
    status = "400"
    cambios = {"Error":"El formato no Corresponde"}
    return status, cambios
#------------------------------------------------------------------------------------

def carga_rco(archivo): #finalizado
    """carga_rco"""
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    num_columnas = len(d_f.keys())
    if num_columnas != 24:
        status = "400"
        cambios = {"Error":"El formato no Corresponde"}
        return status, cambios
    columnas = ['Contrato', 'MTM_CLP']
    df_columnas = d_f[d_f.columns.intersection(columnas)]
    df_columnas.columns = ('num_operacion', 'valor_mtm')
    status, cambios = envio.envio_rco(df_columnas)
    return status, cambios
#------------------------------------------------------------------------------------


def carga_base_full(archivo): #finalizado
    """carga_base_full"""
    print("CARGA FULL 1")
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    print("2")
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    lista_columnas = list(d_f.columns)
    columnas = ["Origen Op", "N Oper", "Cliente", "Rut", "Fecha", "Vecha Vcto", "Tipo Fw", "Moneda 1", "Monto 1",
            "Precio", "Moneda 2", "Monto 2", "Operador", "Tipo"]
    n_coincidencias = len(set(lista_columnas) & set(columnas)) ### campos base_full == 15

    if n_coincidencias == 14:
        df_columnas = d_f[d_f.columns.intersection(columnas)]
        df_columnas.columns = ('nombre_origen', 'num_operacion', 'nombre_cliente', 'rut_cliente', 'fecha_operacion', 'fecha_vencimiento',
                            'compra_venta', 'divisa_inicial', 'monto_inicial', 'tasa_cambio', 'divisa_final', 'monto_final',
                            'codigo_trader', 'nombre_producto')
        df_columnas[['nombre_origen', 'nombre_cliente', 'rut_cliente', 'compra_venta', 'divisa_inicial', 'divisa_final', 'codigo_trader', 'nombre_producto']] = df_columnas[['nombre_origen', 'nombre_cliente', 'rut_cliente', 'compra_venta', 'divisa_inicial', 'divisa_final', 'codigo_trader', 'nombre_producto']].astype("string")
        df_columnas["correlativo"] = None
        df_columnas = df_columnas.reindex(columns=['nombre_origen', 'num_operacion', 'correlativo','nombre_cliente', 'rut_cliente', 'fecha_operacion', 'fecha_vencimiento',
                            'compra_venta', 'divisa_inicial', 'monto_inicial', 'tasa_cambio', 'divisa_final', 'monto_final',
                            'codigo_trader', 'nombre_producto'])
        df_columnas["operacion_vencida"] = 0
        df_columnas["id_estado"] = 1

        status, cambios = envio.envio_base_full(df_columnas)
        return status, cambios
    status = "400"
    cambios = {"Error":"El formato no Corresponde"}
    return status, cambios



#------------------------------------------------------------------------------------


def carga_envio_contratos(archivo): #finalizado
    """carga_envio_contratos"""
    print("carga_envio_contratos")
    archivo.save(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    d_f = pd.read_excel(os.path.join(ROOT_DIR_LECTURA, archivo.filename),
                engine='openpyxl')
    os.remove(os.path.join(ROOT_DIR_LECTURA, archivo.filename))
    lista_columnas = list(d_f.columns)

    columnas = ["Origen Op", "N Oper", "Cliente", "Rut", "Fecha", "Vecha Vcto", "Tipo Fw", "Moneda 1", "Monto 1", "Precios", "Moneda 2",
    "Monto 2", "Medio", "ENVIO A CLIENTE", "RECEPCION CONTRATO FIRMADO", "Folio Contraparte", "Observaciones", "Respuesta",
    "KIT", "Tipo_Producto"]
    n_coincidencias = len(set(lista_columnas) & set(columnas)) ### campos base_full == 15

    if n_coincidencias == 20: ##20 de envio contratos
        # print("\n\n\n\n\n si corresponde al formato")
        df_columnas = d_f[d_f.columns.intersection(columnas)]
        df_columnas.columns = ('nombre_origen', 'num_operacion', 'nombre_cliente', 'rut_cliente', 'fecha_operacion', 'fecha_vencimiento',
                            'compra_venta', 'divisa_inicial', 'monto_inicial', 'tasa_cambio', 'divisa_final', 'monto_final',
                            'nombre_medio', 'fecha_envio', 'fecha_recepcion', 'folio_contraparte', 'observacion', 'status_operacion',
                            'riesgo', 'nombre_producto')

        df_columnas[['nombre_origen', 'nombre_cliente', 'rut_cliente', 'compra_venta', 'divisa_inicial', 'divisa_final', 'nombre_producto', 'folio_contraparte']] = df_columnas[['nombre_origen', 'nombre_cliente', 'rut_cliente', 'compra_venta', 'divisa_inicial', 'divisa_final', 'nombre_producto', 'folio_contraparte']].astype("string")

        df_columnas["correlativo"] = None
        df_columnas = df_columnas.reindex(columns=['nombre_origen', 'num_operacion', 'correlativo', 'nombre_cliente', 'rut_cliente', 'fecha_operacion', 'fecha_vencimiento',
                            'compra_venta', 'divisa_inicial', 'monto_inicial', 'tasa_cambio', 'divisa_final', 'monto_final',
                            'nombre_medio', 'fecha_envio', 'fecha_recepcion', 'folio_contraparte', 'observacion', 'status_operacion',
                            'riesgo', 'nombre_producto'])
        df_columnas["operacion_vencida"] = 0

        status, cambios = envio.envio_envio_contratos(df_columnas)
        return status, cambios
    status = "400"
    cambios = {"Error":"El formato no Corresponde"}
    return status, cambios