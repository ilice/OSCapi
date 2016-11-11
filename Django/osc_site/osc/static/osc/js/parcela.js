/**
 * 
 */

var myIndex = 0;

Date.prototype.getDOY = function() {
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((this - onejan) / 86400000) + 1;
}

/*
 * Los Google Charts no son responsive por lo que es necesario pintarlos de
 * nuevo cuado se produce un cambio de tamaño de la pantalla
 */
$(window).resize(function() {
	onBodyLoad();
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
				document.getElementById('bienvenidos').innerHTML = decodeURI(pair[1]);
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
	var parcelEnvelope = cadastralParcelFeature.bbox;
	var sw = {
		lat : parcelEnvelope.coordinates[0][1],
		lng : parcelEnvelope.coordinates[0][0]
	};
	var ne = {
		lat : parcelEnvelope.coordinates[1][1],
		lng : parcelEnvelope.coordinates[1][0]
	};
	var parcelBounds = new google.maps.LatLngBounds(sw, ne);
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

	try {

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
				colors : [ '#94E8B4', '#72BDA3', '#5E8C61', '#426A4D',
						'#4E6151', '#3B322C', '#7246F2' ],
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
			throw (new Error(
					"Error al recuperar los datos de precipitación de la estación meteorologica más cercana"));
		}

	} catch (error) {
		showErrorInCard(error, "RainfallCard");
	}

}

function drawChartOfTemperaturesByMonthAndYear(parcelclimate_aggregations) {
	try {
		var table = parcelclimate_aggregations.googleDailyFormatedTable.avg_temperature;

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
			throw (new Error(
					"Error al recuperar los datos de temperatura de la estación meteorologica más cercana"));
		}
	} catch (error) {
		showErrorInCard(error, "TemperatureCard");
	}

}

function drawChartOfDailySunHoursByMonthAndYear(parcelclimate_aggregations) {
	try {
		var table = parcelclimate_aggregations.googleDailyFormatedTable.sun_hours;

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
			throw (new Error(
					"Error al recuperar los datos de horas de sol de la estación meteorologica más cercana"));
		}
	} catch (error) {
		showErrorInCard(error, "SunHoursCard");
	}

}

function drawChartOfDailyNetRadiationByMonthAndYear(parcelclimate_aggregations) {
	try {
		var table = parcelclimate_aggregations.googleDailyFormatedTable.radiation;
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
			throw (new Error(
					"Error al recuperar los datos de radiación de la estación meteorologica más cercana"));
		}
	} catch (error) {
		showErrorInCard(error, "RadiationCard");
	}

}

function drawPublicParcelInfoByNationalCadastralReference(
		nationalCadastralReference) {
	var cadastralParcelFeature;

	var url = '/osc/cadastral/parcel?cadastral_code='
			+ nationalCadastralReference
			+ '&retrieve_public_info=True&retrieve_climate_info=True';

	var request = jQuery.ajax({
		url : url,
		type : 'GET',
		dataType : "json"
	});

	request
			.done(function(response, textStatus, jqXHR) {
				cadastralParcelFeature = response.features[0];
				cadastralParcelFeature.properties.climate_aggregations = addGoogleFormatedTablesOf(cadastralParcelFeature.properties.climate_aggregations);
				drawCardsAndWidgets(cadastralParcelFeature);
			});
}

function drawCardsAndWidgets(cadastralParcelFeature) {

	setValueInField(
			cadastralParcelFeature.properties.nationalCadastralReference, "rc");

	setValueInField(
			cadastralParcelFeature.properties.nationalCadastralReference, "rc_smallBar");
	
	drawAlternatives(cadastralParcelFeature);

	drawLocationCard(cadastralParcelFeature);

	drawCatastralCard(cadastralParcelFeature.properties.cadastralData);

	drawLastYearClimateAggregationsWidgetBar(cadastralParcelFeature.properties.climate_aggregations.last_year);

	drawRainfallAggregationsCard(cadastralParcelFeature.properties);

	drawTemperatureAggregationsCard(cadastralParcelFeature.properties);

	drawSunHoursAggregationsCard(cadastralParcelFeature.properties);

	drawRadiationAggregationsCard(cadastralParcelFeature.properties);

	drawCropDistributionCard(cadastralParcelFeature);

}

