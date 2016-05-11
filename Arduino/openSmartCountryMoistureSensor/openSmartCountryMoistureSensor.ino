int moistureSensorPin = A0;
int moistureSensorPower = 11;
#define ON 255

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  while(!Serial)

  pinMode(moistureSensorPower, OUTPUT);
  digitalWrite(moistureSensorPower, LOW);
  Serial.println(F("Setup done!"));
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print(F("Moisture Value:"));
  Serial.print(moistureSensorMeasure());
  Serial.println(" %");
  delay(10000);

}

float moistureSensorMeasure(){
  float moistureSensorMeasure = 0;
  
  analogWrite(moistureSensorPower, ON);
  delay(500);
  moistureSensorMeasure = (analogRead(A0)/671.0)*100.0;
  digitalWrite(moistureSensorPower, LOW);

  return moistureSensorMeasure;
}
