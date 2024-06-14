#include <AccelStepper.h>

// Define the stepper motors and the pins they are connected to
AccelStepper stepper1(AccelStepper::DRIVER, 22, 24);
AccelStepper stepper2(AccelStepper::DRIVER, 28, 30);
AccelStepper stepper3(AccelStepper::DRIVER, 34, 36);
AccelStepper stepper4(AccelStepper::DRIVER, 40, 42);
AccelStepper stepper5(AccelStepper::DRIVER, 46, 48);

// microstepping pins
const int mStepPin1 = 23;
const int mStepPin2 = 29;
const int mStepPin3 = 35;
const int mStepPin4 = 41;
const int mStepPin5 = 47;

// Thermistor setup
const int pinA = 8;
const int pinB = 10;

int thermistorPin1 = A1;
int thermistorPin2 = A2;
int thermistorPin3 = A3;
int thermistorPin4 = A4;

float Rdivider = 2000;
float B = 3499, Tref = 298, R1 = 2000; // constants for the temperature calculation from the thermistor value

int heatingDirection = 0;
int heatingCycle = 50;

// INPUT CONTROL USER
float setpoint = 40;
int controller = 1;
int threshold = 0.5;
int Icontroller = 0; // 0 is off

bool running = true;

unsigned long lastTime = 0;

unsigned long startTime;
unsigned long duration1, duration2, duration3, duration4, duration5;
bool runningStepper = false;

// Function declarations
void processCommand(String command);
void setAllSpeeds(int speed1, int speed2, int speed3, int speed4, int speed5);
void setVolumeAndSpeed(int volume1, int speed1, int volume2, int speed2, int volume3, int speed3, int volume4, int speed4, int volume5, int speed5);
void stopAll();
void resetAllMotors(int speed, int delayTime);

void setup() {
  Serial.begin(115200);  // Use a higher baud rate for faster communication

  stepper1.setMaxSpeed(1000);
  stepper2.setMaxSpeed(1000);
  stepper3.setMaxSpeed(1000);
  stepper4.setMaxSpeed(1000);
  stepper5.setMaxSpeed(1000);

  pinMode(pinA, OUTPUT);
  pinMode(pinB, OUTPUT);
  pinMode(thermistorPin1, INPUT);
  pinMode(thermistorPin2, INPUT);
  pinMode(thermistorPin3, INPUT);
  pinMode(thermistorPin4, INPUT);

  digitalWrite(mStepPin1, HIGH);
  digitalWrite(mStepPin2, HIGH);
  digitalWrite(mStepPin3, HIGH);
  digitalWrite(mStepPin4, HIGH);
  digitalWrite(mStepPin5, HIGH);
}


void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    // Serial.print(command);
    processCommand(command);
  }

  // Run stepper motors if they are running
  if (runningStepper) {
    unsigned long currentTime = millis();
    if (currentTime - startTime < duration1) {
      stepper1.runSpeed();
    } else {
      stepper1.setSpeed(0);
    }
    if (currentTime - startTime < duration2) {
      stepper2.runSpeed();
    } else {
      stepper2.setSpeed(0);
    }
    if (currentTime - startTime < duration3) {
      stepper3.runSpeed();
    } else {
      stepper3.setSpeed(0);
    }
    if (currentTime - startTime < duration4) {
      stepper4.runSpeed();
    } else {
      stepper4.setSpeed(0);
    }
    if (currentTime - startTime < duration5) {
      stepper5.runSpeed();
    } else {
      stepper5.setSpeed(0);
    }

    // Check if all durations have elapsed
    if ((currentTime - startTime >= duration1) &&
        (currentTime - startTime >= duration2) &&
        (currentTime - startTime >= duration3) &&
        (currentTime - startTime >= duration4) &&
        (currentTime - startTime >= duration5)) {
      runningStepper = false; // Stop running the steppers
    }
  }

  // Temperature control
  if (running) {
    controlHeating();
    float T = readTemperatures();
    // Send temperature only when requested to avoid unnecessary serial communication
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command.startsWith("T")) {
        Serial.println(T);
      }
    }
  } else {
    analogWrite(pinA, 0);
    analogWrite(pinB, 0);
  }
}

float readTemperatures() {
  int Vo;
  float R2, logR2, T1, T2, T4;

  Vo = analogRead(thermistorPin1);
  R2 = Rdivider * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T1 = (1.0 / ((log(R2/R1) / B) + (1.0 / Tref))) - 273.15;

  Vo = analogRead(thermistorPin2);
  R2 = Rdivider * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T2 = (1.0 / ((log(R2/R1) / B) + (1.0 / Tref))) - 273.15;

  Vo = analogRead(thermistorPin4);
  R2 = Rdivider * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T4 = (1.0 / ((log(R2/R1) / B) + (1.0 / Tref))) - 273.15;

  return (T1 + T2 + T4) / 3;
}

