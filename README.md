# OpenSmartCountry
Open Smart Country - Campo Inteligente Abierto
http://opensmartcountry.com/

## SIM800L
Para el envío de datos desde el campo será necesario establecer una comunicación móvil, no habrá WiFi, para ello lo más barato que he encontrado es el módulo SIM800L y de momento lo he conectado con el Arduino UNO
### Hardware necesario:
* Arduino UNO
* Batería de 3.7 a 4.2 V, de momento estoy utilizando una de un móvil viejo
* Módulo SIM800L 
* Protoboard y algunos cables
* Una tarjeta SIM, estoy utilizando una 4G de Pepephone y de momento funciona perfectamente
* Soldador y estaño, la SIM800L me llegó sin los pines ni la antena soldados, además para la corriente de la batería tambien he soldado los cables para evitar problemas

### Entorno
IDE de Arduino

### Configuración
En el código de ejemplo [BasicSIM800L.ino](https://github.com/teanocrata/OpenSmartCountry/blob/master/Arduino/SIM800L/BasicSIM800L/BasicSIM800L.ino) está descrito el esquema que he usado, es muy simple

![Conexión básica entre Arduino UNO y SIM800L](https://raw.githubusercontent.com/teanocrata/OpenSmartCountry/master/Arduino/SIM800L/BasicSIM800L/IMG_20160504_201456.jpg "Conexión básica entre Arduino UNO y SIM800L")

### Referencias interesantes
Están también en el código pero de momento simplemente uso:
* SoftwareSerial.h de Arduino: https://www.arduino.cc/en/Reference/SoftwareSerial
* Guía de comandos AT de la página del chip: http://simcomm2m.com/UploadFile/TechnicalFile/SIM800%20Series_AT%20Command%20Manual_V1.09.pdf Es necesario estar registrado para descargarla pero no hay ningún requisito más y actualmente no funciona ni la visualización ni la descarga desde el Chrome, desde Firefox unciona todo correctamente, incluso con el enlace anterior no hace falta estar registrado. Es interesante entrar en la página y registrarse ya que hay bastante información más. También está subida en [OpenSmartCountry/Arduino/SIM800L/BasicSIM800L/BasicSIM800L.ino](https://raw.githubusercontent.com/teanocrata/OpenSmartCountry/master/Arduino/SIM800L/BasicSIM800L/BasicSIM800L.ino)


## openSmartCountrySensor
El proyecto consiste en dos sensores que envían los valores de temperatura y nivel de luz mediante MQTT a AWS IoT, una regla hace que los valores que se envían se guarden en una tabla en una base de datos DynamoBD

### Hardware necesario:
* Arduino Yun
* Sensor de temperatura TMP36
* Fotoresistencia
* Resistencia de 10 kiloohmnios
* Protoboard
* Cables de puente
 
### Entorno
* IDE Arduino: Fundamental, no instalarlo, descomprimirlo
* MQTT.fx para las pruebas
* Cuenta en AWS

### Configuración
* Para configurar la placa Arduino Yun https://www.arduino.cc/en/Guide/ArduinoYun
* Para los esquemas de los sensores se pueden ver los ejemplos 3 y 4 del Libro de Proyectos Arduino
* Para el entorno en AWS seguir la guia http://docs.aws.amazon.com/es_es/iot/latest/developerguide/what-is-aws-iot.html
* Para el SDK de AWS IoT para Arduino seguir la guia https://github.com/aws/aws-iot-device-sdk-arduino-yun


## openSmartCountryGPRS
Este proyecto consiste en el envío a internet de datos de nivel de humedad, temperatura, nivel de luz, nivel de humedad del suelo, existencia de precipitaciones y nivel de precipitación mediante una conexión gprs. Ahora mismo la alimentación es con una batería y enchufado a la red, pero la idea es hacerlo completamente autónomo.

Para ello se utiliza un Arduino Uno con una SIM800L para conectarse a internet (con una SIM de vodafone en este caso), tiene varios sensores que recogen la información y cada 10 minutos se envían las medidas tomadas a una excel del Google Docs. La forma de que la información llegue es invocando a una aplicación web que hace de servicio REST para la hoja y mediante una llamada GET los datos se insertan.

La aplicación Web se ha realizado publicando un Web App desde el App Scripst de Google https://developers.google.com/apps-script/guides/web y siguiendo el [siguiente tutorial y sus enlaces](https://mashe.hawksey.info/2014/07/google-sheets-as-a-database-insert-with-apps-script-using-postget-methods-with-ajax-example/) de [Martin Hawksey (Google Developer Expert (Apps Script) and Open Education advocate)](https://plus.google.com/+MartinHawksey)

### Hardware necesario
* [Arduino Uno](https://www.arduino.cc/en/Main/ArduinoBoardUno) El original cuesta alrededor de 20€, los chinos desde 3,80, no los he probado, el mio es original.
* [Módulo SIM800L montado](http://www.ebay.es/itm/SIM800L-GPRS-GSM-Module-PCB-Antenna-SIM-Board-Quad-band-for-MCU-Arduino-/182101355688?) Entre 7 y 13 euros, este es chino directamente, también hay opciones en Adafruit por ejemplo, algo más desarrollados y bastante más caros. Yo compré el del enlace porque lo enviaban desde España y me llegaba muy rápido (la impaciencia me puede).
* Batería para el SIM800L Yo estoy utilizando una de un móvil viejo, tiene que cumplir las especificaciones del módulo, la que uso es una de Li-iOn de 3,7V con una capacidad de 1800mAh que está bastante cascada (el móvil aguanta 1 hora encendido aprox.), y funciona sin problema.
* Sensor de Temperatura y humedad ambiente DHT11. Hay muchas posibilidades, yo compré [este]( http://www.ebay.es/itm/201568844366?_trksid=p2060353.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT) por la misma razón
* Sensor de humedad del suelo, vale cualquiera, a partir de poco más de 1 euro, yo compré [este](http://www.miniinthebox.com/es/humedad-del-suelo-modulo-de-masa-del-sensor-sensor-de-humedad_p903362.html) pero tardó la vida en llegarme :(
* Resistencia fotoeléctrica: Yo he utilizado una que tenía de un kit, son muy baratas, por unos 20 céntimos aunque es un poco raro comprar una, normalmente van en [paquetes de 10](http://www.ebay.es/itm/10pcs-Resistor-Dependiente-De-Luz-LDR-Fotoresistor-GL5528-Photoresistor-/231670562385?hash=item35f0a43e51:g:9GQAAOSwZ1lWdOrZ) y te puede llegar a cosar lo mismo una que 5 que 10. No se qué tal de calidades.
* Dos resistencias de 10kOhmios, por 1 euro [compras 50](http://www.ebay.es/itm/50x-Resistencias-10K-ohm-5-0-25W-1-4W-carbon-film-resistor-/201479741197?hash=item2ee920df0d:g:1nEAAOSwnH1WY~3a), yo las tenía de algún kit, no he tenido que comprarlas
* Cables de conexión: yo compré [estos](https://www.amazon.es/gp/product/B00QV7O052/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1) por comodidad, es un pack y sale cada uno a unos 20 centimos, seguro que los hay bastante más baratos y los de cualquier kit sirven.
* Tarjeta SIM: Yo estoy utilizando una de Vodafone porque la teníamos en casa sin utilizar por una de esas ofertas, pero vale cualquiera, pordré las configuraciones para otras tarjetas más adelante. Gasta muy pocos datos. (También pondré cuantos exactamente cuando haga más pruebas)
 
### Entorno
* IDE de Arguino https://www.arduino.cc/en/Main/Software
* Google sheets con una cuenta de Google https://www.google.com/intl/es_es/sheets/about/
* Librería de Adafruit para el DHT11: https://github.com/adafruit/DHT-sensor-library En realidad ha sido por comodidas, probablemente quite esta dependencia más adelante
* Opcional Fritzing para ver los esquemas http://fritzing.org/home/

### Configuración
* Para la configuración de la hoja de cálculo en la que se insertarán los datos se puede seguir el tutorial en https://mashe.hawksey.info/2014/07/google-sheets-as-a-database-insert-with-apps-script-using-postget-methods-with-ajax-example y la información de la página de Google Developers al respecto https://developers.google.com/apps-script/guides/web
* Para las conexiones se pueden seguir las fotos y diagramas, he intentado mantener los colores de los cables en las fotos y en los diagramas para que sea más sencillo seguirlos y la colocación es similar. Como algunas piezas no existían he utilizado piezas genéricas en su lugar. Para abrir el archivo fzz se necesita el programa Fitzing que es open source.
* Es necesario modificar en el archivo openSmartCountry.ino la línea del pin de la tarjeta SIM que uses (línea 6) y la url del Web App que despliegues en la hoja de google (línea 11), así como los valores del apn si no es de vodafone (repito, la uso porque la tengo, no quiero dar publicidad ni nada por el estilo ;P).
* Se sube al arduino y en unos istandes debería ponerse a enviar los datos cada 10 minutos
 

El código está muy cogido con pinzas, iré limpiándolo y mejorándolo bastante, de momento simplemente funciona ;)