function drawAlternatives(cadastralParcelFeatures){

    var queries = [];

	if(!(cadastralParcelFeatures.properties.elevation === undefined)){
        var altitude = cadastralParcelFeatures.properties.elevation.toFixed();
        var altitudeQuery = createQueryForTypeAndValue("altitude", altitude);
        queries.push(altitudeQuery);
	}

    if(!(cadastralParcelFeatures.properties.climate_aggregations === undefined)){
        var plotMinTemperature = cadastralParcelFeatures.properties.climate_aggregations.last_year.min_temperature.toFixed();
        var plotMaxTemperature = cadastralParcelFeatures.properties.climate_aggregations.last_year.max_temperature.toFixed();
        var temperatureQuery = createQueryForTypeAndRange("temperature", plotMinTemperature, plotMaxTemperature);
        queries.push(temperatureQuery);

        var plotYearlyRainfall = cadastralParcelFeatures.properties.climate_aggregations.last_year.sum_rainfall.toFixed();
        var rainfallQuery = createQueryForTypeAndValue("rainfall", plotYearlyRainfall);
        queries.push(rainfallQuery);

        var plotYearlySunHours = cadastralParcelFeatures.properties.climate_aggregations.last_year.sum_sun_hours.toFixed();
        var sunHoursQuery = createQueryForTypeAndValue("sunHours", plotYearlySunHours);
        queries.push(sunHoursQuery);
    }

    if(!(cadastralParcelFeatures.properties.reference_point === undefined)){
        var plotLatitude = cadastralParcelFeatures.properties.reference_point.lat.toFixed();
        var latitudeQuery = createQueryForTypeAndValue("latitude", plotLatitude);
        queries.push(latitudeQuery);
    }

    if(!(cadastralParcelFeatures.properties.soil_profile === undefined)){
        var plotpH = cadastralParcelFeatures.properties.soil_profile.pH;
        var pHQuery = createQueryForTypeAndValue("ph", plotpH);
        queries.push(pHQuery);
    }




	var numeroCultivosACargar = 100;

	var query = aggregateQueries(queries);

	var data = {
		size : numeroCultivosACargar,
		query

	};

	var url = "/osc/crops/elastic/search/";

	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			data : JSON.stringify(data),
			type : 'POST',
			dataType : "json"
		});

	request.done(function (response, textStatus, jqXHR) {
		if (response.status == "SUCCESS") {
		
		var crops = response.result.crops;
		
		var rowIndex = 0;
		
		for (cropNumber in crops) {
			var crop = crops[cropNumber]._source;
			
			var id = crops[cropNumber]._id;
			
			var socialImpact = (Math.random() * 100).toFixed();
			var economicImpact = (Math.random() * 100).toFixed();
			var environmentalImpact = (Math.random() * 100).toFixed();
			
			
			var contenido = ''
			+ '<div class="w3-row mySlides">'
			+ '	<div class="w3-third">'
			+ '     <h4>' + crop["Nombres Comunes"] + ' <span class="w3-small">('+ crop["Nombre Científico"] + ')</span></h4>'
			+ '		<h6>Impacto</h6>'
			+ '		Social <i class="fa fa-group"></i>'
			+ '		<div class="w3-progress-container">'
			+ '			<div class="w3-progressbar w3-orange" style="width: '+socialImpact+'%">'
			+ '				<div class="w3-center w3-text-white">'+socialImpact+'%</div>'
			+ '			</div>'
			+ '		</div>'
			+ ''
			+ ''
			+ '		Económico <i class="fa fa fa-money"></i>'
			+ '		<div class="w3-progress-container">'
			+ '			<div class="w3-progressbar w3-blue" style="width: '+economicImpact+'%">'
			+ '				<div class="w3-center w3-text-white">'+economicImpact+'%</div>'
			+ '			</div>'
			+ '		</div>'
			+ ''
			+ ''
			+ '		Medioambiental <i class="fa fa-leaf"></i>'
			+ '		<div class="w3-progress-container">'
			+ '			<div class="w3-progressbar w3-green" style="width: '+environmentalImpact+'%">'
			+ '				<div class="w3-center w3-text-white">'+environmentalImpact+'%</div>'
			+ '			</div>'
			+ '		</div>'
			+ ''
			+ '		<button'
			+ '			class="w3-btn w3-margin w3-dark-grey w3-right w3-ripple w3-small"'
			+ '			onclick="document.getElementById(\'ReportInfo\').style.display=\'block\'">'
			+ '			Obtener informe <i class="fa fa-file-text"></i>'
			+ '		</button>'
			+ ''
			+ '	</div>'
			+ '	<div class="w3-twothird">'
			+ '			<img class="w3-right" onclick="document.getElementById(\'' + id + '_modal\').style.display=\'block\'" src="/static/osc/img/cultivos/' + crop.Foto + '" style="width: 70%">'
			+ '	</div>'
			+ '</div>' ;
				
				
				

			var modal = '<div id="' + id + '_modal" class="w3-modal">' +
				' <div class="w3-modal-content">' +
				'<div class="w3-container">' +
				'<div class="w3-row w3-right">' +
				' <div class="w3-col w3-right">' +
				'<a href="/osc/cultivo?cultivo_id=' + id + '" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-large w3-margin-right"><i class="fa fa-binoculars"></i></a>' +
				'<a href="#" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xlarge" onclick="document.getElementById(\'' + id + '_modal\').style.display=\'none\'"><i class="fa fa-remove"></i></a>' +
				'</div>' +
				'</div>' +
				'<table class="w3-table w3-striped w3-bordered w3-border w3-hoverable w3-white">' +
				'<tr class="w3-grey w3-text-light-grey"><th></th><th>' + crop["Nombres Comunes"] + ' ('+ crop["Nombre Científico"] + ')</th></tr>' +
				'<tr><td>Origen</td><td>' +crop["Origen"] + '</td></tr>' +
				'<tr><td>Distribución</td><td>' + crop["Distribución"] + '</td></tr>' +
				'<tr><td>Adaptación</td><td>' + crop["Adaptación"] + '</td></tr>' +
				'<tr><td>Ciclo vegetativo</td><td>' + crop["Ciclo vegetativo"] + '</td></tr>' +
				'<tr><td>Tipo Fotosintético</td><td>' + crop["Tipo Fotosintético"] + '</td></tr>' +
				'<tr><td>Fotoperíodo</td><td>' + crop["Fotoperíodo"] + '</td></tr>' +
				'<tr><td>Altitud</td><td>' + crop["Altitud"] + '</td></tr>' +
				'<tr><td>Precipitación</td><td>' + crop["Precipitación"] + '</td></tr>' +
				'<tr><td>Humedad ambiental</td><td>' + crop["Humedad ambiental"] + '</td></tr>' +
				'<tr><td>Temperatura</td><td>' + crop["Temperatura"] + '</td></tr>' +
				'<tr><td>Luz</td><td>' + crop["Luz"] + '</td></tr>' +
				'<tr><td>Textura de suelo</td><td>' + crop["Textura de suelo"] + '</td></tr>' +
				'<tr><td>Profundidad de suelo</td><td>' + crop["Profundidad de suelo"] + '</td></tr>' +
				'<tr><td>Salinidad</td><td>' + crop["Salinidad"] + '</td></tr>' +
				'<tr><td>pH</td><td>' + crop["pH"] + '</td></tr>' +
				'<tr><td>Drenaje</td><td>' + crop["Drenaje"] + '</td></tr>' +
				'<tr><td>Otros</td><td>' + crop["Otros"] + '</td></tr>' +
				'</table>' +
				'</div>' +
				'</div>' +
				'</div>';

			document.getElementById('alternativesContainer').innerHTML += contenido;
			document.getElementById('AlternativesCard').innerHTML += modal;


		}
		carousel("mySlides");
		}
	});

	
	
	
}

