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
