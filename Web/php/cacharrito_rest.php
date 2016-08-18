<?php
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'slack_notification.php';
require_once 'cUrl.php';

$querystring = $_SERVER ['QUERY_STRING'];
$request = explode ( '/', trim ( $_SERVER ['PATH_INFO'], '/' ) );

// retrieve the index and type from the path
$index = preg_replace ( '/[^a-z0-9_]+/i', '', array_shift ( $request ) );
$type = preg_replace ( '/[^a-z0-9_]+/i', '', array_shift ( $request ) );

$parametros = array ();

if (! empty ( $querystring )) {
	$explode_querystring = explode ( "&", $querystring );
	
	foreach ( $explode_querystring as $unformated_parametro ) {
		$explode_parametro = explode ( "=", $unformated_parametro );
		$parametros [$explode_parametro [0]] = $explode_parametro [1];
	}
	
	echo doGet ( $parametros, $index, $type );
} else {
	// slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada interna a cacharrito_rest sin parámetros" );
	echo error;
}
function doGet($parametros, $index, $type) {
	$imei = ! empty ( $parametros ["IMEI"] ) ? $parametros ["IMEI"] : NULL;
	$sensor = ! empty ( $parametros ["Sensor"] ) ? $parametros ["Sensor"] : NULL;
	$valor = ! empty ( $parametros ["Valor"] ) ? $parametros ["Valor"] : 0; // empty("0") es true, por eso en este caso uso 0 en lugar de NULL
	$latitud = ! empty ( $parametros ["Latitud"] ) ? $parametros ["Latitud"] : ! empty ( $parametros ["latitud"] ) ? $parametros ["latitud"] : NULL;
	$longitud = ! empty ( $parametros ["Longitud"] ) ? $parametros ["Longitud"] : ! empty ( $parametros ["longitud"] ) ? $parametros ["longitud"] : NULL;
	$accion = ! empty ( $parametros ["accion"] ) ? $parametros ["accion"] : NULL;
	
	if ($accion == NULL) {
		$fecha = date ( "Y-m-d\TH:i" );
		$id = $fecha . "-" . $imei;
		
		$url = "http://81.61.197.16:9200/osc_station/osc_station_record/" . $id . "/_update";
		
		if ($sensor != NULL) {
			$input = '{"doc": {"IMEI" : ' . $imei . ', "' . $sensor . '" : ' . $valor . ', "FECHA" : "' . $fecha . '"}, "doc_as_upsert" : true }';
		} elseif ($latitud != NULL && $longitud != NULL) {
			$input = '{"doc": {"IMEI" : ' . $imei . ', "lat_lon": {"lon" : ' . $longitud . ', "lat" : ' . $latitud . '}, "FECHA" : "' . $fecha . '"}, "doc_as_upsert" : true }';
		} else {
			slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " en los parámetros del cacharrito" );
			;
		}
		
		postHttpcUrl ( $url, $input );
	} else {
		$url = "http://81.61.197.16:9200/" . $index . "/". $type ."/_search?";
		
		$input = '{
  "sort": [
    {
      "_geo_distance": {
        "lat_lon": { 
          "lat":  ' . $latitud . ',
          "lon": ' . $longitud . '
        },
        "order":         "asc",
        "unit":          "km", 
        "distance_type": "plane" 
      }
    },
    { "FECHA":   { "order": "desc" }}
  ],
  "size" : 1
}';
		$response = postHttpcUrl ( $url, $input );
		echo $response;
	}
}

?>