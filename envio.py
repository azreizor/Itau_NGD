import os, pathlib, pyodbc, math
import api_gestor
import time
import pandas as pd, numpy as np, xlsxwriter
from flask import redirect, url_for
import config
from datetime import datetime
from definitions import ROOT_DIR_REPORTE

config = config.traer_config()

def envio_findur(dataframe): #finalizado
    """envio de inputs findur"""
    inicio = time.time() ## seg  1.236 - 1.2959876 // con el nuevo formato seg 1.14113 - 1.17
    cambios = { "Clientes Nuevos":0,
                "Clientes Actualizados":0,
                "Divisas Nuevas":0,
                "Productos Nuevos":0,
                "Traders Nuevos":0,
                "Operaciones Nuevas":0,
                "Operaciones Actualizadas":0,
                "Clientes Bloqueados":0}

    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).replace(" - LE", ""))

    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].fillna('-')
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].apply(lambda x : str(x).strip().upper())
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].replace({'-':None})

    dataframe["nombre_producto"] = dataframe["nombre_producto"].fillna('-')
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : str(x).strip())
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'-':None})

    dataframe["codigo_trader"] = dataframe["codigo_trader"].fillna('-')
    dataframe["codigo_trader"] = dataframe["codigo_trader"].apply(lambda x : str(x).strip().upper())
    dataframe["codigo_trader"] = dataframe["codigo_trader"].replace({'-':None})

    dataframe["compra_venta"] = dataframe["compra_venta"].fillna('-')
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : str(x).strip())
    dataframe["compra_venta"] = dataframe["compra_venta"].replace({'-':None})

    operaciones_no_duplicadas = dataframe.drop_duplicates(["num_operacion"], keep='first') #elimina los traders duplicados
    operaciones_no_duplicadas = operaciones_no_duplicadas.dropna(subset=['num_operacion']) #borra los NULLS
    operaciones_no_duplicadas = operaciones_no_duplicadas.reset_index(drop=True)

    divisas = traer_divisas() #registros base de datos
    divisas_no_duplicadas = dataframe.drop_duplicates(["divisa_inicial"], keep='first') #elimina los clientes duplicados
    divisas_no_duplicadas = divisas_no_duplicadas.reset_index(drop=True)

    productos = traer_productos() #registros base de datos
    productos_no_duplicados = dataframe.drop_duplicates(["nombre_producto"], keep='first') #elimina los clientes duplicados
    productos_no_duplicados = productos_no_duplicados.reset_index(drop=True)

    clientes = traer_clientes() #registros base de datos
    clientes_no_duplicados = dataframe.drop_duplicates(["rut_cliente"], keep='first') #elimina los clientes duplicados
    clientes_no_duplicados = clientes_no_duplicados.reset_index(drop=True)

    traders = traer_traders() #registros base de datos
    traders_no_duplicados = dataframe.dropna(subset=['codigo_trader'])
    traders_no_duplicados = traders_no_duplicados.drop_duplicates(["codigo_trader"], keep='first') #elimina los traders duplicados
    traders_no_duplicados = traders_no_duplicados.reset_index(drop=True)

    operaciones = traer_operaciones() #registros base de datos
    operaciones_no_duplicadas["fecha_operacion"] = operaciones_no_duplicadas["fecha_operacion"].dt.date
    operaciones_no_duplicadas["fecha_vencimiento"] = operaciones_no_duplicadas["fecha_vencimiento"].dt.date

    print("validaciones listas, vamos al TRY")

    try:
        conn = pyodbc.connect(config)
        print("Procede al Envio Findur")
        cursor = conn.cursor()
        cursor.fast_executemany = True

        ## -------------------------------------ingreso de divisas al sistema-----------------------------
        print(f"largo de las divisas es {len(divisas_no_duplicadas)}")
        if len(divisas)==0:
            print("insert directo, no requiere filtrar por divisas nuevas, ya que no hay registros")
            cambios["Divisas Nuevas"] = len(divisas_no_duplicadas)
            query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
            cursor.executemany(query, divisas_no_duplicadas[["divisa_inicial"]].values.tolist())
        else:
            print("pregunta por divisas que no esten en el sistema")
            divisas_nuevas = divisas_no_duplicadas[~divisas_no_duplicadas["divisa_inicial"].isin(divisas["codigo_divisa"])]
            if len(divisas_nuevas)>0: #significa que existen clientes ingresar
                cambios["Divisas Nuevas"] = len(divisas_nuevas)
                print(f"numero de divisas nuevas: {len(divisas_nuevas)}")
                query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
                cursor.executemany(query, divisas_nuevas[["divisa_inicial"]].values.tolist())
            else:
                print("no se encontraron divisas nuevas para ingresar")
        cursor.commit()
        print("saliendo de las devisas")
        ## -------------------------------------ingreso de divisas al sistema-----------------------------

        ## -------------------------------------ingreso de productos al sistema-----------------------------
        print(f"largo de las productos es {len(productos_no_duplicados)}")
        print("preguntara por productos")
        if len(productos)==0:
            print("insert directo, no requiere filtrar por productos nuevos, ya que no hay registros")
            cambios["Productos Nuevos"] = len(productos_no_duplicados)
            query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, 1);"""
            cursor.executemany(query, productos_no_duplicados[["nombre_producto"]].values.tolist())
        else:
            print("pregunta por productos que no estan en el sistema, (son nuevos)")
            productos_nuevos = productos_no_duplicados[~productos_no_duplicados["nombre_producto"].isin(productos["nombre_producto"])] #clientes nuevos
            if len(productos_nuevos)>0: #significa que existen clientes ingresar
                cambios["Productos Nuevos"] = len(productos_nuevos)
                print(f"numero de productos nuevos: {len(productos_nuevos)}")
                query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, 1);"""
                cursor.executemany(query, productos_nuevos[["nombre_producto"]].values.tolist())
            else:
                print("no se encontraron productos nuevos para ingresar")
        cursor.commit()
        print("saliendo de los productos")
        ## -------------------------------------ingreso de productos al sistema-----------------------------

        ## -------------------------------------ingreso de clientes al sistema-----------------------------
        print(f"largo de las clientes es {len(clientes_no_duplicados)}")
        print("preguntara por clientes")
        if len(clientes)==0:
            print("insert directo, no requiere filtrar por clientes nuevos, ya que no hay registros")
            cambios["Clientes Nuevos"] = len(clientes_no_duplicados)
            query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
            cursor.executemany(query, clientes_no_duplicados[["rut_cliente","nombre_cliente"]].values.tolist())

        else:
            print("pregunta por cliente que no estan en el sistema, (son nuevos)")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos
            if len(clientes_nuevos)>0: #significa que existen clientes ingresar
                cambios["Clientes Nuevos"] = len(clientes_nuevos)
                print(f"numero de clientes nuevos: {len(clientes_nuevos)}")
                query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
                cursor.executemany(query, clientes_nuevos[["rut_cliente","nombre_cliente"]].values.tolist())

            clientes_para_actualizar = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes_nuevos["rut_cliente"])] #clientes nuevos
            if len(clientes_para_actualizar)>0: #significa que existen clientes para actualizar
                cambios["Clientes Actualizados"] = len(clientes_para_actualizar)
                print(f"clientes para actualizar: {len(clientes_para_actualizar)}")
                query = """UPDATE dbo.cliente SET nombre_cliente = ? WHERE rut_cliente=?;"""
                cursor.executemany(query, clientes_para_actualizar[["nombre_cliente","rut_cliente"]].values.tolist())

        cursor.commit()
        print("saliendo de los clientes")
        ## -------------------------------------ingreso de clientes al sistema-----------------------------

        ## -------------------------------------ingreso de traders al sistema-----------------------------
        ### no requiere actualizar porque solo se inserta el codigo_trader
        print(f"largo de las traders es {len(traders_no_duplicados)}")
        # print(traders_no_duplicados)
        if len(traders)==0:
            print("insert directo, no requiere filtrar por traders nuevos, ya que no hay registros")
            cambios["Traders Nuevos"] = len(traders_no_duplicados)
            query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
            cursor.executemany(query, traders_no_duplicados[["codigo_trader"]].values.tolist())

        else:
            print("pregunta por traders que no estan en el sistema, (son nuevos)")
            traders_nuevos = traders_no_duplicados[~traders_no_duplicados["codigo_trader"].isin(traders["codigo_trader"])] #traders nuevos
            # print(traders_nuevos)
            print(f"numero de traders nuevos: {len(traders_nuevos)}")
            cambios["Traders Nuevos"] = len(traders_nuevos)
            if len(traders_nuevos)>0:
                query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
                cursor.executemany(query, traders_nuevos[["codigo_trader"]].values.tolist())
        cursor.commit()
        print("saliendo de los traders")
        ## -------------------------------------ingreso de traders al sistema-----------------------------

        ## -------------------------------------ingreso de operaciones al sistema-----------------------------
        print("COMIENZAN LOS JOINS")
        divisas2 = traer_divisas() #registros base de datos
        productos_findur = traer_productos()
        ###----id_tipo_producto------------
        join_idproducto = pd.merge(productos_findur , operaciones_no_duplicadas, on=['nombre_producto'], how="left")
        join_iddivisainicial = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_inicial'], how="left")
        operaciones_no_duplicadas["id_producto"] = join_idproducto["id_producto"]
        operaciones_no_duplicadas["id_divisa_inicial"] = join_iddivisainicial["id_divisa"]
        ###----id_tipo_producto------------

        operaciones_no_duplicadas['fecha_operacion'] = pd.to_datetime(operaciones_no_duplicadas['fecha_operacion']).dt.date
        operaciones_no_duplicadas['fecha_vencimiento'] = pd.to_datetime(operaciones_no_duplicadas['fecha_vencimiento']).dt.date

        operaciones_no_duplicadas = operaciones_no_duplicadas.fillna("nulo")
        operaciones_no_duplicadas = operaciones_no_duplicadas.replace({"nulo" : None})
        print("TERMINAN LOS JOINS")
        #--------------------------------------------------------------------------------------------
        # print(operaciones_no_duplicadas)
        print(f"largo de las operaciones es {len(operaciones_no_duplicadas)}")
        if len(operaciones)==0:
            print("insert directo, no requiere filtrar por operaciones nuevas, ya que no hay registros")
            cambios["Operaciones Nuevas"] = len(operaciones_no_duplicadas)
            query = """
            INSERT INTO dbo.operacion (num_operacion, id_producto, fecha_operacion, fecha_vencimiento,
            rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, compra_venta, codigo_trader, id_origen, operacion_vencida, id_estado)
            values (?,?,?,?,?,?,?,?,?,?,1,0,1);
            """
            cursor.executemany(query, operaciones_no_duplicadas[["num_operacion", "id_producto", "fecha_operacion", "fecha_vencimiento",
            "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "compra_venta", "codigo_trader"]].values.tolist())

        else:
            print("pregunta por operaciones que no estan en el sistema, (son nuevas)")

            operaciones_nuevas = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones["num_operacion"])] #operaciones nuevas
            if len(operaciones_nuevas)>0: #significa que existen clientes ingresar
                print(f"numero de operaciones nuevas: {len(operaciones_nuevas)}")
                print(f"{operaciones_nuevas}")
                cambios["Operaciones Nuevas"] = len(operaciones_nuevas)
                query = """
                INSERT INTO dbo.operacion (num_operacion, id_producto, fecha_operacion, fecha_vencimiento,
                rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, compra_venta, codigo_trader, id_origen, operacion_vencida, id_estado)
                values (?,?,?,?,?,?,?,?,?,?,1,0,1);
                """
                cursor.executemany(query, operaciones_nuevas[["num_operacion", "id_producto", "fecha_operacion", "fecha_vencimiento",
                "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "compra_venta", "codigo_trader"]].values.tolist())

            operaciones_para_actualizar = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones_nuevas["num_operacion"])] #clientes nuevos
            if len(operaciones_para_actualizar)>0: #significa que existen clientes ingresar
                print(f"numero de operaciones para actualizar: {len(operaciones_para_actualizar)}")
                cambios["Operaciones Actualizadas"] = len(operaciones_para_actualizar)
                query = """UPDATE operacion SET id_producto = ?, fecha_operacion = ?, fecha_vencimiento = ?, rut_cliente = ?,
                id_divisa_inicial = ?, monto_inicial = ?, tasa_cambio = ?, compra_venta = ?, codigo_trader = ?, id_origen = 1, id_estado = 1
                WHERE num_operacion = ? ;"""
                cursor.executemany(query, operaciones_para_actualizar[["id_producto", "fecha_operacion", "fecha_vencimiento",
                "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "compra_venta", "codigo_trader", "num_operacion"]].values.tolist())
                print("las operaciones fueron actualizadas")
        cursor.commit()

        cursor.close()
        conn.close()
        print("LANZA VENCIMIENTO DE LAS OPERACIONES")
        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        # api_gestor.api_estado_clientes()
        api_gestor.api_actualizar_estado_operaciones()
        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        print("FINALIZA VENCIMIENTO DE LAS OPERACIONES")
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        cursor.close()
        conn.close()
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

#-----------------------------------------------------------------------------------------------------------------------------

def envio_murex(dataframe): #finalizado
    """envio de inputs murex"""
    inicio = time.time()
    cambios = { "Clientes Nuevos":0,
                "Clientes Actualizados":0,
                "Divisas Nuevas":0,
                "Productos Nuevos":0,
                "Traders Nuevos":0,
                "Operaciones Nuevas":0,
                "Operaciones Actualizadas":0}

    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).strip().upper())

    dataframe["nombre_producto"] = dataframe["nombre_producto"].fillna('-')
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : str(x).strip())
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'-':None})

    dataframe["monto_inicial"] = dataframe["monto_inicial"].apply(lambda x : str(x).strip())
    dataframe["monto_final"] = dataframe["monto_final"].apply(lambda x : str(x).strip())
    dataframe["tasa_cambio"] = dataframe["tasa_cambio"].apply(lambda x : str(x).strip())

    dataframe["monto_inicial"] = dataframe["monto_inicial"].fillna(0)
    dataframe["monto_final"] = dataframe["monto_final"].fillna(0)
    dataframe["tasa_cambio"] = dataframe["tasa_cambio"].fillna(0)

    dataframe["monto_inicial"] = dataframe["monto_inicial"].astype("float")
    dataframe["monto_final"] = dataframe["monto_final"].astype("float")
    dataframe["tasa_cambio"] = dataframe["tasa_cambio"].astype("float")

    dataframe["codigo_trader"] = dataframe["codigo_trader"].fillna('-')
    dataframe["codigo_trader"] = dataframe["codigo_trader"].apply(lambda x : str(x).strip())
    dataframe["codigo_trader"] = dataframe["codigo_trader"].replace({'-':None})

    dataframe["compra_venta"] = dataframe["compra_venta"].fillna('-')
    dataframe["compra_venta"] = dataframe["compra_venta"].replace({'-':None})

    # print(dataframe["divisa_inicial"])

    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].fillna('-')
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].apply(lambda x : str(x).strip().upper())
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].replace({'-':None})
    dataframe["divisa_final"] = dataframe["divisa_final"].fillna('-')
    dataframe["divisa_final"] = dataframe["divisa_final"].apply(lambda x : str(x).strip().upper())
    dataframe["divisa_final"] = dataframe["divisa_final"].replace({'-':None})

    # print(dataframe["divisa_inicial"])

    divisas = traer_divisas() #registros base de datos
    # divisas_iniciales = pd.DataFrame(columns=["divisa_inicial"])
    # divisas_finales = pd.DataFrame(columns=["divisa_final"])
    divisas_totales = pd.DataFrame(columns=["divisas"])
    divisas_totales["divisas"] = pd.concat([dataframe["divisa_inicial"], dataframe["divisa_final"]], axis=0, ignore_index=False)
    # divisas_iniciales = dataframe.drop_duplicates(["divisa_inicial"], keep='first') #elimina los clientes duplicados
    # divisas_finales = dataframe.drop_duplicates(["divisa_final"], keep='first') #elimina los clientes duplicados
    # divisas_totales = pd.DataFrame(columns=["divisas"])
    # divisas_totales["divisas"] = pd.concat([divisas_iniciales["divisa_inicial"], divisas_finales["divisa_final"]], axis=0, ignore_index=False)

    # print(divisas_totales.dtypes)
    # print(divisas_totales)

    divisas_totales = divisas_totales.dropna(subset=['divisas'])
    divisas_totales = divisas_totales.drop_duplicates(["divisas"], keep='first') #elimina los clientes duplicados
    divisas_totales = divisas_totales.reset_index(drop=True)

    productos = traer_productos() #registros base de datos
    productos_no_duplicados = dataframe.dropna(subset=['nombre_producto'])
    productos_no_duplicados = productos_no_duplicados.drop_duplicates(["nombre_producto"], keep='first') #elimina los clientes duplicados
    productos_no_duplicados = productos_no_duplicados.reset_index(drop=True)

    clientes = traer_clientes() #registros base de datos
    clientes_no_duplicados = dataframe.drop_duplicates(["rut_cliente"], keep='first') #elimina los clientes duplicados
    clientes_no_duplicados = clientes_no_duplicados.reset_index(drop=True)

    traders = traer_traders() #registros base de datos
    traders_no_duplicados = dataframe.dropna(subset=['codigo_trader'])
    traders_no_duplicados = traders_no_duplicados.drop_duplicates(["codigo_trader"], keep='first') #elimina los traders duplicados
    traders_no_duplicados = traders_no_duplicados.reset_index(drop=True)

    operaciones = traer_operaciones() #registros base de datos
    operaciones_no_duplicadas = dataframe.drop_duplicates(["num_operacion"], keep='first') #elimina los traders duplicados
    operaciones_no_duplicadas = operaciones_no_duplicadas.dropna(subset=['num_operacion']) #borra los NULLS
    operaciones_no_duplicadas = operaciones_no_duplicadas.reset_index(drop=True)


    try:
        conn = pyodbc.connect(config)
        print("Procede al Envio Murex")
        cursor = conn.cursor()
        cursor.fast_executemany = True

        ## -------------------------------------ingreso de divisas al sistema-----------------------------
        if len(divisas)==0:
            print("insert directo, no requiere filtrar por divisas nuevas, ya que no hay registros")
            cambios["Divisas Nuevas"] = len(divisas_totales)
            query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
            cursor.executemany(query, divisas_totales[["divisas"]].values.tolist())
        else:
            print("pregunta por divisas que no esten en el sistema")
            divisas_nuevas = divisas_totales[~divisas_totales["divisas"].isin(divisas["codigo_divisa"])]
            if len(divisas_nuevas)>0: #significa que existen clientes ingresar
                cambios["Divisas Nuevas"] = len(divisas_nuevas)
                print(f"numero de divisas nuevas: {len(divisas_nuevas)}")
                query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
                cursor.executemany(query, divisas_nuevas[["divisas"]].values.tolist())
            else:
                print("no se encontraron divisas nuevas para ingresar")
        cursor.commit()
        ## -------------------------------------ingreso de divisas al sistema-----------------------------

        ## -------------------------------------ingreso de productos al sistema-----------------------------
        if len(productos)==0:
            print("insert directo, no requiere filtrar por productos nuevos, ya que no hay registros")
            cambios["Productos Nuevos"] = len(productos_no_duplicados)
            print(productos_no_duplicados)
            print(productos_no_duplicados["nombre_producto"])
            query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, 2);"""
            cursor.executemany(query, productos_no_duplicados[["nombre_producto"]].values.tolist())
        else:
            print("pregunta por productos que no estan en el sistema, (son nuevos)")
            productos_nuevos = productos_no_duplicados[~productos_no_duplicados["nombre_producto"].isin(productos["nombre_producto"])] #clientes nuevos
            if len(productos_nuevos)>0: #significa que existen clientes ingresar
                cambios["Productos Nuevos"] = len(productos_nuevos)
                print(f"numero de productos nuevos: {len(productos_nuevos)}")
                query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, 2);"""
                cursor.executemany(query, productos_nuevos[["nombre_producto"]].values.tolist())
            else:
                print("no se encontraron productos nuevos para ingresar")
        cursor.commit()
        ## -------------------------------------ingreso de productos al sistema-----------------------------

        ## -------------------------------------ingreso de clientes al sistema-----------------------------
        if len(clientes)==0:
            print("insert directo, no requiere filtrar por clientes nuevos, ya que no hay registros")
            cambios["Clientes Nuevos"] = len(clientes_no_duplicados)
            query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
            cursor.executemany(query, clientes_no_duplicados[["rut_cliente","nombre_cliente"]].values.tolist())

        else:
            print("pregunta por cliente que no estan en el sistema, (son nuevos)")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos
            if len(clientes_nuevos)>0: #significa que existen clientes ingresar
                cambios["Clientes Nuevos"] = len(clientes_nuevos)
                print(f"numero de clientes nuevos: {len(clientes_nuevos)}")
                query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
                cursor.executemany(query, clientes_nuevos[["rut_cliente","nombre_cliente"]].values.tolist())

            clientes_para_actualizar = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes_nuevos["rut_cliente"])] #clientes nuevos
            if len(clientes_para_actualizar)>0: #significa que existen clientes para actualizar
                cambios["Clientes Actualizados"] = len(clientes_para_actualizar)
                print(f"clientes para actualizar: {len(clientes_para_actualizar)}")
                query = """UPDATE cliente SET nombre_cliente = ? WHERE rut_cliente=?;"""
                cursor.executemany(query, clientes_para_actualizar[["nombre_cliente","rut_cliente"]].values.tolist())
        cursor.commit()
        # -------------------------------------ingreso de clientes al sistema-----------------------------

        # -------------------------------------ingreso de traders al sistema-----------------------------
        ### no requiere actualizar porque solo se inserta el codigo_trader
        if len(traders)==0:
            print("insert directo, no requiere filtrar por traders nuevos, ya que no hay registros")
            cambios["Traders Nuevos"] = len(traders_no_duplicados)
            query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
            cursor.executemany(query, traders_no_duplicados[["codigo_trader"]].values.tolist())
        else:
            print("pregunta por traders que no estan en el sistema, (son nuevos)")
            traders_nuevos = traders_no_duplicados[~traders_no_duplicados["codigo_trader"].isin(traders["codigo_trader"])] #traders nuevos
            # print(traders_nuevos)
            print(f"numero de traders nuevos: {len(traders_nuevos)}")
            cambios["Traders Nuevos"] = len(traders_nuevos)
            if len(traders_nuevos)>0:
                query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
                cursor.executemany(query, traders_nuevos[["codigo_trader"]].values.tolist())
        cursor.commit()
        # -------------------------------------ingreso de traders al sistema-----------------------------

        # -------------------------------------ingreso de operaciones al sistema-----------------------------
        ## -------------------------------------ingreso de operaciones al sistema-----------------------------

        divisas2 = traer_divisas() #registros base de datos
        productos_murex = traer_productos()

        ###----id_tipo_producto------------
        join_idproducto = pd.merge(productos_murex , operaciones_no_duplicadas, on=['nombre_producto'], how="right")
        join_iddivisainicial = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_inicial'], how="right")
        join_iddivisafinal = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_final'], how="right")

        operaciones_no_duplicadas["id_producto"] = join_idproducto["id_producto"]
        operaciones_no_duplicadas["id_divisa_inicial"] = join_iddivisainicial["id_divisa"]
        operaciones_no_duplicadas["id_divisa_final"] = join_iddivisafinal["id_divisa"]
        ###----id_tipo_producto------------

        operaciones_no_duplicadas['fecha_operacion'] = pd.to_datetime(operaciones_no_duplicadas['fecha_operacion']).dt.date
        operaciones_no_duplicadas['fecha_vencimiento'] = pd.to_datetime(operaciones_no_duplicadas['fecha_vencimiento']).dt.date


        operaciones_no_duplicadas = operaciones_no_duplicadas.fillna("nulo")
        operaciones_no_duplicadas = operaciones_no_duplicadas.replace({"nulo" : None})
        #---------------------------------------------------------------------------------------------------

        if len(operaciones)==0:
            print("insert directo, no requiere filtrar por operaciones nuevas, ya que no hay registros")
            cambios["Operaciones Nuevas"] = len(operaciones_no_duplicadas)

            query = """
            INSERT INTO dbo.operacion (num_operacion, id_producto, fecha_operacion, fecha_vencimiento,
            rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final, monto_final, compra_venta, codigo_trader,
            id_origen, operacion_vencida, id_estado) values (?,?,?,?,?,?,?,?,?,?,?,?,2,0,1);
            """

            cursor.executemany(query, operaciones_no_duplicadas[["num_operacion", "id_producto", "fecha_operacion", "fecha_vencimiento",
            "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta",
            "codigo_trader"]].values.tolist())

        else:
            print("pregunta por operaciones que no estan en el sistema, (son nuevas)")

            operaciones_nuevas = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones["num_operacion"])] #operaciones nuevas
            if len(operaciones_nuevas)>0: #significa que existen clientes ingresar
                print(f"numero de operaciones nuevas: {len(operaciones_nuevas)}")

                cambios["Operaciones Nuevas"] = len(operaciones_nuevas)
                query = """
                INSERT INTO dbo.operacion (num_operacion, id_producto, fecha_operacion, fecha_vencimiento,
                rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final, monto_final, compra_venta, codigo_trader,
                id_origen, operacion_vencida, id_estado) values (?,?,?,?,?,?,?,?,?,?,?,?,2,0,1);
                """
                cursor.executemany(query, operaciones_nuevas[["num_operacion", "id_producto", "fecha_operacion", "fecha_vencimiento",
                "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta",
                "codigo_trader"]].values.tolist())

            operaciones_para_actualizar = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones_nuevas["num_operacion"])] #clientes nuevos
            if len(operaciones_para_actualizar)>0: #significa que existen clientes ingresar
                print(f"numero de operaciones para actualizar: {len(operaciones_para_actualizar)}")
                cambios["Operaciones Actualizadas"] = len(operaciones_para_actualizar)
                query = """UPDATE operacion SET id_producto = ?, rut_cliente = ?, id_divisa_inicial = ?, monto_inicial = ?,
                tasa_cambio = ?, id_divisa_final = ?, monto_final = ?, compra_venta = ?, codigo_trader = ?
                WHERE num_operacion = ? ;""" #12  + 2
                print("antes del update")

                cursor.executemany(query, operaciones_para_actualizar[["id_producto", "rut_cliente", "id_divisa_inicial", "monto_inicial",
                    "tasa_cambio", "id_divisa_final", "monto_final","compra_venta", "codigo_trader", "num_operacion"]].values.tolist()) #12
                # print("las operaciones fueron actualizadas")
                print("despues del update")
        cursor.commit()
        ## -------------------------------------ingreso de operaciones al sistema-----------------------------

        print("LANZA VENCIMIENTO DE LAS OPERACIONES")
        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        # api_gestor.api_estado_clientes()
        api_gestor.api_actualizar_estado_operaciones()
        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        print("FINALIZA VENCIMIENTO DE LAS OPERACIONES")

        cursor.close()
        conn.close()
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

