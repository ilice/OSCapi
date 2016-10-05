/**
 * 
 */

var mapa;
var parcela = {};
var informacionPoligono;
var fixedData = false;

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
	// cuando voy directamente al cacharrito o bien si estoy cargando datos
	// fijos
	if (!location.hash && (window.location.search.substring(1).length > 0)) {
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

function cargaDatos() {

	estableceDatosBaseDeLaParcela();
	var c_refpar = obtenDatosCatastro();

	var fixedCoords = [ [ {
		lng : -5.73743277138396,
		lat : 40.4390893833596
	}, {
		lng : -5.7374292381294,
		lat : 40.4390894670862
	}, {
		lng : -5.73739180024054,
		lat : 40.4390907145335
	}, {
		lng : -5.73725167450709,
		lat : 40.4391382615966
	}, {
		lng : -5.73724113701022,
		lat : 40.4391749014607
	}, {
		lng : -5.73721803154044,
		lat : 40.4392562459453
	}, {
		lng : -5.73718072633477,
		lat : 40.4393856619662
	}, {
		lng : -5.73714289614587,
		lat : 40.4394992417711
	}, {
		lng : -5.73709900898761,
		lat : 40.4395972020055
	}, {
		lng : -5.73705224582516,
		lat : 40.4397114438101
	}, {
		lng : -5.73699952384232,
		lat : 40.4398442920897
	}, {
		lng : -5.73695236415262,
		lat : 40.4399778192313
	}, {
		lng : -5.7370488836958,
		lat : 40.440017687337
	}, {
		lng : -5.73708040409467,
		lat : 40.4400274792416
	}, {
		lng : -5.73710763776926,
		lat : 40.4399868408083
	}, {
		lng : -5.73712811791558,
		lat : 40.4399337519324
	}, {
		lng : -5.73714969089239,
		lat : 40.4398814478309
	}, {
		lng : -5.7371687868795,
		lat : 40.4398291123418
	}, {
		lng : -5.73717846353938,
		lat : 40.4397915921367
	}, {
		lng : -5.73719421568004,
		lat : 40.4397383450527
	}, {
		lng : -5.73721632635996,
		lat : 40.4396963867868
	}, {
		lng : -5.73724294352035,
		lat : 40.4396492775525
	}, {
		lng : -5.73727487779192,
		lat : 40.4395821358146
	}, {
		lng : -5.73732973018171,
		lat : 40.4394203229537
	}, {
		lng : -5.73739206998265,
		lat : 40.4392658133442
	}, {
		lng : -5.73743630057109,
		lat : 40.4391501902217
	}, {
		lng : -5.73745579242689,
		lat : 40.4391018085895
	}, {
		lng : -5.73743277138396,
		lat : 40.4390893833596
	}, {
		lng : -5.73743277138396,
		lat : 40.4390893833596
	} ] ];
	var coordenadasLinde = fixedData ? fixedCoords : obtenDatosSIGPAC(c_refpar);

	initMap(coordenadasLinde);
	
	cargaUltimosValores_osc_station();

	
	
	if (!fixedData) {
		// actualiza();
	}
	obtenAltitud(document.getElementById("latitud").innerHTML, document
			.getElementById("longitud").innerHTML);

	obtenEstacion();
	
	cargaMedidaDiasDeLluviaYPrecipitacionAcumulada();
	
	cargaMedidasDiarias();

	if (fixedData){document.getElementById("fixed").style.display = 'inline';}
	if (!fixedData) {
		// obten(2016);
		

		google.charts.load('current', {
			'packages' : [ 'table', 'bar', 'corechart', 'geochart' ]
		});
		document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";

		google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
		google.charts.setOnLoadCallback(graficoTemperaturasMediasDiurnas);
		google.charts.setOnLoadCallback(graficoHorasDeSolDiarias);
		google.charts.setOnLoadCallback(graficoRadiacionNetaDiaria);

	} else {
		document.getElementById("graficoPrecipitacionPorMesYAnio").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedRainChart.PNG\" >";
		document.getElementById("graficoTemperaturaMediaDiurna").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedTempChart.PNG\" >";
		document.getElementById("graficoHorasDeSolDiarias").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedSunChart.PNG\" >";
		document.getElementById("graficoRadiacionNetaDiaria").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedRadiationChart.PNG\" >";
		openCultivo("All")
	}

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
	} else {
		document.getElementById('latitud').innerHTML = Number(40.439983);
		parcela.lat = 40.439983;
		document.getElementById('longitud').innerHTML = Number(-5.737026);
		parcela.lng = -5.737026;
		document.getElementById('pagina').innerHTML = decodeURI('Viña%20de%20la%20estación');
		fixedData = true;

	}
}

