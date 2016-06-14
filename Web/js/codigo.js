var query;

function obten(campo,anio, tipomedida,variable) {
	
	var url = "https://script.google.com/macros/s/AKfycbwbli8yqu-YzY5t2O0v98XROuAv1cT5K7mF4slKDCpIdEsGd28/exec?anio=" + anio + "&variable=" + variable +"&tipomedida=" +tipoMedida;
	
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		document.getElementById(campo).innerHTML = response[variable][tipomedida].value.toFixed(2);
	});
}


function actualiza() {
	var url = "https://script.google.com/macros/s/AKfycbyJ1Qb6CIlZYvW6poU-qAl2MPoEVD-kws2frLnsmOScu-ezbwA/exec?accion=actualiza&latitud="+document.getElementById("latitud").innerHTML+"&longitud="+document.getElementById("longitud").innerHTML;
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});
}
	

function cargaDatos(){

		obtenEstacion();
		actualiza();
		//obten(2016);
		google.charts.load('current', {'packages': ['table', 'bar', 'corechart']});
		google.charts.setOnLoadCallback(graficoPrecipitacionPorMesYAnio);
		google.charts.setOnLoadCallback(graficoTemperaturasMediasDiurnas);
		google.charts.setOnLoadCallback(graficoHorasDeSolDiarias);
		google.charts.setOnLoadCallback(graficoRadiacionNetaDiaria);

		google.charts.setOnLoadCallback(cargaMedidaDiasDeLluvia);
		google.charts.setOnLoadCallback(cargaMedidaPrecipitacionAcumulada);
		google.charts.setOnLoadCallback(cargaMedidaMaximaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMinimaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMediaTemperaturaDiurna);
		google.charts.setOnLoadCallback(cargaMedidaMediaHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaMaximoHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaAcumuladoHorasSolDiarias);
		google.charts.setOnLoadCallback(cargaMedidaMaximoRadiacionDiaria);
		google.charts.setOnLoadCallback(cargaMedidaMediaRadiacionDiaria);
		google.charts.setOnLoadCallback(cargaMedidaAcumuladoRadiacionDiaria);
		

}



		//document.getElementById("diasDeLluvia").innerHTML = response["precipitacionDiaria"]["numeroDeElementosMayoresQueCero"].value.toFixed(2);
		//document.getElementById("pecipitacionacumulada").innerHTML = response["precipitacionDiaria"]["acumulado"].value.toFixed(2);
		// document.getElementById("maximaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["maximo"].value.toFixed(2);
		// document.getElementById("minimaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["minimo"].value.toFixed(2);
		// document.getElementById("mediaTemperaturaDiurna").innerHTML = response["temperaturaMediaDiurna"]["media"].value.toFixed(2);
		// document.getElementById("mediaHorasSolDiarias").innerHTML = response["horasDeSolDiarias"]["media"].value.toFixed(2);
		// document.getElementById("maximasHorasSolDiarias").innerHTML = response["horasDeSolDiarias"]["maximo"].value.toFixed(2);
		// document.getElementById("horasSolAcumuladas").innerHTML = response["horasDeSolDiarias"]["acumulado"].value.toFixed(2);
		// document.getElementById("maximoRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["maximo"].value.toFixed(2);
		// document.getElementById("mediaRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["media"].value.toFixed(2);
		// document.getElementById("acumuladoRadiacionNetaDiaria").innerHTML = response["radiacionNeta"]["acumulado"].value.toFixed(2);