# -------------------------------------------------------------------------------------------------------------------------
def envio_contraparte(dataframe):
    """envio de inputs contraparte"""
    inicio = time.time()
    cambios = {"Equipos Nuevos":0,
               "Clientes Nuevos":0,
               "Clientes Actualizados":0,
               "Equipos Asignados":0,
               "Equipos Asignados Nuevos":0}

    clientes = traer_clientes() #registros base de datos
    dataframe = dataframe.dropna(subset=['nombre_cliente'])
    dataframe["nombre_segmento"] = dataframe["nombre_segmento"].fillna("")
    clientes_no_duplicados = dataframe.drop_duplicates(["rut_cliente"], keep='first') #elimina los clientes duplicados
    clientes_no_duplicados = clientes_no_duplicados.dropna(subset=['rut_cliente']) #borra los NULLS
    clientes_no_duplicados = clientes_no_duplicados.reset_index(drop=True)

    equipos = traer_equipos() #registros base de datos
    equipos_no_duplicados = dataframe.drop(columns=['nombre_cliente', 'rut_cliente','habilitado_opt','habilitado_fwd','riesgo'])
    equipos_no_duplicados = equipos_no_duplicados.drop_duplicates(['nombre_ejecutivo','nombre_jefe_grupo'], keep='first') #elimina los equipos duplicados
    equipos_no_duplicados = equipos_no_duplicados.dropna(subset=['nombre_ejecutivo','nombre_jefe_grupo']) #borra los NULLS
    equipos_no_duplicados = equipos_no_duplicados.reset_index(drop=True)

    clientes_no_duplicados = clientes_no_duplicados.assign(nombre_cliente = lambda x:(x['nombre_cliente'].replace("'"," ")))
    try:
        conn = pyodbc.connect(config)
        print("Procede al Envio Contraparte")
        cursor = conn.cursor()
        cursor.fast_executemany = True
        ## -------------------------------------ingreso de equipos de trabajo al sistema-----------------------------
        if len(equipos)==0:
            print("insert directo, no requiere filtrar por equipos nuevos, ya que no hay registros")
            print(f"numero de equipos nuevos: {len(equipos)}")
            cambios["Equipos Nuevos"] = len(equipos_no_duplicados)
            query = """INSERT INTO dbo.equipo (nombre_ejecutivo, nombre_jefe_grupo) values (?,?);"""
            cursor.executemany(query, equipos_no_duplicados[["nombre_ejecutivo","nombre_jefe_grupo"]].values.tolist())
            print(f"se ingresaron: {len(equipos)} nuevos")
        else: ##no hace falta actualizar ya que todos los campos estan ingresados (no hay actualizaciones)
            print("pregunta por equipos que no estan en el sistema, (son nuevos)")
            equipos_nuevos = equipos_no_duplicados[~equipos_no_duplicados[['nombre_ejecutivo','nombre_jefe_grupo']].apply("-".join, axis=1).isin(equipos[['nombre_ejecutivo','nombre_jefe_grupo']].apply("-".join, axis=1))] #clientes nuevos
            print(f"cantidad de equipos nuevos = : {len(equipos_nuevos)} nuevos")
            if len(equipos_nuevos)>0: #significa que existen equipos para ingresar
                print(f"se ingresaran: {len(equipos_nuevos)} equipos nuevos")
                cambios["Equipos Nuevos"] = len(equipos_nuevos)
                query = """INSERT INTO dbo.equipo (nombre_ejecutivo, nombre_jefe_grupo) values (?,?);"""
                cursor.executemany(query, equipos_nuevos[["nombre_ejecutivo","nombre_jefe_grupo"]].values.tolist())
            else:
                print("no se ingresan equipos nuevos, ya estan actualizados")
        cursor.commit()
        ## -------------------------------------ingreso de equipos de trabajo al sistema-----------------------------
        ## -------------------------------------ingreso de clientes al sistema-----------------------------

        if len(clientes)==0:
            print("insert directo, no requiere filtrar por clientes nuevos, ya que no hay registros")
            cambios["Clientes Nuevos"] = len(clientes_no_duplicados)
            query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, habilitado_opt, habilitado_fwd, id_riesgo, segmento, cliente_bloqueado) values (?,?,?,?,?,?,0);"""
            cursor.executemany(query, clientes_no_duplicados[["rut_cliente","nombre_cliente","habilitado_opt","habilitado_fwd", "riesgo", "nombre_segmento"]].values.tolist())
        else:
            print("pregunta por cliente que no estan en el sistema, (son nuevos)")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos
            if len(clientes_nuevos)>0: #significa que existen clientes ingresar
                print(f"numero de clientes nuevos: {len(clientes_nuevos)}")
                cambios["Clientes Nuevos"] = len(clientes_nuevos)
                query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, habilitado_opt, habilitado_fwd, id_riesgo, segmento, cliente_bloqueado) values (?,?,?,?,?,?,0);"""
                cursor.executemany(query, clientes_nuevos[["rut_cliente","nombre_cliente","habilitado_opt","habilitado_fwd", "riesgo", "nombre_segmento"]].values.tolist())

            clientes_para_actualizar = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes_nuevos["rut_cliente"])] #clientes nuevos
            if len(clientes_para_actualizar)>0: #significa que existen clientes para actualizar
                print(f"clientes para actualizar: {len(clientes_para_actualizar)}")
                cambios["Clientes Actualizados"] = len(clientes_para_actualizar)
                query = """UPDATE cliente SET habilitado_opt = ?, habilitado_fwd = ?, id_riesgo = ?, segmento = ? WHERE rut_cliente = ?;"""
                cursor.executemany(query, clientes_para_actualizar[["habilitado_opt","habilitado_fwd","riesgo", "nombre_segmento", "rut_cliente"]].values.tolist())
        cursor.commit()
        ## -------------------------------------ingreso de clientes al sistema-----------------------------
        ## -------------------------------------ingreso de clientes_equipo al sistema-----------------------------
        # print("COMIENZO EQUIPO_CLIENTE")
        equipos_bd = traer_equipos() #registros base de datos
        equipos_clientes_bd = traer_equipos_clientes() #ESTA VACIO

        clientes_no_duplicados = clientes_no_duplicados.dropna(subset=['nombre_ejecutivo','nombre_jefe_grupo']) #borra los NULLS
        clientes_no_duplicados = clientes_no_duplicados.reset_index(drop=True)

        equipos_clientes_bd = equipos_clientes_bd.query("activo == 1")

        join3 = pd.merge(clientes_no_duplicados , equipos_bd, on=['nombre_ejecutivo','nombre_jefe_grupo'], how="outer")

        join1_equi_equicli = pd.merge(equipos_bd , equipos_clientes_bd, on=['id_equipo'])

        join2_equicli_cli = pd.merge(join1_equi_equicli , join3, on=['rut_cliente'])

        join2_equicli_cli.columns = ('id_equipo_1','nombre_ejecutivo_1', 'nombre_jefe_grupo_1', 'rut_cliente', 'fecha_activo', 'activo', 'nombre_cliente',
                                    'nombre_ejecutivo_2', 'nombre_jefe_grupo_2', 'nombre_segmento', 'habilitado_opt', 'habilitado_fwd', 'riesgo', 'id_equipo_2')

        distintos = join2_equicli_cli.loc[(join2_equicli_cli['nombre_ejecutivo_1'] != join2_equicli_cli['nombre_ejecutivo_2']) |
                                      (join2_equicli_cli['nombre_jefe_grupo_1'] != join2_equicli_cli['nombre_jefe_grupo_2'])]
        distintos = distintos.drop_duplicates(['rut_cliente'], keep='first') #elimina los equipos duplicados

        # APARTADO PARA LOS CLIENTES QUE NO TIENEN UN EQUIPO ASOCIADO (NO TIENEN NINGUNO ACTIVO O DESACTIVADO)

        join_clientes_equipoclientes = pd.merge(clientes_no_duplicados , equipos_clientes_bd, on=['rut_cliente'], how="left")

        # ------ AQUI SE DEBEN SEPARAR LOS CLIENTES QUE TIENEN O NO UN EQUIPO ASOCIADO -------------
        clientes_sin_equipo = join_clientes_equipoclientes[join_clientes_equipoclientes["id_equipo"].isnull()]

        # HACER EL JOIN DE LOS CLIENTES SIN EQUIPO_CLIENTE (ID_EQUIPO NULO) Y BUSCAR EL ID_EQUIPO QUE CORRESPONDE
        clientes_sin_equipo = clientes_sin_equipo.drop(['id_equipo'], axis=1) # drop la columna id_equipo ya que ahora se completara con el nuevo JOIN
        clientes_sin_equipo_id = pd.merge(clientes_sin_equipo , equipos_bd, on=['nombre_ejecutivo','nombre_jefe_grupo'], how="left")

        ## TOMAS LOS DISTINTOS Y ACTUALIZAS CON LAS COLUMNAS 1 Y 2 PARA DESACTIVAR VIEJOS Y ACTIVAR NUEVOS

        # print("\n\n COMIENZAN LOS IF \n")

        if (len(equipos_clientes_bd)>0):
            print("existen equipos clientes en la base de datos, buscar los nuevos y actualizar los existentes")
            if (len(distintos)>0):
                query1 = """UPDATE equipo_cliente SET activo = 0
                WHERE id_equipo = ? AND rut_cliente = ?;"""
                cursor.executemany(query1, distintos[["id_equipo_1","rut_cliente"]].values.tolist())

                query2 = """INSERT INTO dbo.equipo_cliente (id_equipo, rut_cliente, fecha_activo, activo) values
                (?,?, CAST(GETDATE() AS DATE), 1);"""
                cursor.executemany(query2, distintos[["id_equipo_2","rut_cliente"]].values.tolist())
                cambios["Equipos Asignados"] = len(distintos)
            else:
                print("los clientes ya estan con su equipo activo")

            if(len(clientes_sin_equipo_id)>0):
                print("existen clientes que no tienen ningun equipo asociado")
                query4 = """INSERT INTO dbo.equipo_cliente (id_equipo, rut_cliente, fecha_activo, activo) values
                (?,?, CAST(GETDATE() AS DATE), 1);"""
                cursor.executemany(query4, clientes_sin_equipo_id[["id_equipo","rut_cliente"]].values.tolist())
                cambios["Equipos Asignados Nuevos"] = len(clientes_sin_equipo_id)

        else:
            print("no existen equipos clientes, insertar todos los del dataframe")
            join3 = join3.drop_duplicates(['rut_cliente'], keep='first') #elimina los equipos duplicados
            query = """INSERT INTO dbo.equipo_cliente (id_equipo, rut_cliente, fecha_activo, activo) values
            (?,?, CAST(GETDATE() AS DATE), 1);"""
            cursor.executemany(query, join3[["id_equipo","rut_cliente"]].values.tolist())
            cambios["Equipos Asignados"] = len(join3)

        cursor.commit()
        ## -------------------------------------ingreso de clientes_equipo al sistema-----------------------------
        cursor.close()
        conn.close()
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

