#define AREAD_PIN1 A1
#define AREAD_PIN2 A2
#define AREAD_PIN3 A3

#define PWM_OUT_PIN1 9
#define PWM_OUT_PIN2 8
#define PWM_OUT_PIN3 6

int a1input = 0;
int a2input = 0;
int a3input = 0;
int power1 = 0;
int power2 = 0;
int power3 = 0;

int threshold = 30;
int step = 5;
int delayMs = 250;

void setup() {
  pinMode(AREAD_PIN1, INPUT);
  pinMode(AREAD_PIN2, INPUT);
  pinMode(AREAD_PIN3, INPUT);
  pinMode(PWM_OUT_PIN1, OUTPUT);
  pinMode(PWM_OUT_PIN2, OUTPUT);
  pinMode(PWM_OUT_PIN3, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  readInputs();
  power1 = reCalculate(power1, a1input);
  power2 = reCalculate(power2, a2input);
  power3 = reCalculate(power3, a3input);
  log();
  writeAll();
  delay(delayMs);
}

void log() {
  Serial.print("power1:");
  Serial.print(power1);
  Serial.print(",");
  Serial.print("power2:");
  Serial.print(power2);
  Serial.print(",");
  Serial.print("power3:");
  Serial.print(power3);
  Serial.println(threshold);
}

int reCalculate(int power, int input) {
  if (input > threshold) {
    power = power - step;
  } else if (input < threshold) {
    power = power + step;
  } else {
    return power;
  }
  if (power < 0) return 0;
  if (power > 255) return 255;
  return power; 
}

void readInputs() {
  a1input = analogRead(AREAD_PIN1);
  a2input = analogRead(AREAD_PIN2);
  a3input = analogRead(AREAD_PIN3);
}

void writeAll() {
  analogWrite(PWM_OUT_PIN1, power1);
  analogWrite(PWM_OUT_PIN2, power2);
  analogWrite(PWM_OUT_PIN3, power3);
}