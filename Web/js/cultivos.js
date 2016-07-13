var numeroCultivosPorPagina = 6;
var ultimoCultivoCargado = 0;
var paginaActual = 1;


function cargaDatos(){
	
	var paginaInicial = true;
	paginaMas(ultimoCultivoCargado,numeroCultivosPorPagina);
	document.getElementById('pagina').innerHTML = ultimoCultivoCargado/numeroCultivosPorPagina;
	
	
}

function cargaCultivos(numeroCultivoInicial, numeroCultivosACargar){
	var url = "https://search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com/osc/_search?size="+numeroCultivosACargar+"&from="+numeroCultivoInicial;

	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});
	
	request.done(function (response, textStatus, jqXHR) {
		var hits = response["hits"]["hits"];
		document.getElementById('photoGrid').innerHTML = "";
		for(var i=0; i<hits.length; i++){
			var hit = hits[i];
			var contenido = '<div onclick="document.getElementById(\'' + hit["_id"] + '_modal\').style.display=\'block\'">' +
			'<div class="w3-third w3-container">' +
			'<div id="'+ hit["_id"] +'" class="w3-margin w3-card-8 w3-hover-opacity">' + 
			'<img src="img/cultivos/'+hit["_id"]+'.jpg" style="width:100%"/>' +
			'<div class="w3-container">' +
			'<h5><strong>' + hit["_source"]["Nombres Comunes"] + "</strong></h5>" +
			'<h5 align="right"><em>' +hit["_source"]["Nombre Científico"] +'</em></h5>' +
			'</div></div></div>' +
			'</div>';
			
			
			var modal = '<div id="'+ hit["_id"] +'_modal" class="w3-modal">' +
			' <div class="w3-modal-content">' +
			'<div class="w3-container">' +
			'<span onclick="document.getElementById(\'' + hit["_id"] + '_modal\').style.display=\'none\'" ' +
			'class="w3-closebtn">&times;</span>' +
			'<table class="w3-table w3-striped w3-bordered w3-border w3-hoverable w3-white">' +
			'<tr><td>Origen</td><td>'+ hit["_source"]["Origen"] +'</td></tr>' +
			'<tr><td>Distribución</td><td>'+ hit["_source"]["Distribución"] +'</td></tr>' +
			'<tr><td>Adaptación</td><td>'+ hit["_source"]["Adaptación"] +'</td></tr>' +
			'<tr><td>Ciclo vegetativo</td><td>'+ hit["_source"]["Ciclo vegetativo"] +'</td></tr>' +
			'<tr><td>Tipo Fotosintético</td><td>'+ hit["_source"]["Tipo Fotosintético"] +'</td></tr>' +
			'<tr><td>Fotoperíodo</td><td>'+ hit["_source"]["Fotoperíodo"] +'</td></tr>' +
			'<tr><td>Altitud</td><td>'+ hit["_source"]["Altitud"] +'</td></tr>' +
			'<tr><td>Precipitación</td><td>'+ hit["_source"]["Precipitación"] +'</td></tr>' +
			'<tr><td>Humedad ambiental</td><td>'+ hit["_source"]["Humedad ambiental"] +'</td></tr>' +
			'<tr><td>Temperatura</td><td>'+ hit["_source"]["Temperatura"] +'</td></tr>' +
			'<tr><td>Luz</td><td>'+ hit["_source"]["Luz"] +'</td></tr>' +
			'<tr><td>Textura de suelo</td><td>'+ hit["_source"]["Textura de suelo"] +'</td></tr>' +
			'<tr><td>Profundidad de suelo</td><td>'+ hit["_source"]["Profundidad de suelo"] +'</td></tr>' +
			'<tr><td>Salinidad</td><td>'+ hit["_source"]["Salinidad"] +'</td></tr>' +
			'<tr><td>pH</td><td>'+ hit["_source"]["pH"] +'</td></tr>' +
			'<tr><td>Drenaje</td><td>'+ hit["_source"]["Drenaje"] +'</td></tr>' +
			'<tr><td>Otros</td><td>'+ hit["_source"]["Otros"] +'</td></tr>' +
			'</table>' +
			'</div>' +
			'</div>' +
			'</div>';
			


			document.getElementById('photoGrid').innerHTML += contenido;
			document.getElementById('photoGrid').innerHTML += modal;
			
		}
		ultimoCultivoCargado = numeroCultivoInicial + numeroCultivosACargar;
	});
}

function paginaMas(){
	cargaCultivos(ultimoCultivoCargado, numeroCultivosPorPagina);
	document.getElementById('pagina').innerHTML = ultimoCultivoCargado/numeroCultivosPorPagina;
}

function paginaMenos(){
	cargaCultivos(ultimoCultivoCargado-2*numeroCultivosPorPagina, numeroCultivosPorPagina);
	document.getElementById('pagina').innerHTML = ultimoCultivoCargado/numeroCultivosPorPagina;
}

function pagina(numeroPagina){
	cargaCultivos(numeroPagina*numeroCultivosPorPagina, numeroCultivosPorPagina);
	
}
