var query;

var mapa;
var parcela = {lat: 40.439983, lng: 	-5.737026};
var informacionPoligono;

function initMap() {
	var mapOptions = {
		center: parcela,
		zoom: 16,
		mapTypeId: google.maps.MapTypeId.SATELLITE
	}
	
	mapa = new google.maps.Map(document.getElementById('mapa'), mapOptions);
	
	//TODO: con el mapa pequeño este botón queda demasiado grande
	//Create the DIV to hold the control and call the CenterControl() constructor
  //passing in this DIV.
   var centerControlDiv = document.createElement('div');
  var centerControl = new CenterControl(centerControlDiv, mapa);

   centerControlDiv.index = 1;
     mapa.controls[google.maps.ControlPosition.LEFT_CENTER].push(centerControlDiv);
	
	 var marker = new google.maps.Marker({
    position: parcela,
     map: mapa,
	 animation: google.maps.Animation.DROP,
     title: 'Parcela'
   });
  
	 var contenidoVentanaInformacion = '<h1>Viña de la Estación</h1>' +
	 '<p>Se trata de un bien inmueble de tipo <strong><span id="cn"></span></strong> con <span id = "cucons"></span> unidades constructivas y <span id="cucul"></span> subparcelas o cultivos.</p>'+
		'<p>El paraje en el que se encuentra se llama <em><span id="npa"></span></em> en <em><span id="nm"></span> ( <span id="np"></span>).</em></p>' +
		'<p>La calificación catastral  según la clase de cultivo es <strong><span id="ccc"></span></strong> y una intensidad productiva de <span id="ip"></span>.</p>' +
		'<p>La superficie de la parcela son <strong><span id="ssp"> </span> metros cuadrados</strong>.</p>'+
		'<p>Más información disponible en la <a href="http://www.sedecatastro.gob.es/">Sede Electrónica del Catastro</a></p>';

  var informacionMarcador = new google.maps.InfoWindow({
    content: contenidoVentanaInformacion
  });
  
  marker.addListener('click', function() {
    //TODO: hacer que esta información se muestre en otra parte
	informacionMarcador.open(mapa, marker);
  });
  
  var triangleCoords = [
    
{lng: -5.73743277138396, lat: 40.4390893833596},
{lng: -5.7374292381294,   lat: 40.4390894670862},
{lng: -5.73739180024054, lat: 40.4390907145335},
{lng: -5.73725167450709, lat: 40.4391382615966},
{lng: -5.73724113701022, lat: 40.4391749014607},
{lng: -5.73721803154044, lat: 40.4392562459453},
{lng: -5.73718072633477, lat: 40.4393856619662},
{lng: -5.73714289614587, lat: 40.4394992417711},
{lng: -5.73709900898761, lat: 40.4395972020055},
{lng: -5.73705224582516, lat: 40.4397114438101},
{lng: -5.73699952384232, lat: 40.4398442920897},
{lng: -5.73695236415262, lat: 40.4399778192313},
{lng: -5.7370488836958,   lat: 40.440017687337  },
{lng: -5.73708040409467, lat: 40.4400274792416},
{lng: -5.73710763776926, lat: 40.4399868408083},
{lng: -5.73712811791558, lat: 40.4399337519324},
{lng: -5.73714969089239, lat: 40.4398814478309},
{lng: -5.7371687868795,   lat: 40.4398291123418},
{lng: -5.73717846353938, lat: 40.4397915921367},
{lng: -5.73719421568004, lat: 40.4397383450527},
{lng: -5.73721632635996, lat: 40.4396963867868},
{lng: -5.73724294352035, lat: 40.4396492775525},
{lng: -5.73727487779192, lat: 40.4395821358146},
{lng: -5.73732973018171, lat: 40.4394203229537},
{lng: -5.73739206998265, lat: 40.4392658133442},
{lng: -5.73743630057109, lat: 40.4391501902217},
{lng: -5.73745579242689, lat: 40.4391018085895},
{lng: -5.73743277138396, lat: 40.4390893833596},
{lng: -5.73743277138396, lat: 40.4390893833596}
];

  
  var bermudaTriangle = new google.maps.Polygon({
    paths: triangleCoords,
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#FF0000',
    fillOpacity: 0.35
  });
  bermudaTriangle.setMap(mapa);
	
	// Add a listener for the click event.
  bermudaTriangle.addListener('click', showArrays);

  informacionPoligono = new google.maps.InfoWindow;
}

