import pyodbc, pandas as pd, numpy as np, os
from datetime import date, datetime
import envio, config

config = config.traer_config()




#----------------------------------------------------------------------------------

def api_eliminar_usuario(id_usuario):
    """api_eliminar_usuario"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        DELETE FROM usuario
        WHERE id_usuario = {id_usuario}""")
        cursor.commit()
        cursor.close()
        conn.close()
        return "200"
    except Exception as ex:
        print(ex)
        return "400"


#----------------------------------------------------------------------------------

def api_actualizar_usuario(id_usuario, perfil_usuario, nombre_usuario, hash_pass):
    """api_actualizar_usuario"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        UPDATE usuario SET
        perfil_usuario = '{perfil_usuario}',
        nombre_usuario = '{nombre_usuario}',
        contraseña_usuario = '{hash_pass}'
        WHERE id_usuario = {id_usuario}""")
        cursor.commit()
        cursor.close()
        conn.close()
        return "200"
    except Exception as ex:
        print(ex)
        return "400"

#----------------------------------------------------------------------------------

def api_buscar_usuario_actualizar(id_usuario):
    """api_buscar_usuario_actualizar"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        SELECT id_usuario, perfil_usuario, nombre_usuario, contraseña_usuario
        FROM usuario
        WHERE id_usuario = {id_usuario}
        """)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_usuario", "perfil_usuario","nombre_usuario", "pass_usuario"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

#----------------------------------------------------------------------------------

def api_nuevo_usuario(perfil_usuario, nombre_usuario, pass_usuario):
    """api ingresa un nuevo usuario al sistema"""
    print("dentro de api nuevo usuario")
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        INSERT INTO usuario (perfil_usuario, nombre_usuario, contraseña_usuario) VALUES
        ('{perfil_usuario}', '{nombre_usuario}', '{pass_usuario}')""")
        cursor.commit()
        cursor.close()
        conn.close()
        return "200"
    except Exception as ex:
        print(ex)
        return "400"

#----------------------------------------------------------------------------------

def api_traer_usuarios():
    """api trae todos los usuarios del sistema)"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id_usuario, perfil_usuario, nombre_usuario, contraseña_usuario
        FROM usuario
        """)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_usuario", "perfil_usuario","nombre_usuario", "pass_usuario"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)

#----------------------------------------------------------------------------------

def api_buscar_usuario_login(usuario):
    """api_buscar_usuario_login"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = f"""
        SELECT id_usuario, perfil_usuario, nombre_usuario, contraseña_usuario
        FROM usuario
		WHERE nombre_usuario = '{usuario}'"""
        cursor.execute(query)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_usuario", "perfil_usuario","nombre_usuario", "pass_usuario"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


#----------------------------------------------------------------------------------

def api_estado_operacion(fecha_vencimiento):
    """verifica la fecha de vencimiento con la fecha actual para saber si debe marcar la operacion como vencida o no"""
    fecha_actual = datetime.today()
    if fecha_actual > fecha_vencimiento:
        return 4,1 #vencido - estado_vencido + operacion_bloqueada
    return 2,0 #pendiente - estado_pendiente + operacion_nobloqueada

#----------------------------------------------------------------------------------

def api_nuevo_documento(documento):
    """insert_documento"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = f"""
        INSERT INTO dbo.documento (fecha_inicio_documento, fecha_termino_documento, fecha_envio, fecha_recepcion, id_custodio,
                                    id_tipo_documento, id_estado)
        VALUES ('{documento[0]}','{documento[1]}','{documento[2]}','{documento[3]}',{documento[4]},{documento[5]}, 5);"""
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        status = "200"
        return status
    except Exception as ex:
        print(ex)
        status = "500"
        return status

#----------------------------------------------------------------------------------

def api_eliminar_operacion(id_operacion):
    """api_eliminar_operacion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = f"""DELETE FROM operacion WHERE id_operacion={id_operacion};"""
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
    except Exception as ex:
        print(ex)

# --------------------------------------------------------------------------------


