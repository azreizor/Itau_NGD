window.onload = function() {
    var URLactual = location.pathname;
    console.log(URLactual)

    if (URLactual == ('/usuario_tabla')){
        // js_llenar_tabla_usuarios()
        // js_traer_operaciones()
    }
};

function showAlert(icon,title,html,timer){
    Swal.fire({
        icon: icon,
        title:title,
        html: html,
        timer: timer
    })
}


// $("#modal_nueva_operacion").modal('hide')
// $("#correlativo_div").show();
// $("#correlativo_div").hide();
// $("#sistema_origen").prop('disabled', false);
// $("#envio_nueva_operacion").html("Ingresar Operacion");





// //------------------LIMPIA EL MODAL AL CERRAR------------------------------

// function js_cerrar_modal_operacion(){
//     $(this).find('#formulario_nueva_operacion').trigger('reset');
//     $("#id_operacion").val('')
//     $("#num_operacion").val('')
//     $('#sistema_origen').val('').trigger('change.select2');
//     $('#producto').val('').trigger('change.select2');
//     $('#codigo_trader').val('').trigger('change.select2');
//     $('#rut_ejecutivo').val('').trigger('change.select2');
//     $('#compra_venta').val('').trigger('change.select2');
//     $('#rut_cliente').val('').trigger('change.select2');
//     $('#divisa_inicial').val('').trigger('change.select2');
//     $("#precio_inicial").val('')
//     $("#tasa_cambio").val('')
//     $('#divisa_final').val('').trigger('change.select2');
//     $("#precio_final").val('')
//     $("#fecha_operacion").val('')
//     $("#fecha_vencimiento").val('')
//     $("#fecha_envio").val('')
//     $("#fecha_recepcion").val('')
//     $("#valor_mtm").val()
//     $('#medio_suscripcion').val('').trigger('change.select2');
//     $("#folio_contraparte").val('')
//     $("#comentario").val('')
//     $("#observacion").val('')
// }
//   //------------------LIMPIA EL MODAL AL CERRAR------------------------------



//   //------------------AL MOSTRAR MODAL------------------------------
//   function js_mostrar_modal_operacion(){
//     // validacion de los campos y divs para mostrar en el modal segun sea el caso
//     // validacion si esta habilitado para boton nuevo correlativo
//     if($("#id_operacion").val() == 0){
//         $("#envio_nueva_operacion").html("Ingresar Operacion");
//         $("#num_operacion").prop('disabled', false);
//         $("#sistema_origen").prop('disabled', false);

//         $("#envio_nuevo_correlativo").hide();
//         $("#correlativo_div").hide();
//     }else{
//         $("#envio_nueva_operacion").html("Actualizar Operacion");

//         if($("#habilitado").val() == "true"){
//             $("#envio_nuevo_correlativo").show();
//             $("#correlativo_div").show();
//         }
//         if($("#habilitado").val() == "false"){
//             $("#envio_nuevo_correlativo").hide();
//             $("#correlativo_div").hide();
//         }
//     }
//   }
//   //------------------AL MOSTRAR MODAL------------------------------

// //------------------VALIDACION AL APRETAR BOTON SUBMIT------------------------------
// function js_validar_formulario_operacion(){
//     var valido = $("#formulario_nueva_operacion").valid()
//     // "02/09/2022"split("/")-> ['02','09','2022']->reverse() ->['2022','09','02']-> join('-') -> 2022-09-02
//     //SE OBTIENE LA FECHA Y SE ACOMODA
//     const fecha_vencimiento = $("#fecha_vencimiento").val().split("/").reverse().join("-")
//     const fecha_operacion   = $("#fecha_operacion").val().split("/").reverse().join("-")
//     const fecha_envio       = $("#fecha_envio").val().split('/').reverse().join('-')
//     const fecha_recepcion   = $("#fecha_recepcion").val().split('/').reverse().join('-')

//     // SE COMVIERTE A MILISENGUNDOS
//     const fecha_ven = Date.parse(fecha_vencimiento)
//     const fecha_ope = Date.parse(fecha_operacion)
//     const fecha_env = Date.parse(fecha_envio)
//     const fecha_rec = Date.parse(fecha_recepcion)

//     if(fecha_ope>fecha_ven) return showAlert('error','Fecha rechazada','La fecha de vencimiento debe ser mayor a la de operación.',5000)
//     if(fecha_env<fecha_ope) return showAlert('error','Fecha rechazada','La fecha de envio debe ser mayor a la de operación.',5000)
//     if(fecha_env>fecha_rec) return showAlert('error','Fecha rechazada','La fecha de recpción debe ser mayor o igual a la de envío.',5000)

//     if(!valido){
//       return showAlert('error','Campos faltantes','No se logro completar la acción.',5000)
//     }

//     const idOperacion = $("#id_operacion").val()
//     const mensaje = idOperacion=== 0 ? 'Operacion Ingresada con exito' : 'Operacion Actualizada con exito.'

//     $("#modal_nueva_operacion").modal('hide')

//     if(idOperacion == 0)
//         js_nueva_operacion() //funcion envio operacion
//     else
//         js_actualizar_operacion() //funcion envio operacion

//     $("#tabla_operaciones").DataTable().clear()
//     js_inicializa_operaciones()

//     showAlert('success','Cambios Realizados',mensaje,2000)

//     function showAlert(icon,title,html,timer){
//         Swal.fire({
//             icon: icon,
//             title:title,
//             html: html,
//             timer: timer
//         })
//     }
// }
// //------------------VALIDACION AL ENVIAR CORRELATIVO NUEVO------------------------------

