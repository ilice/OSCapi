// En el Pin marcado como NET (antena) en la SIM800L tiene que estar soldada la antena
// En el Pin marcado como VCC (alimentación) tiene que estar conectado el + de una batería de entre 3.7 y 4.2 V
// El Pin marcado como RST (reset) en la SIM800L tiene que estar conectado con el RESET del Arduino UNO
// El Pin marcado como RXD (recepción) en la SIM800L va al PIN11 del Arduino UNO
// El Pin marcado como TXD (transmisión) en la SIM800L va al PIN1p del Arduino UNO
// El Pin marcado como GND (tierra) tiene que estar conectado con el - de una batería de entre 3.7 y 4.2 V y con el GND del Arduino UNO
// En este ejemplo no utilizamos los PIN marcados como RING, DTR, MICP, MICN, SPKP, SPKN de la SIM800L

// Para probar que la SIM800L funciona correctamente enviaremos comandos AT mediante el monitor
// La información de los comandos AT s epuede descargar de la página de SIMCom
// en http://simcomm2m.com/UploadFile/TechnicalFile/SIM800%20Series_AT%20Command%20Manual_V1.09.pdf
// Escribiento AT y pulsando Send debe devolver un OK si todo está bien
// Para ver la cobertura AT+CSQ y pulsando Send debe devolver un +CSQ seguido de unos numeritos, el
// primero un valor de 0 a 99 seún los dBm, un 99 es que no se sabe o no se detecta, el segundo
// en % con un 99 si no es detectable (ver la documentación específica)
// Para ver la carga de la batería  AT+CBC pulsando Send debe devolver un +CBC con unos numeritos,
// el primero dice si está cargando o no o si está terminada de cargar, el segundo el % de carga
// y el tercero el voltaje
// Se puede hacer una llamada con ATD<n>[<msgm>][;] donde n es el número de teléfono al que llamar
// y msgm en I si quieres que no se muestre el número desde el que llamas o i si quieres que si se muestre
// es decir, por ejemplo ATD666555444i; llamará al número 666555444 sin ocultar la identidad
// Es interesante que la tarjeta que se use no tenga el PIN para no tener que pasarlo, si no, se hace con AT+CPIN=<pin>

// https://www.arduino.cc/en/Reference/SoftwareSerial
#include <SoftwareSerial.h>
#include "conf.h"

//SoftwareSerial(rxPin, txPin, inverse_logic)
//Creamos una instancia del objeto SoftwareSerial para conectarnos con el SIM800L,
// en este caso usaremos el PIN10 como rxPin que será el que reciba los datos del
// SIM800L, es decir, el que estatá conectado al TXD en la SIM800L y el PIN11 como
// txPin que será el que transmita los datos, es decir, el que estatá conectado al
// que está marcado como RXD en la SIM800L, inverse_logic es opcional y por defecto
// está a false, si se pone a true, invierte el sentido de los bits de entrada
// tomando LOW en el rxPin como 1-bit y HIGH como 0-bit
SoftwareSerial moduloSIM800L(10, 11);

String origen;

bool conexionSIMCorrecta = false;
bool conexionGPRSCorrecta = false;

char replybuffer[255];
uint8_t readline(uint16_t timeout = 1000, boolean multiline = false);
uint8_t getReply(char *send, uint16_t timeout = 1000);
bool ejecutaComandoYEsperaRespuesta(char *comando, char *respuestaEsperada, int timeout = 1000);
bool print_log(char *src, int code = -1);

