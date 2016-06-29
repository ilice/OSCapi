# OpenSmartCountry
Open Smart Country - Campo Inteligente Abierto
http://opensmartcountry.com/


## openSmartCountryWIFI
Este proyecto consiste en el envío a internet de datos de nivel de humedad, temperatura, nivel de luz, nivel de humedad del suelo, existencia de precipitaciones y nivel de precipitación mediante una conexión gprs. Ahora mismo la alimentación es con una batería y enchufado a la red, pero la idea es hacerlo completamente autónomo.

Para ello se utiliza un Arduino Yun conectado a una red WIFI, tiene varios sensores que recogen la información y cada 10 minutos se envían las medidas tomadas a una excel del Google Docs. La forma de que la información llegue es invocando a una aplicación web que hace de servicio REST para la hoja y mediante una llamada GET los datos se insertan.

La aplicación Web se ha realizado publicando un Web App desde el App Scripst de Google https://developers.google.com/apps-script/guides/web y siguiendo el [siguiente tutorial y sus enlaces](https://mashe.hawksey.info/2014/07/google-sheets-as-a-database-insert-with-apps-script-using-postget-methods-with-ajax-example/) de [Martin Hawksey (Google Developer Expert (Apps Script) and Open Education advocate)](https://plus.google.com/+MartinHawksey)

![Conexión entre Arduino UNO, SIM800L y los distintos sensores](https://raw.githubusercontent.com/teanocrata/OpenSmartCountry/master/Arduino/openSmartCountryGRPS/IMG_20160513_084707.jpg)

### Hardware necesario
* [Arduino Yun](https://www.arduino.cc/en/Main/ArduinoBoardYun) El original cuesta alrededor de 75€ en España, compatibles alrededor de 25€ (no los he probado).
* Sensor de Temperatura y humedad ambiente DHT11. Hay muchas posibilidades, yo compré [este]( http://www.ebay.es/itm/201568844366?_trksid=p2060353.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) por la misma razón
* Sensor de humedad del suelo, vale cualquiera, a partir de poco más de 1 euro, yo compré [este](http://www.miniinthebox.com/es/humedad-del-suelo-modulo-de-masa-del-sensor-sensor-de-humedad_p903362.html) pero tardó la vida en llegarme :(
* Resistencia fotoeléctrica: Yo he utilizado una que tenía de un kit, son muy baratas, por unos 20 céntimos aunque es un poco raro comprar una, normalmente van en [paquetes de 10](http://www.ebay.es/itm/10pcs-Resistor-Dependiente-De-Luz-LDR-Fotoresistor-GL5528-Photoresistor-/231670562385?hash=item35f0a43e51:g:9GQAAOSwZ1lWdOrZ) y te puede llegar a cosar lo mismo una que 5 que 10. No se qué tal de calidades.
* Dos resistencias de 10kOhmios, por 1 euro [compras 50](http://www.ebay.es/itm/50x-Resistencias-10K-ohm-5-0-25W-1-4W-carbon-film-resistor-/201479741197?hash=item2ee920df0d:g:1nEAAOSwnH1WY~3a), yo las tenía de algún kit, no he tenido que comprarlas
* Cables de conexión: yo compré [estos](https://www.amazon.es/gp/product/B00QV7O052/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1) por comodidad, es un pack y sale cada uno a unos 20 centimos, seguro que los hay bastante más baratos y los de cualquier kit sirven.
 
### Entorno
* IDE de Arguino https://www.arduino.cc/en/Main/Software
* Google sheets con una cuenta de Google https://www.google.com/intl/es_es/sheets/about/
* Librería de Adafruit para el DHT11: https://github.com/adafruit/DHT-sensor-library En realidad ha sido por comodidad, probablemente quite esta dependencia más adelante
* Opcional Fritzing para ver los esquemas http://fritzing.org/home/

### Configuración
* Para la configuración de la hoja de cálculo en la que se insertarán los datos se puede seguir el tutorial en https://mashe.hawksey.info/2014/07/google-sheets-as-a-database-insert-with-apps-script-using-postget-methods-with-ajax-example y la información de la página de Google Developers al respecto https://developers.google.com/apps-script/guides/web
* Para las conexiones se pueden seguir las fotos y diagramas de la carpeta https://github.com/teanocrata/OpenSmartCountry/tree/master/Arduino/openSmartCountryGRPS, he intentado mantener los colores de los cables en las fotos y en los diagramas para que sea más sencillo seguirlos y la colocación es similar. Como algunas piezas no existían he utilizado piezas genéricas en su lugar. Para abrir el archivo fzz se necesita el programa Fitzing que es open source.
* Es necesario modificar en el archivo openSmartCountry.ino el IMEI y la url del Web App que despliegues en la hoja de google (línea 11), así como los valores del apn si no es de vodafone (repito, la uso porque la tengo, no quiero dar publicidad ni nada por el estilo ;P).
* Se sube al arduino y en unos istandes debería ponerse a enviar los datos cada 10 minutos
* Mi hoja con los datos se puede ver en [Hoja Google Sheets](https://docs.google.com/spreadsheets/d/16x3sa6vjrsbSCxvWsbqzeB8cXcGHCy72oyrKOePZ0hI/edit?usp=sharing)
 