// function js_validar_formulario_correlativo(){
//     var valido = $("#formulario_nueva_operacion").valid()

//     const fecha_vencimiento = $("#fecha_vencimiento").val().split("/").reverse().join("-")
//     const fecha_operacion   = $("#fecha_operacion").val().split("/").reverse().join("-")
//     const fecha_envio       = $("#fecha_envio").val().split('/').reverse().join('-')
//     const fecha_recepcion   = $("#fecha_recepcion").val().split('/').reverse().join('-')

//     // SE COMVIERTE A MILISENGUNDOS
//     const fecha_ven = Date.parse(fecha_vencimiento)
//     const fecha_ope = Date.parse(fecha_operacion)
//     const fecha_env = Date.parse(fecha_envio)
//     const fecha_rec = Date.parse(fecha_recepcion)

//     if(fecha_ope>fecha_ven) return showAlert('error','Fecha rechazada','La fecha de vencimiento debe ser mayor a la de operación.',5000)
//     if(fecha_env<fecha_ope) return showAlert('error','Fecha rechazada','La fecha de envio debe ser mayor a la de operación.',5000)
//     if(fecha_env>fecha_rec) return showAlert('error','Fecha rechazada','La fecha de recpción debe ser mayor o igual a la de envío.',5000)

//     if(!valido){
//       return showAlert('error','Campos faltantes','No se logro completar la acción.',5000)
//     }

//     $("#modal_nueva_operacion").modal('hide')
//     js_nueva_operacion_correlativo() //funcion envio operacion

//     showAlert('success','nuevo correlativo','operacion nueva guardada',2000)

//     $("#tabla_operaciones").DataTable().clear()
//     js_inicializa_operaciones()

//     function showAlert(icon,title,html,timer){
//         Swal.fire({
//             icon: icon,
//             title:title,
//             html: html,
//             timer: timer
//         })
//     }
// }
// //------------------VALIDACION AL ENVIAR CORRELATIVO NUEVO------------------------------


// //------------------VALIDACION DEL BUSCADOR DE OPERACIONES------------------------------
// function js_validar_filtrar_operaciones(){

//     num_operacion = $("#fil_num_operacion").val()
//     nombre_producto = $("#fil_nombre_producto").val()
//     nombre_cliente = $("#fil_nombre_cliente").val()
//     rut_cliente = $("#fil_rut_cliente").val()
//     fecha_operacion_inicio = $("#fil_fecha_operacion_inicio").val().split("/").reverse().join("-")
//     fecha_operacion_termino = $("#fil_fecha_operacion_termino").val().split("/").reverse().join("-")
//     fecha_vencimiento_inicio = $("#fil_fecha_vencimiento_inicio").val().split('/').reverse().join('-')
//     fecha_vencimiento_termino = $("#fil_fecha_vencimiento_termino").val().split('/').reverse().join('-')
//     fecha_envio_inicio = $("#fil_fecha_envio_inicio").val().split("/").reverse().join("-")
//     fecha_envio_termino = $("#fil_fecha_envio_termino").val().split("/").reverse().join("-")
//     fecha_recepcion_inicio = $("#fil_fecha_recepcion_inicio").val().split('/').reverse().join('-')
//     fecha_recepcion_termino = $("#fil_fecha_recepcion_termino").val().split('/').reverse().join('-')

//     campos = [num_operacion,nombre_producto ,nombre_cliente,rut_cliente,fecha_operacion_inicio,fecha_operacion_termino,
//         fecha_vencimiento_inicio,fecha_vencimiento_termino,fecha_envio_inicio,fecha_envio_termino,fecha_recepcion_inicio,
//         fecha_recepcion_termino]

//     vacios = campos.filter(elemento => {
//         return elemento != '';
//     });
//     console.log(vacios.length);

//     if (vacios.length==0) {
//         Swal.fire({
//             title: 'Advertencia Campos Vacios',
//             text: "Evite la sobrecarga de la consulta realizando filtros en las operaciones",
//             icon: 'warning',
//             showCancelButton: true,
//             cancelButtonColor: '#22bb33',
//             confirmButtonColor: '#d33',
//             cancelButtonText: 'Ok, Volver',
//             confirmButtonText: 'Continuar',
//             reverseButtons: true
//           }).then((result) => {
//             if (result.isConfirmed) {
//               js_filtrar_operaciones()
//               console.log("trae operaciones filtros");
//             }
//           })
//     }else{
//         // SE COMVIERTE A MILISENGUNDOS
//         fecha_op_inicio = Date.parse(fecha_operacion_inicio)
//         fecha_op_termino = Date.parse(fecha_operacion_termino)
//         fecha_ven_inicio = Date.parse(fecha_vencimiento_inicio)
//         fecha_ven_termino = Date.parse(fecha_vencimiento_termino)
//         fecha_env_inicio = Date.parse(fecha_envio_inicio)
//         fecha_env_termino = Date.parse(fecha_envio_termino)
//         fecha_rec_inicio = Date.parse(fecha_recepcion_inicio)
//         fecha_rec_termino = Date.parse(fecha_recepcion_termino)

//         if(fecha_op_inicio>fecha_op_termino) return showAlert('error','Fecha rechazada','La fecha operacion inicio no puede ser mayor a la fecha de termino.',5000)
//         if(fecha_ven_inicio>fecha_ven_termino) return showAlert('error','Fecha rechazada','La fecha vencimiento inicio no puede ser mayor a la fecha de termino.',5000)
//         if(fecha_env_inicio>fecha_env_termino) return showAlert('error','Fecha rechazada','La fecha envio inicio no puede ser mayor a la fecha de termino.',5000)
//         if(fecha_rec_inicio>fecha_rec_termino) return showAlert('error','Fecha rechazada','La fecha recepcion inicio no puede ser mayor a la fecha de termino.',5000)
//         js_filtrar_operaciones()
//     }