def api_nueva_operacion(operacion):
    """api_nueva_operacion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()

        operacion[3] = "NULL" if (operacion[3]=="0") else f"'{operacion[3]}'"
        if operacion[9] == 0 : operacion[9] = "NULL"     #divisa final llega cero
        if operacion[10] == '0' : operacion[10] = "NULL"     #monto final llega cero

        operacion[11] = "NULL" if (operacion[11]=="") else f"'{operacion[11]}'"     #fechas
        operacion[12] = "NULL" if (operacion[12]=="") else f"'{operacion[12]}'"     #fechas
        if operacion[13] != "NULL" : operacion[13] = f"'{operacion[13]}'"     #fechas
        if operacion[14] != "NULL" : operacion[14] = f"'{operacion[14]}'"     #fechas

        #modificar validacion
        if operacion[15] == 0 : operacion[15] = "NULL"        #mtm llega como cero si es vacio

        query = f"""
        INSERT INTO dbo.operacion (id_origen, id_producto, codigo_trader, rut_ejecutivo, rut_cliente, compra_venta, id_divisa_inicial,
                                    monto_inicial, tasa_cambio, id_divisa_final, monto_final, fecha_operacion, fecha_vencimiento,
                                    fecha_envio, fecha_recepcion, valor_mtm, id_medio_suscripcion, folio_contraparte, comentario,
                                    observacion, id_estado, operacion_vencida, num_operacion)
                values ({operacion[0]},{operacion[1]},'{operacion[2]}',{operacion[3]},'{operacion[4]}','{operacion[5]}',{operacion[6]},
                        {operacion[7]},{operacion[8]},{operacion[9]},{operacion[10]},{operacion[11]},{operacion[12]},{operacion[13]},
                        {operacion[14]},{operacion[15]},{operacion[16]},'{operacion[17]}','{operacion[18]}', '{operacion[19]}',
                        {operacion[20]}, {operacion[21]}, {operacion[22]});"""
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        status = "200"
        return status
    except Exception as ex:
        print(ex)
        status = "500"
        return status
#----------------------------------------------------------------------------------
def api_nueva_operacion_correlativo(operacion):
    """api_nueva_operacion_correlativo"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()

        operacion[3] = "NULL" if (operacion[3]=="0") else f"'{operacion[3]}'"
        if operacion[9] == 0 : operacion[9] = "NULL"     #divisa final llega cero
        if operacion[10] == '0' : operacion[10] = "NULL"     #monto final llega cero

        operacion[11] = "NULL" if (operacion[11]=="") else f"'{operacion[11]}'"     #fechas
        operacion[12] = "NULL" if (operacion[12]=="") else f"'{operacion[12]}'"     #fechas
        if operacion[13] != "NULL" : operacion[13] = f"'{operacion[13]}'"     #fechas
        if operacion[14] != "NULL" : operacion[14] = f"'{operacion[14]}'"     #fechas

        ## pendiente de validacion

        #modificar validacion
        if operacion[15] == 0 : operacion[15] = "NULL"        #mtm llega como cero si es vacio


        query_pre = f"""
        SELECT TOP 1 correlativo
        FROM operacion
        WHERE num_operacion = {operacion[22]} AND id_origen = {operacion[0]}
        ORDER BY correlativo DESC
        """
        cursor.execute(query_pre)


        resultado = cursor.fetchone()
        valor = resultado[0]+1

        query = f"""
        INSERT INTO dbo.operacion (id_origen, id_producto, codigo_trader, rut_ejecutivo, rut_cliente, compra_venta, id_divisa_inicial,
                                    monto_inicial, tasa_cambio, id_divisa_final, monto_final, fecha_operacion, fecha_vencimiento,
                                    fecha_envio, fecha_recepcion, valor_mtm, id_medio_suscripcion, folio_contraparte, comentario,
                                    observacion, id_estado, operacion_vencida, num_operacion, correlativo)
                values ({operacion[0]},{operacion[1]},'{operacion[2]}',{operacion[3]},'{operacion[4]}','{operacion[5]}',{operacion[6]},
                        {operacion[7]},{operacion[8]},{operacion[9]},{operacion[10]},{operacion[11]},{operacion[12]},{operacion[13]},
                        {operacion[14]},{operacion[15]},{operacion[16]},'{operacion[17]}','{operacion[18]}', '{operacion[19]}',
                        {operacion[20]}, {operacion[21]}, {operacion[22]}, {valor});"""
        cursor.execute(query)
        cursor.commit()

        cursor.close()
        conn.close()
        status = "200"
        return status
    except Exception as ex:
        print(ex)
        status = "500"
        return status




