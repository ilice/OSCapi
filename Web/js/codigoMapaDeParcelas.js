// If you're adding a number of markers, you may want to drop them on the map
// consecutively rather than all at once. This example shows how to use
// window.setTimeout() to space your markers' animation.

var neighborhoods = [
  {lat: 40.439983, lng: -5.737026, foto:"http://opensmartcountry.com/WEB/img/IMG_20160501_175931.jpg"},
  {lat: 40.489864, lng: -3.639706, foto:"unaFoto"},
  {lat: 40.384769, lng: -5.762048, foto:"unaFoto"}
];

var markers = [];
var map;

function initMap() {

	var myLatlng = {lat: 40.416616, lng: 	-3.703801};
	
	var mapOptions = {
		zoom: 7,
		center: myLatlng,
		mapTypeId: google.maps.MapTypeId.SATELLITE
	};
	
	map = new google.maps.Map(document.getElementById("map"),
    mapOptions);
	
	var contentString = '<div id="content">'+
      '<div id="siteNotice">'+
      '</div>'+
      '<h1 id="firstHeading" class="firstHeading">Uluru</h1>';
	  contentString += '<img src="'+neighborhoods[0].foto +'"/>';
	  contentString += '<div id="bodyContent">'+
      '<p><b>Uluru</b>, also referred to as <b>Ayers Rock</b>, is a large ' +
      'sandstone rock formation in the southern part of the '+
      'Northern Territory, central Australia. It lies 335&#160;km (208&#160;mi) '+
      'south west of the nearest large town, Alice Springs; 450&#160;km '+
      '(280&#160;mi) by road. Kata Tjuta and Uluru are the two major '+
      'features of the Uluru - Kata Tjuta National Park. Uluru is '+
      'sacred to the Pitjantjatjara and Yankunytjatjara, the '+
      'Aboriginal people of the area. It has many springs, waterholes, '+
      'rock caves and ancient paintings. Uluru is listed as a World '+
      'Heritage Site.</p>'+
      '<p>Attribution: Uluru, <a href="https://en.wikipedia.org/w/index.php?title=Uluru&oldid=297882194">'+
      'https://en.wikipedia.org/w/index.php?title=Uluru</a> '+
      '(last visited June 22, 2009).</p>'+
      '</div>'+
      '</div>';
	  
	  var infowindow = new google.maps.InfoWindow({
    content: contentString
  });
  
  var marker = new google.maps.Marker({
    position: myLatlng,
    map: map,
    title: 'Uluru (Ayers Rock)'
  });
  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });
	
}

function drop() {
  clearMarkers();
  for (var i = 0; i < neighborhoods.length; i++) {
    addMarkerWithTimeout(neighborhoods[i], i * 200);
  }
}

function addMarkerWithTimeout(position, timeout) {
  window.setTimeout(function() {
    markers.push(new google.maps.Marker({
      position: position,
      map: map,
      animation: google.maps.Animation.DROP
    }));
  }, timeout);
}

function clearMarkers() {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(null);
  }
  markers = [];
}
