<?php 
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

require_once 'slack_notification.php';
require_once 'cUrl.php';

$querystring = !empty($_SERVER['QUERY_STRING'])?$_SERVER['QUERY_STRING']:"";

$url = "https://maps.googleapis.com/maps/api/elevation/json?key=AIzaSyB-K-4XmS9a5ItnkrqJSS9070qAeRuXt6M";

if(strlen($querystring)>0){
	$url = "$url&$querystring";
}else{
	slack ( "ERROR: llamada sin par�metros " . __FUNCTION__ ." en ". $_SERVER ['SCRIPT_NAME'] ." l�nea ".__LINE__);
}

$response = getHttpscUrl($url);

echo $response;

?>