int PinIR = A5;

void setup(){
  Serial.begin(9600);
  analogReadResolution(14);
}

void loop(){
  int numValues = Serial.parseInt();
  if(numValues>0){
  int Vadc[numValues];
  unsigned long T[numValues];
  unsigned long ref = micros();
  for(int i = 0; i<numValues;i++){
    Vadc[i] = analogRead(PinIR);
    unsigned long timeNow = micros()-ref;
    T[i] = timeNow;
    delay(40);

  }
  for(int i = 0; i< numValues;i++){
    Serial.print(Vadc[i]);
    if (i<numValues-1) {Serial.print(",");}
  }
  Serial.println();

  for(int i = 0;i<numValues;i++){
    Serial.print(T[i]);
    if(i<numValues-1) {Serial.print(",");}
  }
  Serial.println();
  }
}