//     function showAlert(icon,title,html,timer){
//       Swal.fire({
//           icon: icon,
//           title:title,
//           html: html,
//           timer: timer
//       })
//     }
// }

// //-------------------------------------------------------------------

// function js_nueva_operacion(){
//     num_operacion = $("#num_operacion").val()
//     sistema_origen = $("#sistema_origen").val()
//     producto = $("#producto").val()
//     codigo_trader = $("#codigo_trader").val()
//     rut_ejecutivo = $("#rut_ejecutivo").val()==null ? 0:$("#rut_ejecutivo").val()
//     rut_cliente = $("#rut_cliente").val()
//     compra_venta = $("#compra_venta").val()==null ? 0:$("#compra_venta").val()
//     divisa_inicial = $("#divisa_inicial").val()
//     precio_inicial = $("#precio_inicial").val()
//     tasa_cambio = $("#tasa_cambio").val()
//     divisa_final = $("#divisa_final").val()==null ? 0:$("#divisa_final").val()
//     precio_final = $("#precio_final").val()=="" ? 0:$("#precio_final").val()
//     fecha_operacion = $("#fecha_operacion").val()
//     fecha_vencimiento = $("#fecha_vencimiento").val()
//     fecha_envio = $("#fecha_envio").val()=="" ? "NULL":$("#fecha_envio").val()
//     fecha_recepcion = $("#fecha_recepcion").val()=="" ? "NULL":$("#fecha_recepcion").val()
//     valor_mtm = $("#valor_mtm").val()=="" ? 0:$("#valor_mtm").val()
//     medio_suscripcion = $("#medio_suscripcion").val()
//     folio_contraparte = $("#folio_contraparte").val()
//     comentario = $("#comentario").val()
//     observacion = $("#observacion").val()

//     var parametros = {
//         "num_operacion":num_operacion,
//         "sistema_origen":sistema_origen,
//         "producto":producto,
//         "codigo_trader":codigo_trader,
//         "rut_ejecutivo":rut_ejecutivo,
//         "rut_cliente":rut_cliente,
//         "compra_venta":compra_venta,
//         "divisa_inicial":divisa_inicial,
//         "precio_inicial":precio_inicial,
//         "tasa_cambio":tasa_cambio,
//         "divisa_final":divisa_final,
//         "precio_final":precio_final,
//         "fecha_operacion":fecha_operacion,
//         "fecha_vencimiento":fecha_vencimiento,
//         "fecha_envio":fecha_envio,
//         "fecha_recepcion":fecha_recepcion,
//         "valor_mtm":valor_mtm,
//         "medio_suscripcion":medio_suscripcion,
//         "folio_contraparte":folio_contraparte,
//         "comentario":comentario,
//         "observacion":observacion
//     }
//     $.ajax({
//         data:  parametros,
//         dataType: "json",
//         async: false,
//         url:   "/api_nueva_operacion",
//         type:  'post',
//         beforeSend: function () {
//             $("#resultado").html("Procesando, espere por favor...");
//         },
//         success:  function (response) {
//             console.log(response)
//         }
//     });
//     document.getElementById("formulario_nueva_operacion").reset();
//     $("#num_operacion").val()
//     $("#sistema_origen").val()
//     $("#producto").val()
//     $("#codigo_trader").val()
//     $("#rut_ejecutivo").val()
//     $("#rut_cliente").val()
//     $("#compra_venta").val()
//     $("#divisa_inicial").val()
//     $("#precio_inicial").val()
//     $("#tasa_cambio").val()
//     $("#divisa_final").val()
//     $("#precio_final").val()
//     $("#fecha_operacion").val()
//     $("#fecha_vencimiento").val()
//     $("#fecha_envio").val()
//     $("#fecha_recepcion").val()
//     $("#valor_mtm").val()
//     $("#medio_suscripcion").val()
//     $("#folio_contraparte").val()
//     $("#comentario").val()
//     $("#observacion").val()
// }



// //-------------------------------------------------------------------

// function js_nueva_operacion_correlativo(){
//     num_operacion = $("#num_operacion").val()
//     sistema_origen = $("#sistema_origen").val()
//     producto = $("#producto").val()
//     codigo_trader = $("#codigo_trader").val()
//     rut_ejecutivo = $("#rut_ejecutivo").val()==null ? 0:$("#rut_ejecutivo").val()
//     rut_cliente = $("#rut_cliente").val()
//     compra_venta = $("#compra_venta").val()==null ? 0:$("#compra_venta").val()
//     divisa_inicial = $("#divisa_inicial").val()
//     precio_inicial = $("#precio_inicial").val()
//     tasa_cambio = $("#tasa_cambio").val()
//     divisa_final = $("#divisa_final").val()==null ? 0:$("#divisa_final").val()
//     precio_final = $("#precio_final").val()=="" ? 0:$("#precio_final").val()
//     fecha_operacion = $("#fecha_operacion").val()
//     fecha_vencimiento = $("#fecha_vencimiento").val()
//     fecha_envio = $("#fecha_envio").val()=="" ? "NULL":$("#fecha_envio").val()
//     fecha_recepcion = $("#fecha_recepcion").val()=="" ? "NULL":$("#fecha_recepcion").val()
//     valor_mtm = $("#valor_mtm").val()=="" ? 0:$("#valor_mtm").val()
//     medio_suscripcion = $("#medio_suscripcion").val()
//     folio_contraparte = $("#folio_contraparte").val()
//     comentario = $("#comentario").val()
//     observacion = $("#observacion").val()