function obtenDatosCatastro() {

	var end_point = "OVCCoordenadas.asmx/Consulta_RCCOOR";

	var url = "php/catastro.php?end_point=" + end_point
			+ " &SRS=EPSG:4326&Coordenada_X="
			+ document.getElementById("longitud").innerHTML + "&Coordenada_Y="
			+ document.getElementById("latitud").innerHTML;

	// En los datos de SIGPAC se usa en luegar de la referencia catastral, un
	// código de parcela que tiene pinta de estar formado por:
	// código de provincia: 2 dígitos
	// código de municipio: 3 dígitos
	// código de polígono: 8 dígitos con ceros a la izda para completar
	// código de parcela: 5 dígitos con ceros a la izda para completar
	var c_refpar;

	if (!fixedData) {
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

					if (coordenadas.length > 0) {
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
					} else {

						document.getElementById("datosCatastro").innerHTML = '<span onclick="this.parentElement.style.display=\'none\'"'
								+ 'class="w3-closebtn">&times;</span>'
								+ '<h3>Error en la obtención de los datos de la Sede Electrónica del Catastro</strong></h3>'
								+ '<p>Se han intentado recuperar los datos públicos del catastro para la parcela, pero ha ocurrido algún problema.</p>'
								+ 'Si el problema persiste puede contactar con <a href="mailto:info@opensmartcountry.com">info@opensmartcountry.com</a></p>';
						document.getElementById("datosCatastroErrorBadge").style.display = 'block';
					}
				});

	} else {
		document.getElementById("rc").innerHTML = '37284A00600098';
		document.getElementById("direccion").innerHTML = 'Polígono 6 Parcela 98 FTE LUMBRAL. SANCHOTELLO (SALAMANCA)';
		c_refpar = obtenDatosPorReferenciaCatastral('37284A00600098', "", "");
		;
	}
	return c_refpar
}

function obtenDatosPorReferenciaCatastral(rc, provincia, municipio) {

	var end_point = "OVCCallejero.asmx/Consulta_DNPRC";

	var url = "php/catastro.php?end_point=" + end_point + "&RC=" + rc
			+ "&Provincia=" + provincia + "&Municipio=" + municipio;

	// En los datos de SIGPAC se usa en luegar de la referencia catastral, un
	// código de parcela que tiene pinta de estar formado por:
	// código de provincia: 2 dígitos
	// código de municipio: 3 dígitos
	// código de polígono: 8 dígitos con ceros a la izda para completar
	// código de parcela: 5 dígitos con ceros a la izda para completar
	var c_refpar;

	// Request that YSQL string, and run a callback function.
	// Pass a defined function to prevent cache-busting.

	if (!fixedData) {
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
	} else {
		document.getElementById("cn").innerHTML = "rústico";
		document.getElementById("cucons").innerHTML = 0;
		document.getElementById("cucul").innerHTML = 0;
		document.getElementById("ccc").innerHTML = 'e-pastos';
		document.getElementById("ip").innerHTML = 0;
		document.getElementById("ssp").innerHTML = 1409;
		c_refpar = '372840000000600098';

	}

	return c_refpar;

}

function obtenDatosSIGPAC(c_refpar) {

	var url = "php/api_rest.php/plots" +
			"/sigpac/_search?q=c_refpar:"
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
				var hayCoordenadasLinde = false;
				if (typeof response["hits"] != 'undefined') {
					var hits = response["hits"]["hits"];

					for (var i = 0; i < hits.length; i++) {

						var hit = hits[i];

						coordenadasLinde
								.push(arrayToPathLatLong(hit["_source"]["points"]["coordinates"][0]));
						hayCoordenadasLinde = true;
					}

				}
				if (!hayCoordenadasLinde) {
					document.getElementById("datosLinde").innerHTML = '<span onclick="this.parentElement.style.display=\'none\'"'
							+ 'class="w3-closebtn">&times;</span>'
							+ '<h3>Error en la obtención de las coordenadas de la linde</strong></h3>'
							+ '<p>Se han intentado recuperar los datos de las coordenadas de la linde de la parcela, pero ha ocurrido algún problema.</p>'
							+ 'Si el problema persiste puede contactar con <a href="mailto:info@opensmartcountry.com">info@opensmartcountry.com</a></p>';
					document.getElementById("datosLindeErrorBadge").style.display = 'block';
				}
			});
	return coordenadasLinde;
}

