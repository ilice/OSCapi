var parcelas = [{
		lat : 40.416616,
		lng : -3.703801,
		foto : "img/IMG_20160501_175931.jpg",
		url : "viniaDeLaEstacion.html"
	}, {
		lat : 40.439983,
		lng : -5.737026,
		foto : "img/IMG_20160501_175931.jpg",
		url : "viniaDeLaEstacion.html"
	}, {
		lat : 40.489864,
		lng : -3.639706,
		foto : "img/IMG_20160501_175931.jpg",
		url : "viniaDeLaEstacion.html"
	}, {
		lat : 40.384769,
		lng : -5.762048,
		foto : "img/IMG_20160501_175931.jpg",
		url : "viniaDeLaEstacion.html"
	},
	{
		lat : 41.080364,
		lng : -4.588973,
		foto : "img/IMG_0882.jpg",
		url : "laNueva.html"
	}
];

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

	mapa = new google.maps.Map(document.getElementById("mapa"), configuracionMapa);

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
		
		
		var marcador = new google.maps.Marker({
				position : posicion,
				map : mapa,
				animation : google.maps.Animation.DROP
			});

		var contenidoVentana = '<div id="content">' +
			'<h1>Parcela</h1>' +
			'<img src="' + posicion.foto + '" height="400""/>' +
			'<div>' +
			'<ul><li>Latitud: ' + posicion.lat + '</li>' +
			'<li>Longitud: ' + posicion.lng + '</li></ul>' +
			'</div>' +
			'</div><button type="button" onclick="location.href=\'' + posicion.url + '\'">Más detalles</button>';

		var ventanaInformacion = new google.maps.InfoWindow({
				content : contenidoVentana
			});

		marcador.addListener('click', function () {
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