//     var parametros = {
//         "num_operacion":num_operacion,
//         "sistema_origen":sistema_origen,
//         "producto":producto,
//         "codigo_trader":codigo_trader,
//         "rut_ejecutivo":rut_ejecutivo,
//         "rut_cliente":rut_cliente,
//         "compra_venta":compra_venta,
//         "divisa_inicial":divisa_inicial,
//         "precio_inicial":precio_inicial,
//         "tasa_cambio":tasa_cambio,
//         "divisa_final":divisa_final,
//         "precio_final":precio_final,
//         "fecha_operacion":fecha_operacion,
//         "fecha_vencimiento":fecha_vencimiento,
//         "fecha_envio":fecha_envio,
//         "fecha_recepcion":fecha_recepcion,
//         "valor_mtm":valor_mtm,
//         "medio_suscripcion":medio_suscripcion,
//         "folio_contraparte":folio_contraparte,
//         "comentario":comentario,
//         "observacion":observacion
//     }
//     $.ajax({
//         data:  parametros,
//         dataType: "json",
//         async: false,
//         url:   "/api_nueva_operacion_correlativo",
//         type:  'post',
//         beforeSend: function () {
//             $("#resultado").html("Procesando, espere por favor...");
//         },
//         success:  function (response) {
//             console.log(response)
//         }
//     });
//     document.getElementById("formulario_nueva_operacion").reset();
//     $("#num_operacion").val()
//     $("#sistema_origen").val()
//     $("#correlativo").val()
//     $("#producto").val()
//     $("#codigo_trader").val()
//     $("#rut_ejecutivo").val()
//     $("#rut_cliente").val()
//     $("#compra_venta").val()
//     $("#divisa_inicial").val()
//     $("#precio_inicial").val()
//     $("#tasa_cambio").val()
//     $("#divisa_final").val()
//     $("#precio_final").val()
//     $("#fecha_operacion").val()
//     $("#fecha_vencimiento").val()
//     $("#fecha_envio").val()
//     $("#fecha_recepcion").val()
//     $("#valor_mtm").val()
//     $("#medio_suscripcion").val()
//     $("#folio_contraparte").val()
//     $("#comentario").val()
//     $("#observacion").val()
// }
// //-------------------------------------------------------------------

// function js_actualizar_operacion(){
//     id_operacion = $("#id_operacion").val()
//     num_operacion = $("#num_operacion").val()
//     correlativo = $("#correlativo").val()
//     sistema_origen = $("#sistema_origen").val()
//     producto = $("#producto").val()
//     codigo_trader = $("#codigo_trader").val()
//     rut_ejecutivo = $("#rut_ejecutivo").val()==null ? 0:$("#rut_ejecutivo").val()
//     rut_cliente = $("#rut_cliente").val()
//     compra_venta = $("#compra_venta").val()==null ? 0:$("#compra_venta").val()
//     divisa_inicial = $("#divisa_inicial").val()
//     precio_inicial = $("#precio_inicial").val()
//     tasa_cambio = $("#tasa_cambio").val()
//     divisa_final = $("#divisa_final").val()==null ? 0:$("#divisa_final").val()
//     precio_final = $("#precio_final").val()=="" ? 0:$("#precio_final").val()
//     fecha_operacion = $("#fecha_operacion").val()
//     fecha_vencimiento = $("#fecha_vencimiento").val()
//     fecha_envio = $("#fecha_envio").val()=="" ? "NULL":$("#fecha_envio").val()
//     fecha_recepcion = $("#fecha_recepcion").val()=="" ? "NULL":$("#fecha_recepcion").val()
//     valor_mtm = $("#valor_mtm").val()=="" ? 0:$("#valor_mtm").val()
//     medio_suscripcion = $("#medio_suscripcion").val()
//     folio_contraparte = $("#folio_contraparte").val()
//     comentario = $("#comentario").val()
//     observacion = $("#observacion").val()
//     num_operacion = $("#num_operacion").val()

//     var parametros = {
//         "id_operacion":id_operacion,
//         "num_operacion":num_operacion,
//         "correlativo":correlativo,
//         "sistema_origen":sistema_origen,
//         "producto":producto,
//         "codigo_trader":codigo_trader,
//         "rut_ejecutivo":rut_ejecutivo,
//         "rut_cliente":rut_cliente,
//         "compra_venta":compra_venta,
//         "divisa_inicial":divisa_inicial,
//         "precio_inicial":precio_inicial,
//         "tasa_cambio":tasa_cambio,
//         "divisa_final":divisa_final,
//         "precio_final":precio_final,
//         "fecha_operacion":fecha_operacion,
//         "fecha_vencimiento":fecha_vencimiento,
//         "fecha_envio":fecha_envio,
//         "fecha_recepcion":fecha_recepcion,
//         "valor_mtm":valor_mtm,
//         "medio_suscripcion":medio_suscripcion,
//         "folio_contraparte":folio_contraparte,
//         "comentario":comentario,
//         "observacion":observacion,
//         "num_operacion":num_operacion
//     }