function drawLocationCard(cadastralParcelFeature) {
	try{

	initMap(cadastralParcelFeature);

	setValueInField(cadastralParcelFeature.properties.reference_point.lat,
			"latitud");
	setValueInField(cadastralParcelFeature.properties.reference_point.lon,
			"longitud");
	setValueInField(cadastralParcelFeature.properties.elevation.toFixed(2)
			+ " m", "altitud");
	setValueInField(cadastralParcelFeature.properties.elevation.toFixed(2)
			+ " m", "altitud_idea");

	var urlbusqueda = "location.href='/osc/cultivos?altitud="
			+ cadastralParcelFeature.properties.elevation.toFixed() + "'";
	document.getElementById('cultivos_por_altitud').setAttribute('onclick',
			urlbusqueda);
	}catch(error){
		showErrorInCard(error, "LocationCard");
	}

}

function drawCatastralCard(parcelCadastralData) {
	try{
	if (typeof (parcelCadastralData.bico) != 'undefined') {
		setValueInField(parcelCadastralData.bico.bi.idbi.cn, "cn");
		setValueInField(parcelCadastralData.control.cucons, "cucons");
		setValueInField(parcelCadastralData.control.cucul, "cucul");
		var subparcels = parcelCadastralData.bico.lspr.spr;
		for (subparcel in subparcels) {
			document.getElementById("cropTypeTable").innerHTML += '<td><i>'
					+ subparcels[subparcel].dspr.ccc
					+ subparcels[subparcel].dspr.dcc + '</i></td></tr>';

			document.getElementById("productionLevelTable").innerHTML += '<tr><td><i>'
					+ subparcels[subparcel].dspr.ip
					+ '</i> intensidad productiva</td></tr>';

			document.getElementById("cropAreaTable").innerHTML += '<tr><td>'
					+ subparcels[subparcel].dspr.ssp
					+ ' </span> m<sup>2</sup></i></td>	</tr>';

		}
		setValueInField(parcelCadastralData.bico.bi.ldt, "direccion");
	} else {
		
		throw (new Error( "Error en los datos del catastro. Contacte con nosotros."));
	}
	}catch(error){
		showErrorInCard(error, "CatastralCard");
	}

}

