int PinIR = A5;

void setup(){
  Serial.begin(9600);
  analogReadResolution(14);
}

void loop(){
  Serial.println(analogRead(PinIR));
  delay(20);
}