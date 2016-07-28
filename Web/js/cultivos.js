var numeroCultivosPorPagina = 6;
var ultimoCultivoCargado = 0;
var paginaActual = 1;
var elementosEncontrados = 0;


function cargaDatos() {

	ultimoCultivoCargado = 0;
	paginaMas(ultimoCultivoCargado, numeroCultivosPorPagina);

}


function cargaCultivos(numeroCultivoInicial, numeroCultivosACargar) {

	var textoBusqueda = QueryString.search;
	var query;
	var match = textoBusqueda;
	var _all = textoBusqueda;

	if (encodeURIComponent(textoBusqueda) == "undefined") {
		query = {
			"match_all" : {}
		};
	} else {
		if (QueryString.queryType == "match") {

			query = {
				"match" : {
					_all
				}
			};
		} else {
			query = {
				"match_phrase" : {
					_all
				}
			};
		}
	}

	var data = {
		"from" : numeroCultivoInicial,
		"size" : numeroCultivosACargar,
		query

	};

	var url = "../php/api_rest.php/osc";

	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			data : JSON.stringify(data),
			type : 'POST',
			dataType : "json"
		});

	request.done(function (response, textStatus, jqXHR) {
		var hits = response["hits"]["hits"];
		var rowIndex = 0;
		document.getElementById('photoGrid').innerHTML = "";
		for (var i = 0; i < hits.length; i++) {
			if ((i % 3) == 0) {
				document.getElementById('photoGrid').innerHTML += '<div class="w3-row">';
			}

			var hit = hits[i];
			var contenido = '<div onclick="document.getElementById(\'' + hit["_id"] + '_modal\').style.display=\'block\'" class="w3-third w3-container">' +
				'<div id="' + hit["_id"] + '" class="w3-margin w3-card-8 w3-hover-opacity">' +
				'<img src="img/cultivos/' + hit["_source"]["Foto"] + '" style="width:100%"/>' +
				'<div class="w3-container">' +
				'<h4>' + hit["_source"]["Nombres Comunes"] + "</h4>" +
				'<h5 align="right"><em>' + hit["_source"]["Nombre Científico"] + '</em></h5>' +
				'</div></div></div>';

			var modal = '<div id="' + hit["_id"] + '_modal" class="w3-modal">' +
				' <div class="w3-modal-content">' +
				'<div class="w3-container">' +
				'<div class="w3-row w3-right">' +
				' <div class="w3-col w3-right">' +
				'<a href="cultivo.html?cultivo_id=' + hit["_id"] + '" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-large w3-margin-right"><i class="fa fa-binoculars"></i></a>' +
				'<a href="#" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xlarge" onclick="document.getElementById(\'' + hit["_id"] + '_modal\').style.display=\'none\'"><i class="fa fa-remove"></i></a>' +
				'</div>' +
				'</div>' +
				'<table class="w3-table w3-striped w3-bordered w3-border w3-hoverable w3-white">' +
				'<tr><td>Origen</td><td>' + hit["_source"]["Origen"] + '</td></tr>' +
				'<tr><td>Distribución</td><td>' + hit["_source"]["Distribución"] + '</td></tr>' +
				'<tr><td>Adaptación</td><td>' + hit["_source"]["Adaptación"] + '</td></tr>' +
				'<tr><td>Ciclo vegetativo</td><td>' + hit["_source"]["Ciclo vegetativo"] + '</td></tr>' +
				'<tr><td>Tipo Fotosintético</td><td>' + hit["_source"]["Tipo Fotosintético"] + '</td></tr>' +
				'<tr><td>Fotoperíodo</td><td>' + hit["_source"]["Fotoperíodo"] + '</td></tr>' +
				'<tr><td>Altitud</td><td>' + hit["_source"]["Altitud"] + '</td></tr>' +
				'<tr><td>Precipitación</td><td>' + hit["_source"]["Precipitación"] + '</td></tr>' +
				'<tr><td>Humedad ambiental</td><td>' + hit["_source"]["Humedad ambiental"] + '</td></tr>' +
				'<tr><td>Temperatura</td><td>' + hit["_source"]["Temperatura"] + '</td></tr>' +
				'<tr><td>Luz</td><td>' + hit["_source"]["Luz"] + '</td></tr>' +
				'<tr><td>Textura de suelo</td><td>' + hit["_source"]["Textura de suelo"] + '</td></tr>' +
				'<tr><td>Profundidad de suelo</td><td>' + hit["_source"]["Profundidad de suelo"] + '</td></tr>' +
				'<tr><td>Salinidad</td><td>' + hit["_source"]["Salinidad"] + '</td></tr>' +
				'<tr><td>pH</td><td>' + hit["_source"]["pH"] + '</td></tr>' +
				'<tr><td>Drenaje</td><td>' + hit["_source"]["Drenaje"] + '</td></tr>' +
				'<tr><td>Otros</td><td>' + hit["_source"]["Otros"] + '</td></tr>' +
				'</table>' +
				'</div>' +
				'</div>' +
				'</div>';

			document.getElementById('photoGrid').innerHTML += contenido;
			document.getElementById('photoGrid').innerHTML += modal;

			if (((i + 1) % 3) == 0 || (i + 1) == hits.length) {
				document.getElementById('photoGrid').innerHTML += '</div>';
			}

		}
		elementosEncontrados = response["hits"].total;
		ultimoCultivoCargado = numeroCultivoInicial + numeroCultivosACargar;
		document.getElementById('pagina').innerHTML = (ultimoCultivoCargado / numeroCultivosPorPagina) + " / " + Math.ceil((elementosEncontrados / numeroCultivosPorPagina));
	});

}

function paginaMas() {
	cargaCultivos(ultimoCultivoCargado, numeroCultivosPorPagina);

}

function paginaMenos() {
	cargaCultivos(ultimoCultivoCargado - 2 * numeroCultivosPorPagina, numeroCultivosPorPagina);
}

var QueryString = function () {
	// This function is anonymous, is executed immediately and
	// the return value is assigned to QueryString!
	var query_string = {};
	var query = window.location.search.substring(1);
	if (query.search("%22") >= 0) {
		query_string.queryType = "match_phrase";
		query_string.boolType = "or";
	} else if (query.search("%26") >= 0) {
		query_string.queryType = "match";
		query_string.boolType = "and";
	} else {
		query_string.queryType = "match";
		query_string.boolType = "or";
	}
	if (query.length > 0 && query != "search=") {
		var vars = query.split("&");
		for (var i = 0; i < vars.length; i++) {
			var pair = vars[i].split("=");
			// If first entry with this name
			if (typeof query_string[pair[0]] === "undefined") {
				query_string[pair[0]] = decodeURIComponent(pair[1]);
				// If second entry with this name
			} else if (typeof query_string[pair[0]] === "string") {
				var arr = [query_string[pair[0]], decodeURIComponent(pair[1])];
				query_string[pair[0]] = arr;
				// If third or later entry with this name
			} else {
				query_string[pair[0]].push(decodeURIComponent(pair[1]));
			}
		}
	}
	return query_string;
}
();
