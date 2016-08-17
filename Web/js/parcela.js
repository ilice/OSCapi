/**
 * 
 */

var mapa;
var parcela = {};
var informacionPoligono;

/*
 * Los Google Charts no son responsive por lo que es necesario pintarlos de
 * nuevo cuado se produce un cambio de tamaño de la pantalla
 */
$(window).resize(function() {
	graficoPrecipitacionPorMesYAnio();
	graficoTemperaturasMediasDiurnas();
	graficoRadiacionNetaDiaria();
	graficoHorasDeSolDiarias();
});

$(window).load(function() {

	// Si voy a un sitio determinado de la página, no cargo el tour, por ejemplo
	// cuando voy directamente al cacharrito
	if (!location.hash) {
		$('#chooseID').joyride({
			autoStart : true,
			postStepCallback : function(index, tip) {
				if (index == 15) {
					$(this).joyride('set_li', false, 1);
				}
			},
			modal : true,
			expose : true
		});
	}
});

function initMap(coordenadasLinde) {
	var mapOptions = {
		center : parcela,
		zoom : 16,
		mapTypeId : google.maps.MapTypeId.SATELLITE
	}

	mapa = new google.maps.Map(document.getElementById('mapa'), mapOptions);

	var centerControlDiv = document.createElement('div');
	var centerControl = new CenterControl(centerControlDiv, mapa);

	centerControlDiv.index = 1;
	mapa.controls[google.maps.ControlPosition.LEFT_CENTER]
			.push(centerControlDiv);

	var marker = new google.maps.Marker({
		position : parcela,
		map : mapa,
		animation : google.maps.Animation.DROP,
		title : 'Parcela'
	});

	//En realidad la parcel apuede estar formada por varios recintos, iteramos para añadir cada uno de ellos como polígono
	for (var i = 0; i< coordenadasLinde.length; i++){
		var recinto = new google.maps.Polygon({
			paths : coordenadasLinde[i],
			strokeColor : '#FF0000',
			strokeOpacity : 0.8,
			strokeWeight : 2,
			fillColor : '#FF0000',
			fillOpacity : 0.35
		});
		recinto.setMap(mapa);

		// Add a listener for the click event.
		recinto.addListener('click', showArrays);

		informacionPoligono = new google.maps.InfoWindow;
	}

	
}

/** @this {google.maps.Polygon} */
function showArrays(event) {
	// Since this polygon has only one path, we can call getPath() to return the
	// MVCArray of LatLngs.
	var vertices = this.getPath();

	var contentString = '<h3>Coordenadas del recinto</h3>'
			+ '<h4>Localización marcada: </h4>' + event.latLng.lat() + ','
			+ event.latLng.lng()
			+ '<h6>Conjunto de coordenadas fijadas por el catastro:</h6><ul>';

	// Iterate over the vertices.
	for (var i = 0; i < vertices.getLength(); i++) {
		var xy = vertices.getAt(i);
		contentString += '<li>' + xy.lat() + ',' + xy.lng() + '</li>';
	}

	contentString += '</ul>';

	// Replace the info window's content and position.
	informacionPoligono.setContent(contentString);
	informacionPoligono.setPosition(event.latLng);

	// TODO: hacer que esta información se muestre en otra parte
	document.getElementById('coordenadasLinde').innerHTML = contentString;
	document.getElementById('coordenadasLindeModal').style.display = 'block';
	// informacionPoligono.open(mapa);

}

