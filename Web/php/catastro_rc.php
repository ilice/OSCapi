<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/xml; charset=UTF-8");

require_once 'cUrl.php';

$querystring = $_SERVER['QUERY_STRING'];

$url = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?";

if(strlen($querystring)>0){
	$url = "$url$querystring" ;
}

$esJson = false;

$response = getHttpcUrl($url, $esJson);

echo $response

?>