/** @this {google.maps.Polygon} */
function showArrays(event) {
  // Since this polygon has only one path, we can call getPath() to return the
  // MVCArray of LatLngs.
  var vertices = this.getPath();

  var contentString = '<h3>Viña de la estación</h3>' +
      '<h4>Localización marcada: </h4>' + event.latLng.lat() + ',' + event.latLng.lng() +
      '<h6>Conjunto de coordenadas fijadas por el catastro:</h6><ul>';

  // Iterate over the vertices.
  for (var i =0; i < vertices.getLength(); i++) {
    var xy = vertices.getAt(i);
    contentString += '<li>' + xy.lat() + ',' + xy.lng() + '</li>';
  }
  
  contentString += '</ul>';

  // Replace the info window's content and position.
  informacionPoligono.setContent(contentString);
  informacionPoligono.setPosition(event.latLng);

  //TODO: hacer que esta información se muestre en otra parte
  informacionPoligono.open(mapa);
  
}

/**
 * The CenterControl adds a control to the map that recenters the map on Chicago.
 * This constructor takes the control DIV as an argument.
 * @constructor
 */
function CenterControl(controlDiv, map) {

  // Set CSS for the control border.
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = '#fff';
  controlUI.style.border = '2px solid #fff';
  controlUI.style.borderRadius = '3px';
  controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
  controlUI.style.cursor = 'pointer';
  controlUI.style.marginBottom = '22px';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click para centrar el mapa en la parcela';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  var controlText = document.createElement('div');
  controlText.style.color = 'rgb(25,25,25)';
  controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
  controlText.style.fontSize = '8px';
  controlText.style.lineHeight = '12px';
  controlText.style.paddingLeft = '3px';
  controlText.style.paddingRight = '3px';
  controlText.innerHTML = 'Centrar';
  controlUI.appendChild(controlText);

  // Setup the click event listeners: simply set the map to Chicago.
  controlUI.addEventListener('click', function() {
    map.setCenter(parcela);
	map.setZoom(20);
  });

}

function obten(campo,anio, tipomedida,variable) {
	
	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?anio=" + anio + "&variable=" + variable +"&tipomedida=" +tipoMedida;
	
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		document.getElementById(campo).innerHTML = response[variable][tipomedida].value.toFixed(2);
	});
}


function actualiza() {
	var url = "https://script.google.com/macros/s/AKfycbyJ1Qb6CIlZYvW6poU-qAl2MPoEVD-kws2frLnsmOScu-ezbwA/exec?accion=actualiza&latitud="+document.getElementById("latitud").innerHTML+"&longitud="+document.getElementById("longitud").innerHTML;
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});
}
	

function cargaDatos(){

		obtenDatosCatastro();
		obtenEstacion();
		actualiza();
		//obten(2016);
		google.charts.load('current', {'packages': ['table', 'bar', 'corechart', 'geochart']});
		google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
		google.charts.setOnLoadCallback(graficoTemperaturasMediasDiurnas);
		google.charts.setOnLoadCallback(graficoHorasDeSolDiarias);
		google.charts.setOnLoadCallback(graficoRadiacionNetaDiaria);

		google.charts.setOnLoadCallback(cargaMedidaDiasDeLluvia);
		google.charts.setOnLoadCallback(cargaMedidaPrecipitacionAcumulada);
		google.charts.setOnLoadCallback(cargaMedidaMaximaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMinimaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMediaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMediaHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaMaximoHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaAcumuladoHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaMaximoRadiacionDiaria);
		google.charts.setOnLoadCallback(cargaMedidaMediaRadiacionDiaria);
		google.charts.setOnLoadCallback(cargaMedidaAcumuladoRadiacionDiaria);
		
		google.charts.setOnLoadCallback(drawRegionsMap); 

}

function drawRegionsMap() {

	var data = google.visualization.arrayToDataTable([
	  ['latitude', 'longitude', 'temperatura'],
	  [40.440005, -5.737003, 25]
	]);

	var options = {
		region: 'ES',
		displayMode: 'markers',
		colorAxis: {colors: ['blue']},
		resolution: 'provinces'
	};

	var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

	chart.draw(data, options);
 }

