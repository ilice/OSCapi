<?php

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];
$querystring = $_SERVER['QUERY_STRING'];
$request = explode('/', trim($_SERVER['PATH_INFO'],'/'));
$input = file_get_contents('php://input');
$user_agent = $_SERVER['HTTP_USER_AGENT'];

// retrieve the index and type from the path
$index = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));
$type = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));

//Para ver qué versión estoy utilizando
$curlVersion = curl_version();

$data = json_encode($_POST);


$url = "http://81.61.197.16:9200";

if(strlen($index)>0){
	$url = "$url/$index" ;
	
	if(strlen($type)>0){
		$url = "$url/$type" ;
	}
}

$url = "$url/_search" ;

if(strlen($querystring)>0){
	$url = "$url?$querystring" ;
}

$handler = curl_init($url);  

curl_setopt($handler, CURLINFO_HEADER_OUT, true);
curl_setopt($handler, CURLOPT_USERAGENT, $user_agent);

if($method=="POST"){
	curl_setopt($handler, CURLOPT_POST, 1);
	curl_setopt($handler, CURLOPT_POSTFIELDS, $input);
}

curl_setopt ($handler, CURLOPT_CONNECTTIMEOUT, 0);
$response = curl_exec ($handler);


if(curl_error($handler))
{
	error_log('ERROR:' . curl_error($handler));
	error_log("ERROR: " . htmlspecialchars(curl_error($handler)));
	
	$info = curl_getinfo($handler);
	error_log( 'INFO: Se tardó ' . $info['total_time']. ' segundos en enviar una petición a '. $info['url']);
	error_log( 'INFO: Request header ' . $info['request_header']);
	switch ($http_code = curl_getinfo($handler, CURLINFO_HTTP_CODE)) {
		case 200:  # OK
			error_log('INFO: Código HTTP 200-OK: '. $http_code);
			break;
		default:
			error_log('ERROR: Código HTTP inesperado: '. $http_code);
	}
	
}


curl_close($handler);

?>