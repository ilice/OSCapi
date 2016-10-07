<?php 
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

require_once 'slack_notification.php';
require_once 'cUrl.php';
$config = include 'config.php';

$querystring = !empty($_SERVER['QUERY_STRING'])?$_SERVER['QUERY_STRING']:"";

$url = $GLOBALS ['config'] ['googleMapsElevationEndpoint'];

if(strlen($querystring)>0){
	$url = "$url&$querystring";
}else{
	slack ( "ERROR: llamada sin parámetros " . __FUNCTION__ ." en ". $_SERVER ['SCRIPT_NAME'] ." línea ".__LINE__);
}

$response = getHttpscUrl($url);

echo $response;

?>