function obtenEstacion(){
	
	var url = "https://script.google.com/macros/s/AKfycbyJ1Qb6CIlZYvW6poU-qAl2MPoEVD-kws2frLnsmOScu-ezbwA/exec?accion=obtenEstacion&latitud="+document.getElementById("latitud").innerHTML+"&longitud="+document.getElementById("longitud").innerHTML;
	
	
 	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		document.getElementById("estacion").innerHTML = response["ESTACION"];

	}); 
}

//Code Starts


//Code Ends


function obtenDatosCatastro(){
	
	//devuelve un xml y no se puede obtener por cross domain, aquí para resolverlo se utiliza un proxy de yahoo que en realidad da más posibilidades para cruzar datos pero está limitado en número de peticiones diarias
	
	var url = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4326&Coordenada_X="+document.getElementById("longitud").innerHTML+ "&Coordenada_Y="+document.getElementById("latitud").innerHTML;
	
	var yql = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from xml where url="' + url + '"') + '&format=xml&callback=?';
	
	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$.getJSON(yql, function(data){
		xml = data.results[0];
		console.log(xml);

		var xmlDoc = jQuery.parseXML(xml);
		var coordenadas = xmlDoc.getElementsByTagName("coordenadas");
		var coord = coordenadas[0].getElementsByTagName("coord");
		
		var rc = coord[0].getElementsByTagName("pc")[0].getElementsByTagName("pc1") [0].childNodes[0].nodeValue+coord[0].getElementsByTagName("pc")[0].getElementsByTagName("pc2")[0].childNodes[0].nodeValue;
		document.getElementById("rc").innerHTML = rc;
		document.getElementById("direccion").innerHTML = coord[0].getElementsByTagName("ldt")[0].childNodes[0].nodeValue;
		var provincia = "";
		var municipio = "";
		//Curiosamente me obliga a pasar provincia y municipio pero se lo puedo pasar en blanco y funciona igual XD
		obtenDatosPorReferenciaCatastral(rc, provincia, municipio);
	});
	
	
	
}

function obtenProvincia(rc){
	
	var codigoProvincia = rc.substr(0,2);
	
	var url = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia";
	
	var yql = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from xml where url="' + url + '"') + '&format=xml&callback=?';
	
	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$.getJSON(yql, function(data){
		xml = data.results[0];
		console.log(xml);

		var xmlDoc = jQuery.parseXML(xml);
		var provs = xmlDoc.getElementsByTagName("provinciero")[0].getElementsByTagName["prov"];
		
		for(var i=0; i< provs.length; i++){
			var prov = provs[i].getElementsByTagName("cpine")[0].childNodes[0].nodeValue;
			if (prov == codigoProvincia){
				return  provs[i].getElementsByTagName("np")[0].childNodes[0].nodeValue;
			}
		}
		
		
	});
	
	return "";
	
}

function obtenMunicipio(rc){
	
	var codigoMunicipio = rc.substr(2,3);
	
	var url = "http://ovc.catastro.meh.es//ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?Provincia=" + obtenProvincia(rc);
	
	var yql = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from xml where url="' + url + '"') + '&format=xml&callback=?';
	
	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$.getJSON(yql, function(data){
		xml = data.results[0];
		console.log(xml);

		var xmlDoc = jQuery.parseXML(xml);
		var munis = xmlDoc.getElementsByTagName("municipiero")[0].getElementsByTagName["muni"];
		
		for(var i=0; i< munis.length; i++){
			var muni = munis[i].getElementsByTagName("locat")[0].getElementsByTagName("cmc")[0].childNodes[0].nodeValue;
			if (muni == codigoMunicipio){
				return  munis[i].getElementsByTagName("nm")[0].nodeValue;
			}
		}
		
		
	});
	
	return "";
	
}

