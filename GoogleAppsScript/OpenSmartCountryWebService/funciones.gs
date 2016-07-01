function obtenPrimerLibro(estacion){
  var nombreLibro;
  
  if(estacion.length > 1){
    nombreLibro = "Estaciones_InfoRiego";
  }else{
    nombreLibro = "InfoRiego_" + estacion.IDPROVINCIA + "_" + estacion.IDESTACION;
  }
  var libro;
  
  var librosConEseNombre = DriveApp.getFilesByName(nombreLibro);    
  if (librosConEseNombre.hasNext()) {
    libro = SpreadsheetApp.open(librosConEseNombre.next());
  }else{
    libro = creaLibro(nombreLibro);
  }
  
  if(libro==null){throw "Libro no encontrado"};
  
  return libro;
}

function obtenEstacion(latitud, longitud) {
  
  var resultado = {};
  
  var url = 'http://www.inforiego.org/opencms/rest/estacion?username='+username
  +'&password='+password;
  if(latitud != null){
    url = url +'&latitud='+latitud +'&longitud='+longitud;
  }
  
  var data = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  
  if(data.length > 1){
    resultado = data;
  }else{
    
    for(var i=0; i<data.length; i++)
    {
      var obj = data[i];
      
      resultado["IDPROVINCIA"] = obj["IDPROVINCIA"];
      resultado["IDESTACION"] = obj["IDESTACION"];
      resultado["ALTITUD"] = obj["ALTITUD"];
      resultado["ESTACION"] = obj["ESTACION"];
      resultado["ESTACIONCORTO"] = obj["ESTACIONCORTO"];
      resultado["FECHAFINDATOS"] = obj["FECHAFINDATOS"];
      resultado["FECHAINSTAL"] = obj["FECHAINSTAL"];
      resultado["IDPROVINCIA"] = obj["IDPROVINCIA"];
      resultado["LATITUD"] = obj["LATITUD"];
      resultado["LONGITUD"] = obj["LONGITUD"];
      resultado["X_UTM"] = obj["X_UTM"];
      resultado["Y_UTM"] = obj["Y_UTM"];
    }
    
    if(resultado["IDESTACION"] == null){
      throw "no se encuentran datos de estaciones para las coordenadas proporcionadas"
    }  else{
      resultado.result = "success";
    }
    
  }
  
  return resultado;
}


function actualizaDatosClima(libro, estacion, fecha_ini, fecha_fin) {
  
  var resultado = {};
  
  var hoja = libro.getSheetByName("diario");
  if(hoja == null)
  {
    throw "Hoja no encontrada";
  }
  
  var ahora = new Date();
  
  var fecha_ult_modif;
  
  
  var numeroFilas = hoja.getLastRow();
  
  if(numeroFilas>1){
    //actualizo los valores de la última fecha de actualización y de la última fecha para la que tengo datos
    var fecha = hoja.getRange(numeroFilas,1).getValue();
    fecha_ult_modif = ("0" + fecha.getDate()).slice(-2) + '/' + ("0"+(fecha.getMonth()+1)).slice(-2) + '/' + fecha.getFullYear();
    
    fecha = hoja.getRange(numeroFilas,10).getValue();
    fecha.setDate(fecha.getDate() + 1);
    fecha_ini = ("0" + fecha.getDate()).slice(-2) + '/' + ("0"+(fecha.getMonth()+1)).slice(-2) + '/' + fecha.getFullYear();
  }
  
  if(fecha_ini == null){
    fecha_ini = estacion.FECHAINSTAL;
  }
  
  if(fecha_ult_modif == null){
    fecha_ult_modif = "01/01/2010";
  }
  
  if (fecha_fin == null){
    fecha_fin = ("0" + ahora.getDate()).slice(-2) + '/' + ("0"+(ahora.getMonth()+1)).slice(-2) + '/' + ahora.getFullYear();
  }
  
  if(numeroFilas <= 1)
  {
    actualizaCabecera(hoja, estacion);
  }
  var matrizDatosAInsertar = [];
  
  for(var anio = fecha_ini.split("/")[2]; anio<= fecha_fin.split("/")[2]; anio++){
    
    var ini = "01/01/" + anio;
    var fin = "31/12/" + anio;
    
    if(anio == fecha_ini.split("/")[2]){
      ini = fecha_ini.split("/")[0] + "/" + fecha_ini.split("/")[1] + "/" + fecha_ini.split("/")[2];
    }
    if(anio == fecha_fin.split("/")[2]){
      fin = fecha_fin.split("/")[0] + "/" + fecha_fin.split("/")[1] + "/" + fecha_fin.split("/")[2];
    }
    
    
    
    var url = 'http://www.inforiego.org/opencms/rest/diario?username='+username
    +'&password='+password
    +'&provincia='+estacion.IDPROVINCIA
    +'&estacion='+estacion.IDESTACION
    +'&fecha_ini='+ini
    +'&fecha_fin='+fin
    +'&fecha_ult_modif='+fecha_ult_modif;
    
    var data = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    
    
    var headRow = 1;
    var headers = hoja.getRange(1, 1, 1, hoja.getLastColumn()).getValues()[0];
    
    
    for(var i=0; i<data.length; i++)
    {
      var obj = data[i];
      
      var row = [];
      var nextRow = hoja.getLastRow()+1;
      
      for (var j in headers){
        if(headers[j] == 'Timestamp'){
          row.push(ahora);
        }else{
          if(obj[headers[j]]!=null){
            row.push(obj[headers[j]].replace(".",","));
          }else{
            row.push("");
          }
        }
      }
      matrizDatosAInsertar.push(row);
      
      
      
    }    
  }
  if(matrizDatosAInsertar.length > 0){
    hoja.getRange(nextRow, 1, matrizDatosAInsertar.length, matrizDatosAInsertar[0].length).setValues(matrizDatosAInsertar);
  }
  
  if(resultado.error == null){
    resultado.result = "success";
    resultado.value  = "Insertados " + matrizDatosAInsertar.length + " nuevos registros";
  }
  
  return resultado;
}

function actualizaCabecera(hoja, estacion){
  var url = 'http://www.inforiego.org/opencms/rest/diario?username='+username
  +'&password='+password
  +'&provincia='+estacion.IDPROVINCIA
  +'&estacion='+estacion.IDESTACION
  +'&fecha_ini=01/01/2016'
  +'&fecha_fin=01/01/2016'
  +'&fecha_ult_modif=01/01/2016';
  
  var data = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  
  var row = [];
  row.push("Timestamp");
  for(var i=0; i<data.length;i++)
  {
    var obj = data[i];
    for(var propiedad in obj)
    {
      row.push(propiedad);
    }
  }
  hoja.getRange(1, 1, 1, row.length).setValues([row]);
  
}

function creaLibro(nombreLibro){
  var libro = SpreadsheetApp.create(nombreLibro);
  var primeraHoja = libro.getSheets()[0];
  primeraHoja.setName("diario");
  return libro;
}

function actualizaTodasEstaciones(){
  var resultado = {};
  
  var url = 'http://www.inforiego.org/opencms/rest/estacion?username='+username
  +'&password='+password;
    
  var data = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  
    for(var i=0; i<data.length; i++)
    {
      var estacion = data[i];
      
      var libro = obtenPrimerLibro(estacion);
      
      resultado = actualizaDatosClima(libro, estacion);
    }
    
    if(data.length = 0){
      throw "no se encuentran datos de estaciones"
    } 
    
  
  
  return resultado;
  
  
  
}

