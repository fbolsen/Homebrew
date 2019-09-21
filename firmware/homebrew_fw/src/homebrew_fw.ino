#include "OneWire.h"
#include "spark-dallas-temperature.h"


const size_t READ_BUF_SIZE = 64;
const unsigned long CHAR_TIMEOUT = 3000;

const long interval = 1000;           // interval at which to blink (milliseconds)
const int ledPin =  D6;// the number of the LED pin
const int minPeriod = 100;
const int maxPeriod = 10000;
const int minDutyCycle = 0;
const int maxDutyCycle = 100;
const int dutyCycleMillisMin = 10;

const int tempSensorPin = D2;


// Global variables
char readBuf[READ_BUF_SIZE];
size_t readBufOffset = 0;
unsigned long lastCharTime = 0;

bool doPWM = FALSE;
bool doReadSerial = TRUE;
int doPWM_int = 0;

int period = 1000;
int dutyCycle = 0;
int dutyCycleMillis = 0;

double tempC = 0.0;

int counter = 0;
int ledState = LOW;             // ledState used to set the LED
unsigned long previousMillis = 0;        // will store last time LED was updated




// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(tempSensorPin);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

DeviceAddress tempDeviceAddress;



void setup() {
  // set the digital pin as output:
  pinMode(ledPin, OUTPUT);
  Particle.variable("period", &period, INT);
  Particle.function("setPeriod", setPeriod);
  Particle.variable("dutyCycle", &dutyCycle, INT);
  Particle.function("setDutyCycle", setDutyCycle);
  Particle.variable("dutyCycleMillis", &dutyCycleMillis, INT);

  Particle.function("Start", start);
  Particle.function("Stop", stop);

  Particle.function("RequestTemp", requestTemp);
  Particle.variable("tempC", &tempC, DOUBLE);

  Particle.variable("doPWM", &doPWM_int, INT);

  Serial.begin(9600);
  Serial.setTimeout(1000);

  sensors.begin();
  sensors.getAddress(tempDeviceAddress, 0);
  sensors.setResolution(tempDeviceAddress, 10);

  sensors.setWaitForConversion(FALSE);
  sensors.requestTemperatures();


}

int requestTemp(String s) {

  tempC = sensors.getTempCByIndex(0);
  sensors.requestTemperatures();
  //tempC = sensors.getTempCByIndex(0);

  Serial.printlnf("tempC = %f", tempC);

  //Serial.print("Sensor Resolution: ");
  //Serial.println(sensors.getResolution(tempDeviceAddress), DEC);
  //Serial.println();

}

void setDutyCycleMillis() {
  dutyCycleMillis = int(dutyCycle*period/100);
  if (dutyCycleMillis < dutyCycleMillisMin) {
      dutyCycleMillis = dutyCycleMillisMin;
  }

  if (dutyCycleMillis > period) {
      dutyCycleMillis = period;
  }
  Serial.printlnf("dutyCycleMillis = %d", dutyCycleMillis);
}

int setPeriod(String p) {

    period = p.toInt(); //this return zero if p cannot be converted
    // ensure that period is between bounds
    if (period < minPeriod) {
        period = minPeriod;
    } else if (period > maxPeriod) {
        period = maxPeriod;
    }
    Serial.printlnf("period = %f", period);
    setDutyCycleMillis();

}

int setDutyCycle(String p) {
    //Serial.printlnf("dutyCycle str = %s", p.c_str());

    dutyCycle = p.toInt(); //this return zero if p cannot be converted
    // ensure that period is between bounds
    if (dutyCycle < minDutyCycle) {
        dutyCycle = minDutyCycle;
    } else if (dutyCycle > maxDutyCycle) {
        dutyCycle = maxDutyCycle;
    }

    Serial.printlnf("dutyCycle int = %d", dutyCycle);
    //setDutyCycleMillis();
}


int start(String s) {

    doPWM = TRUE;
    doPWM_int = 1;
    int result = s.toInt();
    return result;
}

int stop (String s) {

    doPWM = FALSE;
    doPWM_int = 0;

    // ToDo: Add code to make sure PWM is off
    ledState = LOW;
    digitalWrite(ledPin, ledState);

}

int readSerial(String s) {

    int i=0;
    String mystr = "";

    Serial.printlnf("Entering readSerial!");

    if (s.startsWith("start")) {
      Serial.printlnf("Found start!");
      start("1");
    }
    else if (s.startsWith("stop")) {
      Serial.printlnf("Found stop!");
      stop("1");
    }
    else if (s.startsWith("setPeriod")) {
      Serial.printlnf("Found setPeriod!");
      //parse to get value
      //find "="
      i = s.indexOf("=");
      if (i>-1) {
        Serial.printlnf("Found = at %d", i);
        mystr = s.substring(i+1);
        Serial.printlnf("mystr = %s", mystr.c_str());
        setPeriod(mystr);
      }
    }
    else if (s.startsWith("setDutyCycle")) {
      Serial.printlnf("Found setDutyCycle!");
      i = s.indexOf("=");
      if (i>-1) {
        Serial.printlnf("Found = at %d", i);
        mystr = s.substring(i+1);
        Serial.printlnf("mystr = %s", mystr.c_str());
        //value = mystr.trim().toInt();
        //Serial.printlnf("Value = %d", value);
        setDutyCycle(mystr.c_str());
      }
    }
    else
    {
      Serial.printlnf("Command not recognised: %s", s.c_str());
    }


}

void loop() {

    unsigned long delta = 0;
    unsigned long currentMillis = millis();

    // Read data from serial
    while(Serial.available()) {
        if (readBufOffset < READ_BUF_SIZE) {
            char c = Serial.read();
            if (c != '\n') {
                // Add character to buffer
                readBuf[readBufOffset++] = c;
                lastCharTime = millis();
            }
            else {
                // End of line character found, process line
                readBuf[readBufOffset] = 0;
                Serial.printlnf("got: %s", readBuf);
                readSerial(String(readBuf));
                readBufOffset = 0;
            }
        }
        else {
            Serial.println("readBuf overflow, emptying buffer");
            readBufOffset = 0;
        }
    }

    if (currentMillis - lastCharTime >= CHAR_TIMEOUT) {
        lastCharTime = millis();
        readBuf[readBufOffset] = 0;
        //Serial.printlnf("got timeout: %s", readBuf);
        Serial.printlnf("{\"doPWM\":%d, \"dutyCycle\":%d, \"period\":%d}", doPWM, dutyCycle, period);
        readBufOffset = 0;
    }

    delta = currentMillis - previousMillis;

    if (doPWM && (delta  <=  dutyCycleMillis)) {
        ledState = HIGH;
    } else {
        ledState = LOW;
    }
    digitalWrite(ledPin, ledState);

    if (delta >= period) {
      requestTemp("");
      previousMillis = currentMillis;

    }

}
