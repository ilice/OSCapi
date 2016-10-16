var parcelas = [
		{
			lat : 40.439983,
			lng : -5.737026,
			foto : "img/IMG_20160501_175931.jpg",
			url : "parcela.html?cadastral_code=37284A00600098&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
		},
		{
			lat : 41.080364,
			lng : -4.588973,
			foto : "img/IMG_0882.JPG",
			url : "parcela.html?cadastral_code=40066A00500025&longitud=-4.589025&nombre=La%20Nueva"
		} ];

var marcadores = [];
var mapa;

var idCastillaYLeon = 37;

function inicializaMapa() {

	var kilometroCero = {
		lat : 40.416616,
		lng : -3.703801
	};

	var zoomEspania = 7;

	var castillaYLeon = {
		lat : 41.6571477,
		lng : -5.5472595
	};

	var zoomCastillaYLeon = 8;

	var configuracionMapa = {
		zoom : zoomCastillaYLeon,
		center : castillaYLeon,
		mapTypeId : google.maps.MapTypeId.HYBRID,
		mapTypeControl : true,
		mapTypeControlOptions : {
			style : google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
			position : google.maps.ControlPosition.TOP_LEFT
		},
		zoomControl : true,
		zoomControlOptions : {
			position : google.maps.ControlPosition.LEFT_TOP,
			style : google.maps.ZoomControlStyle.LARGE
		},
		scaleControl : true,
		streetViewControl : false
	};

	mapa = new google.maps.Map(document.getElementById("mapa"),
			configuracionMapa);

	var input = /** @type {!HTMLInputElement} */
	(document.getElementById('buscador'));

	var autocomplete = new google.maps.places.Autocomplete(input);
	autocomplete.bindTo('bounds', mapa);

	var infowindow = new google.maps.InfoWindow();
	var marker = new google.maps.Marker({
		map : mapa,
		anchorPoint : new google.maps.Point(0, -29)
	});

	var geocoder = new google.maps.Geocoder();

	document.getElementById('buscar').addEventListener('click', function() {
		geocodeAddress(geocoder, mapa);
	});

	autocomplete.addListener('place_changed', function() {
		infowindow.close();
		marker.setVisible(false);
		var place = autocomplete.getPlace();
		if (!place.geometry) {
			geocodeAddress(geocoder, mapa);
			return;
		}

		// If the place has a geometry, then present it on a
		// map.
		if (place.geometry.viewport) {
			mapa.fitBounds(place.geometry.viewport);
		} else {
			mapa.setCenter(place.geometry.location);
			mapa.setZoom(17); // Why 17? Because it looks
			// good.
		}
		marker.setIcon(/** @type {google.maps.Icon} */
		({
			url : place.icon,
			size : new google.maps.Size(71, 71),
			origin : new google.maps.Point(0, 0),
			anchor : new google.maps.Point(17, 34),
			scaledSize : new google.maps.Size(35, 35)
		}));
		marker.setPosition(place.geometry.location);
		// marker.setVisible(true);

		var address = '';
		if (place.address_components) {
			address = [
					(place.address_components[0]
							&& place.address_components[0].short_name || ''),
					(place.address_components[1]
							&& place.address_components[1].short_name || ''),
					(place.address_components[2]
							&& place.address_components[2].short_name || '') ]
					.join(' ');
		}

		infowindow.setContent('<div><strong>' + place.name + '</strong><br>'
				+ address);
		infowindow.open(mapa, marker);
	});

	mapa.data.setStyle(function(feature) {
		var zoneType = feature.getProperty('zoneType');
		var color = typeof zoneType != 'undefined' ? 'Gold' : 'Tomato';
		var weight = typeof zoneType != 'undefined' ? 2 : 1;
		var opacity = typeof zoneType != 'undefined' ? 0.1 : 0.3;
		return {
			fillColor : color,
			fillOpacity : opacity,
			strokeColor : color,
			strokeWeight : weight
		};
	});

	var castillaYLeonCoords = getBoundaries(idCastillaYLeon);

	mapa.data.addGeoJson(castillaYLeonCoords);
	// aniadeListenerParaNuevasParcelas(mapa);

	mapa
			.addListener(
					'idle',
					function() {
						var bbox = mapa.getBounds();
						var area = computeArea(bbox);
						if (area <= 16000000) {
							var cadastralParcelFeatureCollection = getCadastralParcelFeatureCollection(bbox);
							if (typeof (cadastralParcelFeatureCollection) != 'undefined'
									&& cadastralParcelFeatureCollection.features.length > 0) {
								mapa.data
										.forEach(function(feature) {
											var zoneType = feature
													.getProperty("zoneType");
											if (typeof zoneType == 'undefined'
													|| zoneType != 'administrative') {
												mapa.data.remove(feature);
											} else {
												mapa.data
														.addListener(
																'click',
																function(event) {
																	var latitude = event.feature.getProperty("reference_point").lat;
																	var longitude = event.feature.getProperty("reference_point").lon;
																	var nationalCadastralReference = event.feature.getProperty("nationalCadastralReference");

																	var bbox = new google.maps.LatLngBounds(
																			google.maps.geometry.spherical
																					.computeOffset(
																							event.latLng,
																							500,
																							-135),
																			google.maps.geometry.spherical
																					.computeOffset(
																							event.latLng,
																							500,
																							45));

																	

																		var image = 'img/OpenSmartCountry_marker_verde.png';

																		var marcador = new google.maps.Marker(
																				{
																					position : {lat: latitude, lng: longitude},
																					map : mapa,
																					animation : google.maps.Animation.DROP,
																					icon : image
																				});

																		var contenidoVentana = '<div id="content">'
																				+ '<h3>Parcela</h3>'
																				+ '<p>'
																				+ latitude
																				+ ' ,'
																				+ longitude
																				+ '</p>'															
																				+ '</div><button type="button" onclick="location.href=\'parcela.html?cadastral_code='
																				+ nationalCadastralReference
																				+ '&nombre=Demo\'">Más detalles</button>';

																		var ventanaInformacion = new google.maps.InfoWindow(
																				{
																					content : contenidoVentana
																				});

																		marcador
																				.addListener(
																						'click',
																						function() {
																							ventanaInformacion
																									.open(
																											mapa,
																											marcador);
																						});

																		

																	

																})
											}
										});
							}
							mapa.data
									.addGeoJson(cadastralParcelFeatureCollection);
							aniadeListenerParaNuevasParcelas(mapa);
						}

					});

}

