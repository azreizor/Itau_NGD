import os, pathlib, json, ast, pandas as pd, sys, numpy as np
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from datetime import datetime, date
from flask_bcrypt import Bcrypt
from flask_session import Session
import inputs, envio, api_gestor, definitions

# from flaskwebgui import FlaskUI
# from waitress import serve

from definitions import ROOT_DIR_TEMPLATE, ROOT_DIR_STATIC

app = Flask(__name__, template_folder=ROOT_DIR_TEMPLATE, static_folder=ROOT_DIR_STATIC)
bcrypt = Bcrypt(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ui = FlaskUI(app, start_server='flask', close_server_on_exit = False)       ### flask web gui

# ui = FlaskUI(app, start_server='flask')       ### flask web gui

app.secret_key = "43718690059058520452752962918477289469"

##---------------------------------------------------------------------------

@app.route("/usuario_tabla")
def usuario_tabla():
    """usuario_tabla"""
    if not session.get("usuario"):
        return redirect("/login")
    usuarios = api_gestor.api_traer_usuarios()
    user = session.get("usuario")
    if user["perfil"] == "Administrador":
        return render_template("usuario_tabla.html", usuarios = usuarios, usuario = session.get("usuario"))
    return redirect("/login")

##--------------------------------

@app.route("/api_eliminar_usuario", methods=['POST'])
def api_eliminar_usuario():
    """api_eliminar_usuario"""
    id_usuario = request.form["id_usuario"]
    response = api_gestor.api_eliminar_usuario(id_usuario)
    return response

##--------------------------------

@app.route("/api_actualizar_usuario", methods=['POST'])
def api_actualizar_usuario():
    """api_actualizar_usuario"""
    id_usuario = request.form["id_usuario"]
    perfil_usuario = request.form["perfil_usuario"]
    nombre_usuario = request.form["nombre_usuario"]
    pass_usuario = request.form["contraseña_usuario"]
    hash_pass = bcrypt.generate_password_hash(pass_usuario, 14).decode('utf-8')
    response = api_gestor.api_actualizar_usuario(id_usuario, perfil_usuario, nombre_usuario, hash_pass)
    return response

##--------------------------------

@app.route("/api_nuevo_usuario", methods=['POST'])
def api_nuevo_usuario():
    """api_nuevo_usuario"""
    perfil_usuario = request.form["perfil_usuario"]
    nombre_usuario = request.form["nombre_usuario"]
    pass_usuario = request.form["contraseña_usuario"]
    print("antes del hash")
    hash_pass = bcrypt.generate_password_hash(pass_usuario, 14).decode('utf-8')
    print("despues del hash")
    response = api_gestor.api_nuevo_usuario(perfil_usuario, nombre_usuario, hash_pass)
    return response

##--------------------------------

@app.route("/api_buscar_usuario", methods=['GET', 'POST'])
def api_buscar_usuario():
    """api_buscar_usuario"""
    id_usuario = request.form["id_usuario"]
    print(f" usuario para la busqueda -- {id_usuario}")
    usuario = api_gestor.api_buscar_usuario_actualizar(id_usuario)
    print(usuario)
    data = usuario.to_json(orient='index')
    return data

##--------------------------------

@app.route("/api_traer_usuarios", methods=['GET'])
def api_traer_usuarios():
    """api_traer_usuarios"""
    usuarios = api_gestor.api_traer_usuarios()
    data = usuarios.to_json(orient='index')
    return data

##---------------------------------------------------------------------------

# @app.route("/estado_columnas_operacion", methods=['GET'])
# def estado_columnas_operacion():
#     """estado_columnas_operacion"""
#     session.permanent = False
#     if not session.get("operaciones"):
#         print("significa que aun no esta seteada la variable")
#         session["operaciones"] = "false"
#         estado = session["operaciones"]
#         return jsonify(estado)
#     session["operaciones"] = "true"
#     estado = session["operaciones"]
#     return jsonify(session["operaciones"])


# @app.route("/traer_columnas_operacion", methods=['GET'])
# def traer_columnas_operacion():
#     """traer_columnas_operacion"""
#     session.permanent = False
#     if not session.get("operaciones"):
#         print("significa que aun no esta seteada la variable")
#         session["operaciones"] = []
#         print("agrega las columnas a la sesion")
#         columnas = session["operaciones"]
#         print("entrega la variable sesion a una nueva variable")
#         return jsonify(columnas)
#     print("dice que ya existe una sesion")
#     return jsonify(session["operaciones"])


# @app.route("/actualizar_columnas_operacion", methods=['POST'])
# def actualizar_columnas_operacion():
#     """actualizar_columnas_operacion"""
#     num_columna = int(request.form["num_columna"])
#     estado = request.form["estado"]
#     columnas = session["operaciones"]

#     print("actualizar_columnas_operacion")

#     if estado == "visible":
#         columnas.remove(num_columna)
#         session["operaciones"] = columnas
#     if estado == "oculta":
#         columnas.append(num_columna)
#         session["operaciones"] = columnas
#     # print(session["operaciones"])
#     return "200"

##---------------------------------------------------------------------------

@app.route("/")
@app.route("/login")
def login():
    """login"""
    session.pop("usuario", None)
    return render_template("login.html")

##--------------------------------------------

@app.route("/logout")
def logout():
    """logout"""
    session.pop("usuario", None)
    return redirect("/login")

##--------------------------------------------

@app.route("/api_login_usuario", methods=['POST'])
def api_login_usuario():
    """api_login_usuario"""
    nombre_usuario = request.form["usuario"]
    pass_usuario = request.form["pass_usuario"]
    resultado = api_gestor.api_buscar_usuario_login(nombre_usuario)
    if(len(resultado)==1):
        response = bcrypt.check_password_hash(resultado["pass_usuario"][0], pass_usuario) #  True
        if(response):
            session["usuario"] = {"hash":resultado["pass_usuario"][0], "perfil":resultado["perfil_usuario"][0]}
            return "200"
    return "400"

##---------------------------------------------------------------------------

@app.route("/reporte_bloqueados")
def reporte_bloqueados():
    """reporte_bloqueados"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        envio.generar_reporte_bloqueados()
        now = datetime.now()
        now = now.strftime("%Y_%m_%d %H-%M-%S")
        return render_template("reporte_bloqueados.html", now = now, usuario = session.get("usuario"))
    return redirect("/login")


@app.route("/reporte_institucionales")
def reporte_institucionales():
    """reporte_institucionales"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        envio.generar_reporte_institucionales()
        return render_template("reporte_institucionales.html", usuario = session.get("usuario"))
    return redirect("/login")

###--------------------------------------------------------------------------

@app.route("/api_eliminar_operacion", methods=['POST'])
def api_eliminar_operacion():
    """api_eliminar_operacion"""
    id_operacion = request.form["id_operacion"]
    print("id de la operacion es")
    print(id_operacion)
    api_gestor.api_eliminar_operacion(id_operacion)
    return "ok"


@app.route("/api_nueva_operacion", methods=['POST'])
def api_nueva_operacion():
    """api_nueva_operacion"""
    num_operacion = int(request.form["num_operacion"])
    sistema_origen = int(request.form["sistema_origen"])
    producto = int(request.form["producto"])
    codigo_trader = request.form["codigo_trader"]
    rut_ejecutivo = request.form["rut_ejecutivo"]
    rut_cliente = request.form["rut_cliente"]
    compra_venta = request.form["compra_venta"]
    divisa_inicial = int(request.form["divisa_inicial"])
    precio_inicial = f"{request.form['precio_inicial']}"
    tasa_cambio = f"{request.form['tasa_cambio']}"
    divisa_final = int(request.form["divisa_final"])
    precio_final = f"{request.form['precio_final']}"
    fecha_operacion = request.form["fecha_operacion"]
    fecha_vencimiento = request.form["fecha_vencimiento"]
    fecha_envio = request.form["fecha_envio"]
    fecha_recepcion = request.form["fecha_recepcion"]
    valor_mtm = f"{request.form['valor_mtm']}"
    medio_suscripcion = int(request.form["medio_suscripcion"])
    folio_contraparte = request.form["folio_contraparte"]
    comentario = request.form["comentario"]
    observacion = request.form["observacion"]

    fecha_operacion = datetime.strptime(fecha_operacion, '%d/%m/%Y')
    fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%d/%m/%Y')
    if fecha_envio != 'NULL':
        fecha_envio = datetime.strptime(fecha_envio, '%d/%m/%Y')
    if fecha_recepcion != 'NULL':
        fecha_recepcion = datetime.strptime(fecha_recepcion, '%d/%m/%Y')

    estado_operacion, operacion_bloqueada = api_gestor.api_estado_operacion(fecha_vencimiento)
    operacion = [sistema_origen, producto, codigo_trader, rut_ejecutivo, rut_cliente, compra_venta, divisa_inicial,
                precio_inicial, tasa_cambio, divisa_final, precio_final, fecha_operacion, fecha_vencimiento, fecha_envio,
                fecha_recepcion, valor_mtm, medio_suscripcion, folio_contraparte, comentario, observacion, estado_operacion,
                operacion_bloqueada, num_operacion]
    api_gestor.api_nueva_operacion(operacion)
    api_gestor.api_estado_cliente(rut_cliente)
    return redirect("/tabla_operaciones")



@app.route("/api_nueva_operacion_correlativo", methods=['POST'])
def api_nueva_operacion_correlativo():
    """api_nueva_operacion_correlativo"""
    num_operacion = int(request.form["num_operacion"])
    sistema_origen = int(request.form["sistema_origen"])
    producto = int(request.form["producto"])
    codigo_trader = request.form["codigo_trader"]
    rut_ejecutivo = request.form["rut_ejecutivo"]
    rut_cliente = request.form["rut_cliente"]
    compra_venta = request.form["compra_venta"]
    divisa_inicial = int(request.form["divisa_inicial"])
    precio_inicial = f"{request.form['precio_inicial']}"
    tasa_cambio = f"{request.form['tasa_cambio']}"
    divisa_final = int(request.form["divisa_final"])
    precio_final = f"{request.form['precio_final']}"
    fecha_operacion = request.form["fecha_operacion"]
    fecha_vencimiento = request.form["fecha_vencimiento"]
    fecha_envio = request.form["fecha_envio"]
    fecha_recepcion = request.form["fecha_recepcion"]
    valor_mtm = f"{request.form['valor_mtm']}"
    medio_suscripcion = int(request.form["medio_suscripcion"])
    folio_contraparte = request.form["folio_contraparte"]
    comentario = request.form["comentario"]
    observacion = request.form["observacion"]

    fecha_operacion = datetime.strptime(fecha_operacion, '%d/%m/%Y')
    fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%d/%m/%Y')
    if fecha_envio != 'NULL':
        fecha_envio = datetime.strptime(fecha_envio, '%d/%m/%Y')
    if fecha_recepcion != 'NULL':
        fecha_recepcion = datetime.strptime(fecha_recepcion, '%d/%m/%Y')

    estado_operacion, operacion_bloqueada = api_gestor.api_estado_operacion(fecha_vencimiento)
    operacion = [sistema_origen, producto, codigo_trader, rut_ejecutivo, rut_cliente, compra_venta, divisa_inicial,
                precio_inicial, tasa_cambio, divisa_final, precio_final, fecha_operacion, fecha_vencimiento, fecha_envio,
                fecha_recepcion, valor_mtm, medio_suscripcion, folio_contraparte, comentario, observacion, estado_operacion,
                operacion_bloqueada, num_operacion]
    api_gestor.api_nueva_operacion_correlativo(operacion)
    api_gestor.api_estado_cliente(rut_cliente)
    return redirect("/tabla_operaciones")

#-----------------------------------------------------------------------------------------------------

@app.route("/api_buscar_datos_operaciones", methods=['GET'])
def api_buscar_datos_operaciones():
    """api_buscar_datos_operaciones esta semi eliminada, verificar en futuro"""
    traders = envio.traer_traders()
    ejecutivos = envio.traer_ejecutivo()
    clientes = envio.traer_clientes()
    origenes = envio.traer_origenes()
    operaciones = envio.traer_productos()
    divisas = envio.traer_divisas()
    medios = envio.traer_medios_suscripcion()
    traders_json = traders.to_json(orient='index')
    ejecutivos_json = ejecutivos.to_json(orient='index')
    clientes_json = clientes.to_json(orient='index')
    origenes_json = origenes.to_json(orient='index')
    operaciones_json = operaciones.to_json(orient='index')
    divisas_json = divisas.to_json(orient='index')
    medios_json = medios.to_json(orient='index')
    data = dict()
    data[traders_json] =traders_json
    data[ejecutivos_json] =ejecutivos_json
    data[clientes_json] = clientes_json
    data[origenes_json] = origenes_json
    data[operaciones_json] = operaciones_json
    data[divisas_json] = divisas_json
    data[medios_json] = medios_json
    return data



@app.route("/api_existe_operacion", methods=['POST'])
def api_existe_operacion():
    """api_existe_operacion"""
    num_operacion = request.form["num_operacion"]
    sistema_origen = request.form["sistema_origen"]
    operacion = api_gestor.api_existe_operacion(num_operacion, sistema_origen)
    print("aqui se trae la operacion encontrada si es que existe")
    if (len(operacion)>0):
        print("el num ya esta ocupado, error")
        return "400"
    else:
        print("el numero esta disponible, todo ok")
        return "200"

#-----------------------------------------------------------------------------------------------------

@app.route("/api_buscar_operacion", methods=['POST'])
def api_buscar_operacion():
    """api_buscar_operacion"""
    id_operacion = request.form["id_operacion"]
    operacion = api_gestor.api_buscar_operacion(id_operacion)

    operacion['fecha_operacion'] = pd.to_datetime(operacion['fecha_operacion'])
    operacion['fecha_vencimiento'] = pd.to_datetime(operacion['fecha_vencimiento'])
    operacion['fecha_envio'] = pd.to_datetime(operacion['fecha_envio'])
    operacion['fecha_recepcion'] = pd.to_datetime(operacion['fecha_recepcion'])

    operacion['fecha_operacion'] = operacion['fecha_operacion'].dt.strftime('%d/%m/%Y')
    operacion['fecha_vencimiento'] = operacion['fecha_vencimiento'].dt.strftime('%d/%m/%Y')
    operacion['fecha_envio'] = operacion['fecha_envio'].dt.strftime('%d/%m/%Y')
    operacion['fecha_recepcion'] = operacion['fecha_recepcion'].dt.strftime('%d/%m/%Y')

    data = operacion.to_json(orient='index')
    # print(data)
    return data

#-----------------------------------------------------------------------------------------------------


@app.route("/api_actualizar_operacion", methods=['POST'])
def api_actualizar_operacion():
    """api_actualizar_operacion"""
    id_operacion = int(request.form["id_operacion"])
    num_operacion = int(request.form["num_operacion"])
    correlativo = int(request.form["correlativo"])
    sistema_origen = int(request.form["sistema_origen"])
    producto = int(request.form["producto"])
    codigo_trader = request.form["codigo_trader"]
    rut_ejecutivo = request.form["rut_ejecutivo"]
    rut_cliente = request.form["rut_cliente"]
    compra_venta = request.form["compra_venta"]
    divisa_inicial = int(request.form["divisa_inicial"])
    precio_inicial = f"{request.form['precio_inicial']}"
    tasa_cambio = f"{request.form['tasa_cambio']}"
    divisa_final = int(request.form["divisa_final"])
    precio_final = f"{request.form['precio_final']}"
    fecha_operacion = request.form["fecha_operacion"]
    fecha_vencimiento = request.form["fecha_vencimiento"]
    fecha_envio = request.form["fecha_envio"]
    fecha_recepcion = request.form["fecha_recepcion"]
    valor_mtm = f"{request.form['valor_mtm']}"
    medio_suscripcion = int(request.form["medio_suscripcion"])
    folio_contraparte = request.form["folio_contraparte"]
    comentario = request.form["comentario"]
    observacion = request.form["observacion"]

    fecha_operacion = datetime.strptime(fecha_operacion, '%d/%m/%Y')
    fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%d/%m/%Y')
    if fecha_envio != 'NULL':
        fecha_envio = datetime.strptime(fecha_envio, '%d/%m/%Y')
    if fecha_recepcion != 'NULL':
        fecha_recepcion = datetime.strptime(fecha_recepcion, '%d/%m/%Y')

    estado_operacion, operacion_bloqueada = api_gestor.api_estado_operacion(fecha_vencimiento)
    operacion = [sistema_origen, producto, codigo_trader, rut_ejecutivo, rut_cliente, compra_venta, divisa_inicial,
                precio_inicial, tasa_cambio, divisa_final, precio_final, fecha_operacion, fecha_vencimiento, fecha_envio,
                fecha_recepcion, valor_mtm, medio_suscripcion, folio_contraparte, comentario, observacion, num_operacion,
                estado_operacion, operacion_bloqueada, id_operacion, correlativo]
    print(operacion)
    api_gestor.api_actualizar_operacion(operacion)
    api_gestor.api_estado_cliente(rut_cliente)

    return "ok"


@app.route("/api_traer_operaciones")
def api_traer_operaciones():
    """api_traer_operaciones"""
    operaciones = api_gestor.api_traer_operaciones()

    operaciones['fecha_operacion'] = pd.to_datetime(operaciones['fecha_operacion'])
    operaciones['fecha_vencimiento'] = pd.to_datetime(operaciones['fecha_vencimiento'])
    operaciones['fecha_envio'] = pd.to_datetime(operaciones['fecha_envio'])
    operaciones['fecha_recepcion'] = pd.to_datetime(operaciones['fecha_recepcion'])

    operaciones['fecha_operacion'] = operaciones['fecha_operacion'].dt.strftime('%d-%m-%Y')
    operaciones['fecha_vencimiento'] = operaciones['fecha_vencimiento'].dt.strftime('%d-%m-%Y')
    operaciones['fecha_envio'] = operaciones['fecha_envio'].dt.strftime('%d-%m-%Y')
    operaciones['fecha_recepcion'] = operaciones['fecha_recepcion'].dt.strftime('%d-%m-%Y')

    # print(operaciones[["fecha_operacion", "fecha_vencimiento", "fecha_envio", "fecha_recepcion"]])

    # data = operaciones.to_json(orient='index')
    data = operaciones.to_json(orient='records')
    # parsed = json.loads(result)
    # resultado = json.dumps(parsed, indent=4)
    return data




@app.route("/api_filtrar_operaciones", methods=['POST'])
def api_filtrar_operaciones():
    """api_filtrar_operaciones"""

    num_operacion = request.form["num_operacion"]
    nombre_producto = request.form["nombre_producto"]
    nombre_cliente = request.form["nombre_cliente"]
    rut_cliente = request.form["rut_cliente"]

    fecha_operacion_inicio = request.form["fecha_operacion_inicio"]
    fecha_operacion_termino = request.form["fecha_operacion_termino"]
    fecha_vencimiento_inicio = request.form["fecha_vencimiento_inicio"]
    fecha_vencimiento_termino = request.form["fecha_vencimiento_termino"]
    fecha_envio_inicio = request.form["fecha_envio_inicio"]
    fecha_envio_termino = request.form["fecha_envio_termino"]
    fecha_recepcion_inicio = request.form["fecha_recepcion_inicio"]
    fecha_recepcion_termino = request.form["fecha_recepcion_termino"]

    query = api_gestor.api_validar_filtros(num_operacion, nombre_producto, nombre_cliente, rut_cliente, fecha_operacion_inicio, fecha_operacion_termino,
        fecha_vencimiento_inicio, fecha_vencimiento_termino, fecha_envio_inicio, fecha_envio_termino, fecha_recepcion_inicio,
        fecha_recepcion_termino)

    operaciones = api_gestor.api_operaciones_filtradas(query)
    data = operaciones.to_json(orient='records')

    return data

#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------


@app.route("/api_nuevo_documento", methods=['POST'])
def api_nuevo_documento():
    """api_nuevo_documento"""

    fecha_inicio = request.form["fecha_inicio"]
    fecha_termino = request.form["fecha_termino"]
    fecha_envio = request.form["fecha_envio"]
    fecha_recepcion = request.form["fecha_recepcion"]
    id_custodio = int(request.form["id_custodio"])
    id_tipo_documento = int(request.form["id_tipo_documento"])

    fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y')
    fecha_termino = datetime.strptime(fecha_termino, '%d/%m/%Y')
    fecha_envio = datetime.strptime(fecha_envio, '%d/%m/%Y')
    fecha_recepcion = datetime.strptime(fecha_recepcion, '%d/%m/%Y')

    documento = [fecha_inicio, fecha_termino, fecha_envio, fecha_recepcion, id_custodio, id_tipo_documento]
    # print(documento)
    status = api_gestor.api_nuevo_documento(documento)

    return redirect("/tabla_documentos")




###codigo pendiente para la validacion de la firma antes de eliminar un documento
###codigo pendiente para la validacion de la firma antes de eliminar un documento
###codigo pendiente para la validacion de la firma antes de eliminar un documento
@app.route("/api_existe_firma", methods=['POST'])
def api_existe_firma():
    """api_existe_firma"""
    id_documento = request.form["id_documento"]
    print(id_documento)
    firma = api_gestor.api_existe_firma(id_documento)
    data = firma.to_json(orient='records')
    return data


@app.route("/api_eliminar_documento", methods=['POST'])
def api_eliminar_documento():
    """api_eliminar_documento"""
    id_documento = request.form["id_documento"]
    api_gestor.api_eliminar_documento(id_documento)
    return "ok"




####------------------------------------------------------------------------------------

@app.route("/formularios/", methods=["POST"])
def formularios():
    """formularios"""
    if request.method == 'POST':
        origen = request.form["origen"]
        if origen == 'nueva_firma':
            print("formulario nueva firma")
            id_documento = int(request.form["id_documento"])
            id_apoderado = int(request.form["id_apoderado"])
            fecha_firma = request.form["fecha_firma"]
            fecha_firma = datetime.strptime(fecha_firma, '%d/%m/%Y')
            firma = [id_documento, id_apoderado, fecha_firma]
            status = envio.insert_firma_documento(firma)
            return redirect(f"/tabla_documentos/?status={status}")

    return redirect("/tabla_operaciones/?status=600")



##---------------------------------------------------------------------------
###----------menu de operaciones
# trae las operaciones del sistema y los datos para poblar el formulario de operaciones
@app.route("/tabla_operaciones/", methods=['GET'])
@app.route("/tabla_operaciones")
def tabla_operaciones():
    """tabla_operaciones"""
    if not session.get("usuario"):
        return redirect("/login")
    traders = envio.traer_traders()
    ejecutivos = envio.traer_ejecutivo()
    clientes = envio.traer_clientes()
    origenes = envio.traer_origenes()
    productos = envio.traer_productos()
    divisas = envio.traer_divisas()
    medios = envio.traer_medios_suscripcion()

    return render_template("tabla_operaciones.html",
                           productos = productos, traders = traders, ejecutivos = ejecutivos, clientes = clientes,
                           origenes = origenes, divisas = divisas, medios = medios, usuario = session.get("usuario"))


###------menu de operaciones
##---------------------------------------------------------------------------

##---------------------------------------------------------------------------
###----------menu de documentos

@app.route("/tabla_documentos/", methods=['GET'])
@app.route("/tabla_documentos")
def tabla_documentos():
    """tabla_documentos"""
    if not session.get("usuario"):
        return redirect("/login")

    status = request.args.get('status')
    documentos = envio.traer_documentos_tabla()

    documentos['fecha_inicio_documento'] = pd.to_datetime(documentos['fecha_inicio_documento'])
    documentos['fecha_termino_documento'] = pd.to_datetime(documentos['fecha_termino_documento'])
    documentos['fecha_envio'] = pd.to_datetime(documentos['fecha_envio'])
    documentos['fecha_recepcion'] = pd.to_datetime(documentos['fecha_recepcion'])

    documentos['fecha_inicio_documento'] = documentos['fecha_inicio_documento'].dt.strftime('%d-%m-%Y')
    documentos['fecha_termino_documento'] = documentos['fecha_termino_documento'].dt.strftime('%d-%m-%Y')
    documentos['fecha_envio'] = documentos['fecha_envio'].dt.strftime('%d-%m-%Y')
    documentos['fecha_recepcion'] = documentos['fecha_recepcion'].dt.strftime('%d-%m-%Y')
    custodios = envio.traer_custodios()
    tipo_documentos = envio.traer_tipo_documento()
    return render_template("tabla_documentos.html", documentos = documentos, status = status, tipo_documentos = tipo_documentos,custodios = custodios, usuario = session.get("usuario"))

###------menu de documentos
##---------------------------------------------------------------------------


##---------------------------------------------------------------------------
###----------menu de firmas

@app.route("/tabla_firmas/", methods=['GET'])
@app.route("/tabla_firmas")
def tabla_firmas():
    """tabla_firmas"""
    if not session.get("usuario"):
        return redirect("/login")
    status = request.args.get('status')
    firmas = envio.traer_firmas_tabla()
    return render_template("tabla_firmas.html", firmas = firmas, status = status , usuario = session.get("usuario"))

@app.route("/nueva_firma/", methods=['GET'])
def nueva_firma():
    if not session.get("usuario"):
        return redirect("/login")
    id_documento = request.args.get('id_documento')
    documento = envio.buscar_documento(id_documento)
    apoderados = envio.traer_apoderados()
    return render_template("nueva_firma.html", documento = documento, apoderados = apoderados, usuario = session.get("usuario"))

###------menu de firmas
##---------------------------------------------------------------------------


@app.route("/tabla_clientes")
def tabla_clientes():
    """tabla_clientes"""
    if not session.get("usuario"):
        return redirect("/login")
    clientes = envio.traer_clientes()
    return render_template("tabla_clientes.html", clientes = clientes, usuario = session.get("usuario"))


## ---------------------------------------------------------------------------

@app.route("/carga_findur")
@app.route("/carga_findur/", methods=['GET'])
def carga_findur():
    """carga_findur"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_findur.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")

@app.route("/carga_murex/", methods=['GET'])
def carga_murex():
    """carga_murex"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_murex.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")

