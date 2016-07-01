OpenSmartCountryWebServicevar username = "mariamunoz";
var password = "39y67h";

function doGet(parametros) {
  
  //para depuración
  if(parametros == null){
    parametros={};
    parametros.parameter = {};
    parametros.parameter.accion = "actualiza";
    parametros.parameter.anio = "2016";
    parametros.parameter.latitud = 40.996163;
    parametros.parameter.longitud =  -4.764504;
  }
  var resultado = {};
  
  var accion = parametros.parameter["accion"];
  var latitud = parametros.parameter["latitud"];
  var longitud = parametros.parameter["longitud"];
  
  var estacion = obtenEstacion(latitud, longitud);
  
  var libro = obtenPrimerLibro(estacion);
  
  var fecha_ini = parametros.parameter["fecha_ini"];
  var fecha_fin = parametros.parameter["fecha_fin"];
  
  var anio = parametros.parameter["anio"];
  
  switch(accion) {
    case "actualiza":
      resultado = actualizaDatosClima(libro, estacion, fecha_ini, fecha_fin);
      break;
    case "obtenEstacion":
      resultado = obtenEstacion(latitud, longitud);
      break;
    default:
      throw "Accion no implementada";
  }
  
  //  var anio = Number(parametros.parameter["anio"]);
  //  var tiposMedida = parametros.parameter["tipomedida"];
  //  if(tiposMedida != null){
  //    tiposMedida=tiposMedida.split(",");
  //  }
  //  var variable = parametros.parameter["variable"];
  //  
  //
  //  
  //  var latitud = parametros.parameter["latitud"];
  //  var longitud = parametros.parameter["longitud"];
  
  Logger.log(JSON.stringify(resultado));
  
  return ContentService
  .createTextOutput(JSON.stringify(resultado))
  .setMimeType(ContentService.MimeType.JSON);
}