#----------------------------------------------------------------------------------
def api_actualizar_operacion(operacion):
    """api_actualizar_operacion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()

        operacion[3] = "NULL" if (operacion[3]=="0") else f"'{operacion[3]}'"
        if operacion[9] == 0 : operacion[9] = "NULL"     #divisa final llega cero
        if operacion[10] == '0' : operacion[10] = "NULL"     #monto final llega cero

        operacion[11] = "NULL" if (operacion[11]=="") else f"'{operacion[11]}'"     #fechas
        operacion[12] = "NULL" if (operacion[12]=="") else f"'{operacion[12]}'"     #fechas
        if operacion[13] != "NULL" : operacion[13] = f"'{operacion[13]}'"     #fechas
        if operacion[14] != "NULL" : operacion[14] = f"'{operacion[14]}'"     #fechas

        #modificar validacion
        if operacion[15] == 0 : operacion[15] = "NULL"        #mtm llega como cero si es vacio

        query = f"""
        UPDATE operacion SET id_origen = {operacion[0]}, id_producto = {operacion[1]}, codigo_trader = '{operacion[2]}',
            rut_ejecutivo = {operacion[3]}, rut_cliente = '{operacion[4]}', compra_venta = '{operacion[5]}',
            id_divisa_inicial = {operacion[6]}, monto_inicial = {operacion[7]}, tasa_cambio = {operacion[8]},
            id_divisa_final = {operacion[9]}, monto_final = {operacion[10]}, fecha_operacion = {operacion[11]},
            fecha_vencimiento = {operacion[12]}, fecha_envio = {operacion[13]}, fecha_recepcion = {operacion[14]},
            valor_mtm = {operacion[15]}, id_medio_suscripcion = {operacion[16]}, folio_contraparte = '{operacion[17]}',
            comentario = '{operacion[18]}', observacion = '{operacion[19]}', num_operacion = {operacion[20]},
            id_estado = {operacion[21]}, operacion_vencida = {operacion[22]}
            WHERE id_operacion={operacion[23]} AND correlativo={operacion[24]};"""
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        return "ok actualizacion bd"
    except Exception as ex:
        print(ex)


#----------------------------------------------------------------------------------
def api_buscar_operacion(id_operacion):
    """api_buscar_operacion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        SELECT op.id_operacion, op.num_operacion, op.correlativo, op.id_origen, op.id_producto, op.compra_venta, op.id_divisa_inicial, op.monto_inicial,
        op.tasa_cambio,
        op.id_divisa_final, op.monto_final,
        op.fecha_operacion,
        op.fecha_vencimiento,
        op.fecha_envio,
        op.fecha_recepcion,
        op.valor_mtm,
        op.folio_contraparte, op.comentario, op.observacion, op.codigo_trader, op.rut_ejecutivo, op.rut_cliente, op.id_medio_suscripcion
        FROM operacion as op
		WHERE id_operacion = {id_operacion};""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_operacion", "num_operacion", "correlativo", "id_origen", "id_producto", "compra_venta",
        "id_divisa_inicial", "monto_inicial", "tasa_cambio", "id_divisa_final", "monto_final", "fecha_operacion", "fecha_vencimiento",
        "fecha_envio", "fecha_recepcion", "valor_mtm", "folio_contraparte", "comentario", "observacion", "codigo_trader", "rut_ejecutivo",
        "rut_cliente", "id_medio_suscripcion"])

        num_operacion, correlativo_actual, id_origen = dataframe["num_operacion"][0], dataframe["correlativo"][0], dataframe["id_origen"][0]
        query_correlativo = f"""
        SELECT TOP 1 correlativo
        FROM operacion
        WHERE num_operacion = {num_operacion} AND id_origen = {id_origen}
        ORDER BY correlativo DESC
        """
        cursor.execute(query_correlativo)
        resultado = cursor.fetchone()
        correlativo_final = resultado[0]
        if(correlativo_actual==correlativo_final):
            dataframe["habilitado"] = "true"
        else:
            dataframe["habilitado"] = "false"
        cursor.close()
        conn.close()
        # print(f"las operaciones que coinciden con el filtro son {len(dataframe)}")
        return dataframe
    except Exception as ex:
        print(ex)


