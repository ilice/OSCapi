<?php

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

require_once 'slack_notification.php';
require_once 'cUrl.php';
$config = include 'config.php';

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];
$querystring = !empty($_SERVER['QUERY_STRING'])?$_SERVER['QUERY_STRING']:"";
$request = explode('/', trim(empty($_SERVER['PATH_INFO'])?"":$_SERVER['PATH_INFO'],'/'));
$input = file_get_contents('php://input');

$url = $GLOBALS ['config'] ['quijoteServerEndPoint'];

// retrieve the index and type from the path
$index = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));
$type = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));
$element = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));

if(strlen($index)>0){
	$url = "$url/$index" ;
	if(strlen($type)>0){
		$url = "$url/$type" ;
		if(strlen($element)>0){
			$url = "$url/$element" ;
		}
	}
}

if(strlen($querystring)>0){
	$url = "$url?$querystring" ;
}

if($method=="GET"){
	echo getHttpcUrl($url);
}elseif ($method == "POST"){
	echo postHttpcUrl($url, $input);
}else{
	slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " M�todo no implementado " . $method . "- para la url: " . $url . " y el input: " . $input);
}

?>