function dibujaMarcadores() {
	limpiaMarcadores();
	for (var i = 0; i < parcelas.length; i++) {
		aniadeMarcadorConTimeout(parcelas[i], i * 200);
	}
}

function aniadeMarcadorConTimeout(posicion, timeout) {

	window.setTimeout(function() {
		var unaCosa = 'uno';

		var image = 'img/OpenSmartCountry_marker_rojo.png';

		var marcador = new google.maps.Marker({
			position : posicion,
			map : mapa,
			animation : google.maps.Animation.DROP,
			icon : image
		});

		var contenidoVentana = '<div id="content">' + '<h1>Parcela</h1>'
				+ '<img src="' + posicion.foto + '" height="400""/>' + '<div>'
				+ '<ul><li>Latitud: ' + posicion.lat + '</li>'
				+ '<li>Longitud: ' + posicion.lng + '</li></ul>' + '</div>'
				+ '</div><button type="button" onclick="location.href=\''
				+ posicion.url + '\'">Más detalles</button>';

		var ventanaInformacion = new google.maps.InfoWindow({
			content : contenidoVentana
		});

		marcador.addListener('click', function() {
			ventanaInformacion.open(mapa, marcador);
		});

		marcadores.push(marcador);
	}, timeout);

}

function limpiaMarcadores() {
	for (var i = 0; i < marcadores.length; i++) {
		marcadores[i].setmap(null);
	}
	marcadores = [];
}

function geocodeAddress(geocoder, resultsMap) {
	var address = document.getElementById('buscador').value;
	geocoder.geocode({
		'address' : address
	}, function(results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
			resultsMap.setCenter(results[0].geometry.location);
			resultsMap.setZoom(15);
			var marker = new google.maps.Marker({
				map : resultsMap,
				position : results[0].geometry.location
			});
			marker.setVisible(false);
			var infowindow = new google.maps.InfoWindow();
			infowindow.setContent('<div>Localización aproximada: <strong>'
					+ address + '</strong></div>');
			infowindow.open(mapa, marker);
		} else {
			var location = buscaLocalizacionPorReferenciaCatastral(address);
			if (!jQuery.isEmptyObject(location)) {
				resultsMap.setCenter(location);
				resultsMap.setZoom(15);
				var marker = new google.maps.Marker({
					map : resultsMap,
					position : location
				});
				marker.setVisible(false);
				var infowindow = new google.maps.InfoWindow();
				infowindow.setContent('<div>Referencia catastral: <strong>'
						+ address + '</strong></div>');
				infowindow.open(mapa, marker);
			}
		}
	});
}

