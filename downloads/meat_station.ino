// Meat inspection belt station — ESP32 firmware (ESP32-DevKitC, Arduino-ESP32 core 3.x)
// COMPACT demo belt: the belt only moves while a tray is being processed; after CLEAR it stops and waits (pick the tray up at the exit, then load the next).
// Belt: 12 V DC right-angle worm gearmotor with Hall quadrature encoder (JGY-370 class, ~66 rpm, self-locking) + Cytron MD13S driver (PWM + DIR) on a Ø32 roller;
// position comes from the encoder (closed loop), there is no stepper.  Station sequence (stop-and-capture):
//   FEED (belt runs slowly) → IR sees the tray → advance D_CAM → AT_CAM (host captures the images) → advance D_SEN → AT_SEN (read AS7341 / MLX90614 / MQ-137)
//   → advance D_CLEAR (tray leaves the tunnel) → FEED
// Host protocol: 115200 baud, one command per line, one JSON object per line back.  See ../README.md.
// Safety: the E-stop cuts the 12 V rail (Cytron driver + servo buck + LED); GPIO ESTOP_OK reads the 12 V rail through an optocoupler/divider:
// LOW = power cut → the motor command is zeroed here as well and the station stays in ESTOP until the START button is pressed with power back.
// NOT a certified safety function — the E-stop is a hardware power cut only.
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <Adafruit_AS7341.h>
#include <Adafruit_MLX90614.h>
#include "esp_timer.h"

enum State { S_IDLE, S_FEED, S_TO_CAM, S_AT_CAM, S_TO_SEN, S_AT_SEN, S_CLEAR, S_ESTOP };

// ------------------------------------------------------------------ pins (ESP32-DevKitC)
static const int PIN_PWM = 26;       // Cytron MD13S PWM (20 kHz max)
static const int PIN_DIR = 27;       // Cytron MD13S DIR
static const int PIN_ENC_A = 13;     // motor Hall encoder A (power the encoder from 3V3, NOT from the motor supply)
static const int PIN_ENC_B = 14;     // motor Hall encoder B
static const int PIN_IR = 34;        // E18-D80NK open-collector output + 10 k pull-up to 3V3 (input-only pin), LOW = object present
static const int PIN_START = 32;     // START button to GND (internal pull-up)
static const int PIN_ESTOP_OK = 33;  // HIGH = 12 V present (E-stop released), through optocoupler or 100k/47k divider
static const int PIN_LED_W = 16;     // MOSFET gate: white 5000 K COB
static const int PIN_LED_NIR = 17;   // MOSFET gate: NIR 850 nm bars
static const int PIN_LED_UV = 18;    // MOSFET gate: UV 365 nm bars
static const int PIN_BUZZER = 19;
static const int PIN_SDA = 21;
static const int PIN_SCL = 22;
static const int PIN_MQ = 35;        // MQ-137 AO through a 10 k/20 k divider (module AO swings to 5 V), input-only pin

// ------------------------------------------------------------------ mechanics / sequence (mm)
// counts per mm = encoder counts per output-shaft turn (x4 quadrature) / (π × 32 mm roller).  JGY-370 worm gearmotor (~66 rpm): the real PPR and
// ratio are NOT known (sellers differ) — the value below is a placeholder (11 PPR × 4 × 81 = 3564 per turn): you MUST run CAL (ADV 100, measure the travel,
// CAL = old × 100 / measured) before trusting any distance.
static float counts_per_mm = 3564.0f / (PI * 32.0f);          // ≈ 35.5 placeholder, overwritten by CAL (stored in NVS)
static float belt_speed_mm_s = 50.0f;                          // feed + travel speed
static float accel_mm_s2 = 150.0f;
static float D_CAM = 35.0f;      // IR (x 140) → camera station (x 175)
static float D_SEN = 65.0f;      // camera → spectral/thermal station (x 240)
static float D_CLEAR = 100.0f;   // sensors → tray is out of the tunnel (compact belt: stays on the belt, waiting to be picked up)
static const uint32_t CAM_TIMEOUT_MS = 12000;   // host did not answer NEXT → continue and flag
static const uint32_t SEN_SETTLE_MS = 1200;
static const uint32_t IR_DEBOUNCE_MS = 30;

