<?php
header ( "Access-Control-Allow-Origin: *" );
header ( "Content-Type: application/json; charset=UTF-8" );

require_once 'cUrl.php';
$config = include 'config.php';

// get the HTTP method, path and body of the request
$method = $_SERVER ['REQUEST_METHOD'];
$querystring = ! empty ( $_SERVER ['QUERY_STRING'] ) ? $_SERVER ['QUERY_STRING'] : "";
$request = explode ( '/', trim ( empty ( $_SERVER ['PATH_INFO'] ) ? "" : $_SERVER ['PATH_INFO'], '/' ) );
$input = file_get_contents ( 'php://input' );

$url = $GLOBALS ['config'] ['elasticendpoint'] . "/plots/sigpac/_search";

// $bbox="41.401658195918856,-3.7401386077600485,41.402228979075865,-3.74004553075701";

$bbox = explode ( "=", $querystring ) [1];
$sw_lat = explode ( ",", $bbox ) [0];
$sw_lng = explode ( ",", $bbox ) [1];
$ne_lat = explode ( ",", $bbox ) [2];
$ne_lng = explode ( ",", $bbox ) [3];

// "AG", "ED", "CA", "ZU", "ZV", "ZC"
$input = '{
	"size" : 10000,
   "query": {
      "bool": {
         "must_not": 
            {
               "match": {
                  "uso_sigpac": "AG"
               }
            }
         ,
		"must_not": 
            {
               "match": {
                  "uso_sigpac": "ED"
               }
            }
         ,
		"must_not": 
            {
               "match": {
                  "uso_sigpac": "CA"
               }
            }
         ,
		"must_not": 
            {
               "match": {
                  "uso_sigpac": "ZU"
               }
            }
         ,
		"must_not": 
            {
               "match": {
                  "uso_sigpac": "ZV"
               }
            }
         ,
		"must_not": 
            {
               "match": {
                  "uso_sigpac": "ZC"
               }
            }
         ,
         "must": {
            "geo_bounding_box": {
               "bbox_center": {
                  "bottom_left": {
                     "lat": '.$sw_lat.',
                     "lon": '.$sw_lng.'
                  },
                  "top_right": {
                     "lat": '.$ne_lat.',
                     "lon": '.$ne_lng.'
                  }
               }
            }
         }
      }
   }
}';
$elastic_response = json_decode ( postHttpcUrl ( $url, $input ), true );

$hits = $elastic_response ["hits"] ["hits"];
$features = array ();
foreach ( $hits as $hit ) {
	$nationalCadastralReference = $hit ["_source"] ["c_refpar"];
	$bounded_by = $hit ["_source"] ["bbox"];
	$reference_point = $hit ["_source"] ["bbox_center"];
	$areaValue = $hit ["_source"] ["superficie"] / 1000000;
	$properties = array (
			"nationalCadastralReference" => substr ( $nationalCadastralReference, 0, 5 ) . 'A' . substr ( $nationalCadastralReference, 10, 8 ),
			"bounded_by" => $bounded_by,
			"reference_point" => $reference_point,
			"areaValue" => $areaValue 
	);
	$geometry = dropGeometryCoordinates ( $hit ["_source"] ["points"] );
	$feature = array (
			"type" => "Feature",
			"properties" => $properties,
			"geometry" => $geometry 
	);
	array_push ( $features, $feature );
}

$geoJson = array (
		"type" => "FeatureCollection",
		"features" => $features 
);

$response = json_encode ( $geoJson );
function dropGeometryCoordinates($geometry) {
	$coordinates = $geometry ["coordinates"];
	$droppedGeometry = array (
			"type" => "polygon",
			"coordinates" => dropCoordinates ( $coordinates ) 
	);
	return $droppedGeometry;
}
function dropCoordinates($coordinates) {
	$droppedCoordinates = array ();
	foreach ( $coordinates as $pairOfCoordinates ) {
		if (isACoordinatesPair ( $pairOfCoordinates )) {
			array_push ( $droppedCoordinates, array (
					$pairOfCoordinates [1],
					$pairOfCoordinates [0] 
			) );
		} else {
			array_push ( $droppedCoordinates, dropCoordinates ( $pairOfCoordinates ) );
		}
	}
	;
	return $droppedCoordinates;
}
function isACoordinatesPair($element) {
	$isACoordinatesPair = false;
	if (gettype ( $element ) == 'array') {
		if (gettype ( $element [0] ) != 'array') {
			$isACoordinatesPair = true;
		}
	}
	return $isACoordinatesPair;
}
echo $response;