function drawLastYearClimateAggregationsWidgetBar(
		parcellast_yearClimate_aggregations) {
	setValueInField(
			parcellast_yearClimate_aggregations.sum_rainfall.toFixed(2),
			"precipitacion-widget");
	setValueInField(parcellast_yearClimate_aggregations.avg_temperature
			.toFixed(2), "temperatura-widget");
	setValueInField(parcellast_yearClimate_aggregations.sum_sun_hours
			.toFixed(2), "horasSol-widget");
	setValueInField(parcellast_yearClimate_aggregations.sum_radiation
			.toFixed(2), "radiacion-widget");
}

function drawRainfallAggregationsCard(parcelPorperties) {

	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelPorperties.climate_aggregations;

		google.charts.setOnLoadCallback(function() {
			drawChartOfRainfallByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelPorperties.closest_station.ESTACION + " a "
				+ parcelPorperties.closest_station.distance_to_parcel.toFixed()
				+ " km de distancia  (lineal)", "estacionLluvia");

		setValueInField(parcelclimate_aggregations.last_year.rainy_days,
				"diasDeLluvia");
		setValueInField(parcelclimate_aggregations.last_year.sum_rainfall
				.toFixed(2), "pecipitacionacumulada");
	} catch (error) {
		showErrorInCard(error, "RainfallCard");
	}
}

function drawTemperatureAggregationsCard(parcelPorperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelPorperties.climate_aggregations;

		google.charts.setOnLoadCallback(function() {
			drawChartOfTemperaturesByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelPorperties.closest_station.ESTACION + " a "
				+ parcelPorperties.closest_station.distance_to_parcel.toFixed()
				+ " km de distancia  (lineal)", "estacionTemperatura");

		setValueInField(parcelclimate_aggregations.last_year.max_temperature
				.toFixed(2), "maximaTemperaturaDiurna");
		setValueInField(parcelclimate_aggregations.last_year.min_temperature
				.toFixed(2), "minimaTemperaturaDiurna");
		setValueInField(parcelclimate_aggregations.last_year.avg_temperature
				.toFixed(2), "mediaTemperaturaDiurna");
	} catch (error) {
		showErrorInCard(error, "TemperatureCard");
	}
}

