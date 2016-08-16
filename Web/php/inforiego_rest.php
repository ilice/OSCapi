<?php
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'slack_notification.php';

define ( "username", "mariamunoz" );
define ( "password", "39y67h" );

echo doGet ( NULL );
function doGet($parametros) {
	
	// para depuraci�n
	if ($parametros == NULL) {
		$parametros = array (
				"accion" => "actualiza",
				"latitud" => 40.996163,
				"longitud" => - 4.764504 
		);
	}
	
	$accion = $parametros ["accion"];
	$latitud = ! empty ( $parametros ["latitud"] ) ? $parametros ["latitud"] : NULL;
	$longitud = ! empty ( $parametros ["longitud"] ) ? $parametros ["longitud"] : NULL;
	
	$estacion = obtenEstacion ( $latitud, $longitud );
	
	$fecha_ini = ! empty ( $parametros ["fecha_ini"] ) ? $parametros ["fecha_ini"] : NULL;
	$fecha_fin = ! empty ( $parametros ["fecha_fin"] ) ? $parametros ["fecha_fin"] : NULL;
	

	
	switch ($accion) {
		case "actualiza" :
			$resultado = actualizaDatosClima ( $estacion, $fecha_ini, $fecha_fin );
			break;
		case "obtenEstacion" :
			$resultado = $estacion;
			break;
		case "actualizaTodasEstaciones" :
			$resultado = actualizaTodasEstaciones ();
		default :
			throw "Accion no implementada";
	}
	
	return json_encode ( $resultado, JSON_UNESCAPED_UNICODE );
}
function obtenEstacion($latitud, $longitud) {
	$url = 'http://www.inforiego.org/opencms/rest/estacion?username=' . username . '&password=' . password;
	if ($latitud != null) {
		$url = $url . '&latitud=' . $latitud . '&longitud=' . $longitud;
	}
	
	$response = getHttpcUrl( $url );	
	
	if (count ( $response ) > 1) {
		$resultado = $response;
	} else {
		$resultado = $response[0];
		
		if ($resultado ["IDESTACION"] == null) {
			slack ( "no se encuentran datos de estaciones para las coordenadas proporcionadas" );
		} else {
			$resultado ["result"] = "success";
		}
	}
	
	return $resultado;
}
function actualizaDatosClima($estacion, $fecha_ini, $fecha_fin) {
	$ahora = getDate ();
	$fecha_ult_modif = fechaUltimoRegistro ( $estacion );
	
	if ($fecha_ini == null) {
		$fecha_ini = $estacion ["FECHAINSTAL"];
	}
	
	if ($fecha_fin == null) {
		$fecha_fin = str_pad ( $ahora ["mday"], 2, "0", STR_PAD_LEFT ) . "/" . str_pad ( $ahora ["mon"], 2, "0", STR_PAD_LEFT ) . "/" . $ahora ["year"];
	}
	
	if ($fecha_ult_modif == null) {
		$fecha_ult_modif = "01/01/2016";
	}
	
	for($anio = explode ( "/", $fecha_ini ) [2]; $anio <= explode ( "/", $fecha_fin ) [2]; $anio ++) {
		
		$ini = "01/01/" . $anio;
		$fin = "31/12/" . $anio;
		
		if ($anio == explode ( "/", $fecha_ini ) [2]) {
			$ini = $fecha_ini;
		}
		
		$url = 'http://www.inforiego.org/opencms/rest/diario?username=' . username . '&password=' . password . '&provincia=' . $estacion ["IDPROVINCIA"] . '&estacion=' . $estacion ["IDESTACION"] . '&fecha_ini=' . $ini . '&fecha_fin=' . $fin . '&fecha_ult_modif=' . $fecha_ult_modif;
		
		$response = getHttpcUrl($url);
		
		foreach ($response as $element){
			$url = 'http://81.61.197.16:9200/test_inforiego/info_riego_diario/' . str_replace("/", "_", $element["FECHA"]) . '_' . $element["IDPROVINCIA"] . '_' . $element['IDESTACION'];
			$element = format_info_riego_diario($element, $estacion);
			putHttpcUrl($url, json_encode($element, JSON_UNESCAPED_UNICODE));			
		}
	}
	$resultado ["result"] = "success";
	
	return $resultado;
}
function fechaUltimoRegistro($estacion) {
	$url = "http://81.61.197.16:9200/test_inforiego/info_riego_diario/_search?";
	
	$input = "{
  \"size\": 0,
  \"query\" : {
        \"constant_score\" : { 
            \"filter\" : {
            \"bool\" : {
              \"must\" : [
                {\"term\" : { \"IDESTACION\" : \"" . $estacion ["IDESTACION"] . "\" }},
                {\"term\" : { \"IDPROVINCIA\" : \"" . $estacion ["IDPROVINCIA"] . "\" }}
                ]
            }
        }
    }
    },
   \"aggs\" : {
        \"max_fecha\" : { \"max\" : { \"field\" : \"FECHA\" } }
    }
}";
	$response = postHttpcUrl($url, $input);
		
	
	$max_fecha = json_decode ( $response, true ) ["aggregations"] ["max_fecha"];
	
	return is_null ( $max_fecha ["value"] ) ? NULL : $max_fecha ["value_as_string"];
}

