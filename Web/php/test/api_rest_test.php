<?php
header ( "Content-Type: text/html; charset=UTF-8" );

require_once( __DIR__ . '/../../../vendor/simpletest/simpletest/autorun.php');

class TestOfapi_rest extends UnitTestCase {
	function __construct() {
		parent::__construct ( 'Api rest test' );
	}
	function getResponse($url, $data = NULL) {
		$handler = curl_init ( $url );
		
		if (! empty ( $data )) {
			curl_setopt ( $handler, CURLOPT_POST, 1 );
			curl_setopt ( $handler, CURLOPT_POSTFIELDS, $data );
		}
		
		curl_setopt ( $handler, CURLINFO_HEADER_OUT, true );
		curl_setopt ( $handler, CURLOPT_RETURNTRANSFER, true );
		curl_setopt ( $handler, CURLOPT_CONNECTTIMEOUT, 0 );
		
		$response = curl_exec ( $handler );
		return $response;
	}
	function testApi_restServiceExistsAndIsOnline() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php?";
		
		$response = $this->getResponse ( $url );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
	}
	function testObtieneDatosDelCultivoPorId() {
		$cultivo_id = 19;
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc?q=_id:" . $cultivo_id;
		
		$response = $this->getResponse ( $url );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta respondepara la url: ' . $url );
		$this->assertEqual ( $results ['total'], 1, 'Hay un y solo un cultivo por id en la base de datos' );
		$this->assertEqual ( $results ['hits'] [0] ['_source'] ["Clave"], "$cultivo_id", 'La clave que obtengo es udual al id' );
	}
	function testObtieneCultivosPaginados() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
		
		$data = '{"from" : 0,"size" : 6	}';
		
		$response = $this->getResponse ( $url, $data );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url . ' con los datos ' . $data);
		$this->assertTrue ( count ( $results ['hits'] ) <= $tamanioDePagina, 'El m�ximo de cultivos por página es ' . $tamanioDePagina );
		$this->assertTrue ( count ( $results ['hits'] ) > 0, 'Hay cultivos en la p�gina ' );
	}
	function testBuscaPorPalabra() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
		$palabra = 'lechuga';
		
		$data = '{"from" : 0,"size" : 6	, "query": { "match": { "_all": "' . $palabra . '" } } } }';
		
		$response = $this->getResponse ( $url, $data );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( utf8_encode ( $response ), true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$this->assertTrue ( count ( $results ['hits'] ) <= $tamanioDePagina, 'El m�ximo de cultivos por p�gina es ' . $tamanioDePagina );
		$this->assertTrue ( count ( $results ['hits'] ) > 0, 'Hay cultivos en la p�gina ' );
		$posicion = strpos ( $response, $palabra );
		$this->assertTrue ( $posicion !== false, 'La palabra ' . $palabra . "est� en los resultados" );
	}
	function testBuscaPorFraseExacta() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
		$frase = "chile de árbol";
		
		$data = '{"from" : 0,"size" : ' . $tamanioDePagina . '	, "query": { "match_phrase": { "_all": "' . $frase . '" } } } }';
		
		$response = $this->getResponse ( $url, $data );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( $response, true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$hits = $results ['hits'];
		$this->assertTrue ( count ( $hits ) <= $tamanioDePagina, 'El máximo de cultivos por p�gina es ' . $tamanioDePagina );
		$this->assertTrue ( count ( $hits ) > 0, 'Hay cultivos en la página ' );
		foreach ( $hits as $hit ) {
			$posicion = strpos ( json_encode ( $hit, JSON_UNESCAPED_UNICODE ), $frase );
			$this->assertTrue ( $posicion !== false, 'La frase ' . $frase . "está en los resultados" );
		}
	}
	function testBuscaPorPalabras() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
		$frase = "chile de árbol";
		
		$data = '{"from" : 0,"size" : ' . $tamanioDePagina . '	, "query": { "match": { "_all": "' . $frase . '" } } } }';
		
		$response = $this->getResponse ( $url, $data );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( $response, true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$hits = $results ['hits'];
		$this->assertTrue ( count ( $hits ) <= $tamanioDePagina, 'El máximo de cultivos por página es ' . $tamanioDePagina );
		$this->assertTrue ( count ( $hits ) > 1, 'Hay mas de un cultivo en la página ' );
		$enAlgunCasoNoApareceLaFraseCompleta = false;
		$enAlgunCasoApareceLaFraseCompleta = false;
		foreach ( $hits as $hit ) {
			$posicion = $this->apareceAlgunaPalabraEnTexto ( json_encode ( $hit, JSON_UNESCAPED_UNICODE ), explode ( " ", $frase ) );
			$this->assertTrue ( $posicion !== false, 'La frase ' . $frase . "está en los resultados" );
			if (! strpos ( json_encode ( $hit, JSON_UNESCAPED_UNICODE ), $frase )) {
				$enAlgunCasoNoApareceLaFraseCompleta = true;
			} else {
				$enAlgunCasoApareceLaFraseCompleta = true;
			}
		}
		$this->assertTrue ( $enAlgunCasoNoApareceLaFraseCompleta, "Alguno de los cultivos que encuentra no tiene la frase exacta sino alguna de las palabras" );
		$this->assertTrue ( $enAlgunCasoApareceLaFraseCompleta, "Encuentra el cultivo que tiene la frase completa" );
	}
	function apareceAlgunaPalabraEnTexto($texto, $palabras) {
		$esta = false;
		foreach ( $palabras as $palabra ) {
			if (strpos ( $texto, $palabra )) {
				$esta = true;
			}
			;
		}
		return $esta;
	}
	function testBuscaPorAltitud() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
		
		$altitud = 900;
		$data = '{
		"from" : 0,
		"size" : ' . $tamanioDePagina . ',
				 "query": 
		{
			"constant_score" : {
			"filter" : {
			"bool": {
			"must": [
			{"range" : {
				"altitude.min" : {
				"lte"  : ' . $altitud . '
			}
			}},
			{"range" : {
				"altitude.max" : {
				"gte" : ' . $altitud . '
			}
			}}
		
			]
		}
		}
		}
		}
						}}';
		
		$response = $this->getResponse ( $url, $data );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( $response, true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$hits = $results ['hits'];
		$this->assertTrue ( count ( $hits ) <= $tamanioDePagina, 'El máximo de cultivos por página es ' . $tamanioDePagina );
		$this->assertTrue ( count ( $hits ) > 0, 'Hay cultivos para esa altitud' );
		
		foreach ($hits as $hit) {
			$estaEnAlgunRango = false;
			foreach ($hit["_source"]["altitude"] as $rangoAltitud) {
				if (isset($rangoAltitud["min"]) and isset($rangoAltitud["max"]) and $rangoAltitud["min"] <= $altitud and $altitud <= $rangoAltitud["max"] ) {
					$estaEnAlgunRango = true;
				};
			}
			$this->assertTrue($estaEnAlgunRango, "La altitud de referencia está comprendida en alguno de los rangos de altitudes del cultivo");
		}
		
		
	}
	
	function testNoTenemosPlantasMaritimas() {
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/osc";
		$tamanioDePagina = 6;
	
		$altitud = -1;
		$data = '{
		"from" : 0,
		"size" : ' . $tamanioDePagina . ',
				 "query":
		{
			"constant_score" : {
			"filter" : {
			"bool": {
			"must": [
			{"range" : {
				"altitude.min" : {
				"lte"  : ' . $altitud . '
			}
			}},
			{"range" : {
				"altitude.max" : {
				"gte" : ' . $altitud . '
			}
			}}
	
			]
		}
		}
		}
		}
						}}';
	
		$response = $this->getResponse ( $url, $data );
	
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( $response, true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = $response_json ['hits'];
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$hits = $results ['hits'];
		$this->assertEqual ( count ( $hits ) , 0, 'No hay cultivos para esa altitud' );
	
		foreach ($hits as $hit) {
			$estaEnAlgunRango = false;
			foreach ($hit["_source"]["altitude"] as $rangoAltitud) {
				if ($rangoAltitud["min"] < $altitud and $altitud <$rangoAltitud["max"] ) {
					$estaEnAlgunRango = true;
				};
			}
			$this->assertTrue($estaEnAlgunRango, "La altitud de referencia está comprendida en alguno de los rangos de altitudes del cultivo");
		}
	
	
	}
	
	function testBuscaPorReferenciaCatastral(){
		
		$referenciaCatastral = "372840000000600098";
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/" ;
		$url = $server_name . "/" . $web_folder . "php/api_rest.php/plots/sigpac_record/_search?q=c_refpar:" . $referenciaCatastral;
		
		$response = $this->getResponse ( $url );
		
		$this->assertNotNull ( $response, 'Hay respuesta' );
		$response_json = json_decode ( $response, true );
		$error = json_last_error_msg ();
		$this->assertEqual ( $error , 'No error' , 'Es json y no hay errores al parsearlo, error: ' . $error );
		$results = isset($response_json ['hits'])?$response_json ['hits']:NULL;
		$this->assertNotNull ( $results, 'Se hace la llamada interna a la base de datos y esta responde para la url: ' . $url );
		$hits = $results ['hits'];
		$this->assertEqual ( count ( $hits ) , 1, 'Existen datos para la referencia catastral' );
		$this->assertTrue(count($hits[0]["_source"]["points"]["coordinates"][0]) >= 2 , "Tiene suficientes coordenadas para que sea un recinto");
		
		
	}
}
?>