# -------------------------------------------------------------------------------------------------------------------------

def envio_confirmaciones(dataframe): #en proceso
    """envio de inputs confirmaciones"""
    inicio = time.time()
    cambios = {"Operaciones Actualizadas":0,
               "Operaciones No Registradas":0,
               "Nuevos Medio Suscripcion":0,
               "Nuevos Medio Confirmacion":0,
               "Clientes Actualizados":0}

    medios = traer_medios()
    medios_suscripcion = medios.query("nombre_campo == 'suscripcion'")
    medios_confirmacion = medios.query("nombre_campo == 'confirmacion'")

    operaciones = traer_operaciones() #registros base de datos
    dataframe = dataframe.dropna(subset=['num_operacion'])
    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).upper())
    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).replace(" - LE", ""))

    dataframe = dataframe.drop_duplicates(["num_operacion"], keep='first').reset_index(drop=True)

    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].fillna('-')
    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].apply(lambda x : str(x).strip().upper())
    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].replace({'-':None})
    dataframe["status_operacion"] = dataframe["status_operacion"].replace({'CONFIRMADA':'CONFIRMADO'})

    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].fillna('-')
    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].apply(lambda x : str(x).strip().upper())
    dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].replace({'-':None})

    dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].fillna('-')
    dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].apply(lambda x : str(x).strip().upper())
    dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].replace({'-':None})

    dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].fillna('NO')
    dataframe["envio_confirmacion"] = dataframe["envio_confirmacion"].apply(lambda x : str(x).strip().upper())

    dataframe["tipo_cliente"] = dataframe["tipo_cliente"].fillna('-')
    dataframe["tipo_cliente"] = dataframe["tipo_cliente"].apply(lambda x : str(x).strip().upper())
    dataframe["tipo_cliente"] = dataframe["tipo_cliente"].replace({'-':None})
    dataframe["tipo_cliente"] = dataframe["tipo_cliente"].apply(lambda x :
        "INSTITUCIONAL" if x in ["BNAC", "BANCO NACIONAL", "BEXT", "BANCO EXTRANJERO"] else x)


    status = dataframe.drop_duplicates(["status_operacion"], keep='first')

    suscripcion = dataframe.dropna(subset=['medio_suscripcion'])
    suscripcion = suscripcion.drop_duplicates(["medio_suscripcion"], keep='first').reset_index(drop=True)

    confirmacion = dataframe.dropna(subset=['medio_confirmacion'])
    confirmacion = confirmacion.drop_duplicates(["medio_confirmacion"], keep='first').reset_index(drop=True)

    clientes = traer_clientes() #registros base de datos
    clientes_no_duplicados = dataframe.drop_duplicates(["rut_cliente"], keep='first') #elimina los clientes duplicados
    clientes_no_duplicados = clientes_no_duplicados.reset_index(drop=True)

    operaciones_no_duplicadas = dataframe

    try:
        conn = pyodbc.connect(config)
        print("Procede al Envio Confirmaciones")
        cursor = conn.cursor()
        cursor.fast_executemany = True

        ## -------------------------------------ingreso de medios al sistema-----------------------------

        if len(medios)==0:
            print("insert directo, no requiere filtrar por medios nuevos, ya que no hay registros")
            cambios["Nuevos Medio Suscripcion"] = len(suscripcion['medio_suscripcion'])

            query = """INSERT INTO dbo.medio (id_campo, nombre_campo, nombre_medio) values (1, 'suscripcion', ?);"""
            cursor.executemany(query, suscripcion[["medio_suscripcion"]].values.tolist())

            cambios["Nuevos Medio Confirmacion"] = len(confirmacion['medio_confirmacion'])
            query2 = """INSERT INTO dbo.medio (id_campo, nombre_campo, nombre_medio) values (2, 'confirmacion', ?);"""
            cursor.executemany(query2, confirmacion[["medio_confirmacion"]].values.tolist())

        else:
            print("busca medios distintos a los ya registrados")
            nuevos_medio_suscripcion = suscripcion[~suscripcion["medio_suscripcion"].isin(medios_suscripcion["nombre_medio"])]
            if len(nuevos_medio_suscripcion)>0:
                cambios["Nuevos Medio Suscripcion"] = len(nuevos_medio_suscripcion['medio_suscripcion'])
                query = """INSERT INTO dbo.medio (id_campo, nombre_campo, nombre_medio) values (1, 'suscripcion', ?);"""
                cursor.executemany(query, nuevos_medio_suscripcion[["medio_suscripcion"]].values.tolist())

            nuevos_medio_confirmacion = confirmacion[~confirmacion["medio_confirmacion"].isin(medios_confirmacion["nombre_medio"])]
            if len(nuevos_medio_confirmacion)>0:
                cambios["Nuevos Medio Confirmacion"] = len(nuevos_medio_confirmacion['medio_confirmacion'])
                query2 = """INSERT INTO dbo.medio (id_campo, nombre_campo, nombre_medio) values (2, 'confirmacion', ?);"""
                cursor.executemany(query2, nuevos_medio_confirmacion[["medio_confirmacion"]].values.tolist())
        cursor.commit()
        ## -------------------------------------ingreso de medios al sistema-----------------------------

        ## -------------------------------------actualizaciones de OPERACIONES al sistema-----------------------------

        estados_bd = traer_estados()
        estados_operacion_bd = estados_bd.query("nombre_campo == 'estado_operacion'")
        estados_confirmacion_bd = estados_bd.query("nombre_campo == 'estado_confirmacion'")
        medios2 = traer_medios()
        medios_suscripcion2 = medios2.query("nombre_campo == 'suscripcion'")
        medios_confirmacion2 = medios2.query("nombre_campo == 'confirmacion'")

        ##----id_tipo_producto------------
        join_idstatus = pd.merge(estados_operacion_bd , operaciones_no_duplicadas, left_on=['nombre_estado'], right_on=['status_operacion'], how="right")
        join_idsuscripcion = pd.merge(medios_suscripcion2 , operaciones_no_duplicadas, left_on=['nombre_medio'], right_on=['medio_suscripcion'], how="right")
        join_idconfirmacion = pd.merge(medios_confirmacion2 , operaciones_no_duplicadas, left_on=['nombre_medio'], right_on=['medio_confirmacion'], how="right")
        join_idenvio = pd.merge(estados_confirmacion_bd , operaciones_no_duplicadas, left_on=['nombre_estado'], right_on=['envio_confirmacion'], how="right")

        operaciones_no_duplicadas["id_estado_operacion"] = join_idstatus["id_estado"]
        operaciones_no_duplicadas["id_estado_operacion"] = operaciones_no_duplicadas["id_estado_operacion"]
        operaciones_no_duplicadas["id_medio_suscripcion"] = join_idsuscripcion["id_medio"]
        operaciones_no_duplicadas["id_medio_suscripcion"] = operaciones_no_duplicadas["id_medio_suscripcion"]
        operaciones_no_duplicadas["id_medio_confirmacion"] = join_idconfirmacion["id_medio"]
        operaciones_no_duplicadas["id_medio_confirmacion"] = operaciones_no_duplicadas["id_medio_confirmacion"]
        operaciones_no_duplicadas["id_estado_confirmacion"] = join_idenvio["id_estado"]
        operaciones_no_duplicadas["id_estado_confirmacion"] = operaciones_no_duplicadas["id_estado_confirmacion"]

        operaciones_no_duplicadas = operaciones_no_duplicadas.fillna("nulo")
        operaciones_no_duplicadas = operaciones_no_duplicadas.replace({"nulo" : None})

        ## -------------------------------------ingreso de clientes al sistema-----------------------------
        print("preguntara por clientes")
        if len(clientes)==0:
            print("no existen clientes para actualizar")
        else:
            print("pregunta por clientes para actualizar")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos

            clientes_para_actualizar = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes_nuevos["rut_cliente"])] #clientes nuevos
            if len(clientes_para_actualizar)>0: #significa que existen clientes para actualizar
                cambios["Clientes Actualizados"] = len(clientes_para_actualizar)
                print(f"clientes para actualizar: {len(clientes_para_actualizar)}")
                query = """UPDATE cliente SET tipo_cliente = ? WHERE rut_cliente=?;"""
                cursor.executemany(query, clientes_para_actualizar[["tipo_cliente","rut_cliente"]].values.tolist())
        cursor.commit()
        ## -------------------------------------ingreso de clientes al sistema-----------------------------

        if len(operaciones)==0:
            print("No existen operaciones para actualizar")
        else:
            print("pregunta por operaciones para actualizar")
            operaciones_no_registradas = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones["num_operacion"])] #operaciones nuevas
            if len(operaciones_no_registradas)>0:
                cambios["Operaciones No Registradas"] = len(operaciones_no_registradas['num_operacion'])

            operaciones_para_actualizar = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones_no_registradas["num_operacion"])] #clientes nuevos
            if len(operaciones_para_actualizar)>0:
                cambios["Operaciones Actualizadas"] = len(operaciones_para_actualizar['num_operacion'])
                query = """UPDATE operacion SET id_estado = ?, id_medio_suscripcion = ?, id_medio_confirmacion = ?, id_envio_confirmacion = ?
                    WHERE num_operacion = ? ;"""
                cursor.executemany(query, operaciones_para_actualizar[["id_estado_operacion", "id_medio_suscripcion",
                    "id_medio_confirmacion", "id_estado_confirmacion", "num_operacion"]].values.tolist())
        cursor.commit()
        print("sale de las operaciones")
        ## -------------------------------------actualizaciones de OPERACIONES al sistema-----------------------------

        cursor.close()
        conn.close()
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

