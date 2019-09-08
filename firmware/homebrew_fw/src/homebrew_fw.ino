#include "OneWire.h"
#include "spark-dallas-temperature.h"


const long interval = 1000;           // interval at which to blink (milliseconds)
const int ledPin =  D6;// the number of the LED pin
const int minPeriod = 100;
const int maxPeriod = 10000;
const int minDutyCycle = 0;
const int maxDutyCycle = 100;
const int dutyCycleMillisMin = 10;

const int tempSensorPin = D2;

bool doPWM = FALSE;
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

  sensors.begin();
  sensors.getAddress(tempDeviceAddress, 0);
  //sensors.setResolution(tempDeviceAddress, resolution);
  sensors.setWaitForConversion(FALSE);
  sensors.requestTemperatures();


}

int requestTemp(String s) {

  //tempC = sensors.getTempCByIndex(0);
  sensors.requestTemperatures();
  tempC = sensors.getTempCByIndex(0);
}

void setDutyCycleMillis() {
  dutyCycleMillis = int(dutyCycle*period/100);
  if (dutyCycleMillis < dutyCycleMillisMin) {
      dutyCycleMillis = dutyCycleMillisMin;
  }

  if (dutyCycleMillis > period) {
      dutyCycleMillis = period;
  }
}

int setPeriod(String p) {

    period = p.toInt(); //this return zero if p cannot be converted
    // ensure that period is between bounds
    if (period < minPeriod) {
        period = minPeriod;
    } else if (period > maxPeriod) {
        period = maxPeriod;
    }

    setDutyCycleMillis();

}

int setDutyCycle(String p) {

    dutyCycle = p.toInt(); //this return zero if p cannot be converted
    // ensure that period is between bounds
    if (dutyCycle < minDutyCycle) {
        dutyCycle = minDutyCycle;
    } else if (dutyCycle > maxDutyCycle) {
        dutyCycle = maxDutyCycle;
    }

    setDutyCycleMillis();
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

void loop() {

    unsigned long currentMillis = millis();
    unsigned long delta = 0;
    //unsigned long onTime = 0;
    //unsigned long offTime = 0;

    //if (!Particle.connected()) {
    //  doPWM = FALSE;
    //  ledState = LOW;
    //  Serial.printlnf("Not connected to cloud - doPWM = FALSE!");
    //}


    //Serial.print(doPWM_int);

    if (doPWM) {

        delta = currentMillis - previousMillis;
        //Serial.printlnf("delta = %d", delta);

        if (delta  <=  dutyCycleMillis) {
            ledState = HIGH;
        } else {
            ledState = LOW;
        }
        digitalWrite(ledPin, ledState);

        if (delta >= period) {

          //tempC = sensors.getTempCByIndex(0);

          // save the  time of the last period
          previousMillis = currentMillis;
            // set the LED with the ledState of the variable:
            //digitalWrite(ledPin, ledState);
        }

    }
}
