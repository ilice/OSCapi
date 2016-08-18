<?php
require_once 'slack_notification.php';
require_once 'cUrl.php';

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/xml; charset=UTF-8");

$querystring = $_SERVER['QUERY_STRING'];

$url = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?";

if(strlen($querystring)>0){
	$url = "$url$querystring" ;
}

$response = getHttpscUrl($url);

libxml_use_internal_errors(true);

$response_xml = simplexml_load_string($response);
$xml = explode("\n", $response);

if (!$response_xml) {
	$errors = libxml_get_errors();

	foreach ($errors as $error) {
		slack("Error al obtener la referencia catastral más cercana a las coordenadas dadas: " . trim($error->message) . " Line: $error->line" . " Column: $error->column" . " para la llamada: <$url>");
	}

	libxml_clear_errors();
}else{
	echo $response;
}


if(!$response){
	slack("Error al obtener la referencia catastral más cercana a las coordenadas dadas");
}

?>