//     $.ajax({
//         data:  parametros,
//         dataType: "json",
//         async: false,
//         url:   "/api_actualizar_operacion",
//         type:  'post',
//         beforeSend: function () {
//                 $("#resultado").html("Procesando, espere por favor...");
//         },
//         success:  function (response) {
//             console.log(response)
//         }
//     });

//     document.getElementById("formulario_nueva_operacion").reset();
//     $("#id_operacion").val()
//     $("#num_operacion").val()
//     $("#correlativo").val()
//     $("#sistema_origen").val()
//     $("#producto").val()
//     $("#codigo_trader").val()
//     $("#rut_ejecutivo").val()
//     $("#rut_cliente").val()
//     $("#compra_venta").val()
//     $("#divisa_inicial").val()
//     $("#precio_inicial").val()
//     $("#tasa_cambio").val()
//     $("#divisa_final").val()
//     $("#precio_final").val()
//     $("#fecha_operacion").val()
//     $("#fecha_vencimiento").val()
//     $("#fecha_envio").val()
//     $("#fecha_recepcion").val()
//     $("#valor_mtm").val()
//     $("#medio_suscripcion").val()
//     $("#folio_contraparte").val()
//     $("#comentario").val()
//     $("#observacion").val()
// }
// //-------------------------------------------------------------------


// //-------------------------------------------------------------------
// function js_buscar_operacion(id_operacion){
//     var parametros = {
//         "id_operacion" : id_operacion
//     };
//     $.ajax({
//         data:  parametros,
//         dataType: "json",
//         async: false,
//         url:   "/api_buscar_operacion",
//         type:  'post',
//         beforeSend: function () {
//                 $("#resultado").html("Procesando, espere por favor...");
//         },
//         success:  function (response) {
//             $("#id_operacion").val(response[0].id_operacion);
//             $("#num_operacion").val(response[0].num_operacion);
//             $("#num_operacion").prop('disabled', true);
//             $("#correlativo").val(response[0].correlativo);
//             $("#correlativo").prop('disabled', true);
//             $('#sistema_origen').val(response[0].id_origen).trigger('change.select2');
//             $("#sistema_origen").prop('disabled', true);
//             $('#producto').val(response[0].id_producto).trigger('change.select2');
//             $('#codigo_trader').val(response[0].codigo_trader).trigger('change.select2');
//             $('#rut_ejecutivo').val(response[0].rut_ejecutivo).trigger('change.select2');
//             $('#rut_cliente').val(response[0].rut_cliente).trigger('change.select2');
//             $("#compra_venta").val(response[0].compra_venta).trigger('change.select2');
//             $('#divisa_inicial').val(response[0].id_divisa_inicial).trigger('change.select2');
//             $("#precio_inicial").val(response[0].monto_inicial)
//             $("#tasa_cambio").val(response[0].tasa_cambio)
//             $('#divisa_final').val(response[0].id_divisa_final).trigger('change.select2');
//             $("#precio_final").val(response[0].monto_final)
//             $("#fecha_operacion").val(response[0].fecha_operacion)
//             $("#fecha_vencimiento").val(response[0].fecha_vencimiento)
//             $("#fecha_envio").val(response[0].fecha_envio)
//             $("#fecha_recepcion").val(response[0].fecha_recepcion)
//             $("#valor_mtm").val(response[0].valor_mtm)
//             $('#medio_suscripcion').val(response[0].id_medio_suscripcion).trigger('change.select2');
//             $("#folio_contraparte").val(response[0].folio_contraparte)
//             $("#comentario").val(response[0].comentario)
//             $("#observacion").val(response[0].observacion)

//             $("#habilitado").val(response[0].habilitado)
//         }
//     });
// }


// function js_eliminar_operacion(id_operacion){
//     var parametros = {
//         "id_operacion" : id_operacion
//     };

//     const swalWithBootstrapButtons = Swal.mixin({
//         customClass: {
//         confirmButton: 'btn btn-success',
//         cancelButton: 'btn btn-danger'
//         },
//         buttonsStyling: false
//         })

//     swalWithBootstrapButtons.fire({
//         title: 'Estas Seguro?',
//         text: "La operacion sera borrada definitivamente",
//         icon: 'warning',
//         showCancelButton: true,
//         confirmButtonText: 'Si, Borrala!',
//         cancelButtonText: 'No, Cancelar!',
//         reverseButtons: true
//     }).then((result) => {
//         if (result.isConfirmed){
//             $.ajax({
//                 data:  parametros,
//                 dataType: "json",
//                 async: false,
//                 url:   "/api_eliminar_operacion",
//                 type:  'post',
//                 beforeSend: function () {
//                     $("#resultado").html("Procesando, espere por favor...");
//                 },
//                 success:  function (response) {
//                     console.log(response)
//                 }
//             });
//             swalWithBootstrapButtons.fire(
//                 'Borrada',
//                 'La operacion fue borrada',
//                 'success'
//             )
//             location.reload();
//         }
//     })
// }

