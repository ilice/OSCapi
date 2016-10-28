/**
 * 
 */
function cargaDatos() {

	var cultivo_id = QueryString.cultivo_id;

	var url = "php/django_server_wrapper.php/osc/crops/elastic" + cultivo_id;

	var data = {
		"query" : {
			"constant_score" : {
				"filter" : {
					"term" : {
						"_id" : cultivo_id
					}
				}
			}
		}
	};

	var request = jQuery.ajax({
		crossDomain : true,
		url : url,
		type : 'POST',
		dataType : "json",
		data : JSON.stringify(data)
	});

	request
			.done(function(response, textStatus, jqXHR) {
				if (response.status == "SUCCESS") {
					var result = response.result.crops;
					for (crop in result) {
						var cropId = result[crop]._id;
						crop = result[crop]._source;
						document.title += crop.Nombre;
						document.getElementById("pagina").innerHTML = crop.Nombre;

						// Widgets iniciales: como el texto es largo se recorta
						// y
						// ponen unos puntos para ver más
						document.getElementById("precipitacion").innerHTML = recorta(
								"precipitacion", crop["Precipitación"], 120);
						document.getElementById("temperatura").innerHTML = recorta(
								"temperatura", crop["Temperatura"], 120);
						document.getElementById("sol").innerHTML = recorta(
								"sol", crop["Luz"], 120);
						document.getElementById("humedad_ambiental").innerHTML = recorta(
								"humedad_ambiental", crop["Humedad ambiental"],
								120);

						// Ficha básica del cultivo
						document.getElementById('ficha').innerHTML = crop["Nombre"];
						document.getElementById('nombre').innerHTML = crop["Nombre"];
						document.getElementById('nombre_cientifico').innerHTML = crop["Nombre Científico"];
						document.getElementById('familia').innerHTML = crop["Familia"];
						document.getElementById('nombres_comunes').innerHTML = crop["Nombres Comunes"];
						document.getElementById('imagen').innerHTML = '<img src="img/cultivos/'
								+ crop["Foto"] + '" style="width:100%"/>';

						document.getElementById('buscar_imagen').innerHTML = '<button id="buscar_imagen" class="w3-btn w3-margin w3-dark-grey w3-center"'
								+ 'onclick="location.href=\'https://www.google.es/search?q='
								+ crop["Nombre Científico"]
								+ '&tbm=isch\'">'
								+ '<i class="fa fa-search"></i> Buscar otras imágenes en la Web'
								+ '</button>';

						// Ficha sobre origen y distribución
						document.getElementById('origen').innerHTML = crop["Origen"];
						document.getElementById('distribucion').innerHTML = crop["Distribución"];
						document.getElementById('adaptacion').innerHTML = crop["Adaptación"];
						document.getElementById('altitud').innerHTML = crop["Altitud"];

						// Ficha sobre los periodos
						document.getElementById('ciclo_vegetativo').innerHTML = recorta(
								"ciclo_vegetativo", crop["Ciclo vegetativo"],
								35);
						document.getElementById('fotoperiodo').innerHTML = recorta(
								"fotoperiodo", crop["Fotoperíodo"], 35);
						destacaTipoFotosintetico(crop["Tipo Fotosintético"]);

						// Observaciones
						var observaciones = crop["Otros"];
						if (observaciones.length > 0) {

							observaciones = '<div class="w3-orange w3-text-dark-grey w3-row-padding">'
									+ '<span onclick="this.parentElement.style.display=\'none\'"'
									+ 'class="w3-closebtn w3-padding">&times;</span>'
									+ '<h3>Observaciones</h3>'
									+ ' <p>'
									+ observaciones + '</p>' + '</div>';

							document.getElementById('observaciones').innerHTML = observaciones;
						}

						// Suelo
						document.getElementById('textura').innerHTML = crop["Textura de suelo"];
						document.getElementById('profundidad').innerHTML = crop["Profundidad de suelo"];
						document.getElementById('drenaje').innerHTML = crop["Drenaje"];

						document.getElementById('salinidad').innerHTML = crop["Salinidad"];
						document.getElementById('ph').innerHTML = crop["pH"];

						var id = crop.Foto.substring(0, crop.Foto.indexOf('.'));
						document.getElementById('cropId').value = id;

						var altitudeRequirements = crop.altitude;
						for (altitudeRequirementNumber in altitudeRequirements) {
							var altitude = altitudeRequirements[altitudeRequirementNumber];

							addMinMaxRequirementsRow("Altitud", altitude);

						}

					}
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
	var tipoCamelCase = tipo.substr(0, 1).toUpperCase() + tipo.substr(1);

	var modal = '<div id="' + tipo + '_modal" class="w3-modal">'
			+ ' <div class="w3-modal-content">'
			+ ' <div class="w3-container w3-text-grey">'
			+ ' <span onclick="document.getElementById(\'' + tipo
			+ '_modal\').style.display=\'none\'" '
			+ '  class="w3-closebtn">&times;</span> ' + '  <p><h4>'
			+ tipoCamelCase + ':</h4> ' + texto + '</p>' + '  </div> '
			+ '  </div> ' + '  </div>';

	if (texto.length > caracteres) {
		recorte = recorte
				+ '<span class="w3-closebtn" onclick="document.getElementById(\''
				+ tipo + '_modal\').style.display=\'block\'"">...</span>'
				+ modal;
	}

	return recorte;
}

function destacaTipoFotosintetico(tipoFotosintetico) {
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

function removeRequirementsRow(id){
	var item = document.getElementById(id);
	item.parentNode.removeChild(item);
}

function addMinMaxRequirementsRow(type, requirement)

{
	var number = document.getElementsByClassName(type).length + 1;

	var rowContainer = document.createElement("div");
	rowContainer.setAttribute("id", type + "_requirement_" + number);
	document.getElementById("requirementsRows").appendChild(rowContainer);
	
	var removeButton = document.createElement("a");
	removeButton.setAttribute("href", "javascript:void(0)");
	removeButton.setAttribute("class", "w3-closebtn");
	removeButton.setAttribute("onclick","removeRequirementsRow(\"" + type + "_requirement_" + number + "\")");
	rowContainer.appendChild(removeButton);
	
	var removeButtonIcon = document.createElement("i");
	removeButtonIcon.setAttribute("class", "fa fa-remove");
	removeButton.appendChild(removeButtonIcon);
	
	
	
	var row = document.createElement("div");
	row.setAttribute("class", "w3-row-padding " + type);
	//row.setAttribute("id", type + "_requirement_" + number);
	rowContainer.appendChild(row);
	row.style = "margin-right: 50px;";
	
	
	
	
	
	
	//First column: Label

	var firstColumn = document.createElement("div");
	firstColumn.setAttribute("class", "w3-quarter")
	row.appendChild(firstColumn);
	
	var requirementName = document.createElement("h3");
	requirementName.setAttribute("class", "w3-text-right");
	firstColumn.appendChild(requirementName);

	var nameLabelText = document.createTextNode(type);
	requirementName.appendChild(nameLabelText);
	
	
	
	
	
	//Second column: Minimum

	var secondColumn = document.createElement("div");
	secondColumn.setAttribute("class", "w3-quarter");
	row.appendChild(secondColumn);

	var labelOfSecondColumn = document.createElement("label");
	labelOfSecondColumn.setAttribute("class",
			"w3-label w3-text-grey w3-validate");
	secondColumn.appendChild(labelOfSecondColumn);

	var labelOflabelOfSecondColumn = document.createElement("b");
	labelOfSecondColumn.appendChild(labelOflabelOfSecondColumn);

	var textOflabelOflabelOfSecondColumn = document.createTextNode("Mínima");
	labelOflabelOfSecondColumn.appendChild(textOflabelOflabelOfSecondColumn);

	var inputOfSecondColumn = document.createElement("input");
	inputOfSecondColumn.setAttribute("id", "min_" + type + "_"
			+ number);
	inputOfSecondColumn.setAttribute("class",
			"w3-input w3-border w3-light-grey");
	inputOfSecondColumn.setAttribute("name", "min_" + type + "_"
			+ number);
	inputOfSecondColumn.setAttribute("type", "number");
	inputOfSecondColumn.setAttribute("placeholder", type + " mínima");
	if (!(requirement=== undefined) &&!(requirement.min === undefined)) {
		inputOfSecondColumn.setAttribute("value", requirement.min);
	}
	secondColumn.appendChild(inputOfSecondColumn);
	
	
	//Third column: Maximum

	var thirdColumn = document.createElement("div");
	thirdColumn.setAttribute("class", "w3-quarter");
	row.appendChild(thirdColumn);

	var labelOfThirdColumn = document.createElement("label");
	labelOfThirdColumn.setAttribute("class",
			"w3-label w3-text-grey w3-validate");
	thirdColumn.appendChild(labelOfThirdColumn);

	var labelOflabelOfThirdColumn = document.createElement("b");
	labelOfThirdColumn.appendChild(labelOflabelOfThirdColumn);

	var textOflabelOflabelOfThirdColumn = document.createTextNode("Máxima");
	labelOflabelOfThirdColumn.appendChild(textOflabelOflabelOfThirdColumn);

	var inputOfThirdColumn = document.createElement("input");
	inputOfThirdColumn.setAttribute("id", "max_" + type + "_"
			+ number);
	inputOfThirdColumn
			.setAttribute("class", "w3-input w3-border w3-light-grey");
	inputOfThirdColumn.setAttribute("name", "max_" + type +"_"
			+ number);
	inputOfThirdColumn.setAttribute("type", "number");
	inputOfThirdColumn.setAttribute("placeholder", type + " máxima");
	if (!(requirement=== undefined) &&!(requirement.max === undefined)) {
		inputOfThirdColumn.setAttribute("value", requirement.max);
	}
	thirdColumn.appendChild(inputOfThirdColumn);
	
	//Fourth column: Comments

	var fourthColumn = document.createElement("div");
	fourthColumn.setAttribute("class", "w3-quarter");
	row.appendChild(fourthColumn);

	var labelOfFourthColumn = document.createElement("label");
	labelOfFourthColumn.setAttribute("class",
			"w3-label w3-text-grey w3-validate");
	fourthColumn.appendChild(labelOfFourthColumn);

	var labelOflabelOfFourthColumn = document.createElement("b");
	labelOfFourthColumn.appendChild(labelOflabelOfFourthColumn);

	var textOflabelOflabelOfFourthColumn = document
			.createTextNode("Observaciones");
	labelOflabelOfFourthColumn.appendChild(textOflabelOflabelOfFourthColumn);

	var inputOfFourthColumn = document.createElement("input");
	inputOfFourthColumn.setAttribute("id", "obs_" + type  
			+ number);
	inputOfFourthColumn.setAttribute("class",
			"w3-input w3-border w3-light-grey");
	inputOfFourthColumn.setAttribute("name", "obs_" + type
			+ number);
	inputOfFourthColumn.setAttribute("type", "text");
	inputOfFourthColumn.setAttribute("placeholder",
			"Observaciones sobre la Altitud");
	if (!(requirement=== undefined) &&!(requirement.obs === undefined)) {
		inputOfFourthColumn.setAttribute("value", requirement.obs);
	}
	fourthColumn.appendChild(inputOfFourthColumn);
}

function updateCrop(form) {
    
    for(element in form)
    {
    	var id = form[element].id;
    	var requirement = getRequirement(id);
    	var type = getType(id);
    	var value = form[element].value;
    	
    }
}

function getType(id){
	return id.split("_")[0];
}

function getRequirement(id){
	return id.split("_")[1];
}

function reloadPage(){
	location.reload(true);
}