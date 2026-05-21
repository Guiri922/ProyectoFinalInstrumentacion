int PinIR = A5;

void setup(){
  Serial.begin(9600);
  analogReadResolution(14);
}

void loop(){
  int number_for_avarage=0;
  Serial.println(analogRead(PinIR));
  delay(5);
}