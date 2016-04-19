#include <aws_iot_mqtt.h>
#include <aws_iot_version.h>
#include "aws_iot_config.h"

aws_iot_mqtt_client myClient; //inicio el cliente mqtt
char msg[100]; //bufer de lectura y escritura para el mensaje a enviar TODO pasarlo a un mensaje por cada sensor
int rc = -100; //valor devuelto por la librería al realizar las peticiones
bool success_connect = false; //indicador para saber si está o no conectado

// Función de log
bool print_log(char* src, int code) {
  bool ret = true;
  if (code == 0) {
    Serial.print(F("[INFO] command: "));
    Serial.print(src);
    Serial.println(F(" completed."));
    ret = true;
  }
  else {
    Serial.print(F("[ERROR] command: "));
    Serial.print(src);
    Serial.println(F(" code: "));
    Serial.print(code);
    ret = false;
  }
  return ret;
}



//Constantes que fijan los pines en los que están conectados los sensores
const int lightSensor = A0;
const int tempSensor = A1;

//Variables para guardar el valor del sensor en cada intervalo de medida
int lightValue = 0;
float tempValue = 0.0;
float desiredTemp = 70.0;
char float_buf[5];


// Función para sacar el dato de temperatura del mensaje
void msg_callback_delta(char* src, int len) {
  String data = String(src);

  int st = data.indexOf("\"state\":") + strlen("\"state\":");
  int ed = data.indexOf(",\"metadata\":");
  String delta = data.substring(st, ed);

  st = delta.indexOf("\"Temp\":") + strlen("\"Temp\":");
  ed = delta.indexOf("}");
  String delta_data = delta.substring(st, ed);
  desiredTemp = delta_data.toFloat();
}

char topic[80];

void setup() {
  // Inicializa el Serial para la salida y espera hasta que está activo
  Serial.begin(115200);
  while (!Serial);

  //Saca por el serial la versión del SDK de Amazon que estamos utilizando, los valores están en el archivo aws_iot_version.h en la carpeta de la librería
  char curr_version[80];
  sprintf(curr_version, "AWS IoT SDK Version(dev) %d.%d.%d-%s\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_TAG);
  Serial.println(curr_version);

  //Construye el nombre del topic en el que se va a publicar la información
  sprintf(topic, "%s/%s", AWS_IOT_CLIENT_ID, AWS_IOT_MY_THING_NAME);

  while (!success_connect) {
    //Configura el cliente
    //En todo momento se va guardando en la variable rc el resultado de la llamada a la librería para poder saber por qué falla
    if (print_log("setup", myClient.setup(AWS_IOT_CLIENT_ID))) {
      //Se carga la configuración de usuario que está especificada en el archivo aws_iot_config.h
      if ((print_log("config", myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH)))) {
        //Se intenta conectar con la configuración redeterminada: 60 segundos
        if (print_log("connect", myClient.connect())) {
          success_connect = true;
          // Mediante la conexión, se inicializa el shadow y se registra la delta function
          print_log("shadow init", myClient.shadow_init(AWS_IOT_MY_THING_NAME));
          print_log("register thing shadow delta function", myClient.shadow_register_delta_func(AWS_IOT_MY_THING_NAME, msg_callback_delta));
        }
      }
    }
  }
}

void loop() {

  lightValue = analogRead(lightSensor);

  float voltage = (analogRead(tempSensor) / 1024.0) * 5.0;
  tempValue = (voltage - .5) * 100;

  if (success_connect) {

    dtostrf(tempValue, 4, 1, float_buf);
    float_buf[4] = '\0';

    //Se construye el mensaje en formato JSON con los valores de temperatura y luz
    sprintf(msg, "{\"state\":{\"reported\":{\"Temp\":%s}}}", float_buf);

    //Se publica el mensaje en el tópico que se pasa por parámetro
    print_log("shadow update", myClient.shadow_update(AWS_IOT_MY_THING_NAME, msg, strlen(msg), NULL, 5));

    print_log("yield", myClient.yield());

    delay(1000);
  }
}
