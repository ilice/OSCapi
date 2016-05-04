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

//SoftwareSerial(rxPin, txPin, inverse_logic)
//Creamos una instancia del objeto SoftwareSerial para conectarnos con el SIM800L, 
// en este caso usaremos el PIN10 como rxPin que será el que reciba los datos del 
// SIM800L, es decir, el que estatá conectado al TXD en la SIM800L y el PIN11 como 
// txPin que será el que transmita los datos, es decir, el que estatá conectado al
// que está marcado como RXD en la SIM800L, inverse_logic es opcional y por defecto
// está a false, si se pone a true, invierte el sentido de los bits de entrada 
// tomando LOW en el rxPin como 1-bit y HIGH como 0-bit
SoftwareSerial miPuertoDeSerieVirtual(10, 11);

void setup()  
{
  // Abre el puerto de comunicación entre el Arduino y el ordenador para poder
  //comunicarnos con él a través del monitor (Ctrl+Mayús+M), la velocidad será 
  // 9600 bits por segundo, al abrir el monitor es importante que tenga esa 
  //velocidad seleccionada
  Serial.begin(9600);
  
  //Especificamos la velocidad de la comunicación entre el Arduino UNO y la SIM800L
  miPuertoDeSerieVirtual.begin(9600);

}

void loop()
{
  //Verificamos que hay bytes disponibles para leer en el puerto de serie virtual,
  // es decir, que el SIM800L ha enviado algo y escribimos lo que ha enviado en el 
  //monitor
  if (miPuertoDeSerieVirtual.available()>0)
    Serial.write(miPuertoDeSerieVirtual.read());

  // Verificamos si en el monitor hay bytes disponibles, es decir, si hemos escrito algo y pulsado "Send",
  // mientras haya algo, se lo enviamos al SIM800L seguido de "Enter" o nueva línea  
  if (Serial.available()>0)
  { 
    while(Serial.available()>0)
    {
      miPuertoDeSerieVirtual.write(Serial.read());
    }
    miPuertoDeSerieVirtual.println();
  }
}
