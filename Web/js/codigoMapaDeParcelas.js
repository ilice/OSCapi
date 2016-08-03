var parcelas = [ {
	lat : 40.416616,
	lng : -3.703801,
	foto : "img/IMG_20160501_175931.jpg",
	url : "parcela.html?latitud=40.439983&longitud=-5.737026&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
}, {
	lat : 40.439983,
	lng : -5.737026,
	foto : "img/IMG_20160501_175931.jpg",
	url : "parcela.html?latitud=40.439983&longitud=-5.737026&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
}, {
	lat : 40.489864,
	lng : -3.639706,
	foto : "img/IMG_20160501_175931.jpg",
	url : "parcela.html?latitud=40.439983&longitud=-5.737026&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
}, {
	lat : 40.384769,
	lng : -5.762048,
	foto : "img/IMG_20160501_175931.jpg",
	url : "parcela.html?latitud=40.439983&longitud=-5.737026&nombre=Viña%20de%20la%20estación&avatar=avatar_vinia.PNG"
}, {
	lat : 41.080364,
	lng : -4.588973,
	foto : "img/IMG_0882.JPG",
	url : "parcela.html?latitud=41.080364&longitud=-4.589025&nombre=La%20Nueva"
} ];

var marcadores = [];
var mapa;

function inicializaMapa() {

	var kilometroCero = {
		lat : 40.416616,
		lng : -3.703801
	};

	var configuracionMapa = {
		zoom : 7,
		center : kilometroCero,
		mapTypeId : google.maps.MapTypeId.SATELLITE
	};

	mapa = new google.maps.Map(document.getElementById("mapa"),
			configuracionMapa);


	mapa.addListener('click', function(event) {
		var latitude = event.latLng.lat();
		var longitude = event.latLng.lng();
		
		var image = 'img/OpenSmartCountry_marker_verde.png';

		var marcador = new google.maps.Marker({
			position : event.latLng,
			map : mapa,
			animation : google.maps.Animation.DROP,
			icon: image
		});

		var contenidoVentana = '<div id="content">' + 
		'<h3>Parcela</h3>' +
		'<p>' +latitude +' ,'+ longitude + '</p>' +
		'</div><button type="button" onclick="location.href=\'parcela.html?latitud='+ latitude + '&longitud='+ longitude+'&nombre=Demo\'">Más detalles</button>';

		var ventanaInformacion = new google.maps.InfoWindow({
			content : contenidoVentana
		});

		marcador.addListener('click', function() {
			ventanaInformacion.open(mapa, marcador);
		});

		// Center of map
		mapa.panTo(new google.maps.LatLng(latitude, longitude));
	})
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
			icon: image
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