#----------------------------------------------------------------------------------


def api_existe_operacion(num_operacion, sistema_origen):
    """api_existe_operacion"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        print(f"""SELECT monto_inicial, fecha_envio, fecha_recepcion, comentario, num_operacion FROM operacion WHERE
                       num_operacion = {num_operacion};""")
        cursor.execute(f"""
        SELECT op.num_operacion, op.id_origen, op.id_producto, op.compra_venta, op.id_divisa_inicial, op.monto_inicial, op.tasa_cambio,
        op.id_divisa_final, op.monto_final,
        op.fecha_operacion,
        op.fecha_vencimiento,
        op.fecha_envio,
        op.fecha_recepcion,
        op.valor_mtm,
        op.folio_contraparte, op.comentario, op.observacion, op.codigo_trader, op.rut_ejecutivo, op.rut_cliente, op.id_medio_suscripcion
        FROM operacion as op
		WHERE num_operacion = {num_operacion} AND id_origen= {sistema_origen};""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["num_operacion", "id_origen", "id_producto", "compra_venta",
        "id_divisa_inicial", "monto_inicial", "tasa_cambio", "id_divisa_final", "monto_final", "fecha_operacion", "fecha_vencimiento",
        "fecha_envio", "fecha_recepcion", "valor_mtm", "folio_contraparte", "comentario", "observacion", "codigo_trader", "rut_ejecutivo",
        "rut_cliente", "id_medio_suscripcion"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


#----------------------------------------------------------------------------------


def api_traer_operaciones():
    """traer_operaciones"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT op.id_operacion, op.num_operacion, ori.nombre_origen, pro.nombre_producto, cli.rut_cliente, cli.nombre_cliente, ri.nota_riesgo,
        cli.cliente_bloqueado, op.fecha_operacion, op.fecha_vencimiento, op.fecha_envio, op.fecha_recepcion, es.nombre_estado,
        op.folio_contraparte, op.comentario, op.observacion, op.codigo_trader, eq.nombre_ejecutivo, eq.nombre_jefe_grupo, cli.segmento
        FROM operacion as op
        LEFT JOIN producto as pro ON pro.id_producto = op.id_producto
        LEFT JOIN origen as ori ON ori.id_origen = op.id_origen
        LEFT JOIN cliente as cli ON cli.rut_cliente = op.rut_cliente
        LEFT JOIN riesgo as ri ON ri.id_riesgo = cli.id_riesgo
        LEFT JOIN estado as es ON es.id_estado = op.id_estado
        LEFT JOIN equipo_cliente as eq_cli ON eq_cli.rut_cliente = cli.rut_cliente AND eq_cli.activo = 1
        LEFT JOIN equipo as eq ON eq.id_equipo = eq_cli.id_equipo
        """)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_operacion", "num_operacion", "nombre_origen", "nombre_producto", "rut_cliente",
        "nombre_cliente", "nota_riesgo", "cliente_bloqueado", "fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_recepcion",
        "nombre_estado", "folio_contraparte", "comentario", "observacion", "codigo_trader", "nombre_ejecutivo", "nombre_jefe_grupo",
        "segmento"])
        dataframe["cliente_bloqueado"] = dataframe["cliente_bloqueado"].apply(lambda x : "SI" if x == 1 else "NO")
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
def api_bloquear_clientes(clientes):
    """traer_operaciones"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = """
            UPDATE cliente SET cliente_bloqueado = 1
            WHERE rut_cliente = ?;
            """
        cursor.executemany(query, clientes[["rut_cliente"]].values.tolist())
        cursor.commit()
        cursor.close()
        conn.close()
        return "ok"
    except Exception as ex:
        print(ex)

#----------------------------------------------------------------------------------
def api_desbloquear_clientes(clientes):
    """traer_operaciones"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = """
            UPDATE cliente SET cliente_bloqueado = 0
            WHERE rut_cliente = ?;
            """
        cursor.executemany(query, clientes[["rut_cliente"]].values.tolist())
        cursor.commit()
        cursor.close()
        conn.close()
        return "ok"
    except Exception as ex:
        print(ex)

#----------------------------------------------------------------------------------


def api_eliminar_documento(id_documento):
    """api_eliminar_documento"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = f"""DELETE FROM documento WHERE id_documento={id_documento};"""
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
    except Exception as ex:
        print(ex)

#----------------------------------------------------------------------------------
def api_existe_firma(id_documento):
    """api_existe_firma"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""SELECT id_documento FROM firma WHERE id_documento = {id_documento}""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["id_documento"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)


