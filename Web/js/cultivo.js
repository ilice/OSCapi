/**
 * 
 */
function cargaDatos() {

	var cultivo_id = QueryString.cultivo_id;

	var url = "../php/api_rest.php/osc?q=_id:" + cultivo_id;

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		type : 'GET',
		dataType : "json"
	});

	request
			.done(function(response, textStatus, jqXHR) {
				var hits = response["hits"]["hits"];

				for (var i = 0; i < hits.length; i++) {

					var hit = hits[i];
					
					document.title += hit["_source"]["Nombre"];

					document.getElementById("pagina").innerHTML = hit["_source"]["Nombre"];
					
					//Widgets iniciales: como el texto es largo se recorta y ponen unos puntos para ver más
					document.getElementById("precipitacion").innerHTML = recorta(
							"precipitacion", hit["_source"]["Precipitación"], 120);
					document.getElementById("temperatura").innerHTML = recorta(
							"temperatura", hit["_source"]["Temperatura"], 120);
					document.getElementById("sol").innerHTML = recorta(
							"sol", hit["_source"]["Luz"], 120);
					document.getElementById("humedad_ambiental").innerHTML = recorta(
							"humedad_ambiental",
							hit["_source"]["Humedad ambiental"], 120);

					//Ficha básica del cultivo
					document.getElementById('ficha').innerHTML = hit["_source"]["Nombre"];
					document.getElementById('nombre').innerHTML = hit["_source"]["Nombre"];
					document.getElementById('nombre_cientifico').innerHTML = hit["_source"]["Nombre Científico"];
					document.getElementById('familia').innerHTML = hit["_source"]["Familia"];
					document.getElementById('nombres_comunes').innerHTML = hit["_source"]["Nombres Comunes"];
					document.getElementById('imagen').innerHTML = '<img src="img/cultivos/'
							+ hit["_source"]["Foto"] + '" style="width:100%"/>';

					document.getElementById('buscar_imagen').innerHTML = '<button id="buscar_imagen" class="w3-btn w3-margin w3-dark-grey w3-center"'
							+ 'onclick="location.href=\'https://www.google.es/search?q='
							+ hit["_source"]["Nombre Científico"]
							+ '&tbm=isch\'">'
							+ '<i class="fa fa-search"></i> Buscar otras imágenes en la Web'
							+ '</button>';

					//Ficha sobre origen y distribución
					document.getElementById('origen').innerHTML = hit["_source"]["Origen"];
					document.getElementById('distribucion').innerHTML = hit["_source"]["Distribución"];
					document.getElementById('adaptacion').innerHTML = hit["_source"]["Adaptación"];
					document.getElementById('altitud').innerHTML = hit["_source"]["Altitud"];
					
					
					//Ficha sobre los periodos
					document.getElementById('ciclo_vegetativo').innerHTML = recorta("ciclo_vegetativo", hit["_source"]["Ciclo vegetativo"], 35);
					document.getElementById('fotoperiodo').innerHTML = recorta("fotoperiodo", hit["_source"]["Fotoperíodo"], 35);
					destacaTipoFotosintetico(hit["_source"]["Tipo Fotosintético"]);

					//Observaciones
					var observaciones = hit["_source"]["Otros"];
					if(observaciones.length > 0){
						
						observaciones = '<div class="w3-orange w3-text-dark-grey w3-row-padding">' +
							'<span onclick="this.parentElement.style.display=\'none\'"' +
							'class="w3-closebtn w3-padding">&times;</span>' +
							'<h3>Observaciones</h3>' +
							' <p>' + observaciones + '</p>' +
							'</div>';
					
						document.getElementById('observaciones').innerHTML = observaciones;
					}

					//Suelo
					document.getElementById('textura').innerHTML = hit["_source"]["Textura de suelo"];
					document.getElementById('profundidad').innerHTML = hit["_source"]["Profundidad de suelo"];
					document.getElementById('drenaje').innerHTML = hit["_source"]["Drenaje"];

					document.getElementById('salinidad').innerHTML = hit["_source"]["Salinidad"];
					document.getElementById('ph').innerHTML = hit["_source"]["pH"];

				}

			});

}

