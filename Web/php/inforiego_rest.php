<?php
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'slack_notification.php';
require_once 'cUrl.php';
$config = include 'config.php';

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
	
	echo main ( $parametros );
} else {
	slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Llamada interna a inforiego sin parámetros" );
	echo error;
}
function main($parametros) {
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
			case "actualizaRecord" :
				$resultado = actualizaRecord ( $estaciones, $fecha_ini, $fecha_fin );
				break;
			case "actualizaDiario" :
				$resultado = actualizaDatosClima ( $estaciones, $fecha_ini, $fecha_fin );
				break;
			case "actualizaEstaciones" :
				$resultado = actualizaEstaciones ( $estaciones );
				break;
			case "obtenEstacion" :
				$resultado = $estaciones;
				break;
			case "diasDeLluvia" :
				$resultado = diasDeLluvia ( $latitud, $longitud, $anio );
				break;
			case "medidasDiarias" :
				$resultado = medidasDiarias ( $latitud, $longitud, $anio );
				break;
			case "datosMedidaPorAnio" :
				$resultado = datosMedidaPorAnio ( $medida, $longitud, $latitud, $numeroDeAnios, $intervalo, $formato );
				break;
			default :
				slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . " Acción no implementada: " . $accion );
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
	
	$response = getHttpcUrl ( $url );
	return json_decode ( utf8_encode ( $response ), true );
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
			
			if ($anio == explode ( "/", $fecha_fin ) [2]) {
				$fin = $fecha_fin;
			}
			
			$url = 'http://www.inforiego.org/opencms/rest/diario?username=' . username . '&password=' . password . '&provincia=' . $estacion ["IDPROVINCIA"] . '&estacion=' . $estacion ["IDESTACION"] . '&fecha_ini=' . $ini . '&fecha_fin=' . $fin . '&fecha_ult_modif=' . $fecha_ult_modif;
			
			$response = getHttpcUrl ( $url );
			$response_json = json_decode ( utf8_encode ( $response ), true );
			
			foreach ( $response_json as $element ) {
				$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_daily/' . str_replace ( "/", "_", $element ["FECHA"] ) . '_' . $element ["IDPROVINCIA"] . '_' . $element ['IDESTACION'];
				$element = format_info_riego_diario ( $element, $estacion );
				putHttpcUrl ( $url, json_encode ( $element, JSON_UNESCAPED_UNICODE ) );
			}
		}
	}
	
	$resultado ["result"] = "success";
	
	return json_encode ( $resultado, JSON_UNESCAPED_UNICODE );
}
function actualizaRecord($estaciones, $fecha_ini, $fecha_fin) {
	$updated = 0;
	foreach ( $estaciones as $estacion ) {
		
		$ahora = getDate ();
		$fecha_ult_modif = fechaUltimoRegistro_info_riego_record ( $estacion );
		
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
			
			if ($anio == explode ( "/", $fecha_fin ) [2]) {
				$fin = $fecha_fin;
			}
			
			for($month = explode ( "/", $ini ) [1]; $month <= explode ( "/", $fin ) [1]; $month ++) {
				
				$ini_month = "01/" . $month . "/" . $anio;
				$fin_month = days_in_month ( $month, $anio ) . "/" . $month . "/" . $anio;
				
				if ($month == explode ( "/", $ini ) [1]) {
					$ini_month = $ini;
				}
				
				if ($month == explode ( "/", $fin ) [1]) {
					$fin_month = $fin;
				}
				
				$url = 'http://www.inforiego.org/opencms/rest/horario?username=' . username . '&password=' . password . '&provincia=' . $estacion ["IDPROVINCIA"] . '&estacion=' . $estacion ["IDESTACION"] . '&fecha_ini=' . $ini_month . '&fecha_fin=' . $fin_month . '&fecha_ult_modif=' . $fecha_ult_modif;
				
				$response = getHttpcUrl ( $url );
				$response_json = json_decode ( utf8_encode ( $response ), true );
				
				foreach ( $response_json as $element ) {
					$element = format_info_riego_record ( $element, $estacion );
					$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_record/' . urlencode ( $estacion ["ESTACIONCORTO"] . " - " . substr ( $element ["date"], 0, 10 ) . " " . substr ( $element ["date"], 11, 8 ) );
					putHttpcUrl ( $url, json_encode ( $element, JSON_UNESCAPED_UNICODE ) );
					$updated ++;
				}
			}
		}
	}
	
	$resultado ["updated"] = $updated;
	$resultado ["result"] = "success";
	
	return json_encode ( $resultado, JSON_UNESCAPED_UNICODE );
}
function actualizaEstaciones($estaciones) {
	$resultado = "error";
	
	foreach ( $estaciones as $estacion ) {
		$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_station/' . $estacion ["ESTACIONCORTO"];
		$estacion = format_info_riego_estacion ( $estacion );
		putHttpcUrl ( $url, json_encode ( $estacion, JSON_UNESCAPED_UNICODE ) );
		$resultado = "success";
	}
	
	return $resultado;
}
function fechaUltimoRegistro($estacion) {
	$url = $GLOBALS ['config'] ['elasticendpoint'] . "inforiego/info_riego_daily/_search";
	
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
	
	$aggregations = isset ( json_decode ( $response, true ) ["aggregations"] ) ? json_decode ( $response, true ) ["aggregations"] : NULL;
	
	$max_fecha = isset ( $aggregations ) ? $aggregations ["max_fecha"] : NULL;
	
	return is_null ( $max_fecha ["value"] ) ? NULL : $max_fecha ["value_as_string"];
}
function fechaUltimoRegistro_info_riego_record($estacion) {
	$url = $GLOBALS ['config'] ['elasticendpoint'] . "inforiego/info_riego_record/_search";
	
	$input = "{
  \"size\": 0,
  \"filter\" : { \"term\": { \"code\": \"" . $estacion ["ESTACIONCORTO"] . "\" } },			
   \"aggs\" : {
        \"max_fecha\" : { \"max\" : { \"field\" : \"date\" } }
    }
}";
	
	$response = postHttpcUrl ( $url, $input );
	
	$aggregations = json_decode ( $response, true ) ["aggregations"];
	
	$max_fecha = isset ( $aggregations ) ? $aggregations ["max_fecha"] : NULL;
	
	return is_null ( $max_fecha ["value"] ) ? NULL : formatDateToDDMMYYYY ( $max_fecha ["value_as_string"] );
}
function diasDeLluvia($latitud, $longitud, $anio) {
	$respuesta = '{"error" : "No se han podido obtener los días de lluvia"}';
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	if ($anio == NULL || $latitud == NULL || $longitud == NULL) {
		slack ( "ERROR: " . $_SERVER ['SCRIPT_NAME'] . json_encode ( $resultado ) . " al obtener días de lluvia para lat:  " . $latitud . " long: " . $longitud . " año: " . $anio );
	}
	$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_daily/_search';
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
	if(isset($resultado["aggregations"])){
	$diasDeLluvia = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["doc_count"];
	$precipitacionAcumulada = $resultado ["aggregations"] ["anios"] ["buckets"] [0] ["sum_precipitacion"] ["value"];
	
	$respuesta = '{"diasDeLluvia": ' . $diasDeLluvia . ', "precipitacionAcumulada": ' . $precipitacionAcumulada . '}';
	}
	
	return $respuesta;
}
function medidasDiarias($latitud, $longitud, $anio) {
	$respuesta = "";
	
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_daily/_search?';
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
function datosMedidaPorAnio($medida, $latitud, $longitud, $numeroDeAnios, $intervalo, $formato) {
	$respuesta = "";
	
	$estacion = obtenEstaciones ( $latitud, $longitud ) [0];
	$url = $GLOBALS ['config'] ['elasticendpoint'] . 'inforiego/info_riego_daily/_search';
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
		if (isset ( $resultado ["aggregations"] )) {
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
		}else{
			slack ( "ERROR: No se obtienen correctamente los datos agregados. " . $_SERVER ['SCRIPT_NAME'] . json_encode ( $resultado ) . " para el input " . $input );
			$respuesta = error;
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
function format_info_riego_record($element, $estacion) {
	$new_element = [ ];
	$new_element ["code"] = $estacion ["ESTACIONCORTO"];
	$fecha = $element ["FECHA"];
	$hora = format_HHmm ( $element ["HORAMIN"] );
	$new_element ["date"] = substr ( $fecha, 6, 4 ) . "-" . substr ( $fecha, 3, 2 ) . "-" . substr ( $fecha, 0, 2 ) . "T" . substr ( $hora, 0, 2 ) . ":" . substr ( $hora, 2, 2 ) . ":00";
	
	$new_element ["lat_lon"] = array (
			"lat" => gradosSexagesimalesAgradosDecimales ( $estacion ["LATITUD"] ),
			"lon" => gradosSexagesimalesAgradosDecimales ( $estacion ["LONGITUD"] ) 
	);
	
	$new_element ["location"] = $estacion ["ESTACION"];
	$new_element ["radiation"] = floatval ( $element ["RADIACION"] );
	$new_element ["rain"] = floatval ( $element ["PRECIPITACION"] );
	$new_element ["rel_humidity"] = floatval ( $element ["HUMEDADMEDIA"] );
	$new_element ["station_height"] = intval ( $estacion ["ALTITUD"] );
	$new_element ["temperature"] = floatval ( $element ["TEMPMEDIA"] );
	$new_element ["wind_direction"] = floatval ( $element ["DIRVIENTO"] );
	$new_element ["wind_speed"] = floatval ( $element ["VELVIENTO"] );
	
	return $new_element;
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
function formatDateToDDMMYYYY($date) {
	$dateTokenized = explode ( "-", explode ( "T", $date ) [0] );
	
	return $dateTokenized [2] . "/" . $dateTokenized [1] . "/" . $dateTokenized [0];
}
function days_in_month($month, $year) {
	// calculate number of days in a month
	return $month == 2 ? ($year % 4 ? 28 : ($year % 100 ? 29 : ($year % 400 ? 28 : 29))) : (($month - 1) % 7 % 2 ? 30 : 31);
}
?>