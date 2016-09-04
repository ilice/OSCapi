<?php
header ( "Access-Control-Allow-Origin: *" );
header ( "Content-Type: application/xml; charset=UTF-8" );

require_once 'cUrl.php';

$querystring = $_SERVER ['QUERY_STRING'];

if (! empty ( $querystring )) {
	$explode_querystring = explode ( "&", $querystring );
	
	foreach ( $explode_querystring as $unformated_parametro ) {
		$explode_parametro = explode ( "=", $unformated_parametro );
		$parametros [$explode_parametro [0]] = $explode_parametro [1];
	}
} else {
	slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada sin parámetros" );
}

$url = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/" . $parametros ["end_point"] . "?";

foreach ( $parametros as $clave => $valor ) {
	if ($clave != "end_point") {
		$url = $url . "&" . $clave . "=" . $valor;
	}
}

$esJson = false;

$response = getHttpcUrl ( $url, $esJson );

echo $response
?>
