<?php
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'slack_notification.php';

define ( "username", "mariamunoz" );
define ( "password", "39y67h" );
define ( "error", '{"error":"error"}' );

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
	slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada interna a inforiego sin parámetros" );
	echo error;
}
function doGet($parametros) {
	$accion = ! empty ( $parametros ["accion"] ) ? $parametros ["accion"] : NULL;
	
	if ($accion == NULL) {
		
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada interna a inforiego sin determinar la acción a realizar" );
		$resultado = error;
	} else {
		
		$latitud = ! empty ( $parametros ["latitud"] ) ? $parametros ["latitud"] : NULL;
		$longitud = ! empty ( $parametros ["longitud"] ) ? $parametros ["longitud"] : NULL;
		$estaciones = obtenEstaciones ( $latitud, $longitud );
		$fecha_ini = ! empty ( $parametros ["fecha_ini"] ) ? $parametros ["fecha_ini"] : NULL;
		$fecha_fin = ! empty ( $parametros ["fecha_fin"] ) ? $parametros ["fecha_fin"] : NULL;
		$anio = ! empty ( $parametros ["anio"] ) ? $parametros ["anio"] : NULL;
		$medida = ! empty ( $parametros ["medida"] ) ? $parametros ["medida"] : NULL;
		$numeroDeAnios = ! empty ( $parametros ["numeroDeAnios"] ) ? $parametros ["numeroDeAnios"] : NULL;
		$intervalo = ! empty ( $parametros ["intervalo"] ) ? $parametros ["intervalo"] : NULL;
		$formato = ! empty ( $parametros ["formato"] ) ? $parametros ["formato"] : NULL;
		
		switch ($accion) {
			case "actualiza" :
				$resultado = actualizaDatosClima ( $estaciones, $fecha_ini, $fecha_fin );
				break;
			case "actualizaDiario" :
				$resultado = actualizaDatosClima ( $estaciones, $fecha_ini, $fecha_fin );
				break;
			case "actualizaEstaciones" :
				$resultado = actualizaEstaciones ( $estaciones );
			case "obtenEstacion" :
				$resultado = $estaciones;
				break;
			case "diasDeLluvia" :
				$resultado = diasDeLluvia ( $latitud, $longitud, $anio );
				break;
			case "temperaturaDiaria" :
				$resultado = temperaturaDiaria ( $latitud, $longitud, $anio );
				break;
			case "datosMedidaPorAnio" :
				$resultado = datosMedidaPorAnio ( $medida, $longitud, $latitud, $numeroDeAnios, $intervalo, $formato );
				break;
			default :
				slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Acción no implementada" );
				$resultado = error;
		}
	}
	return $resultado;
}
function obtenEstaciones($latitud, $longitud) {
	$url = 'http://www.inforiego.org/opencms/rest/estacion?username=' . username . '&password=' . password;
	
	if ($latitud != null) {
		$url = $url . '&latitud=' . $latitud . '&longitud=' . $longitud;
	}
	
	return getHttpcUrl ( $url );
}
function actualizaDatosClima($estaciones, $fecha_ini, $fecha_fin) {
	foreach ( $estaciones as $estacion ) {
		
		$ahora = getDate ();
		$fecha_ult_modif = fechaUltimoRegistro ( $estacion );
		
		if ($fecha_ini == null) {
			$fecha_ini = $estacion ["FECHAINSTAL"];
		}
		
		if ($fecha_fin == null) {
			$fecha_fin = str_pad ( $ahora ["mday"], 2, "0", STR_PAD_LEFT ) . "/" . str_pad ( $ahora ["mon"], 2, "0", STR_PAD_LEFT ) . "/" . $ahora ["year"];
		}
		
		if ($fecha_ult_modif == null) {
			$fecha_ult_modif = "01/01/2000";
		}
		
		for($anio = explode ( "/", $fecha_ini ) [2]; $anio <= explode ( "/", $fecha_fin ) [2]; $anio ++) {
			
			$ini = "01/01/" . $anio;
			$fin = "31/12/" . $anio;
			
			if ($anio == explode ( "/", $fecha_ini ) [2]) {
				$ini = $fecha_ini;
			}
			
			$url = 'http://www.inforiego.org/opencms/rest/diario?username=' . username . '&password=' . password . '&provincia=' . $estacion ["IDPROVINCIA"] . '&estacion=' . $estacion ["IDESTACION"] . '&fecha_ini=' . $ini . '&fecha_fin=' . $fin . '&fecha_ult_modif=' . $fecha_ult_modif;
			
			$response = getHttpcUrl ( $url );
			
			foreach ( $response as $element ) {
				$url = 'http://81.61.197.16:9200/test_inforiego/info_riego_diario/' . str_replace ( "/", "_", $element ["FECHA"] ) . '_' . $element ["IDPROVINCIA"] . '_' . $element ['IDESTACION'];
				$element = format_info_riego_diario ( $element, $estacion );
				putHttpcUrl ( $url, json_encode ( $element, JSON_UNESCAPED_UNICODE ) );
			}
		}
	}
	
	$resultado ["result"] = "success";
	
	return $resultado;
}
function actualizaEstaciones($estaciones) {
	foreach ( $estaciones as $estacion ) {
		
		$url = 'http://81.61.197.16:9200/test_estaciones_inforiego/info_riego_estacion/' . $estacion ["ESTACIONCORTO"];
		$estacion = format_info_riego_estacion ( $estacion );
		putHttpcUrl ( $url, json_encode ( $estacion, JSON_UNESCAPED_UNICODE ) );
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
	$response = postHttpcUrl ( $url, $input );
	
	$max_fecha = json_decode ( $response, true ) ["aggregations"] ["max_fecha"];
	
	return is_null ( $max_fecha ["value"] ) ? NULL : $max_fecha ["value_as_string"];
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
		slack ( "ERROR: " . $response );
	}
	
	curl_close ( $handler );
	
	return $response;
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
		slack ( "ERROR: " . $response );
	}
	
	curl_close ( $handler );
	
	return $response;
}
function format_info_riego_diario($element, $estacion) {
	$element ["DIA"] = intval ( $element ["DIA"] );
	$element ["DIRVIENTO"] = floatval ( $element ["DIRVIENTO"] );
	$element ["DIRVIENTOVELMAX"] = floatval ( $element ["DIRVIENTOVELMAX"] );
	$element ["ETBC"] = floatval ( $element ["ETBC"] );
	$element ["ETHARG"] = floatval ( $element ["ETHARG"] );
	$element ["ETPMON"] = floatval ( $element ["ETPMON"] );
	$element ["ETRAD"] = floatval ( $element ["ETRAD"] );
	$element ["HORMINHUMMAX"] = format_HHmm ( $element ["HORMINHUMMAX"] );
	$element ["HORMINHUMMIN"] = format_HHmm ( $element ["HORMINHUMMIN"] );
	$element ["HORMINTEMPMAX"] = format_HHmm ( $element ["HORMINTEMPMAX"] );
	$element ["HORMINTEMPMIN"] = format_HHmm ( $element ["HORMINTEMPMIN"] );
	$element ["HORMINVELMAX"] = format_HHmm ( $element ["HORMINVELMAX"] );
	$element ["HUMEDADD"] = floatval ( $element ["HUMEDADD"] );
	$element ["HUMEDADMAX"] = floatval ( $element ["HUMEDADMAX"] );
	$element ["HUMEDADMEDIA"] = floatval ( $element ["HUMEDADMEDIA"] );
	$element ["HUMEDADMIN"] = floatval ( $element ["HUMEDADMIN"] );
	$element ["N"] = floatval ( $element ["N"] );
	$element ["PEBC"] = floatval ( $element ["PEBC"] );
	$element ["PEHARG"] = floatval ( $element ["PEHARG"] );
	$element ["PEPMON"] = floatval ( $element ["PEPMON"] );
	$element ["PERAD"] = floatval ( $element ["PERAD"] );
	$element ["PRECIPITACION"] = floatval ( $element ["PRECIPITACION"] );
	$element ["RADIACION"] = floatval ( $element ["RADIACION"] );
	$element ["RECORRIDO"] = floatval ( $element ["RECORRIDO"] );
	$element ["RMAX"] = floatval ( $element ["RMAX"] );
	$element ["RN"] = floatval ( $element ["RN"] );
	$element ["TEMPD"] = floatval ( $element ["TEMPD"] );
	$element ["TEMPMAX"] = floatval ( $element ["TEMPMAX"] );
	$element ["TEMPMEDIA"] = floatval ( $element ["TEMPMEDIA"] );
	$element ["TEMPMIN"] = floatval ( $element ["TEMPMIN"] );
	$element ["VD"] = floatval ( $element ["VD"] );
	$element ["VELVIENTO"] = floatval ( $element ["VELVIENTO"] );
	$element ["VELVIENTOMAX"] = floatval ( $element ["VELVIENTOMAX"] );
	$element ["VN"] = floatval ( $element ["VN"] );
	
	$element ["lat_lon"] = array (
			"lat" => gradosSexagesimalesAgradosDecimales ( $estacion ["LATITUD"] ),
			"lon" => gradosSexagesimalesAgradosDecimales ( $estacion ["LONGITUD"] ) 
	);
	$element ["altitud"] = intval ( $estacion ["ALTITUD"] );
	
	return $element;
}
function format_info_riego_estacion($estacion) {
	$estacion ["ALTITUD"] = intval ( $estacion ["ALTITUD"] );
	
	$estacion ["lat_lon"] = array (
			"lat" => gradosSexagesimalesAgradosDecimales ( $estacion ["LATITUD"] ),
			"lon" => gradosSexagesimalesAgradosDecimales ( $estacion ["LONGITUD"] ) 
	);
	
	foreach ( $estacion as $propiedad_estacion => $valor ) {
		if (empty ( $valor )) {
			unset ( $estacion [$propiedad_estacion] );
		}
	}
	
	return $estacion;
}
function gradosSexagesimalesAgradosDecimales($gradosSexagesimales) {
	$orientacion = ((strcmp ( substr ( $gradosSexagesimales, - 1 ), "N" ) == 0) || (strcmp ( substr ( $gradosSexagesimales, - 1 ), "E" ) == 0)) ? 1 : - 1;
	$grados = floatval ( ltrim ( substr ( $gradosSexagesimales, 0, 2 ), 0 ) );
	$minutos = floatval ( ltrim ( substr ( $gradosSexagesimales, 2, 2 ), 0 ) );
	$segundos = floatval ( ltrim ( substr ( $gradosSexagesimales, 4, 2 ), 0 ) );
	$segundos = floatval ( ltrim ( substr ( $gradosSexagesimales, 4, 2 ), 0 ) );
	$centesimas = floatval ( ltrim ( substr ( $gradosSexagesimales, 6, 3 ), 0 ) );
	$gradosDecimales = $orientacion * ($grados + ($minutos / 60) + ($segundos / 3600) + ($centesimas / 360000));
	return floatval ( $gradosDecimales );
}
function diasDeLluvia($latitud, $longitud, $anio) {
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	$url = 'http://81.61.197.16:9200/test_inforiego/info_riego_diario/_search?';
	$input = utf8_encode ( '{"size" : 0,
   "query" : {
        "constant_score" : {
            "filter" : {
              "bool": { 
                "must": [
                  {"range" : {
                      "PRECIPITACION" : {
                          "gt" : 0
                      }
                  }},
                  { "term": { "IDESTACION" : "' . $estacion ["IDESTACION"] . '" } },
                  { "term": { "IDPROVINCIA" : "' . $estacion ["IDPROVINCIA"] . '" } },
                  { "term": { "AÑO" : "' . $anio . '" } }
                ]
              }
            }
        }
    },
   "aggs": {
      "anios": {
         "terms": {
            "field": "AÑO"
         },
         "aggs": { 
            "sum_precipitacion": { 
               "sum": {
                  "field": "PRECIPITACION" 
               }
            }
         }
      }
   }
}' );
	
	$resultado = json_decode ( postHttpcUrl ( $url, $input ), true );
	$diasDeLluvia = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["doc_count"];
	$precipitacionAcumulada = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["sum_precipitacion"] ["value"];
	
	return '{"diasDeLluvia": ' . $diasDeLluvia . ', "precipitacionAcumulada": ' . $precipitacionAcumulada . '}';
}
function temperaturaDiaria($latitud, $longitud, $anio) {
	$respuesta = "";
	
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	$url = 'http://81.61.197.16:9200/test_inforiego/info_riego_diario/_search?';
	$input = utf8_encode ( '{"size" : 0,
   "query" : {
        "constant_score" : {
            "filter" : {
              "bool": {
                "must": [
                  { "term": { "IDESTACION" : "' . $estacion ["IDESTACION"] . '" } },
                  { "term": { "IDPROVINCIA" : "' . $estacion ["IDPROVINCIA"] . '" } },
                  { "term": { "AÑO" : "' . $anio . '" } }
                ]
              }
            }
        }
    },
   "aggs": {
      "anios": {
         "terms": {
            "field": "AÑO"
         },
         "aggs":  {
            "max_temperatura": { 
               "max": {
                  "field": "TEMPMAX" 
               }
            },
            "min_temperatura": { 
               "min": {
                  "field": "TEMPMIN" 
               }
            },
            "media_temperatura": { 
               "avg": {
                  "field": "TEMPMEDIA" 
               }
            },
            "media_horas_sol": { 
               "avg": {
                  "field": "N" 
               }
            },
            "max_horas_sol": { 
               "max": {
                  "field": "N" 
               }
            },
            "sum_horas_sol": { 
               "sum": {
                  "field": "N" 
               }
            },
            "media_radiacion": { 
               "avg": {
                  "field": "RADIACION" 
               }
            },
            "max_radiacion": { 
               "max": {
                  "field": "RADIACION" 
               }
            },
            "sum_radiacion": { 
               "sum": {
                  "field": "RADIACION" 
               }
            }          
         }
      }
   }
}' );
	
	$resultado = json_decode ( postHttpcUrl ( $url, $input ), true );
	
	if (isset ( $resultado ["error"] )) {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . json_encode ( $resultado ) . " para el input " . $input );
		$respuesta = error;
	} else {
		$min_temperatura = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["min_temperatura"] ["value"];
		$max_temperatura = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["max_temperatura"] ["value"];
		$media_temperatura = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["media_temperatura"] ["value"];
		$media_horas_sol = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["media_horas_sol"] ["value"];
		$max_horas_sol = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["max_horas_sol"] ["value"];
		$sum_horas_sol = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["sum_horas_sol"] ["value"];
		$media_radiacion = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["media_radiacion"] ["value"];
		$max_radiacion = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["max_radiacion"] ["value"];
		$sum_radiacion = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["sum_radiacion"] ["value"];
		
		$respuesta = '{"min_temperatura": ' . $min_temperatura . ',
			"max_temperatura": ' . $max_temperatura . ',
			"media_temperatura": ' . $media_temperatura . ',
			"media_horas_sol": ' . $media_horas_sol . ',
			"max_horas_sol": ' . $max_horas_sol . ',
			"sum_horas_sol": ' . $sum_horas_sol . ',
			"media_radiacion": ' . $media_radiacion . ',
			"max_radiacion": ' . $max_radiacion . ',
			"sum_radiacion": ' . $sum_radiacion . '
			}';
	}
	return $respuesta;
}
function format_HHmm($hora) {
	$hora_HHmm = str_pad ( $hora, 4, "0", STR_PAD_LEFT );
	$HH = substr ( $hora_HHmm, 0, 2 );
	$mm = substr ( $hora_HHmm, 2, 2 );
	if (strcmp ( $HH, "24" ) == 0) {
		$hora_HHmm = "00" . $mm;
	}
	return $hora_HHmm;
}
function datosMedidaPorAnio($medida, $latitud, $longitud, $numeroDeAnios, $intervalo, $formato) {
	$respuesta = "";
	
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	$url = 'http://81.61.197.16:9200/test_inforiego/info_riego_diario/_search?';
	$input = utf8_encode ( '{
   "size" : 0,
   "query" : {
        "constant_score" : {
            "filter" : {
              "bool": { 
                "must": [
                  { "term": { "IDESTACION" : "' . $estacion ["IDESTACION"] . '" } },
                  { "term": { "IDPROVINCIA" : "' . $estacion ["IDPROVINCIA"] . '" } } 
                ]
              }
            }
        }
    },
   "aggs": {
      "anios": {
         "terms": {
            "field": "AÑO",
              "order": {
                "_term" : "desc" 
              },
             "size": ' . $numeroDeAnios . '
         },
         "aggs": { 
            "medida": { 
               "date_histogram": {
                  "field": "FECHA",
                  "interval": "' . $intervalo . '",
                  "format": "' . $formato . '" 
               },
               "aggs": {
                  "medida": {
                     "sum": { "field": "' . $medida . '"} 
                  }
               }
            }
         }
      }
   }
}' );
	
	$resultado = json_decode ( postHttpcUrl ( $url, $input ), true );
	
	if (isset ( $resultado ["error"] )) {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . json_encode ( $resultado ) . " para el input " . $input );
		$respuesta = error;
	} else {
		
		$data = array ();
		$columnas = array ();
		$anios_buckets = $resultado ["aggregations"] ["anios"] ["buckets"];
		
		foreach ( $anios_buckets as $anio_bucket ) {
			
			$anio = $anio_bucket ["key_as_string"];
			$intervalos_buckets = $anio_bucket ["medida"] ["buckets"];
			array_push ( $columnas, array (
					"label" => $anio,
					"type" => "number" 
			) );
			
			foreach ( $intervalos_buckets as $intervalo_bucket ) {
				$numero_intervalo = intVal ( $intervalo_bucket ["key_as_string"] );
				$valor = $intervalo_bucket ["medida"] ["value"];
				$data [$anio] [$numero_intervalo] = $valor;
			}
		}
		
		$max_items = strcmp ( $formato, "M" ) == 0 ? 13 : 367;
		$rows = array ();
		for($numero_intervalo = 1; $numero_intervalo < $max_items; $numero_intervalo ++) {
			$row = array ();
			if (strcmp ( $formato, "M" ) == 0) {
				array_push ( $row, nombre_mes ( $numero_intervalo ) );
			} else {
				array_push ( $row, "" . $numero_intervalo );
			}
			
			foreach ( $columnas as $columna ) {
				array_push ( $row, isset ( $data [$columna ["label"]] [$numero_intervalo] ) ? $data [$columna ["label"]] [$numero_intervalo] : NULL );
			}
			array_push ( $rows, $row );
		}
		
		array_unshift ( $columnas, array (
				"label" => "Mes",
				"type" => "string" 
		) );
		
		$respuesta = json_encode ( array (
				"cols" => $columnas,
				"rows" => $rows 
		) );
	}
	
	return $respuesta;
}
function nombre_mes($numero_mes) {
	$nombre_mes = array (
			"Mes",
			"Enero",
			"Febrero",
			"Marzo",
			"Abril",
			"Mayo",
			"Junio",
			"Julio",
			"Agosto",
			"Septiembre",
			"Octubre",
			"Noviembre",
			"Diciembre" 
	);
	
	return $nombre_mes [$numero_mes];
}
?>