void setup()
{
  // Abre el puerto de comunicación entre el Arduino y el ordenador para poder
  //comunicarnos con él a través del monitor (Ctrl+Mayús+M), la velocidad será
  // 9600 bits por segundo, al abrir el monitor es importante que tenga esa
  //velocidad seleccionada
  Serial.begin(9600);
  while (!Serial);
  Serial.println(F("Comunicación por USB con ARDUINO iniciada"));
  delay(1000);

  //Especificamos la velocidad de la comunicación entre el Arduino UNO y la SIM800L
  moduloSIM800L.begin(9600);
  Serial.println(F("Comunicación por serie con SIM800L"));
  //Esperamos 10 segundos a que el módulo de SIM se active completamente
  delay(1000);

  //Configuración básica del módulo con la SIM
  while (!conexionSIMCorrecta) {
    print_log("Comprueba conexión con SIM800L", ejecutaComandoYEsperaRespuesta("AT", "OK", 4000) ? CORRECTO : AT_ERROR);
    print_log("Reinicio con funcionalidad del módulo SIM800L completa", ejecutaComandoYEsperaRespuesta("AT+CFUN=1,1", "OK", 10000) ? CORRECTO : AT_ERROR);
    while (readline(10000, true));
    if (String(replybuffer).indexOf("+CPIN: SIM PIN") < 0) {
      char sendbuff[14] = "AT+CPIN=";
      sendbuff[8] = SIM_PIN[0];
      sendbuff[9] = SIM_PIN[1];
      sendbuff[10] = SIM_PIN[2];
      sendbuff[11] = SIM_PIN[3];
      sendbuff[12] = '\0';
      print_log("Código PIN", ejecutaComandoYEsperaRespuesta(sendbuff, "OK") ? CORRECTO : PIN_ERROR);
      while (readline(10000, true));
      if (String(replybuffer).indexOf("+CPIN: READY") < 0)
        conexionSIMCorrecta = true;
    }
  }

  //Configuración de la conexión a internet
  while (!conexionGPRSCorrecta) {
    print_log("Modo GPRS", ejecutaComandoYEsperaRespuesta("AT+SAPBR=3,1,\"Contype\",\"GPRS\"", "OK") ? CORRECTO : AT_ERROR);
    print_log("APN", ejecutaComandoYEsperaRespuesta("AT+SAPBR=3,1,\"APN\",\"ac.vodafone.es\"", "OK") ? CORRECTO : AT_ERROR);
    print_log("APN user", ejecutaComandoYEsperaRespuesta("AT+SAPBR=3,1,\"USER\",\"vodafone\"", "OK") ? CORRECTO : AT_ERROR);
    print_log("APN pasword", ejecutaComandoYEsperaRespuesta("AT+SAPBR=3,1,\"PWD\",\"vodafone\"", "OK") ? CORRECTO : AT_ERROR);
    print_log("Activación GPRS", ejecutaComandoYEsperaRespuesta("AT+SAPBR=1,1", "OK") ? CORRECTO : AT_ERROR);

    //Comprueba con una petición HTTP
    conexionGPRSCorrecta = peticionURL("www.google.es");
  }

  //  peticionURL("script.google.com/macros/s/AKfycbyAMTjQueuBn3adO1b_fCpMx19LIxd4Ph_BvX_wu7XAtbebJjqV/exec?Temperatura=0,5&HumedadAtmosférica=3,2&Luz=10&HumedadSuelo=45&Origen=325612" + origen);


  Serial.println(F("---------------Configuración concluida--------------"));
}

void loop()
{
  //Verificamos que hay bytes disponibles para leer en el puerto de serie virtual,
  // es decir, que el SIM800L ha enviado algo y escribimos lo que ha enviado en el
  //monitor
  if (moduloSIM800L.available() > 0)
    Serial.write(moduloSIM800L.read());

  // Verificamos si en el monitor hay bytes disponibles, es decir, si hemos escrito algo y pulsado "Send",
  // mientras haya algo, se lo enviamos al SIM800L seguido de "Enter" o nueva línea
  if (Serial.available() > 0)
  {
    while (Serial.available() > 0)
    {
      moduloSIM800L.write(Serial.read());
    }
    moduloSIM800L.println();
  }
}


bool ejecutaComandoYEsperaRespuesta(char *comando, char *respuestaEsperada, int timeout) {
  getReply(comando, timeout);
  uint8_t r = readline(timeout);
  return (strcmp(replybuffer, respuestaEsperada) == 0);
}

