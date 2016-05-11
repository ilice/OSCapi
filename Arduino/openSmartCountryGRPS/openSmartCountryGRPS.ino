#include <SoftwareSerial.h>

#define PIN  "8651"
#define apn  F("ac.vodafone.es")
#define apnusername F("vodafone")
#define apnpassword F("vodafone")
#define apnpassword F("vodafone")
#define restURL F("script.google.com/macros/s/AKfycbyAMTjQueuBn3adO1b_fCpMx19LIxd4Ph_BvX_wu7XAtbebJjqV/exec?")

SoftwareSerial miPuertoDeSerieVirtual(10, 11);

boolean sendCheckReply(const __FlashStringHelper * send, const __FlashStringHelper * reply, uint16_t timeout = 500);
boolean sendCheckReply(char* send, const __FlashStringHelper *reply, uint16_t timeout = 500);
uint8_t readline(uint16_t timeout = 500);
uint8_t getReply(const __FlashStringHelper *send,  uint16_t timeout = 500);
boolean expectReply(const __FlashStringHelper * reply, uint16_t timeout = 10000);
boolean sendParseReply(const __FlashStringHelper * tosend, const __FlashStringHelper * toreply, uint16_t *v, char divider, uint8_t index = 0);
boolean parseReply(const __FlashStringHelper * toreply, uint16_t *v, char divider  = ',', uint8_t index = 0);
char replybuffer[255];
char imei[16] = {0}; // MUST use a 16 character buffer for IMEI!
const __FlashStringHelper * ok_reply;
float latitude, longitude;
const int SIM800LresetPin =  12;

uint8_t sensorType = 0;
int sensorValue = 0;


void setup()
{
  Serial.begin(9600);
  miPuertoDeSerieVirtual.begin(9600);
  //while (!Serial);

  resetSIM800L();

  ok_reply = F("OK");

  memoryTest();

  echoOFF();

  getIMEI(imei);

  unlockSIM();

  enableGPRS();

  printGSMLoc();

  memoryTest();
}

void loop()
{
  sensorType += 1;
  sensorValue += 2;

  sendMeasure();

  delay(10000);

  memoryTest();
}

boolean sendCheckReply(const char *send, const char *reply, uint16_t timeout) {
  //Serial.println(F("Entrando en: 78-sendCheckReply"));
  if (! getReply(send, timeout) )
    return false;

  //  for (uint8_t i = 0; i < strlen(replybuffer); i++) {
  //    Serial.print(replybuffer[i], HEX); Serial.print(" ");
  //  }
  //  Serial.println();
  //  for (uint8_t i = 0; i < strlen(reply); i++) {
  //    Serial.print(reply[i], HEX); Serial.print(" ");
  //  }
  //  Serial.println();

  return (strcmp(replybuffer, reply) == 0);
}

uint8_t getReply(const char *send, uint16_t timeout) {
  //Serial.println(F("Entrando en: 95-getReply"));
  flushInput();


  //Serial.print(F("\t---> ")); Serial.println(send);


  miPuertoDeSerieVirtual.println(send);

  uint8_t l = readline(timeout);

  //Serial.print(F("\t<--- ")); Serial.println(replybuffer);

  return l;
}


uint8_t getReply(const __FlashStringHelper *send, uint16_t timeout) {
  //Serial.println(F("Entrando en: 113-getReply"));
  flushInput();


  //Serial.print(F("\t---> ")); Serial.println(send);


  miPuertoDeSerieVirtual.println(send);

  uint8_t l = readline(timeout);

  //Serial.print (F("\t<--- ")); Serial.println(replybuffer);

  return l;
}

boolean sendCheckReply(const __FlashStringHelper *send, const __FlashStringHelper *reply, uint16_t timeout) {
  //Serial.println(F("Entrando en: 130-sendCheckReply"));
  if (! getReply(send, timeout) )
    return false;

  //  for (uint8_t i = 0; i < strlen(replybuffer); i++) {
  //    Serial.print(replybuffer[i], HEX); Serial.print(" ");
  //  }
  //  Serial.println();
  //  Serial.print(reply); Serial.println(".");

  return (strcmp_P((replybuffer), (char PROGMEM *)reply) == 0);
}