/**
 * The CenterControl adds a control to the map that recenters the map on plot.
 *  This constructor takes the control DIV as an argument.
 * 
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
	controlUI.style.marginLeft = '10px';
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

	// Setup the click event listeners: simply set the map to plot coordinates.
	controlUI.addEventListener('click', function() {
		map.setCenter(parcela);
		map.setZoom(20);
	});

}

function obten(campo, anio, tipomedida, variable) {

	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?anio="
			+ anio + "&variable=" + variable + "&tipomedida=" + tipoMedida;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		method : "GET",
		dataType : "json"
	});

	request
			.done(function(response, textStatus, jqXHR) {
				document.getElementById(campo).innerHTML = response[variable][tipomedida].value
						.toFixed(2);
			});
}

function actualiza() {
	
	var url = "php/inforiego_rest.php?accion=actualiza&latitud="
		+ document.getElementById("latitud").innerHTML
	+ "&longitud="
	+ document.getElementById("longitud").innerHTML;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		async: false,
		type : 'GET',
		dataType : "json"
	});
	
}

function cargaDatos() {

	estableceDatosBaseDeLaParcela();
	var c_refpar = obtenDatosCatastro();
	var coordenadasLinde = obtenDatosSIGPAC(c_refpar);

	initMap(coordenadasLinde);

	obtenEstacion();
	actualiza();
	obtenAltitud(document.getElementById("latitud").innerHTML, document
			.getElementById("longitud").innerHTML);

	// obten(2016);
	google.charts.load('current', {
		'packages' : [ 'table', 'bar', 'corechart', 'geochart' ]
	});
	document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";

	google.charts.setOnLoadCallback(cargaUltimoValorHumedadSuelo);
	google.charts.setOnLoadCallback(cargaUltimoValorTemperatura);
	google.charts.setOnLoadCallback(cargaUltimoValorHumedad);
	google.charts.setOnLoadCallback(cargaUltimoValorLluvia);
	google.charts.setOnLoadCallback(cargaUltimoValorLuz);
	google.charts.setOnLoadCallback(cargaUltimoValorBateria);
	google.charts.setOnLoadCallback(cargaUltimaLatitudCacharrito);
	google.charts.setOnLoadCallback(cargaUltimaLongitudCacharrito);

	google.charts.setOnLoadCallback(cargaMedidaDiasDeLluviaYPrecipitacionAcumulada);
	google.charts.setOnLoadCallback(cargaMedidasDiarias);
	
	google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
	google.charts.setOnLoadCallback(graficoTemperaturasMediasDiurnas);
	google.charts.setOnLoadCallback(graficoHorasDeSolDiarias);
	google.charts.setOnLoadCallback(graficoRadiacionNetaDiaria);

}

function obtenEstacion() {

	var url = "https://script.google.com/macros/s/AKfycbyJ1Qb6CIlZYvW6poU-qAl2MPoEVD-kws2frLnsmOScu-ezbwA/exec?accion=obtenEstacion&latitud="
			+ document.getElementById("latitud").innerHTML
			+ "&longitud="
			+ document.getElementById("longitud").innerHTML;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		method : "GET",
		dataType : "json"
	});

	request
			.done(function(response, textStatus, jqXHR) {
				document.getElementById("estacionLluvia").innerHTML = response["ESTACION"];
				document.getElementById("estacionTemperatura").innerHTML = response["ESTACION"];
				document.getElementById("estacionSol").innerHTML = response["ESTACION"];
				document.getElementById("estacionRadiacion").innerHTML = response["ESTACION"];

			});
}

function obtenDatosCatastro() {
	
	var url = "php/catastro_coord.php?SRS=EPSG:4326&Coordenada_X="
		+ document.getElementById("longitud").innerHTML
		+ "&Coordenada_Y="
		+ document.getElementById("latitud").innerHTML;

	
	// En los datos de SIGPAC se usa en luegar de la referencia catastral, un
	// código de parcela que tiene pinta de estar formado por:
	// código de provincia: 2 dígitos
	// código de municipio: 3 dígitos
	// código de polígono: 8 dígitos con ceros a la izda para completar
	// código de parcela: 5 dígitos con ceros a la izda para completar
	var c_refpar;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.

	var request = jQuery.ajax({
		url : url,
		async : false,
		type : 'GET',
		dataType : "xml"
	});

	request
			.done(function(response, textStatus, jqXHR) {

						var xmlDoc = response;
						var coordenadas = xmlDoc
								.getElementsByTagName("coordenadas");
						var coord = coordenadas[0]
								.getElementsByTagName("coord");

						var rc = coord[0].getElementsByTagName("pc")[0]
								.getElementsByTagName("pc1")[0].childNodes[0].nodeValue
								+ coord[0].getElementsByTagName("pc")[0]
										.getElementsByTagName("pc2")[0].childNodes[0].nodeValue;
						document.getElementById("rc").innerHTML = rc;
						document.getElementById("direccion").innerHTML = coord[0]
								.getElementsByTagName("ldt")[0].childNodes[0].nodeValue;
						var provincia = "";
						var municipio = "";
						// Curiosamente me obliga a pasar provincia y municipio
						// pero se lo puedo pasar en blanco y funciona igual XD
						c_refpar = obtenDatosPorReferenciaCatastral(rc,
								provincia, municipio);
					});


	return c_refpar
}

function obtenProvincia(rc) {

	var codigoProvincia = rc.substr(0, 2);

	var url = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia";

	var yql = 'http://query.yahooapis.com/v1/public/yql?q='
			+ encodeURIComponent('select * from xml where url="' + url + '"')
			+ '&format=xml&callback=?';

	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$
			.getJSON(
					yql,
					function(data) {
						xml = data.results[0];
						// console.log(xml);

						var xmlDoc = jQuery.parseXML(xml);
						var provs = xmlDoc.getElementsByTagName("provinciero")[0].getElementsByTagName["prov"];

						for (var i = 0; i < provs.length; i++) {
							var prov = provs[i].getElementsByTagName("cpine")[0].childNodes[0].nodeValue;
							if (prov == codigoProvincia) {
								return provs[i].getElementsByTagName("np")[0].childNodes[0].nodeValue;
							}
						}

					});

	return "";

}

function obtenMunicipio(rc) {

	var codigoMunicipio = rc.substr(2, 3);

	var url = "http://ovc.catastro.meh.es//ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?Provincia="
			+ obtenProvincia(rc);

	var yql = 'http://query.yahooapis.com/v1/public/yql?q='
			+ encodeURIComponent('select * from xml where url="' + url + '"')
			+ '&format=xml&callback=?';

	var xml;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.
	$
			.getJSON(
					yql,
					function(data) {
						xml = data.results[0];
						// console.log(xml);

						var xmlDoc = jQuery.parseXML(xml);
						var munis = xmlDoc.getElementsByTagName("municipiero")[0].getElementsByTagName["muni"];

						for (var i = 0; i < munis.length; i++) {
							var muni = munis[i].getElementsByTagName("locat")[0]
									.getElementsByTagName("cmc")[0].childNodes[0].nodeValue;
							if (muni == codigoMunicipio) {
								return munis[i].getElementsByTagName("nm")[0].nodeValue;
							}
						}

					});

	return "";

}

function obtenDatosPorReferenciaCatastral(rc, provincia, municipio) {

	// devuelve un xml y no se puede obtener por cross domain, aquí para
	// resolverlo se utiliza un proxy de yahoo que en realidad da más
	// posibilidades para cruzar datos pero está limitado en número de
	// peticiones diarias
	var url = "php/catastro_rc.php?RC=" + rc + "&Provincia=" + provincia
			+ "&Municipio=" + municipio;

	
	// En los datos de SIGPAC se usa en luegar de la referencia catastral, un
	// código de parcela que tiene pinta de estar formado por:
	// código de provincia: 2 dígitos
	// código de municipio: 3 dígitos
	// código de polígono: 8 dígitos con ceros a la izda para completar
	// código de parcela: 5 dígitos con ceros a la izda para completar
	var c_refpar;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.

	var request = jQuery.ajax({
		url : url,
		async : false,
		type : 'GET',
		dataType : "xml"
	});

	request
			.done(function(response, textStatus, jqXHR) {

				var xmlDoc = response;

				var bi = xmlDoc.getElementsByTagName("bico")[0]
						.getElementsByTagName("bi");
				var cn = bi[0].getElementsByTagName("idbi")[0]
						.getElementsByTagName("cn")[0].childNodes[0].nodeValue;

				switch (cn) {
				case "RU":
					document.getElementById("cn").innerHTML = "rústico";
					break;
				default:

				}

				var control = xmlDoc.getElementsByTagName("control");
				var cucons = control[0].getElementsByTagName("cucons");
				if (cucons.length > 0) {
					document.getElementById("cucons").innerHTML = cucons[0].childNodes[0].nodeValue;
				} else {
					document.getElementById("cucons").innerHTML = 0;
				}

				var cucul = control[0].getElementsByTagName("cucul");
				if (cucul.length > 0) {
					document.getElementById("cucul").innerHTML = cucul[0].childNodes[0].nodeValue;
				} else {
					document.getElementById("cucul").innerHTML = 0;
				}

				npa = bi[0].getElementsByTagName("dt")[0]
						.getElementsByTagName("locs")[0]
						.getElementsByTagName("lors")[0]
						.getElementsByTagName("lorus")[0]
						.getElementsByTagName("npa")[0].childNodes[0].nodeValue;

				// document.getElementById("npa").innerHTML = npa;
				// document.getElementById("nm").innerHTML =
				// bi[0].getElementsByTagName("dt")[0].getElementsByTagName("nm")[0].childNodes[0].nodeValue;
				// document.getElementById("np").innerHTML =
				// bi[0].getElementsByTagName("dt")[0].getElementsByTagName("np")[0].childNodes[0].nodeValue;
				var dspr = xmlDoc.getElementsByTagName("bico")[0]
						.getElementsByTagName("lspr")[0]
						.getElementsByTagName("spr")[0]
						.getElementsByTagName("dspr");
				document.getElementById("ccc").innerHTML = dspr[0]
						.getElementsByTagName("ccc")[0].childNodes[0].nodeValue
						+ dspr[0].getElementsByTagName("dcc")[0].childNodes[0].nodeValue;
				document.getElementById("ip").innerHTML = dspr[0]
						.getElementsByTagName("ip")[0].childNodes[0].nodeValue;
				document.getElementById("ssp").innerHTML = dspr[0]
						.getElementsByTagName("ssp")[0].childNodes[0].nodeValue;

				var cp = ("00" + bi[0].getElementsByTagName("dt")[0]
						.getElementsByTagName("loine")[0]
						.getElementsByTagName("cp")[0].childNodes[0].nodeValue)
						.slice(-2);
				var cmc = ("000" + bi[0].getElementsByTagName("dt")[0]
						.getElementsByTagName("cmc")[0].childNodes[0].nodeValue)
						.slice(-3);
				var cpo = ("00000000" + bi[0].getElementsByTagName("dt")[0]
						.getElementsByTagName("locs")[0]
						.getElementsByTagName("lors")[0]
						.getElementsByTagName("lorus")[0]
						.getElementsByTagName("cpp")[0]
						.getElementsByTagName("cpo")[0].childNodes[0].nodeValue)
						.slice(-8);
				var cpa = ("0000" + bi[0].getElementsByTagName("dt")[0]
						.getElementsByTagName("locs")[0]
						.getElementsByTagName("lors")[0]
						.getElementsByTagName("lorus")[0]
						.getElementsByTagName("cpp")[0]
						.getElementsByTagName("cpa")[0].childNodes[0].nodeValue)
						.slice(-5);
				c_refpar = cp + cmc + cpo + cpa;

			});

	return c_refpar;

}

function graficoPrecipitacionPorMesYAnio() {
	
	var tabla = obtenDatosPorAnio("PRECIPITACION", 3, "month", "M");
	
	var columnas = tabla.cols;
	var filas = tabla.rows;
	
	var dt = new google.visualization.DataTable();

	for(var i = 0; i < columnas.length; i++){
		dt.addColumn(columnas[i].type, columnas[i].label);
	}
	dt.addRows(filas);
	
	var opciones = {
			chart : {
				title : 'Precipitaciones mensuales en mm',
				subtitle : 'Comparativa acumulado mensual últimos años',
			},
			bars : 'vertical',
			colors : [ '#94E8B4', '#72BDA3', '#5E8C61', '#426A4D', '#4E6151',
					'#3B322C', '#7246F2' ],
			hAxis : {
				title : 'Mes'
			},
			vAxis : {
				title : 'Precipitación en mm'
			}
		};

	var grafica = new google.visualization.ColumnChart(document
			.getElementById('graficoPrecipitacionPorMesYAnio'));
	// chart.draw(data, google.charts.Bar.convertOptions(options));
	grafica.draw(dt, opciones);
}

function graficoTemperaturasMediasDiurnas() {

	var tabla = obtenDatosPorAnio("TEMPMEDIA", 3, "day", "DDD");
	
	var columnas = tabla.cols;
	var filas = tabla.rows;
	
	var dt = new google.visualization.DataTable();

	for(var i = 0; i < columnas.length; i++){
		dt.addColumn(columnas[i].type, columnas[i].label);
	}
	dt.addRows(filas);


	var opciones = {
		chart : {
			title : 'Temperaturas medias diurnas',
			subtitle : 'Comparativa temperatura media diurna últimos años',
		},
		explorer : {},
		colors : [ '#7F0D0B', '#BF1411', '#400706' ],
		hAxis : {
			title : 'Día del año',
			gridlines : {
				count : 12
			}
		},
		vAxis : {
			title : 'Temperatura en ºC'
		},
		series : {
			0 : {

				lineWidth : 1

			},
			1 : {

				lineWidth : 1

			},
			2 : {

				lineWidth : 2

			}
		}
	};

	

	var grafica = new google.visualization.LineChart(document
			.getElementById('graficoTemperaturaMediaDiurna'));
	// chart.draw(data, google.charts.Bar.convertOptions(options));
	grafica.draw(dt, opciones);
}

function graficoHorasDeSolDiarias() {

var tabla = obtenDatosPorAnio("N", 3, "day", "DDD");
	
	var columnas = tabla.cols;
	var filas = tabla.rows;
	
	var dt = new google.visualization.DataTable();

	for(var i = 0; i < columnas.length; i++){
		dt.addColumn(columnas[i].type, columnas[i].label);
	}
	dt.addRows(filas);

	var opciones = {
		chart : {
			title : 'Horas de Sol Diarias',
			subtitle : 'Comparativa horas de sol diarias',
		},
		explorer : {},
		colors : [ '#BFA71F', '#7F6F15', '#FFDF2A' ],
		hAxis : {
			title : 'Día del año',
			gridlines : {
				count : 12
			}
		},
		vAxis : {
			title : 'Horas de Sol (h)'
		},
		series : {
			0 : {

				lineWidth : 1

			},
			1 : {

				lineWidth : 1

			},
			2 : {

				lineWidth : 2

			}
		}
	};

	

	var grafica = new google.visualization.LineChart(document
			.getElementById('graficoHorasDeSolDiarias'));
	// chart.draw(data, google.charts.Bar.convertOptions(options));
	grafica.draw(dt, opciones);
}

function graficoRadiacionNetaDiaria() {

var tabla = obtenDatosPorAnio("RADIACION", 3, "day", "DDD");
	
	var columnas = tabla.cols;
	var filas = tabla.rows;
	
	var dt = new google.visualization.DataTable();

	for(var i = 0; i < columnas.length; i++){
		dt.addColumn(columnas[i].type, columnas[i].label);
	}
	dt.addRows(filas);

	var opciones = {
		chart : {
			title : 'Radiación neta diaria en MJ/m&#178',
			subtitle : 'Comparativa radiación neta diaria',
		},
		explorer : {},
		colors : [ '#BF480A', '#FF600D', '#E5570C' ],
		hAxis : {
			title : 'Día del año',
			gridlines : {
				count : 12
			}
		},
		series : {
			0 : {

				lineWidth : 1

			},
			1 : {

				lineWidth : 1

			},
			2 : {

				lineWidth : 2

			}
		}
	};

	var grafica = new google.visualization.LineChart(document
			.getElementById('graficoRadiacionNetaDiaria'));
	// chart.draw(data, google.charts.Bar.convertOptions(options));
	grafica.draw(dt, opciones);
}



function cargaUltimoValorHumedadSuelo() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'HumedadSuelo' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorHumedadSuelo);
}

function trataUltimoValorHumedadSuelo(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaHumedadSuelo').innerHTML = datos
			.getValue(0, 0).toLocaleString();
	document.getElementById('ultimaMedidaHumedadSuelo').innerHTML = datos
			.getValue(0, 1).toFixed(2);
}

function cargaUltimoValorTemperatura() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Temperatura' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorTemperatura);
}

function trataUltimoValorTemperatura(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaTemperatura').innerHTML = datos
			.getValue(0, 0).toLocaleString();
	document.getElementById('ultimaMedidaTemperatura').innerHTML = datos
			.getValue(0, 1).toFixed(2);
}

function cargaUltimoValorHumedad() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Humedad' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorHumedad);
}

function trataUltimoValorHumedad(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaHumedad').innerHTML = datos
			.getValue(0, 0).toLocaleString();
	document.getElementById('ultimaMedidaHumedad').innerHTML = datos.getValue(
			0, 1);
}

function cargaUltimoValorLluvia() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Lluvia' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorLluvia);
}

function trataUltimoValorLluvia(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaLluvia').innerHTML = datos
			.getValue(0, 0).toLocaleString();
	document.getElementById('ultimaMedidaLluvia').innerHTML = datos.getValue(0,
			1);
}

function cargaUltimoValorLuz() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Luz' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorLuz);
}

function trataUltimoValorLuz(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaLuz').innerHTML = datos.getValue(
			0, 0).toLocaleString();
	document.getElementById('ultimaMedidaLuz').innerHTML = datos.getValue(0, 1);
}

function cargaUltimoValorBateria() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Bateria' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimoValorBateria);
}

function trataUltimoValorBateria(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('horaUltimaMedidaBateria').innerHTML = datos
			.getValue(0, 0).toLocaleString();
	document.getElementById('ultimaMedidaBateria').innerHTML = datos.getValue(
			0, 1);
}

function cargaUltimaLatitudCacharrito() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Latitud' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimaLatitudCacharrito);
}

function trataUltimaLatitudCacharrito(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('ultimaPosicionLatitud').innerHTML = datos
			.getValue(0, 1);
}

function cargaUltimaLongitudCacharrito() {

	var queryEncoded = encodeURIComponent("select A, D where C = 'Longitud' order by A desc limit 1");

	var queryCompleted = new google.visualization.Query(
			'https://docs.google.com/spreadsheets/d/1xR-yM3fqh_bvkzs1dbUMZR9pb6AoJpAdtVyF5h18vgY/gviz/tq?gid=0&headers=1&tq='
					+ queryEncoded);
	queryCompleted.send(trataUltimaLongitudCacharrito);
}

function trataUltimaLongitudCacharrito(respuesta) {
	if (respuesta.isError()) {
		alert('Error en query: ' + respuesta.getMessage() + ' '
				+ respuesta.getDetailedMessage());
		return;
	}

	var datos = respuesta.getDataTable();

	document.getElementById('ultimaPosicionLongitud').innerHTML = datos
			.getValue(0, 1);
}

function cargaMedidaDiasDeLluviaYPrecipitacionAcumulada() {
	
	var hoy = new Date();
	
	var diasDeLluvia = 0;
	var precipitacionAcumulada = 0;
	
	var url = "php/inforiego_rest.php?accion=diasDeLluvia&latitud="
		+ document.getElementById("latitud").innerHTML
	+ "&longitud="
	+ document.getElementById("longitud").innerHTML
	+ "&anio="
	+ hoy.getFullYear();

	var request = jQuery.ajax({
		crossDomain : true,
		async : false,
		url : url,
		type : 'GET',
		dataType : "json"
	});
	
	request
	.done(function(response, textStatus, jqXHR) {
		diasDeLluvia = response.diasDeLluvia;
		precipitacionAcumulada = response.precipitacionAcumulada.toFixed(2);
	});
	
	document.getElementById('diasDeLluvia').innerHTML = diasDeLluvia;
	document.getElementById('pecipitacionacumulada').innerHTML = precipitacionAcumulada;
	document.getElementById('precipitacion-widget').innerHTML = precipitacionAcumulada;

}

function cargaMedidasDiarias() {
	
var hoy = new Date();
	
	var min_temperatura = 0;
	var max_temperatura = 0;
	var media_temperatura = 0;
		
	var url = "php/inforiego_rest.php?accion=temperaturaDiaria&latitud="
		+ document.getElementById("latitud").innerHTML
	+ "&longitud="
	+ document.getElementById("longitud").innerHTML
	+ "&anio="
	+ hoy.getFullYear();

	var request = jQuery.ajax({
		crossDomain : true,
		async : false,
		url : url,
		type : 'GET',
		dataType : "json"
	});
	
	request
	.done(function(response, textStatus, jqXHR) {
		min_temperatura = response.min_temperatura.toFixed(2);
		max_temperatura = response.max_temperatura.toFixed(2);
		media_temperatura = response.media_temperatura.toFixed(2);
		media_horas_sol = response.media_horas_sol.toFixed(2);
		max_horas_sol = response.max_horas_sol.toFixed(2);
		sum_horas_sol = response.sum_horas_sol.toFixed(2);
		media_radiacion = response.media_radiacion.toFixed(2);
		max_radiacion = response.max_radiacion.toFixed(2);
		sum_radiacion = response.sum_radiacion.toFixed(2);
	});

	document.getElementById('maximaTemperaturaDiurna').innerHTML = max_temperatura;
	document.getElementById('minimaTemperaturaDiurna').innerHTML = min_temperatura;
	document.getElementById('mediaTemperaturaDiurna').innerHTML = media_temperatura;
	document.getElementById('temperatura-widget').innerHTML = media_temperatura;
	document.getElementById('mediaHorasSolDiarias').innerHTML = media_horas_sol;
	document.getElementById('maximasHorasSolDiarias').innerHTML = max_horas_sol;
	document.getElementById('horasSolAcumuladas').innerHTML = sum_horas_sol;
	document.getElementById('horasSol-widget').innerHTML = sum_horas_sol;
	document.getElementById('maximoRadiacionNetaDiaria').innerHTML = max_radiacion;
	document.getElementById('mediaRadiacionNetaDiaria').innerHTML = media_radiacion;
	document.getElementById('acumuladoRadiacionNetaDiaria').innerHTML = sum_radiacion;
	document.getElementById('radiacion-widget').innerHTML = sum_radiacion;
}

function obtenAltitud(latitud, longitud) {

	var url = "php/altitud.php?locations=" + latitud + "," + longitud;

	var request = jQuery.ajax({

		url : url,
		type : 'GET',
		dataType : "json"
	});

	request.done(function(response, textStatus, jqXHR) {
		var hits = response["results"][0]["elevation"].toFixed() + " m";
		document.getElementById('altitud').innerHTML = hits;
		document.getElementById('altitud_idea').innerHTML = hits;
		var urlbusqueda = "location.href='cultivos.html?altitud="
				+ response["results"][0]["elevation"].toFixed() + "'";
		document.getElementById('cultivos_por_altitud').setAttribute('onclick',
				urlbusqueda);
	});

}

function estableceDatosBaseDeLaParcela() {
	// El objeto window representa la ventana del navegador abierta
	// Location contiene la información de la URL de la ventana
	// Search devuelve desde la ? incluida, hacemos el substring(1) para quitar
	// la ?
	var query = window.location.search.substring(1);

	if (query.length > 0) {
		// Si la query tiene algo
		var vars = query.split("&");
		for (var i = 0; i < vars.length; i++) {
			var pair = vars[i].split("=");
			// If first entry with this name
			switch (pair[0]) {
			case "latitud":
				parcela.lat = Number(pair[1]);
				document.getElementById('latitud').innerHTML = parcela.lat;
				break;
			case "longitud":
				parcela.lng = Number(pair[1]);
				document.getElementById('longitud').innerHTML = parcela.lng;
				break;
			case "nombre":
				document.getElementById('pagina').innerHTML = decodeURI(pair[1]);
				break;
			default:
				break;
			}
		}
	}
}

function obtenDatosSIGPAC(c_refpar) {

	var url = "php/api_rest.php/plots/sigpac_record/_search?q=c_refpar:"
			+ c_refpar;
	var coordenadasLinde = [];

	var request = jQuery.ajax({
		crossDomain : true,
		async : false,
		url : url,
		type : 'GET',
		dataType : "json"
	});

	request
			.done(function(response, textStatus, jqXHR) {
				var hits = response["hits"]["hits"];

				for (var i = 0; i < hits.length; i++) {

					var hit = hits[i];

					coordenadasLinde.push(arrayToPathLatLong(hit["_source"]["points"]["coordinates"][0]));
				}
			});
	return coordenadasLinde;
}

function arrayToPathLatLong(array) {
	var paths = [];

	for (var i = 0; i < array.length; i++) {
		var path = {};
		path.lat = array[i][0];
		path.lng = array[i][1];
		paths.push(path);
	}

	return paths;
}

function obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato){
	
	var datos;
	
	var url = "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud="
		+ document.getElementById("latitud").innerHTML
	+ "&longitud="
	+ document.getElementById("longitud").innerHTML
	+ "&medida="
	+ medida
	+ "&numeroDeAnios="
	+ numeroDeAnios
	+ "&intervalo="
	+ intervalo
	+ "&formato="
	+ formato;

	var request = jQuery.ajax({
		crossDomain : true,
		async : false,
		url : url,
		type : 'GET',
		dataType : "json"
	});
	
	request
	.done(function(response, textStatus, jqXHR) {
		datos = response;
	});
	
	return datos;
}