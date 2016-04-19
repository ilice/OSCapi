#include <aws_iot_mqtt.h>
#include <aws_iot_version.h>
#include "aws_iot_config.h"

aws_iot_mqtt_client myClient; //inicio el cliente mqtt
char msg[32]; //bufer de lectura y escritura para el mensaje a enviar TODO pasarlo a un mensaje por cada sensor
int rc = -100; //valor devuelto por el placeholder?
bool success_connect = false; //indicador para saber si está o no conectado

// Función para sacar por el serial el mensaje
void msg_callback(char* src, int len) {
  Serial.println("CALLBACK:");
  int i;
  for(i=0; i<len; i++){
    Serial.print(src[i]);
  }
  Serial.println("");
}

//Constantes que fijan los pines en los que están conectados los sensores
const int lightSensor = A0;
const int tempSensor = A1;

//Variables para guardar el valor del sensor en cada intervalo de medida
int lightValue = 0;
int tempValue = 0;



void setup() {
  // Inicializa el Serial para la salida y espera hasta que está activo
  Serial.begin(115200);
  while(!Serial);
  
  //Saca por el serial la versión del SDK de Amazon que estamos utilizando, los valores están en el archivo aws_iot_version.h en la carpeta de la librería
  char curr_version[80];
  sprintf(curr_version, "AWS IoT SDK Version(dev) %d.%d.%d-%s\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_TAG);
  Serial.println(curr_version);

  while(!success_connect){
    //Configura el cliente
    //En todo momento se va guardando en la variable rc el resultado de la llamada a la librería para poder saber por qué falla
    if((rc =myClient.setup(AWS_IOT_CLIENT_ID)) == 0) {
      //Se carga la configuración de usuario que está especificada en el archivo aws_iot_config.h
      if((rc=myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH)) ==0){
        //Se intenta conectar con la configuración redeterminada: 60 segundos
        if((rc = myClient.connect()) == 0) {
          success_connect = true;
          // Mediante la conexión, se suscribe al tópico que se le pasa por parámetros
          if((rc=myClient.subscribe("topic2", 1, msg_callback)) != 0) {
            Serial.println(F("Subscribe failed!"));
            Serial.print(rc);
          }
        }
        else {
          Serial.println(F("Connect failed!"));
          Serial.println(rc);
        }
      }
      else {
        Serial.println(F("Config failed!"));
        Serial.print(rc);
      }
    }
    else {
      Serial.println(F("Setup failed!"));
      Serial.println(rc);
    }
    //Delay para asegurar que SUBACK está recibido, puede variar de acuerdo al servidor
    delay(2000);
  }
}

void loop() {

  lightValue = analogRead(lightSensor);
  
  float voltage = (analogRead(tempSensor) / 1024.0) * 5.0;
  tempValue = (voltage - .5) * 100;

  
  if(success_connect){
    //Se construye el mensaje en formato JSON con los valores de temperatura y luz
    sprintf(msg, "{\"temp\": \"%d\",\"light\": \"%d\"}", tempValue,lightValue);
        
    //Se publica el mensaje en el tópico que se pasa por parámetro
    if((rc = myClient.publish("topic2", msg, strlen(msg), 1, false)) != 0){
      Serial.println("Publish failed!");
      Serial.println(rc);
    }

    Serial.println(F("Mensaje a publicar:"));
    Serial.println(msg);

    // Get a chance to run a callback
    if((rc = myClient.yield()) != 0) {
      Serial.println("Yield failed!");
      Serial.println(rc);
    }
  
    delay(1000);
  }
}