function cargaUltimosValores_osc_station() {
	if (!fixedData) {
		var url = "php/cacharrito_rest.php/osc_station/osc_station_record/_search?accion=ultimoValor&latitud="
				+ document.getElementById("latitud").innerHTML
				+ "&longitud="
				+ document.getElementById("longitud").innerHTML;

		var ultimosValores;
		var request = jQuery.ajax({
			url : url,
			type : 'GET',
			dataType : "json"
		});

		request
				.done(function(response, textStatus, jqXHR) {
					if (typeof response["hits"] != 'undefined') {
						ultimosValores = response["hits"]["hits"][0];

						var fecha = new Date(ultimosValores._source.FECHA);
						document.getElementById('horaUltimaMedidaHumedadSuelo').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaHumedadSuelo').innerHTML = ultimosValores._source.HumedadSuelo ? ultimosValores._source.HumedadSuelo
								.toFixed(2)
								: "";
						document.getElementById('horaUltimaMedidaTemperatura').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaTemperatura').innerHTML = ultimosValores._source.Temperatura ? ultimosValores._source.Temperatura
								.toFixed(2)
								: "";
						document.getElementById('horaUltimaMedidaHumedad').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaHumedad').innerHTML = ultimosValores._source.Humedad ? ultimosValores._source.Humedad
								.toFixed(2)
								: "";
						document.getElementById('horaUltimaMedidaLluvia').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaLluvia').innerHTML = ultimosValores._source.Lluvia ? ultimosValores._source.Lluvia
								.toFixed(2)
								: "";
						document.getElementById('horaUltimaMedidaLuz').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaLuz').innerHTML = ultimosValores._source.Luz ? ultimosValores._source.Luz
								.toFixed(2)
								: "";
						document.getElementById('horaUltimaMedidaBateria').innerHTML = fecha
								.toLocaleString();
						document.getElementById('ultimaMedidaBateria').innerHTML = ultimosValores._source.Bateria ? ultimosValores._source.Bateria
								.toFixed(2)
								: "";
						document.getElementById('ultimaPosicionLatitud').innerHTML = ultimosValores._source.lat_lon ? ultimosValores._source.lat_lon.lat
								: "";
						document.getElementById('ultimaPosicionLongitud').innerHTML = ultimosValores._source.lat_lon ? ultimosValores._source.lat_lon.lon
								: "";
					} else {

						document.getElementById('horaUltimaMedidaHumedadSuelo').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaHumedadSuelo').style.color = 'red';
						document.getElementById('horaUltimaMedidaTemperatura').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaTemperatura').style.color = 'red';
						document.getElementById('horaUltimaMedidaHumedad').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaHumedad').style.color = 'red';
						document.getElementById('horaUltimaMedidaLluvia').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaLluvia').style.color = 'red';
						document.getElementById('horaUltimaMedidaLuz').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaLuz').style.color = 'red';
						document.getElementById('horaUltimaMedidaBateria').innerHTML = 'Error';
						document.getElementById('horaUltimaMedidaBateria').style.color = 'red';
						document.getElementById('ultimaPosicionLatitud').innerHTML = 'Error';
						document.getElementById('ultimaPosicionLatitud').style.color = 'red';
						document.getElementById('ultimaPosicionLongitud').innerHTML = 'Error';
						document.getElementById('ultimaPosicionLongitud').style.color = 'red';

						document.getElementById("datosOscar").innerHTML = '<span onclick="this.parentElement.style.display=\'none\'"'
							+ 'class="w3-closebtn">&times;</span>'
							+ '<h3>Error en la obtención de los datos de la estación <strong>"OSC&alpha;r"</strong></h3>'
							+ '<p>Se han intentado recuperar los datos de la estación situada en la parcela, pero ha ocurrido algún problema.</p>'
							+ 'Si el problema persiste puede contactar con <a href="mailto:info@opensmartcountry.com">info@opensmartcountry.com</a></p>';
					document.getElementById("datosOscarErrorBadge").style.display = 'block';

					}
				});

	} else {
		document.getElementById('horaUltimaMedidaHumedadSuelo').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaHumedadSuelo').innerHTML = 10;
		document.getElementById('horaUltimaMedidaTemperatura').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaTemperatura').innerHTML = 8;
		document.getElementById('horaUltimaMedidaHumedad').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaHumedad').innerHTML = 70;
		document.getElementById('horaUltimaMedidaLluvia').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaLluvia').innerHTML = 34;
		document.getElementById('horaUltimaMedidaLuz').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaLuz').innerHTML = 56;
		document.getElementById('horaUltimaMedidaBateria').innerHTML = "16/9/2016 09:38:00"
		document.getElementById('ultimaMedidaBateria').innerHTML = 67;
		document.getElementById('ultimaPosicionLatitud').innerHTML = 40.49;
		document.getElementById('ultimaPosicionLongitud').innerHTML = -3.65;
	}
}

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

	// En realidad la parcela apuede estar formada por varios recintos, iteramos
	// para añadir cada uno de ellos como polígono
	for (var i = 0; i < coordenadasLinde.length; i++) {
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
 * This constructor takes the control DIV as an argument.
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

function obtenEstacion() {

	if (!fixedData) {
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
	} else {
		document.getElementById("estacionLluvia").innerHTML = "Losar Del Barco";
		document.getElementById("estacionTemperatura").innerHTML = "Losar Del Barco";
		document.getElementById("estacionSol").innerHTML = "Losar Del Barco";
		document.getElementById("estacionRadiacion").innerHTML = "Losar Del Barco";
	}
}

function cargaMedidaDiasDeLluviaYPrecipitacionAcumulada() {

	var hoy = new Date();

	var diasDeLluvia = 0;
	var precipitacionAcumulada = 0;

	if (!fixedData) {
		var url = "php/inforiego_rest.php?accion=diasDeLluvia&latitud="
				+ document.getElementById("latitud").innerHTML + "&longitud="
				+ document.getElementById("longitud").innerHTML + "&anio="
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
					precipitacionAcumulada = response.precipitacionAcumulada
							.toFixed(2);
				});

		document.getElementById('diasDeLluvia').innerHTML = diasDeLluvia;
		document.getElementById('pecipitacionacumulada').innerHTML = precipitacionAcumulada;
		document.getElementById('precipitacion-widget').innerHTML = precipitacionAcumulada;
	} else {
		document.getElementById('diasDeLluvia').innerHTML = 66;
		document.getElementById('pecipitacionacumulada').innerHTML = 308.54;
		document.getElementById('precipitacion-widget').innerHTML = 308.54;
	}

}