# -------------------------------------------------------------------------------------------------

def api_estado_cliente(rut_cliente):
    """trae las operaciones de un cliente en particular y evalua si el cliente debe ser bloqueado"""
    operaciones_pendientes = api_operaciones_sinrecepcion_cliente(rut_cliente)
    print(operaciones_pendientes)

    if len(operaciones_pendientes) > 0:
        print("el dataframe no esta vacio")
        operaciones_pendientes["fecha_envio"] = operaciones_pendientes["fecha_envio"].astype("datetime64[ns]")
        operaciones_pendientes["fecha_actual"] = operaciones_pendientes["fecha_actual"].astype("datetime64[ns]")
        operaciones_pendientes['dias'] = operaciones_pendientes.apply(lambda row : np.busday_count(row['fecha_envio'].date(),row['fecha_actual'].date()),axis=1)
        # print(operaciones_pendientes)
        para_bloquear = operaciones_pendientes.query("dias >= 8")
        if len(para_bloquear) > 0:
            print("el cliente deberia bloquearse")
            api_bloquea_cliente(rut_cliente)
            print("el cliente fue bloqueado")
        else:
            print("el cliente debe desbloquearse")
            api_desbloquea_cliente(rut_cliente)
            print("el cliente fue desbloquearse")
    else:
        print("el cliente debe desbloquearse")
        api_desbloquea_cliente(rut_cliente)
        print("el cliente fue desbloquearse")
    return "ok"


# -------------------------------------------------------------------------------------------------

def api_estado_clientes():
    """trae las operaciones que estan pendientes de recepcion y evalua las operaciones que deberian bloquear a los clientes con
    fechas_recepcion pendientes"""
    operaciones_pendientes = api_operaciones_sinrecepcion()
    print(f"aqui pregunta si la operacion esta pendiente \n {operaciones_pendientes[operaciones_pendientes['rut_cliente']=='97018000-1']}")

    if len(operaciones_pendientes) > 0:
        print("el dataframe no esta vacio")
        operaciones_pendientes["fecha_envio"] = operaciones_pendientes["fecha_envio"].astype("datetime64[ns]")
        operaciones_pendientes["fecha_actual"] = operaciones_pendientes["fecha_actual"].astype("datetime64[ns]")
        operaciones_pendientes['dias'] = operaciones_pendientes.apply(lambda row : np.busday_count(row['fecha_envio'].date(),row['fecha_actual'].date()),axis=1)
        # print(operaciones_pendientes)
        operaciones_pendientes = operaciones_pendientes.sort_values('dias', ascending=False).drop_duplicates('rut_cliente').sort_index()
        para_bloquear = operaciones_pendientes.query("dias >= 8")

        clientes_bd = envio.traer_clientes()
        para_desbloquear = clientes_bd[~clientes_bd['rut_cliente'].isin(para_bloquear["rut_cliente"])]

        # print(len(para_bloquear))
        # print(len(para_desbloquear))

        if len(para_bloquear) > 0:
            print("los clientes deben bloquearse")
            print(f"dataframe que se debe bloquear {para_bloquear}")
            api_bloquear_clientes(para_bloquear)
            print("los clientes fueron bloqueados")
        if len(para_desbloquear) > 0:
            print("los clientes deben desbloquearse")
            print(f"dataframe que se debe des-bloquear {para_desbloquear}")
            api_desbloquear_clientes(para_desbloquear)
            print("los clientes fueron desbloqueados")
    return "ok"