function getHttpcUrl($url){

	$user_agent = $_SERVER['HTTP_USER_AGENT'];
	
	$handler = curl_init($url);
	
	curl_setopt($handler, CURLINFO_HEADER_OUT, true);
	curl_setopt($handler, CURLOPT_USERAGENT, $user_agent);
	curl_setopt ($handler, CURLOPT_RETURNTRANSFER, true );
	
	curl_setopt ($handler, CURLOPT_CONNECTTIMEOUT, 0);
	$response = curl_exec ($handler);
	
	if(curl_error($handler))
	{
		slack('ERROR:' . curl_error($handler));
		slack("ERROR: " . htmlspecialchars(curl_error($handler)));
	
		$info = curl_getinfo($handler);
		slack( 'INFO: Se tard� ' . $info['total_time']. ' segundos en enviar una petici�n a '. $info['url']);
		slack( 'INFO: Request header ' . $info['request_header']);
		switch ($http_code = curl_getinfo($handler, CURLINFO_HTTP_CODE)) {
			case 200:  # OK
				slack('INFO: C�digo HTTP 200-OK: '. $http_code. " en getHttpcUrl($url)");
				break;
			default:
				slack('ERROR: C�digo HTTP inesperado: '. $http_code . " en getHttpcUrl($url)");
		}
	
	}
	
	
	curl_close($handler);
	
	$response_json = json_decode ( utf8_encode ( $response ), true );
	
	$error = json_last_error_msg ();
	if (strcmp ($error , "No error" ) <> 0) {
		slack ( "Error: " . $error . " para la llamada: <$url>" );
	}
	
	if (! $response) {
		slack ( "Error en getHttpcUrl($url)" );
	}
	
	return $response_json;
}

function postHttpcUrl($url, $input){
	$handler = curl_init ( $url );
	
	curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
	// curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
	
	curl_setopt ( $handler, CURLOPT_POST, 1 );
	curl_setopt ( $handler, CURLOPT_POSTFIELDS, $input );
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	
	curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );
	$response = curl_exec ( $handler );
	
	if (curl_error ( $handler )) {
		error_log ( 'ERROR:' . curl_error ( $handler ) );
		error_log ( "ERROR: " . htmlspecialchars ( curl_error ( $handler ) ) );
	
		$info = curl_getinfo ( $handler );
		error_log ( 'INFO: Se tard� ' . $info ['total_time'] . ' segundos en enviar una petici�n a ' . $info ['url'] );
		error_log ( 'INFO: Request header ' . $info ['request_header'] );
		switch ($http_code = curl_getinfo ( $handler, CURLINFO_HTTP_CODE )) {
			case 200 : // OK
				error_log ( 'INFO: C�digo HTTP 200-OK: ' . $http_code );
				break;
			default :
				error_log ( 'ERROR: C�digo HTTP inesperado: ' . $http_code );
		}
	}
	
	curl_close ( $handler );
	
	return $response;
}

