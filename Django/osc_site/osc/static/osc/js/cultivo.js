/**
 * 
 */
function cargaDatos() {

    addWidget('blue', 'white', "fa fa-tint",  "Precipitación");
    addWidget('red', 'white', "fa fa-eyedropper",  "Temperatura");
    addWidget('yellow', 'dark-grey', "fa fa-sun-o",  "Luz");
    addWidget('green', 'white', "fa fa-rss",  "Humedad ambiental");


    makeEditable();

	var cultivo_id = QueryString.cultivo_id;

	document.getElementById('cropId').value = cultivo_id;
	document.getElementById('propertyCropId').value = cultivo_id;
	document.getElementById('cultivo_id').value = cultivo_id;

	var url = "/osc/crops/elastic/search/";

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

						drawCrop(crop);

						document.title += crop.Nombre;
						document.getElementById("pagina").innerHTML = crop.Nombre;

						// Ficha básica del cultivo
						setValueInField(crop["Nombre"],'ficha');

						if(!(crop["Foto"] === undefined)){
						setValueInField('<img src="/static/osc/img/cultivos/'
								+ crop["Foto"] + '" style="width:100%"/>', 'imagen');}

						setValueInField('<button id="buscar_imagen" class="w3-btn w3-margin w3-dark-grey w3-center"'
								+ 'onclick="location.href=\'https://www.google.es/search?q='
								+ crop["Nombre Científico"]
								+ '&tbm=isch\'">'
								+ '<i class="fa fa-search"></i> Buscar otras imágenes en la Web'
								+ '</button>', 'buscar_imagen');


						// Observaciones
						var observaciones = crop["Otros"];
						if (!(observaciones === undefined) && observaciones.length > 0) {

							observaciones = '<div class="w3-orange w3-text-dark-grey w3-row-padding">'
									+ '<span onclick="this.parentElement.style.display=\'none\'"'
									+ 'class="w3-closebtn w3-padding">&times;</span>'
									+ '<h3>Observaciones</h3>'
									+ ' <p>'
									+ observaciones + '</p>' + '</div>';

							setValueInField(observaciones, 'observaciones');
						}

						var altitudeRequirements = crop.altitude;
						for (altitudeRequirementNumber in altitudeRequirements) {
							var altitude = altitudeRequirements[altitudeRequirementNumber];

							addMinMaxRequirementsRow("Altitud", altitude);

						}

						var pHRequirements = crop.ph;
						for (pHRequirementNumber in pHRequirements) {
							var pH = pHRequirements[pHRequirementNumber];

							addMinMaxRequirementsRow("pH", pH);

						}
						
						var latitudeRequirements = crop.latitude;
						for (latitudeRequirementsNumber in latitudeRequirements) {
							var latitude = latitudeRequirements[latitudeRequirementsNumber];

							addMinMaxRequirementsRow("Latitud", latitude);

						}

						var sunHoursRequirements = crop.sunHours;
						for (sunHoursRequirementsNumber in sunHoursRequirements){
						    var sunHours = sunHoursRequirements[sunHoursRequirementsNumber];

						    addMinMaxRequirementsRow("Sol", sunHours);
						}

						var temperatureRequirements = crop.temperature;
						for (temperatureRequirementsNumber in temperatureRequirements){
						    var temperature = temperatureRequirements[temperatureRequirementsNumber];

						    addMinMaxRequirementsRow("Temperatura", temperature);
						}

						var rainfallRequirements = crop.rainfall;
						for (rainfallRequitementNumber in rainfallRequirements){
						    var rainfall = rainfallRequirements[rainfallRequitementNumber];

						    addMinMaxRequirementsRow("Precipitaciones", rainfall);
						}

						var tags = crop.labels;
						for (tagNumber in tags){
						    addTag(tags[tagNumber]);
						    addEditableTag(tags[tagNumber]);
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

function destacaTipoFotosintetico(tipoFotosintetico) {
    document.getElementById('Tipo Fotosintético').innerHTML = tipoFotosintetico;
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

function removeRequirementsRow(id) {
	var item = document.getElementById(id);
	item.parentNode.removeChild(item);
}

function addMinMaxRequirementsRow(type, requirement)

{
	var number = document.getElementsByClassName(type).length + 1;

	var rowContainer = document.createElement("fieldset");
	rowContainer.setAttribute("id", type + "_requirement_" + number);
	rowContainer.setAttribute("class", "w3-border-0");
	document.getElementById("requirementsRows").appendChild(rowContainer);

	var removeButton = document.createElement("a");
	removeButton.setAttribute("href", "javascript:void(0)");
	removeButton.setAttribute("class", "w3-closebtn");
	removeButton.setAttribute("onclick", "removeRequirementsRow(\"" + type
			+ "_requirement_" + number + "\")");
	rowContainer.appendChild(removeButton);

	var removeButtonIcon = document.createElement("i");
	removeButtonIcon.setAttribute("class", "fa fa-remove");
	removeButton.appendChild(removeButtonIcon);

	var row = document.createElement("div");
	row.setAttribute("class", "w3-row-padding " + type);
	// row.setAttribute("id", type + "_requirement_" + number);
	rowContainer.appendChild(row);
	row.style = "margin-right: 50px;";

	// First column: Label

	var firstColumn = document.createElement("div");
	firstColumn.setAttribute("class", "w3-quarter")
	row.appendChild(firstColumn);

	var labelOfFirstColumn = document.createElement("label");
	labelOfFirstColumn.setAttribute("class",
			"w3-label w3-text-grey w3-validate");
	firstColumn.appendChild(labelOfFirstColumn);

	var labelOflabelOfFirstColumn = document.createElement("b");
	labelOfFirstColumn.appendChild(labelOflabelOfFirstColumn);

	var textOflabelOflabelOfFirstColumn = document
			.createTextNode("Restricción");
	labelOflabelOfFirstColumn.appendChild(textOflabelOflabelOfFirstColumn);

	var inputOfFirstColumn = document.createElement("input");
	inputOfFirstColumn.setAttribute("id", "measure_" + type + "_" + number);
	inputOfFirstColumn
			.setAttribute("class", "w3-input w3-border w3-light-grey");
	inputOfFirstColumn.setAttribute("name", "measure_" + type + "_" + number);
	inputOfFirstColumn.setAttribute("type", "text");
	inputOfFirstColumn.setAttribute("placeholder", "Medida");
	inputOfFirstColumn.setAttribute("list", "measures");
	if (!(type === undefined)) {
		inputOfFirstColumn.setAttribute("value", type);
	}
	firstColumn.appendChild(inputOfFirstColumn);

	// Second column: Minimum

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
	inputOfSecondColumn.setAttribute("id", "min_" + type + "_" + number);
	inputOfSecondColumn.setAttribute("class",
			"w3-input w3-border w3-light-grey");
	inputOfSecondColumn.setAttribute("name", "min_" + type + "_" + number);
	inputOfSecondColumn.setAttribute("type", "number");
	inputOfSecondColumn.setAttribute("step", "0.01");
	inputOfSecondColumn.setAttribute("placeholder", type + " mínima");
	if (!(requirement === undefined) && !(requirement.min === undefined)) {
		inputOfSecondColumn.setAttribute("value", requirement.min);
	}
	secondColumn.appendChild(inputOfSecondColumn);

	// Third column: Maximum

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
	inputOfThirdColumn.setAttribute("id", "max_" + type + "_" + number);
	inputOfThirdColumn
			.setAttribute("class", "w3-input w3-border w3-light-grey");
	inputOfThirdColumn.setAttribute("name", "max_" + type + "_" + number);
	inputOfThirdColumn.setAttribute("type", "number");
	inputOfThirdColumn.setAttribute("step", "0.01");
	inputOfThirdColumn.setAttribute("placeholder", type + " máxima");
	if (!(requirement === undefined) && !(requirement.max === undefined)) {
		inputOfThirdColumn.setAttribute("value", requirement.max);
	}
	thirdColumn.appendChild(inputOfThirdColumn);

	// Fourth column: Comments

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
	inputOfFourthColumn.setAttribute("id", "obs_" + type + "_" + number);
	inputOfFourthColumn.setAttribute("class",
			"w3-input w3-border w3-light-grey");
	inputOfFourthColumn.setAttribute("name", "obs_" + type + "_" + number);
	inputOfFourthColumn.setAttribute("type", "text");
	inputOfFourthColumn.setAttribute("placeholder",
			"Observaciones sobre la Altitud");
	if (!(requirement === undefined) && !(requirement.obs === undefined)) {
		inputOfFourthColumn.setAttribute("value", requirement.obs);
	}
	fourthColumn.appendChild(inputOfFourthColumn);
}

function updateCrop() {

	var form = document.getElementById("cropForm");
	var doc = {};
	doc["altitude"] = [];
	var cropId = form.getElementsByTagName("input").cropId.value;

	var fieldsets = document.getElementsByTagName("fieldset");
	var fieldsetNumber;
	for (fieldsetNumber = 0; fieldsetNumber < fieldsets.length; fieldsetNumber++) {
		var fieldset = fieldsets[fieldsetNumber];
		var inputs = fieldset.getElementsByTagName("input");
		var label;
		var requirement = {};
		var inputNumber;
		for (inputNumber = 0; inputNumber < inputs.length; inputNumber++) {
			var input = inputs[inputNumber];
			var type = getType(input.id);
			var value = input.value;
			if (type != "measure") {
				requirement[type] = value;
			} else {
				label = value;
			}
		}
		switch (label) {
		case "Altitud":
			label = "altitude";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		case "Latitud":
			label = "altitude";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		case "pH":
			label = "ph";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		case "Temperatura":
			label = "temperature";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		case "Precipitaciones":
			label = "rainfall";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		case "Sol":
			label = "sunHours";
			if (doc[label] === undefined) {
				doc[label] = [ requirement ];
			} else {
				doc[label].push(requirement);
			}
			break;
		default:
			break;
		}

	}

	var tags = document.getElementsByTagName("tag");
	var tagsArray = [];
	for (var tagNumber = 0; tagNumber < tags.length; tagNumber++){
	    tagsArray.push(tags[tagNumber].innerHTML);
	}
	doc["labels"] = tagsArray;


	var data = {
		doc : doc
	};
	var url = "/osc/crops/elastic/update/" + cropId + "/";

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

					document.getElementById('resultText').innerHTML = '<p><i class="fa fa-check-square-o w3-text-green"></i> ¡Estupendo! El cultivo se ha actualizado. <i class="fa fa-smile-o"></i></p>';
					document.getElementById('result').style.display = 'block';

				} else {
					document.getElementById('resultText').innerHTML = '<p>La hemos liao. '
							+ '<i class="fa fa fa-meh-o w3-text-red"></i> '
							+ ' Aquí va algo de información por si ayuda. '
							+ '<i class="fa fa-fire-extinguisher w3-text-red"></i></p>'
							+ '<h4>Datos del request a la url:</h4> '
							+ '<p>'
							+ url
							+ '</p>'
							+ '<div class="w3-panel w3-pale-blue w3-leftbar w3-border-blue">'
							+ '<pre style="white-space: pre-wrap;"><code>'
							+ JSON.stringify(data)
							+ '</code></pre>'
							+ '</div>'
							+ '<div class="w3-panel w3-pale-red w3-leftbar w3-border-red">'
							+ '<pre style="white-space: pre-wrap;"><code>'
							+ JSON.stringify(response)
							+ '</code></pre>' + '</div>';
					;
					document.getElementById('result').style.display = 'block';

				}

			});

}

