// Dibuja el mapa en la barra lateral
function drawRegionsMap() {

	var data = google.visualization.arrayToDataTable([
				['latitude', 'longitude', 'temperatura'],
				[40.440005, -5.737003, 25]
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
	
	document.getElementById("mySidenav").style.display = "block";
	document.getElementById("myOverlay").style.display = "block";
	if(document.getElementById("isGoogleChartsCorechartLoaded").innerHTML ==  "false"){
		google.charts.load('current', {'packages':['corechart']});
		document.getElementById("isGoogleChartsCorechartLoaded").innerHTML = "true";
	}
	google.charts.setOnLoadCallback(drawRegionsMap);
}

function w3_close() {
	document.getElementById("mySidenav").style.display = "none";
	document.getElementById("myOverlay").style.display = "none";
}