boolean sendCheckReply(char* send, const __FlashStringHelper *reply, uint16_t timeout) {
  //Serial.println(F("Entrando en: 145-sendCheckReply"));
  if (! getReply(send, timeout) )
    return false;
  //
  //  for (uint8_t i = 0; i < strlen(replybuffer); i++) {
  //    Serial.print(replybuffer[i], HEX); Serial.print(" ");
  //  }
  //  Serial.println();
  //  Serial.println(reply);

  return (strcmp_P((replybuffer), (char PROGMEM *)reply) == 0);
}

uint8_t readline(uint16_t timeout) {
  //Serial.println(F("Entrando en: 158-readline"));
  uint16_t replyidx = 0;

  while (timeout--) {
    if (replyidx >= 254) {
      //Serial.print(F("SPACE"));
      break;
    }

    while (miPuertoDeSerieVirtual.available()) {
      char c =  miPuertoDeSerieVirtual.read();
      if (c == '\r') continue;
      if (c == 0xA) {
        if (replyidx == 0)   // the first 0x0A is ignored
          continue;


        timeout = 0;         // the second 0x0A is the end of the line
        break;

      }
      replybuffer[replyidx] = c;
      //Serial.print(c, HEX); Serial.print("#"); Serial.println(c);
      replyidx++;
    }

    if (timeout == 0) {
      //Serial.println(F("TIMEOUT"));
      break;
    }
    delay(1);
  }
  replybuffer[replyidx] = 0;  // null term
  return replyidx;
}

void flushInput() {
  //Serial.println(F("Entrando en: 195-flushInput"));
  // Read all available serial input to flush pending data.
  uint16_t timeoutloop = 0;
  while (timeoutloop++ < 40) {
    while (miPuertoDeSerieVirtual.available()) {
      miPuertoDeSerieVirtual.read();
      timeoutloop = 0;  // If char was received reset the timer
    }
    delay(1);
  }
}

uint8_t getIMEI(char *imei) {
  //Serial.println(F("Entrando en: 208-getIMEI"));
  getReply(F("AT+GSN"));

  // up to 15 chars
  strncpy(imei, replybuffer, 15);
  imei[15] = '\0';

  readline(); // eat 'OK'

  return strlen(imei);
}


uint8_t unlockSIM(const char *pin) {
  //Serial.println(F("Entrando en: 222-unlockSIM"));
  char sendbuff[14] = "AT+CPIN=";
  sendbuff[8] = pin[0];
  sendbuff[9] = pin[1];
  sendbuff[10] = pin[2];
  sendbuff[11] = pin[3];
  sendbuff[12] = '\0';

  return sendCheckReply(sendbuff, F("OK"));
}

// this function will return the number of bytes currently free in RAM
int memoryTest() {
  //Serial.println(F("Entrando en: 235-memoryTest"));
  int byteCounter = 0; // initialize a counter
  byte *byteArray; // create a pointer to a byte array
  // More on pointers here: http://en.wikipedia.org/wiki/Pointer#C_pointers

  // use the malloc function to repeatedly attempt allocating a certain number of bytes to memory
  // More on malloc here: http://en.wikipedia.org/wiki/Malloc
  while ( (byteArray = (byte*) malloc (byteCounter * sizeof(byte))) != NULL ) {
    byteCounter++; // if allocation was successful, then up the count for the next try
    free(byteArray); // free memory after allocating it
  }

  free(byteArray); // also free memory after the function finishes

  Serial.print(F("Memory test results: "));
  Serial.print(byteCounter, DEC);
  Serial.println(F(" bytes free"));

  return byteCounter; // send back the highest number of bytes successfully allocated
}