// ------------------------------------------------------------------ DC motor + encoder, 1 kHz position loop with trapezoid profile
static volatile int32_t enc_count = 0;
static volatile uint8_t enc_prev = 0;
static const int8_t ENC_TAB[16] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0};
static void IRAM_ATTR encISR() {
  uint8_t cur = (digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B);
  enc_count += ENC_TAB[(enc_prev << 2) | cur];
  enc_prev = cur;
}

static esp_timer_handle_t ctlTimer;
static volatile bool moving = false;
static volatile bool run_forever = false;
static volatile float tgt_pos = 0, tgt_vel = 0;   // profile position [counts], velocity [counts/s]
static volatile float goal_pos = 0;
static float v_max = 2000, a_max = 6000;
static float Kp = 8.0f, Ki = 0.02f, Kd = 25.0f, Kff = 0.26f;  // duty (0..1023) per count / per count-s / per count/ms / per count/s — initial values, TUNE on the real motor
static const float DUTY_MIN = 60;                  // stiction compensation
static float i_term = 0, e_prev = 0;
static volatile bool motor_on = false;
static volatile bool stalled = false;
static uint32_t settle_ms = 0, stall_ms = 0;
static int32_t pos_last = 0;
static volatile float last_duty = 0;

static void motorWrite(float u) {          // u: signed duty, -1023..1023
  last_duty = u;
  float m = fabsf(u);
  if (m < 1) { ledcWrite(PIN_PWM, 0); return; }
  m = constrain(m + DUTY_MIN, 0.0f, 1023.0f);
  digitalWrite(PIN_DIR, u >= 0 ? HIGH : LOW);
  ledcWrite(PIN_PWM, (uint32_t)m);
}

static void ctlCallback(void *) {          // runs every 1 ms
  if (!motor_on) { ledcWrite(PIN_PWM, 0); return; }
  const float dt = 0.001f;
  int32_t pos = enc_count;
  if (moving) {
    if (run_forever) {
      tgt_vel = min(tgt_vel + a_max * dt, v_max);
      tgt_pos += tgt_vel * dt;
      if (tgt_pos - pos > 400) tgt_pos = pos + 400;        // never run away from the tray if the belt is blocked
    } else {
      float rem = goal_pos - tgt_pos;
      float v_stop = sqrtf(2.0f * a_max * fabsf(rem));
      float v_des = min(v_max, v_stop);
      if (tgt_vel < v_des) tgt_vel = min(tgt_vel + a_max * dt, v_des); else tgt_vel = max(tgt_vel - a_max * dt, v_des);
      if (tgt_vel < 80 && fabsf(rem) > 0.5f) tgt_vel = 80;
      float step = tgt_vel * dt;
      if (step >= rem) { tgt_pos = goal_pos; tgt_vel = 0; } else tgt_pos += step;
    }
  } else { tgt_vel = 0; }
  float e = tgt_pos - pos;
  i_term = constrain(i_term + Ki * e, -200.0f, 200.0f);
  float u = Kp * e + i_term + Kd * (e - e_prev) + Kff * tgt_vel;
  e_prev = e;
  u = constrain(u, -700.0f, 700.0f);                           // limit torque / current (≈ 70 %)
  motorWrite(u);
  if (moving && !run_forever && tgt_pos == goal_pos && fabsf(goal_pos - pos) < 6) {
    if (++settle_ms > 80) { moving = false; settle_ms = 0; i_term = 0; }
  } else settle_ms = 0;
  // stall guard: high command but the encoder does not move for 0.8 s
  if (moving && fabsf(last_duty) > 450 && abs(pos - pos_last) < 4) { if (++stall_ms > 800) { stalled = true; moving = false; motor_on = false; ledcWrite(PIN_PWM, 0); } }
  else stall_ms = 0;
  if ((ets_get_cpu_frequency() > 0) && (esp_timer_get_time() & 0x3FF) == 0) pos_last = pos;   // sample ~ every 1 ms-ish window
}