function getType(id) {
	return id.split("_")[0];
}

function getRequirement(id) {
	return id.split("_")[1];
}

function getRequirementId(id) {
	return id.split("_")[2];
}

function reloadPage() {
	location.reload(true);
}

function addTag(tag){

    var tagElement = document.createElement('span');
    tagElement.setAttribute("class","w3-tag w3-light-grey w3-small w3-margin");
    tagElement.appendChild(document.createTextNode(tag));
    document.getElementById("tags").appendChild(tagElement);

}

function addEditableTag(tag){

    if(tag === undefined)
    {
        tag = document.getElementById("newTag").value;
        document.getElementById("newTag").value = "";
    }

    var tagElement = document.createElement('span');
    tagElement.setAttribute("class","w3-tag w3-light-grey w3-margin");
    tagElement.setAttribute("id","tag_" + tag);

    var removeButton = document.createElement("a");
	removeButton.setAttribute("href", "javascript:void(0)");
	//removeButton.setAttribute("class", "w3-closebtn");
	removeButton.setAttribute("class", "w3-margin-left");
	removeButton.setAttribute("onclick", "removeTag(\"tag_" + tag + "\")");

	var removeButtonIcon = document.createElement("i");
	removeButtonIcon.setAttribute("class", "fa fa-remove w3-tiny");
	removeButton.appendChild(removeButtonIcon);

	var tagText = document.createElement('tag');
	tagText.appendChild(document.createTextNode(tag));

    tagElement.appendChild(tagText);
    tagElement.appendChild(removeButton);

	document.getElementById("tagsRow").appendChild(tagElement);

}

