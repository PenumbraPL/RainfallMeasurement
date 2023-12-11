#include <hcsr04.h>

#define DEBUG

#define TRIG_PIN 12
#define ECHO_PIN 13
#define HYDRO_IN A0
#define BUTTON_IN A5
#define WATER_PUMP_OUT 8
#define WATER_FLOW_IN 2 // interupts only on digital pin 2 , 3 on arduino uno

#define SERIAL_SPEED 9600
#define TIMEOUT 1

const uint16_t buttonSwLvl = 500;
const unsigned long period = 1000;
const float calibrationFactor = 2.25f; // from datasheet
const uint16_t sensorSwLvl = 500;
uint16_t distanceSwLvl = 0;
uint16_t objectHeight = 0;

bool turnOn = false;
bool reset0 = false;
bool isWritten = false;

volatile int flowFrequency;
float flowRate; // global ??
unsigned long oldTime;
float totalPumpOut;
bool stringComplete = false;
String inputString = "";

/*=========================================*/

HCSR04 hcsr04(TRIG_PIN, ECHO_PIN, 20, 4000);

void flow(){
   flowFrequency++;
}



void setup(){
    Serial.begin(SERIAL_SPEED);
    //Serial.setTimeout(TIMEOUT);

    pinMode(WATER_PUMP_OUT, OUTPUT);
    digitalWrite(WATER_PUMP_OUT, HIGH);

    pinMode(WATER_FLOW_IN, INPUT);
    pinMode(BUTTON_IN, INPUT);
    pinMode(HYDRO_IN, INPUT);
    digitalWrite(WATER_FLOW_IN, HIGH);
    
    pinMode(WATER_FLOW_IN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(WATER_FLOW_IN), flow, RISING);

   oldTime = millis();
   totalPumpOut = 0;
}

void loop() {
   if(millis() - oldTime > period){
      cli();
      int sensorValue = analogRead(HYDRO_IN);
      int buttonValue = analogRead(BUTTON_IN);

      flowRate = (float) flowFrequency / calibrationFactor;
      flowRate *= 1000. / 60.;
      totalPumpOut += flowRate;
      //Serial.write(flowFrequency);
   #ifdef DEBUG
      Serial.print("D:" );
      Serial.println(hcsr04.distanceInMillimeters());
      //Serial.print("B:");
      //Serial.println( buttonValue);
      Serial.print("S:");
      Serial.println(sensorValue);
      Serial.print("H:");
      Serial.println(objectHeight);
      Serial.print("H_MIN:");
      Serial.println(distanceSwLvl);
      Serial.print("P:");
      Serial.println(String(flowFrequency));
   #endif
      
      
      if(buttonValue < buttonSwLvl){
         //turnOn = !turnOn;
      }
      if(sensorValue > sensorSwLvl){
      turnOn = true; 
      }

      // response to python
      // machine state

      if(hcsr04.distanceInMillimeters() > distanceSwLvl){
         //turnOn = false;
      }
      if(turnOn){
         digitalWrite(WATER_PUMP_OUT, LOW); 
      }else{
         digitalWrite(WATER_PUMP_OUT, HIGH);
      }
      
      flowFrequency = 0;
      oldTime = millis();
      sei();
   }

}

void serialEvent() {
  while (Serial.available()) {

      inputString = Serial.readString();
      objectHeight = atoi(inputString.c_str());
      distanceSwLvl =objectHeight * 0.2;
      turnOn = true;
    
   
   //inputString += inChar;
   //Serial.write(&inChar, 1);
   //if (inChar == '\n') {
   //   stringComplete = true;
   // }
  }
}


// float waterInMilliliters(unsigned long period){
//    flow_frequency = 0;
//    oldTime = millis();
//    sei();
//    while(millis() - oldTime < period);
//    cli();
//    flowRate = (float) flowFrequency / calibrationFactor;
//    flowRate *= 1000. / 60.;
// }
