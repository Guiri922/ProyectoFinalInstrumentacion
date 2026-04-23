int PinIR = A0;

void setup(){
  Serial.begin(9600);
  analogReadResolution(14);
}

void loop(){
  int number_for_avarage=0;
  for(int i=0; i<30; i++){
      number_for_avarage += int(analogRead(PinIR));
      delay(2);
  }
  Serial.println(int(number_for_avarage/30.0));
  delay(50);
}