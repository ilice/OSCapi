/**
 * 
 */

/*
 * Los Google Charts no son responsive por lo que es necesario pintarlos de
 * nuevo cuado se produce un cambio de tamaño de la pantalla
 */
$(window).resize(function() {
	onBodyLoad();
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

function onBodyLoad() {

	var nationalCadastralReference = getNationalCadastreReference();

	drawPublicParcelInfoByNationalCadastralReference(nationalCadastralReference);

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

	var mapa = new google.maps.Map(document.getElementById('mapa'), mapOptions);

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

function drawChartOfRainfallByMonthAndYear(parcelclimate_aggregations) {

	var table = parcelclimate_aggregations.googleFormatedTable.rainfall;

	if (typeof table != 'undefined') {
		var columns = table.cols;
		var rows = table.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columns.length; i++) {
			dt.addColumn(columns[i].type, columns[i].label);
		}
		dt.addRows(rows);

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

function drawChartOfTemperaturesByMonthAndYear(parcelclimate_aggregations) {

	var table = parcelclimate_aggregations.googleFormatedTable.avg_temperature;

	if (typeof table != 'undefined') {
		var columns = table.cols;
		var rows = table.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columns.length; i++) {
			dt.addColumn(columns[i].type, columns[i].label);
		}
		dt.addRows(rows);

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

function drawChartOfDailySunHoursByMonthAndYear(parcelclimate_aggregations) {

	var table = parcelclimate_aggregations.googleFormatedTable.sun_hours;

	if (typeof table != 'undefined') {

		var columns = table.cols;
		var rows = table.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columns.length; i++) {
			dt.addColumn(columns[i].type, columns[i].label);
		}
		dt.addRows(rows);

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

function drawChartOfDailyNetRadiationByMonthAndYear(parcelclimate_aggregations) {

	var table = parcelclimate_aggregations.googleFormatedTable.radiation;
	if (typeof table != 'undefined') {

		var columns = table.cols;
		var rows = table.rows;

		var dt = new google.visualization.DataTable();

		for (var i = 0; i < columns.length; i++) {
			dt.addColumn(columns[i].type, columns[i].label);
		}
		dt.addRows(rows);

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

function drawPublicParcelInfoByNationalCadastralReference(
		nationalCadastralReference) {
	var cadastralParcelFeature;

	var url = 'php/django_server_wrapper.php/osc/cadastral/parcel?cadastral_code='
			+ nationalCadastralReference
			+ '&retrieve_public_info=True&retrieve_climate_info=True';

	var request = jQuery.ajax({
		url : url,
		type : 'GET',
		dataType : "json"
	});

	request.done(function(response, textStatus, jqXHR) {
		cadastralParcelFeature = response.features[0];
		cadastralParcelFeature.properties.climate_aggregations = addGoogleFormatedTablesOf(cadastralParcelFeature.properties.climate_aggregations);
		drawCardsAndWidgets(cadastralParcelFeature);
	});
}

function drawCardsAndWidgets(cadastralParcelFeature) {

	setValueInField(
			cadastralParcelFeature.properties.nationalCadastralReference, "rc");

	drawLocationCard(cadastralParcelFeature);

	drawCatastralCard(cadastralParcelFeature.properties.cadastralData);

	drawLastYearClimateAggregationsWidgetBar(cadastralParcelFeature.properties.climate_aggregations.last_year);

	drawRainfallAggregationsCard(cadastralParcelFeature.properties.climate_aggregations);

	drawTemperatureAggregationsCard(cadastralParcelFeature.properties.climate_aggregations);
	
	drawSunHoursAggregationsCard(cadastralParcelFeature.properties.climate_aggregations);
	
	drawRadiationAggregationsCard(cadastralParcelFeature.properties.climate_aggregations);
	
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

function drawRainfallAggregationsCard(parcelclimate_aggregations) {
	loadGoogleChartsCorechart();

	google.charts.setOnLoadCallback(function() {
		drawChartOfRainfallByMonthAndYear(parcelclimate_aggregations)
	});

	setValueInField(parcelclimate_aggregations.last_year.rainfall_days,
			"diasDeLluvia");
	setValueInField(parcelclimate_aggregations.last_year.sum_rainfall.toFixed(2),
			"pecipitacionacumulada");
}

function drawTemperatureAggregationsCard(parcelclimate_aggregations) {
	loadGoogleChartsCorechart();

	google.charts.setOnLoadCallback(function() {
		drawChartOfTemperaturesByMonthAndYear(parcelclimate_aggregations)
	});

	setValueInField(parcelclimate_aggregations.last_year.max_temperature.toFixed(2),
			"maximaTemperaturaDiurna");
	setValueInField(parcelclimate_aggregations.last_year.min_temperature.toFixed(2),
			"minimaTemperaturaDiurna");
	setValueInField(parcelclimate_aggregations.last_year.avg_temperature.toFixed(2),
			"mediaTemperaturaDiurna");
}

function drawSunHoursAggregationsCard(parcelclimate_aggregations) {
	loadGoogleChartsCorechart();

	google.charts.setOnLoadCallback(function() {
		drawChartOfDailySunHoursByMonthAndYear(parcelclimate_aggregations)
	});

	setValueInField(parcelclimate_aggregations.last_year.avg_sun_hours.toFixed(2),
			"mediaHorasSolDiarias");
	setValueInField(parcelclimate_aggregations.last_year.max_sun_hours.toFixed(2),
			"maximasHorasSolDiarias");
	setValueInField(parcelclimate_aggregations.last_year.sum_sun_hours,
			"horasSolAcumuladas");
}

function drawRadiationAggregationsCard(parcelclimate_aggregations) {
	loadGoogleChartsCorechart();

	google.charts.setOnLoadCallback(function() {
		drawChartOfDailyNetRadiationByMonthAndYear(parcelclimate_aggregations)
	});

	setValueInField(parcelclimate_aggregations.last_year.max_radiation.toFixed(2),
			"maximoRadiacionNetaDiaria");
	setValueInField(parcelclimate_aggregations.last_year.avg_radiation.toFixed(2),
			"mediaRadiacionNetaDiaria");
	setValueInField(parcelclimate_aggregations.last_year.sum_radiation.toFixed(2),
			"acumuladoRadiacionNetaDiaria");
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

function addGoogleFormatedTablesOf(parcelClimate_aggregations) {

	var yearly_measures = parcelClimate_aggregations.by_month;
	var colsByMeasure = [];
	var rowsByMeasure = [];
	var monthNames = [ "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
			"Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
			"Diciembre" ];

	for (i = 0; i < yearly_measures.length; i++) {
		var year = yearly_measures[i].year;
		var monthly_measures = yearly_measures[i].monthly_measures;
		for (j = 0; j < monthly_measures.length; j++) {
			var measures = monthly_measures[j];
			var month = measures.month;
			for ( var measure in measures) {
				if (measure != 'month') {
					if (!colsByMeasure.hasOwnProperty(measure)) {
						colsByMeasure[measure] = [ {
							label : "Mes",
							type : "string"
						} ];
					}
					if (!rowsByMeasure.hasOwnProperty(measure)) {
						rowsByMeasure[measure] = [];
						for (monthName in monthNames) {
							rowsByMeasure[measure].push([ monthNames[monthName] ]);
						}
					}
					rowsByMeasure[measure][month - 1].push(measures[measure]);
				}
			}
		}
		for ( var measure in colsByMeasure) {
			colsByMeasure[measure].push({
				label : year,
				type : "number"
			});
			for ( var month in rowsByMeasure[measure]) {
				if (rowsByMeasure[measure][month].length < colsByMeasure[measure].length) {
					rowsByMeasure[measure][month].push(null);
				}

			}
		}
	}

	var googleFormatedTable = [];
	for ( var measureType in colsByMeasure) {
		googleFormatedTable[measureType] = {
			cols : colsByMeasure[measureType],
			rows : rowsByMeasure[measureType]
		}
	}

	parcelClimate_aggregations["googleFormatedTable"] = googleFormatedTable;
	return parcelClimate_aggregations;
}

function loadGoogleChartsCorechart() {
	if (document.getElementById("isGoogleChartsCorechartLoaded").innerHTML != "true") {
		google.charts.load('current', {
			'packages' : [ 'table', 'bar', 'corechart', 'geochart' ]
		});
		document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";
	}
}