function cargaBarraLateral() {

	document.getElementById('mySidenav').innerHTML = "";
	document.getElementById('mySidenav').innerHTML += " <div class=\"w3-container  \">";
	document.getElementById('mySidenav').innerHTML += "			<div class=\"w3-row w3-right\">";
	document.getElementById('mySidenav').innerHTML += "				<div class=\"w3-col w3-right\">";
	document.getElementById('mySidenav').innerHTML += "					<a href=\"index.html\" class=\"w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge\"><i class=\"fa fa-home\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "					<a href=\"mapaDeParcelas.html\" class=\"w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge\"><i class=\"fa fa-globe\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "					<a href=\"#\" class=\"w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge\" onclick=\"w3_close()\"><i class=\"fa fa-remove\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "				</div>";
	document.getElementById('mySidenav').innerHTML += "			</div>";
	document.getElementById('mySidenav').innerHTML += "		</div>";
	document.getElementById('mySidenav').innerHTML += "		<hr/>";

	document.getElementById('mySidenav').innerHTML += "		<div class=\"w3-container w3-row w3-padding-16\">";
	document.getElementById('mySidenav').innerHTML += "			<div class=\"w3-col s4\">";
	document.getElementById('mySidenav').innerHTML += "				<img src=\"img/avatar_vinia.PNG\" class=\"w3-circle w3-margin-right\" style=\"width:46px\" alt=\"Avatar Viña de la Estación\"/>";
	document.getElementById('mySidenav').innerHTML += "			</div>";
	document.getElementById('mySidenav').innerHTML += "			<div class=\"w3-col s8\">";
	document.getElementById('mySidenav').innerHTML += "				<span>Bienvenidos a <strong>"+ document.getElementById('pagina').innerHTML+"</strong></span><br/>";
	document.getElementById('mySidenav').innerHTML += "				<a href=\"#\" class=\"w3-hover-none w3-hover-text-red w3-show-inline-block\"><i class=\"fa fa-envelope\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "				<a href=\"#\" class=\"w3-hover-none w3-hover-text-green w3-show-inline-block\"><i class=\"fa fa-user\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "				<a href=\"#\" class=\"w3-hover-none w3-hover-text-blue w3-show-inline-block\"><i class=\"fa fa-cog\"></i></a>";
	document.getElementById('mySidenav').innerHTML += "			</div>";
	document.getElementById('mySidenav').innerHTML += "		</div>";
	document.getElementById('mySidenav').innerHTML += "		<hr/>";

	document.getElementById('mySidenav').innerHTML += "		<div class=\"w3-container\" id=\"panelNavegacion\">";
	document.getElementById('mySidenav').innerHTML += "			<h5>Panel de navegación</h5>";
	document.getElementById('mySidenav').innerHTML += "		</div>";

	document.getElementById('mySidenav').innerHTML += "		<a href=\"#\" class=\"w3-padding w3-blue\" onclick=\"w3_close();\"><i class=\"fa fa fa-television fa-fw\"></i>  General</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#catastro\" class=\"w3-padding\" onclick=\"document.getElementById('catastro').style.display='block';w3_close();\"><i class=\"fa fa-institution fa-fw\"></i>  Catastro</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#tarjetaMapa\" class=\"w3-padding\" onclick=\"document.getElementById('tarjetaMapa').style.display='block';w3_close();\"><i class=\"fa fa-map fa-fw\"></i>  Mapa</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#cacharrito\" class=\"w3-padding\" onclick=\"document.getElementById('cacharrito').style.display='block';w3_close();\"><i class=\"fa fa-map-pin\"></i>  Sensores en la parcela</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#precipitacion\" class=\"w3-padding\" onclick=\"document.getElementById('precipitacion').style.display='block';w3_close();\"><i class=\"fa fa-tint fa-fw\"></i>  Precipitaciones</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#temperatura\" class=\"w3-padding\" onclick=\"document.getElementById('temperatura').style.display='block';w3_close();\"><i class=\"fa fa-eyedropper fa-fw\"></i>  Temperatura</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#sol\" class=\"w3-padding\" onclick=\"document.getElementById('sol').style.display='block';w3_close();\"><i class=\"fa fa-certificate fa-fw\"></i>  Sol</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#radiacion\" class=\"w3-padding\" onclick=\"document.getElementById('radiacion').style.display='block';w3_close();\"><i class=\"fa fa-rss fa-fw\"></i>  Radiacion</a>";
	document.getElementById('mySidenav').innerHTML += "		<a href=\"#informacion\" class=\"w3-padding\" onclick=\"document.getElementById('informacion').style.display='block';w3_close();\"><i class=\"fa fa-info fa-fw\"></i>  Información</a>";

	document.getElementById('mySidenav').innerHTML += "		<div  id=\"regions_div\"  style=\"width: 100%; height: auto;\" ></div>";

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
