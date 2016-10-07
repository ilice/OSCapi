<?php

// (string) $message - message to be passed to Slack
// (string) $room - room in which to write the message, too
// (string) $icon - You can set up custom emoji icons to use with each message
function slack($message, $room = "errors", $icon = ":hankey:") {
	$room = ($room) ? $room : "errors";
	
	$data = json_encode ( array (
			"channel" => "#{$room}",
			"text" => utf8_encode ( $message ),
			"icon_emoji" => $icon 
	) );
	
	// You can get your webhook endpoint from your Slack settings
	$ch = curl_init ( $GLOBALS ['config'] ['slackHookEndpoint']);
	curl_setopt ( $ch, CURLOPT_POST, 1 );
	curl_setopt ( $ch, CURLOPT_POSTFIELDS, array (
			'payload' => $data 
	) );
	curl_setopt ( $ch, CURLOPT_RETURNTRANSFER, true );
	curl_setopt ( $ch, CURLOPT_SSL_VERIFYPEER, 0 );
	
	$result = curl_exec ( $ch );
	
	curl_close ( $ch );
	
	if ($result == "invalid_payload") {
		
		$data = json_encode ( array (
				"channel" => "#{$room}",
				"text" => "Error al mostrar el error",
				"icon_emoji" => $icon 
		) );
		
		$ch = curl_init ( "https://hooks.slack.com/services/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" );
		curl_setopt ( $ch, CURLOPT_POST, 1 );
		curl_setopt ( $ch, CURLOPT_POSTFIELDS, array (
				'payload' => $data 
		) );
		curl_setopt ( $ch, CURLOPT_RETURNTRANSFER, true );
		curl_setopt ( $ch, CURLOPT_SSL_VERIFYPEER, 0 );
		
		$result = curl_exec ( $ch );
		
		curl_close ( $ch );
	}
	
	return $result;
}

?>