// function js_nueva_operacion(){
//     num_operacion = $("#num_operacion").val()
//     sistema_origen = $("#sistema_origen").val()
//     producto = $("#producto").val()
//     codigo_trader = $("#codigo_trader").val()
//     rut_ejecutivo = $("#rut_ejecutivo").val()==null ? 0:$("#rut_ejecutivo").val()
//     rut_cliente = $("#rut_cliente").val()
//     compra_venta = $("#compra_venta").val()==null ? 0:$("#compra_venta").val()
//     divisa_inicial = $("#divisa_inicial").val()
//     precio_inicial = $("#precio_inicial").val()
//     tasa_cambio = $("#tasa_cambio").val()
//     divisa_final = $("#divisa_final").val()==null ? 0:$("#divisa_final").val()
//     precio_final = $("#precio_final").val()=="" ? 0:$("#precio_final").val()
//     fecha_operacion = $("#fecha_operacion").val()
//     fecha_vencimiento = $("#fecha_vencimiento").val()
//     fecha_envio = $("#fecha_envio").val()=="" ? "NULL":$("#fecha_envio").val()
//     fecha_recepcion = $("#fecha_recepcion").val()=="" ? "NULL":$("#fecha_recepcion").val()
//     valor_mtm = $("#valor_mtm").val()=="" ? 0:$("#valor_mtm").val()
//     medio_suscripcion = $("#medio_suscripcion").val()
//     folio_contraparte = $("#folio_contraparte").val()
//     comentario = $("#comentario").val()
//     observacion = $("#observacion").val()

//     var parametros = {
//         "num_operacion":num_operacion,
//         "sistema_origen":sistema_origen,
//         "producto":producto,
//         "codigo_trader":codigo_trader,
//         "rut_ejecutivo":rut_ejecutivo,
//         "rut_cliente":rut_cliente,
//         "compra_venta":compra_venta,
//         "divisa_inicial":divisa_inicial,
//         "precio_inicial":precio_inicial,
//         "tasa_cambio":tasa_cambio,
//         "divisa_final":divisa_final,
//         "precio_final":precio_final,
//         "fecha_operacion":fecha_operacion,
//         "fecha_vencimiento":fecha_vencimiento,
//         "fecha_envio":fecha_envio,
//         "fecha_recepcion":fecha_recepcion,
//         "valor_mtm":valor_mtm,
//         "medio_suscripcion":medio_suscripcion,
//         "folio_contraparte":folio_contraparte,
//         "comentario":comentario,
//         "observacion":observacion
//     }

//     $.ajax({
//         data:  parametros,
//         dataType: "json",
//         async: false,
//         url:   "/api_nueva_operacion",
//         type:  'post',
//         beforeSend: function () {
//                 $("#resultado").html("Procesando, espere por favor...");
//         },
//         success:  function (response) {
//                 //$("#resultado").html(response);
//                 console.log(response)
//         }
//     });

//     document.getElementById("formulario_nueva_operacion").reset();
//     $("#num_operacion").val()
//     $("#sistema_origen").val()
//     $("#producto").val()
//     $("#codigo_trader").val()
//     $("#rut_ejecutivo").val()
//     $("#rut_cliente").val()
//     $("#compra_venta").val()
//     $("#divisa_inicial").val()
//     $("#precio_inicial").val()
//     $("#tasa_cambio").val()
//     $("#divisa_final").val()
//     $("#precio_final").val()
//     $("#fecha_operacion").val()
//     $("#fecha_vencimiento").val()
//     $("#fecha_envio").val()
//     $("#fecha_recepcion").val()
//     $("#valor_mtm").val()
//     $("#medio_suscripcion").val()
//     $("#folio_contraparte").val()
//     $("#comentario").val()
//     $("#observacion").val()
// }

// //-------------------------------------------------------------------

// //-------------------------------------------------------------------

// function js_eliminar_operacion(id_operacion){
//     var parametros = {
//       "id_operacion" : id_operacion
//     };

//     const swalWithBootstrapButtons = Swal.mixin({
//         customClass: {
//             confirmButton: 'btn btn-success',
//             cancelButton: 'btn btn-danger'
//         },
//         buttonsStyling: false
//     })

//     swalWithBootstrapButtons.fire({
//         title: 'Estas Seguro?',
//         text: "La operacion sera borrada definitivamente",
//         icon: 'warning',
//         showCancelButton: true,
//         confirmButtonText: 'Si, Borrala!',
//         cancelButtonText: 'No, Cancelar!',
//         reverseButtons: true
//     }).then((result) => {
//         if (result.isConfirmed) {
//             $.ajax({
//                 data:  parametros,
//                 dataType: "json",
//                 async: false,
//                 url:   "/api_eliminar_operacion",
//                 type:  'post',
//                 beforeSend: function () {
//                     $("#resultado").html("Procesando, espere por favor...");
//                 },
//                 success:  function (response) {
//                     console.log(response)
//                 }
//             });
//             swalWithBootstrapButtons.fire(
//                 'Borrada',
//                 'La operacion fue borrada',
//                 'success'
//             )
//             location.reload();
//         }
//     })
// }


// function js_validacion_operacion(){
//     const num_operacion   = $('#num_operacion').val()
//     const sistema_origen  = $('#sistema_origen').val()

//     if(num_operacion!==''  && sistema_origen!=='' && sistema_origen){
//         parametros = {
//             'num_operacion': num_operacion,
//             'sistema_origen': sistema_origen
//         }
//         $.ajax({
//             data:  parametros,
//             dataType: "json",
//             async: false,
//             url:   "/api_existe_operacion",
//             method:  'post',
//             beforeSend: function () {
//                 $("#resultado").html("Procesando, espere por favor...");
//             },
//             success:  function (response) {
//                 if (response == "400") {
//                     $("#num_operacion").val('')
//                     $("#num_operacion").focus()
//                     Swal.fire({
//                         icon: 'warning',
//                         title:'Error en la operación',
//                         text: "El numero de operacion o sistema de origen ya existe",
//                         timer: 5000
//                     })
//                 }
//             }
//         });
//     }
// }

// //-------------------------------------------------------------------
// //-------------------------------------------------------------------

