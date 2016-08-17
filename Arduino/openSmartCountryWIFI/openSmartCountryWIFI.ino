#include <Console.h>
#include <Process.h>
#include "LowPower.h"

#include "DHT.h"
#define DHTTYPE DHT11   // DHT 11
#define esTMP36 true //Si en lugar del DHT usamos el TMP36 (solo da la temperatura)

#define restURL F("http://opensmartcountry.com/php/cacharrito_rest.php?")
#define ON 255
#define LATITUD 0
#define LONGITUD 1
#define HUMEDADSUELO 2
#define TEMPERATURA 3
#define HUMEDAD 4
#define LLUVIA 5
#define CANTIDADLLUVIA 6
#define LUZ 7
#define BATERIA 8
#define VOLTAJEBATERIA 9

#define MEASUREINTERVAL 600000

float latitude = 40.489155;
float longitude = -3.653121;

char imei[16] = {'8','6','7','2','7','3','0','2','8','5','8','5','1','8','5','\0'}; // MUST use a 16 character buffer for IMEI!
uint8_t sensorType = 0;
char sensorValue[12] = {0};

int moistureSensorPin = A1;
int moistureSensorPower = 9;
int moistureMaxValue = 400;

int tempSensorPin = A3;
int tempAndHumiditySensorPin = 2;
int tempAndHumiditySensorPower = 3;

int rainSensorPin = 4;
int rainSensorPower = 6;
int rainLevelSensorPin = A0;

int lightSensorPin = A2;
int lightSensorPower = 5;

uint8_t sleepCounter = 0;
uint8_t sleepTimes = 100;

DHT dht(tempAndHumiditySensorPin, DHTTYPE);
 
void setup() {
  // Initialize Bridge
  Bridge.begin();
 
  Console.begin();
//  while (!Console) {
//    ; // wait for Console port to connect.
//  }

  pinMode(moistureSensorPower, OUTPUT);
  digitalWrite(moistureSensorPower, LOW);

  pinMode(tempAndHumiditySensorPower, OUTPUT);
  digitalWrite(tempAndHumiditySensorPower, LOW);

  pinMode(rainSensorPower, OUTPUT);
  digitalWrite(rainSensorPower, LOW);

  pinMode(lightSensorPower, OUTPUT);
  digitalWrite(lightSensorPower, LOW);

  calibrateMoistureSensor();
}
 
void loop() {

  sendLocation();

  sensorType = HUMEDADSUELO;
  updateSensorValue(moistureSensorMeasure());
  sendMeasure();

  sensorType = TEMPERATURA;
  updateSensorValue(tempSensorMeasure());
  sendMeasure();

  sensorType = HUMEDAD;
  updateSensorValue(humiditySensorMeasure());
  sendMeasure();

  sensorType = LLUVIA;
  updateSensorValue(rainSensorMeasure());
  sendMeasure();

  sensorType = CANTIDADLLUVIA;
  updateSensorValue(rainLevelSensorMeasure());
  sendMeasure();

  sensorType = LUZ;
  updateSensorValue(lightSensorMeasure());
  sendMeasure();

  sensorType = BATERIA;
  updateSensorValue(batterySensorMeasure());
  sendMeasure();

  sensorType = VOLTAJEBATERIA;
  updateSensorValue(batteryVoltageSensorMeasure());
  sendMeasure();

  Console.println(F("Power down"));
  //Dejo 1 segundo para que todo termine correctamente antes de "apagar" temporalmente el Arguino
  delay(1000);
  sleepCounter = 0;
  while (sleepCounter < sleepTimes) {
    // do something 10 times
    sleepCounter++;
    // put the processor to sleep for 8 seconds
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }
  //delay(MEASUREINTERVAL);
  Console.println(F("Power up"));
  memoryTest();
}
 