function drawSunHoursAggregationsCard(parcelPorperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelPorperties.climate_aggregations;

		google.charts.setOnLoadCallback(function() {
			drawChartOfDailySunHoursByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelPorperties.closest_station.ESTACION + " a "
				+ parcelPorperties.closest_station.distance_to_parcel.toFixed()
				+ " km de distancia  (lineal)", "estacionSol");

		setValueInField(parcelclimate_aggregations.last_year.avg_sun_hours
				.toFixed(2), "mediaHorasSolDiarias");
		setValueInField(parcelclimate_aggregations.last_year.max_sun_hours
				.toFixed(2), "maximasHorasSolDiarias");
		setValueInField(parcelclimate_aggregations.last_year.sum_sun_hours,
				"horasSolAcumuladas");
	} catch (error) {
		showErrorInCard(error, "TemperatureCard");
	}
}

function drawRadiationAggregationsCard(parcelPorperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelPorperties.climate_aggregations;

		google.charts
				.setOnLoadCallback(function() {
					drawChartOfDailyNetRadiationByMonthAndYear(parcelclimate_aggregations)
				});

		setValueInField(parcelPorperties.closest_station.ESTACION + " a "
				+ parcelPorperties.closest_station.distance_to_parcel.toFixed()
				+ " km de distancia  (lineal)", "estacionRadiacion");

		setValueInField(parcelclimate_aggregations.last_year.max_radiation
				.toFixed(2), "maximoRadiacionNetaDiaria");
		setValueInField(parcelclimate_aggregations.last_year.avg_radiation
				.toFixed(2), "mediaRadiacionNetaDiaria");
		setValueInField(parcelclimate_aggregations.last_year.sum_radiation
				.toFixed(2), "acumuladoRadiacionNetaDiaria");
	} catch (error) {
		showErrorInCard(error, "RadiationCard");
	}
}