function removeTag(tag){
	var item = document.getElementById(tag);
	item.parentNode.removeChild(item);
}

function edit(property){
    var content = document.getElementById(property).childNodes;
    var value = "";
    if(document.getElementById(property).childElementCount > 1){
        value = document.getElementById(property).childNodes[0].nodeValue;
    }else{
        value = document.getElementById(property).innerHTML;
    }
    document.getElementById('propertyRow').value = value;
    document.getElementById('editPropertyModButton').setAttribute("onclick", "updatePropertyCrop(\"" + property + "\")");
    document.getElementById('editPropertyModal').style.display='block';
}

function updatePropertyCrop(property){
    var form = document.getElementById("propertyForm");
    var value = form.getElementsByTagName("textarea").propertyRow.value;
    var doc = {};

    doc[property] = value;

    var data = {
		doc : doc
	};

	data["doc_as_upsert"] = "true";

	var url = "/osc/crops/elastic/update/" + document.getElementById("cropId").value + "/";


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

					document.getElementById('resultText').innerHTML = '<p><i class="fa fa-check-square-o w3-text-green"></i> ¡Estupendo! El cultivo se ha actualizado. <i class="fa fa-smile-o"></i></p>';
					document.getElementById('result').style.display = 'block';

				} else {
					document.getElementById('resultText').innerHTML = '<p>La hemos liao. '
							+ '<i class="fa fa fa-meh-o w3-text-red"></i> '
							+ ' Aquí va algo de información por si ayuda. '
							+ '<i class="fa fa-fire-extinguisher w3-text-red"></i></p>'
							+ '<h4>Datos del request a la url:</h4> '
							+ '<p>'
							+ url
							+ '</p>'
							+ '<div class="w3-panel w3-pale-blue w3-leftbar w3-border-blue">'
							+ '<pre style="white-space: pre-wrap;"><code>'
							+ JSON.stringify(data)
							+ '</code></pre>'
							+ '</div>'
							+ '<div class="w3-panel w3-pale-red w3-leftbar w3-border-red">'
							+ '<pre style="white-space: pre-wrap;"><code>'
							+ JSON.stringify(response)
							+ '</code></pre>' + '</div>';
					;
					document.getElementById('result').style.display = 'block';

				}

			});
}