function cargaMedidasDiarias() {

	var hoy = new Date();

	var min_temperatura = 0;
	var max_temperatura = 0;
	var media_temperatura = 0;
	var media_horas_sol = 0;
	var max_horas_sol = 0;
	var sum_horas_sol = 0;
	var sum_horas_sol = 0;
	var max_radiacion = 0;
	var media_radiacion = 0;
	var sum_radiacion = 0;
	var sum_radiacion = 0;
	if (!fixedData) {

		var url = "php/inforiego_rest.php?accion=medidasDiarias&latitud="
				+ document.getElementById("latitud").innerHTML + "&longitud="
				+ document.getElementById("longitud").innerHTML + "&anio="
				+ hoy.getFullYear();

		var request = jQuery.ajax({
			crossDomain : true,
			async : false,
			url : url,
			type : 'GET',
			dataType : "json"
		});

		request.done(function(response, textStatus, jqXHR) {
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

	} else {
		document.getElementById('maximaTemperaturaDiurna').innerHTML = 34.66;
		document.getElementById('minimaTemperaturaDiurna').innerHTML = -6.59;
		document.getElementById('mediaTemperaturaDiurna').innerHTML = 12.66;
		document.getElementById('temperatura-widget').innerHTML = 12.66;
		document.getElementById('mediaHorasSolDiarias').innerHTML = 10.05;
		document.getElementById('maximasHorasSolDiarias').innerHTML = 13.51;
		document.getElementById('horasSolAcumuladas').innerHTML = 2462.54;
		document.getElementById('horasSol-widget').innerHTML = 2462.54;
		document.getElementById('maximoRadiacionNetaDiaria').innerHTML = 34.02;
		document.getElementById('mediaRadiacionNetaDiaria').innerHTML = 20.21;
		document.getElementById('acumuladoRadiacionNetaDiaria').innerHTML = 4951.24;
		document.getElementById('radiacion-widget').innerHTML = 4951.24;
	}
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

	var url = "php/inforiego_rest.php?accion=actualizaDiario&latitud="
			+ document.getElementById("latitud").innerHTML + "&longitud="
			+ document.getElementById("longitud").innerHTML;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		async : false,
		type : 'GET',
		dataType : "json"
	});

}



