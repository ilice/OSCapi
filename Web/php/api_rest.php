<?php

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];
$querystring = $_SERVER['QUERY_STRING'];
$request = explode('/', trim($_SERVER['PATH_INFO'],'/'));
$input = file_get_contents('php://input');

// retrieve the index and type from the path
$index = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));
$type = preg_replace('/[^a-z0-9_]+/i','',array_shift($request));


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

if($method=="POST"){
	curl_setopt($handler, CURLOPT_POST, 1);
	curl_setopt($handler, CURLOPT_POSTFIELDS, $input);
}
$response = curl_exec ($handler);  

curl_close($handler);  

?>