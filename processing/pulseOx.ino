// Create an IntervalTimer object 
IntervalTimer myTimer;

int LEDtimer = 0;
int blinkTime = 1;  // time in seconds for which to keep each LED on.

// next we make arrays for storing the data temporarily and then releasing it at leisure by Serial
// they are ints because they take the least amount of space (in bits) for storage on RAM and the ADC output is int anyway, so that's great
int i = 0;   // the counter for the array position
int redData[1000], irData[1000];  // 1000 samples = 200 samples/second for 5 seconds

void setup(void) {
  Serial.begin(115200);
  analogReadRes(13);
  
  pinMode(3, OUTPUT);  // 640nm LED
  pinMode(4, OUTPUT);  // 850nm LED
  
  // myTimer.begin(captureData, 5000);
}

void captureDataRed(void) {
  // save the data real quick into the respective array
  if (i < 1000) {
    redData[i] = analogRead(A0);
  }
  i++;
  // Serial.println(analogRead(A0));
}
void captureDataIR(void) {
  // save the data real quick into the respective array
  if (i < 1000) {
    irData[i] = analogRead(A0);
  }
  i++;
  // Serial.println(analogRead(A0));
}

// the next are hte functions to turn on the red and the IR led. arguments passed would be the blink time.
void gimmeRed() {
  digitalWrite(4, LOW);
  digitalWrite(3, HIGH); 
}
void gimmeIR() {
  digitalWrite(3, LOW);
  digitalWrite(4, HIGH);
  delay(blinkTime*1000);    
}
void lightsOff() {
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
}

void loop(void) {
  while (Serial.available()) {
    // get the new byte:
    char inChar = Serial.read(); 
    if (inChar == 'r') {
      // put on the red LED and start acquiring into the array..
      gimmeRed();
      i = 0;
      delay(500);  // a slight delay to let the photodiode RC constant not muck things up
      myTimer.begin(captureDataRed, 5000);
    } else if (inChar == 'i') {
      gimmeIR();
      i = 0;
      delay(500);  // a slight delay to let the photodiode RC constant not muck things up
      myTimer.begin(captureDataIR, 5000);
    } else if (inChar == 'q') {
      // put lights off.
       lightsOff();
       // stop acquiring data, i.e. end the timerIntervals, all of them
       i = 1001;
       myTimer.end();
    } else if (inChar == 't') {
      // wait for 100ms
      delay(100);
       // transmit the data, from both arrays, as a tab delimited line...
      for (int j = 0; j<1000; j++) {
        Serial.print(redData[j]);
        Serial.print('\t');
        Serial.println(irData[j]);
        // delay(1);  // a small delay just to give python (which will be receiving the data) enough time to process
      }
    }
  }
}