function putHttpcUrl($url, $input){
	$handler = curl_init ( $url );
	
	curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
	// curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
	
	curl_setopt ( $handler, CURLOPT_CUSTOMREQUEST, 'PUT' );
	curl_setopt ( $handler, CURLOPT_POSTFIELDS, $input );
	curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
	
	curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );
	$response = curl_exec ( $handler );
	
	if (curl_error ( $handler )) {
		error_log ( 'ERROR:' . curl_error ( $handler ) );
		error_log ( "ERROR: " . htmlspecialchars ( curl_error ( $handler ) ) );
	
		$info = curl_getinfo ( $handler );
		error_log ( 'INFO: Se tard� ' . $info ['total_time'] . ' segundos en enviar una petici�n a ' . $info ['url'] );
		error_log ( 'INFO: Request header ' . $info ['request_header'] );
		switch ($http_code = curl_getinfo ( $handler, CURLINFO_HTTP_CODE )) {
			case 200 : // OK
				error_log ( 'INFO: C�digo HTTP 200-OK: ' . $http_code );
				break;
			default :
				error_log ( 'ERROR: C�digo HTTP inesperado: ' . $http_code );
		}
	}
	
	curl_close ( $handler );
	
	return $response;
	
} 

function format_info_riego_diario($element, $estacion) {
	
	$element["DIA"] = intval($element["DIA"]);
	$element["DIRVIENTO"] = floatval($element["DIRVIENTO"]);
	$element["DIRVIENTOVELMAX"] = floatval($element["DIRVIENTOVELMAX"]);
	$element["ETBC"] = floatval($element["ETBC"]);
	$element["ETHARG"] = floatval($element["ETHARG"]);
	$element["ETPMON"] = floatval($element["ETPMON"]);
	$element["ETRAD"] = floatval($element["ETRAD"]);
	$element["HORMINHUMMAX"] = str_pad ( $element["HORMINHUMMAX"], 4, "0", STR_PAD_LEFT );
	$element["HORMINHUMMIN"] = str_pad ( $element["HORMINHUMMIN"], 4, "0", STR_PAD_LEFT );
	$element["HORMINTEMPMAX"] = str_pad ( $element["HORMINTEMPMAX"], 4, "0", STR_PAD_LEFT );
	$element["HORMINTEMPMIN"] = str_pad ( $element["HORMINTEMPMIN"], 4, "0", STR_PAD_LEFT );
	$element["HORMINVELMAX"] = str_pad ( $element["HORMINVELMAX"], 4, "0", STR_PAD_LEFT );
	$element["HUMEDADD"] = floatval($element["HUMEDADD"]);
	$element["HUMEDADMAX"] = floatval($element["HUMEDADMAX"]);
	$element["HUMEDADMEDIA"] = floatval($element["HUMEDADMEDIA"]);
	$element["HUMEDADMIN"] = floatval($element["HUMEDADMIN"]);
	$element["N"] = floatval($element["N"]);
	$element["PEBC"] = floatval($element["PEBC"]);
	$element["PEHARG"] = floatval($element["PEHARG"]);
	$element["PEPMON"] = floatval($element["PEPMON"]);
	$element["PERAD"] = floatval($element["PERAD"]);
	$element["PRECIPITACION"] = floatval($element["PRECIPITACION"]);
	$element["RADIACION"] = floatval($element["RADIACION"]);
	$element["RECORRIDO"] = floatval($element["RECORRIDO"]);
	$element["RMAX"] = floatval($element["RMAX"]);
	$element["RN"] = floatval($element["RN"]);
	$element["TEMPD"] = floatval($element["TEMPD"]);
	$element["TEMPMAX"] = floatval($element["TEMPMAX"]);
	$element["TEMPMEDIA"] = floatval($element["TEMPMEDIA"]);
	$element["TEMPMIN"] = floatval($element["TEMPMIN"]);
	$element["VD"] = floatval($element["VD"]);
	$element["VELVIENTO"] = floatval($element["VELVIENTO"]);
	$element["VELVIENTOMAX"] = floatval($element["VELVIENTOMAX"]);
	$element["VN"] = floatval($element["VN"]);
	
	$element["lat_lon"] = array("lat" => floatval((strcmp(substr($estacion["LATITUD"], -1), "S") == 0? "-": "") . ltrim(substr($estacion["LATITUD"], 0, 2), "0") . "." . substr($estacion["LATITUD"], 2, 7)) , "lon" => floatval((strcmp(substr($estacion["LONGITUD"], -1), "W") == 0? "-": "") . ltrim(substr($estacion["LONGITUD"], 0, 2), "0") . "." . substr($estacion["LONGITUD"], 2, 7)));
	$element["altitud"] = intval($estacion["ALTITUD"]);
		
	return $element;
}
?>