static void startMove(float mm, bool forever = false) {
  if (moving) return;
  v_max = belt_speed_mm_s * counts_per_mm;
  a_max = accel_mm_s2 * counts_per_mm;
  motor_on = true; stalled = false;
  tgt_pos = enc_count; tgt_vel = 0; e_prev = 0; i_term = 0; stall_ms = 0; pos_last = enc_count;
  run_forever = forever;
  goal_pos = tgt_pos + mm * counts_per_mm;
  moving = true;
}

static void stopMove() {
  moving = false; run_forever = false;
  tgt_vel = 0; tgt_pos = enc_count;                  // hold where we are
}
static void motorEnable(bool on) { motor_on = on; if (!on) ledcWrite(PIN_PWM, 0); }

// ------------------------------------------------------------------ sensors
static Adafruit_AS7341 as7341;
static Adafruit_MLX90614 mlx;
static bool have_as = false, have_mlx = false;

// ------------------------------------------------------------------ state machine
static State state = S_IDLE;
static const char *stateName(State s) {
  switch (s) {
    case S_IDLE: return "idle"; case S_FEED: return "feed"; case S_TO_CAM: return "to_cam"; case S_AT_CAM: return "at_cam";
    case S_TO_SEN: return "to_sen"; case S_AT_SEN: return "at_sen"; case S_CLEAR: return "clear"; default: return "estop";
  }
}
static uint32_t t_state = 0;
static uint32_t tray_id = 0;
static bool cam_timed_out = false;
static bool auto_mode = true;
static bool ir_prev = false;
static uint32_t ir_change = 0;
static Preferences prefs;

static void setState(State s) {
  state = s; t_state = millis();
  Serial.printf("{\"ev\":\"state\",\"state\":\"%s\",\"id\":%lu}\n", stateName(s), (unsigned long)tray_id);
}

static void beep(int ms) { digitalWrite(PIN_BUZZER, HIGH); delay(ms); digitalWrite(PIN_BUZZER, LOW); }

static bool irActive() { return digitalRead(PIN_IR) == LOW; }
static bool powerOk() { return digitalRead(PIN_ESTOP_OK) == HIGH; }

static void setLed(const String &ch, int v) {
  v = constrain(v, 0, 255);
  if (ch == "W") ledcWrite(PIN_LED_W, v);
  else if (ch == "NIR") ledcWrite(PIN_LED_NIR, v);
  else if (ch == "UV") ledcWrite(PIN_LED_UV, v);
}
static void allLedOff() { ledcWrite(PIN_LED_W, 0); ledcWrite(PIN_LED_NIR, 0); ledcWrite(PIN_LED_UV, 0); }

static void readSensors() {
  float to = NAN, ta = NAN;
  if (have_mlx) { to = mlx.readObjectTempC(); ta = mlx.readAmbientTempC(); }
  long mq = 0;
  for (int i = 0; i < 16; i++) { mq += analogRead(PIN_MQ); delay(2); }
  mq /= 16;
  Serial.printf("{\"ev\":\"sensors\",\"id\":%lu,\"t_obj\":%.2f,\"t_amb\":%.2f,\"mq137_raw\":%ld,\"as\":", (unsigned long)tray_id, to, ta, mq);
  if (have_as && as7341.readAllChannels()) {
    // F1 415, F2 445, F3 480, F4 515, F5 555, F6 590, F7 630, F8 680 nm, Clear, NIR
    Serial.printf("[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u]",
                  as7341.getChannel(AS7341_CHANNEL_415nm_F1), as7341.getChannel(AS7341_CHANNEL_445nm_F2),
                  as7341.getChannel(AS7341_CHANNEL_480nm_F3), as7341.getChannel(AS7341_CHANNEL_515nm_F4),
                  as7341.getChannel(AS7341_CHANNEL_555nm_F5), as7341.getChannel(AS7341_CHANNEL_590nm_F6),
                  as7341.getChannel(AS7341_CHANNEL_630nm_F7), as7341.getChannel(AS7341_CHANNEL_680nm_F8),
                  as7341.getChannel(AS7341_CHANNEL_CLEAR), as7341.getChannel(AS7341_CHANNEL_NIR));
  } else {
    Serial.print("null");
  }
  Serial.println("}");
}

