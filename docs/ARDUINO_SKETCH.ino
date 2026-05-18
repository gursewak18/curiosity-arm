/*
  Curiosity Arm Arduino Servo Receiver

  Expected serial command format:
  S:90;E:120
*/

#include <Servo.h>

Servo shoulderServo;
Servo elbowServo;

const int shoulderPin = 9;
const int elbowPin = 10;

void setup() {
  Serial.begin(115200);
  shoulderServo.attach(shoulderPin);
  elbowServo.attach(elbowPin);
  shoulderServo.write(90);
  elbowServo.write(90);
}

void loop() {
  if (!Serial.available()) {
    return;
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  int shoulderIndex = command.indexOf("S:");
  int elbowIndex = command.indexOf(";E:");

  if (shoulderIndex != 0 || elbowIndex < 0) {
    return;
  }

  int shoulderAngle = command.substring(2, elbowIndex).toInt();
  int elbowAngle = command.substring(elbowIndex + 3).toInt();

  shoulderServo.write(constrain(shoulderAngle, 0, 180));
  elbowServo.write(constrain(elbowAngle, 0, 180));
}

