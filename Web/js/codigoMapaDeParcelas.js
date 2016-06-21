// If you're adding a number of markers, you may want to drop them on the map
// consecutively rather than all at once. This example shows how to use
// window.setTimeout() to space your markers' animation.

var neighborhoods = [{
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
	}
];

var markers = [];
var map;

function initMap() {

	var myLatlng = {
		lat : 40.416616,
		lng : -3.703801
	};

	var mapOptions = {
		zoom : 7,
		center : myLatlng,
		mapTypeId : google.maps.MapTypeId.SATELLITE
	};

	map = new google.maps.Map(document.getElementById("map"),
			mapOptions);

}

function drop() {
	clearMarkers();
	for (var i = 0; i < neighborhoods.length; i++) {
		//addMarkerWithTimeout(neighborhoods[i], i * 200);

		var marker = new google.maps.Marker({
				position : neighborhoods[i],
				map : map,
				animation : google.maps.Animation.DROP

			});

		var contentString = '<div id="content">' +
			'<h1>Parcela</h1>' +
			'<img src="' + neighborhoods[i].foto + '" height="400""/>' +
			'<div>' +
			'<ul><li>Latitud: ' + neighborhoods[i].lat + '</li>' +
			'<li>Longitud: ' + neighborhoods[i].lng + '</li></ul>' +
			'</div>' +
			'</div><button type="button" onclick="location.href=\''+ neighborhoods[i].url + '\'">Más detalles</button>';

		var infowindow = new google.maps.InfoWindow({
				content : contentString
			});

		marker.addListener('click', function () {
			infowindow.open(map, marker);
		});

	}
}

function clearMarkers() {
	for (var i = 0; i < markers.length; i++) {
		markers[i].setMap(null);
	}
	markers = [];
}