boolean enableGPRS(boolean onoff) {

  if (onoff) {
    // disconnect all sockets
    sendCheckReply(F("AT+CIPSHUT"), F("SHUT OK"), 20000);

    if (! sendCheckReply(F("AT+CGATT=1"), ok_reply, 10000))
      return false;

    // set bearer profile! connection type GPRS
    if (! sendCheckReply(F("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\""),
                         ok_reply, 10000))
      return false;

    // set bearer profile access point name
    if (apn) {
      // Send command AT+SAPBR=3,1,"APN","<apn value>" where <apn value> is the configured APN value.
      if (! sendCheckReplyQuoted(F("AT+SAPBR=3,1,\"APN\","), apn, ok_reply, 10000))
        return false;

      // send AT+CSTT,"apn","user","pass"
      flushInput();

      miPuertoDeSerieVirtual.print(F("AT+CSTT=\""));
      miPuertoDeSerieVirtual.print(apn);
      if (apnusername) {
        miPuertoDeSerieVirtual.print("\",\"");
        miPuertoDeSerieVirtual.print(apnusername);
      }
      if (apnpassword) {
        miPuertoDeSerieVirtual.print("\",\"");
        miPuertoDeSerieVirtual.print(apnpassword);
      }
      miPuertoDeSerieVirtual.println("\"");

      //Serial.print(F("\t---> ")); Serial.print(F("AT+CSTT=\""));
      //Serial.print(apn);

      if (apnusername) {
        //Serial.print("\",\"");
        //Serial.print(apnusername);
      }
      if (apnpassword) {
        //Serial.print("\",\"");
        //Serial.print(apnpassword);
      }
      //Serial.println("\"");

      if (! expectReply(ok_reply)) return false;

      // set username/password
      if (apnusername) {
        // Send command AT+SAPBR=3,1,"USER","<user>" where <user> is the configured APN username.
        if (! sendCheckReplyQuoted(F("AT+SAPBR=3,1,\"USER\","), apnusername, ok_reply, 10000))
          return false;
      }
      if (apnpassword) {
        // Send command AT+SAPBR=3,1,"PWD","<password>" where <password> is the configured APN password.
        if (! sendCheckReplyQuoted(F("AT+SAPBR=3,1,\"PWD\","), apnpassword, ok_reply, 10000))
          return false;
      }
    }

    // open GPRS context
    if (! sendCheckReply(F("AT+SAPBR=1,1"), ok_reply, 30000))
      return false;

    // bring up wireless connection
    if (! sendCheckReply(F("AT+CIICR"), ok_reply, 10000))
      return false;

  } else {
    // disconnect all sockets
    if (! sendCheckReply(F("AT+CIPSHUT"), F("SHUT OK"), 20000))
      return false;

    // close GPRS context
    if (! sendCheckReply(F("AT+SAPBR=0,1"), ok_reply, 10000))
      return false;

    if (! sendCheckReply(F("AT+CGATT=0"), ok_reply, 10000))
      return false;

  }
  return true;
}

boolean expectReply(const __FlashStringHelper * reply, uint16_t timeout) {
  readline(timeout);

  //Serial.print(F("\t<--- ")); Serial.println(replybuffer);

  return (strcmp_P((replybuffer), (char PROGMEM *)reply) == 0);
}

boolean sendCheckReplyQuoted(const __FlashStringHelper * prefix, const __FlashStringHelper * suffix, const __FlashStringHelper * reply, uint16_t timeout) {
  getReplyQuoted(prefix, suffix, timeout);
  return (strcmp_P((replybuffer), (char PROGMEM *)reply) == 0);
}

// Send prefix, ", suffix, ", and newline. Return response (and also set replybuffer with response).
uint8_t getReplyQuoted(const __FlashStringHelper * prefix, const __FlashStringHelper * suffix, uint16_t timeout) {
  flushInput();


  //Serial.print(F("\t---> ")); Serial.print(prefix);
  //Serial.print('"'); Serial.print(suffix); Serial.println('"');


  miPuertoDeSerieVirtual.print(prefix);
  miPuertoDeSerieVirtual.print('"');
  miPuertoDeSerieVirtual.print(suffix);
  miPuertoDeSerieVirtual.println('"');

  uint8_t l = readline(timeout);

  //Serial.print (F("\t<--- ")); Serial.println(replybuffer);

  return l;
}

uint8_t getNetworkStatus(void) {
  uint16_t status;

  if (! sendParseReply(F("AT+CREG?"), F("+CREG: "), &status, ',', 1)) return 0;

  return status;
}

boolean sendParseReply(const __FlashStringHelper * tosend, const __FlashStringHelper * toreply, uint16_t *v, char divider, uint8_t index) {
  getReply(tosend);

  if (! parseReply(toreply, v, divider, index)) return false;

  readline(); // eat 'OK'

  return true;
}

