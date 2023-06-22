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


//funcionalidad sin utilizar por el momento - para validar la eliminacion de un documento que contiene una firma asociada
function js_existe_firma(id_documento){
    var parametros = {
        "id_documento" : id_documento
    };
    $.ajax({
        data:  parametros,
        dataType: "json",
        async: false,
        url:   "/api_existe_firma",
        type:  'post',
        beforeSend: function () {
            $("#resultado").html("Procesando, espere por favor...");
        },
        success:  function (response) {
            console.log(response)
        }
    });
}