function obtenDatosPorReferenciaCatastral(rc, provincia, municipio){
	
	//devuelve un xml y no se puede obtener por cross domain, aquí para resolverlo se utiliza un proxy de yahoo que en realidad da más posibilidades para cruzar datos pero está limitado en número de peticiones diarias
	
	var url = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?RC="+rc + "&Provincia=" + provincia + "&Municipio=" + municipio;
	
	var yql = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from xml where url="' + url + '"') + '&format=xml&callback=?';
	
	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$.getJSON(yql, function(data){
		xml = data.results[0];
		console.log(xml);

		var xmlDoc = jQuery.parseXML(xml);
		
		var xmlDoc = jQuery.parseXML(xml);
		var bi = xmlDoc.getElementsByTagName("bico")[0].getElementsByTagName("bi");
		var cn = bi[0].getElementsByTagName("idbi")[0].getElementsByTagName("cn")[0].childNodes[0].nodeValue;
		
		switch (cn){
			case "RU":
				document.getElementById("cn").innerHTML = "rústico";
				break;
			default:
				
		}
		
		var control = xmlDoc.getElementsByTagName("control");
		var cucons = control[0].getElementsByTagName("cucons");
		if(cucons.length > 0){
			document.getElementById("cucons").innerHTML = cucons[0].childNodes[0].nodeValue;
		}else{
			document.getElementById("cucons").innerHTML = 0;
		}
		
		var cucul = control[0].getElementsByTagName("cucul");
		if(cucul.length > 0){
			document.getElementById("cucul").innerHTML = cucul[0].childNodes[0].nodeValue;
		}else{
			document.getElementById("cucul").innerHTML = 0;
		}
		
		npa = bi[0].getElementsByTagName("dt")[0].getElementsByTagName("locs")[0].getElementsByTagName("lors")[0].getElementsByTagName("lorus")[0].getElementsByTagName("npa")[0].childNodes[0].nodeValue;
		
		//document.getElementById("npa").innerHTML = npa;
		//document.getElementById("nm").innerHTML = bi[0].getElementsByTagName("dt")[0].getElementsByTagName("nm")[0].childNodes[0].nodeValue;
		//document.getElementById("np").innerHTML = bi[0].getElementsByTagName("dt")[0].getElementsByTagName("np")[0].childNodes[0].nodeValue;
		var dspr = xmlDoc.getElementsByTagName("bico")[0].getElementsByTagName("lspr")[0].getElementsByTagName("spr")[0].getElementsByTagName("dspr");
		document.getElementById("ccc").innerHTML = dspr[0].getElementsByTagName("ccc")[0].childNodes[0].nodeValue + dspr[0].getElementsByTagName("dcc")[0].childNodes[0].nodeValue ;
		document.getElementById("ip").innerHTML = dspr[0].getElementsByTagName("ip")[0].childNodes[0].nodeValue;
		document.getElementById("ssp").innerHTML = dspr[0].getElementsByTagName("ssp")[0].childNodes[0].nodeValue;
		
	});
	
	
	
}




    function graficoPrecipitacionPorMesYAnio() {
		
		
      var queryPrecipitacionPorMesYAnio = encodeURIComponent('select month(J) + 1, sum(AA) group by month(J) pivot B');

      var queryCompletaPrecipitacionPorMesYAnio = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryPrecipitacionPorMesYAnio);
      queryCompletaPrecipitacionPorMesYAnio.send(trataRespuestaPrecipitacionPorMesYAnio);
    }

    function trataRespuestaPrecipitacionPorMesYAnio(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Precipitaciones mensuales en mm',
            subtitle: 'Comparativa acumulado mensual últimos años',
          },
          bars: 'vertical',
          colors: [ '#94E8B4' ,'#72BDA3', '#5E8C61',  '#426A4D', '#4E6151', '#3B322C','#7246F2' ],
		  hAxis: { ticks: [1,2,3,4,5,6,7,8,9,10,11,12] , title: 'Mes'},
		  vAxis: { title: 'Precipitación en mm'}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.ColumnChart(document.getElementById('graficoPrecipitacionPorMesYAnio'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	 function graficoTemperaturasMediasDiurnas() {
		
		
      var queryTemperaturasMediasDiurnas = encodeURIComponent('select C, sum(AH) where B >= 2014 group by C pivot B');

      var queryCompletaTemperaturasMediasDiurnas = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryTemperaturasMediasDiurnas);
      queryCompletaTemperaturasMediasDiurnas.send(trataRespuestaTemperaturasMediasDiurnas);
    }

    function trataRespuestaTemperaturasMediasDiurnas(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Temperaturas medias diurnas',
            subtitle: 'Comparativa temperatura media diurna últimos años',
          },
		  explorer: {},
          colors: ['#7F0D0B', '#BF1411','#400706' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  vAxis: { title: 'Temperatura en ºC'},
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoTemperaturaMediaDiurna'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }

	
	function graficoHorasDeSolDiarias() {
		
		
      var queryHorasDeSolDiarias = encodeURIComponent('select C, sum(V) where B >= 2014 group by C pivot B');

      var queryCompletaHorasDeSolDiarias = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryHorasDeSolDiarias);
      queryCompletaHorasDeSolDiarias.send(trataRespuestaHorasDeSolDiarias);
    }

    function trataRespuestaHorasDeSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Horas de Sol Diarias',
            subtitle: 'Comparativa horas de sol diarias',
          },
		  explorer: {},
          colors: ['#BFA71F', '#7F6F15','#FFDF2A' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  vAxis: { title: 'Horas de Sol (h)'},
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoHorasDeSolDiarias'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	function graficoRadiacionNetaDiaria() {
		
		
      var queryRadiacionNetaDiaria = encodeURIComponent('select C, sum(AB) where B >= 2014 group by C pivot B');

      var queryCompletaRadiacionNetaDiaria = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryRadiacionNetaDiaria);
      queryCompletaRadiacionNetaDiaria.send(trataRespuestaRadiacionNetaDiaria);
    }

    function trataRespuestaRadiacionNetaDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Radiación neta diaria en MJ/m&#178',
            subtitle: 'Comparativa radiación neta diaria',
          },
		  explorer: {},
          colors: ['#BF480A', '#FF600D','#E5570C' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoRadiacionNetaDiaria'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	
	
	function graficoRadiacionNetaDiaria() {
		
		
      var queryRadiacionNetaDiaria = encodeURIComponent('select C, sum(AB) where B >= 2014 group by C pivot B');

      var queryCompletaRadiacionNetaDiaria = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryRadiacionNetaDiaria);
      queryCompletaRadiacionNetaDiaria.send(trataRespuestaRadiacionNetaDiaria);
    }

    function trataRespuestaRadiacionNetaDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Radiación neta diaria en MJ/m&#178',
            subtitle: 'Comparativa radiación neta diaria',
          },
		  explorer: {},
          colors: ['#BF480A', '#FF600D','#E5570C' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  vAxis: {title: 'Radiación neta diaria en MJ/m²'},
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoRadiacionNetaDiaria'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	function cargaMedidaDiasDeLluvia() {
				
      var queryEncoded = encodeURIComponent('select count(AA) where B = 2016 and AA>0 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaDiasDeLluvia);
    }

    function trataRespuestaDiasDeLluvia(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('diasDeLluvia').innerHTML = datos.getValue(0,0).toFixed(2);;
    }
			

	
	function cargaMedidaPrecipitacionAcumulada() {
				
      var queryEncoded = encodeURIComponent('select sum(AA) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaPrecipitacionAcumulada);
    }

    function trataRespuestaPrecipitacionAcumulada(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('pecipitacionacumulada').innerHTML = datos.getValue(0,0).toFixed(2);
	  document.getElementById('precipitacion-widget').innerHTML = datos.getValue(0,0).toFixed(2);
    }

	function cargaMedidaMaximaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select max(AG) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximaTemperaturaDiurna);
    }

    function trataRespuestaMaximaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMinimaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select min(AI) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMinimaTemperaturaDiurna);
    }

    function trataRespuestaMinimaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('minimaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select avg(AH) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaTemperaturaDiurna);
    }

    function trataRespuestaMediaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	  document.getElementById('temperatura-widget').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select avg(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaHorasSolDiarias);
    }

    function trataRespuestaMediaHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaHorasSolDiarias').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMaximoHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select max(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximoHorasSolDiarias);
    }

    function trataRespuestaMaximoHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximasHorasSolDiarias').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaAcumuladoHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select sum(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaAcumuladoHorasSolDiarias);
    }

    function trataRespuestaAcumuladoHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('horasSolAcumuladas').innerHTML = datos.getValue(0,0).toFixed(2);
	  document.getElementById('horasSol-widget').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMaximoRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select max(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximoRadiacionDiaria);
    }

    function trataRespuestaMaximoRadiacionDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximoRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select avg(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaRadiacionlDiaria);
    }

    function trataRespuestaMediaRadiacionlDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	  document.getElementById('radiacion-widget').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaAcumuladoRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select sum(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaAcumuladoRadiacionDiaria);
    }

    function trataRespuestaAcumuladoRadiacionDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('acumuladoRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	// Script to open and close sidenav
function w3_open() {
    document.getElementsByClassName("w3-sidenav")[0].style.display = "block";
    document.getElementsByClassName("w3-overlay")[0].style.display = "block";
}
 
function w3_close() {
    document.getElementsByClassName("w3-sidenav")[0].style.display = "none";
    document.getElementsByClassName("w3-overlay")[0].style.display = "none";
}