function makeEditable(){

    var editable = 'none';
    var makeEditable = 'inline';
    if(QueryString.API_KEY == "3r1k4"){
        editable = 'inline';
        makeEditable = 'none';
    }
    var editables = document.getElementsByClassName("editable");
    for(var editableNumber = 0; editableNumber < editables.length; editableNumber++){
        editables[editableNumber].style.display = editable;
    }

    var makeEditables = document.getElementsByClassName("makeEditable");
    for(var makeEditableNumber = 0; makeEditableNumber < makeEditables.length; makeEditableNumber++){
        makeEditables[makeEditableNumber].style.display = makeEditable;
    }
}

function setValueInField(value, field) {
    if(!(value === undefined)){
	    document.getElementById(field).innerHTML = value;
	}
}

function setCropValue(field, crop){
    var value = crop[field];
    setValueInField(value, field);
}

function drawCrop(crop){
    for (cropProperty in crop)
    {
        drawCropProperty(cropProperty, crop[cropProperty]);
    }
}

function drawCropProperty(property, value){
    if(typeof value == 'string' && document.getElementById(property) != null){
        setValueInField(value, property);
    }
}

function addWidget(color, textColor, icon,  dataType){

        var widget = document.createElement('div');
        widget.setAttribute('class', 'w3-quarter');
        var container = document.createElement('div');
        container.setAttribute('class', 'w3-container w3-text-' + textColor + ' w3-margin w3-' + color);
        widget.appendChild(container);
        var bigIcon = document.createElement('p');
        bigIcon.setAttribute('class', 'w3-xxxlarge w3-margin-top w3-margin-0 ' + icon);
        container.appendChild(bigIcon);
        var text = document.createElement('p');
        text.setAttribute('style', 'height:150px; overflow:auto');
        text.setAttribute('id', dataType);
        container.appendChild(text);
        var title = document.createElement('h4');
        title.appendChild(document.createTextNode(dataType));
        container.appendChild(title);
        var editableButton = document.createElement('span');
        editableButton.setAttribute('class', 'editable w3-right');
        title.appendChild(editableButton);
        var editButton = document.createElement('a');
        editButton.setAttribute('href', 'javascript:void(0)');
        editButton.setAttribute('onclick', 'edit("'+ dataType + '")');
        editableButton.appendChild(editButton);
        var editButtonIcon = document.createElement('i');
        editButtonIcon.setAttribute('class', 'fa fa-edit w3-small');
        editButton.appendChild(editButtonIcon);

        document.getElementById('widgets').appendChild(widget);

}