// // function js_traer_columnas_operacion(){
// //     var resultado
// //     $.ajax({
// //         dataType: "json",
// //         async: false,
// //         url:   "/traer_columnas_operacion",
// //         method:  'get',
// //         beforeSend: function () {
// //             $("#resultado").html("Procesando, espere por favor...");
// //         },
// //         success:  function (response) {
// //             resultado = response
// //         }
// //     })
// //     return resultado
// // }


// // function js_traer_estado_columnas_operacion(){
// //     var resultado
// //     $.ajax({
// //         dataType: "json",
// //         async: false,
// //         url:   "/estado_columnas_operacion",
// //         method:  'get',
// //         beforeSend: function () {
// //             $("#resultado").html("Procesando, espere por favor...");
// //         },
// //         success:  function (response) {
// //             resultado = response
// //         }
// //     })
// //     return resultado
// // }

// //-------------------------------------------------------------------
// //-------------------------------------------------------------------

// // function js_actualizar_columnas_operacion(columna, estado){

// //     console.log("actualizar_columnas_operacion");

// //     var parametros = {
// //         "num_columna" : columna,
// //         "estado" : estado
// //     };
// //     $.ajax({
// //         data:  parametros,
// //         dataType: "json",
// //         async: false,
// //         url:   "/actualizar_columnas_operacion",
// //         method:  'post',
// //         beforeSend: function () {
// //             $("#resultado").html("Procesando, espere por favor...");
// //         },
// //         success:  function (response) {
// //         }
// //     })
// // }

// //-------------------------------------------------------------------
// //-------------------------------------------------------------------

// function js_inicializa_operaciones(){

//     console.log("dentro de operaciones")
//     tabla = $("#tabla_operaciones").DataTable({
//         "buttons": ["colvis"],
//         "info":true,
//         "searching":true,
//         "lengthMenu": [ 10, 25, 50, 75, 100 ],
//         "lengthChange": true,
//         scrollY: 600,
//         scrollX: true,
//         destroy: true,
//         stateSave: true,
//         // "columnDefs": [{ "visible": false, "targets": columnas}],
//     }).buttons().container().appendTo('#tabla_operaciones_wrapper .col-md-6:eq(0)');

//     // $('#tabla_operaciones').on('column-visibility.dt', function ( e, settings, column, state ) {
//     //     // state ? columnas.pop(column) : columnas.push(column)
//     //     state ? js_actualizar_columnas_operacion(column, "visible") : js_actualizar_columnas_operacion(column, "oculta")
//     //     // console.log(columnas)
//     // });
// }



// //-------------------------------------------------------------------
// //-------------------------------------------------------------------

function js_llenar_tabla_usuarios(){
    var usuarios
    //-----------------------AJAX OPERACIONES---------------------------------
    $.ajax({
        dataType: "json",
        async: false,
        url:   "/api_traer_usuarios",
        type:  'get',
        beforeSend: function () {
            $("#resultado").html("Procesando, espere por favor...");
        },
        success:  function (response) {
            usuarios = response
        }
    });
    console.log(usuarios);
    //-----------------------AJAX OPERACIONES---------------------------------

    tabla = $("#tabla_operaciones").DataTable({
        "buttons": ["colvis"],
        "info":true,
        "searching":true,
        "lengthMenu": [ 10, 25, 50, 75, 100 ],
        "lengthChange": true,
        select: true,
        scrollY: 600,
        scrollX: true,
        destroy: true,
        stateSave: true,
        data: usuarios,
        columns: [
        { name: 'id_usuario', data: 'id_usuario',
        render: function (data, type, row) {
          return "<div class='btn-group'>"+
                    "<button type='button' class='btn btn-primary'>Accion</button>"+
                    "<button type='button' class='btn btn-primary dropdown-toggle dropdown-icon' data-toggle='dropdown'>"+
                      "<span class='sr-only'>Toggle Dropdown</span>"+
                    "</button>"+
                    "<div class='dropdown-menu' role='menu'>"+
                      "<a class='dropdown-item' data-toggle='modal' data-target='#modal_nueva_operacion' onclick='js_buscar_operacion("+data+")'>Editar</a>"+
                      "<a class='dropdown-item' data-toggle='modal' data-target='#modal_eliminar_operacion' onclick='js_eliminar_operacion("+data+")'>Eliminar</a>"+
                    "</div>"+
                  "</div>";
          }
        },
        { name: 'perfil_usuario', data: 'perfil_usuario' },
        { name: 'nombre_usuario', data: 'nombre_usuario' },
        { name: 'pass_usuario', data: 'pass_usuario' }
        ]
        // ,"columnDefs": [{ "visible": false, "targets": columnas}]
        }).buttons().container().appendTo('#tabla_operaciones_wrapper .col-md-6:eq(0)');

        $('#tabla_operaciones').DataTable().columns.adjust();

        // var names = $('#tabla_operaciones').DataTable().columns.names();
        // var names = $("#tabla_operaciones").DataTable().columns()
        // console.log(names);

        Swal.fire({
            icon: 'success',
            title:'Tabla Actualizada',
            html: 'Las Operaciones han sido desplegadas',
            timer: 4000
        })
}

// //-------------------------------------------------------------------

function js_validar_formulario_nuevo_usuario(){
    var perfil_usuario = $("#perfil_usuario").val()
    var nombre_usuario = $("#nombre_usuario").val()
    var contraseña_usuario = $("#contraseña_usuario").val()

    if(perfil_usuario == "" || nombre_usuario == "" || contraseña_usuario == ""){
        console.log("formulario incompleto");
        showAlert('error','Formulario Incompleto','Complete todos los campos',4000)
    }else{
        console.log("todo ok");
        js_envio_nuevo_usuario()
    }
}

