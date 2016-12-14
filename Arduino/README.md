# OpenSmartCountry
Open Smart Country - Campo Inteligente Abierto
http://opensmartcountry.com/

El proyecto Open Smart Country se compone de varios módulos, uno de ellos es una estación realizada con Arduino que se ocupa de recoger datos sobre el terreno y enviarlos a la web para que sean mostrados en la aplicación.
En este apartado se encuentra el código que se utiliza en la estación y de momento está sepatado en varias carpetas según la parte que se está desarrollando. La última versión del software que lleva el módulo está en openSmartCountryGPRS, el resto de carpetas contienen proyectos que aislan partes para comprender su funcionamiento y hacer más rápido el desarrollo.

## SIM800L
Para el envío de datos desde el campo será necesario establecer una comunicación móvil, no habrá WiFi, para ello lo más barato que he encontrado es el módulo SIM800L y de momento lo he conectado con el Arduino UNO.
En este proyecto simplemente se prueba el funcionamiento del Arduino con la SIM800L.

## openSmartCountrySensor
El proyecto consiste en dos sensores que envían los valores de temperatura y nivel de luz mediante MQTT a AWS IoT, una regla hace que los valores que se envían se guarden en una tabla en una base de datos DynamoBD
En este caso se utiliza un Arduino Yun que permite la conexión mediante Wi-Fi. No es el objetivo final pero es interesante para entender cómo funciona la arquitectura en modelos más avanzados de IoT.

## openSmartCountryGPRS
Este proyecto consiste en el envío a internet de datos de nivel de humedad, temperatura, nivel de luz, nivel de humedad del suelo, existencia de precipitaciones y nivel de precipitación mediante una conexión gprs. Utiliza baterías y placas solares aunque aún se necesita pulir un poco el tema de la alimentación.

## openSmartCountryMoistureSensor
Proyecto básico con el sensor de humedad, simplemente saca por consola los valores que este sensor recoge.

## openSmartCountryWIFI
Hace prácticamente lo mismo que openSmartCountryGPRS, pero conectándose por WIFI, es decir, si tienes una red WIFI cercana esta puede ser la mejor opción. El prototipo funciona ahora mismo conectado a la corriente eléctrica doméstica.

El código está muy cogido con pinzas, iré limpiándolo y mejorándolo bastante, de momento simplemente funciona ;)
Tal cual está, con todos los cables y sin fuente de alimentación alternativa, no se puede utilizar. En eso trabajaré en el futuro más inmediato.