@app.route("/carga_contraparte/", methods=['GET'])
def carga_contraparte():
    """carga_contraparte"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_contraparte.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")

@app.route("/carga_confirmaciones/", methods=['GET'])
def carga_confirmaciones():
    """carga_confirmaciones"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_confirmaciones.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")

@app.route("/carga_rco/", methods=['GET'])
def carga_rco():
    """carga_rco"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_rco.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")


@app.route("/carga_base_full")
@app.route("/carga_base_full/", methods=['GET'])
def carga_base_full():
    """carga_base_full"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_base_full.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")


@app.route("/carga_envio_contratos")
@app.route("/carga_envio_contratos/", methods=['GET'])
def carga_envio_contratos():
    """carga_envio_contratos"""
    if not session.get("usuario"):
        return redirect("/login")
    user = session.get("usuario")
    if user["perfil"] in ["Administrador", "Usuario"]:
        status = request.args.get('status')
        cambios = request.args.get('cambios')
        cambios = f"{cambios}"
        cambios = ast.literal_eval(cambios)
        return render_template("carga_envio_contratos.html", status = status, cambios = cambios, usuario = session.get("usuario"))
    return redirect("/login")


##--------------------------------------------------------------------------



@app.route("/subir_archivo", methods=["GET", "POST"])
def subir_archivo():
    """subir_archivo"""
    if request.method == 'POST':
        origen = request.form["origen"]
        excel = request.files["archivoexcel"]
        if origen == 'findur':
            status, cambios = inputs.carga_findur(excel)
            return redirect(f"/carga_findur/?status={status}&cambios={cambios}")

        if origen == 'murex':
            status, cambios = inputs.carga_murex(excel)
            return redirect(f"/carga_murex/?status={status}&cambios={cambios}")

        if origen == 'contraparte':
            status, cambios = inputs.carga_contraparte(excel)
            return redirect(f"/carga_contraparte/?status={status}&cambios={cambios}")

        if origen == 'confirmaciones':
            status, cambios = inputs.carga_confirmaciones(excel)
            return redirect(f"/carga_confirmaciones/?status={status}&cambios={cambios}")

        if origen == 'rco':
            status, cambios = inputs.carga_rco(excel)
            return redirect(f"/carga_rco/?status={status}&cambios={cambios}")

        if origen == 'base_full':
            status, cambios = inputs.carga_base_full(excel)
            return redirect(f"/carga_base_full/?status={status}&cambios={cambios}")

        if origen == 'envio_contratos':
            print("ENTRA EN EL envio_contrato")
            status, cambios = inputs.carga_envio_contratos(excel)
            return redirect(f"/carga_envio_contratos/?status={status}&cambios={cambios}")

    return redirect("/index")

#----------------------------------------------------------------


####--------------------- FOR FLASK -----------------------
app.run(port=5001, debug=True)
if __name__ == '__main__':
    app.run(debug=True)
####--------------------- FOR FLASK -----------------------

# if __name__ == "__main__":
#     ui.run()