void controlHeating() {
  unsigned long currentTime = millis();
  unsigned long changeTime = currentTime - lastTime;
  lastTime = currentTime;

  float T = readTemperatures();

  if (heatingDirection == 0) {
    analogWrite(pinA, heatingCycle);
    digitalWrite(pinB, LOW);
  } else {
    digitalWrite(pinA, LOW);
    analogWrite(pinB, heatingCycle);
  }

  if (T > setpoint) {
    // heatingCycle has a maximum of 155 to reduce big oscillations, this maximum could be lowered to reduce oscillations
    if (heatingDirection == 1 && heatingCycle < 155 - threshold) {
      heatingCycle += controller * (T - setpoint) + Icontroller * (T - setpoint) * changeTime;
      if (heatingCycle > 255) {
        heatingCycle = 255;
      }
    } else if (heatingDirection == 0 && heatingCycle > threshold) {
      heatingCycle -= controller * (T - setpoint) + Icontroller * (T - setpoint) * changeTime;
    }
    if (heatingCycle <= threshold) {
      heatingDirection = heatingDirection ^ 1;
    }
    // Serial.print(heatingDirection);
    // Serial.println(heatingCycle);
  } else {
    if (heatingDirection == 1 && heatingCycle > threshold) {
      heatingCycle -= controller * (setpoint - T) + Icontroller * (setpoint - T) * changeTime;

    } else if (heatingDirection == 0 && heatingCycle < 155 - threshold) {
      heatingCycle += controller * (setpoint - T) + Icontroller * (setpoint - T) * changeTime;

      if (heatingCycle > 255) {
        heatingCycle = 255;
      }
    }
    if (heatingCycle <= threshold) {
      heatingDirection = heatingDirection ^ 1;
    }
    // Serial.print(heatingDirection);
    // Serial.println(heatingCycle);
  }

  // if (heatingDirection == 0) {
  //   analogWrite(pinA, heatingCycle);
  //   digitalWrite(pinB, LOW);
  // } else {
  //   digitalWrite(pinA, LOW);
  //   analogWrite(pinB, heatingCycle);
  // }
}

void processCommand(String command) {
  Serial.print(command);
  if (command.startsWith("TSPEED")) {
    int speed1, speed2, speed3, speed4, speed5;
    sscanf(command.c_str(), "SPEED %d %d %d %d %d", &speed1, &speed2, &speed3, &speed4, &speed5);
    setAllSpeeds(speed1, speed2, speed3, speed4, speed5);
  } else if (command.startsWith("TVOLUME")) {
    // Serial.println('hel');
    long volume1, speed1, volume2, speed2, volume3, speed3, volume4, speed4, volume5, speed5;
    sscanf(command.c_str(), "TVOLUME %ld %d %ld %d %ld %d %ld %d %ld %d", &volume1, &speed1, &volume2, &speed2, &volume3, &speed3, &volume4, &speed4, &volume5, &speed5);
    setVolumeAndSpeed(volume1, speed1, volume2, speed2, volume3, speed3, volume4, speed4, volume5, speed5);
    Serial.print(speed1);
  } else if (command.startsWith("TCONTROLLER=")) {
    controller = command.substring(12).toInt();
  } else if (command.startsWith("TSETPOINT=")) {
    setpoint = command.substring(10).toFloat();
  } else if (command == "TSTOP") {
    running = false;
    Serial.println("Experiment stopped.");
  } else if (command == "START") {
    running = true;
    Serial.println("Experiment started.");
  } else if (command.startsWith("TRESET")) {
    int speed, delayTime;
    sscanf(command.c_str(), "RESET %d %d", &speed, &delayTime);
    resetAllMotors(speed, delayTime);
  }
}

void setAllSpeeds(int speed1, int speed2, int speed3, int speed4, int speed5) {
  stepper1.setSpeed(speed1);
  stepper2.setSpeed(speed2);
  stepper3.setSpeed(speed3);
  stepper4.setSpeed(speed4);
  stepper5.setSpeed(speed5);
}

void setVolumeAndSpeed(int volume1, int speed1, int volume2, int speed2, int volume3, int speed3, int volume4, int speed4, int volume5, int speed5) {
  const float VOLUME_TO_SPEED_FACTOR = 0.36;
  const float SPEED_OFFSET = 2.85;
  // const float SPEED_OFFSET = 0;

  int stepperSpeed1 = round(VOLUME_TO_SPEED_FACTOR * speed1 + SPEED_OFFSET);
  int stepperSpeed2 = round(VOLUME_TO_SPEED_FACTOR * speed2 + SPEED_OFFSET);
  int stepperSpeed3 = round(VOLUME_TO_SPEED_FACTOR * speed3 + SPEED_OFFSET);
  int stepperSpeed4 = round(VOLUME_TO_SPEED_FACTOR * speed4 + SPEED_OFFSET);
  int stepperSpeed5 = round(VOLUME_TO_SPEED_FACTOR * speed5 + SPEED_OFFSET);

  stepper1.setSpeed(stepperSpeed1);
  stepper2.setSpeed(stepperSpeed2);
  stepper3.setSpeed(stepperSpeed3);
  stepper4.setSpeed(stepperSpeed4);
  stepper5.setSpeed(stepperSpeed5);
  // Serial.print(stepperSpeed1);

  duration1 = volume1 / abs(speed1) * 1000;
  duration2 = volume2 / abs(speed2) * 1000;
  duration3 = volume3 / abs(speed3) * 1000;
  duration4 = volume4 / abs(speed4) * 1000;
  duration5 = volume5 / abs(speed5) * 1000;

  startTime = millis();
  runningStepper = true;
}

void stopAll() {
  stepper1.setSpeed(0);
  stepper2.setSpeed(0);
  stepper3.setSpeed(0);
  stepper4.setSpeed(0);
  stepper5.setSpeed(0);
  running = false;
}

void resetAllMotors(int speed, int delayTime) {
  setAllSpeeds(speed, speed, speed, speed, speed);
  // delay(delayTime);
  // stopAll();
}