function buscaLocalizacionPorReferenciaCatastral(referenciaCatastral) {
	var location = {};
	var base = 10;
	var provinciasConDatos = [ 5, 9, 24, 34, 37, 40, 42, 47, 49 ];
	var provincia = parseInt(referenciaCatastral.substring(0, 2), base);
	var municipio = parseInt(referenciaCatastral.substring(2, 5), base);
	var poligono = parseInt(referenciaCatastral.substring(6, 9), base);
	var parcela = parseInt(referenciaCatastral.substring(9, 14), base);

	if (isNaN(provincia) || isNaN(municipio) || isNaN(poligono)
			|| isNaN(parcela)) {
		document.getElementById('textoDelAviso').innerHTML = '<p>No encontramos lugares para el texto de búsqueda introducido.</p>'
				+ '<p> Si está intentando buscar una referencia catastral el formato debe ser: </p>'
				+ '<ul class="w3-ul w3-hoverable w3-small">'
				+ '	<li>00 - Dos dígitos para la provincia </li>'
				+ '	<li>000 - Tres dígitos para el municipio </li>'
				+ '	<li>A -Una letra para el sector</li>'
				+ '	<li>000 - Tres dígitos para el polígono</li>'
				+ '	<li>00000 - Cuatro dígitos para la parcela</li>'
				+ '	<li>0000 - Cuatro dígitos para el identificador de construcción (no son obligatorios)</li>'
				+ '	<li>AA - Dos letras de control (no son obligatorios)</li>'
				+ '	</ul>'
				+ 'Por ejemplo puede probar a buscar la referencia catastral: <strong>37284A00600098</strong>'
				+ '<p> Pruebe a realizar la búsqueda de nuevo.</p>';
		document.getElementById('aviso').style.display = 'block';

	} else if (provinciasConDatos.indexOf(provincia) == -1) {
		document.getElementById('textoDelAviso').innerHTML = '<p>Aún no tenemos datos para esa provincia.</p>'
				+ '<p> Estamos empezando por Castilla y León pero en breve ampliaremos a otras comunidades. </p>'
				+ '<p> Si quiere que <strong>prioricemos su zona</strong> contacte con nosotros. </p>';
		document.getElementById('aviso').style.display = 'block';

	} else {

		var url = "php/api_rest.php/plots" + "/sigpac/_search";

		var input = '{' + '   "query": {' + '      "constant_score": {'
				+ '         "filter": {' + '            "bool": {'
				+ '               "must": [' + '                  {'
				+ '                     "term": {'
				+ '                        "provincia": '
				+ provincia
				+ '                     }'
				+ '                  }, '
				+ '                  {'
				+ '                     "term": {'
				+ '                        "municipio": '
				+ municipio
				+ '                     }'
				+ '                  }, '
				+ '                  {'
				+ '                     "term": {'
				+ '                        "poligono": '
				+ poligono
				+ '                     }'
				+ '                  }, '
				+ '                  {'
				+ '                     "term": {'
				+ '                        "parcela": '
				+ parcela
				+ '                     }'
				+ '                  }'
				+ '               ],'
				+ '               "must_not": '
				+ '                  {'
				+ '                      "match": {'
				+ '                         "uso_sigpac": "CA"'
				+ '                      }'
				+ '                  }'
				+ '               '
				+ '            }'
				+ '         }'
				+ '      }' + '   }' + '}';

		var coordenadasLinde = [];

		var request = jQuery.ajax({
			crossDomain : true,
			async : false,
			url : url,
			data : input,
			type : 'POST',
			dataType : "json"
		});

		request.done(function(response, textStatus, jqXHR) {
			var hayCoordenadasLinde = false;
			if (typeof response["hits"] != 'undefined') {
				var hits = response["hits"]["hits"];

				for (var i = 0; i < hits.length; i++) {

					var hit = hits[i];

					// coordenadasLinde
					// .push(arrayToPathLatLong(hit["_source"]["bbox_center"]["coordinates"][0]));
					hayCoordenadasLinde = true;
					location["lat"] = hit["_source"]["bbox_center"]["lat"];
					location["lng"] = hit["_source"]["bbox_center"]["lon"];
				}

			}
		});

	}

	return location;
}

function getBoundaries(idProvincia) {
	var geoJSONBoundaries = JSON
			.parse('{ "type": "FeatureCollection", '
					+ '"features": ['
					+ '{ "type": "Feature",'
					+ '"geometry": {}, "properties": {"zone": null, "zoneType": "administrative"}'
					+ '}]}');

	var url = "php/api_rest.php/crappyzone/bullshit/" + idProvincia;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		type : 'GET',
		dataType : "json",
		async : false
	});

	request.done(function(response, textStatus, jqXHR) {
		coordinates = response["_source"]["boundaries"];
		zone = response["_source"]["zone"];
	});

	geoJSONBoundaries["features"][0]["geometry"] = coordinates;
	geoJSONBoundaries["features"][0]["properties"]["zone"] = zone;

	return geoJSONBoundaries;
}

function getCadastralParcelFeatureCollection(bbox) {
	var cadastralParcelFeatureCollection;

	var url = "php/temp_features.php/osc/cadastral/parcel?bbox="
			+ bbox.toUrlValue();

	var request = jQuery.ajax({
		url : url,
		type : 'GET',
		dataType : "json",
		async : false
	});

	request.done(function(response, textStatus, jqXHR) {
		cadastralParcelFeatureCollection = response;
	});

	return cadastralParcelFeatureCollection;
}

function aniadeListenerParaNuevasParcelas(mapa, feature) {

	mapa.data.forEach(function(feature) {

	});

}

function computeArea(bbox) {
	var area = 0;

	var northEastCorner = bbox.getNorthEast();
	var southWestCorner = bbox.getSouthWest();
	var northWestCorner = new google.maps.LatLng(northEastCorner.lat(),
			southWestCorner.lng());

	area = google.maps.geometry.spherical.computeDistanceBetween(
			northEastCorner, northWestCorner)
			* google.maps.geometry.spherical.computeDistanceBetween(
					northWestCorner, southWestCorner);

	return area;
}

