function actualiza(){
  obtenYEscribeDatosIdealista('venta');
  obtenYEscribeDatosIdealista('alquiler');
  obtenYEscribeDatosFotocasa('venta');
}

function obtenYEscribeDatosIdealista(tipo) {
 
  var portal = 'idealista';
  var html = UrlFetchApp.fetch('https://www.idealista.com/'+ tipo  +'-terrenos/#municipality-search').getContentText();
  var locations_list = '';
  var fromText = '<div class="locations-list clearfix">';
  var toText = '</div>';
   
  var index_OfFromText = html.indexOf(fromText);
  locations_list = html.slice(index_OfFromText, html.length);
  var index_OfToText = locations_list.indexOf(toText);
  locations_list = locations_list.slice(0, index_OfToText + toText.length);

  Logger.log('locations_list length: ' + locations_list.length);
   
  var document = XmlService.parse(locations_list);
  var root = document.getRootElement();
  
  var numeroDeAnuncios = 0;
  var uls = root.getChildren();
  for (var i = 0; i < uls.length; i++) {
    var ul = uls[i];
    var lis = ul.getChildren();
    for (var j = 0; j< lis.length; j++) {
      var li = lis[j];
      var p = li.getChildText('p');
      var a = li.getChildText('a');
      if(a == null){
        a = li.getText();
      }
      addNumeroDeAnuncios(a,p, tipo, portal);
      Logger.log('Hay ' + p + ' anuncios en ' + a);
      numeroDeAnuncios += parseInt(p.replace('.', ''));
    }
  }
  Logger.log('--- TOTAL: ' + numeroDeAnuncios + ' anuncios');
}

function addNumeroDeAnuncios(a, p, tipo, portal) {
  
  var sheet = SpreadsheetApp.getActiveSheet();
  var columna = obtenColumna(portal, tipo);
  var lastRow = sheet.getLastRow();
    
  var primeraColumna = sheet.getRange(1, 1, lastRow, 1).getValues();
  var filaEncontrada = false;
  for (var i= 0; i< primeraColumna.length && !filaEncontrada; i++){
    var valor = primeraColumna[i][0];
    if (valor.trim() == a.trim()){
      sheet.getRange(i +1, columna).setValue(p);
      filaEncontrada = true;
    }
  }
  if(!filaEncontrada){
    sheet.getRange(lastRow + 1, 1).setValue(a.trim());
    sheet.getRange(lastRow + 1, columna).setValue(p);
  }
}

function obtenColumna(portal, tipo){

  var sheet = SpreadsheetApp.getActiveSheet();
  var columna = sheet.getLastColumn() + 1;
  if(tipo == 'venta' && portal == 'idealista'){
    columna = 2;
  }else if (tipo == 'alquiler' && portal == 'idealista'){
    columna = 3;
  }else if (portal == 'fotocasa'){
    columna = 4;
  }
  
  return columna;
}

function obtenYEscribeDatosFotocasa(tipo) {
 
  var portal = 'fotocasa';
  
  var html = UrlFetchApp.fetch('http://www.fotocasa.es/comprar/terrenos/espana/listado').getContentText();
  var locations_list = '';
  var fromText = '<div data-item="rptLoc"';
  var second_fromText = '<div class="scrollable">';
  var toText = '</div>';
   
  var index_OfFromText = html.indexOf(fromText);
  locations_list = html.slice(index_OfFromText, html.length);
  locations_list = html.slice(html.indexOf(second_fromText), locations_list.length);
  
  var index_OfToText = locations_list.indexOf(toText);
  locations_list = locations_list.slice(0, index_OfToText + toText.length);

  Logger.log('locations_list length: ' + locations_list.length);
   
  var document = XmlService.parse(locations_list);
  var root = document.getRootElement();
  
  var numeroDeAnuncios = 0;
  var uls = root.getChildren();
  for (var i = 0; i < uls.length; i++) {
    var ul = uls[i];
    var lis = ul.getChildren();
    for (var j = 0; j< lis.length; j++) {
      var li = lis[j];
      var p = li.getChildText('span');
      var a = li.getChildText('a');
      if(a == null){
        a = li.getText();
      }
      
      Logger.log('Hay ' + p + ' anuncios en ' + a);
      p = p.replace('(','');
      p = p.replace(')','');
      addNumeroDeAnuncios(a,p, tipo, portal);
      numeroDeAnuncios += parseInt(p.replace('.', ''));
    }
  }
  Logger.log('--- TOTAL: ' + numeroDeAnuncios + ' anuncios');
}

function addNumeroDeAnuncios(a, p, tipo, portal) {
  
  var sheet = SpreadsheetApp.getActiveSheet();
  var columna = obtenColumna(portal, tipo);
  var lastRow = sheet.getLastRow();
    
  var primeraColumna = sheet.getRange(1, 1, lastRow, 1).getValues();
  var filaEncontrada = false;
  for (var i= 0; i< primeraColumna.length && !filaEncontrada; i++){
    var valor = primeraColumna[i][0];
    if (valor.trim() == a.trim()){
      sheet.getRange(i +1, columna).setValue(p);
      filaEncontrada = true;
    }
  }
  if(!filaEncontrada){
    sheet.getRange(lastRow + 1, 1).setValue(a.trim());
    sheet.getRange(lastRow + 1, columna).setValue(p);
  }
}