static void printStatus() {
  Serial.printf("{\"ev\":\"status\",\"state\":\"%s\",\"id\":%lu,\"moving\":%d,\"ir\":%d,\"power_ok\":%d,\"counts_per_mm\":%.3f,\"speed\":%.1f,\"d_cam\":%.1f,\"d_sen\":%.1f,\"d_clear\":%.1f,\"as7341\":%d,\"mlx90614\":%d,\"auto\":%d}\n",
                stateName(state), (unsigned long)tray_id, (int)moving, (int)irActive(), (int)powerOk(), counts_per_mm, belt_speed_mm_s,
                D_CAM, D_SEN, D_CLEAR, (int)have_as, (int)have_mlx, (int)auto_mode);
}

// ------------------------------------------------------------------ host commands
static String line;
static void handleCommand(String cmd) {
  cmd.trim();
  if (!cmd.length()) return;
  String up = cmd; up.toUpperCase();
  int sp = cmd.indexOf(' ');
  String a1 = sp > 0 ? cmd.substring(sp + 1) : "";
  a1.trim();
  if (up == "PING") { Serial.println("{\"ev\":\"pong\"}"); }
  else if (up == "STATUS") { printStatus(); }
  else if (up.startsWith("RUN")) { if (powerOk()) { setState(S_FEED); } else Serial.println("{\"ev\":\"error\",\"msg\":\"power off (E-stop)\"}"); }
  else if (up == "STOP") { stopMove(); motorEnable(false); setState(S_IDLE); }
  else if (up.startsWith("SPEED ")) { belt_speed_mm_s = constrain(a1.toFloat(), 10.0f, 120.0f); printStatus(); }
  else if (up.startsWith("DIST ")) {                          // DIST cam sen clear
    float c = a1.toFloat(); int s2 = a1.indexOf(' ');
    if (s2 > 0) { String r = a1.substring(s2 + 1); r.trim(); float s3 = r.toFloat(); int s4 = r.indexOf(' ');
      if (s4 > 0) { String r2 = r.substring(s4 + 1); r2.trim(); D_CLEAR = r2.toFloat(); }
      D_CAM = c; D_SEN = s3; }
    printStatus();
  }
  else if (up.startsWith("ADV ")) { if (powerOk()) { stopMove(); startMove(a1.toFloat()); Serial.println("{\"ev\":\"adv_start\"}"); } }
  else if (up.startsWith("LED ")) { int s2 = a1.indexOf(' '); if (s2 > 0) { String ch = a1.substring(0, s2); ch.toUpperCase(); setLed(ch, a1.substring(s2 + 1).toInt()); Serial.println("{\"ev\":\"led_ok\"}"); } }
  else if (up == "ALLOFF") { allLedOff(); }
  else if (up == "READ") { readSensors(); }
  else if (up == "NEXT") { if (state == S_AT_CAM) { allLedOff(); setState(S_TO_SEN); startMove(D_SEN); } }
  else if (up.startsWith("AUTO ")) { auto_mode = a1.toInt() != 0; printStatus(); }
  else if (up.startsWith("CAL ")) { float v = a1.toFloat(); if (v > 5 && v < 400) { counts_per_mm = v; prefs.putFloat("cpmm", v); } printStatus(); }
  else if (up.startsWith("PID ")) { float k1 = a1.toFloat(); int p2 = a1.indexOf(' '); if (p2 > 0) { String r = a1.substring(p2 + 1); r.trim(); Ki = r.toFloat(); int p3 = r.indexOf(' '); if (p3 > 0) { Kd = r.substring(p3 + 1).toFloat(); } } Kp = k1; Serial.printf("{\"ev\":\"pid\",\"kp\":%.3f,\"ki\":%.3f,\"kd\":%.3f,\"kff\":%.3f}\n", Kp, Ki, Kd, Kff); }
  else if (up == "ENC") { Serial.printf("{\"ev\":\"enc\",\"count\":%ld,\"duty\":%.0f}\n", (long)enc_count, last_duty); }
  else { Serial.println("{\"ev\":\"error\",\"msg\":\"unknown command\"}"); }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DIR, OUTPUT);
  ledcAttach(PIN_PWM, 20000, 10);
  ledcWrite(PIN_PWM, 0);
  pinMode(PIN_ENC_A, INPUT_PULLUP); pinMode(PIN_ENC_B, INPUT_PULLUP);
  enc_prev = (digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), encISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_B), encISR, CHANGE);
  motorEnable(false);
  pinMode(PIN_IR, INPUT); pinMode(PIN_START, INPUT_PULLUP); pinMode(PIN_ESTOP_OK, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  ledcAttach(PIN_LED_W, 5000, 8); ledcAttach(PIN_LED_NIR, 5000, 8); ledcAttach(PIN_LED_UV, 5000, 8);
  allLedOff();
  analogReadResolution(12);
  Wire.begin(PIN_SDA, PIN_SCL);
  have_as = as7341.begin();
  if (have_as) { as7341.setATIME(100); as7341.setASTEP(999); as7341.setGain(AS7341_GAIN_64X); }
  have_mlx = mlx.begin();
  prefs.begin("meatqa", false);
  counts_per_mm = prefs.getFloat("cpmm", counts_per_mm);
  esp_timer_create_args_t args = {};
  args.callback = &ctlCallback;
  args.name = "ctl";
  esp_timer_create(&args, &ctlTimer);
  esp_timer_start_periodic(ctlTimer, 1000);
  Serial.println("{\"ev\":\"boot\",\"fw\":\"meat_station 1.0\"}");
  printStatus();
  if (!powerOk()) setState(S_ESTOP);
}

