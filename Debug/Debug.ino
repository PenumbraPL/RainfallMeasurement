#define DEBUG

#define SERIAL_SPEED 9600
#define TIMEOUT 1


const int period = 5000;
volatile int flowFrequency;
float flowRate; // global ??
unsigned long oldTime;

/*=========================================*/


void setup(){
    Serial.begin(SERIAL_SPEED);
   
   oldTime = millis();
}

void loop() {
   if(millis() - oldTime > period){
     cli();


   #ifdef DEBUG
      Serial.print("D:");
      Serial.println(0);
      Serial.flush();
      Serial.print("B:");
      Serial.println(0);
      Serial.flush();
      Serial.print("S:");
      Serial.println(0);
      Serial.flush();
      Serial.print("H:");
      Serial.println(0);
      Serial.flush();
      Serial.print("H_MIN:");
      Serial.println(0);
      Serial.flush();
      Serial.print("P:");
      Serial.println(0);
      Serial.flush();
   #endif
      
      flowFrequency = 0;
      oldTime = millis();
      sei();
   }

}

void serialEvent() {
  while (Serial.available() > 0) {

      String i = Serial.readString();
      Serial.println(i);
      Serial.flush();
   }
}