boolean parseReply(const __FlashStringHelper * toreply, uint16_t *v, char divider, uint8_t index) {
  char *p = strstr_P(replybuffer, (char PROGMEM *)toreply);  // get the pointer to the voltage
  if (p == 0) return false;
  p += strlen_P((char PROGMEM *)toreply);
  //DEBUG_PRINTLN(p);
  for (uint8_t i = 0; i < index; i++) {
    // increment dividers
    p = strchr(p, divider);
    if (!p) return false;
    p++;
    //DEBUG_PRINTLN(p);

  }
  *v = atoi(p);

  return true;
}

boolean getGSMLoc(float *lat, float *lon) {

  uint16_t returncode;
  char gpsbuffer[120];

  getReply(F("AT+CIPGSMLOC=1,1"), (uint16_t)10000);

  if (! parseReply(F("+CIPGSMLOC: "), &returncode))
    return false;

  char *p = replybuffer + 14;
  uint16_t lentocopy = min(119, strlen(p));
  strncpy(gpsbuffer, p, lentocopy + 1);

  readline(); // eat OK

  // make sure we have a valid return code
  if (returncode != 0)
    return false;

  // +CIPGSMLOC: 0,-74.007729,40.730160,2015/10/15,19:24:55
  // tokenize the gps buffer to locate the lat & long
  char *longp = strtok(gpsbuffer, ",");
  if (! longp) return false;

  char *latp = strtok(NULL, ",");
  if (! latp) return false;

  *lat = atof(latp);
  *lon = atof(longp);

  return true;

}

void flushSerial() {
  while (Serial.available())
    Serial.read();
}

uint8_t getReply(const __FlashStringHelper * prefix, int32_t suffix, uint16_t timeout) {
  flushInput();


  //Serial.print(F("\t---> ")); Serial.print(prefix); Serial.println(suffix, DEC);


  miPuertoDeSerieVirtual.print(prefix);
  miPuertoDeSerieVirtual.println(suffix, DEC);

  uint8_t l = readline(timeout);

  //Serial.print (F("\t<--- ")); Serial.println(replybuffer);

  return l;
}

bool sendMeasure() {
  uint16_t statuscode;
  int16_t length;

  flushSerial();

  // Handle any pending
  sendCheckReply(F("AT+HTTPTERM"), ok_reply);

  // Initialize and set parameters
  if (!sendCheckReply(F("AT+HTTPINIT"), ok_reply)) {
    Serial.println(F("ERROR HTTP INIT"));
    return false;
  }

  if (!sendCheckReply(F("AT+HTTPPARA=\"CID\",1"), ok_reply)) {
    Serial.println(F("ERROR HTTP CID PARAM"));
    return false;
  }

  miPuertoDeSerieVirtual.print(F("AT+HTTPPARA=\"URL\",\""));
  //Serial.print(F("AT+HTTPPARA=\"URL\",\""));
  miPuertoDeSerieVirtual.print(restURL);
  //Serial.print(restURL);
  miPuertoDeSerieVirtual.print(F("IMEI="));
  //Serial.print(F("IMEI="));
  miPuertoDeSerieVirtual.print(imei);
  //Serial.print(imei);
  miPuertoDeSerieVirtual.print(F("&Sensor="));
  //Serial.print(F("&Sensor="));
  switch (sensorType) {
    case 1:
      miPuertoDeSerieVirtual.print(F("Latitud"));
      //Serial.print(F("Luz"));
      break;
    case 2:
      miPuertoDeSerieVirtual.print(F("Longitud"));
      //Serial.print(F("Humedad"));
      break;
    case 3:
      miPuertoDeSerieVirtual.print(F("Humedad"));
      //Serial.print(F("Humedad"));
      break;
    case 4:
      miPuertoDeSerieVirtual.print(F("Luz"));
      //Serial.print(F("Humedad"));
      break;
    default:
      miPuertoDeSerieVirtual.print(F("Lluvia"));
      //Serial.print(F("Lluvia"));
      break;
  }
  miPuertoDeSerieVirtual.print(F("&Valor="));
  //Serial.print(F("&Valor="));
  miPuertoDeSerieVirtual.print(sensorValue);
  //Serial.print(sensorValue);
  miPuertoDeSerieVirtual.println('"');
  //Serial.println('"');

  readline(10000);

  //Serial.print(F("\t<--- "));
  //Serial.println(replybuffer);

  // HTTPS
  if (!sendCheckReply(F("AT+HTTPSSL=1"), ok_reply)) {
    //Serial.println(F("ERROR HTTP SSL"));
    return false;
  }

  if (! sendCheckReply(F("AT+HTTPACTION=0"), ok_reply))
  {
    //Serial.println(F("ERROR HTTP GET EXECUTION"));
    return false;
  }


  // Parse response status and size.
  readline(30000);
  if (! parseReply(F("+HTTPACTION:"), &statuscode, ',', 1))
    return false;
  if (! parseReply(F("+HTTPACTION:"), (uint16_t *)&length, ',', 2))
    return false;

  //Serial.print(F("Status: ")); Serial.println(*statuscode);
  //Serial.print(F("Len: ")); Serial.println(*datalength);

  // HTTP response data
  flushInput();
  miPuertoDeSerieVirtual.println(F("AT+HTTPREAD"));
  uint8_t l = readline(500);
  if (! parseReply(F("+HTTPREAD:"), (uint16_t *)&length, ',', 0)) {
    //Serial.println(F("ERROR HTTP READ RESPONSE"));
    return false;
  }
  while (length > 0) {
    while (miPuertoDeSerieVirtual.available()) {
      char c = miPuertoDeSerieVirtual.read();
      Serial.write(c);
      length--;
      if (! length) break;
    }
  }
  Serial.println(F("\n****"));
  sendCheckReply(F("AT+HTTPTERM"), ok_reply);
  return true;
}

