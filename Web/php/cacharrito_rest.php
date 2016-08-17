<?php
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'slack_notification.php';

$querystring = $_SERVER ['QUERY_STRING'];
$parametros = array ();

if (! empty ( $querystring )) {
	$explode_querystring = explode ( "&", $querystring );
	
	foreach ( $explode_querystring as $unformated_parametro ) {
		$explode_parametro = explode ( "=", $unformated_parametro );
		$parametros [$explode_parametro [0]] = $explode_parametro [1];
	}
	
	echo doGet ( $parametros );
} else {
	// slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada interna a cacharrito_rest sin parámetros" );
	echo error;
}
function doGet($parametros) {
	$imei = ! empty ( $parametros ["IMEI"] ) ? $parametros ["IMEI"] : NULL;
	$sensor = ! empty ( $parametros ["Sensor"] ) ? $parametros ["Sensor"] : NULL;
	$valor = ($parametros ["Valor"]==="0"||$parametros ["Valor"]) ? $parametros ["Valor"] : NULL;
	$latitud = ! empty ( $parametros ["Latitud"] ) ? $parametros ["Latitud"] : NULL;
	$longitud = ! empty ( $parametros ["Longitud"] ) ? $parametros ["Longitud"] : NULL;
	
	$fecha = date ( "Y-m-d\TH:i" );
	$id = $fecha . "-" . $imei;
	
	$url = "http://81.61.197.16:9200/osc_station/osc_station_record/" . $id;
	
	if ($sensor != NULL) {
		$input = '{"IMEI" : ' . $imei . ', "' . $sensor . '" : ' . $valor . '}';
	} elseif ($latitud != NULL && $longitud != NULL) {
		$input = '{"IMEI" : ' . $imei . ', "lat_lon": {"lon" : ' . $longitud . ', "lat" : ' . $latitud . '}}';
	} else {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " en los parámetros del cacharrito" );
		;
	}
	
	putHttpcUrl ( $url, $input );
}
function putHttpcUrl($url, $input) {
	$user_agent = $_SERVER ['HTTP_USER_AGENT'];
	
	$handler = curl_init ( $url );
	
	curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
	curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
	curl_setopt ( $handler, CURLOPT_CUSTOMREQUEST, 'PUT' );
	curl_setopt ( $handler, CURLOPT_POSTFIELDS, $input );
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );
	
	$response = curl_exec ( $handler );
	
	if (curl_error ( $handler )) {
		$info = curl_getinfo ( $handler );
		$http_code = curl_getinfo ( $handler, CURLINFO_HTTP_CODE );
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . htmlspecialchars ( curl_error ( $handler ) ) . 'Se tardó ' . $info ['total_time'] . ' segundos en enviar una petición a ' . $info ['url'] . 'con Request header ' . $info ['request_header'] . 'y Código HTTP inesperado: ' . $http_code . " en getHttpcUrl($url)" );
	} elseif (isset ( json_decode ( $response, true ) ["error"] )) {
		slack ( "ERROR: " . $response . " para el input: " . $input);
	}
	
	curl_close ( $handler );
	
	return $response;
}

?>