// Función de log
bool print_log(char *src, int code) {
  bool ret = true;
  if (DEBUG_MODE) {
    if (code == 0) {
      Serial.print(F("[INFO] command: "));
      Serial.print(src);
      Serial.println(F(" completado."));
      ret = true;
    } else if (code < 0) {
      Serial.print(F("[INFO] "));
      Serial.println(src);
      ret = true;
    } else {
      Serial.print(F("[ERROR] command: "));
      Serial.print(src);
      Serial.print(F(" código: "));
      Serial.println(code);
      ret = false;
    }
  }
  return ret;
}

bool peticionURL(String url) {

  bool peticionURLCorrecta = false;

  print_log("Inicialización del servicio HTTP", ejecutaComandoYEsperaRespuesta("AT+HTTPINIT", "OK") ? CORRECTO : AT_ERROR);
  print_log("CID de la sesión HTTP", ejecutaComandoYEsperaRespuesta("AT+HTTPPARA=\"CID\",1", "OK") ? CORRECTO : AT_ERROR);
  url = "AT+HTTPPARA=\"URL\",\"" + url + "\"";
  char charBufferURL[url.length()+1];
  url.toCharArray(charBufferURL, url.length()+1);
  print_log("URL de la sesión HTTP", ejecutaComandoYEsperaRespuesta(charBufferURL, "OK") ? CORRECTO : AT_ERROR);
  print_log("Activación de la función HTTPS", ejecutaComandoYEsperaRespuesta("AT+HTTPSSL=1", "OK") ? CORRECTO : AT_ERROR);
  print_log("Ejecución de la petición HTTPS", ejecutaComandoYEsperaRespuesta("AT+HTTPACTION=0", "OK") ? CORRECTO : AT_ERROR);
  while (readline(20000, true));
  if (String(replybuffer).indexOf("+HTTPACTION: 0,200,") < 0)
    peticionURLCorrecta = true;
  print_log("Termina el servicio HTTPS", ejecutaComandoYEsperaRespuesta("AT+HTTPTERM", "OK") ? CORRECTO : AT_ERROR);

  return peticionURLCorrecta;

}

uint8_t readline(uint16_t timeout, boolean multiline) {
  uint16_t replyidx = 0;

  while (timeout--) {

    if (replyidx >= 254) {
      //DEBUG_PRINTLN(F("SPACE"));
      //Serial.println(F("SPACE"));
      break;
    }

    while (moduloSIM800L.available()) {
      char c =  moduloSIM800L.read();
      if (c == '\r') continue;
      if (c == 0xA) {
        if (replyidx == 0)   // the first 0x0A is ignored
          continue;

        if (!multiline) {
          timeout = 0;   // the second 0x0A is the end of the line
          //Serial.println(F("the second 0x0A is the end of the line"));
          break;
        }
      }
      replybuffer[replyidx] = c;
      //DEBUG_PRINT(c, HEX); DEBUG_PRINT("#"); DEBUG_PRINTLN(c);
      //      Serial.print(c, HEX);
      //      Serial.print(F("#"));
      //      Serial.println(c);
      replyidx++;
    }

    if (timeout == 0) {
      //DEBUG_PRINTLN(F("TIMEOUT"));
      //Serial.println(F("TIMEOUT"));
      break;
    }
    delay(1);
  }
  replybuffer[replyidx] = 0;  // null term
  //Serial.print(F("Replybuffer:"));
  //Serial.println(replybuffer);
  return replyidx;
}


uint8_t getReply(char *send, uint16_t timeout) {
  //flushInput();


  //DEBUG_PRINT(F("\t---> ")); DEBUG_PRINTLN(send);
  //Serial.print(F("\t---> "));
  //Serial.println(send);


  moduloSIM800L.println(send);

  //Cada vez que realizamos una petición, devuelve la petición realizada
  //y luego la respuesta, es decir, cuando enviamos un comando AT, la
  //respuesta es una línea con el comando AT y al menos otra con la respuesta,
  //por eso, cada vez que enviamos un comando leemos lo primero la línea del
  //comando que hemos enviado
  uint8_t l = readline(timeout);

  //DEBUG_PRINT (F("\t<--- ")); DEBUG_PRINTLN(replybuffer);
  //Serial.print(F("\t<--- "));
  //Serial.println(replybuffer);

  return l;
}