void resetSIM800L() {
  Serial.print(F("Reiniciando la SIM800L ."));
  pinMode(SIM800LresetPin, OUTPUT);
  digitalWrite(SIM800LresetPin, LOW);
  delay(1000);
  digitalWrite(SIM800LresetPin, HIGH);
  for (int i = 0; i < 19; i++) {
    Serial.print(F("."));
    delay(1000); //TODO: esto tengo que cambiarlo por esperar a que esté conectado bien en lugar de una espera arbitraria
  }
  Serial.println(F("  Done!"));
}

void echoOFF() {
  //This setting determines whether or not the TA echoes characters received from TE during Command state.
  if (!sendCheckReply(F("AT"), ok_reply)) {
    //Serial.println("Ha respondido TA, hay que especificar ATE0");
    sendCheckReply(F("ATE0"), F("ATE0"));
  } else {
    //Serial.println("Ha respondido OK, todo bien!");
  }
}

void unlockSIM() {
  if (!sendCheckReply(F("AT+CPIN?"), F("+CPIN: READY"))) {
    Serial.print(F("Unlocking SIM card: "));
    if (! unlockSIM(PIN)) {
      Serial.println(F("Failed"));
    } else {
      Serial.println(F("OK!"));
    }
    delay(10000);//TODO: esto tengo que cambiarlo por esperar a que esté conectado bien en lugar de una espera arbitraria
  }
}

void enableGPRS() {
  if (!sendCheckReply(F("AT+CGATT?"), F("+CGATT: READY"))) {
    if (!enableGPRS(true)) {
      Serial.println(F("Failed to turn on"));
    } else {
      Serial.println(F("Turn on"));
    }
  }
}

void printGSMLoc() {
  if (getNetworkStatus() == 1) {
    // network & GPRS? Great! Print out the GSM location to compare
    boolean gsmloc_success = getGSMLoc(&latitude, &longitude);

    if (gsmloc_success) {
      sensorType = 1;
      sensorValue = latitude*1000;
      sendMeasure();
      sensorType = 2;
      sensorValue = longitude*1000;
      sendMeasure();
      Serial.print("GSMLoc lat:");
      Serial.println(latitude, 6);
      Serial.print("GSMLoc long:");
      Serial.println(longitude, 6);
    } else {
      Serial.println("GSM location failed...");
      Serial.println(F("Disabling GPRS"));
      enableGPRS(false);
      Serial.println(F("Enabling GPRS"));
      if (!enableGPRS(true)) {
        Serial.println(F("Failed to turn GPRS on"));
      }
    }
  }
}