# -------------------------------------------------------------------------


# ------------------------------------------ carga RCO --------------------------------------

def envio_rco(dataframe): #finalizado
    """envio de inputs rco"""
    cambios = {"Operaciones Vencidas":0,
               "Operaciones No Existentes":0,
               "Operaciones Actualizadas":0}

    operaciones = traer_operaciones() #registros base de datos
    dataframe["valor_mtm"] = dataframe["valor_mtm"].fillna(0)
    operaciones_no_duplicadas = dataframe.drop_duplicates(["num_operacion"], keep='first') #elimina los traders duplicados
    operaciones_no_duplicadas = operaciones_no_duplicadas.dropna(subset=['num_operacion']) #borra los NULLS
    operaciones_no_duplicadas = operaciones_no_duplicadas.reset_index(drop=True)

    try:
        conn = pyodbc.connect(config)
        print("Procede al Envio RCO")
        cursor = conn.cursor()
        cursor.fast_executemany = True

        ## -------------------------------------ingreso de operaciones al sistema-----------------------------
        if len(operaciones)==0:
            print("no existen operaciones, no se puede actualizar")
            cambios["Operaciones No Existentes"] = len(operaciones_no_duplicadas)
        else:
            print("pregunta por operaciones que no estan en el sistema, (son nuevas)")

            operaciones_noregistradas = operaciones_no_duplicadas[~operaciones_no_duplicadas["num_operacion"].isin(operaciones["num_operacion"])] #operaciones nuevas
            print(f"operaciones no registradas - {len(operaciones_noregistradas)}")

            operaciones_rco_ensistema = operaciones_no_duplicadas[operaciones_no_duplicadas["num_operacion"].isin(operaciones["num_operacion"])] #operaciones nuevas
            print(f"operaciones RCO en sistema - {len(operaciones_rco_ensistema)}")

            operaciones_vencidas = operaciones[~operaciones["num_operacion"].isin(operaciones_no_duplicadas["num_operacion"])] #operaciones nuevas
            print(f"operaciones vencidas - {len(operaciones_vencidas)}")

            if len(operaciones_vencidas)>0:
                print(f"numero de operaciones vencidas: {len(operaciones_vencidas)}")
                cambios["Operaciones Vencidas"] = len(operaciones_vencidas)
                query = """UPDATE operacion SET operacion_vencida = 1, id_estado = 4 WHERE num_operacion = ?;"""
                cursor.executemany(query, operaciones_vencidas[["num_operacion"]].values.tolist())

            if len(operaciones_noregistradas)>0: #significa que existen clientes ingresar
                print(f"numero de operaciones no registradas: {len(operaciones_noregistradas)}")
                cambios["Operaciones No Existentes"] = len(operaciones_noregistradas)
        #         operaciones_noregistradas.to_excel("../static/reportes/Operaciones RCO no Actualizadas.xlsx", sheet_name='Hoja1')

            query_limpiar = """UPDATE operacion SET valor_mtm = NULL"""
            cursor.execute(query_limpiar)

            if len(operaciones_rco_ensistema)>0:
                print(f"numero de operaciones RCO en sistema, para actualizar: {len(operaciones_rco_ensistema)}")
                cambios["Operaciones Actualizadas"] = len(operaciones_rco_ensistema)
                query = """UPDATE operacion SET
                valor_mtm = ?, operacion_vencida = 0 WHERE num_operacion= ? ;"""
                cursor.executemany(query, operaciones_rco_ensistema[["valor_mtm","num_operacion"]].values.tolist())
                print("las operaciones fueron actualizadas")
            cursor.commit()
        ## -------------------------------------ingreso de operaciones al sistema-----------------------------
        cursor.close()
        conn.close()
        status = "200"
        return status, cambios
    except Exception as ex:
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios
# ------------------------------------------ carga RCO --------------------------------------



###------------------------------------------------reporte clientes bloqueados-------------------------------------
def generar_reporte_bloqueados():
    # now = datetime.now()
    # now = now.strftime("%Y_%m_%d %H-%M-%S")
    # archivo_inst = f"{ROOT_DIR_REPORTE}reporte_institucionales_{now}.xlsx"
    # archivo_bloq = f"{ROOT_DIR_REPORTE}reporte_bloqueados_{now}.xlsx"

    operaciones_clientes = traer_reporte_bloqueados()

    feriados = api_gestor.api_traer_feriados()
    feriados = feriados["fecha_feriado"].values.tolist()

    if(len(operaciones_clientes)>0):
        print("BLOQUEADOS NO VACIOS")
        # print(operaciones_clientes)
        operaciones_clientes["fecha_vencimiento"] = operaciones_clientes["fecha_vencimiento"].astype("datetime64[ns]")
        operaciones_clientes["fecha_envio"] = operaciones_clientes["fecha_envio"].astype("datetime64[ns]")
        operaciones_clientes["fecha_actual"] = operaciones_clientes["fecha_actual"].astype("datetime64[ns]")
        operaciones_clientes["cliente_bloqueado"] = operaciones_clientes["cliente_bloqueado"].apply(lambda x : 'BLOQUEADO' if(x == 1) else 'EN PLAZO')

        # ### contar los dias desde que se envio la documentacion y se espera la respuesta del cliente
        operaciones_clientes["dias_pendientes"] = operaciones_clientes.apply(
            lambda row : np.busday_count(row['fecha_envio'].date(), row['fecha_actual'].date(), "1111100",holidays=feriados), axis=1)

        # ### dias que faltan para que venza la operacion
        operaciones_clientes["para_vencer"] = operaciones_clientes.apply(
            lambda row : np.busday_count(row['fecha_actual'].date(), row['fecha_vencimiento'].date(), "1111100",holidays=feriados), axis=1)

        operaciones_clientes["dias_pendientes"] = operaciones_clientes["dias_pendientes"].apply(lambda x : x+1)

        operaciones_clientes["nombre_estado"] = operaciones_clientes.apply(
            lambda row : 'VENCIDO' if (row['para_vencer'] < 0) else (
                'VIGENTE' if (row['para_vencer'] > 5) else "A PUNTO DE VENCER") ,axis=1)

        operaciones_clientes = operaciones_clientes.drop(["fecha_actual", "para_vencer"], axis=1)

        operaciones_clientes = operaciones_clientes.sort_values(by=['dias_pendientes'], ascending=False)

        operaciones_clientes = operaciones_clientes[["nombre_producto", "nombre_origen", "num_operacion", "correlativo", "nota_riesgo",
                    "nombre_cliente", "rut_cliente", "fecha_operacion_2", "fecha_vencimiento_2", "fecha_envio_2" ,"dias_pendientes",
                    "cliente_bloqueado", "comentario", "observacion", "tipo_cliente", "nombre_estado", "codigo_trader", "nombre_ejecutivo",
                    "nombre_jefe_grupo", "segmento", "mtm"]]

        productos_forward = ["Forward", "NDF", "Cross Forward", "NDF FX", "FWD Starting", "Forward FX", "NDF UF",
                            "Cross NDF", "Observado", "Cross NDF UF", "NDF Asiatico", "NDF FX Swap", "Cross FWD UF", "Observado FX",
                            "FWD Starting FX"]

        productos_option = ["Vanilla Option", "Structured Option", "Asian Option", "Strip FXD", "Fwd Americano"]

        productos_swap = ["FX Swap", "SWAP", "IRS_ICP_CLP", "CCS_ICP_UF", "CCS_CLP_UF", "CCS_SOFR_ICP_CLP_COM", "IRS_ICP_UF",
                          "CCS_SOFR_ICP_USD_EFIS", "IRS_LIBOR", "IRS_SOFR_FL_FI", "IRS USD", "IRS FX", "SPC", "CCS CLP", "CCS FX",
                          "CCS UF", "ND CCS CLP", "ND CCS FX", "ND CCS UF", "CCS_USD_CLP_EF", "CCS_USD_UF_EF", "CCS_LIBOR_ICP_COM",
                          "CCS_USD_UF_COM", "CCS_LIBOR_ICP_EF", "IRS_TSOFR_FX_FL"]

        productos_filtro = productos_forward+productos_option+productos_swap

        operaciones_clientes = operaciones_clientes.loc[operaciones_clientes.apply(lambda x: x["nombre_producto"] in productos_filtro, axis=1)]

        bloqueados = operaciones_clientes.query("dias_pendientes >= 8")
        bloqueados["cliente_bloqueado"] = "BLOQUEADO"

        en_plazo = operaciones_clientes.query("dias_pendientes < 8")
        en_plazo["cliente_bloqueado"] = "EN PLAZO"

        columnas = ["Producto", "Origen Op", "N Operacion", "Correlativo", "Kit", "Cliente", "Rut", "Fecha Operacion", "Fecha de Vencimiento",
                    "ENVIO A CLIENTE", "DIAS PENDIENTES", "Estado Contrato", "Comentarios Mesa", "Observaciones", "TIPO CLIENTE",
                    "Estado Operacion", "Operador", "Ejecutivo", "Jefe de Grupo", "Segmento", "MTM"]
        ### en caso de que bloqueados este vacio
        print("aqui va la validaciones de las operaciones")

        # print(f"bloqueados ------------------------ \n bloqueados.query('num_operacion == 4910551')")

        if (len(bloqueados)>0):
            print("operaciones que estan bloqueadas")
            print(bloqueados.sort_values(by=["num_operacion", "correlativo"]))

            bloqueados_fw = bloqueados.loc[bloqueados.apply(lambda x: x["nombre_producto"] in productos_forward, axis=1)]
            # operacion_blo = bloqueados_fw.loc[bloqueados_fw['num_operacion'] == 7381779]
            # print(f"AQUI ESTA LA OPERACION1111 \n {operacion_blo}")
            bloqueados_op = bloqueados.loc[bloqueados.apply(lambda x: x["nombre_producto"] in productos_option, axis=1)]
            # operacion_blo2 = bloqueados_op.loc[bloqueados_op['num_operacion'] == 7381779]
            # print(f"AQUI ESTA LA OPERACION2222 \n {operacion_blo2}")
            bloqueados_swap = bloqueados.loc[bloqueados.apply(lambda x: x["nombre_producto"] in productos_swap, axis=1)]
            # print(bloqueados_swap.sort_values(by=["num_operacion", "correlativo"]))

            # print(bloqueados_swap.query("num_operacion == 4910551"))
            # operacion_blo3 = bloqueados_swap.loc[bloqueados_swap['num_operacion'] == 7381779]
            # print(f"AQUI ESTA LA OPERACION3333 \n {operacion_blo3}")

            # bloqueados_fw["nombre_producto"] = bloqueados_fw["nombre_producto"] = "Forward"
            # bloqueados_op["nombre_producto"] = bloqueados_op["nombre_producto"] = "Option"
            # bloqueados_swap["nombre_producto"] = bloqueados_swap["nombre_producto"] = "Swap"

            bloqueados_fw.columns = columnas
            bloqueados_op.columns = columnas
            bloqueados_swap.columns = columnas
        else:
            bloqueados_fw = pd.DataFrame(columns=columnas)
            bloqueados_op = pd.DataFrame(columns=columnas)
            bloqueados_swap = pd.DataFrame(columns=columnas)

        ### en caso de que en plazo este vacio
        if (len(en_plazo)>0):
            # operacion_plazo = en_plazo.loc[en_plazo['num_operacion'] == 7381779]
            # print(f"AQUI ESTA EN PLAZO \n {operacion_plazo}")
            en_plazo.columns = columnas
            print("operaciones que estan en plazo")
        else:
            en_plazo = pd.DataFrame(columns=columnas)

        with pd.ExcelWriter(ROOT_DIR_REPORTE+"Reporte_Bloqueados.xlsx", engine='xlsxwriter') as writer:
            bloqueados_fw.to_excel(writer, sheet_name='Bloqueados_FWD', index=False)
            bloqueados_op.to_excel(writer, sheet_name='Bloqueados_Opcion', index=False)
            bloqueados_swap.to_excel(writer, sheet_name='Bloqueados_Swap', index=False)
            en_plazo.to_excel(writer, sheet_name='Empresas_EnPlazo', index=False)

    else:
        print("SIN BLOQUEADOS NI EN PLAZO")
        columnas = ["Producto", "Origen Op", "N Operacion", "Correlativo", "Kit", "Cliente", "Rut", "Fecha Operacion", "Fecha de Vencimiento",
                    "ENVIO A CLIENTE", "DIAS PENDIENTES", "Estado Contrato", "Comentarios Mesa", "Observaciones", "TIPO CLIENTE",
                    "Estado Operacion", "Operador", "Ejecutivo", "Jefe de Grupo", "Segmento", "MTM"]
        bloqueados_fw = pd.DataFrame(columns=columnas)
        bloqueados_op = pd.DataFrame(columns=columnas)
        bloqueados_swap = pd.DataFrame(columns=columnas)
        en_plazo = pd.DataFrame(columns=columnas)

        with pd.ExcelWriter(ROOT_DIR_REPORTE+"Reporte_Bloqueados.xlsx", engine='xlsxwriter') as writer:
            bloqueados_fw.to_excel(writer, sheet_name='Bloqueados_FWD', index=False)
            bloqueados_op.to_excel(writer, sheet_name='Bloqueados_Opcion', index=False)
            bloqueados_swap.to_excel(writer, sheet_name='Bloqueados_Swap', index=False)
            en_plazo.to_excel(writer, sheet_name='Empresas_EnPlazo', index=False)
    return "ok"
###------------------------------------------------reporte clientes bloqueados-------------------------------------


