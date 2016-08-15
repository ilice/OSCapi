<?php
require_once 'slack_notification.php';

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/xml; charset=UTF-8");

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];
$querystring = $_SERVER['QUERY_STRING'];
//$request = explode('/', trim($_SERVER['PATH_INFO'],'/'));
//$input = file_get_contents('php://input');

// retrieve the index and type from the path
//$index = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));
//$type = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));


$data = json_encode($_POST);


$url = "https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?";


// if(strlen($index)>0){
// 	$url = "$url/$index" ;

// 	if(strlen($type)>0){
// 		$url = "$url/$type" ;
// 	}
// }



//$url = "$url" ;

if(strlen($querystring)>0){
	$url = "$url$querystring" ;
}

$handler = curl_init($url);

curl_setopt($handler, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($handler, CURLOPT_SSL_VERIFYPEER, 0);

$response = curl_exec ($handler);

curl_close($handler);

libxml_use_internal_errors(true);

$response_xml = simplexml_load_string($response);
$xml = explode("\n", $response);

if (!$response_xml) {
	$errors = libxml_get_errors();

	foreach ($errors as $error) {
		slack("Error al obtener la referencia catastral m�s cercana a las coordenadas dadas: " . trim($error->message) . " Line: $error->line" . " Column: $error->column" . " para la llamada: <$url>");
	}

	libxml_clear_errors();
}else{
	echo $response;
}


if(!$response){
	slack("Error al obtener la referencia catastral m�s cercana a las coordenadas dadas");
}

?>