void runCurl(String url) {
  // Launch "curl" command and get Arduino ascii art logo from the network
  // curl is command line program for transferring data using different internet protocols
  Process p;        // Create a process and call it "p"
  p.begin("curl");  // Process that launch the "curl" command
  p.addParameter("-k");
  p.addParameter("-L"); //If the server reports that the requested page has moved to a different location (indicated with a Location: header and a 3XX response code), this option will make curl redo the request on the new place
  p.addParameter(url); // Add the URL parameter to "curl"
  p.run();      // Run the process and wait for its termination
 
  while (p.available() > 0) {
    char c = p.read();
    Console.print(c);
  }
  // Ensure the last bit of data is sent.
  Console.println();
  Console.flush();
}

int memoryTest() {
  Console.println(F("Entrando en: 235-memoryTest"));
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

  Console.print(F("Memory test results: "));
  Console.print(byteCounter, DEC);
  Console.println(F(" bytes free"));

  return byteCounter; // send back the highest number of bytes successfully allocated
}

void updateSensorValue (float value) {
  dtostrf(value, -11, 8, sensorValue);
  sensorValue[11] = '\0';
}

void updateSensorValue (double value) {
  dtostrf(value, -11, 8, sensorValue);
  sensorValue[11] = '\0';
}

void updateSensorValue (bool value) {

  if (value) {
    sensorValue[0] = '1';
  } else {
    sensorValue[0] = '0';
  }
  sensorValue[1] = '\0';
}

void updateSensorValue (int value) {
  //El -11 en lugar del 11 es para que ajuste a la izquierda en lugar de a la derecha
  dtostrf(value, -11, 0, sensorValue);
  sensorValue[11] = '\0';
}
 
float moistureSensorMeasure() {
  float moistureSensorMeasure = 0;

  analogWrite(moistureSensorPower, ON);
  delay(500);
  moistureSensorMeasure = (analogRead(moistureSensorPin) * 100.0) / (float)moistureMaxValue;
  digitalWrite(moistureSensorPower, LOW);

  Console.print(F("Moisture: "));
  Console.println(moistureSensorMeasure);

  return moistureSensorMeasure;
}

float tempSensorMeasure() {
  
  analogWrite(tempAndHumiditySensorPower, ON);
  delay(2000);

  float temp = dht.readTemperature();

  if (isnan(temp)) {
    Console.println(F("Failed to read from DHT sensor!"));
  }

  if(esTMP36){
    // read the value on AnalogIn pin 0
    // and store it in a variable
    int sensorVal = analogRead(tempSensorPin);
  
    // send the 10-bit sensor value out the serial port
    Console.print("sensor Value: ");
    Console.print(sensorVal);
  
    // convert the ADC reading to voltage
    float voltage = (sensorVal / 1024.0) * 5.0;
  
    // Send the voltage level out the Serial port
    Console.print(", Volts: ");
    Console.print(voltage);
  
    // convert the voltage to temperature in degrees C
    // the sensor changes 10 mV per degree
    // the datasheet says there's a 500 mV offset
    // ((volatge - 500mV) times 100)
    Console.print(", degrees C: ");
    float temperature = (voltage - .5) * 100;
    Console.println(temperature);
  
    temp = temperature;
  }

  digitalWrite(tempAndHumiditySensorPower, LOW);
  
  Console.print(F("Temp: "));
  Console.println(temp);

  return temp;
}



float humiditySensorMeasure() {

  analogWrite(tempAndHumiditySensorPower, ON);

  delay(2000);

  float humidity = dht.readHumidity();

  if (isnan(humidity)) {
    Console.println(F("Failed to read from humidity sensor!"));
  }

  digitalWrite(tempAndHumiditySensorPower, LOW);

  Console.print(F("Humidity: "));
  Console.println(humidity);

  return humidity;
}

void calibrateMoistureSensor() {
  Console.println(F("Calibrate moisture sensor"));
  int moistureSensorValue = 0;
  for ( int i = 0; i < 10; i++) {

    analogWrite(moistureSensorPower, ON);
    delay(500);
    moistureSensorValue = analogRead(moistureSensorPin);
    if (moistureMaxValue < moistureSensorValue)
      moistureMaxValue = moistureSensorValue;

    Console.println(moistureMaxValue);

    digitalWrite(moistureSensorPower, LOW);

    delay(2000);

  }
  Console.println(F("Done."));

}