function drawCropDistributionCard(cadastralParcelFeature) {
	try {
		if (cadastralParcelFeature.properties.cadastralData.bico.bi.dt.np == "SALAMANCA") {
			document.getElementById("fixed").style.display = 'inline';
			openCropDistribution("All");
		}
	} catch (error) {
		showErrorInCard(error, "CropDistributionCard");
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

	try {
		var yearly_measures_by_month = parcelClimate_aggregations.by_month;
		var yearly_measures_by_day = parcelClimate_aggregations.by_day;

		var colsByMeasure = [];
		var rowsByMeasure = [];

		var colsByDailyMeasure = [];
		var rowsByDailyMeasure = [];

		var days = [];
		for (var i = 1; i < 367; i++) {
			days.push(i + "");
		}

		var monthNames = [ "Enero", "Febrero", "Marzo", "Abril", "Mayo",
				"Junio", "Julio", "Agosto", "Septiembre", "Octubre",
				"Noviembre", "Diciembre" ];

		for (i = 0; i < yearly_measures_by_month.length; i++) {
			var year = yearly_measures_by_month[i].year;
			var monthly_measures = yearly_measures_by_month[i].monthly_measures;
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
								rowsByMeasure[measure]
										.push([ monthNames[monthName] ]);
							}
						}
						rowsByMeasure[measure][month - 1]
								.push(measures[measure]);
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

		for (i = 0; i < yearly_measures_by_day.length; i++) {
			var year = yearly_measures_by_day[i].year;
			var daily_measures = yearly_measures_by_day[i].daily_measures;
			for (j = 0; j < daily_measures.length; j++) {
				var measures = daily_measures[j];
				var day = (new Date(measures.day.split("-")[1] + "-"
						+ measures.day.split("-")[0] + "-"
						+ measures.day.split("-")[2])).getDOY();
				for ( var measure in measures) {
					if (measure != 'Day') {
						if (!colsByDailyMeasure.hasOwnProperty(measure)) {
							colsByDailyMeasure[measure] = [ {
								label : "Día",
								type : "string"
							} ];
						}
						if (!rowsByDailyMeasure.hasOwnProperty(measure)) {
							rowsByDailyMeasure[measure] = [];
							for (dayOfYear in days) {
								rowsByDailyMeasure[measure]
										.push([ days[dayOfYear] ]);
							}
						}
						rowsByDailyMeasure[measure][day - 1]
								.push(measures[measure]);
					}
				}
			}
			for ( var measure in colsByDailyMeasure) {
				colsByDailyMeasure[measure].push({
					label : year,
					type : "number"
				});
				for ( var day in rowsByDailyMeasure[measure]) {
					if (rowsByDailyMeasure[measure][day].length < colsByDailyMeasure[measure].length) {
						rowsByDailyMeasure[measure][day].push(null);
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

		var googleDailyFormatedTable = [];
		for ( var measureType in colsByDailyMeasure) {
			googleDailyFormatedTable[measureType] = {
				cols : colsByDailyMeasure[measureType],
				rows : rowsByDailyMeasure[measureType]
			}
		}

		parcelClimate_aggregations["googleFormatedTable"] = googleFormatedTable;
		parcelClimate_aggregations["googleDailyFormatedTable"] = googleDailyFormatedTable;
	} catch (error) {
		throw error;
	}

	return parcelClimate_aggregations;

}

function loadGoogleChartsCorechart() {
	try {
		if (document.getElementById("isGoogleChartsCorechartLoaded").innerHTML != "true") {
			google.charts.load('current', {
				'packages' : [ 'table', 'bar', 'corechart', 'geochart' ]
			});
			document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";
		}
	} catch (error) {
		throw error;
	}
}

function showErrorInCard(error, card) {
	document.getElementById(card + 'ErrorBadge').style.display = 'block';
	document.getElementById(card + 'ErrorText').innerHTML += "<p>"
			+ error.message + "</p>";
	
	document.getElementById('ErrorBadge').style.display = 'block';
	document.getElementById('ErrorText').innerHTML += "<p>"
			+ error.message + "</p>";
	
}

function carousel(seats) {
	var i;
	var x = document
			.getElementsByClassName(seats);
	for (i = 0; i < x.length; i++) {
		x[i].style.display = "none";
	}
	myIndex++;
	if (myIndex > x.length) {
		myIndex = 1
	}
	x[myIndex - 1].style.display = "block";
	setTimeout(carousel, 4000, seats); // Change image every 2 seconds
}


function createQueryForTypeAndValue(type, value){
    var query;
    var minType = type + ".min";
    var maxType = type + ".max";
    //Dis Max Query: A query that generates the union of documents produced by its subqueries,
    //and that scores each document with the maximum score for that document as
    //produced by any subquery, plus a tie breaking increment for any additional
    //matching subqueries.
	if (encodeURIComponent(value) != "undefined"){

        var subqueryValueBetweenMinAndMaxValueForCrop = {
            bool: {
                must: [
                 {
                    range: {
                       [minType] : {
                          lte: value
                       }
                    }
                 },
                 {
                    range: {
                       [maxType] : {
                          gte: value
                       }
                    }
                 }
                ]
            }
        };

        var subqueryValueGreaterThanMinWithoutMaxValueForCrop = {
            bool: {
                must: {
                    range: {
                        [minType]: {
                           lte: value
                        }
                    }
                },
                must_not: {
                    exists: {
                        field: maxType
                    }
                }
            }
        };

        var subqueryValueSmallerThanMaxWithoutMinValueForCrop = {
            bool: {
                must: {
                    range: {
                        [maxType]: {
                           gte: value
                        }
                    }
                },
                must_not: {
                    exists: {
                        field: minType
                    }
                }
            }
        };

        var subqueryCropsWithoutValueRanges = {
            bool: {
                must_not: {
                    exists: {
                        field: maxType
                    }
                },
                must_not: {
                    exists: {
                        field: minType
                    }
                }
            }
        };

		query = {
            dis_max: {
                tie_breaker: 0.7,
                boost: 1.2,
                queries: [
                    subqueryValueBetweenMinAndMaxValueForCrop,
                    subqueryValueGreaterThanMinWithoutMaxValueForCrop,
                    subqueryValueSmallerThanMaxWithoutMinValueForCrop,
                    subqueryCropsWithoutValueRanges
                ]
            }
         };
	}

	return query;
}

function createQueryForTypeAndRange(type, minValue, maxValue){
    var query;
    var minType = type + ".min";
    var maxType = type + ".max";
    //Dis Max Query: A query that generates the union of documents produced by its subqueries,
    //and that scores each document with the maximum score for that document as
    //produced by any subquery, plus a tie breaking increment for any additional
    //matching subqueries.
	if (encodeURIComponent(minValue) != "undefined" && encodeURIComponent(maxValue) != "undefined"){

        var subqueryValueBetweenMinAndMaxValueForCrop = {
            bool: {
                must: [
                 {
                    range: {
                       [minType] : {
                          lte: minValue
                       }
                    }
                 },
                 {
                    range: {
                       [maxType] : {
                          gte: maxValue
                       }
                    }
                 }
                ]
            }
        };

        var subqueryValueGreaterThanMinWithoutMaxValueForCrop = {
            bool: {
                must: {
                    range: {
                        [minType]: {
                           lte: minValue
                        }
                    }
                },
                must_not: {
                    exists: {
                        field: maxType
                    }
                }
            }
        };

        var subqueryValueSmallerThanMaxWithoutMinValueForCrop = {
            bool: {
                must: {
                    range: {
                        [maxType]: {
                           gte: maxValue
                        }
                    }
                },
                must_not: {
                    exists: {
                        field: minType
                    }
                }
            }
        };

        var subqueryCropsWithoutValueRanges = {
            bool: {
                must_not: {
                    exists: {
                        field: maxType
                    }
                },
                must_not: {
                    exists: {
                        field: minType
                    }
                }
            }
        };

		query = {
            dis_max: {
                tie_breaker: 0.7,
                boost: 1.2,
                queries: [
                    subqueryValueBetweenMinAndMaxValueForCrop,
                    subqueryValueGreaterThanMinWithoutMaxValueForCrop,
                    subqueryValueSmallerThanMaxWithoutMinValueForCrop,
                    subqueryCropsWithoutValueRanges
                ]
            }
         };
	}

	return query;
}

function aggregateQueries(queries){

    var query = {
        bool: {
            must: queries
        }
    };

    return query;
}

function onSignIn(googleUser) {

  var profile = googleUser.getBasicProfile();
  var profile_image_url = profile.getImageUrl();

  drawUserMenu(profile_image_url, 'google');

  document.getElementById('esMiParcela').style.display = 'none';
  document.getElementById('esMiParcelaButton').disabled = true;
  document.getElementById('meInteresaEstaParcelaButton').disabled = true;


}

function logout(socialNetwork){
    if(socialNetwork == 'google'){
        signOut();
    }else if (socialNetwork == 'facebook'){
        FB.logout(function(response) {
       // Person is now logged out
       statusChangeCallback(response);
    });
    }

    document.getElementById('userMenu').parentNode.removeChild(document.getElementById('userMenu'));
    document.getElementById('avatar').src = "/static/osc/img/avatar.PNG";
    document.getElementById('esMiParcelaButton').disabled = false;
    document.getElementById('meInteresaEstaParcelaButton').disabled = false;
}


function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
}


// Dibuja el mapa en la barra lateral
function drawRegionsMap() {

	var latitud = document.getElementById("latitud").innerHTML;
	var longitud = document.getElementById("longitud").innerHTML;

	var data = google.visualization.arrayToDataTable([
				['latitude', 'longitude', 'temperatura'],
				[Number(latitud), Number(longitud), 25]
			]);

	var options = {
		region : 'ES',
		displayMode : 'markers',
		colorAxis : {
			colors : ['blue']
		},
		resolution : 'provinces'
	};

	var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

	chart.draw(data, options);
}

// Script to open and close sidenav
function w3_open() {

	if(document.getElementById("mySidenav").innerHTML == ""){
		cargaBarraLateral();
	}
	document.getElementById("mySidenav").style.display = "block";
	document.getElementById("myOverlay").style.display = "block";
	if(document.getElementById("latitud")){


	if (document.getElementById("isGoogleChartsCorechartLoaded").innerHTML == "false") {
		google.charts.load('current', {
			'packages' : ['corechart']
		});
		document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";
	}
	google.charts.setOnLoadCallback(drawRegionsMap);
	}

}

function w3_close() {
	document.getElementById("mySidenav").style.display = "none";
	document.getElementById("myOverlay").style.display = "none";
}

// -------------Facebook code---------------

// This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      testAPI();
    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      //document.getElementById('status').innerHTML = 'Please log ' +
      //  'into this app.';
    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
      //document.getElementById('status').innerHTML = 'Please log ' +
      //  'into Facebook.';
    }
  }

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }

  window.fbAsyncInit = function() {
  FB.init({
    appId      : '1620993304869407',
    cookie     : true,  // enable cookies to allow the server to access
                        // the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v2.5' // use graph api version 2.5
  });

  // Now that we've initialized the JavaScript SDK, we call
  // FB.getLoginStatus().  This function gets the state of the
  // person visiting this page and can return one of three states to
  // the callback you provide.  They can be:
  //
  // 1. Logged into your app ('connected')
  // 2. Logged into Facebook, but not your app ('not_authorized')
  // 3. Not logged into Facebook and can't tell if they are logged into
  //    your app or not.
  //
  // These three cases are handled in the callback function.

  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });

  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
      //document.getElementById('status').innerHTML =
      //  'Thanks for logging in, ' + response.name + '!';

       profile_image_url = 'http://graph.facebook.com/' + response.id + '/picture';

       drawUserMenu(profile_image_url, 'facebook');
    });



  }