###------------------------------------------------reporte institucionales bloqueados-------------------------------------
def generar_reporte_institucionales():

    operaciones_clientes = traer_reporte_institucionales()

    feriados = api_gestor.api_traer_feriados()
    feriados = feriados["fecha_feriado"].values.tolist()

    if(len(operaciones_clientes)>0):
        print("INSTITUCIONALES NO VACIOS")
        operaciones_clientes["fecha_vencimiento"] = operaciones_clientes["fecha_vencimiento"].astype("datetime64[ns]")
        operaciones_clientes["fecha_envio"] = operaciones_clientes["fecha_envio"].astype("datetime64[ns]")
        operaciones_clientes["fecha_actual"] = operaciones_clientes["fecha_actual"].astype("datetime64[ns]")

        ### contar los dias desde que se envio la documentacion y se espera la respuesta del cliente
        operaciones_clientes["dias_pendientes"] = operaciones_clientes.apply(
            lambda row : np.busday_count(row['fecha_envio'].date(), row['fecha_actual'].date(), "1111100",holidays=feriados), axis=1)

        ### dias que faltan para que venza la operacion
        operaciones_clientes["para_vencer"] = operaciones_clientes.apply(
            lambda row : np.busday_count(row['fecha_actual'].date(), row['fecha_vencimiento'].date(), "1111100",holidays=feriados), axis=1)

        operaciones_clientes["dias_pendientes"] = operaciones_clientes["dias_pendientes"].apply(lambda x : x+1)

        operaciones_clientes["nombre_estado"] = operaciones_clientes.apply(
            lambda row : 'VENCIDO' if (row['para_vencer'] < 0) else (
                'VIGENTE' if (row['para_vencer'] > 5) else "A PUNTO DE VENCER") ,axis=1)

        operaciones_clientes = operaciones_clientes.drop(["fecha_actual", "para_vencer", "comentario"], axis=1)

        operaciones_clientes = operaciones_clientes[["nombre_producto", "nombre_origen", "num_operacion", "correlativo", "nota_riesgo",
                    "nombre_cliente", "rut_cliente", "fecha_operacion_2", "fecha_vencimiento_2", "fecha_envio_2" ,"dias_pendientes",
                    "observacion", "tipo_cliente", "nombre_estado", "codigo_trader", "nombre_ejecutivo",
                    "nombre_jefe_grupo", "segmento", "mtm"]]

        productos_forward = ["Forward", "NDF", "Cross Forward", "NDF FX", "FWD Starting", "Forward FX", "NDF UF",
                            "Cross NDF", "Observado", "Cross NDF UF", "NDF Asiatico", "NDF FX Swap", "Cross FWD UF", "Observado FX",
                            "FWD Starting FX"]

        productos_option = ["Vanilla Option", "Structured Option", "Asian Option", "Strip FXD", "Fwd Americano"]

        productos_swap = ["FX Swap", "SWAP", "IRS_ICP_CLP", "CCS_ICP_UF", "CCS_CLP_UF", "CCS_SOFR_ICP_CLP_COM", "IRS_ICP_UF",
                          "CCS_SOFR_ICP_USD_EFIS", "IRS_LIBOR", "IRS_SOFR_FL_FI", "IRS USD", "IRS FX", "SPC", "CCS CLP", "CCS FX",
                          "CCS UF", "ND CCS CLP", "ND CCS FX", "ND CCS UF", "CCS_USD_CLP_EF", "CCS_USD_UF_EF", "CCS_LIBOR_ICP_COM",
                          "CCS_USD_UF_COM", "CCS_LIBOR_ICP_EF", "IRS_TSOFR_FX_FL"]

        productos_filtro = productos_forward+productos_option+productos_swap

        operaciones_clientes = operaciones_clientes.loc[operaciones_clientes.apply(lambda x: x["nombre_producto"] in productos_filtro, axis=1)]

        bloqueados_fw = operaciones_clientes.loc[operaciones_clientes.apply(lambda x: x["nombre_producto"] in productos_forward, axis=1)]
        bloqueados_op = operaciones_clientes.loc[operaciones_clientes.apply(lambda x: x["nombre_producto"] in productos_option, axis=1)]
        bloqueados_swap = operaciones_clientes.loc[operaciones_clientes.apply(lambda x: x["nombre_producto"] in productos_swap, axis=1)]

        # bloqueados_fw["nombre_producto"] = bloqueados_fw["nombre_producto"] = "Forward"
        # bloqueados_op["nombre_producto"] = bloqueados_op["nombre_producto"] = "Option"
        # bloqueados_swap["nombre_producto"] = bloqueados_swap["nombre_producto"] = "Swap"

        institucionales = pd.concat([bloqueados_fw, bloqueados_op, bloqueados_swap])
        institucionales = institucionales.reset_index(drop=True)

        institucionales = institucionales.sort_values(by=['dias_pendientes'], ascending=False)

        columnas = ["Producto", "Origen Op", "N Operacion", "Correlativo", "Kit", "Cliente", "Rut", "Fecha Operacion", "Fecha de Vencimiento",
                    "ENVIO A CLIENTE", "DIAS PENDIENTES", "Observaciones", "TIPO CLIENTE",
                    "Estado Operacion", "Operador", "Ejecutivo", "Jefe de Grupo", "Segmento", "MTM"]
        institucionales.columns = columnas

        with pd.ExcelWriter(ROOT_DIR_REPORTE+"Reporte_Institucionales.xlsx", engine='xlsxwriter') as writer:
            institucionales.to_excel(writer, sheet_name='Institucionales y Extranjeros', index=False)
    else:
        print("INSTITUCIONALES VACIO")
        columnas = ["Producto", "Origen Op", "N Operacion", "Correlativo", "Kit", "Cliente", "Rut", "Fecha Operacion", "Fecha de Vencimiento",
                    "ENVIO A CLIENTE", "DIAS PENDIENTES", "Observaciones", "TIPO CLIENTE",
                    "Estado Operacion", "Operador", "Ejecutivo", "Jefe de Grupo", "Segmento", "MTM"]
        vacios = pd.DataFrame(columns=columnas)
        with pd.ExcelWriter(ROOT_DIR_REPORTE+"Reporte_Institucionales.xlsx", engine='xlsxwriter') as writer:
            vacios.to_excel(writer, sheet_name='Institucionales y Extranjeros', index=False)
    return "ok"
###------------------------------------------------reporte institucionales bloqueados-------------------------------------




###------------------------------------------------------------------------
def traer_origenes():
    """traer_origenes"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM origen;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_origen", "nombre_origen"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------
def traer_productos():
    """traer_productos"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT id_producto, nombre_producto, nombre_familia, id_origen
                       FROM producto;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_producto", "nombre_producto", "nombre_familia", "id_origen"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------
def traer_divisas():
    """traer_divisas"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM divisa;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_divisa", "nombre_divisa", "codigo_divisa"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------
def traer_medios_suscripcion():
    """traer_medios_suscripcion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM medio WHERE nombre_campo = 'suscripcion';""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_medio", "id_campo", "nombre_campo", "nombre_medio"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
# -------------------------------------------------------------------------
def traer_clientes():
    """traer_clientes"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT rut_cliente, nombre_cliente, habilitado_opt, habilitado_fwd, id_riesgo FROM cliente;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["rut_cliente","nombre_cliente","habilitado_opt", "habilitado_fwd", "id_riesgo"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------
def traer_traders():
    """traer_traders"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT codigo_trader FROM trader;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["codigo_trader"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------
def traer_operaciones():
    """traer_operaciones"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT num_operacion, correlativo, rut_cliente, id_origen, compra_venta, fecha_operacion, fecha_vencimiento,
        id_estado, operacion_vencida FROM operacion;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["num_operacion", "correlativo", "rut_cliente", "id_origen", "compra_venta",
        "fecha_operacion", "fecha_vencimiento", "id_estado", "operacion_vencida"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------
def traer_operaciones_tabla():
    """traer_operaciones_tabla"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT op.num_operacion, ori.nombre_origen, pro.nombre_producto, cli.rut_cliente, cli.nombre_cliente, ri.nota_riesgo,
		cli.cliente_bloqueado, op.fecha_operacion, op.fecha_vencimiento, op.fecha_envio, op.fecha_recepcion, es.nombre_estado,
		op.folio_contraparte, op.comentario, op.observacion, op.codigo_trader, eq.nombre_ejecutivo, eq.nombre_jefe_grupo, cli.segmento
        FROM operacion as op
        JOIN producto as pro ON pro.id_producto = op.id_producto
		JOIN origen as ori ON ori.id_origen = op.id_origen
		JOIN cliente as cli ON cli.rut_cliente = op.rut_cliente
		LEFT JOIN riesgo as ri ON ri.id_riesgo = cli.id_riesgo
		JOIN estado as es ON es.id_estado = op.id_estado
		LEFT JOIN equipo_cliente as eq_cli ON eq_cli.rut_cliente = cli.rut_cliente AND eq_cli.activo = 1
		LEFT JOIN equipo as eq ON eq.id_equipo = eq_cli.id_equipo;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["num_operacion", "nombre_origen", "nombre_producto", "rut_cliente",
        "nombre_cliente", "nota_riesgo", "cliente_bloqueado", "fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_recepcion",
        "nombre_estado", "folio_contraparte", "comentario", "observacion", "codigo_trader", "nombre_ejecutivo", "nombre_jefe_grupo",
        "segmento"])
        dataframe["cliente_bloqueado"] = dataframe["cliente_bloqueado"].apply(lambda x : "SI" if x == 1 else "NO")
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
        

# -------------------------------------------------------------------------

def traer_documentos_tabla():
    """traer_documentos_tabla"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT doc.id_documento, doc.fecha_inicio_documento, doc.fecha_termino_documento, doc.fecha_envio, doc.fecha_recepcion,
        cus.rut_custodio, cus.nombre_custodio, tip_doc.tipo_documento, est.id_estado, est.nombre_estado, tip_doc.dias_vigencia
        FROM documento AS doc
        JOIN custodio AS cus ON cus.id_custodio = doc.id_custodio
        JOIN tipo_documento AS tip_doc ON tip_doc.id_tipo_documento = doc.id_tipo_documento
        JOIN estado AS est ON est.id_estado = doc.id_estado;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=[
        "id_documento", "fecha_inicio_documento", "fecha_termino_documento", "fecha_envio", "fecha_recepcion",
        "rut_custodio", "nombre_custodio", "tipo_documento", "id_estado", "nombre_estado", "dias_vigencia"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


def buscar_documento(id_documento):
    """buscar_documento"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        SELECT doc.id_documento, doc.fecha_inicio_documento, doc.fecha_termino_documento, doc.fecha_envio, doc.fecha_recepcion,
        cus.rut_custodio, cus.nombre_custodio, tip_doc.tipo_documento, est.id_estado, est.nombre_estado
        FROM documento AS doc
        JOIN custodio AS cus ON cus.id_custodio = doc.id_custodio
        JOIN tipo_documento AS tip_doc ON tip_doc.id_tipo_documento = doc.id_tipo_documento
        JOIN estado AS est ON est.id_estado = doc.id_estado
        WHERE doc.id_documento = {id_documento};""")

        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=[
        "id_documento", "fecha_inicio_documento", "fecha_termino_documento", "fecha_envio", "fecha_recepcion", "rut_custodio",
        "nombre_custodio", "tipo_documento", "id_estado", "nombre_estado"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
# -------------------------------------------------------------------------

def traer_firmas_tabla():
    """traer_firmas_tabla"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT fir.id_documento, doc.fecha_inicio_documento, doc.fecha_termino_documento, fir.fecha_firma, apo.rut_apoderado, apo.nombre_apoderado
        FROM firma AS fir
        JOIN documento AS doc ON doc.id_documento = fir.id_documento
        JOIN apoderado AS apo ON apo.id_apoderado = fir.id_apoderado;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=[
        "id_documento", "fecha_inicio_documento", "fecha_termino_documento", "fecha_firma", "rut_apoderado",
        "nombre_apoderado"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
# -------------------------------------------------------------------------
def traer_equipos():
    """traer_equipos"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM equipo;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_equipo","nombre_ejecutivo","nombre_jefe_grupo"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------

def traer_equipos_clientes():
    """traer_equipos_clientes"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM equipo_cliente;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_equipo","rut_cliente","fecha_activo","activo"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------

def traer_custodios():
    """traer_custodios"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM custodio;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_custodio", "rut_custodio", "nombre_custodio"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------
def traer_apoderados():
    """traer_apoderados"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM apoderado;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_apoderado","rut_apoderado","nombre_apoderado"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
# -------------------------------------------------------------------------

def traer_tipo_documento():
    """traer_tipo_documento"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM tipo_documento;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_tipo_documento", "tipo_documento", "dias_vigencia"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------

def traer_ejecutivo():
    """traer_ejecutivo"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM ejecutivo;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["rut_ejecutivo", "nombre_ejecutivo", "sucursal_ejecutivo",
                    "correo_ejecutivo", "telefono_ejecutivo"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------

def traer_estados():
    """traer_estados"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM estado;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_estado", "id_tabla", "nombre_campo", "nombre_estado"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------

def traer_estados_operaciones():
    """traer_estados_operaciones"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM estado WHERE nombre_campo = 'estado_operacion';""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_estado", "id_tabla", "nombre_campo", "nombre_estado"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

# -------------------------------------------------------------------------

def traer_medios():
    """traer_medios"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM medio;""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_medio", "id_campo", "nombre_campo", "nombre_medio"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------

def insert_firma_documento(firma):
    """insert_firma_documento"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()

        query = f"""INSERT INTO dbo.firma (id_documento, id_apoderado, fecha_firma)
                    values ({firma[0]},{firma[1]},'{firma[2]}');"""
        query2 = f"""UPDATE documento SET id_estado = 6 WHERE id_documento = {firma[0]};"""
        cursor.execute(query)
        cursor.execute(query2)
        cursor.commit()
        cursor.close()
        conn.close()
        status = "700"
        return status
    except Exception as ex:
        print(ex)
        status = "500"
        return status


# -------------------------------------------------------------------------

def traer_reporte_bloqueados():
    """traer_reporte_bloqueados"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT pro.nombre_producto, ori.nombre_origen, op.num_operacion, op.correlativo, ri.nota_riesgo, cli.nombre_cliente, cli.rut_cliente,
		fecha_operacion,
		fecha_vencimiento,
		fecha_envio,
		CAST( GETDATE() AS Date ) as fecha_actual,
        CONVERT(varchar, op.fecha_operacion,103) as fecha_operacion_2,
		CONVERT(varchar, op.fecha_vencimiento,103) as fecha_vencimiento_2,
		CONVERT(varchar, op.fecha_envio,103) as fecha_envio_2,
		CONVERT(varchar, GETDATE(),103) as fecha_actual_2,
        cli.cliente_bloqueado,
        op.comentario, op.observacion, cli.tipo_cliente, es.nombre_estado, op.codigo_trader, eq.nombre_ejecutivo, eq.nombre_jefe_grupo,
        cli.segmento, op.valor_mtm
        FROM operacion as op
		JOIN producto as pro ON pro.id_producto = op.id_producto
		JOIN origen as ori ON ori.id_origen = op.id_origen
        JOIN cliente as cli ON cli.rut_cliente = op.rut_cliente
		LEFT JOIN riesgo as ri ON ri.id_riesgo = cli.id_riesgo
		LEFT JOIN estado as es ON es.id_estado = op.id_estado
		LEFT JOIN equipo_cliente as eq_cli ON eq_cli.rut_cliente = cli.rut_cliente AND eq_cli.activo = 1
		LEFT JOIN equipo as eq ON eq.id_equipo = eq_cli.id_equipo
		WHERE op.fecha_envio is not null
		and op.fecha_recepcion is null
        order by num_operacion
        """)
        #### esta query valida que que la operacion no tenga fecha recepcion pero si tenga fecha de envio (esta pendiente)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["nombre_producto", "nombre_origen", "num_operacion", "correlativo",
        "nota_riesgo", "nombre_cliente", "rut_cliente",
        "fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_actual",
        "fecha_operacion_2", "fecha_vencimiento_2", "fecha_envio_2", "fecha_actual_2", "cliente_bloqueado",
        "comentario", "observacion", "tipo_cliente", "nombre_estado", "codigo_trader", "nombre_ejecutivo", "nombre_jefe_grupo",
        "segmento", "mtm"])
        cursor.close()
        conn.close()
        print(f"este es el largo del dataframe {len(dataframe)}")
        # print(dataframe[["fecha_operacion","fecha_operacion_2"]])
        dataframe = dataframe.query("tipo_cliente != 'INSTITUCIONAL'")
        print(f"este es el largo del dataframe {len(dataframe)}")
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------

