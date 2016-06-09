
function obten(campo,anio, tipomedida,variable) {
	
	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?anio=" + anio + "&variable=" + variable +"&tipomedida=" +tipoMedida;
	
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		document.getElementById(campo).innerHTML = response[variable][tipomedida].value.toFixed(2);
	});
}

function actualiza() {
	
	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?actualizaDatos&provincia=37&estacion=3";
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});
}


if(document.title == "Open Smart Country"){
	
	
	actualiza();
	obten(2016);
	// obten("diasDeLluvia", 2016, "numeroDeElementosMayoresQueCero","precipitacionDiaria");
	// obten("pecipitacionacumulada", 2016, "acumulado","precipitacionDiaria");
	// obten("maximaTemperaturaDiurna", 2016, "maximo","temperaturaMediaDiurna");
	// obten("minimaTemperaturaDiurna", 2016, "minimo","temperaturaMediaDiurna");
	// obten("mediaTemperaturaDiurna", 2016, "media","temperaturaMediaDiurna");
	// obten("mediaHorasSolDiarias", 2016, "media","horasDeSolDiarias");
	// obten("maximasHorasSolDiarias", 2016, "maximo","horasDeSolDiarias");
	// obten("horasSolAcumuladas", 2016, "numeroDeElementos","horasDeSolDiarias");
	// obten("maximoRadiacionNetaDiaria", 2016, "maximo","radiacionNeta");
	// obten("mediaRadiacionNetaDiaria", 2016, "media","radiacionNeta");
	// obten("acumuladoRadiacionNetaDiaria", 2016, "acumulado","radiacionNeta");
	
}


function obten(anio){
	
	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?anio=" + anio;
	
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		
		document.getElementById("diasDeLluvia").innerHTML = response["precipitacionDiaria"]["numeroDeElementosMayoresQueCero"].value.toFixed(2);
		document.getElementById("pecipitacionacumulada").innerHTML = response["precipitacionDiaria"]["acumulado"].value.toFixed(2);
		document.getElementById("maximaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["maximo"].value.toFixed(2);
		document.getElementById("minimaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["minimo"].value.toFixed(2);
		document.getElementById("mediaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["media"].value.toFixed(2);
		document.getElementById("mediaHorasSolDiarias").innerHTML = response["horasDeSolDiarias"]["media"].value.toFixed(2);
		document.getElementById("maximasHorasSolDiarias").innerHTML = response["horasDeSolDiarias"]["maximo"].value.toFixed(2);
		document.getElementById("horasSolAcumuladas").innerHTML = response["horasDeSolDiarias"]["acumulado"].value.toFixed(2);
		document.getElementById("maximoRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["maximo"].value.toFixed(2);
		document.getElementById("mediaRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["media"].value.toFixed(2);
		document.getElementById("acumuladoRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["acumulado"].value.toFixed(2);

	});
}
