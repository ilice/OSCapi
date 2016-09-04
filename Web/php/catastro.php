<?php
header ( "Access-Control-Allow-Origin: *" );
header ( "Content-Type: application/xml; charset=UTF-8" );

require_once 'cUrl.php';

$querystring = !empty($_SERVER['QUERY_STRING'])?$_SERVER['QUERY_STRING']:"";

if (! empty ( $querystring )) {
	$explode_querystring = explode ( "&", $querystring );
	
	foreach ( $explode_querystring as $unformated_parametro ) {
		$explode_parametro = explode ( "=", $unformated_parametro );
		$parametros [$explode_parametro [0]] = $explode_parametro [1];
	}
	
	$url = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/" . $parametros ["end_point"] . "?";
	
	foreach ( $parametros as $clave => $valor ) {
		if ($clave != "end_point") {
			$url = $url . "&" . $clave . "=" . $valor;
		}
	}
	
	$esJson = false;
	
	$response = getHttpcUrl ( $url, $esJson );
} else {
	
	slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada sin par�metros" . __FUNCTION__ ." en ". $_SERVER ['SCRIPT_NAME'] ." linea ".__LINE__ );
	$response = '<?xml version="1.0" encoding="utf-8"?>
			<consulta_coordenadas>
				<control>
					<cucoor>0</cucoor>
					<cuerr>1</cuerr>
				</control>
				<error>
					ERROR: ' . $_SERVER ['SCRIPT_NAME'] . ' Llamada sin parametros  '. __FUNCTION__ .' en '. $_SERVER ['SCRIPT_NAME'] .' linea '.__LINE__ .'
				</error>
			</consulta_coordenadas>	';
}

echo $response;
?>