function login(){
  FB.login(function(response) {
    if (response.authResponse) {
     console.log('Welcome!  Fetching your information.... ');
     FB.api('/me', function(response) {
       console.log('Successful login for: ' + response.name);
      //document.getElementById('status').innerHTML =
      //  'Thanks for logging in, ' + response.name + '!';

       profile_image_url = 'http://graph.facebook.com/' + response.id + '/picture';

       drawUserMenu(profile_image_url, 'facebook');

       document.getElementById('esMiParcela').style.display = 'none';
       document.getElementById('esMiParcelaButton').disabled = true;
       document.getElementById('meInteresaEstaParcelaButton').disabled = true;
     });
    } else {
     console.log('User cancelled login or did not fully authorize.');
    }
},{scope: 'public_profile,email'});
}

function drawUserMenu(profile_image_url, socialNetwork){

  var userMenu = document.createElement('div');
  userMenu.setAttribute('id', 'userMenu');

  var avatar_dropdown_hover = document.createElement('div');
  avatar_dropdown_hover.setAttribute('class', "w3-dropdown-hover");
  avatar_dropdown_hover.setAttribute('style', 'background-color: transparent');
  userMenu.appendChild(avatar_dropdown_hover);

  var avatar = document.createElement('img');
  avatar.setAttribute('src', profile_image_url);
  avatar.setAttribute('class', "w3-circle");
  avatar.setAttribute('alt', 'User avatar');
  avatar.setAttribute('style', 'width:100%;max-width:36px')
  avatar_dropdown_hover.appendChild(avatar);

  var avatar_dropdown_content = document.createElement('div');
  avatar_dropdown_content.setAttribute('class', 'w3-dropdown-content w3-card-4 w3-margin-right');
  avatar_dropdown_content.setAttribute('style', 'right:0');
  avatar_dropdown_hover.appendChild(avatar_dropdown_content);

  var logout_row = document.createElement('a');
  logout_row.setAttribute('href', 'javascript:void(0)');
  logout_row.setAttribute('onclick', 'logout("'+socialNetwork+'")');
  avatar_dropdown_content.appendChild(logout_row);

  var logout_icon = document.createElement('i');
  logout_icon.setAttribute('class', 'fa fa-sign-out')
  logout_row.appendChild(logout_icon);
  logout_row.appendChild(document.createTextNode(' Cerrar sesión'));

  document.getElementById('userMenuItem').appendChild(userMenu);

  document.getElementById("avatar").src = profile_image_url;
}

function openForm(relation){
    if (relation == 'esMiParcela'){
        document.getElementById('objetiveDescription').innerHTML = 'Registra tu parcela';
        document.getElementById('esMiParcela').style.display = 'block';
    }else {
        document.getElementById('objetiveDescription').innerHTML = 'Obten información sobre la parcela';
        document.getElementById('esMiParcela').style.display = 'block';

    }
}