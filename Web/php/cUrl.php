<?php

function postHttpcUrl($url, $input) {
	$user_agent = $_SERVER ['HTTP_USER_AGENT'];

	$handler = curl_init ( $url );

	curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
	curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
	curl_setopt ( $handler, CURLOPT_POST, 1 );
	curl_setopt ( $handler, CURLOPT_POSTFIELDS, $input );
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );

	$response = curl_exec ( $handler );

	if (curl_error ( $handler )) {
		$info = curl_getinfo ( $handler );
		$http_code = curl_getinfo ( $handler, CURLINFO_HTTP_CODE );
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . htmlspecialchars ( curl_error ( $handler ) ) . 'Se tardó ' . $info ['total_time'] . ' segundos en enviar una petición a ' . $info ['url'] . 'con Request header ' . $info ['request_header'] . 'y Código HTTP inesperado: ' . $http_code . " en getHttpcUrl($url)" );
	} elseif (isset ( json_decode ( $response, true ) ["error"] )) {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " - " . $response . " para la url: " . $url . " y el input: " . $input);
	}

	curl_close ( $handler );

	return $response;
}

function getHttpcUrl($url) {
	$user_agent = $_SERVER ['HTTP_USER_AGENT'];

	$handler = curl_init ( $url );

	curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
	curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );

	$response = curl_exec ( $handler );

	if (curl_error ( $handler )) {
		$info = curl_getinfo ( $handler );
		$http_code = curl_getinfo ( $handler, CURLINFO_HTTP_CODE );
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . htmlspecialchars ( curl_error ( $handler ) ) . 'Se tardó ' . $info ['total_time'] . ' segundos en enviar una petición a ' . $info ['url'] . 'con Request header ' . $info ['request_header'] . 'y Código HTTP inesperado: ' . $http_code . " en getHttpcUrl($url)" );
	}elseif (isset ( json_decode ( $response, true ) ["error"] )) {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " - " . $response . " para la url: " . $url);
	}

	curl_close ( $handler );

	$response_json = json_decode ( utf8_encode ( $response ), true );

	$error = json_last_error_msg ();
	if (strcmp ( $error, "No error" ) != 0) {
		slack ( "Error: " . $error . " para la llamada: <$url>" );
	}

	if (! $response) {
		slack ( "Error en getHttpcUrl($url)" );
	}

	return $response_json;
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
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " - " . $response . " para la url: " . $url . " y el input: " . $input);
	}

	curl_close ( $handler );

	return $response;
}

function getHttpscUrl($url) {
	
	$handler = curl_init($url);  

	curl_setopt($handler, CURLOPT_SSL_VERIFYPEER, 0);
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	$response = curl_exec ($handler);  


	curl_close($handler); 
	
	return $response;
}
?>