var parcelas = [
		{
			lat : 40.439983,
			lng : -5.737026,
			foto : "/static/osc/img/IMG_20160501_175931.jpg",
			url : "/parcela?cadastral_code=37284A00600098&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
		},
		{
			lat : 41.080364,
			lng : -4.588973,
			foto : "/static/osc/img/IMG_0882.JPG",
			url : "/parcela?cadastral_code=40066A00500025&longitud=-4.589025&nombre=La%20Nueva"
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

	var inputSmall = /** @type {!HTMLInputElement} */
	(document.getElementById('buscadorSmall'));

	var autocompleteSmall = new google.maps.places.Autocomplete(inputSmall);
	autocompleteSmall.bindTo('bounds', mapa);

	var infowindow = new google.maps.InfoWindow();
	var marker = new google.maps.Marker({
		map : mapa,
		anchorPoint : new google.maps.Point(0, -29)
	});

	var geocoder = new google.maps.Geocoder();

	document.getElementById('buscar').addEventListener('click', function() {
		geocodeAddress(geocoder, mapa);
	});

	document.getElementById('buscarSmall').addEventListener('click', function() {
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

    autocompleteSmall.addListener('place_changed', function() {
		infowindow.close();
		marker.setVisible(false);
		var place = autocompleteSmall.getPlace();
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

	mapa.addListener('idle', function() {
		var bbox = mapa.getBounds();
		var area = computeArea(bbox);
		if (area <= 2000000) {
			document.getElementById("loader").style.display = "block";
			mapa.data.forEach(function(feature) {
				var zoneType = feature.getProperty("zoneType");
				if (typeof zoneType == 'undefined'
						|| zoneType != 'administrative') {
					mapa.data.remove(feature);
				} else {

				}
			});

			var url = "/cadastral/parcel?bbox="
					+ getOptimalBbox(bbox).toUrlValue();

			mapa.data.loadGeoJson(url, null, function(features) {
				document.getElementById("loader").style.display = "none";
			});

		}

	});
	mapa.data
			.addListener(
					'click',
					function(event) {
						if (typeof (event.feature
								.getProperty("reference_point")) == 'undefined') {
							//TODO ahora  nunca pasa por aquí porque solo se permite hacer clik en las parcelas pintadas, hay que poner este aviso en otro sitio
							document.getElementById('textoDelAviso').innerHTML = '<p>Seleccione una de las <strong>parcelas dibujadas</strong>.</p>'
									+ '<p> Para que se vean las parcelas debe hacer zoom hasta que aparezcan marcadas en rojo, en ese momento simplemente seleccione una de ellas para añadir un marcador.</p>'
									+ '<p> Una vez esté el marcador en la parcela pulse sobre él para poder ver datos básicos o para ver su <strong>perfil</strong> </p>'
									+ '<p> Si no consigue <strong>marcar su parcela </strong> contacte con nosotros. </p>';
							document.getElementById('aviso').style.display = 'block';
						} else {
							ga('send', 'event', 'Interactions', 'click', 'Select plot');
							var latitude = event.feature
									.getProperty("reference_point").lat;
							var longitude = event.feature
									.getProperty("reference_point").lon;
							var nationalCadastralReference = event.feature
									.getProperty("nationalCadastralReference");

							var bbox = new google.maps.LatLngBounds(
									google.maps.geometry.spherical
											.computeOffset(event.latLng, 500,
													-135),
									google.maps.geometry.spherical
											.computeOffset(event.latLng, 500,
													45));

							var image = '/static/osc/img/OpenSmartCountry_marker_verde.png';

							var marcador = new google.maps.Marker({
								position : {
									lat : latitude,
									lng : longitude
								},
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
									+ '</div> '
									+ ' <button ga-on="click" '
		                            + '			ga-event-category="Interactions" '
		                            + ' 		ga-event-action="click" '
		                            + '         ga-event-label="Más detalles" '
		                            + '			type="button" '
		                            + '			onclick="window.open(\'/parcela?cadastral_code='
									+ nationalCadastralReference
									+ '&nombre=Demo\')">Más detalles</button>';

							var ventanaInformacion = new google.maps.InfoWindow(
									{
										content : contenidoVentana
									});

							marcador.addListener('click', function() {
								ventanaInformacion.open(mapa, marcador);
							});
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

		var image = '/static/osc/img/OpenSmartCountry_marker_rojo.png';

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
				+ '</div> ' 
				+ ' <button ga-on="click" '
                + '			ga-event-category="Interactions" '
                + ' 		ga-event-action="click" '
                + '         ga-event-label="Más detalles" '
                + '			type="button" '
                + '			onclick="window.open(\''
				+ posicion.url + '\')">Más detalles</button>';

		var ventanaInformacion = new google.maps.InfoWindow({
			content : contenidoVentana
		});

		marcador.addListener('click', function() {
			ga('send', 'event', 'Interactions', 'click', 'Open info window');
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
	var addressSmall = document.getElementById('buscadorSmall').value;
	if(addressSmall != "" && address == ""){
	    address = addressSmall;
	}
	geocoder
			.geocode(
					{
						'address' : address
					},
					function(results, status) {
						if (status === google.maps.GeocoderStatus.OK) {
							resultsMap.setCenter(results[0].geometry.location);
							resultsMap.setZoom(15);
							var marker = new google.maps.Marker({
								map : resultsMap,
								position : results[0].geometry.location
							});
							marker.setVisible(false);
							var infowindow = new google.maps.InfoWindow();
							infowindow
									.setContent('<div>Localización aproximada: <strong>'
											+ address + '</strong></div>');
							infowindow.open(mapa, marker);
						} else {
							var location = getCoodinatesFromNationalCadastralReference(address);
							if (!jQuery.isEmptyObject(location)) {
								resultsMap.setCenter(location);
								resultsMap.setZoom(15);
								var marker = new google.maps.Marker({
									map : resultsMap,
									position : location
								});
								marker.setVisible(false);
								var infowindow = new google.maps.InfoWindow();
								infowindow
										.setContent('<div>Referencia catastral: <strong>'
												+ address + '</strong></div>');
								infowindow.open(mapa, marker);
							}
						}
					});
}

function getCoodinatesFromNationalCadastralReference(nationalCadastralReference) {
	var location = {};
	var base = 10;
	var provinciasConDatos = [ 5, 9, 24, 34, 37, 40, 42, 47, 49 ];
	var provincia = parseInt(nationalCadastralReference.substring(0, 2), base);
	var municipio = parseInt(nationalCadastralReference.substring(2, 5), base);
	var poligono = parseInt(nationalCadastralReference.substring(6, 9), base);
	var parcela = parseInt(nationalCadastralReference.substring(9, 14), base);

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

	} else {

		var url = '/cadastral/parcel?cadastral_code='
				+ nationalCadastralReference
				+ '&retrieve_public_info=True&retrieve_climate_info=True';

		var request = jQuery.ajax({
			url : url,
			type : 'GET',
			dataType : "json",
		        async : false
		});

		request.done(function(response, textStatus, jqXHR) {

			var features = response.features;
			for (feature in features) {
				location["lat"] = features[feature].properties.reference_point.lat;
				location["lng"] = features[feature].properties.reference_point.lon;
			}
                        if (location.lat === undefined || location.lng === undefined) {
                                document.getElementById('textoDelAviso').innerHTML = '<p>No hemos encotrado datos para los criterios de búsqueda.</p>'
                                        + '<p>Estamos empezando por Castilla y León pero en breve ampliaremos a otras comunidades.</p>'
                                        + '<p>Si quiere que <strong>prioricemos su zona</strong> contacte con nosotros.</p>';
                                document.getElementById('aviso').style.display = 'block';
                        }
		});

	}

	return location;
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

function getOptimalBbox(bbox) {
	var reducedBbox = bbox;
	if (computeArea(bbox) > 500000) {
		var distance = google.maps.geometry.spherical.computeDistanceBetween(
				bbox.getSouthWest(), bbox.getNorthEast());
		var offsetdistance = distance * 0.1;
		reducedBbox = new google.maps.LatLngBounds(
				google.maps.geometry.spherical.computeOffset(bbox
						.getSouthWest(), offsetdistance, 45),
				google.maps.geometry.spherical.computeOffset(bbox
						.getNorthEast(), offsetdistance, -135));
	}
	return reducedBbox;
}
