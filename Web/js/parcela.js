/**
 * 
 */

var mapa;
var parcela = {};
var informacionPoligono;
var fixedData = false;
var tableee;

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

	var nationalCadastralReference = getNationalCadastreReference();

	var cadastralParcelFeature = getPublicParcelInfoByNationalCadastralReference(nationalCadastralReference);

	draw(cadastralParcelFeature);

	if (!fixedData) {
				 google.charts.load('current', {
		 'packages' : [ 'table', 'bar', 'corechart', 'geochart' ]
		 });
		 document.getElementById("isGoogleChartsCorechartLoaded").innerHTML =
		 "true";
		//
		 google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
		// google.charts.setOnLoadCallback(graficoTemperaturasMediasDiurnas);
		// google.charts.setOnLoadCallback(graficoHorasDeSolDiarias);
		// google.charts.setOnLoadCallback(graficoRadiacionNetaDiaria);

	} else {
		document.getElementById("graficoPrecipitacionPorMesYAnio").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedRainChart.PNG\" >";
		document.getElementById("graficoTemperaturaMediaDiurna").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedTempChart.PNG\" >";
		document.getElementById("graficoHorasDeSolDiarias").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedSunChart.PNG\" >";
		document.getElementById("graficoRadiacionNetaDiaria").innerHTML = "<img style=\"width:100%;height:100%\" src=\"img/fixedRadiationChart.PNG\" >";
		openCultivo("All")
	}

}

function getNationalCadastreReference() {
	// El objeto window representa la ventana del navegador abierta
	// Location contiene la información de la URL de la ventana
	// Search devuelve desde la ? incluida, hacemos el substring(1) para quitar
	// la ?
	var query = window.location.search.substring(1);
	var nationalCadastreReference = "";

	if (query.length > 0) {
		// Si la query tiene algo
		var vars = query.split("&");
		for (var i = 0; i < vars.length; i++) {
			var pair = vars[i].split("=");
			// If first entry with this name
			switch (pair[0]) {
			case "cadastral_code":
				nationalCadastreReference = pair[1];
				break;
			case "nombre":
				document.getElementById('pagina').innerHTML = decodeURI(pair[1]);
				break;
			default:
				break;
			}
		}
	}

	return nationalCadastreReference;
}
function initMap(cadastralParcelFeature) {

	var parcelCenter = cadastralParcelFeature.properties.reference_point;

	var mapOptions = {
		center : {
			lat : parcelCenter.lat,
			lng : parcelCenter.lon
		},
		zoom : 16,
		mapTypeId : google.maps.MapTypeId.HYBRID
	}

	mapa = new google.maps.Map(document.getElementById('mapa'), mapOptions);

	// TODO: me extraña que esto no se pueda hacer más limpio
	var parcelEnvelopeCoordinates = cadastralParcelFeature.bbox;
	var parcelBounds = new google.maps.LatLngBounds({
		lng : parcelEnvelopeCoordinates[0],
		lat : parcelEnvelopeCoordinates[1]
	}, {
		lng : parcelEnvelopeCoordinates[2],
		lat : parcelEnvelopeCoordinates[3]
	})
	mapa.fitBounds(parcelBounds);

	var centerControlDiv = document.createElement('div');
	var centerControl = new CenterControl(centerControlDiv, mapa, parcelBounds);

	centerControlDiv.index = 1;
	mapa.controls[google.maps.ControlPosition.LEFT_CENTER]
			.push(centerControlDiv);

	mapa.data.addGeoJson(cadastralParcelFeature);

	mapa.data.setStyle({
		strokeColor : '#FF0000',
		strokeOpacity : 0.8,
		strokeWeight : 2,
		fillColor : '#FF0000',
		fillOpacity : 0.35
	});

}

/**
 * The CenterControl adds a control to the map that recenters the map on plot.
 * This constructor takes the control DIV as an argument.
 * 
 * @constructor
 */
function CenterControl(controlDiv, map, parcelBounds) {

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
		map.fitBounds(parcelBounds);
	});

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

