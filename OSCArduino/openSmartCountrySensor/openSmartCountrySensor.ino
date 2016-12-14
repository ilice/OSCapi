#include <aws_iot_mqtt.h>
#include <aws_iot_version.h>
#include "aws_iot_config.h"

aws_iot_mqtt_client myClient; //inicio el cliente mqtt
char str_tempValue[5];
char msg[100]; //bufer de escritura para el mensaje JSON a enviar
bool success_connect = false; //indicador para saber si está o no conectado
int error_counter = 0;
bool debug_mode = false;

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
    error_counter++;
  }
  return ret;
}

//Constantes que fijan los pines en los que están conectados los sensores
const int lightSensor = A0;
const int tempSensor = A1;

//Variables para guardar el valor del sensor en cada intervalo de medida
int lightValue = 0;
float tempValue = 0.0;

// Función para sacar datos que cambien en el shadow, por ejemplo si se modifican desde una app, de momento no la usamos
//void msg_callback_delta(char* src, int len) {
//}

void setup() {
  // Inicializa el Serial para la salida y espera hasta que está activo
  Serial.begin(115200);
  if (debug_mode) {
    while (!Serial);
  }

  //Saca por el serial la versión del SDK de Amazon que estamos utilizando, los valores están en el archivo aws_iot_version.h en la carpeta de la librería
  char curr_version[80];
  sprintf(curr_version, "AWS IoT SDK Version(dev) %d.%d.%d-%s\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_TAG);
  Serial.println(curr_version);

  conectTOAWSIoT();
}

void loop() {

  lightValue = analogRead(lightSensor);

  float voltage = (analogRead(tempSensor) / 1024.0) * 5.0;
  tempValue = (voltage - .5) * 100.0;

  if (success_connect) {

    dtostrf(tempValue, 4, 1, str_tempValue);
    str_tempValue[4] = '\0';
    
    //Se construye el mensaje en formato JSON con los valores de temperatura y luz
    sprintf(msg, "{\"state\":{\"reported\":{\"Temp\": %s, \"Light\": %d}}}", str_tempValue, lightValue);

    //Se actualiza la shadow
    print_log("shadow update", myClient.shadow_update(AWS_IOT_MY_THING_NAME, msg, strlen(msg), NULL, 5));

    print_log("yield", myClient.yield());

    delay(2000);

    if (error_counter >= 10) {
      Serial.println(F("Too many failures: reset connection"));
      success_connect = false;
      //TODO de momento no hago el disconnect porque no funciona, en todo caso si él por las pruebas parece que no va mal la nueva conexión, lo que no se es si se estará acumulando algo que no deba
      //print_log("disconnect", myClient.disconnect());
      conectTOAWSIoT();
    }
  }
}

void conectTOAWSIoT() {
  while (!success_connect) {
    //Configura el cliente
    if (print_log("setup", myClient.setup(AWS_IOT_CLIENT_ID))) {
      //Se carga la configuración de usuario que está especificada en el archivo aws_iot_config.h
      if ((print_log("config", myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH)))) {
        //Se intenta conectar con la configuración redeterminada: 60 segundos
        if (print_log("connect", myClient.connect())) {
          success_connect = true;
          error_counter = 0;
          // Mediante la conexión, se inicializa el shadow y se registra la delta function
          print_log("shadow init", myClient.shadow_init(AWS_IOT_MY_THING_NAME));
          // De momento no se utiliza la parte de actuzlización desde un sitio externo, por eso se deja comentada esta parte
          //print_log("register thing shadow delta function", myClient.shadow_register_delta_func(AWS_IOT_MY_THING_NAME, msg_callback_delta));
        }
      }
    }
  }
}