function obtenEstacion(){
	
	var url = "https://script.google.com/macros/s/AKfycbyJ1Qb6CIlZYvW6poU-qAl2MPoEVD-kws2frLnsmOScu-ezbwA/exec?accion=obtenEstacion&latitud=40.440005&longitud=-5.737003";
	
	
	var request = jQuery.ajax({
			crossDomain : true,
			url : url,
			method : "GET",
			dataType : "json"
		});

	
	request.done(function (response, textStatus, jqXHR) {
		document.getElementById("estacion").innerHTML = response["ESTACION"];

	});
}



    function graficoPrecipitacionPorMesYAnio() {
		
		
      var queryPrecipitacionPorMesYAnio = encodeURIComponent('select month(J) + 1, sum(AA) group by month(J) pivot B');

      var queryCompletaPrecipitacionPorMesYAnio = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryPrecipitacionPorMesYAnio);
      queryCompletaPrecipitacionPorMesYAnio.send(trataRespuestaPrecipitacionPorMesYAnio);
    }

    function trataRespuestaPrecipitacionPorMesYAnio(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Precipitaciones mensuales',
            subtitle: 'Comparativa acumulado mensual últimos años',
          },
          bars: 'vertical',
          colors: [ '#94E8B4' ,'#72BDA3', '#5E8C61',  '#426A4D', '#4E6151', '#3B322C','#7246F2' ],
		  hAxis: { ticks: [1,2,3,4,5,6,7,8,9,10,11,12] , title: 'Mes'}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.ColumnChart(document.getElementById('graficoPrecipitacionPorMesYAnio'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	 function graficoTemperaturasMediasDiurnas() {
		
		
      var queryTemperaturasMediasDiurnas = encodeURIComponent('select C, sum(AH) where B >= 2014 group by C pivot B');

      var queryCompletaTemperaturasMediasDiurnas = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryTemperaturasMediasDiurnas);
      queryCompletaTemperaturasMediasDiurnas.send(trataRespuestaTemperaturasMediasDiurnas);
    }

    function trataRespuestaTemperaturasMediasDiurnas(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Temperaturas medias diurnas',
            subtitle: 'Comparativa temperatura media diurna últimos años',
          },
		  explorer: {},
          colors: ['#7F0D0B', '#BF1411','#400706' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoTemperaturaMediaDiurna'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }

	
	function graficoHorasDeSolDiarias() {
		
		
      var queryHorasDeSolDiarias = encodeURIComponent('select C, sum(V) where B >= 2014 group by C pivot B');

      var queryCompletaHorasDeSolDiarias = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryHorasDeSolDiarias);
      queryCompletaHorasDeSolDiarias.send(trataRespuestaHorasDeSolDiarias);
    }

    function trataRespuestaHorasDeSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Horas de Sol Diarias',
            subtitle: 'Comparativa horas de sol diarias',
          },
		  explorer: {},
          colors: ['#BFA71F', '#7F6F15','#FFDF2A' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoHorasDeSolDiarias'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	function graficoRadiacionNetaDiaria() {
		
		
      var queryRadiacionNetaDiaria = encodeURIComponent('select C, sum(AB) where B >= 2014 group by C pivot B');

      var queryCompletaRadiacionNetaDiaria = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryRadiacionNetaDiaria);
      queryCompletaRadiacionNetaDiaria.send(trataRespuestaRadiacionNetaDiaria);
    }

    function trataRespuestaRadiacionNetaDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Radiación neta diaria en MJ/m&#178',
            subtitle: 'Comparativa radiación neta diaria',
          },
		  explorer: {},
          colors: ['#BF480A', '#FF600D','#E5570C' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoRadiacionNetaDiaria'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	
	
	function graficoRadiacionNetaDiaria() {
		
		
      var queryRadiacionNetaDiaria = encodeURIComponent('select C, sum(AB) where B >= 2014 group by C pivot B');

      var queryCompletaRadiacionNetaDiaria = new google.visualization.Query(
          'https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryRadiacionNetaDiaria);
      queryCompletaRadiacionNetaDiaria.send(trataRespuestaRadiacionNetaDiaria);
    }

    function trataRespuestaRadiacionNetaDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }


		var opciones = {
          chart: {
            title: 'Radiación neta diaria en MJ/m&#178',
            subtitle: 'Comparativa radiación neta diaria',
          },
		  explorer: {},
          colors: ['#BF480A', '#FF600D','#E5570C' ],
		  hAxis: {title: 'Día del año', gridlines:{count: 12} },
		  series: {
			  0: {
				
				  lineWidth : 1
				
			  },
			  1: {
				
				  lineWidth : 1
				
			  },
			  2: {
				
				  lineWidth : 2
				
			  }
			}
		};
		
      var datos = respuesta.getDataTable();
	  
	  var grafica = new google.visualization.LineChart(document.getElementById('graficoRadiacionNetaDiaria'));
      //chart.draw(data, google.charts.Bar.convertOptions(options));
	  grafica.draw(datos, opciones);
    }
	
	
	function cargaMedidaDiasDeLluvia() {
				
      var queryEncoded = encodeURIComponent('select count(AA) where B = 2016 and AA>0 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaDiasDeLluvia);
    }

    function trataRespuestaDiasDeLluvia(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('diasDeLluvia').innerHTML = datos.getValue(0,0).toFixed(2);;
    }
			

	
	function cargaMedidaPrecipitacionAcumulada() {
				
      var queryEncoded = encodeURIComponent('select sum(AA) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaPrecipitacionAcumulada);
    }

    function trataRespuestaPrecipitacionAcumulada(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('pecipitacionacumulada').innerHTML = datos.getValue(0,0).toFixed(2);;
    }

	function cargaMedidaMaximaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select max(AG) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximaTemperaturaDiurna);
    }

    function trataRespuestaMaximaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMinimaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select min(AI) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMinimaTemperaturaDiurna);
    }

    function trataRespuestaMinimaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('minimaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaTemperaturaDiurna() {
				
      var queryEncoded = encodeURIComponent('select avg(AH) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaTemperaturaDiurna);
    }

    function trataRespuestaMediaTemperaturaDiurna(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaTemperaturaDiurna').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select avg(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaHorasSolDiarias);
    }

    function trataRespuestaMediaHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaHorasSolDiarias').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMaximoHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select max(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximoHorasSolDiarias);
    }

    function trataRespuestaMaximoHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximasHorasSolDiarias').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaAcumuladoHorasSolDiarias() {
				
      var queryEncoded = encodeURIComponent('select sum(V) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaAcumuladoHorasSolDiarias);
    }

    function trataRespuestaAcumuladoHorasSolDiarias(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('horasSolAcumuladas').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMaximoRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select max(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMaximoRadiacionDiaria);
    }

    function trataRespuestaMaximoRadiacionDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('maximoRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaMediaRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select avg(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaMediaRadiacionlDiaria);
    }

    function trataRespuestaMediaRadiacionlDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('mediaRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	}
	
	function cargaMedidaAcumuladoRadiacionDiaria() {
				
      var queryEncoded = encodeURIComponent('select sum(AB) where B = 2016 group by B');

      var queryCompleted = new google.visualization.Query('https://docs.google.com/spreadsheets/d/1_Vn8rU9GaedJ6aSVmldOQpeFL0vLcP8HpIEIQv8hofc/gviz/tq?gid=0&headers=1&tq=' + queryEncoded);
      queryCompleted.send(trataRespuestaAcumuladoRadiacionDiaria);
    }

    function trataRespuestaAcumuladoRadiacionDiaria(respuesta) {
      if (respuesta.isError()) {
        alert('Error en query: ' + respuesta.getMessage() + ' ' + respuesta.getDetailedMessage());
        return;
      }
		
      var datos = respuesta.getDataTable();
	  
	  document.getElementById('acumuladoRadiacionNetaDiaria').innerHTML = datos.getValue(0,0).toFixed(2);
	}