function graficoPrecipitacionPorMesYAnio() {

	var tabla = tableee.avg_temperature;

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

function getPublicParcelInfoByNationalCadastralReference(
		nationalCadastralReference) {
	var cadastralParcelFeature;

	var url = 'php/django_server_wrapper.php/osc/cadastral/parcel?cadastral_code='
			+ nationalCadastralReference
			+ '&retrieve_public_info=True&retrieve_climate_info=True';

	var request = jQuery.ajax({
		url : url,
		type : 'GET',
		dataType : "json",
		async : false
	});

	request.done(function(response, textStatus, jqXHR) {
		cadastralParcelFeature = response.features[0];
	});
	
	cadastralParcelFeature.properties.climate_aggregations = addGoogleFormatedTables(cadastralParcelFeature.properties.climate_aggregations);

	return cadastralParcelFeature;

}

function draw(cadastralParcelFeature) {

	setValueInField(
			cadastralParcelFeature.properties.nationalCadastralReference, "rc");

	drawLocationCard(cadastralParcelFeature);

	drawCatastralCard(cadastralParcelFeature.properties.cadastralData);

	drawLastYearClimateAggregationsWidgetBar(cadastralParcelFeature.properties.climate_aggregations.last_year);
	
	drawRainfallAggregationsCard(cadastralParcelFeature.properties.climate_aggregations);

	drawCropDistributionCard(cadastralParcelFeature);

}

function drawLocationCard(cadastralParcelFeature) {

	initMap(cadastralParcelFeature);

	setValueInField(cadastralParcelFeature.properties.reference_point.lat,
			"latitud");
	setValueInField(cadastralParcelFeature.properties.reference_point.lon,
			"longitud");
	setValueInField(cadastralParcelFeature.properties.reference_point.elevation
			.toFixed(2)
			+ " m", "altitud");
	setValueInField(cadastralParcelFeature.properties.reference_point.elevation
			.toFixed(2)
			+ " m", "altitud_idea");

	var urlbusqueda = "location.href='cultivos.html?altitud="
			+ cadastralParcelFeature.properties.reference_point.elevation
					.toFixed() + "'";
	document.getElementById('cultivos_por_altitud').setAttribute('onclick',
			urlbusqueda);

}

function drawCatastralCard(parcelCadastralData) {

	setValueInField(parcelCadastralData.bico.bi.idbi.cn, "cn");
	setValueInField(parcelCadastralData.control.cucons, "cucons");
	setValueInField(parcelCadastralData.control.cucul, "cucul");
	setValueInField(parcelCadastralData.bico.lspr.spr.dspr.ccc
			+ parcelCadastralData.bico.lspr.spr.dspr.dcc, "ccc");
	setValueInField(parcelCadastralData.bico.lspr.spr.dspr.ip, "ip");
	setValueInField(parcelCadastralData.bico.lspr.spr.dspr.ssp, "ssp");
	setValueInField(parcelCadastralData.bico.lspr.spr.dspr.czc, "czc");
	setValueInField(parcelCadastralData.bico.bi.ldt, "direccion");

}

function drawLastYearClimateAggregationsWidgetBar(
		parcellast_yearClimate_aggregations) {
	setValueInField(
			parcellast_yearClimate_aggregations.sum_rainfall.toFixed(2),
			"precipitacion-widget");
	setValueInField(parcellast_yearClimate_aggregations.avg_temperature
			.toFixed(2), "temperatura-widget");
	// TODO: esto debe ser la suma de las horas de sol, no las horas medias de
	// sol, o al menos eso era antes
	setValueInField(parcellast_yearClimate_aggregations.avg_sun_hours
			.toFixed(2), "horasSol-widget");
	setValueInField(parcellast_yearClimate_aggregations.sum_radiation
			.toFixed(2), "radiacion-widget");
}

function drawRainfallAggregationsCard(parcelclimate_aggregations){
		//google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
}

function drawCropDistributionCard(cadastralParcelFeature) {
	if (cadastralParcelFeature.properties.cadastralData.bico.bi.dt.np == "SALAMANCA") {
		document.getElementById("fixed").style.display = 'inline';
		openCropDistribution("All");
	}
}

function setValueInField(value, field) {
	document.getElementById(field).innerHTML = typeof (value) != 'undefined' ? value
			: "";
}

function openCropDistribution(crop) {
	var i;
	var x = document.getElementsByClassName("city");
	for (i = 0; i < x.length; i++) {
		x[i].style.display = "none";
	}
	document.getElementById(crop).style.display = "block";
}

function addGoogleFormatedTables(parcelClimate_aggregations){
	
	var parcelClimate_aggregationsBy_month = parcelClimate_aggregations.by_month;
	var cols = [];
	cols["avg_temperature"] = [{label: "Mes", type: "string"}];
	cols["rainfall"] = [{label: "Mes", type: "string"}];
	cols["sun_hours"] = [{label: "Mes", type: "string"}];
	cols["radiation"] = [{label: "Mes", type: "string"}];
	
	var rows = [];
	rows["avg_temperature"] = [];
	rows["rainfall"] = [];
	rows["sun_hours"] = [];
	rows["radiation"] = [];
	
	rows["avg_temperature"].push(["Enero"]);
	rows["avg_temperature"].push(["Febrero"]);
	rows["avg_temperature"].push(["Marzo"]);
	rows["avg_temperature"].push(["Abril"]);
	rows["avg_temperature"].push(["Mayo"]);
	rows["avg_temperature"].push(["Junio"]);
	rows["avg_temperature"].push(["Julio"]);
	rows["avg_temperature"].push(["Agosto"]);
	rows["avg_temperature"].push(["Septiembre"]);
	rows["avg_temperature"].push(["Octubre"]);
	rows["avg_temperature"].push(["Noviembre"]);
	rows["avg_temperature"].push(["Diciembre"]);
	
	rows["rainfall"].push(["Enero"]);
	rows["rainfall"].push(["Febrero"]);
	rows["rainfall"].push(["Marzo"]);
	rows["rainfall"].push(["Abril"]);
	rows["rainfall"].push(["Mayo"]);
	rows["rainfall"].push(["Junio"]);
	rows["rainfall"].push(["Julio"]);
	rows["rainfall"].push(["Agosto"]);
	rows["rainfall"].push(["Septiembre"]);
	rows["rainfall"].push(["Octubre"]);
	rows["rainfall"].push(["Noviembre"]);
	rows["rainfall"].push(["Diciembre"]);
	
	rows["sun_hours"].push(["Enero"]);
	rows["sun_hours"].push(["Febrero"]);
	rows["sun_hours"].push(["Marzo"]);
	rows["sun_hours"].push(["Abril"]);
	rows["sun_hours"].push(["Mayo"]);
	rows["sun_hours"].push(["Junio"]);
	rows["sun_hours"].push(["Julio"]);
	rows["sun_hours"].push(["Agosto"]);
	rows["sun_hours"].push(["Septiembre"]);
	rows["sun_hours"].push(["Octubre"]);
	rows["sun_hours"].push(["Noviembre"]);
	rows["sun_hours"].push(["Diciembre"]);
	
	rows["radiation"].push(["Enero"]);
	rows["radiation"].push(["Febrero"]);
	rows["radiation"].push(["Marzo"]);
	rows["radiation"].push(["Abril"]);
	rows["radiation"].push(["Mayo"]);
	rows["radiation"].push(["Junio"]);
	rows["radiation"].push(["Julio"]);
	rows["radiation"].push(["Agosto"]);
	rows["radiation"].push(["Septiembre"]);
	rows["radiation"].push(["Octubre"]);
	rows["radiation"].push(["Noviembre"]);
	rows["radiation"].push(["Diciembre"]);
	
	for(i=0; i<parcelClimate_aggregationsBy_month.length; i++){
		var year = parcelClimate_aggregationsBy_month[i].year;
		var monthly_measures = parcelClimate_aggregationsBy_month[i].monthly_measures;
		for (j=0; j<monthly_measures.length; j++){
			var avg_temperature = monthly_measures[j].avg_temperature;
			var rainfall = monthly_measures[j].rainfall;
			var sun_hours = monthly_measures[j].sun_hours;
			var radiation = monthly_measures[j].radiation;
			var month = monthly_measures[j].month;
			rows["avg_temperature"][month-1].push(avg_temperature);
			rows["rainfall"][month-1].push(rainfall);
			rows["sun_hours"][month-1].push(sun_hours);
			rows["radiation"][month-1].push(radiation);
		}
		cols["avg_temperature"].push({label: year, type: "number"});
		cols["rainfall"].push({label: year, type: "number"});
		cols["sun_hours"].push({label: year, type: "number"});
		cols["radiation"].push({label: year, type: "number"});
	}
	
	var googleFormatedTable = [];
	googleFormatedTable["avg_temperature"] = {cols: cols["avg_temperature"], rows: rows["avg_temperature"]};
	googleFormatedTable["rainfall"] = {cols: cols["rainfall"], rows: rows["rainfall"]};
	googleFormatedTable["sun_hours"] = {cols: cols["sun_hours"], rows: rows["sun_hours"]};
	googleFormatedTable["radiation"] = {cols: cols["radiation"], rows: rows["radiation"]};
	parcelClimate_aggregations["googleFormatedTable"]=googleFormatedTable;
	tableee = googleFormatedTable;
	return parcelClimate_aggregations;
}