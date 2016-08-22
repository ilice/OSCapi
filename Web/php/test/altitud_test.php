<?php

require_once( __DIR__ . '/../../../vendor/simpletest/simpletest/autorun.php');


class TestOfAltitud extends UnitTestCase {
	function __construct() {
		parent::__construct ( 'Altitud test' );
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
	
	function testAltitudGetPlotAltitudeForLatitudeAndLongitude() {
		
		$latitud = 40.439983;
		$longitud = - 5.737026;
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"";
		$web_folder = ($server_name == "localhost")? "Web/":"";
		$url = $server_name . "/" . $web_folder . "php/altitud.php?locations=" . $latitud . "," . $longitud;
		
		
		$response = $this->getResponse($url);
		
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo');
		$status = $response_json['status'];
		$this->assertEqual ($status, "OK", 'El estado de la respuesta es OK');
		$results = $response_json['results'];
		$this->assertNotNull ($results, 'Se hace la llamada interna para obtener la altitud');
		$this->assertTrue(count($results) == 1, 'Hay un resultado de altitud para las coordenadas dadas');
		$this->assertIsA($results[0]['elevation'], 'double' , 'Devuelve correctamente la altitud');
		
	}
	
	function testAltitudGetErrorOnMissingParameters() {
			
		$latitud = 40.439983;
		$longitud = - 5.737026;
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"";
		$web_folder = ($server_name == "localhost")? "Web/":"";
		$url = $server_name . "/" . $web_folder . "php/altitud.php?locations=" . $latitud . ",";
	
		$response = $this->getResponse($url);
	
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo');
		$status = $response_json['status'];
		$this->assertEqual ($status, "INVALID_REQUEST", 'El estado de la respuesta es petición inválida');
		$results = $response_json['results'];
		$this->assertNotNull ($results, 'Se hace la llamada interna para obtener la altitud');
		$this->assertTrue(count($results) == 0, 'No hay resultados de altitud porque las coordenadas no están completas');
		$this->assertNotNull($response_json['error_message'], 'Devuelve un mensaje de error');
		
		
		$url = $server_name . "/" . $web_folder . "php/altitud.php?locations=" . "," . $longitud;
		
		$response = $this->getResponse($url);
		
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo');
		$status = $response_json['status'];
		$this->assertEqual ($status, "INVALID_REQUEST", 'El estado de la respuesta es petición inválida');
		$results = $response_json['results'];
		$this->assertNotNull ($results, 'Se hace la llamada interna para obtener la altitud');
		$this->assertTrue(count($results) == 0, 'No hay resultados de altitud porque las coordenadas no están completas');
		$this->assertNotNull($response_json['error_message'], 'Devuelve un mensaje de error');
		
		$url = $server_name . "/" . $web_folder . "php/altitud.php?locations=" . ",";
		
		$response = $this->getResponse($url);
		
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo');
		$status = $response_json['status'];
		$this->assertEqual ($status, "INVALID_REQUEST", 'El estado de la respuesta es petición inválida');
		$results = $response_json['results'];
		$this->assertNotNull ($results, 'Se hace la llamada interna para obtener la altitud');
		$this->assertTrue(count($results) == 0, 'No hay resultados de altitud porque las coordenadas no están completas');
		$this->assertNotNull($response_json['error_message'], 'Devuelve un mensaje de error');
	
	}
	
	function testAltitudServiceExistsAndIsOnline() {
				
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"";
		$web_folder = ($server_name == "localhost")? "Web/":"";
		$url = $server_name . "/" . $web_folder . "php/altitud.php?";
		
		$response = $this->getResponse($url);
		
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo');
		$status = $response_json['status'];
		$this->assertEqual ($status, "INVALID_REQUEST", 'El estado de la respuesta es petición inválida');
		$results = $response_json['results'];
		$this->assertNotNull ($results, 'Se hace la llamada interna para obtener la altitud');
		$this->assertTrue(count($results) == 0, 'No hay resultados de altitud porque las coordenadas no están completas');
		$this->assertNotNull($response_json['error_message'], 'Devuelve un mensaje de error');
		
	}
}
?>