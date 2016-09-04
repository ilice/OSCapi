<?php

require_once( __DIR__ . '/../../../vendor/simpletest/simpletest/autorun.php');


class TestOfCatastro extends UnitTestCase {
	function __construct() {
		parent::__construct ( 'Catastro test' );
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

	function testCatastroGetRCForLatitudeAndLongitude() {
		//obtenDatosCatastro() en parcela.js
		$latitud = 40.439983;
		$longitud = - 5.737026;
		$end_point = "OVCCoordenadas.asmx/Consulta_RCCOOR";
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/catastro.php?end_point=". $end_point . "&SRS=EPSG:4326&Coordenada_X=" . $longitud .
		"&Coordenada_Y=" . $latitud;

		$response = $this->getResponse($url);

		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_xml=simplexml_load_string($response);
		$this->assertNotEqual ( $response_xml , false , 'Debe ser xml y parsearse correctamente. Parseando: ' . $response . " para la url: " . $url);
		$this->assertEqual ($response_xml->control[0]->cuerr, 0, 'No debe haber errores  para la url: ' . $url . ' y hay ' . $response_xml->control[0]->cuerr);
		$this->assertEqual ($response_xml->control[0]->cucoor, 1, 'Debe haber un resultado para la url: ' . $url . ' y hay ' . $response_xml->control[0]->cucoor);
		$this->assertEqual ($response_xml->coordenadas->count(), 1, 'Debe haber un resultado para la url: ' . $url . ' y hay ' . $response_xml->coordenadas->count());
		$this->assertNotNull ($response_xml->coordenadas[0]->coord[0]->pc[0]->pc1[0], 'Debe existir el elemento pc1 para la url: ' . $url);
		$this->assertNotNull ($response_xml->coordenadas[0]->coord[0]->pc[0]->pc2[0], 'Debe existir el elemento pc2 para la url: ' . $url);
		$this->assertNotNull ($response_xml->coordenadas[0]->coord[0]->ldt[0], 'Debe existir el elemento ldt para la url: ' . $url);
		
	}
	
	function testCatastroGetProvinciaForRC() {
		//obtenProvincia() en parcela.js
		$codigoProvincia = 37;
		$end_point = "OVCCallejero.asmx/ConsultaProvincia";
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/catastro.php?end_point=". $end_point;
	
		$response = $this->getResponse($url);
	
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_xml=simplexml_load_string($response);
		$this->assertNotEqual ( $response_xml , false , 'Debe ser xml y parsearse correctamente. Parseando: ' . $response . " para la url: " . $url);
		$this->assertTrue ($response_xml->provinciero->prov->count() >= 48, 'Debe haber como mínimo 48 provincias para la url: ' . $url . ' y hay ' . $response_xml->provinciero->prov->count());
		$provincia_encontrada = false;
		foreach ($response_xml->provinciero->prov as $provincia) {
			if ($provincia->cpine = $codigoProvincia) {
				$provincia_encontrada = true;
			};
		}
		$this->assertTrue ($provincia_encontrada, 'Debe haber datos para la provincia ' . $codigoProvincia . ' para la url: ' . $url );
		
	}
	
	function testCatastroGetMunicipioForRC() {
		//obtenMunicipio() en parcela.js
		$codigoMunicipio = 284;
		$nombre_provincia = "SALAMANCA";
		$end_point = "OVCCallejero.asmx/ConsultaMunicipio";
		
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/catastro.php?end_point=". $end_point . "&Provincia=" . $nombre_provincia . "&Municipio=";
		
		$response = $this->getResponse($url);
	
		$this->assertNotNull ( $response, 'Hay respuesta');
		$response_xml=simplexml_load_string($response);
		$this->assertNotEqual ( $response_xml , false , 'Debe ser xml y parsearse correctamente. Parseando: ' . $response . " para la url: " . $url);
		$this->assertTrue ($response_xml->municipiero->muni->count() >= 362, 'Debe haber como mínimo 362 municipios para la url: ' . $url . ' y hay ' . $response_xml->municipiero->muni->count());
		$municipio_encontrado = false;
		foreach ($response_xml->municipiero->muni as $municipio) {
			if ($municipio->cpine = $codigoMunicipio) {
				$municipio_encontrado = true;
			};
		}
		$this->assertTrue ($municipio_encontrado, 'Debe haber datos para la provincia ' . $codigoMunicipio . ' para la url: ' . $url );
	
	}
	
	function testCatastroGetDatosCatastroForRC() {
		//obtenDatosPorReferenciaCatastral() en parcela.js
		$rc = "37284A00600098";
		$end_point = "OVCCallejero.asmx/Consulta_DNPRC";
	
		$server_name = !empty($_SERVER['SERVER_NAME'])?$_SERVER['SERVER_NAME']:"http://localhost:8080";
		$web_folder = "Web/";
		$url = $server_name . "/" . $web_folder . "php/catastro.php?end_point=". $end_point . "&Provincia=&Municipio=&RC=" . $rc;
		
 		$response = $this->getResponse($url);
	
 		$this->assertNotNull ( $response, 'Hay respuesta');
 		$response_xml=simplexml_load_string($response);
 		$this->assertNotEqual ( $response_xml , false , 'Debe ser xml y parsearse correctamente. Parseando: ' . $response . " para la url: " . $url);
 		$this->assertTrue ($response_xml->bico[0]->bi[0]->idbi[0]->cn[0] == "RU", 'El tipo (cn) de la parcela debe ser RU para la url: ' . $url . ' y es ' . $response_xml->bico[0]->bi[0]->idbi[0]->cn[0]);
 		$this->assertTrue (strlen($response_xml->bico[0]->bi[0]->dt[0]->locs[0]->lors[0]->lorus[0]->npa) > 0, 'La parcela tiene que tener nombre de localización para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->lspr[0]->spr[0]->dspr[0]->ccc) > 0, 'La parcela tiene que tener ccc para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->lspr[0]->spr[0]->dspr[0]->dcc) > 0, 'La parcela tiene que tener dcc para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->lspr[0]->spr[0]->dspr[0]->ip) > 0, 'La parcela tiene que tener ip para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->lspr[0]->spr[0]->dspr[0]->ssp) > 0, 'La parcela tiene que tener ssp para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->bi[0]->dt[0]->loine[0]->cp) > 0, 'La parcela tiene que tener cp para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->bi[0]->dt[0]->cmc) > 0, 'La parcela tiene que tener cmc para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->bi[0]->dt[0]->locs[0]->lors[0]->lorus[0]->cpp[0]->cpo) > 0, 'La parcela tiene que tener cpo para la url: ' . $url );
 		$this->assertTrue (strlen($response_xml->bico[0]->bi[0]->dt[0]->locs[0]->lors[0]->lorus[0]->cpp[0]->cpa) > 0, 'La parcela tiene que tener cpa para la url: ' . $url );
	
	}

}
?>