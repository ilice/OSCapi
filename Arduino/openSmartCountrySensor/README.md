# OpenSmartCountry
Open Smart Country - Campo Inteligente Abierto
http://opensmartcountry.com/

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