def traer_reporte_institucionales():
    """traer_reporte_institucionales"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT pro.nombre_producto, ori.nombre_origen, op.num_operacion, op.correlativo, ri.nota_riesgo, cli.nombre_cliente, cli.rut_cliente,
        fecha_operacion,
		fecha_vencimiento,
		fecha_envio,
		CAST( GETDATE() AS Date ) as fecha_actual,
        CONVERT(varchar, op.fecha_operacion,103) as fecha_operacion_2,
		CONVERT(varchar, op.fecha_vencimiento,103) as fecha_vencimiento_2,
		CONVERT(varchar, op.fecha_envio,103) as fecha_envio_2,
		CONVERT(varchar, GETDATE(),103) as fecha_actual_2,
        op.comentario, op.observacion, cli.tipo_cliente, es.nombre_estado, op.codigo_trader, eq.nombre_ejecutivo, eq.nombre_jefe_grupo,
        cli.segmento, op.valor_mtm
        FROM operacion as op
		LEFT JOIN producto as pro ON pro.id_producto = op.id_producto
		LEFT JOIN origen as ori ON ori.id_origen = op.id_origen
        JOIN cliente as cli ON cli.rut_cliente = op.rut_cliente
		LEFT JOIN riesgo as ri ON ri.id_riesgo = cli.id_riesgo
		LEFT JOIN estado as es ON es.id_estado = op.id_estado
		LEFT JOIN equipo_cliente as eq_cli ON eq_cli.rut_cliente = cli.rut_cliente AND eq_cli.activo = 1
		LEFT JOIN equipo as eq ON eq.id_equipo = eq_cli.id_equipo
        WHERE op.fecha_envio is not null
		AND op.fecha_recepcion IS NULL
		AND cli.tipo_cliente = 'INSTITUCIONAL'
        """)
        #### esta query valida que que la operacion no tenga fecha recepcion pero si tenga fecha de envio (esta pendiente)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["nombre_producto", "nombre_origen", "num_operacion", "correlativo",
        "nota_riesgo", "nombre_cliente", "rut_cliente",
        "fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_actual",
        "fecha_operacion_2", "fecha_vencimiento_2", "fecha_envio_2", "fecha_actual_2",
        "comentario", "observacion", "tipo_cliente", "nombre_estado", "codigo_trader", "nombre_ejecutivo", "nombre_jefe_grupo",
        "segmento", "mtm"])
        cursor.close()
        conn.close()
        # print(dataframe)
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------

