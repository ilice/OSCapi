var numeroCultivosPorPagina = 6;
var ultimoCultivoCargado = 0;
var paginaActual = 1;
var elementosEncontrados = 0;


function cargaDatos() {

	ultimoCultivoCargado = 0;
	paginaMas(ultimoCultivoCargado, numeroCultivosPorPagina);

}


function cargaCultivos(numeroCultivoInicial, numeroCultivosACargar) {

	var altitud = QueryString.altitud;
	var textoBusqueda = QueryString.search;
	var query;
	var match = textoBusqueda;
	var _all = textoBusqueda;

	if (encodeURIComponent(altitud) != "undefined"){
		query = {
				"constant_score" : {
		            "filter" : {
		                "bool": {
		                "must": [
		                   {"range" : {
		                    "altitude.min" : {
		                        "lte"  : altitud
		                    }
		                }},
		                {"range" : {
		                    "altitude.max" : {
		                        "gte" : altitud
		                    }
		                }}
		                
		                ]
		                }
		            }
		        }
		};
	} else if (encodeURIComponent(textoBusqueda) == "undefined") {
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

	var url = "/crops/elastic/search/";

	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			data : JSON.stringify(data),
			type : 'POST',
			dataType : "json"
		});

	request.done(function (response, textStatus, jqXHR) {
		if (response.status == "SUCCESS") {
			
			
		var crops = response.result.crops;
		var rowIndex = 0;
		document.getElementById('photoGrid').innerHTML = "";
		for (cropNumber in crops) {
			var crop = crops[cropNumber]["_source"];
			var id = crops[cropNumber]._id;
			
			if ((cropNumber % 3) == 0) {
				document.getElementById('photoGrid').innerHTML += '<div class="w3-row">';
			}

			var contenido = '<a style="text-decoration:none;" ga-on="click" ga-event-category="Interactions" ga-event-action="click" ga-event-label="Crop details"' +
				'href="/cultivo?cultivo_id=' + id + '" target="_blank" class="w3-third w3-container">' +
				'<div id="' + id + '" class="w3-margin w3-card-8 w3-hover-opacity">' +
				'<img src="/static/osc/img/cultivos/' + crop.Foto + '" style="width:100%"/>' +
				'<div class="w3-container">' +
				'<h4>' + crop["Nombres Comunes"] + "</h4>" +
				'<h5 align="right"><em>' + crop["Nombre Científico"] + '</em></h5>' +
				'</div></div></a>';

			document.getElementById('photoGrid').innerHTML += contenido;

			if (((cropNumber + 1) % 3) == 0 || (cropNumber + 1) == crops.length) {
				document.getElementById('photoGrid').innerHTML += '</div>';
			}

		}
		elementosEncontrados = response.result.total;
		document.getElementById('cultivo_id').value = response.result.total + 1;
		ultimoCultivoCargado = numeroCultivoInicial + numeroCultivosACargar;
		document.getElementById('pagina').innerHTML = (ultimoCultivoCargado / numeroCultivosPorPagina) + " / " + Math.ceil((elementosEncontrados / numeroCultivosPorPagina));
	}});

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
	
	//El objeto window representa la ventana del navegador abierta
	//Location contiene la información de la URL de la ventana
	//Search devuelve desde la ? incluida, hacemos el substring(1) para quitar la ?
	var query = window.location.search.substring(1);
	
	
	if (query.search("%22") >= 0) {
		//Buscamos si hay algunas comillas (") ya que en este 
		//caso buscamos exactamente los términos que nos llegan
		//y en el orden que nos llegan
		//https://www.elastic.co/guide/en/elasticsearch/guide/current/phrase-matching.html
		query_string.queryType = "match_phrase";
		query_string.boolType = "or";
	} else if (query.search("%26") >= 0) {
		//Si hay algún & establecemos que queremos buscar con ese operador
		query_string.queryType = "match";
		query_string.boolType = "and";
	} else {
		//Y si no hacemos una búsqueda normal en la que aparezcan 
		//todos los resultados que contengan algunos de los términos de búsqueda
		query_string.queryType = "match";
		query_string.boolType = "or";
	}
	
	if (query.length > 0 && query != "search=") {
		//Si la query tiene algo y no es solo "search=" (esto pasa cuando
		//limpias el buscador y le das a la lupa, que sigue dejando la palabra search
		//TODO mejor que cuando no haya cosas que buscar no ponga el "search=" y la query llegue vacía
		
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