// //-------------------------------------------------------------------

function js_envio_nuevo_usuario(){
    var perfil_usuario = $("#perfil_usuario").val()
    var nombre_usuario = $("#nombre_usuario").val()
    var contraseña_usuario = $("#contraseña_usuario").val()

    var parametros = {
        "perfil_usuario" : perfil_usuario,
        "nombre_usuario" : nombre_usuario,
        "contraseña_usuario" : contraseña_usuario
    };
    $.ajax({
        data:  parametros,
        dataType: "json",
        async: false,
        url:   "/api_nuevo_usuario",
        method:  'post',
        beforeSend: function () {
            $("#resultado").html("Procesando, espere por favor...");
        },
        success:  function (response) {
            if (response == "200") {
                showAlert('success','Operacion Exitosa','Usuario Ingresado',4000)
                $("#modal_nuevo_usuario").modal('hide')
            }else{
                return showAlert('error','Error Operacion','Fallo el Ingreso del Usuario',4000)
            }
        }
    })
    location.reload();
}

// //-------------------------------------------------------------------

function js_boton_editar_usuario(id_usuario){
    console.log("editar usuario");
    var parametros = {"id_usuario" : id_usuario};
    $.ajax({
        data:  parametros,
        dataType: "json",
        async: false,
        url:   "/api_buscar_usuario",
        method:  'post',
        beforeSend: function () {
            $("#resultado").html("Procesando, espere por favor...");
        },
        success:  function (response) {
            console.log(response);
            // ---- mostrar modal
            $("#modal_nuevo_usuario").modal('show')

            // ---- mostrar-ocultar botones
            $("#envio_actualizar_usuario").show()
            $("#envio_nuevo_usuario").hide();

            // ---- cambia el label de la contraseña
            $("#label_contraseña_usuario").html("Nueva Contraseña *");

            // ---- setear los valores del usuario
            $("#id_usuario").val(response[0].id_usuario);
            $('#perfil_usuario').val(response[0].perfil_usuario).trigger('change.select2');
            $("#nombre_usuario").val(response[0].nombre_usuario);
            $("#contraseña_usuario").val('');
        }
    })
}

// //-------------------------------------------------------------------

function js_validar_formulario_actualizar_usuario(){
    console.log("dentro de validar formulario");

    var perfil_usuario = $("#perfil_usuario").val()
    var nombre_usuario = $("#nombre_usuario").val()
    var contraseña_usuario = $("#contraseña_usuario").val()

    if(perfil_usuario == "" || nombre_usuario == "" || contraseña_usuario == ""){
        console.log("formulario incompleto actualizar");
        return showAlert('error','Formulario Incompleto','Complete todos los campos',4000)
    }else{
        console.log("todo ok");
        js_envio_actualizar_usuario()
    }
}
// //-------------------------------------------------------------------

function js_envio_actualizar_usuario(){
    var id_usuario = $("#id_usuario").val()
    var perfil_usuario = $("#perfil_usuario").val()
    var nombre_usuario = $("#nombre_usuario").val()
    var contraseña_usuario = $("#contraseña_usuario").val()

    var parametros = {
        "id_usuario" : id_usuario,
        "perfil_usuario" : perfil_usuario,
        "nombre_usuario" : nombre_usuario,
        "contraseña_usuario" : contraseña_usuario
    };
    $.ajax({
        data:  parametros,
        dataType: "json",
        async: false,
        url:   "/api_actualizar_usuario",
        method:  'post',
        beforeSend: function () {
            $("#resultado").html("Procesando, espere por favor...");
        },
        success:  function (response) {
            if (response == "200") {
                showAlert('success','Operacion Exitosa','Usuario Actualizado',4000)
                $("#modal_nuevo_usuario").modal('hide')
            }else{
                return showAlert('error','Error Operacion','Fallo la Actualizacion del Usuario',4000)
            }
        }
    })
    location.reload();
}

// //-------------------------------------------------------------------

function js_mostrar_modal_nuevo_usuario(){
    // ---- mostrar-ocultar botones
    $("#envio_nuevo_usuario").show()
    $("#envio_actualizar_usuario").hide();
    // ---- cambia el label de la contraseña
    $("#label_contraseña_usuario").html("Contraseña Usuario");
}

// //-------------------------------------------------------------------

function js_boton_eliminar_usuario(id_usuario){
    var parametros = {
        "id_usuario" : id_usuario
    };

    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
        confirmButton: 'btn btn-success',
        cancelButton: 'btn btn-danger'
        },
        buttonsStyling: false
        })

    swalWithBootstrapButtons.fire({
        title: 'Estas Seguro?',
        text: "El Usuario sera borrado definitivamente",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Si, Borralo!',
        cancelButtonText: 'No, Cancelar!',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed){
            $.ajax({
                data:  parametros,
                dataType: "json",
                async: false,
                url:   "/api_eliminar_usuario",
                type:  'post',
                beforeSend: function () {
                    $("#resultado").html("Procesando, espere por favor...");
                },
                success:  function (response) {
                    console.log(response)
                    if (response == "200") {
                        return showAlert('success','Operacion Exitosa','Usuario Borrado',4000)
                    }else{
                        return showAlert('error','Error Operacion','Fallo la Eliminacion del Usuario',4000)
                    }
                }
            });
            location.reload();
        }
    })
}

// //-------------------------------------------------------------------

// //-------------------------------------------------------------------