int rainLevelSensorMeasure() {

  int rainLevelSensorMeasure;

  analogWrite(rainSensorPower, ON);

  delay(2000);

  rainLevelSensorMeasure = analogRead(rainLevelSensorPin);

  if (isnan(rainLevelSensorMeasure)) {
    Console.println(F("Failed to read from rain level sensor!"));
  }

  Console.print(F("Rainlevel: "));
  Console.println(rainLevelSensorMeasure);

  digitalWrite(rainSensorPower, LOW);

  return rainLevelSensorMeasure;
}


bool rainSensorMeasure() {

  analogWrite(rainSensorPower, ON);

  delay(2000);

  bool lluvia = digitalRead(rainSensorPin);

  if(rainLevelSensorMeasure()==0)
  { 
    lluvia = false;
  }

  Console.print(F("Rain: "));
  Console.println(lluvia);

  if (isnan(lluvia)) {
    Console.println(F("Failed to read from rain sensor!"));
  }

  digitalWrite(rainSensorPower, LOW);

  return lluvia;
}

int lightSensorMeasure() {

  int lightSensorMeasure; 

  analogWrite(lightSensorPower, ON);

  delay(2000);

  lightSensorMeasure = analogRead(lightSensorPin);

  Console.print(F("Light: "));
  Console.println(lightSensorMeasure);

  if (isnan(lightSensorMeasure)) {
    Console.println(F("Failed to read from ligth sensor!"));
  }

  digitalWrite(lightSensorPower, LOW);

  return lightSensorMeasure;
}

int batterySensorMeasure() {
  return 100;
}

int batteryVoltageSensorMeasure() {
  return 5;
}
bool sendMeasure() {
  uint16_t statuscode;
  int16_t length;

  Console.print("sensorType: ");
  Console.println(sensorType);
  
  String url = restURL;
  url.concat(F("IMEI="));
  url.concat(imei);
  url.concat(F("&Sensor="));
  
  Console.print(restURL);
  Console.print(F("IMEI="));
  Console.print(imei);
  Console.print(F("&Sensor="));
  
  switch (sensorType) {
    case LATITUD:
      Console.print(F("Latitud"));
      url.concat(F("Latitud"));
      break;
    case LONGITUD:
      Console.print(F("Longitud"));
      url.concat(F("Longitud"));
      break;
    case HUMEDADSUELO:
      Console.print(F("HumedadSuelo"));
      url.concat(F("HumedadSuelo"));
      break;
    case TEMPERATURA:
      Console.print(F("Temperatura"));
      url.concat(F("Temperatura"));
      break;
    case HUMEDAD:
      Console.print(F("Humedad"));
      url.concat(F("Humedad"));
      break;
    case LLUVIA:
      Console.print(F("Lluvia"));
      url.concat(F("Lluvia"));
      break;
    case CANTIDADLLUVIA:
      Console.print(F("CantidadLluvia"));
      url.concat(F("CantidadLluvia"));
      break;
    case LUZ:
      Console.print(F("Luz"));
      url.concat(F("Luz"));
      break;
    case BATERIA:
      Console.print(F("Bateria"));
      url.concat(F("Bateria"));
      break;
    case VOLTAJEBATERIA:
      Console.print(F("VoltajeBateria"));
      url.concat(F("VoltajeBateria"));
      break;
    default:
      Console.print(F("NoConf"));
      url.concat(F("NoConf"));
      break;
  }

  Console.print(F("&Valor="));
  url.concat(F("&Valor="));

  Console.print(sensorValue);
  url.concat(sensorValue);
  
  runCurl(url);
  
  return true;
}

bool sendLocation() {
  uint16_t statuscode;
  int16_t length;

  Console.print("sensorType: ");
  Console.println(sensorType);
  
  String url = restURL;
  url.concat(F("IMEI="));
  url.concat(imei);
  url.concat(F("&Latitud="));
  url.concat(latitude);
  url.concat(F("&Longitud="));
  url.concat(longitude);
  
  Console.print(restURL);
  Console.print(F("IMEI="));
  Console.print(imei);
  Console.print(F("&Latitud="));
  Console.print(latitude);
  Console.print(F("&Longitud="));
  Console.print(longitude);
  
  runCurl(url);
  
  return true;
}
