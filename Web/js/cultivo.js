<!DOCTYPE HTML>
<html>
	<head>
		<meta charset="UTF-8"/>
		<title>Open Smart Country - Cultivos</title>
		<meta name="viewport" content="width=device-width, initial-scale=1"/>
		<meta name="keywords" content="Open Smart Country, Agrotech, IoT, Analitycs, Open Data, Cultivos"/>
		<meta name="description" content="Información específica sobre un cultivo determinado"/>
		<meta name="author" content="Isabel Muñoz @teanocrata"/>
		<link rel="stylesheet" href="http://www.w3schools.com/lib/w3.css"/>
		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway"/>
		<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.6.3/css/font-awesome.min.css"/>
		<link rel="stylesheet" href="css/estilo.css"/>	
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js"></script>
		<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
		<script type="text/javascript" src="https://www.google.com/jsapi"></script>
		<script src="js/cultivo.js"  type="text/javascript"></script>
		<script>
		  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
		  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
		  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
		  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
		  ga('create', 'UA-74247467-2', 'auto');
		  ga('send', 'pageview');
		</script>
	</head>
	<body>

		<!-- Barra de navegación superior -->	
		<nav class="w3-top">
			<div class="w3-navbar w3-container w3-padding-0" id="myNavbar">
				<img class="w3-padding-large w3-opacity w3-left" src="img/OpenSmartCountry_logo_25x26.png" alt="Open Smart Country logo" />
				<a id="openNav" href="#" class="w3-padding-large w3-left" onclick="w3_open()">HOME</a>
				<div class="w3-padding-large w3-right w3-right"><span id="rc"></span></div>
			</div>
		</nav>

		<!-- Sidenav/menu -->
		<script src="js\codigoBarraLateral.js"></script>
		<!-- TODO: arreglar esta chapuza. Necesito saber si se ha cargado previamente la librería de google para pintar los mapas porque si se ha hecho no puedo volver a cargarla y si no se ha hecho tengo que hacerlo. Para eso guardo aquí si se ha cargado o no.-->
		<div id="isGoogleChartsCorechartLoaded" style="display:none">false</div>
		<nav id="mySidenav" class="w3-sidenav  w3-card-8 w3-animate-left" style="z-index:3;width:300px;display:none">
			<div class="w3-container  ">
				<div class="w3-row w3-right">
					<div class="w3-col w3-right">
						<a href="index.html" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge"><i class="fa fa-home"></i></a>
						<a href="mapaDeParcelas.html" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge"><i class="fa fa-globe"></i></a>
						<a href="#" class="w3-hover-none w3-hover-text-dark-grey w3-show-inline-block w3-xxlarge" onclick="w3_close()"><i class="fa fa-remove"></i></a>
					</div>
				</div>
			</div>
			<hr/>

			<div class="w3-container w3-row w3-padding-16">
				<div class="w3-col s4">
					<img src="img/avatar_vinia.PNG" class="w3-circle w3-margin-right" style="width:46px" alt="Avatar Viña de la Estación"/>
				</div>
				<div class="w3-col s8">
					<span>Bienvenidos a <strong>La Viña de la Estación</strong></span><br/>
					<a href="#" class="w3-hover-none w3-hover-text-red w3-show-inline-block"><i class="fa fa-envelope"></i></a>
					<a href="#" class="w3-hover-none w3-hover-text-green w3-show-inline-block"><i class="fa fa-user"></i></a>
					<a href="#" class="w3-hover-none w3-hover-text-blue w3-show-inline-block"><i class="fa fa-cog"></i></a>
				</div>
			</div>
			<hr/>

			<div class="w3-container" id="panelNavegacion">
				<h5>Panel de navegación</h5>
			</div>

			<a href="#" class="w3-padding w3-blue" onclick="w3_close();"><i class="fa fa fa-television fa-fw"></i>  General</a>
			<a href="#catastro" class="w3-padding" onclick="document.getElementById('catastro').style.display='block';w3_close();"><i class="fa fa-institution fa-fw"></i>  Catastro</a>
			<a href="#tarjetaMapa" class="w3-padding" onclick="document.getElementById('tarjetaMapa').style.display='block';w3_close();"><i class="fa fa-map fa-fw"></i>  Mapa</a>
			<a href="#cacharrito" class="w3-padding" onclick="document.getElementById('cacharrito').style.display='block';w3_close();"><i class="fa fa-map-pin"></i>  Sensores en la parcela</a>
			<a href="#precipitacion" class="w3-padding" onclick="document.getElementById('precipitacion').style.display='block';w3_close();"><i class="fa fa-tint fa-fw"></i>  Precipitaciones</a>
			<a href="#temperatura" class="w3-padding" onclick="document.getElementById('temperatura').style.display='block';w3_close();"><i class="fa fa-eyedropper fa-fw"></i>  Temperatura</a>
			<a href="#sol" class="w3-padding" onclick="document.getElementById('sol').style.display='block';w3_close();"><i class="fa fa-certificate fa-fw"></i>  Sol</a>
			<a href="#radiacion" class="w3-padding" onclick="document.getElementById('radiacion').style.display='block';w3_close();"><i class="fa fa-rss fa-fw"></i>  Radiacion</a>
			<a href="#informacion" class="w3-padding" onclick="document.getElementById('informacion').style.display='block';w3_close();"><i class="fa fa-info fa-fw"></i>  Información</a>

			<div  id="regions_div"  style="width: 100%; height: auto;" ></div>


		</nav>

		<!-- Overlay effect when opening sidenav on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->

		<div class="w3-main" >
		</div>

		<!-- Footer -->
		<footer class="w3-center w3-dark-grey w3-padding-48 w3-hover-black">
			<div class="w3-xlarge w3-padding-32">
				<a href="https://www.facebook.com/isabelmunozordonez" class="w3-hover-text-indigo w3-show-inline-block"><i class="fa fa-facebook-official"></i></a>
				<a href="https://twitter.com/teanocrata" class="w3-hover-text-light-blue w3-show-inline-block"><i class="fa fa-twitter"></i></a>
				<a href="https://www.linkedin.com/in/m-isabel-muñoz-ordóñez-588a8b92" class="w3-hover-text-indigo w3-show-inline-block"><i class="fa fa-linkedin"></i></a>
				<a href="https://github.com/teanocrata/OpenSmartCountry" class="w3-hover-text-indigo w3-show-inline-block"><i class="fa fa-github"></i></a>
			</div>
			<a class="w3-right w3-padding-medium" rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">
				<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" />
			</a>
		</footer>

		<!-- Botón FAB al estilo material design-->
		<div class="contenedor w3-container">
			<ul class="w3-ul w3-center" >
				<li class="sinBorde"><button class="btn botonF5 w3-btn-floating w3-dark-grey" onclick="document.getElementById('suscripcion').style.display='block'"><i class="fa fa-envelope-o"></i></button></li>
				<li class="sinBorde"><button class="btn botonF5 w3-btn-floating w3-dark-grey" onclick="location.href='mapaDeParcelas.html'"><i class="fa fa-map-marker"></i></button></li>
				<li class="sinBorde"><button class="btn botonF4 w3-btn-floating w3-dark-grey" onclick="location.href='oscar.html'"><i class="fa fa-wifi"></i></button></li>
				<li class="sinBorde"><button class="btn botonF3 w3-btn-floating w3-dark-grey" onclick="location.href='viniaDeLaEstacion.html'"><i class="fa fa-unlock-alt"></i></button></li>
				<li class="sinBorde"><button class="btn botonF2 w3-btn-floating w3-dark-grey" onclick="document.getElementById('analytics').style.display='block'"><i class="fa fa-line-chart"></i></button></li>
				<li class="sinBorde"><button class="botonF1 w3-btn-floating-large w3-dark-grey" id="botonMas"><i class="fa fa-plus"></i></button></li>
			</ul>
		</div>
		<script src="js\codigoFAB.js"></script>
		<!-- Ventana modal con el contenido de analitycs hasta que tengamos algo que mostrar -->
		<div id="analytics" class="w3-modal">
			<div class="w3-modal-content">
				<div class="w3-container">
					<span onclick="document.getElementById('analytics').style.display='none'" class="w3-closebtn">&times;</span>
					<p class="w3-center">Para esto vamos a necesitar un poco más de tiempo, pero esperamos tener una primera versión en breve para que puedas hacerte una idea del potencial que tiene.</p>
					<p class="w3-center">Si quieres más información, tienes curiosidad o te apetece participar, no dudes en contactar con <a href="mailto:isabel@opensmartcountry.com">nosotros</a>.</p>
				</div>
			</div>
		</div>
		<!--Ventana de suscripción -->
		<div id="suscripcion" class="w3-modal">
			<div class="w3-modal-content">
				<div class="w3-container w3-padding w3-center">
					<span onclick="document.getElementById('suscripcion').style.display='none'" class="w3-closebtn">&times;</span>
					<p>Si quieres que te avisemos con los avances que realicemos, déjanos tu correo y te informaremos.</p>
					<p>Sólo lo utilizaremos para eso, <strong>nada de Spam</strong>, y puedes darte de baja cuando quieras.</p>
					<p>Rellene el siguiente formulario para suscribirse.</p>
					<form class="w3-container" enctype="application/x-www-form-urlencoded" action="http://opensmartcountry.ip-zone.com/ccm/subscribe/index/form/9ljsfx841o" method="post">
						<dl class="zend_form">
							<dt id="groups-label"> </dt>
							<dd id="groups-element">
								<input class="w3-input" type="hidden" name="groups[]" value="1"/>
							</dd>

							<dt id="name-label">
								<label for="name" class="optional w3-label w3-text-grey">Nombre</label>
							</dt>
							<dd id="name-element">
								<input type="text" class="w3-input" name="name" id="name" value=""/>
							</dd>

							<dt id="email-label">
								<label for="email" class="required w3-label w3-validate w3-text-grey">Email</label>
							</dt>
							<dd id="email-element">
								<input type="email" class="w3-input" name="email" id="email" value="" required/>
							</dd>				

							<dt id="submit-label"> </dt>
							<dd id="submit-element">
								<button type="submit" name="submit" id="submit" class="w3-btn w3-dark-grey w3-margin-top" onClick="ga('send', 'event', 'Subscripciones', 'suscribirse', 'OK');">Mantenme al tanto</button>
							</dd>

						</dl>
					</form>
				</div>
			</div>
		</div>
		<!-- Fin bloque botón FAB al estilo material design-->

	</body>
</html>