# ---------------------------------------------------------------------------------------------------------------

def api_operaciones_sinrecepcion_cliente(rut_cliente):
    """api trae las operaciones sin fecha de recepcion (que deberian ser bloqueadas o no segun dias transcurridos )"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        SELECT
        op.rut_cliente, op.fecha_envio, op.fecha_recepcion,
        CAST( GETDATE() AS Date ) as fecha_actual
        FROM operacion as op
        WHERE op.fecha_envio IS NOT NULL AND op.fecha_recepcion IS NULL and rut_cliente = '{rut_cliente}'""")
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["rut_cliente", "fecha_envio", "fecha_recepcion", "fecha_actual"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)
# ---------------------------------------------------------------------------------------------------------------

def api_bloquea_cliente(rut_cliente):
    """api bloquea el cliente con fechas de recepcion pendiente"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        UPDATE cliente SET cliente_bloqueado = 1
        WHERE rut_cliente = '{rut_cliente}'""")
        cursor.commit()
        cursor.close()
        conn.close()
    except Exception as ex:
        print(ex)
# ---------------------------------------------------------------------------------------------------------------

def api_desbloquea_cliente(rut_cliente):
    """api desbloquea el cliente que no tiene recepciones pendientes"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(f"""
        UPDATE cliente SET cliente_bloqueado = 0
        WHERE rut_cliente = '{rut_cliente}'""")
        cursor.commit()
        cursor.close()
        conn.close()
    except Exception as ex:
        print(ex)

#---------------------------------------------------------------------------------------------------------------

def api_operaciones_sinrecepcion():
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

#---------------------------------------------------------------------------------------------------------------

def api_actualizar_estado_operaciones():
    """
    actualiza el estado de las operaciones con validaciones de los campos,
    (operaciones no vencidas, fecha_vencimiento no es nula, fecha vencimiento menor a la fecha actual)
    """
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = """
            UPDATE operacion SET operacion_vencida = 1, id_estado = 4
	        WHERE operacion.operacion_vencida != 1
	        AND fecha_vencimiento IS NOT NULL
	        AND fecha_vencimiento < (SELECT CAST( GETDATE() AS Date ) as fecha_actual)
            """
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        conn.close()
        print("se actualizaron los estados")
        return "ok"
    except Exception as ex:
        print(ex)

    return "ok"


#----------------------------------------------------------------------------------

def api_validar_filtros(num_operacion, nombre_producto, nombre_cliente, rut_cliente, fecha_operacion_inicio, fecha_operacion_termino,
        fecha_vencimiento_inicio, fecha_vencimiento_termino, fecha_envio_inicio, fecha_envio_termino, fecha_recepcion_inicio,
        fecha_recepcion_termino):
    """api_validar_filtros"""

    queryinicial ="""
    SELECT op.id_operacion, op.num_operacion, op.correlativo, ori.nombre_origen, pro.nombre_producto, op.compra_venta, op.id_divisa_inicial,
	op.monto_inicial, op.tasa_cambio, op.id_divisa_final, op.monto_final, op.valor_mtm, op.operacion_vencida, cli.rut_cliente,
    cli.nombre_cliente, ri.nota_riesgo, cli.cliente_bloqueado,
    CONVERT(varchar, op.fecha_operacion,103) as fecha_operacion,
    CONVERT(varchar, op.fecha_vencimiento,103) as fecha_vencimiento,
    CONVERT(varchar, op.fecha_envio,103) as fecha_envio,
    CONVERT(varchar, op.fecha_recepcion,103) as fecha_recepcion,
    es.nombre_estado, op.folio_contraparte, op.comentario, op.observacion, op.codigo_trader, eq.nombre_ejecutivo, eq.nombre_jefe_grupo,
    cli.segmento, op.id_medio_suscripcion, op.id_medio_confirmacion, op.id_envio_confirmacion
    FROM operacion as op
    LEFT JOIN producto as pro ON pro.id_producto = op.id_producto
    LEFT JOIN origen as ori ON ori.id_origen = op.id_origen
    LEFT JOIN cliente as cli ON cli.rut_cliente = op.rut_cliente
    LEFT JOIN riesgo as ri ON ri.id_riesgo = cli.id_riesgo
    LEFT JOIN estado as es ON es.id_estado = op.id_estado
    LEFT JOIN equipo_cliente as eq_cli ON eq_cli.rut_cliente = cli.rut_cliente AND eq_cli.activo = 1
    LEFT JOIN equipo as eq ON eq.id_equipo = eq_cli.id_equipo
	WHERE"""

    if num_operacion != "":
        num_operacion = f" op.num_operacion LIKE '{num_operacion}%' AND"
    if nombre_producto != "":
        nombre_producto = f" pro.nombre_producto = '{nombre_producto}' AND"
    if nombre_cliente != "":
        nombre_cliente = f" cli.nombre_cliente LIKE '%{nombre_cliente}%' AND"
    if rut_cliente != "":
        rut_cliente = f" cli.rut_cliente LIKE '%{rut_cliente}%' AND"
    if fecha_operacion_inicio != "":
        fecha_operacion_inicio = f" op.fecha_operacion >= '{datetime.strptime(fecha_operacion_inicio, '%d/%m/%Y')}' AND"
    if fecha_operacion_termino != "":
        fecha_operacion_termino = f" op.fecha_operacion <= '{datetime.strptime(fecha_operacion_termino, '%d/%m/%Y')}' AND"
    if fecha_vencimiento_inicio != "":
        fecha_vencimiento_inicio = f" op.fecha_vencimiento >= '{datetime.strptime(fecha_vencimiento_inicio, '%d/%m/%Y')}' AND"
    if fecha_vencimiento_termino != "":
        fecha_vencimiento_termino = f" op.fecha_vencimiento <= '{datetime.strptime(fecha_vencimiento_termino, '%d/%m/%Y')}' AND"
    if fecha_envio_inicio != "":
        fecha_envio_inicio = f" op.fecha_envio >='{datetime.strptime(fecha_envio_inicio, '%d/%m/%Y')}' AND"
    if fecha_envio_termino != "":
        fecha_envio_termino = f" op.fecha_envio <= '{datetime.strptime(fecha_envio_termino, '%d/%m/%Y')}' AND"
    if fecha_recepcion_inicio != "":
        fecha_recepcion_inicio = f" op.fecha_recepcion >= '{datetime.strptime(fecha_recepcion_inicio, '%d/%m/%Y')}' AND"
    if fecha_recepcion_termino != "":
        fecha_recepcion_termino = f" op.fecha_recepcion <= '{datetime.strptime(fecha_recepcion_termino, '%d/%m/%Y')}' AND"

    query = queryinicial + num_operacion + nombre_producto + nombre_cliente + rut_cliente + fecha_operacion_inicio + fecha_operacion_termino + fecha_vencimiento_inicio + fecha_vencimiento_termino + fecha_envio_inicio + fecha_envio_termino + fecha_recepcion_inicio + fecha_recepcion_termino

    query = query.rstrip("AND")
    query = query.rstrip("WHERE")
    # query = query + "order by num_operacion asc, correlativo"
    query = query + "order by id_operacion"
    # print(query)

    return query


#----------------------------------------------------------------------------------

def api_operaciones_filtradas(query):
    """api_operaciones_filtradas"""

    medios = envio.traer_medios()
    estados = envio.traer_estados()
    divisas = envio.traer_divisas()

    medios_suscripcion = medios.query("nombre_campo == 'suscripcion'")
    medios_confirmacion = medios.query("nombre_campo == 'confirmacion'")
    envio_confirmacion = estados.query("nombre_campo == 'estado_confirmacion'")

    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        cursor.execute(query)
        resultado = cursor.fetchall()

        dataframe = pd.DataFrame.from_records(resultado,
        columns=["id_operacion", "num_operacion", "correlativo", "nombre_origen", "nombre_producto", "compra_venta", "divisa_inicial",
                "monto_inicial", "tasa_cambio", "divisa_final", "monto_final", "valor_mtm", "operacion_vencida", "rut_cliente",
        "nombre_cliente", "nota_riesgo", "cliente_bloqueado", "fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_recepcion",
        "nombre_estado", "folio_contraparte", "comentario", "observacion", "codigo_trader", "nombre_ejecutivo", "nombre_jefe_grupo",
        "segmento", "medio_suscripcion", "medio_confirmacion", "envio_confirmacion"])
        dataframe["cliente_bloqueado"] = dataframe["cliente_bloqueado"].apply(lambda x : "SI" if x == 1 else "NO")
        dataframe["operacion_vencida"] = dataframe["operacion_vencida"].apply(lambda x : "SI" if x == 1 else "NO")
        dataframe["compra_venta"] = dataframe["compra_venta"].apply(lambda x : "Venta" if x == "S" else ("Compra" if x == "B" else x ))

        dataframe["divisa_inicial"] = dataframe["divisa_inicial"].fillna(0)
        dataframe["divisa_inicial"] = dataframe["divisa_inicial"].astype(int)
        join_divisa_inicial = pd.merge(dataframe , divisas, left_on=['divisa_inicial'], right_on=['id_divisa'], how="left")
        dataframe["divisa_inicial"] = join_divisa_inicial["codigo_divisa"]

        dataframe["divisa_final"] = dataframe["divisa_final"].fillna(0)
        dataframe["divisa_final"] = dataframe["divisa_final"].astype(int)
        join_divisa_final = pd.merge(dataframe , divisas, left_on=['divisa_final'], right_on=['id_divisa'], how="left")
        dataframe["divisa_final"] = join_divisa_final["codigo_divisa"]

        dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].fillna(0)
        dataframe["medio_suscripcion"] = dataframe["medio_suscripcion"].astype(int)
        join_suscripcion = pd.merge(dataframe , medios_suscripcion, left_on=['medio_suscripcion'], right_on=['id_medio'], how="left")
        dataframe["medio_suscripcion"] = join_suscripcion["nombre_medio"]

        dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].fillna(0)
        dataframe["medio_confirmacion"] = dataframe["medio_confirmacion"].astype(int)
        join_confirmacion = pd.merge(dataframe , medios_confirmacion, left_on=['medio_confirmacion'], right_on=['id_medio'], how="left")
        dataframe["medio_confirmacion"] = join_confirmacion["nombre_medio"]

        dataframe["envio_confirmacion"] = dataframe["envio_confirmacion"].fillna(0)
        dataframe["envio_confirmacion"] = dataframe["envio_confirmacion"].astype(int)
        join_envio = pd.merge(dataframe , envio_confirmacion, left_on=['envio_confirmacion'], right_on=['id_estado'], how="left")
        dataframe["envio_confirmacion"] = join_envio["nombre_estado_y"]

        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)



def api_traer_feriados():
    """api_traer_feriados"""
    try:
        conn = pyodbc.connect(config)
        cursor = conn.cursor()
        query = """
        SELECT fecha_feriado, nombre_feriado, tipo_feriado, irrenunciable FROM feriado
        """
        cursor.execute(query)
        resultado = cursor.fetchall()
        dataframe = pd.DataFrame.from_records(resultado, columns=["fecha_feriado", "nombre_feriado", "tipo_feriado", "irrenunciable"])
        cursor.close()
        conn.close()
        return dataframe
    except Exception as ex:
        print(ex)