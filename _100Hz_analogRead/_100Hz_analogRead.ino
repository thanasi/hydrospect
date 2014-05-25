//timer interrupts
//by Amanda Ghassaei
//June 2012
//http://www.instructables.com/id/Arduino-Timer-Interrupts/

// 2014 - 05 - 25
// This is a modified version of the code by DJ. I will be using Timer0 to make an interrupt happen every 100Hz
// and then I'll attempt to use port manipulation to quickly analogRead a pin and send it to the Serial port

void setup(){
  Serial.begin(115200);
  
  cli();//stop interrupts

//set timer0 interrupt at 2kHz
  TCCR0A = 0;// set entire TCCR2A register to 0
  TCCR0B = 0;// same for TCCR2B
  TCNT0  = 0;//initialize counter value to 0
  // set compare match register for 2khz increments
  OCR0A = 155;// = (16*10^6) / (100*64) - 1 (must be <256)
  // turn on CTC mode
  TCCR0A |= (1 << WGM01);
  // Set CS01 and CS00 bits for 64 prescaler
  TCCR0B |= (1 << CS12) | (1 << CS10);   
  // enable timer compare interrupt
  TIMSK0 |= (1 << OCIE0A);

  sei();//allow interrupts

}//end setup

ISR(TIMER0_COMPA_vect){//timer0 interrupt 
 
  Serial.println(analogRead(A0));
}

void loop(){
  // only needed as a formality

}