def traer_operaciones_norecepcion():
    """traer_operaciones_norecepcion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
            op.num_operacion, op.rut_cliente, op.fecha_envio, op.fecha_recepcion,
            CAST( GETDATE() AS Date ) as fecha_actual
            FROM operacion as op
            WHERE op.fecha_envio IS NOT NULL AND op.fecha_recepcion IS NULL
            """)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["num_operacion", "rut_cliente", "fecha_envio", "fecha_recepcion", "fecha_actual"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


##----------------------------------------------------------------------------------------------



###--------------------------------------CARGA_BASE_FULL----------------------------------------


def envio_base_full(dataframe): #finalizado
    """envio envio_base_full"""
    inicio = time.time() ## seg  1.236 - 1.2959876 // con el nuevo formato seg 1.14113 - 1.17
    cambios = { "Clientes Nuevos":0,
                "Clientes Actualizados":0,
                "Divisas Nuevas":0,
                "Productos Nuevos":0,
                "Traders Nuevos":0,
                "Operaciones Nuevas":0,
                "Operaciones Actualizadas":0,
                "Clientes Bloqueados":0}

    print(f"el largo original {len(dataframe)}")

    ## copia el num_operacion original y transforma uno en entero * 10 (le quita el fracional) luego se resta para dejar
    ## solo el resto y transformarlo a entero para obtener el correlativo
    dataframe["num_operacion_or"] = dataframe["num_operacion"]
    dataframe["num_operacion"] = dataframe["num_operacion"].astype(int)
    dataframe["correlativo"] = dataframe.apply(lambda row : int((row['num_operacion_or']*10) - (row['num_operacion']*10)), axis=1)

    dataframe = dataframe.sort_values(['num_operacion', 'correlativo'], ascending = [True, True])

    dataframe["nombre_cliente"] = dataframe["nombre_cliente"].fillna("-")
    dataframe["rut_cliente"] = dataframe["rut_cliente"].fillna("0-0")
    dataframe["nombre_cliente"] = dataframe["nombre_cliente"].apply(lambda x : None if str(x) == "-" else x)

    #primera letra en mayuscula
    dataframe['nombre_origen'] = dataframe['nombre_origen'].str.capitalize()
    dataframe["nombre_origen"] = dataframe["nombre_origen"].apply(lambda x : "Modificado" if x in ["Modifcado"] else x)

#----------------------------------------------------------------------------------
    lista = dataframe.index[dataframe['nombre_origen'] == 'Modificado'].tolist()
    num_operacion = []
    for item in lista:
        if(dataframe['num_operacion'][item] != dataframe['num_operacion'][item-1]):
            num_operacion.append(dataframe['num_operacion'][item])
    print("numero de operaciones pendientes")
    print(num_operacion)
#----------------------------------------------------------------------------------
    # lista2 = dataframe.index[dataframe['nombre_origen'] == 'Modificado'].tolist()

    if len(num_operacion)==0:
        print("se eliminaron las inconsistencias, ahora a cambiar los origenes")
        for item in lista:
            dataframe['nombre_origen'][item] = dataframe['nombre_origen'][item-1]
            dataframe['operacion_vencida'][item-1] = 1
            dataframe['id_estado'][item-1] = 4
    else:
        status = "900"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

#----------------------------------------------------------------------------------

    dataframe = dataframe.query("nombre_origen == 'Findur' or nombre_origen == 'Murex' or nombre_origen == 'Bac'")

    #pone mayusculas en el rut de cliente, esto es para igualar las letras K de los rut con los ya ingresados en el sistema
    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).upper())
    dataframe = dataframe.dropna(subset = ["rut_cliente"])


    dataframe["codigo_trader"] = dataframe["codigo_trader"].str[0:44]
    #codigo trader en mayusculas, en caso de existir un 0 reemplazar por un guion a modo de vacio
    dataframe["codigo_trader"] = dataframe["codigo_trader"].apply(lambda x : str(x).strip().upper())
    dataframe["codigo_trader"] = dataframe["codigo_trader"].fillna("-")
    dataframe["codigo_trader"] = dataframe["codigo_trader"].apply(lambda x : None if str(x) == "-" else x)


    #elimina los espaciones en blanco de los nombres de productos
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : str(x).strip())

    dataframe["producto_or"] = dataframe["nombre_producto"]
    #renombra los productos desde base full para que coincidan con los ingresados en el sistema previamente
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : "Option" if x in ["Forward Perdida Acotada",
                            "Forward perdida Acotada", "Forward Entrada Salida", "Collar (Risk Reversal)", "Forward Asiático"] else x)
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : "Forward" if x in ["FORWARD", "ARBITRAJE", "FORWARD"]else x)
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : "SWAP" if x in ["CCS_USD_UF_EF", "Swap"] else x)
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : "Vanilla Option" if x in ["Vanilla"] else x)
    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : "Fwd Americano" if x in ["Forward Americano"] else x)

    #reemplaza los campos de compra y venta para coincidir con el formato. llena los vacios con guion //sera ,mejor dejarlos vacios
    dataframe["compra_venta"] = dataframe["compra_venta"].fillna("-")
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "-" if x in ["ACTUALIZAR"] else x)
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : None if str(x) == "-" else x)
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "B" if x in ["C", "BUY", "Buy"] else x)
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "S" if x in ["V", "SELL", "Sell"] else x)

    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].replace({'ACTUALIZAR': "0"})
    dataframe[["divisa_inicial", "divisa_final"]] = dataframe[["divisa_inicial", "divisa_final"]].fillna("0")
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].apply(lambda x : None if str(x) == "0" else x)
    dataframe["divisa_final"] = dataframe["divisa_final"].replace({'ACTUALIZAR': "0"})
    dataframe["divisa_final"] = dataframe["divisa_final"].apply(lambda x : None if str(x) == "0" else x)


    dataframe[["monto_inicial", "tasa_cambio", "monto_final"]] = dataframe[["monto_inicial", "tasa_cambio", "monto_final"]].fillna(0)

    dataframe["fecha_operacion"] = dataframe["fecha_operacion"].apply(lambda x : None if x == "0" else x)
    dataframe["fecha_vencimiento"] = dataframe["fecha_vencimiento"].apply(lambda x : None if x == "0" else x)

    # # traspasa las divisas inciales y finales del dataframe para poder trabajar con ellas
    divisas = traer_divisas() #registros base de datos
    divisas_iniciales = pd.DataFrame(columns=["divisa_inicial"])
    divisas_finales = pd.DataFrame(columns=["divisa_final"])
    divisas_iniciales = dataframe.drop_duplicates(["divisa_inicial"], keep='first') #elimina los clientes duplicados
    divisas_finales = dataframe.drop_duplicates(["divisa_final"], keep='first') #elimina los clientes duplicados

    # # concatena las divisas iniciales y finales en un nuevo dataframe para tener el universo total de divisas recibidas en la carga
    divisas_totales = pd.DataFrame(columns=["divisas"])
    divisas_totales["divisas"] = pd.concat([divisas_iniciales["divisa_inicial"], divisas_finales["divisa_final"]], axis=0, ignore_index=False)
    divisas_totales = divisas_totales.drop_duplicates(["divisas"], keep='first') #elimina los clientes duplicados
    divisas_totales = divisas_totales.dropna(subset = ['divisas'])
    divisas_totales = divisas_totales.reset_index(drop=True)

    # # una vez formateados los nombres de los productos se botan los duplicados para tener los productos unicos
    productos = traer_productos() #registros base de datos
    productos_no_duplicados = dataframe.drop_duplicates(["nombre_producto"], keep='first') #elimina los clientes duplicados
    productos_no_duplicados = productos_no_duplicados.reset_index(drop=True)

    # # bota los clientes duplicados del dataframe de la carga full
    clientes = traer_clientes() #registros base de datos
    clientes_no_duplicados = dataframe.drop_duplicates(["rut_cliente"], keep='first')

    # # bota los trader duplicados y se hace un tratamiento de los datos recibidos
    traders = traer_traders() #registros base de datos
    # para reemplazar las valores al mismo tiempo ------> df.replace({'-': None, 'None': None})
    traders_no_duplicados = dataframe.drop_duplicates(["codigo_trader"], keep='first') #elimina los traders duplicados
    traders_no_duplicados = traders_no_duplicados.dropna(subset = ['codigo_trader'])
    traders_no_duplicados = traders_no_duplicados.reset_index(drop=True)

    # # traspasa la informacion del dataframe original para realizar el tratamiento y cambio el formato de las fechas
    operaciones = traer_operaciones() #registros base de datos
    operaciones_no_duplicadas = dataframe
    operaciones_no_duplicadas["fecha_operacion"] = operaciones_no_duplicadas["fecha_operacion"].dt.date
    operaciones_no_duplicadas["fecha_vencimiento"] = operaciones_no_duplicadas["fecha_vencimiento"].apply(lambda x : None if pd.isna(x) else datetime.date(x))

    operaciones_no_duplicadas = operaciones_no_duplicadas.reset_index(drop=True)
    origenes = traer_origenes() #nombre_origen , id_origen

    try:
        conn = pyodbc.connect(config)
        print("Procede a la Carga Full")
        cursor = conn.cursor()
        cursor.fast_executemany = True

    #     ## -------------------------------------ingreso de divisas al sistema-----------------------------
        if len(divisas)==0:
            print("insert directo, no requiere filtrar por divisas nuevas, ya que no hay registros")
            cambios["Divisas Nuevas"] = len(divisas_totales)
            query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
            cursor.executemany(query, divisas_totales[["divisas"]].values.tolist())
        else:
            print("pregunta por divisas que no esten en el sistema")
            divisas_nuevas = divisas_totales[~divisas_totales["divisas"].isin(divisas["codigo_divisa"])]
            if len(divisas_nuevas)>0: #significa que existen clientes ingresar
                cambios["Divisas Nuevas"] = len(divisas_nuevas)
                print(f"numero de divisas nuevas: {len(divisas_nuevas)}")
                query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
                cursor.executemany(query, divisas_nuevas[["divisas"]].values.tolist())
            else:
                print("no se encontraron divisas nuevas para ingresar")
        cursor.commit()
        # # # -------------------------------------ingreso de divisas al sistema-----------------------------

        # # # -------------------------------------ingreso de productos al sistema-----------------------------

        join_origen = pd.merge(origenes , productos_no_duplicados, on=['nombre_origen'], how="right")
        productos_no_duplicados["id_origen"] = join_origen["id_origen"]

        if len(productos)==0:
            print("insert directo, no requiere filtrar por productos nuevos, ya que no hay registros")
            cambios["Productos Nuevos"] = len(productos_no_duplicados)
            query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, ?);"""
            cursor.executemany(query, productos_no_duplicados[["nombre_producto", "id_origen"]].values.tolist())
        else:
            print("pregunta por productos que no estan en el sistema, (son nuevos)")
            productos_nuevos = productos_no_duplicados[~productos_no_duplicados["nombre_producto"].isin(productos["nombre_producto"])] #clientes nuevos
            if len(productos_nuevos)>0: #significa que existen clientes ingresar
                cambios["Productos Nuevos"] = len(productos_nuevos)
                print(f"numero de productos nuevos: {len(productos_nuevos)}")
                query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?, ?);"""
                cursor.executemany(query, productos_nuevos[["nombre_producto", "id_origen"]].values.tolist())
            else:
                print("no se encontraron productos nuevos para ingresar")
        cursor.commit()
        # # # -------------------------------------ingreso de productos al sistema-----------------------------

        # # # -------------------------------------ingreso de clientes al sistema-----------------------------

        if len(clientes)==0:
            print("insert directo, no requiere filtrar por clientes nuevos, ya que no hay registros")
            cambios["Clientes Nuevos"] = len(clientes_no_duplicados)
            query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
            cursor.executemany(query, clientes_no_duplicados[["rut_cliente","nombre_cliente"]].values.tolist())

        else:
            print("pregunta por cliente que no estan en el sistema, (son nuevos)")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos

            if len(clientes_nuevos)>0: #significa que existen clientes ingresar
                cambios["Clientes Nuevos"] = len(clientes_nuevos)
                print(f"numero de clientes nuevos: {len(clientes_nuevos)}")
                query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado) values (?,?,0);"""
                cursor.executemany(query, clientes_nuevos[["rut_cliente","nombre_cliente"]].values.tolist())

            clientes_para_actualizar = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes_nuevos["rut_cliente"])] #clientes nuevos
            if len(clientes_para_actualizar)>0: #significa que existen clientes para actualizar
                cambios["Clientes Actualizados"] = len(clientes_para_actualizar)
                print(f"clientes para actualizar: {len(clientes_para_actualizar)}")
                query = """UPDATE cliente SET nombre_cliente = ? WHERE rut_cliente=?;"""
                cursor.executemany(query, clientes_para_actualizar[["nombre_cliente","rut_cliente"]].values.tolist())
        cursor.commit()
        # # # -------------------------------------ingreso de clientes al sistema-----------------------------

        # # # -------------------------------------ingreso de traders al sistema-----------------------------
        ## no requiere actualizar porque solo se inserta el codigo_trader
        if len(traders)==0:
            print("insert directo, no requiere filtrar por traders nuevos, ya que no hay registros")
            cambios["Traders Nuevos"] = len(traders_no_duplicados)
            query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
            cursor.executemany(query, traders_no_duplicados[["codigo_trader"]].values.tolist())

        else:
            print("pregunta por traders que no estan en el sistema, (son nuevos)")
            traders_nuevos = traders_no_duplicados[~traders_no_duplicados["codigo_trader"].isin(traders["codigo_trader"])] #traders nuevos
            print(f"numero de traders nuevos: {len(traders_nuevos)}")
            cambios["Traders Nuevos"] = len(traders_nuevos)
            if len(traders_nuevos)>0:
                query = """INSERT INTO dbo.trader (codigo_trader) values (?);"""
                cursor.executemany(query, traders_nuevos[["codigo_trader"]].values.tolist())
        cursor.commit()
        # # ## -------------------------------------ingreso de traders al sistema-----------------------------

        divisas2 = traer_divisas() #registros base de datos
        productos2 = traer_productos() #registros base de datos

        # ##----id_tipo_producto------------
        join_idproducto = pd.merge(productos2 , operaciones_no_duplicadas, on=['nombre_producto'], how="right")

        join_iddivisainicial = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_inicial'], how="right")

        join_iddivisafinal = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_final'], how="right")

        operaciones_no_duplicadas["id_producto"] = join_idproducto["id_producto"]
        operaciones_no_duplicadas["id_divisa_inicial"] = join_iddivisainicial["id_divisa"]
        operaciones_no_duplicadas["id_divisa_final"] = join_iddivisafinal["id_divisa"]

        join_origenes = pd.merge(origenes , operaciones_no_duplicadas, on=['nombre_origen'], how="right")
        operaciones_no_duplicadas["id_origen"] = join_origenes["id_origen"]

        operaciones_no_duplicadas = operaciones_no_duplicadas.drop_duplicates(subset=['nombre_origen','num_operacion','correlativo'], keep='last').reset_index(drop=True)

        operaciones_no_duplicadas = operaciones_no_duplicadas.fillna("nulo")
        operaciones_no_duplicadas = operaciones_no_duplicadas.replace({"nulo" : None})

        # ## -------------------------------------ingreso de operaciones al sistema-----------------------------

        if len(operaciones)==0:
            print("insert directo, no requiere filtrar por operaciones nuevas, ya que no hay registros")
            cambios["Operaciones Nuevas"] = len(operaciones_no_duplicadas)

            query = """
            INSERT INTO dbo.operacion (id_origen, num_operacion, correlativo, id_producto, fecha_operacion, fecha_vencimiento,
            rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final, monto_final, compra_venta, codigo_trader,
            operacion_vencida, id_estado) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
            """

            cursor.executemany(query, operaciones_no_duplicadas[["id_origen", "num_operacion", "correlativo", "id_producto", "fecha_operacion",
                        "fecha_vencimiento", "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio",
                        "id_divisa_final", "monto_final", "compra_venta", "codigo_trader", "operacion_vencida",
                        "id_estado"]].values.tolist())

        else:
            #--- crea un codigo para diferencias las operaciones entre si (ayuda a filtrar por mas de un campo)
            #--- el codigo es (id_origen + num_operacion + correlativo)
            operaciones["cod"] = operaciones.apply(lambda row : f"{row['id_origen']}+{row['num_operacion']}+{row['correlativo']}", axis=1)
            operaciones_no_duplicadas["cod"] = operaciones_no_duplicadas.apply(lambda row : f"{row['id_origen']}+{row['num_operacion']}+{row['correlativo']}", axis=1)

            print("pregunta por operaciones que no estan en el sistema, (son nuevas)")
            operaciones_nuevas = operaciones_no_duplicadas[~operaciones_no_duplicadas["cod"].isin(operaciones["cod"])] #operaciones nuevas
            if len(operaciones_nuevas)>0: #significa que existen clientes ingresar
                cambios["Operaciones Nuevas"] = len(operaciones_nuevas)
                print("OPERACIONES NUEVAS")
                query = """
                INSERT INTO dbo.operacion (id_origen, num_operacion, correlativo, id_producto, fecha_operacion, fecha_vencimiento,
                rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final, monto_final, compra_venta, codigo_trader,
                operacion_vencida, id_estado) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                """
                cursor.executemany(query, operaciones_nuevas[["id_origen", "num_operacion", "correlativo", "id_producto", "fecha_operacion",
                "fecha_vencimiento", "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio",
                "id_divisa_final", "monto_final", "compra_venta", "codigo_trader", "operacion_vencida",
                "id_estado"]].values.tolist())

            operaciones_para_actualizar = operaciones_no_duplicadas[~operaciones_no_duplicadas["cod"].isin(operaciones_nuevas["cod"])] #clientes nuevos
            if len(operaciones_para_actualizar)>0: #significa que existen clientes ingresar
                cambios["Operaciones Actualizadas"] = len(operaciones_para_actualizar)
                print("OPERACIONES PARA ACTUALIZAR")

                query = """UPDATE operacion SET id_origen = ?, id_producto = ?, fecha_operacion = ?, fecha_vencimiento = ?,
                rut_cliente = ?, id_divisa_inicial = ?, monto_inicial = ?, tasa_cambio = ?, id_divisa_final = ?, monto_final = ?,
                compra_venta = ?, codigo_trader = ?, operacion_vencida = ?, id_estado = ?
                WHERE num_operacion = ? and correlativo = ? ;"""

                cursor.executemany(query, operaciones_para_actualizar[["id_origen", "id_producto", "fecha_operacion", "fecha_vencimiento",
                "rut_cliente", "id_divisa_inicial", "monto_inicial", "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta",
                "codigo_trader", "operacion_vencida", "id_estado", "num_operacion", "correlativo"]].values.tolist())
                print("las operaciones fueron actualizadas")
        cursor.commit()

        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        api_gestor.api_estado_clientes()
        api_gestor.api_actualizar_estado_operaciones()
        # -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------

        cursor.close()
        conn.close()
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        cursor.close()
        conn.close()
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

###-------------------------------------------CARGA BASE FULL--------------------------------------------




###--------------------------------------CARGA_ENVIO_CONTRATOS----------------------------------------


def envio_envio_contratos(dataframe): #finalizado
    """envio envio_envio_contratos"""
    inicio = time.time() ## seg  1.236 - 1.2959876 // con el nuevo formato seg 1.14113 - 1.17
    cambios = { "Clientes Nuevos":0,
                "Clientes Actualizados":0,
                "Divisas Nuevas":0,
                "Productos Nuevos":0,
                "Medios Suscripcion Nuevos":0,
                "Operaciones Nuevas":0,
                "Operaciones Actualizadas":0,
                "Clientes Bloqueados":0}

    dataframe["num_operacion_or"] = dataframe["num_operacion"]
    dataframe["num_operacion"] = dataframe["num_operacion"].astype(int)
    dataframe["correlativo"] = dataframe.apply(lambda row : int((row['num_operacion_or']*10) - (row['num_operacion']*10)), axis=1)
    dataframe = dataframe.sort_values(['num_operacion', 'correlativo'], ascending = [True, True])

    #primera letra en mayuscula
    dataframe['nombre_origen'] = dataframe['nombre_origen'].str.capitalize()
    dataframe["nombre_origen"] = dataframe["nombre_origen"].apply(lambda x : "Modificado" if x in ["Modifcado", "Modificacion"] else x)

#----------------------------------------------------------------------------------
    lista = dataframe.index[dataframe['nombre_origen'] == 'Modificado'].tolist()
    num_operacion = []
    origen = []
    for item in lista:
        if(dataframe['num_operacion'][item] != dataframe['num_operacion'][item-1]):
            num_operacion.append(dataframe['num_operacion'][item])
            origen.append(dataframe['nombre_origen'][item])
    # print("numero de operaciones pendientes")
    # print(num_operacion)

    if len(num_operacion)!=0:
        status = "900"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios
    else:
        for item in lista:
            dataframe['nombre_origen'][item] = dataframe['nombre_origen'][item-1]

#----------------------------------------------------------------------------------
    # filtrado = dataframe[~dataframe['num_operacion'].isin(num_operacion)]
    # print(len(dataframe))
    # print(len(num_operacion))
    # print(len(filtrado))

    # num_operacion2 = []
    # origen2 = []
    # lista2 = filtrado.index[filtrado['nombre_origen'] == 'Modificado'].tolist()
    # for item in lista2:
    #     if(filtrado['num_operacion'][item] != filtrado['num_operacion'][item-1]):
    #         num_operacion2.append(filtrado['num_operacion'][item])
    #         origen2.append(filtrado['nombre_origen'][item])
    # print("numero de operaciones pendientes")
    # print(num_operacion2)
    # print(len(filtrado))
    # print(len(num_operacion2))

    # if len(num_operacion2)!=0:
    #     status = "900"
    #     cambios = {"Error":"Error en la Consulta"}
    #     return status, cambios

    # print(dataframe)
    # dataframe = filtrado
    # print(dataframe)
    dataframe = dataframe.reset_index(drop=True)
    # print(dataframe)

#----------------------------------------------------------------------------------
    # lista2 = dataframe.index[dataframe['nombre_origen'] == 'Modificado'].tolist()

    # if len(num_operacion)==0:
    #     print("se eliminaron las inconsistenvias, ahora a cambiar los origenes")
    #     for item in lista2:
    #         dataframe['nombre_origen'][item] = dataframe['nombre_origen'][item-1]
    # else:
    #     # filtro por nombre de origen en las operaciones
    #     nuevo = pd.DataFrame(list(zip(num_operacion, origen)), columns =['num_operacion', 'origen'])
    #     nuevo.to_excel("detalles_envio_contrato.xlsx", index=False)
    #     status = "900"
    #     cambios = {"Error":"Error en la Consulta"}
    #     return status, cambios

#----------------------------------------------------------------------------------

    dataframe = dataframe.query("nombre_origen == 'Findur' or nombre_origen == 'Murex' or nombre_origen == 'Bac'")

    dataframe["nombre_producto"] = dataframe["nombre_producto"].apply(lambda x : str(x).strip())
    dataframe["nombre_producto"] = dataframe["nombre_producto"].fillna("nulo")
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'<NA>':'nulo'})
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'FORWARD':'Forward'})
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'CCS_USD_UF_EF':'SWAP'})
    #### tratamiento de los nulos
    dataframe["nombre_producto"] = dataframe["nombre_producto"].replace({'nulo':None})

    dataframe["rut_cliente"] = dataframe["rut_cliente"].apply(lambda x : str(x).upper())

    dataframe["riesgo"] = dataframe["riesgo"].apply(lambda x : x if x in ["1","2","3"] else 3)
    dataframe["riesgo"] = dataframe["riesgo"].astype(int)

    dataframe["folio_contraparte"] = dataframe["folio_contraparte"].fillna("nulo")
    dataframe["observacion"] = dataframe["observacion"].fillna("nulo")
    dataframe["status_operacion"] = dataframe["status_operacion"].fillna("nulo")
    dataframe["status_operacion"] = dataframe["status_operacion"].apply(lambda x : "CONFIRMADO" if "CONF" in x else "PENDIENTE")
    #### tratamiento de los nulos
    dataframe[["folio_contraparte", "observacion", "status_operacion"]] = dataframe[["folio_contraparte", "observacion", "status_operacion"]].replace({'nulo':None})


    dataframe["compra_venta"] = dataframe["compra_venta"].fillna("nulo")
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "B" if x in ["C", "BUY", "Buy"] else x)
    dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "S" if x in ["V", "SELL", "Sell"] else x)
    dataframe["compra_venta"] = dataframe["compra_venta"].replace({'nulo':None})

    dataframe[["divisa_inicial", "divisa_final"]] = dataframe[["divisa_inicial", "divisa_final"]].fillna("nulo")
    dataframe["divisa_inicial"] = dataframe["divisa_inicial"].apply(lambda x : None if str(x) == "0" else x)
    dataframe["divisa_final"] = dataframe["divisa_final"].apply(lambda x : None if str(x) == "0" else x)
    dataframe[["divisa_inicial", "divisa_final"]] = dataframe[["divisa_inicial", "divisa_final"]].replace({'nulo':None})

    dataframe[["monto_inicial", "tasa_cambio", "monto_final"]] = dataframe[["monto_inicial", "tasa_cambio", "monto_final"]].fillna(0)

    dataframe["nombre_medio"] = dataframe["nombre_medio"].apply(lambda x : str(x).upper())
    dataframe["nombre_medio"] = dataframe["nombre_medio"].fillna("nulo")
    dataframe["nombre_medio"] = dataframe["nombre_medio"].apply(lambda x : "DCV" if "DCV" in x else x)
    dataframe["nombre_medio"] = dataframe["nombre_medio"].apply(lambda x : "Fisica" if "FISIC" in x else x)
    dataframe["nombre_medio"] = dataframe["nombre_medio"].apply(lambda x : "Otro" if x in
        ["ESPEJO", "SI", "EMPRESA", "0", "EF","CHICAGO CAMARA", "STANDARD CAMARA", "PENDIENTE EVIDENCIA","NAN", "PENDIENTE"] else x)
    dataframe["nombre_medio"] = dataframe["nombre_medio"].apply(lambda x : "SINACOFI" if x in ["SUSCRITO SINACOFI"] else x)
    dataframe["nombre_medio"] = dataframe["nombre_medio"].replace({'MT300':'MT-300'})
    dataframe["nombre_medio"] = dataframe["nombre_medio"].replace({'MAIL':'Mail'})
    dataframe["nombre_medio"] = dataframe["nombre_medio"].replace({'SOMA':'Soma'})
    dataframe["nombre_medio"] = dataframe["nombre_medio"].replace({'nulo':None})

    dataframe["compra_venta"] = dataframe["compra_venta"].fillna("nulo")
    dataframe["compra_venta"] = dataframe["compra_venta"].replace({'0':None, 0:None, 'nulo':None})

    dataframe[["fecha_vencimiento", "fecha_envio", "fecha_recepcion"]] = dataframe[["fecha_vencimiento", "fecha_envio", "fecha_recepcion"]].fillna("nulo")
    dataframe[["fecha_vencimiento", "fecha_envio", "fecha_recepcion"]] = dataframe[["fecha_vencimiento", "fecha_envio", "fecha_recepcion"]].replace({'nulo':None})

    divisas = traer_divisas() #registros base de datos
    divisas_iniciales = pd.DataFrame(columns=["divisa_inicial"])
    divisas_finales = pd.DataFrame(columns=["divisa_final"])

    divisas_iniciales = dataframe.drop_duplicates(["divisa_inicial"], keep='first') #elimina los clientes duplicados
    divisas_finales = dataframe.drop_duplicates(["divisa_final"], keep='first') #elimina los clientes duplicados

    divisas_totales = pd.DataFrame(columns=["divisas"])
    divisas_totales["divisas"] = pd.concat([divisas_iniciales["divisa_inicial"], divisas_finales["divisa_final"]], axis=0, ignore_index=False)
    divisas_totales = divisas_totales.drop_duplicates(["divisas"], keep='first') #elimina los clientes duplicados
    divisas_totales = divisas_totales.dropna(subset=['divisas'])
    divisas_totales = divisas_totales.reset_index(drop=True)
    # print(divisas_totales["divisas"])

    productos = traer_productos() #registros base de datos
    productos_no_duplicados = dataframe.drop_duplicates(["nombre_producto"], keep='first') #elimina los clientes duplicados
    productos_no_duplicados = productos_no_duplicados.dropna(subset=['nombre_producto'])
    productos_no_duplicados = productos_no_duplicados.reset_index(drop=True)

    clientes = traer_clientes() #registros base de datos
    clientes_no_duplicados = dataframe
    clientes_no_duplicados = clientes_no_duplicados.drop_duplicates(["rut_cliente"], keep='first')

    medios = traer_medios_suscripcion() #registros base de datos
    medios_no_duplicados = dataframe.drop_duplicates("nombre_medio", keep="first")
    medios_no_duplicados = medios_no_duplicados.dropna(subset=['nombre_medio'])

    operaciones = traer_operaciones() #registros base de datos
    operaciones_no_duplicadas = dataframe
    operaciones_no_duplicadas["fecha_operacion"] = operaciones_no_duplicadas["fecha_operacion"].dt.date
    operaciones_no_duplicadas["fecha_vencimiento"] = operaciones_no_duplicadas["fecha_vencimiento"].apply(lambda x : x if pd.isna(x) else datetime.date(x))
    operaciones_no_duplicadas["fecha_envio"] = operaciones_no_duplicadas["fecha_envio"].apply(lambda x : x if pd.isna(x) else datetime.date(x))
    operaciones_no_duplicadas["fecha_recepcion"] = operaciones_no_duplicadas["fecha_recepcion"].apply(lambda x : x if pd.isna(x) else datetime.date(x))

    operaciones_no_duplicadas = operaciones_no_duplicadas.drop_duplicates(subset=['nombre_origen','num_operacion','correlativo'], keep='last').reset_index(drop=True)

    try:
        conn = pyodbc.connect(config)
        print("Procede a ENVIO CONTRATOS")
        cursor = conn.cursor()
        cursor.fast_executemany = True

    #     ## -------------------------------------ingreso de divisas al sistema-----------------------------
        if len(divisas)==0:
            print("insert directo, no requiere filtrar por divisas nuevas, ya que no hay registros")
            cambios["Divisas Nuevas"] = len(divisas_totales)
            query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
            cursor.executemany(query, divisas_totales[["divisas"]].values.tolist())
        else:
            print("pregunta por divisas que no esten en el sistema")
            divisas_nuevas = divisas_totales[~divisas_totales["divisas"].isin(divisas["codigo_divisa"])]
            if len(divisas_nuevas)>0: #significa que existen clientes ingresar
                cambios["Divisas Nuevas"] = len(divisas_nuevas)
                print(f"numero de divisas nuevas: {len(divisas_nuevas)}")
                query = """INSERT INTO dbo.divisa (codigo_divisa) values (?);"""
                cursor.executemany(query, divisas_nuevas[["divisas"]].values.tolist())
            else:
                print("no se encontraron divisas nuevas para ingresar")
        cursor.commit()
    #     ## -------------------------------------ingreso de divisas al sistema-----------------------------

    #     ## -------------------------------------ingreso de productos al sistema-----------------------------
        print(f"el largo de los productos por el momento{len(productos_no_duplicados['nombre_producto'])}")

        origenes = traer_origenes() #nombre_origen , id_origen
        join_origen = pd.merge(origenes , productos_no_duplicados, on=['nombre_origen'], how="right")
        productos_no_duplicados["id_origen"] = join_origen["id_origen"]

        if len(productos)==0:
            print("insert directo, no requiere filtrar por productos nuevos, ya que no hay registros")
            cambios["Productos Nuevos"] = len(productos_no_duplicados)
            query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?,?);"""
            cursor.executemany(query, productos_no_duplicados[["nombre_producto", "id_origen"]].values.tolist())
        else:
            print("pregunta por productos que no estan en el sistema, (son nuevos)")
            productos_nuevos = productos_no_duplicados[~productos_no_duplicados["nombre_producto"].isin(productos["nombre_producto"])] #clientes nuevos
      #     clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos
            if len(productos_nuevos)>0: #significa que existen clientes ingresar
                cambios["Productos Nuevos"] = len(productos_nuevos)
                print(f"numero de productos nuevos: {len(productos_nuevos)}")
                query = """INSERT INTO dbo.producto (nombre_producto, id_origen) values (?,?);"""
                cursor.executemany(query, productos_nuevos[["nombre_producto", "id_origen"]].values.tolist())
            else:
                print("no se encontraron productos nuevos para ingresar")
        cursor.commit()
        ## -------------------------------------ingreso de productos al sistema-----------------------------

        ## -------------------------------------ingreso de clientes al sistema-----------------------------

        if len(clientes)==0:
            print("insert directo, no requiere filtrar por clientes nuevos, ya que no hay registros")
            cambios["Clientes Nuevos"] = len(clientes_no_duplicados)
            query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado, id_riesgo) values (?,?,0,?);"""
            cursor.executemany(query, clientes_no_duplicados[["rut_cliente","nombre_cliente", "riesgo"]].values.tolist())
        else:
            print("pregunta por cliente que no estan en el sistema, (son nuevos)")
            clientes_nuevos = clientes_no_duplicados[~clientes_no_duplicados["rut_cliente"].isin(clientes["rut_cliente"])] #clientes nuevos

            if len(clientes_nuevos)>0: #significa que existen clientes ingresar
                cambios["Clientes Nuevos"] = len(clientes_nuevos)
                print(f"numero de clientes nuevos: {len(clientes_nuevos)}")
                query = """INSERT INTO dbo.cliente (rut_cliente, nombre_cliente, cliente_bloqueado, id_riesgo) values (?,?,0,?);"""
                cursor.executemany(query, clientes_nuevos[["rut_cliente","nombre_cliente", "riesgo"]].values.tolist())

        cursor.commit()
        ## -------------------------------------ingreso de clientes al sistema-----------------------------


        ## -------------------------------------ingreso de medios_suscripcion-----------------------------
        # medios_suscripcion   -    ingresar solo nuevos
        if len(medios)==0:
            print("insert directo, no requiere filtrar por medios nuevos, ya que no hay registros")
            cambios["Medios Suscripcion Nuevos"] = len(medios_no_duplicados)
            query = """INSERT INTO dbo.medio (nombre_medio, id_campo, nombre_campo) values (?,1,'suscripcion');"""
            cursor.executemany(query, medios_no_duplicados[["nombre_medio"]].values.tolist())

        else:
            print("pregunta por medios que no estan en el sistema, (son nuevos)")
            medios_nuevos = medios_no_duplicados[~medios_no_duplicados["nombre_medio"].isin(medios["nombre_medio"])] #traders nuevos
            print(f"Medios Suscripcion Nuevos: {len(medios_nuevos)}")
            cambios["Medios Suscripcion Nuevos"] = len(medios_nuevos)
            if len(medios_nuevos)>0:
                query = """INSERT INTO dbo.medio (nombre_medio, id_campo, nombre_campo) values (?,1,'suscripcion');"""
                cursor.executemany(query, medios_nuevos[["nombre_medio"]].values.tolist())
        cursor.commit()
        ## -------------------------------------ingreso de medios_suscripcion-----------------------------


        ## -------------------------------------ingreso de operaciones al sistema-----------------------------

        divisas2 = traer_divisas() #registros base de datos
        productos2 = traer_productos()
        medios2 = traer_medios_suscripcion()
        status2 = traer_estados_operaciones()
        # # ##----id_tipo_producto------------
        join_idproducto = pd.merge(productos2 , operaciones_no_duplicadas, on=['nombre_producto'], how="right")
        join_iddivisainicial = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_inicial'], how="right")
        join_iddivisafinal = pd.merge(divisas2 , operaciones_no_duplicadas, left_on=['codigo_divisa'], right_on=['divisa_final'], how="right")

        operaciones_no_duplicadas["id_producto"] = join_idproducto["id_producto"]
        operaciones_no_duplicadas["id_divisa_inicial"] = join_iddivisainicial["id_divisa"]
        operaciones_no_duplicadas["id_divisa_final"] = join_iddivisafinal["id_divisa"]

        # print(operaciones_no_duplicadas.dtypes)
        # print(operaciones_no_duplicadas["nombre_origen"])

        join_origenes = pd.merge(origenes , operaciones_no_duplicadas, on=['nombre_origen'], how="right")
        operaciones_no_duplicadas["id_origen"] = join_origenes["id_origen"]

        # print(operaciones_no_duplicadas.dtypes)


        join_idmedios = pd.merge(medios2, operaciones_no_duplicadas, on="nombre_medio", how="right")
        operaciones_no_duplicadas["id_medio_suscripcion"] = join_idmedios["id_medio"]

        join_idstatus = pd.merge(status2, operaciones_no_duplicadas, left_on=['nombre_estado'], right_on=['status_operacion'], how="right")
        operaciones_no_duplicadas["id_estado"] = join_idstatus["id_estado"]

        operaciones_no_duplicadas[["id_divisa_inicial", "id_divisa_final", "id_estado", "id_producto", "id_medio_suscripcion", "id_origen"]] = operaciones_no_duplicadas[["id_divisa_inicial", "id_divisa_final", "id_estado", "id_producto", "id_medio_suscripcion", "id_origen"]].fillna("nulo")
        operaciones_no_duplicadas[["id_divisa_inicial", "id_divisa_final", "id_estado", "id_producto", "id_medio_suscripcion", "id_origen"]] = operaciones_no_duplicadas[["id_divisa_inicial", "id_divisa_final", "id_estado", "id_producto", "id_medio_suscripcion", "id_origen"]].replace({'nulo':None})

    # # -----------------------------NO SE OCUPA------------------------------------------------------------
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_origen"]][operaciones_no_duplicadas['id_origen'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","compra_venta"]][operaciones_no_duplicadas['compra_venta'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_divisa_inicial"]][operaciones_no_duplicadas['id_divisa_inicial'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_divisa_final"]][operaciones_no_duplicadas['id_divisa_final'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_medio_suscripcion"]][operaciones_no_duplicadas['id_medio_suscripcion'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","fecha_envio"]][operaciones_no_duplicadas['fecha_envio'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","fecha_recepcion"]][operaciones_no_duplicadas['fecha_recepcion'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","folio_contraparte"]][operaciones_no_duplicadas['folio_contraparte'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","observacion"]][operaciones_no_duplicadas['observacion'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_estado"]][operaciones_no_duplicadas['id_estado'].isnull()])
    # #     # print(operaciones_no_duplicadas[["num_operacion","id_producto"]][operaciones_no_duplicadas['id_producto'].isnull()])

    # # ---------------------------------NO SE OCUPA--------------------------------------------------------
    # # operaciones_no_duplicadas.to_excel("envio_contrato_full.xlsx")
    # #     ###----id_tipo_producto------------
    # #     # print(f"OPERACIONES ACTUALES -> {len(operaciones_no_duplicadas)}")

    #     # print(operaciones_no_duplicadas[[
    #     #     "id_origen", "num_operacion", "correlativo", "id_producto", "fecha_operacion"
    #     #     ]])
    #     # print(operaciones_no_duplicadas[[
    #     #     "fecha_vencimiento", "fecha_envio", "fecha_recepcion", "rut_cliente", "id_divisa_inicial"
    #     #     ]])
    #     # print(operaciones_no_duplicadas[[
    #     #     "monto_inicial","tasa_cambio", "id_divisa_final", "monto_final", "compra_venta"
    #     #     ]])
    #     # print(operaciones_no_duplicadas[[
    #     #     "id_medio_suscripcion", "folio_contraparte", "observacion", "id_estado"
    #     #     ]])
    #     # print(operaciones_no_duplicadas[[
    #     #     "nombre_origen"]])
    #     # ----------------------------------NO SE OCUPA-------------------------------------------------------
        if len(operaciones)==0:
            print("insert directo, no requiere filtrar por operaciones nuevas, ya que no hay registros")
            cambios["Operaciones Nuevas"] = len(operaciones_no_duplicadas)

            if len(operaciones_no_duplicadas)>0:
                query = """
                INSERT INTO dbo.operacion (id_origen, num_operacion, correlativo, id_producto, fecha_operacion, fecha_vencimiento,
                fecha_envio, fecha_recepcion, rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final,
                monto_final, compra_venta, id_medio_suscripcion, folio_contraparte, observacion, id_estado) values
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                """
                cursor.executemany(query, operaciones_no_duplicadas[["id_origen", "num_operacion", "correlativo", "id_producto", "fecha_operacion",
                    "fecha_vencimiento", "fecha_envio", "fecha_recepcion", "rut_cliente", "id_divisa_inicial", "monto_inicial",
                    "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta", "id_medio_suscripcion", "folio_contraparte",
                    "observacion", "id_estado"]].values.tolist())
        else:
            #--- crea un codigo para diferencias las operaciones entre si (ayuda a filtrar por mas de un campo)
            #--- el codigo es (id_origen + num_operacion + correlativo)
            operaciones["cod"] = operaciones.apply(lambda row : f"{row['id_origen']}+{row['num_operacion']}+{row['correlativo']}", axis=1)
            operaciones_no_duplicadas["cod"] = operaciones_no_duplicadas.apply(lambda row : f"{row['id_origen']}+{row['num_operacion']}+{row['correlativo']}", axis=1)

            print("pregunta por operaciones que no estan en el sistema, (son nuevas)")

            operaciones_nuevas = operaciones_no_duplicadas[~operaciones_no_duplicadas["cod"].isin(operaciones["cod"])] #operaciones nuevas
            print(f"OPERACIONES NUEVAS -> {len(operaciones_nuevas)}")
            if len(operaciones_nuevas)>0: #significa que existen clientes ingresar
                cambios["Operaciones Nuevas"] = len(operaciones_nuevas)
                query = """
                INSERT INTO dbo.operacion (id_origen, num_operacion, correlativo, id_producto, fecha_operacion, fecha_vencimiento,
                fecha_envio, fecha_recepcion, rut_cliente, id_divisa_inicial, monto_inicial, tasa_cambio, id_divisa_final,
                monto_final, compra_venta, id_medio_suscripcion, folio_contraparte, observacion, id_estado) values
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                """
                cursor.executemany(query, operaciones_nuevas[["id_origen", "num_operacion", "correlativo", "id_producto", "fecha_operacion",
                    "fecha_vencimiento", "fecha_envio", "fecha_recepcion", "rut_cliente", "id_divisa_inicial", "monto_inicial",
                    "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta", "id_medio_suscripcion", "folio_contraparte",
                    "observacion", "id_estado"]].values.tolist())

            operaciones_para_actualizar = operaciones_no_duplicadas[~operaciones_no_duplicadas["cod"].isin(operaciones_nuevas["cod"])] #clientes nuevos
            if len(operaciones_para_actualizar)>0: #significa que existen clientes ingresar
                cambios["Operaciones Actualizadas"] = len(operaciones_para_actualizar)
                print("OPERACIONES PARA ACTUALIZAR")

                query = """UPDATE operacion SET id_origen = ?, id_producto = ?, fecha_operacion = ?, fecha_vencimiento = ?,
                fecha_envio = ?, fecha_recepcion = ?, rut_cliente = ?, id_divisa_inicial = ?, monto_inicial = ?, tasa_cambio = ?,
                id_divisa_final = ?, monto_final = ?, compra_venta = ?, id_medio_suscripcion = ?, folio_contraparte = ?,
                observacion = ?, id_estado = ?
                WHERE num_operacion = ? and correlativo = ?;"""
                cursor.executemany(query, operaciones_para_actualizar[["id_origen", "id_producto", "fecha_operacion",
                    "fecha_vencimiento", "fecha_envio", "fecha_recepcion", "rut_cliente", "id_divisa_inicial", "monto_inicial",
                    "tasa_cambio", "id_divisa_final", "monto_final", "compra_venta", "id_medio_suscripcion", "folio_contraparte",
                    "observacion", "id_estado", "num_operacion", "correlativo"]].values.tolist())

                print(f"numero de operaciones para actualizar: {len(operaciones_para_actualizar)}")
            print("las operaciones fueron actualizadas")
        cursor.commit()

        ## -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------
        # api_gestor.api_estado_clientes()
        # api_gestor.api_actualizar_estado_operaciones()
        ## -------------------------------------Bloqueo de Clientes sin Recepcion-----------------------------

        cursor.close()
        conn.close()
        status = "200"
        fin = time.time()
        print(f"el tiempo de ejecucion es: {fin - inicio}")
        return status, cambios
    except Exception as ex:
        cursor.close()
        conn.close()
        print(ex)
        status = "500"
        cambios = {"Error":"Error en la Consulta"}
        return status, cambios

###-------------------------------------------CARGA_ENVIO_CONTRATOS--------------------------------------------