function obtenProvincia(rc) {

	var codigoProvincia = rc.substr(0, 2);

	var end_point = "OVCCallejero.asmx/ConsultaProvincia";

	var url = "php/catastro.php?end_point=" + end_point;

	var nombre_provincia = "";

	var request = jQuery.ajax({
		url : url,
		async : false,
		type : 'GET',
		dataType : "xml"
	});

	request
			.done(function(response, textStatus, jqXHR) {

				var xmlDoc = response;
				var provs = xmlDoc.getElementsByTagName("provinciero")[0].getElementsByTagName["prov"];

				for (var i = 0; i < provs.length; i++) {
					var prov = provs[i].getElementsByTagName("cpine")[0].childNodes[0].nodeValue;
					if (prov == codigoProvincia) {
						nombre_provincia = provs[i].getElementsByTagName("np")[0].childNodes[0].nodeValue;
					}
				}
			});

	return nombre_provincia;

}

function obtenMunicipio(rc) {

	var codigoMunicipio = rc.substr(2, 3);

	var end_point = "OVCCallejero.asmx/ConsultaMunicipio";

	var url = "php/catastro.php?end_point=" + end_point;

	url = url + "Provincia=" + obtenProvincia(rc) + "&Municipio=";

	var nombre_municipio = "";

	var request = jQuery.ajax({
		url : url,
		async : false,
		type : 'GET',
		dataType : "xml"
	});

	request
			.done(function(response, textStatus, jqXHR) {

				var xmlDoc = response;
				var munis = xmlDoc.getElementsByTagName("municipiero")[0].getElementsByTagName["muni"];

				for (var i = 0; i < munis.length; i++) {
					var muni = munis[i].getElementsByTagName("locat")[0]
							.getElementsByTagName("cmc")[0].childNodes[0].nodeValue;
					if (muni == codigoMunicipio) {
						nombre_municipio = munis[i].getElementsByTagName("nm")[0].nodeValue;
					}
				}

			});

	return nombre_municipio;

}

function graficoPrecipitacionPorMesYAnio() {

	var tabla = obtenDatosPorAnio("PRECIPITACION", 3, "month", "M");

	if (typeof tabla != 'undefined') {
		var columnas = tabla.cols;
		var filas = tabla.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columnas.length; i++) {
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
	} else {
		document.getElementById('graficoPrecipitacionPorMesYAnio').innerHTML = "<p style=\"color:red;\">Error al recuperar los datos de precipitación de la estación meteorologica más cercana</p>";
	}
}

function graficoTemperaturasMediasDiurnas() {

	var tabla = obtenDatosPorAnio("TEMPMEDIA", 3, "day", "DDD");

	if (typeof tabla != 'undefined') {
		var columnas = tabla.cols;
		var filas = tabla.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columnas.length; i++) {
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
	} else {
		document.getElementById('graficoTemperaturaMediaDiurna').innerHTML = "<p  style=\"color:red;\">Error al recuperar los datos de temperatura de la estación meteorologica más cercana</p>";
	}

}

function graficoHorasDeSolDiarias() {

	var tabla = obtenDatosPorAnio("N", 3, "day", "DDD");

	if (typeof tabla != 'undefined') {

		var columnas = tabla.cols;
		var filas = tabla.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columnas.length; i++) {
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
	} else {
		document.getElementById('graficoHorasDeSolDiarias').innerHTML = "<p style=\"color:red;\">Error al recuperar los datos de horas de sol de la estación meteorologica más cercana</p>";
	}

}

function graficoRadiacionNetaDiaria() {

	var tabla = obtenDatosPorAnio("RADIACION", 3, "day", "DDD");
	if (typeof tabla != 'undefined') {

		var columnas = tabla.cols;
		var filas = tabla.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columnas.length; i++) {
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
	} else {
		document.getElementById('graficoRadiacionNetaDiaria').innerHTML = "<p style=\"color:red;\">Error al recuperar los datos de temperatura de la estación meteorologica más cercana</p>";
	}

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

function obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) {

	var datos;

	var url = "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud="
			+ document.getElementById("latitud").innerHTML + "&longitud="
			+ document.getElementById("longitud").innerHTML + "&medida="
			+ medida + "&numeroDeAnios=" + numeroDeAnios + "&intervalo="
			+ intervalo + "&formato=" + formato;

	var request = jQuery.ajax({
		crossDomain : true,
		async : false,
		url : url,
		type : 'GET',
		dataType : "json"
	});

	request.done(function(response, textStatus, jqXHR) {
		datos = response;
	});

	return datos;
}