#include <SoftwareSerial.h>
SoftwareSerial miPuertoDeSerieVirtual(10, 11);

boolean sendCheckReply(const __FlashStringHelper *send, const char *reply, uint16_t timeout = 500);
boolean sendCheckReply(const __FlashStringHelper * send, const __FlashStringHelper * reply, uint16_t timeout = 500);
uint8_t readline(uint16_t timeout = 500, boolean multiline = false);
uint8_t getReply(const __FlashStringHelper *send,  uint16_t timeout = 500);
char replybuffer[255];

void setup()
{
  Serial.begin(9600);
  miPuertoDeSerieVirtual.begin(9600);
  while (!Serial);

  // run the memory test function and print the results to the serial port
  int result = memoryTest();
  Serial.print(F("Memory test results: "));
  Serial.print(result, DEC);
  Serial.println(F(" bytes free"));

  //This setting determines whether or not the TA echoes characters received from TE during Command state.
  if (!sendCheckReply(F("AT"), F("OK"))) {
    sendCheckReply(F("ATE0"), F("ATE0"));
  } 

  char imei[15] = {0}; // MUST use a 16 character buffer for IMEI!
  uint8_t imeiLen = getIMEI(imei);
  
  // run the memory test function and print the results to the serial port
  result = memoryTest();
  Serial.print(F("Memory test results: "));
  Serial.print(result, DEC);
  Serial.println(F(" bytes free"));
}

void loop()
{
  if (miPuertoDeSerieVirtual.available() > 0)
    Serial.write(miPuertoDeSerieVirtual.read());

  if (Serial.available() > 0)
  {
    while (Serial.available() > 0)
    {
      miPuertoDeSerieVirtual.write(Serial.read());
    }
    miPuertoDeSerieVirtual.println();
  }
}

boolean sendCheckReply(const char *send, const char *reply, uint16_t timeout) {
  if (! getReply(send, timeout) )
    return false;
  /*
    for (uint8_t i=0; i<strlen(replybuffer); i++) {
    DEBUG_PRINT(replybuffer[i], HEX); DEBUG_PRINT(" ");
    }
    DEBUG_PRINTLN();
    for (uint8_t i=0; i<strlen(reply); i++) {
      DEBUG_PRINT(reply[i], HEX); DEBUG_PRINT(" ");
    }
    DEBUG_PRINTLN();
  */
  return (strcmp(replybuffer, reply) == 0);
}

uint8_t getReply(const char *send, uint16_t timeout) {
  flushInput();


  //DEBUG_PRINT(F("\t---> ")); DEBUG_PRINTLN(send);


  miPuertoDeSerieVirtual.println(send);

  uint8_t l = readline(timeout);

  //DEBUG_PRINT (F("\t<--- ")); DEBUG_PRINTLN(replybuffer);

  return l;
}


uint8_t getReply(const __FlashStringHelper *send, uint16_t timeout) {
  flushInput();


  //DEBUG_PRINT(F("\t---> ")); DEBUG_PRINTLN(send);


  miPuertoDeSerieVirtual.println(send);

  uint8_t l = readline(timeout);

  //DEBUG_PRINT (F("\t<--- ")); DEBUG_PRINTLN(replybuffer);

  return l;
}

boolean sendCheckReply(const __FlashStringHelper *send, const __FlashStringHelper *reply, uint16_t timeout) {
  if (! getReply(send, timeout) )
    return false;
  return (strcmp((replybuffer), ((char PROGMEM *)reply)) == 0);
}

uint8_t readline(uint16_t timeout, boolean multiline) {
  uint16_t replyidx = 0;

  while (timeout--) {
    if (replyidx >= 254) {
      //DEBUG_PRINTLN(F("SPACE"));
      break;
    }

    while (miPuertoDeSerieVirtual.available()) {
      char c =  miPuertoDeSerieVirtual.read();
      if (c == '\r') continue;
      if (c == 0xA) {
        if (replyidx == 0)   // the first 0x0A is ignored
          continue;

        if (!multiline) {
          timeout = 0;         // the second 0x0A is the end of the line
          break;
        }
      }
      replybuffer[replyidx] = c;
      //DEBUG_PRINT(c, HEX); DEBUG_PRINT("#"); DEBUG_PRINTLN(c);
      replyidx++;
    }

    if (timeout == 0) {
      //DEBUG_PRINTLN(F("TIMEOUT"));
      break;
    }
    delay(1);
  }
  replybuffer[replyidx] = 0;  // null term
  return replyidx;
}

void flushInput() {
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
  getReply(F("AT+GSN"));

  // up to 15 chars
  strncpy(imei, replybuffer, 15);
  imei[15] = 0;

  readline(); // eat 'OK'

  return strlen(imei);
}

// this function will return the number of bytes currently free in RAM
int memoryTest() {
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
  return byteCounter; // send back the highest number of bytes successfully allocated
}


