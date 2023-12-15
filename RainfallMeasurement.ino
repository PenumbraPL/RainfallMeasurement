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
uint16_t sensorSwLvl = 650;
uint16_t distanceSwLvl = 0;

bool turnOn = false;
bool reset0 = false;
bool isWritten = false;

volatile int flowFrequency;
float flowRate;
unsigned long oldTime;
bool stringComplete = false;
String inputString = "";


int sensorValue;
int buttonValue;

/*=========================================*/

HCSR04 hcsr04(TRIG_PIN, ECHO_PIN, 20, 4000);

void flow(){
   flowFrequency++;
}

void send_to_serial(const char* symbol, int value){
      Serial.print(symbol);
      Serial.println(value);
      Serial.flush();
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
}

enum States { NORMAL, PUMP_OUT };


int normal(void* data){
      if(sensorValue > sensorSwLvl){
         return PUMP_OUT;
      }
      return NORMAL;
}

int pump_out(void* data){
      if(hcsr04.distanceInMillimeters() > distanceSwLvl){
         return NORMAL;
      }
      return PUMP_OUT;
}

int (*states[])(void*) = {normal, pump_out};
unsigned int current = NORMAL;

void loop() {
   if(millis() - oldTime > period){
      cli();
      sensorValue = analogRead(HYDRO_IN);
      buttonValue = analogRead(BUTTON_IN);


      send_to_serial("D:", hcsr04.distanceInMillimeters());
      send_to_serial("B:", buttonValue);
      send_to_serial("S:", sensorValue);
      send_to_serial("P:", flowFrequency);
      
      
      // if(buttonValue < buttonSwLvl){
      //    if(current == NORMAL) current = PUMP_OUT;
      //    if(current == PUMP_OUT) current = NORMAL;
      // }

      current = states[current]((void*) &current);

      if(current == PUMP_OUT){
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
      int delimieter = inputString.indexOf(":");
      if(inputString.substring(0, delimieter-1).compareTo("BB")){
         int buttonValue = inputString.substring(delimieter+1).toInt();
         if(buttonValue){
            digitalWrite(WATER_PUMP_OUT, LOW);
         }else{
            digitalWrite(WATER_PUMP_OUT, HIGH); 
         }
      }
      if(inputString.substring(0, delimieter-1).compareTo("MAX")){
         int objectHeight = inputString.substring(delimieter+1).toInt();
         distanceSwLvl = objectHeight * 0.8;
      }
  }
}