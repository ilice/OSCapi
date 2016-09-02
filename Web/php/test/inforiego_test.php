<?php

require_once( __DIR__ . '/../../../vendor/simpletest/simpletest/autorun.php');


class TestOfInforiego extends UnitTestCase {
	function __construct() {
		parent::__construct ( 'Inforiego test' );
	}

	function getResponse($url){
		//$user_agent = $_SERVER ['HTTP_USER_AGENT'];

		$handler = curl_init ( $url );

		curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
		//curl_setopt ( $handler, CURLOPT_USERAGENT, $user_agent );
		curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
		curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );

		$response = curl_exec ( $handler );
		return $response;
	}

	function testInforiegoGetLluviaYPrecipitacionAcumuladaForLatitudeAndLongitudeAndYear() {
		//cargaMedidaDiasDeLluviaYPrecipitacionAcumulada() en parcela.js
		
		$anio = Date('Y');
		$latitud = 40.439983;
		$longitud = - 5.737026;
		
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=diasDeLluvia&latitud=". $latitud . "&longitud=" . $longitud .
		"&anio=" . $anio;
		
		$response = $this->getResponse($url);

		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$diasDeLluvia = isset($response_json['diasDeLluvia'])?$response_json['diasDeLluvia']:null;
		$this->assertNotNull ($diasDeLluvia, 'Se espera que se devuelvan los días de lluvia para el año mediante la url: ' . $url);
		$this->assertTrue ($diasDeLluvia >= 0, 'El número de días de lluvia debe ser mayor o igual a cero para el año mediante la url: ' . $url);
		$precipitacionAcumulada = isset($response_json['precipitacionAcumulada'])?$response_json['precipitacionAcumulada']:null;
		$this->assertNotNull ($precipitacionAcumulada, 'Se espera que se devuelva la precipitación acumulada para el año mediante la url: ' . $url);
		$this->assertTrue ($precipitacionAcumulada >= 0, 'La precipitación acumulada debe ser mayor o igual a cero para el año mediante la url: ' . $url);
	}
	
	function testInforiegoGetMedidasDiariasForLatitudeAndLongitudeAndYear() {
		//cargaMedidasDiarias() en parcela.js
	
		$anio = Date('Y');
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=medidasDiarias&latitud=". $latitud . "&longitud=" . $longitud .
		"&anio=" . $anio;
	
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$min_temperatura = isset($response_json['min_temperatura'])?$response_json['min_temperatura']:null;
		$this->assertNotNull ($min_temperatura, 'Se espera que se devuelva la temperatura mínima para el año mediante la url: ' . $url);
		$this->assertTrue ($min_temperatura >= -40, 'La temperatura mínima debe ser mayor o igual a -40º para el año mediante la url: ' . $url);
		$max_temperatura = isset($response_json['max_temperatura'])?$response_json['max_temperatura']:null;
		$this->assertNotNull ($max_temperatura, 'Se espera que se devuelva la temperatura mínima para el año mediante la url: ' . $url);
		$this->assertTrue ($max_temperatura >= -40, 'La temperatura máxima debe ser mayor o igual a -40º para el año mediante la url: ' . $url);
		$media_temperatura = isset($response_json['media_temperatura'])?$response_json['media_temperatura']:null;
		$this->assertNotNull ($media_temperatura, 'Se espera que se devuelva la temperatura media para el año mediante la url: ' . $url);
		$this->assertTrue ($media_temperatura >= -40, 'La temperatura media debe ser mayor o igual a -40º para el año mediante la url: ' . $url);
		$media_horas_sol = isset($response_json['media_horas_sol'])?$response_json['media_horas_sol']:null;
		$this->assertNotNull ($media_horas_sol, 'Se espera que se devuelva la media de horas de sol diarias para el año mediante la url: ' . $url);
		$this->assertTrue ($media_horas_sol >= 0, 'La media de horas de sol diarias debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
		$max_horas_sol = isset($response_json['max_horas_sol'])?$response_json['max_horas_sol']:null;
		$this->assertNotNull ($max_horas_sol, 'Se espera que se devuelva las máximas de horas de sol diarias para el año mediante la url: ' . $url);
		$this->assertTrue ($max_horas_sol >= 0, 'El máximo de horas de sol diarias debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
		$sum_horas_sol = isset($response_json['sum_horas_sol'])?$response_json['sum_horas_sol']:null;
		$this->assertNotNull ($sum_horas_sol, 'Se espera que se devuelva las suma de horas de sol diarias para el año mediante la url: ' . $url);
		$this->assertTrue ($sum_horas_sol >= 0, 'La suma de horas de sol diarias debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
		$media_radiacion = isset($response_json['media_radiacion'])?$response_json['media_radiacion']:null;
		$this->assertNotNull ($media_radiacion, 'Se espera que se devuelva la media de la radiación solar diaria para el año mediante la url: ' . $url);
		$this->assertTrue ($media_radiacion >= 0, 'La media de la radiación solar diaria debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
		$max_radiacion = isset($response_json['max_radiacion'])?$response_json['max_radiacion']:null;
		$this->assertNotNull ($max_radiacion, 'Se espera que se devuelva el máximo de la radiación solar diaria para el año mediante la url: ' . $url);
		$this->assertTrue ($max_radiacion >= 0, 'El máximo de la radiación solar diaria debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
		$sum_radiacion = isset($response_json['sum_radiacion'])?$response_json['sum_radiacion']:null;
		$this->assertNotNull ($sum_radiacion, 'Se espera que se devuelva la suma de la radiación solar diaria para el año mediante la url: ' . $url);
		$this->assertTrue ($sum_radiacion >= 0, 'La suma de la radiación solar diaria debe ser mayor o igual a 0 para el año mediante la url: ' . $url);
	
	}
	
	function testInforiegoGetDatosPrecipitacionAnualesForLatitudeAndLongitudeAndNoYearAndOthers() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
		
		$medida = "PRECIPITACION";
		$numeroDeAnios = 3;
		$intervalo = "month";
		$formato = "M";
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud=". $latitud . "&longitud=" . $longitud .
		"&medida=" . $medida . "&numeroDeAnios=" . $numeroDeAnios . "&intervalo=" . $intervalo . "&formato=" . $formato;
		
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$cols = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($cols, 'Se espera que se devuelvan las etiquetas de las columnas mediante la url: ' . $url);
		$this->assertTrue (count($cols) >= 2, 'Las columnas devueltas deben ser como mínimo la columna con los nombres (por ejemplo "Mes") y la columna con cada dato (por ejemplo año 2014)   mediante la url: ' . $url);
		
		$rows = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($rows, 'Se espera que se devuelvan filas para las columnas mediante la url: ' . $url);
		$this->assertTrue (count($rows) >= 1, 'Al menos una fila con datos   mediante la url: ' . $url);
	
	}
	
	function testInforiegoGetDatosTemperaturaAnualesForLatitudeAndLongitudeAndNoYearAndOthers() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
		
		$medida = "TEMPMEDIA";
		$numeroDeAnios = 3;
		$intervalo = "day";
		$formato = "DDD";
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud=". $latitud . "&longitud=" . $longitud .
		"&medida=" . $medida . "&numeroDeAnios=" . $numeroDeAnios . "&intervalo=" . $intervalo . "&formato=" . $formato;
	
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$cols = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($cols, 'Se espera que se devuelvan las etiquetas de las columnas mediante la url: ' . $url);
		$this->assertTrue (count($cols) >= 2, 'Las columnas devueltas deben ser como mínimo la columna con los nombres (por ejemplo "Mes") y la columna con cada dato (por ejemplo año 2014)   mediante la url: ' . $url);
	
		$rows = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($rows, 'Se espera que se devuelvan filas para las columnas mediante la url: ' . $url);
		$this->assertTrue (count($rows) >= 1, 'Al menos una fila con datos   mediante la url: ' . $url);
	
	}
	
	function testInforiegoGetDatosHorasSolAnualesForLatitudeAndLongitudeAndNoYearAndOthers() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
	
		$medida = "N";
		$numeroDeAnios = 3;
		$intervalo = "day";
		$formato = "DDD";
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud=". $latitud . "&longitud=" . $longitud .
		"&medida=" . $medida . "&numeroDeAnios=" . $numeroDeAnios . "&intervalo=" . $intervalo . "&formato=" . $formato;
	
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$cols = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($cols, 'Se espera que se devuelvan las etiquetas de las columnas mediante la url: ' . $url);
		$this->assertTrue (count($cols) >= 2, 'Las columnas devueltas deben ser como mínimo la columna con los nombres (por ejemplo "Mes") y la columna con cada dato (por ejemplo año 2014)   mediante la url: ' . $url);
	
		$rows = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($rows, 'Se espera que se devuelvan filas para las columnas mediante la url: ' . $url);
		$this->assertTrue (count($rows) >= 1, 'Al menos una fila con datos   mediante la url: ' . $url);
	
	}
	
	function testInforiegoGetDatosRadiacionAnualesForLatitudeAndLongitudeAndNoYearAndOthers() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
	
		$medida = "RADIACION";
		$numeroDeAnios = 3;
		$intervalo = "day";
		$formato = "DDD";
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=datosMedidaPorAnio&latitud=". $latitud . "&longitud=" . $longitud .
		"&medida=" . $medida . "&numeroDeAnios=" . $numeroDeAnios . "&intervalo=" . $intervalo . "&formato=" . $formato;
	
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$cols = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($cols, 'Se espera que se devuelvan las etiquetas de las columnas mediante la url: ' . $url);
		$this->assertTrue (count($cols) >= 2, 'Las columnas devueltas deben ser como mínimo la columna con los nombres (por ejemplo "Mes") y la columna con cada dato (por ejemplo año 2014)   mediante la url: ' . $url);
	
		$rows = isset($response_json['cols'])?$response_json['cols']:null;
		$this->assertNotNull ($rows, 'Se espera que se devuelvan filas para las columnas mediante la url: ' . $url);
		$this->assertTrue (count($rows) >= 1, 'Al menos una fila con datos   mediante la url: ' . $url);
	
	}
	
	function tetstInforiegoActualizaDatosDiariosInforiegoForLatitudeAndLongitude() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
	
		$latitud = 40.439983;
		$longitud = - 5.737026;
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=actualizaDiario&latitud=". $latitud . "&longitud=" . $longitud;
			
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$result = isset($response_json['result'])?$response_json['result']:null;
		$this->assertTrue ($result == "success", 'Actualiza correctamente  mediante la url: ' . $url);
		
	}
	
	function tetstInforiegoActualizaDatosDiariosInforiegoForAllStations() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=actualizaDiario";
			
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$result = isset($response_json['result'])?$response_json['result']:null;
		$this->assertTrue ($result == "success", 'Actualiza correctamente  mediante la url: ' . $url);
	
	}
	
	function tetstInforiegoActualizaDatosHorariosInforiegoForAllStations() {
		//obtenDatosPorAnio(medida, numeroDeAnios, intervalo, formato) en parcela.js
		$latitud = 40.439983;
		$longitud = - 5.737026;
		
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/inforiego_rest.php?accion=actualizaRecord&fecha_ini=01/07/2016&latitud=" . $latitud . "&longitud=" . $longitud;
			
		$response = $this->getResponse($url);
	
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error . ' al parsear ' . $response);
		$result = isset($response_json['result'])?$response_json['result']:null;
		$this->assertTrue ($result == "success", 'Actualiza correctamente  mediante la url: ' . $url);
	
	}
	
	
}
?>