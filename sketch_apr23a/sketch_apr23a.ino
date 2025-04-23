void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT); // LED verde (acerto)
  pinMode(12, OUTPUT); // LED vermelho (erro)
}

void loop() {
  if (Serial.available()) {
    char comando = Serial.read();

    if (comando == 'G') {
      digitalWrite(13, HIGH);
      delay(200);
      digitalWrite(13, LOW);
    }
    else if (comando == 'R') {
      digitalWrite(12, HIGH);
      delay(200);
      digitalWrite(12, LOW);
    }
  }
}