var QueryString = function() {
	// This function is anonymous, is executed immediately and
	// the return value is assigned to QueryString!
	var query_string = {};

	// El objeto window representa la ventana del navegador abierta
	// Location contiene la información de la URL de la ventana
	// Search devuelve desde la ? incluida, hacemos el substring(1) para quitar
	// la ?
	var query = window.location.search.substring(1);

	if (query.search("%22") >= 0) {
		// Buscamos si hay algunas comillas (") ya que en este
		// caso buscamos exactamente los términos que nos llegan
		// y en el orden que nos llegan
		// https://www.elastic.co/guide/en/elasticsearch/guide/current/phrase-matching.html
		query_string.queryType = "match_phrase";
		query_string.boolType = "or";
	} else if (query.search("%26") >= 0) {
		// Si hay algún & establecemos que queremos buscar con ese operador
		query_string.queryType = "match";
		query_string.boolType = "and";
	} else {
		// Y si no hacemos una búsqueda normal en la que aparezcan
		// todos los resultados que contengan algunos de los términos de
		// búsqueda
		query_string.queryType = "match";
		query_string.boolType = "or";
	}

	if (query.length > 0 && query != "search=") {
		// Si la query tiene algo y no es solo "search=" (esto pasa cuando
		// limpias el buscador y le das a la lupa, que sigue dejando la palabra
		// search
		// TODO mejor que cuando no haya cosas que buscar no ponga el "search="
		// y la query llegue vacía

		var vars = query.split("&");
		for (var i = 0; i < vars.length; i++) {
			var pair = vars[i].split("=");
			// If first entry with this name
			if (typeof query_string[pair[0]] === "undefined") {
				query_string[pair[0]] = decodeURIComponent(pair[1]);
				// If second entry with this name
			} else if (typeof query_string[pair[0]] === "string") {
				var arr = [ query_string[pair[0]], decodeURIComponent(pair[1]) ];
				query_string[pair[0]] = arr;
				// If third or later entry with this name
			} else {
				query_string[pair[0]].push(decodeURIComponent(pair[1]));
			}
		}
	}
	return query_string;
}();

function recorta(tipo, texto, caracteres) {
	var recorte = texto.substring(0, 120);
	var tipoCamelCase = tipo.substr( 0, 1 ).toUpperCase() + tipo.substr( 1 );

	var modal = '<div id="'+ tipo+ '_modal" class="w3-modal">'
			+ ' <div class="w3-modal-content">'
			+ ' <div class="w3-container w3-text-grey">'
			+ ' <span onclick="document.getElementById(\'' + tipo
			+ '_modal\').style.display=\'none\'" '
			+ '  class="w3-closebtn">&times;</span> ' + '  <p><h4>'+ tipoCamelCase +':</h4> '
			+ texto + '</p>' + '  </div> ' + '  </div> ' + '  </div>';

	if (texto.length > caracteres) {
		recorte = recorte
				+ '<span class="w3-closebtn" onclick="document.getElementById(\''
				+ tipo + '_modal\').style.display=\'block\'"">...</span>'
				+ modal;
	}

	return recorte;
}

function destacaTipoFotosintetico(tipoFotosintetico){
	switch (tipoFotosintetico) {
	case "C3":
		document.getElementById("c3").style.opacity = 1;
		document.getElementById("tarjeta_c3").className = "w3-card-8 w3-hover-opacity";
		document.getElementById("c4").style.opacity = 0.2;
		document.getElementById("tarjeta_c4").className = "w3-card-2";
		document.getElementById("cam").style.opacity = 0.2;
		document.getElementById("tarjeta_cam").className = "w3-card-2";
		break;
	case "C4":
		document.getElementById("c3").style.opacity = 0.2;
		document.getElementById("tarjeta_c3").className = "w3-card-2";
		document.getElementById("c4").style.opacity = 1;
		document.getElementById("tarjeta_c4").className = "w3-card-8 w3-hover-opacity";
		document.getElementById("cam").style.opacity = 0.2;
		document.getElementById("tarjeta_cam").className = "w3-card-2";
		break;
	case "CAM":
		document.getElementById("c3").style.opacity = 0.2;
		document.getElementById("tarjeta_c3").className = "w3-card-2";
		document.getElementById("c4").style.opacity = 0.2;
		document.getElementById("tarjeta_c4").className = "w3-card-2";
		document.getElementById("cam").style.opacity = 1;
		document.getElementById("tarjeta_cam").className = "w3-card-8 w3-hover-opacity";
		break;
	default:
		document.getElementById("c3").style.opacity = 0.2;
		document.getElementById("c4").style.opacity = 0.2;
		document.getElementById("cam").style.opacity = 0.2;

	}
}