void loop() {
  // serial commands
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') { handleCommand(line); line = ""; }
    else if (c != '\r' && line.length() < 80) line += c;
  }
  if (stalled) { stalled = false; allLedOff(); Serial.println("{\"ev\":\"error\",\"msg\":\"motor stall - belt blocked or encoder missing\"}"); beep(400); setState(S_IDLE); }
  // E-stop / power loss: the hardware already cut the 12 V, make the firmware agree
  if (!powerOk() && state != S_ESTOP) {
    stopMove(); motorEnable(false); allLedOff(); setState(S_ESTOP); beep(200);
  }
  // START button (active low, debounced by time)
  static uint32_t t_btn = 0;
  if (digitalRead(PIN_START) == LOW && millis() - t_btn > 400) {
    t_btn = millis();
    if (state == S_ESTOP) { if (powerOk()) { setState(S_IDLE); beep(60); } }
    else if (state == S_IDLE) { setState(S_FEED); beep(60); }
    else { stopMove(); motorEnable(false); allLedOff(); setState(S_IDLE); beep(60); }
  }
  // IR debounce
  bool ir = irActive();
  if (ir != ir_prev && millis() - ir_change > IR_DEBOUNCE_MS) {
    ir_prev = ir; ir_change = millis();
    if (ir && state == S_FEED && auto_mode) {                  // leading edge of a tray
      tray_id++; cam_timed_out = false;
      stopMove();
      setState(S_TO_CAM);
      startMove(D_CAM);
    }
  }
  // sequence
  switch (state) {
    case S_TO_CAM:
      if (!moving) { setState(S_AT_CAM); Serial.printf("{\"ev\":\"at_cam\",\"id\":%lu}\n", (unsigned long)tray_id); }
      break;
    case S_AT_CAM:
      if (millis() - t_state > CAM_TIMEOUT_MS) { cam_timed_out = true; Serial.println("{\"ev\":\"error\",\"msg\":\"host timeout at camera\"}"); allLedOff(); setState(S_TO_SEN); startMove(D_SEN); }
      break;
    case S_TO_SEN:
      if (!moving) { setState(S_AT_SEN); }
      break;
    case S_AT_SEN:
      if (millis() - t_state > SEN_SETTLE_MS) { readSensors(); setState(S_CLEAR); startMove(D_CLEAR); }
      break;
    case S_CLEAR:
      if (!moving) { Serial.printf("{\"ev\":\"tray_done\",\"id\":%lu,\"cam_timeout\":%d}\n", (unsigned long)tray_id, (int)cam_timed_out); setState(S_FEED); }
      break;
    default: break;
  }
  delay(1);
}
