//$(document).ready(function() {
//    var URLactual = location.pathname;
//    js_traer_operaciones()
    //alert(URLactual);
    //if (URLactual == ('/tabla_documentos') || ('/tabla_documentos/')) {
    //  alert("dentro de documentos");
    //  console.log("estas en documentos")
    //}
    //if (URLactual == '/tabla_operaciones') {
    //  alert("dentro de operaciones");
    //  console.log("estas en operaciones")
    //  js_traer_operaciones()
    //}
//  });

//window.onload = function() {
//    var URLactual = location.pathname;
//    console.log(URLactual)
//
//    if (URLactual == ('/tabla_documentos')){
//        console.log("dentro de documentos")
//        js_traer_operaciones()
//    }
//};


function js_eliminar_documento(id_documento){
    var parametros = {
        "id_documento" : id_documento
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
        text: "El documento sera borrado definitivamente",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Si, Borralo!',
        cancelButtonText: 'No, Cancelar!',
        reverseButtons: true
    }).then((result) => {

      if (result.isConfirmed) {

        $.ajax({
            data:  parametros,
            dataType: "json",
            async: false,
            url:   "/api_eliminar_documento",
            method:  'post',
            beforeSend: function () {
                $("#resultado").html("Procesando, espere por favor...");
            },
            success:  function (response) {
                console.log(response)
            }
        });

        swalWithBootstrapButtons.fire(
            'Borrado',
            'El documento fue borrado',
            'success'
        )
        location.reload();
        }
    })
}






function js_validar_formulario_documento(){
    const valido = $("#nuevo_documento").valid()

    // const fecha_inicio      = $("#fecha_inicio").val().split("/").reverse().join("-")
    // const fecha_termino     = $("#fecha_termino").val().split("/").reverse().join("-")
    // const fecha_envio       = $("#fecha_envio").val().split('/').reverse().join('-')
    // const fecha_recepcion   = $("#fecha_recepcion").val().split('/').reverse().join('-')

    // const fecha_ini = Date.parse(fecha_inicio)
    // const fecha_ter = Date.parse(fecha_termino)
    // const fecha_env = Date.parse(fecha_envio)
    // const fecha_rec = Date.parse(fecha_recepcion)

    // if(fecha_ini>fecha_ter) return showAlert('error','Fecha rechazada','La fecha de vencimiento debe ser mayor a la de operación.',5000)

    if(valido){

        $("#modal_nuevo_documento").modal('hide')

        const id_custodio       = $("#id_custodio").val(),
              id_tipo_documento = $("#id_tipo_documento").val(),
              fecha_inicio      = $("#fecha_inicio").val(),
              fecha_termino     = $("#fecha_termino").val(),
              fecha_envio       = $("#fecha_envio").val(),
              fecha_recepcion   = $("#fecha_recepcion").val()

        const parametros = {
            "id_custodio":id_custodio,
            "id_tipo_documento":id_tipo_documento,
            "fecha_inicio" :fecha_inicio,
            "fecha_termino":fecha_termino,
            "fecha_envio":fecha_envio,
            "fecha_recepcion":fecha_recepcion
        }

        $.ajax({
            data:  parametros,
            dataType: "json",
            async: false,
            url:   "/api_nuevo_documento",
            method:  'post',
            beforeSend: function () {
              $("#resultado").html("Procesando, espere por favor...");
            },
            success:  function (response) {
              //$("#resultado").html(response);
              console.log(response)
            }
        });

        document.getElementById("nuevo_documento").reset();

        showAlert('success','Cambios Realizados','mensaje',2000)

    function showAlert(icon,title,html,timer){
        Swal.fire({
            icon: icon,
            title:title,
            html: html,
            timer: timer
        })
    }
    location.reload();
    }
}