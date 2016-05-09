#include <SoftwareSerial.h>
SoftwareSerial miPuertoDeSerieVirtual(10, 11);

void setup()  
{
  Serial.begin(9600);

  miPuertoDeSerieVirtual.begin(9600);
}

void loop()
{
  if (miPuertoDeSerieVirtual.available()>0)
    Serial.write(miPuertoDeSerieVirtual.read());

  if (Serial.available()>0)
  { 
    while(Serial.available()>0)
    {
      miPuertoDeSerieVirtual.write(Serial.read());
    }
    miPuertoDeSerieVirtual.println();
  }
}
