/**
 * 
 */

var myIndex = 0;

Date.prototype.getDOY = function () {
	var onejan = new Date(this.getFullYear(), 0, 1);
	return Math.ceil((this - onejan) / 86400000) + 1;
}

/*
 * Los Google Charts no son responsive por lo que es necesario pintarlos de
 * nuevo cuado se produce un cambio de tamaño de la pantalla
 */
$(window).resize(function () {
	FB.getLoginStatus(function (response) {
		console.log('FB.getLoginStatus');
		statusChangeCallback(response);
	});
});

function drawPlotProfile(accessToken) {

	if (accessToken === undefined) {
		console.log('drawPlotProfile without user');
	} else {
		console.log('drawPlotProfile for user');
	}

	var nationalCadastralReference = getNationalCadastreReference();
	
	drawParcelInfoByNationalCadastralReference(nationalCadastralReference, accessToken);

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
	controlUI.addEventListener('click', function () {
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
				colors : ['#94E8B4', '#72BDA3', '#5E8C61', '#426A4D',
					'#4E6151', '#3B322C', '#7246F2'],
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
				colors : ['#7F0D0B', '#BF1411', '#400706'],
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
				colors : ['#BFA71F', '#7F6F15', '#FFDF2A'],
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
				colors : ['#BF480A', '#FF600D', '#E5570C'],
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

function drawParcelInfoByNationalCadastralReference(
	nationalCadastralReference, accessToken) {
	var cadastralParcelFeature = {};
	
	//TODO creo el accessToken que debe ir en el cuerpo y no en la url

	var url = '/osc/cadastral/parcel?cadastral_code='
		 + nationalCadastralReference
		 + '&retrieve_public_info=True&retrieve_climate_info=True&retrieve_soil_info=True&accessToken='
		 + (accessToken===undefined?'':accessToken);

	var request = jQuery.ajax({
			url : url,
			type : 'GET',
			dataType : "json"
		});

	request
	.done(function (response, textStatus, jqXHR) {
		if(response.error === undefined){
			cadastralParcelFeature = response.features[0];
			cadastralParcelFeature.properties.climate_aggregations = addGoogleFormatedTablesOf(cadastralParcelFeature.properties.climate_aggregations);
		}else{
			showError(new Error('Se ha producido un error al recuperar la información de la parcela.'));
		}
		cadastralParcelFeature.getProperty = getProperty;
		drawCardsAndWidgets(cadastralParcelFeature);
	});
}

function drawCardsAndWidgets(cadastralParcelFeature) {

	setValueInField(
		cadastralParcelFeature.getProperty('properties.nationalCadastralReference'), "rc");

	setValueInField(
		cadastralParcelFeature.getProperty('properties.nationalCadastralReference'), "rc_smallBar");
	
	drawCompletionParcelProfileBar(cadastralParcelFeature);

	drawAlternatives(cadastralParcelFeature);

	drawLocationCard(cadastralParcelFeature);

	drawCatastralCard(cadastralParcelFeature.getProperty('properties.cadastralData'));
	
	drawSoilCard(cadastralParcelFeature.getProperty('properties.closest_soil_measure'));

	drawLastYearClimateAggregationsWidgetBar(cadastralParcelFeature.getProperty('properties.climate_aggregations.last_year'));

	drawRainfallAggregationsCard(cadastralParcelFeature.getProperty('properties'));

	drawTemperatureAggregationsCard(cadastralParcelFeature.getProperty('properties'));

	drawSunHoursAggregationsCard(cadastralParcelFeature.getProperty('properties'));

	drawRadiationAggregationsCard(cadastralParcelFeature.getProperty('properties'));

	drawCropDistributionCard(cadastralParcelFeature);

}

function drawCompletionParcelProfileBar(cadastralParcelFeature){
	
	var parcelProfile = cadastralParcelFeature.getProperty('property.parcelProfile');	
	
	//TODO esto debe de mostrarse por la información que nos llega a pintar no por el access token 
	//if(parcelProfile === undefined){
	
	if(getCookie("accessToken") != ''){
		document.getElementById('completionParcelProfileBarCard').style.display = 'block';
		createProgressCircle('10');
	}else{
		document.getElementById('completionParcelProfileBarCard').style.display = 'none';
		
	}
		
}



function drawAlternatives(cadastralParcelFeatures) {

	var queries = [];

	if (!(cadastralParcelFeatures.getProperty('properties.elevation') === undefined)) {
		var altitude = cadastralParcelFeatures.getProperty('properties.elevation').toFixed();
		var altitudeQuery = createQueryForTypeAndValue("altitude", altitude);
		queries.push(altitudeQuery);
		
		var optimalAltitudeQuery = createQueryForTypeAndValue("optimal_altitude", altitude);
		queries.push(optimalAltitudeQuery);
	}

	if (!(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') === undefined)) {
		var plotMinTemperature = cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year.min_temperature').toFixed();
		var plotMaxTemperature = cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year.max_temperature').toFixed();
		var temperatureQuery = createQueryForTypeAndRange("temperature", plotMinTemperature, plotMaxTemperature);
		queries.push(temperatureQuery);
		
		var optimalTemperatureQuery = createQueryForTypeAndRange("optimal_temperature", plotMinTemperature, plotMaxTemperature);
		queries.push(optimalTemperatureQuery);

		var plotYearlyRainfall = cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year.sum_rainfall').toFixed();
		var rainfallQuery = createQueryForTypeAndValue("rainfall", plotYearlyRainfall);
		queries.push(rainfallQuery);
		
		var optimalrainfallQuery = createQueryForTypeAndValue("optimal_rainfall", plotYearlyRainfall);
		queries.push(optimalrainfallQuery);

		var plotYearlySunHours = cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year.sum_sun_hours').toFixed();
		var sunHoursQuery = createQueryForTypeAndValue("sunHours", plotYearlySunHours);
		queries.push(sunHoursQuery);
		
		var optimalSunHoursQuery = createQueryForTypeAndValue("optimal_sunHours", plotYearlySunHours);
		queries.push(optimalSunHoursQuery);
	}

	if (!(cadastralParcelFeatures.getProperty('properties.reference_point.lat') === undefined)) {
		var plotLatitude = cadastralParcelFeatures.getProperty('properties.reference_point.lat').toFixed();
		var latitudeQuery = createQueryForTypeAndValue("latitude", plotLatitude);
		queries.push(latitudeQuery);
	}

	if (!(cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_H2O') === undefined)) {
		var plotpH_inH2O = cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_H2O');
		var pH_in_H2OQuery = createQueryForTypeAndValue("ph", plotpH_inH2O);
		queries.push(pH_in_H2OQuery);
		
		var optimalpH_in_H2OQuery = createQueryForTypeAndValue("optimal_ph", plotpH_inH2O);
		queries.push(optimalpH_in_H2OQuery);
	}
	
	if (!(cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_CaCl2') === undefined)) {
		var plotpH_in_CaCl2 = cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_CaCl2');
		var pH_in_CaCl2Query = createQueryForTypeAndValue("ph", plotpH_in_CaCl2);
		queries.push(pH_in_CaCl2Query);
		
		var optimalpH_in_CaCl2Query = createQueryForTypeAndValue("optimal_ph", plotpH_in_CaCl2);
		queries.push(optimalpH_in_CaCl2Query);
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
				var score = crops[cropNumber]._score;
				
				addAlternativesTableRow(crop, score, cadastralParcelFeatures);

				var id = crops[cropNumber]._id;

				var socialImpact = (Math.random() * 100).toFixed();
				var economicImpact = (Math.random() * 100).toFixed();
				var environmentalImpact = (Math.random() * 100).toFixed();

				var contenido = ''
					 + '<div class="mySlides">'
					 + '	<div class="w3-row">'
					 + '		<div class="w3-third w3-padding-small">'
					 + '            <h4 style="text-transform: capitalize">'+ crop["Nombre"].toLowerCase() +'</h4>'
					 + '			<h6>Impacto</h6>'
					 + '			Social <i class="fa fa-group"></i>'
					 + '			<div class="w3-progress-container">'
					 + '				<div class="w3-progressbar w3-orange" style="width: ' + socialImpact + '%">'
					 + '					<div class="w3-center w3-text-white">' + socialImpact + '%</div>'
					 + '				</div>'
					 + '			</div>'
					 + ''
					 + ''
					 + '			Económico <i class="fa fa fa-money"></i>'
					 + '			<div class="w3-progress-container">'
					 + '				<div class="w3-progressbar w3-blue" style="width: ' + economicImpact + '%">'
					 + '					<div class="w3-center w3-text-white">' + economicImpact + '%</div>'
					 + '				</div>'
					 + '			</div>'
					 + ''
					 + ''
					 + '			Medioambiental <i class="fa fa-leaf"></i>'
					 + '			<div class="w3-progress-container">'
					 + '				<div class="w3-progressbar w3-green" style="width: ' + environmentalImpact + '%">'
					 + '					<div class="w3-center w3-text-white">' + environmentalImpact + '%</div>'
					 + '				</div>'
					 + '			</div>'
					 + ''
					 + '			<button'
					 + '				ga-on="click"'
					 + '				ga-event-category="Interactions"'
					 + '				ga-event-action="click"'
					 + '				ga-event-label="Obtener informe"'
					 + '				class="w3-btn w3-margin w3-dark-grey w3-right w3-ripple w3-small"'
					 + '				onclick="document.getElementById(\'ReportInfo\').style.display=\'block\'">'
					 + '				Obtener informe <i class="fa fa-file-text"></i>'
					 + '			</button>'
					 + ''
					 + '		</div>'
					 + '		<div class="w3-twothird">'
					 + '	<div class="w3-row">'
					 + '		<ul class="w3-navbar">'
					 + '			<li class="w3-right w3-grey w3-text-white"><a href="javascript:void(0)" onclick="" '
					 + '															ga-on="click"'
					 + '															ga-event-category="Interactions"'
					 + '															ga-event-action="click"'
					 + '															ga-event-label="Agrícolas"'
					 + '                                                            >Agrícolas</a></li>'
					 + '			<li class="w3-right"><a href="javascript:void(0)"'
					 + '       	                 onclick="document.getElementById(\'AlternativesInfo\').style.display=\'block\'"'
					 + '															ga-on="click"'
					 + '															ga-event-category="Interactions"'
					 + '															ga-event-action="click"'
					 + '															ga-event-label="Energéticas"'
					 + '															>Energéticas</a>'
					 + '			</li>'
					 + '			<li class="w3-right"><a href="javascript:void(0)"'
					 + '       	                 onclick="document.getElementById(\'AlternativesInfo\').style.display=\'block\'"'
					 + '															ga-on="click"'
					 + '															ga-event-category="Interactions"'
					 + '															ga-event-action="click"'
					 + '															ga-event-label="Forestales"'
					 + '															>Forestales</a>'
					 + '			</li>'
					 + '			<li class="w3-right"><a href="javascript:void(0)"'
					 + '    	                    onclick="document.getElementById(\'AlternativesInfo\').style.display=\'block\'"'
					 + '															ga-on="click"'
					 + '															ga-event-category="Interactions"'
					 + '															ga-event-action="click"'
					 + '															ga-event-label="Sociales"'
					 + '															>Sociales</a>'
					 + '			</li>'
					 + '		</ul>'
					 + '	</div>'
					 + '				<a href="/osc/cultivo?cultivo_id=' + id + '" target="_blank"><img ga-on="click"' 
					 + '					ga-event-category="Interactions"'
					 + '					ga-event-action="click"'
					 + '					ga-event-label="Select crop" class="w3-right" onclick="document.getElementById(\'' + id + '_modal\').style.display=\'block\'" src="/static/osc/img/cultivos/' + crop.Foto + '" style="width: 100%"></a>'
					 + '		</div>'
					 + '	</div>'
					 + '</div>';

				document.getElementById('alternativesContainer').innerHTML += contenido;
				

			}
			carousel("mySlides");
		}
	});

}

function drawLocationCard(cadastralParcelFeature) {
	try {

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
	} catch (error) {
		showErrorInCard(error, "LocationCard");
	}

}

function drawCatastralCard(parcelCadastralData) {
	try {
		if (typeof(parcelCadastralData.bico) != 'undefined') {
			setValueInField(parcelCadastralData.bico.bi.idbi.cn, "cn");
			setValueInField(parcelCadastralData.control.cucons, "cucons");
			setValueInField(parcelCadastralData.control.cucul, "cucul");
			var subparcels = parcelCadastralData.bico.lspr.spr;
			
			var cropTypeTableBody = document.getElementById('cropTypeTableBody');
			var cropTypeTableContent = cropTypeTableBody.getElementsByTagName('tr');
			var cropTypeTableContentCount = cropTypeTableContent.length;
			for(var cropTypeElementNumber = 0; cropTypeElementNumber < cropTypeTableContentCount; cropTypeElementNumber++){
				cropTypeTableBody.removeChild(cropTypeTableContent[cropTypeTableContentCount - cropTypeElementNumber - 1]);
			}
		
			
			var productionLevelTableBody = document.getElementById('productionLevelTableBody');
			var productionLevelTableContent = productionLevelTableBody.getElementsByTagName('tr');
			var productionLevelTableContentCount = productionLevelTableContent.length;
			for(var productionLevelElementNumber = 0; productionLevelElementNumber < productionLevelTableContentCount; productionLevelElementNumber++){
				productionLevelTableBody.removeChild(productionLevelTableContent[productionLevelTableContentCount - productionLevelElementNumber - 1]);
			}
			

			var cropAreaTableBody = document.getElementById('cropAreaTableBody');
			var cropAreaTableContent = cropAreaTableBody.getElementsByTagName('tr');
			var cropAreaTableContentCount = cropAreaTableContent.length;
			for(var cropAreaElementNumber = 0; cropAreaElementNumber < cropAreaTableContentCount; cropAreaElementNumber++){
				cropAreaTableBody.removeChild(cropAreaTableContent[cropAreaTableContentCount - cropAreaElementNumber - 1]);
			}
			
			
			for (subparcel in subparcels) {
				document.getElementById("cropTypeTableBody").innerHTML += '<tr><td><i>'
				 + subparcels[subparcel].dspr.ccc
				 + subparcels[subparcel].dspr.dcc + '</i></td></tr>';

				document.getElementById("productionLevelTableBody").innerHTML += '<tr><td><i>'
				 + subparcels[subparcel].dspr.ip
				 + '</i> intensidad productiva</td></tr>';

				document.getElementById("cropAreaTableBody").innerHTML += '<tr><td>'
				 + subparcels[subparcel].dspr.ssp
				 + ' </span> m<sup>2</sup></i></td>	</tr>';

			}
			setValueInField(parcelCadastralData.bico.bi.ldt, "direccion");
		} else {

			throw (new Error('Error en los datos del catastro.'));
		}
	} catch (error) {
		showErrorInCard(error, "CatastralCard");
	}

}

function drawSoilCard(closest_soil_measure){
	setValueInField(closest_soil_measure.silt, "silt", "%");
	setValueInField(closest_soil_measure.CaCO3, "CaCO3");
	setValueInField(closest_soil_measure.OC, "OC");
	setValueInField(closest_soil_measure.N, "N");
	setValueInField(closest_soil_measure.P, "P");
	setValueInField(closest_soil_measure.sand, "sand", "%");
	setValueInField(closest_soil_measure.coarse, "coarse");
	setValueInField(closest_soil_measure.clay, "clay", "%");
	setValueInField(closest_soil_measure.K, "K");
	setValueInField(closest_soil_measure.CEC, "CEC");
	setValueInField(closest_soil_measure.distance_to_parcel, "distance_to_parcel_on_closest_soil_measure");
	setValueInField(closest_soil_measure.pH_in_CaCl2, "pH_in_CaCl2");
	setValueInField(closest_soil_measure.pH_in_H2O, "pH_in_H2O");
	
	document.getElementById("phRange").value = closest_soil_measure.pH_in_H2O;
}

function drawLastYearClimateAggregationsWidgetBar(
	parcellast_yearClimate_aggregations) {
	if(parcellast_yearClimate_aggregations!= undefined){
	setValueInField(
		parcellast_yearClimate_aggregations.sum_rainfall.toFixed(2),
		"precipitacion-widget");
	setValueInField(parcellast_yearClimate_aggregations.avg_temperature
		.toFixed(2), "temperatura-widget");
	setValueInField(parcellast_yearClimate_aggregations.sum_sun_hours
		.toFixed(2), "horasSol-widget");
	setValueInField(parcellast_yearClimate_aggregations.sum_radiation
		.toFixed(2), "radiacion-widget");
	}else{
		showError(new Error('Error al crear los widgets de resumen.'));
	}
}

function drawRainfallAggregationsCard(parcelProperties) {

	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelProperties.climate_aggregations;

		google.charts.setOnLoadCallback(function () {
			drawChartOfRainfallByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelProperties.closest_station.ESTACION + " a "
			 + parcelProperties.closest_station.distance_to_parcel.toFixed()
			 + " km de distancia  (lineal)", "estacionLluvia");

		setValueInField(parcelclimate_aggregations.last_year.rainy_days,
			"diasDeLluvia");
		setValueInField(parcelclimate_aggregations.last_year.sum_rainfall
			.toFixed(2), "pecipitacionacumulada");
	} catch (error) {
		showErrorInCard(error, "RainfallCard");
	}
}

function drawTemperatureAggregationsCard(parcelProperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelProperties.climate_aggregations;

		google.charts.setOnLoadCallback(function () {
			drawChartOfTemperaturesByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelProperties.closest_station.ESTACION + " a "
			 + parcelProperties.closest_station.distance_to_parcel.toFixed()
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

function drawSunHoursAggregationsCard(parcelProperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelProperties.climate_aggregations;

		google.charts.setOnLoadCallback(function () {
			drawChartOfDailySunHoursByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelProperties.closest_station.ESTACION + " a "
			 + parcelProperties.closest_station.distance_to_parcel.toFixed()
			 + " km de distancia  (lineal)", "estacionSol");

		setValueInField(parcelclimate_aggregations.last_year.avg_sun_hours
			.toFixed(2), "mediaHorasSolDiarias");
		setValueInField(parcelclimate_aggregations.last_year.max_sun_hours
			.toFixed(2), "maximasHorasSolDiarias");
		setValueInField(parcelclimate_aggregations.last_year.sum_sun_hours,
			"horasSolAcumuladas");
	} catch (error) {
		showErrorInCard(error, "SunHoursCard");
	}
}

function drawRadiationAggregationsCard(parcelProperties) {
	try {
		loadGoogleChartsCorechart();

		var parcelclimate_aggregations = parcelProperties.climate_aggregations;

		google.charts
		.setOnLoadCallback(function () {
			drawChartOfDailyNetRadiationByMonthAndYear(parcelclimate_aggregations)
		});

		setValueInField(parcelProperties.closest_station.ESTACION + " a "
			 + parcelProperties.closest_station.distance_to_parcel.toFixed()
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
			document.getElementById("fixed").style.display = 'block';
			document.getElementById("fixedLink").style.display = 'block';
			openCropDistribution("All");
		}
	} catch (error) {
		showErrorInCard(error, "CropDistributionCard");
	}
}

function setValueInField(value, field, format ="") {
	document.getElementById(field).innerHTML = (typeof(value) != 'undefined' ? value
		 : "") + format;
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

		var monthNames = ["Enero", "Febrero", "Marzo", "Abril", "Mayo",
			"Junio", "Julio", "Agosto", "Septiembre", "Octubre",
			"Noviembre", "Diciembre"];

		for (i = 0; i < yearly_measures_by_month.length; i++) {
			var year = yearly_measures_by_month[i].year;
			var monthly_measures = yearly_measures_by_month[i].monthly_measures;
			for (j = 0; j < monthly_measures.length; j++) {
				var measures = monthly_measures[j];
				var month = measures.month;
				for (var measure in measures) {
					if (measure != 'month') {
						if (!colsByMeasure.hasOwnProperty(measure)) {
							colsByMeasure[measure] = [{
									label : "Mes",
									type : "string"
								}
							];
						}
						if (!rowsByMeasure.hasOwnProperty(measure)) {
							rowsByMeasure[measure] = [];
							for (monthName in monthNames) {
								rowsByMeasure[measure]
								.push([monthNames[monthName]]);
							}
						}
						rowsByMeasure[measure][month - 1]
						.push(measures[measure]);
					}
				}
			}
			for (var measure in colsByMeasure) {
				colsByMeasure[measure].push({
					label : year,
					type : "number"
				});
				for (var month in rowsByMeasure[measure]) {
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
				for (var measure in measures) {
					if (measure != 'Day') {
						if (!colsByDailyMeasure.hasOwnProperty(measure)) {
							colsByDailyMeasure[measure] = [{
									label : "Día",
									type : "string"
								}
							];
						}
						if (!rowsByDailyMeasure.hasOwnProperty(measure)) {
							rowsByDailyMeasure[measure] = [];
							for (dayOfYear in days) {
								rowsByDailyMeasure[measure]
								.push([days[dayOfYear]]);
							}
						}
						rowsByDailyMeasure[measure][day - 1]
						.push(measures[measure]);
					}
				}
			}
			for (var measure in colsByDailyMeasure) {
				colsByDailyMeasure[measure].push({
					label : year,
					type : "number"
				});
				for (var day in rowsByDailyMeasure[measure]) {
					if (rowsByDailyMeasure[measure][day].length < colsByDailyMeasure[measure].length) {
						rowsByDailyMeasure[measure][day].push(null);
					}

				}
			}
		}

		var googleFormatedTable = [];
		for (var measureType in colsByMeasure) {
			googleFormatedTable[measureType] = {
				cols : colsByMeasure[measureType],
				rows : rowsByMeasure[measureType]
			}
		}

		var googleDailyFormatedTable = [];
		for (var measureType in colsByDailyMeasure) {
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
				'packages' : ['table', 'bar', 'corechart', 'geochart']
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

	showError(error);

}

function showError(error){
	
	var errorPanel = document.createElement('div');
	errorPanel.setAttribute('class', 'w3-col w3-panel w3-red w3-card-4');
	errorPanel.appendChild(document.createTextNode(error.message));
	
	var proposedAction = document.createElement('a');
	proposedAction.setAttribute('class', 'w3-right');
	proposedAction.setAttribute('href', '/osc/propietario/#contacto');
	proposedAction.setAttribute('target', '_blank');
	proposedAction.appendChild(document.createTextNode('Contacte con nosotros'));
	
	errorPanel.appendChild(proposedAction);
	
	document.getElementById('infoContainer').appendChild(errorPanel);
	document.getElementById('ErrorBadge').style.display = 'block';
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

function createQueryForTypeAndValue(type, value) {
	var query;
	var minType = type + ".min";
	var maxType = type + ".max";
	// Dis Max Query: A query that generates the union of documents produced by
	// its subqueries,
	// and that scores each document with the maximum score for that document as
	// produced by any subquery, plus a tie breaking increment for any
	// additional
	// matching subqueries.
	if (encodeURIComponent(value) != "undefined") {

		var subqueryValueBetweenMinAndMaxValueForCrop = {
			bool : {
				must : [{
						range : {
							[minType] : {
								lte : value
							}
						}
					}, {
						range : {
							[maxType] : {
								gte : value
							}
						}
					}
				]
			}
		};

		var subqueryValueGreaterThanMinWithoutMaxValueForCrop = {
			bool : {
				must : {
					range : {
						[minType] : {
							lte : value
						}
					}
				},
				must_not : {
					exists : {
						field : maxType
					}
				}
			}
		};

		var subqueryValueSmallerThanMaxWithoutMinValueForCrop = {
			bool : {
				must : {
					range : {
						[maxType] : {
							gte : value
						}
					}
				},
				must_not : {
					exists : {
						field : minType
					}
				}
			}
		};

		var subqueryCropsWithoutValueRanges = {
			bool : {
				must_not : {
					exists : {
						field : maxType
					}
				},
				must_not : {
					exists : {
						field : minType
					}
				}
			}
		};

		query = {
			dis_max : {
				tie_breaker : 0.7,
				boost : 1.2,
				queries : [
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

function createQueryForTypeAndRange(type, minValue, maxValue) {
	var query;
	var minType = type + ".min";
	var maxType = type + ".max";
	// Dis Max Query: A query that generates the union of documents produced by
	// its subqueries,
	// and that scores each document with the maximum score for that document as
	// produced by any subquery, plus a tie breaking increment for any
	// additional
	// matching subqueries.
	if (encodeURIComponent(minValue) != "undefined" && encodeURIComponent(maxValue) != "undefined") {

		var subqueryValueBetweenMinAndMaxValueForCrop = {
			bool : {
				must : [{
						range : {
							[minType] : {
								lte : minValue
							}
						}
					}, {
						range : {
							[maxType] : {
								gte : maxValue
							}
						}
					}
				]
			}
		};

		var subqueryValueGreaterThanMinWithoutMaxValueForCrop = {
			bool : {
				must : {
					range : {
						[minType] : {
							lte : minValue
						}
					}
				},
				must_not : {
					exists : {
						field : maxType
					}
				}
			}
		};

		var subqueryValueSmallerThanMaxWithoutMinValueForCrop = {
			bool : {
				must : {
					range : {
						[maxType] : {
							gte : maxValue
						}
					}
				},
				must_not : {
					exists : {
						field : minType
					}
				}
			}
		};

		var subqueryCropsWithoutValueRanges = {
			bool : {
				must_not : {
					exists : {
						field : maxType
					}
				},
				must_not : {
					exists : {
						field : minType
					}
				}
			}
		};

		query = {
			dis_max : {
				tie_breaker : 0.7,
				boost : 1.2,
				queries : [
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

function aggregateQueries(queries) {

	var query = {
		bool : {
			must : queries
		}
	};

	return query;
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

	if (document.getElementById("mySidenav").innerHTML == "") {
		cargaBarraLateral();
	}
	document.getElementById("mySidenav").style.display = "block";
	document.getElementById("myOverlay").style.display = "block";
	if (document.getElementById("latitud")) {

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


// --------------------- Google code ---------------------
function onSignIn(googleUser) {
	
	var accessToken=getCookie("accessToken");
	
		if(accessToken == ''){
		
		console.log('onSignIn(googleUser)');
	
		var authorizationGrant =  {
				googleAccessToken: googleUser.getAuthResponse().id_token , 
				plot: getNationalCadastreReference(),
				relation : document.getElementById('myPlotRadio').checked?'myPlot':'interestingPlot'			
		};
		
		getAccessToken(authorizationGrant);

	}
}


function signOut() {
	console.log('signOut');
	var auth2 = gapi.auth2.getAuthInstance();
	auth2.signOut().then(function () {
		console.log('User signed out.');
		var response = {status: 'unknown'};
		statusChangeCallback(response);
	});
}



// -------------Facebook code---------------


window.fbAsyncInit = function () {
	FB.init({
		appId : '1620985944870143',
		cookie : true, // enable cookies to allow the server to access
		// the session
		xfbml : true, // parse social plugins on this page
		version : 'v2.5' // use graph api version 2.5
	});

	// Now that we've initialized the JavaScript SDK, we call
	// FB.getLoginStatus(). This function gets the state of the
	// person visiting this page and can return one of three states to
	// the callback you provide. They can be:
	//
	// 1. Logged into your app ('connected')
	// 2. Logged into Facebook, but not your app ('not_authorized')
	// 3. Not logged into Facebook and can't tell if they are logged into
	// your app or not.
	//
	// These three cases are handled in the callback function.

	FB.getLoginStatus(function (response) {
		console.log('FB.getLoginStatus');
		statusChangeCallback(response);
	});

};

// Load the SDK asynchronously
(function (d, s, id) {
	var js,	fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) return;
	js = d.createElement(s); js.id = id;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));







// --------------------- email code ----------------------------




function emailInit() {
	console.log('emailInit');
	getLoginStatus(statusChangeCallback);
}






function getEmailLogin(userEmailTokenID){
	
	console.log('getEmailLogin');

	data = {userEmailTokenID: userEmailTokenID};
	
	
	user = {
			//name : response.name,
			name : 'Invitado',
			//email : response.email,
			email : userEmailTokenID,
			loginMethod: 'email',
			//userProfilePicture : response.userProfilePinture, 
			userProfilePicture : "/static/osc/img/avatar.PNG",
			plot : getNationalCadastreReference(), 
			relation : 'myPlot'
	};
	
	var response = {status: 'connected', user: user};
	
	return response;
	
}


// ------------- login commons ---------------

function drawUser(accessToken) {
	
	console.log('drawUser');
	
	var userEndPoint = "/osc/....";
	var data = {accessToken: accessToken};
	
	/*var request = jQuery.ajax({
		crossDomain : true,
		url : userEndPoint,
		data : JSON.stringify(data),
		type : 'POST',
		dataType : "json"
	});

	request.done(function (response, textStatus, jqXHR) {*/
		//TODO eliminar cuando esté el servicio de consulta de usuario
		var response = {status: 'SUCCESS', user: user = { name : 'Invitado', email : 'test@email.com',	loginMethod: ((accessToken=='33')?'email':(accessToken=='66')?'facebook':'google'), userProfilePicture : "/static/osc/img/avatar.PNG", plots : [getNationalCadastreReference()], relation : 'myPlot'}};
		
		if (response.status == "SUCCESS") {
			var user = response.user;
			
			console.log('Successful login for: ' + user.email);

			document.getElementById('esMiParcela').style.display = 'none';
			document.getElementById('esMiParcelaButton').disabled = true;
			document.getElementById('meInteresaEstaParcelaButton').disabled = true;


			console.log(user);	
			
			drawUserMenu(user);
			
		}
			
//  });
		
}

function login(callback){

	var authorizationGrant = getAuthorizationGrant(callback);
	
	

}

function getLoginStatus(callback) {
	console.log('getLoginStatus');
	var accessToken=getCookie("accessToken");
	var response = {};
	if (accessToken != "") {
		console.log('getLoginStatus: with accessToken');
		response = {status: 'connected', accessToken: accessToken};
    }else{
    	console.log('getLoginStatus: without accessToken');
    	response = {status: 'not_connected'};
    }
	callback(response);
}

function statusChangeCallback(response) {
	console.log('statusChangeCallback');
	console.log(response);
	
	// The response object is returned with a status field that lets the
	// app know the current login status of the person.
	// Full docs on the response object can be found in the documentation
	// for FB.getLoginStatus().
	if (response.status === 'connected' && response.accessToken != undefined) {
		console.log('statusChangeCallback: Logged into Open Smart Country');
		var accessToken = response.accessToken;
		//TODO eliminar esto cuanto esté el django server con consulta de datos de usuario, ahora pasamos el response porque tiene más info
		drawUser(accessToken);
		drawPlotProfile(accessToken);
	} else if (response.status == 'not_connected'){
		console.log('statusChangeCallback: Not logged into Open Smart Country'); 
		drawPlotProfile();	
	} else {
		console.log('statusChangeCallback: unknown'); 
		emailInit();
	}
}

function logout(socialNetwork) {
	
	
	
	console.log('logout('+socialNetwork+')');
	
	setCookie('accessToken', '', 0);
	
	if (socialNetwork == 'google') {
		signOut();
	} else if (socialNetwork == 'facebook') {
		FB.logout(function (response) {
			// Person is now logged out
			statusChangeCallback(response);
			
		});
	} else if (socialNetwork == 'email'){
		var response = {status: 'unknown'};
		statusChangeCallback(response);
	}

	
	
	document.getElementById('userMenu').parentNode.removeChild(document.getElementById('userMenu'));
	document.getElementById('avatar').src = "/static/osc/img/avatar.PNG";
	document.getElementById('esMiParcelaButton').disabled = false;
	document.getElementById('meInteresaEstaParcelaButton').disabled = false;
}


function drawUserMenu(user) {
	var profile_image_url = user.userProfilePicture;
	console.log('drawUserMenu');

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
	logout_row.setAttribute('onclick', 'logout("' + user.loginMethod + '")');
	avatar_dropdown_content.appendChild(logout_row);

	var logout_icon = document.createElement('i');
	logout_icon.setAttribute('class', 'fa fa-sign-out')
	logout_row.appendChild(logout_icon);
	logout_row.appendChild(document.createTextNode(' Cerrar sesión'));

	document.getElementById('userMenuItem').appendChild(userMenu);

	document.getElementById("avatar").src = profile_image_url;
}

function authorizationRequest(relation) {
	if (relation == 'esMiParcela') {
		document.getElementById('interestingPlotRadio').checked = false;
		document.getElementById('interestingPlotRadio').disabled = true;
		document.getElementById('myPlotRadio').checked = true;
		document.getElementById('myPlotRadio').disabled = false;
		document.getElementById('objetiveDescription').innerHTML = 'Registra tu parcela';
		document.getElementById('esMiParcela').style.display = 'block';
	} else {
		document.getElementById('interestingPlotRadio').checked = true;
		document.getElementById('interestingPlotRadio').disabled = false;
		document.getElementById('myPlotRadio').checked = false;
		document.getElementById('myPlotRadio').disabled = true;
		document.getElementById('objetiveDescription').innerHTML = 'Obten información sobre la parcela';
		document.getElementById('esMiParcela').style.display = 'block';

	}
}


//------- cookies functions ----- 
function setCookie(cname,cvalue,exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


function getAuthorizationGrant(callback){
	callback();
}

function emailAuthorizationGrant(){
	var authorizationGrant =  {
			email: document.getElementById('email').value , 
			password: document.getElementById('password').value, 
			plot: getNationalCadastreReference(),
			relation : document.getElementById('myPlotRadio').checked?'myPlot':'interestingPlot'			
	};
	
	getAccessToken(authorizationGrant);
}


function facebookAuthorizationGrant() {
	console.log('login');
	FB.login(function (response) {
		console.log('login: statusChangeCallback');
		
		var authorizationGrant =  {
				facebookAccessToken: response.authResponse.accessToken , 
				plot: getNationalCadastreReference(),
				relation : document.getElementById('myPlotRadio').checked?'myPlot':'interestingPlot'			
		};
		
		getAccessToken(authorizationGrant);

	}, {
		scope : 'public_profile,email',
		return_scopes : true
	});
}

function getAccessToken(authorizationGrant){

	var authorizationTokenEndPoint = "/osc/....";
		
	/*var request = jQuery.ajax({
		crossDomain : true,
		url : authorizationTokenEndPoint,
		data : JSON.stringify(authorizationGrant),
		type : 'POST',
		dataType : "json"
	});

	request.done(function (response, textStatus, jqXHR) {*/
		//TODO quitar esto de response =
		var response = {status: 'connected', accessToken: (authorizationGrant.facebookAccessToken != undefined)?"66":(authorizationGrant.googleAccessToken != undefined)?"99":"33" };
		if (response.status == "connected") {
			var accessToken = response.accessToken;
			setCookie('accessToken', accessToken, 1);
			statusChangeCallback(response);
		}
			
//  });
}

function getProperty(property){
	var properties = property.split('.');
	var result = this;
	for (var i = 0; i < properties.length; i++){
		if(result != undefined){
			result = result[properties[i]];
		}else{
			break;
		}
	}
	if(result === undefined){
		showError (new Error('Error al intentar recuperar el dato '+ property + '.'));
	}
	return result;
}


function addAlternativesTableRow(crop, score, cadastralParcelFeatures){
	var table = document.getElementById('AlternativesTableContent');
	var row = document.createElement('tr');
	var td = document.createElement('td');
	var check;
	
	var a = document.createElement('a');
	a.setAttribute('href', '/osc/cultivo?cultivo_id=' + crop.Clave);
	a.setAttribute('target', '_blank');
	var image = document.createElement('img');
	image.setAttribute('src','/static/osc/img/cultivos/' + crop['Foto']);
	image.setAttribute('style','width:100%;max-width:40px');
	a.appendChild(image);
	td.appendChild(a);
	row.appendChild(td);

	td = document.createElement('td');
	td.appendChild(document.createTextNode(crop['Nombre']));
	row.appendChild(td);
	
	td = document.createElement('td');
	td.appendChild(document.createTextNode(crop['Nombre Científico']));
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	
	check = document.createElement('i');
	if(cadastralParcelFeatures.getProperty("properties.elevation") != undefined && crop.optimal_altitude != undefined && crop.optimal_altitude.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	} else if(cadastralParcelFeatures.getProperty("properties.elevation") != undefined && crop.altitude != undefined && crop.altitude.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-orange');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	check = document.createElement('i');
	if((cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_H2O') != undefined || cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_CaCl2') != undefined) && crop.optimal_ph != undefined && crop.optimal_ph.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	} else if((cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_H2O') != undefined || cadastralParcelFeatures.getProperty('properties.closest_soil_measure.pH_in_CaCl2') != undefined) && crop.ph != undefined && crop.ph.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-orange');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	check = document.createElement('i');
	if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.optimal_rainfall != undefined && crop.optimal_rainfall.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	} else if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.rainfall != undefined && crop.rainfall.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-orange');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	check = document.createElement('i');
	if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.optimal_sunHours != undefined && crop.optimal_sunHours.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	} else if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.sunHours != undefined && crop.sunHours.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-orange');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	check = document.createElement('i');
	if(cadastralParcelFeatures.getProperty('properties.reference_point.lat') != undefined && crop.latitude != undefined && crop.latitude.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.setAttribute('class', 'w3-center');
	check = document.createElement('i');
	if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.optimal_temperature != undefined && crop.optimal_temperature.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-green');
	} else if(cadastralParcelFeatures.getProperty('properties.climate_aggregations.last_year') != undefined && crop.temperature != undefined && crop.temperature.length > 0){
		check.setAttribute('class', 'fa fa-check-square-o w3-text-orange');
	}
	td.appendChild(check);
	row.appendChild(td);
	
	td = document.createElement('td');
	td.appendChild(document.createTextNode(score.toFixed(2)));
	row.appendChild(td);
	
	
	table.appendChild(row);
}


// ------------ Progreso perfil -----------------------

function createProgressCircle(percent){
	
	var el = document.createElement('div');
	el.setAttribute('class', 'chart');
	el.setAttribute('id', 'graph');
	el.setAttribute('data-percent', percent);
	el.setAttribute('style', 'position:relative; width:86px; height:86px;');
	
	var progressCircle = document.getElementById("progressCircle");
	while (progressCircle.firstChild) {
		progressCircle.removeChild(progressCircle.firstChild);
	}

	progressCircle.appendChild(el);
	

	var options = {
	    percent:  percent,
	    size: 86,
	    lineWidth: 8,
	    rotate: el.getAttribute('data-rotate') || 0
	}

	var canvas = document.createElement('canvas');
	canvas.setAttribute('style', 'display: block; position:absolute; top:0; left:0;');
	
	var span = document.createElement('div');
	span.textContent = options.percent + '%';
	span.setAttribute('style', ' color:#555; display:block; line-height:86px; text-align:center; width:86px; font-family:sans-serif; font-size:20px; font-weight:100; margin-left:5px;');
    
	if (typeof(G_vmlCanvasManager) !== 'undefined') {
	    G_vmlCanvasManager.initElement(canvas);
	}

	var ctx = canvas.getContext('2d');
	canvas.width = canvas.height = options.size;

	el.appendChild(span);
	el.appendChild(canvas);

	ctx.translate(options.size / 2, options.size / 2); // change center
	ctx.rotate((-1 / 2 + options.rotate / 180) * Math.PI); // rotate -90 deg

	// imd = ctx.getImageData(0, 0, 240, 240);
	var radius = (options.size - options.lineWidth) / 2;

	var drawCircle = function(color, lineWidth, percent) {
			percent = Math.min(Math.max(0, percent || 1), 1);
			ctx.beginPath();
			ctx.arc(0, 0, radius, 0, Math.PI * 2 * percent, false);
			ctx.strokeStyle = color;
	        ctx.lineCap = 'round'; // butt, round or square
			ctx.lineWidth = lineWidth
			ctx.stroke();
	};

	drawCircle('#efefef', options.lineWidth, 100 / 100);
	drawCircle('#555555', options.lineWidth, options.percent / 100);

}