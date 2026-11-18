# รายการสาย (wire list) — สถานีตรวจเนื้อ

ร่างจาก firmware ยังไม่ผ่านการตรวจโดยช่างไฟ · ตัวเลข # ตรงกับป้ายบนภาพ

| # | จาก | ไป | สี | หมายเหตุ | เบอร์สาย |
|---|---|---|---|---|---|
| 1 | E18.L | E7.L | brown | L · C14 → L · PSU | AWG18 |
| 2 | E18.N | E7.N | blue | N · C14 → N · PSU | AWG18 |
| 3 | E18.PE | E7.PE | green-yellow | PE · C14 → PE · PSU | AWG18 |
| 4 | E7.+V | E12.in | red | +V · PSU → in · E-stop NC | AWG18 |
| 5 | E12.out | J12.12V | red | out · E-stop NC → ราง +12 V | AWG18 |
| 6 | E7.-V | J12.GND | black | −V · PSU → GND | AWG18 |
| 7 | J12.12V | E8.IN+ | red | ราง +12 V → IN+ · LM2596 | AWG22 |
| 8 | J12.GND | E8.IN- | black | GND → IN− · LM2596 | AWG22 |
| 9 | E8.OUT+ | J12.5V | orange | OUT+ · 5 V → ราง +5 V | AWG22 |
| 10 | E8.OUT- | J12.GND2 | black | OUT− · GND → GND | AWG22 |
| 11 | E5.J7.1 | M1.J20.1 | red | M+ → M+ มอเตอร์ | AWG20 |
| 12 | E5.J7.2 | M1.J20.2 | white | M− → M− มอเตอร์ | AWG20 |
| 13 | GPIO26 | E5.J5.1 | yellow | GPIO26 → RPWM |  |
| 14 | GPIO27 | E5.J5.2 | yellow | GPIO27 → LPWM |  |
| 15 | J12.5V | E5.J5.3 | orange | +5 V → R_EN |  |
| 16 | J12.5V | E5.J5.4 | orange | +5 V → L_EN |  |
| 17 | J12.5V | E5.J5.7 | orange | +5 V → VCC |  |
| 18 | J12.GND | E5.J5.8 | black | GND → GND |  |
| 19 | J12.12V | E5.J6.1 | red | +12 V → B+ | AWG18 |
| 20 | J12.GND2 | E5.J6.2 | black | GND → B− | AWG18 |
| 21 | GPIO3V3 | M1.J21.1 | violet | 3V3 → E_VCC |  |
| 22 | J12.GND | M1.J21.2 | black | GND → E_GND |  |
| 23 | GPIO13 | M1.J21.3 | green | GPIO13 → E_A |  |
| 24 | GPIO14 | M1.J21.4 | green | GPIO14 → E_B |  |
| 25 | GPIOGND | J12.GND | black | GND · ESP32 → GND ร่วม |  |
| 26 | J12.5V | E9.BN | brown | +5 V → BN |  |
| 27 | J12.GND | E9.BU | blue | GND → BU |  |
| 28 | E9.BK | GPIO34 | black | BK สัญญาณ → GPIO34 |  |
| 29 | E9.BK | R3.1 | black | BK → R3 |  |
| 30 | R3.2 | GPIO3V3 | violet | R3 → 3V3 |  |
| 31 | B1.NO1 | GPIO32 | yellow | NO1 → GPIO32 |  |
| 32 | B1.NO2 | J12.GND2 | black | NO2 → GND |  |
| 33 | J12.12V | R1.1 | red | +12 V (หลัง E-stop) → R1 |  |
| 34 | R1.2 | GPIO33 | yellow | จุดกลาง R1/R2 → GPIO33 ESTOP_OK |  |
| 35 | R1.2 | R2.1 | yellow | R1 → R2 |  |
| 36 | R2.2 | J12.GND | black | R2 → GND |  |
| 60 | E4.' + PIN['22'] | S1.J40.4 | green | GPIO22 SCL → SCL |  |
| 61 | E4.' + PIN['22'] | S2.J41.3 | green | GPIO22 SCL → SCL |  |
| 62 | E4.' + PIN['21'] | S1.J40.5 | blue | GPIO21 SDA → SDA |  |
| 63 | E4.' + PIN['21'] | S2.J41.4 | blue | GPIO21 SDA → SDA |  |
| 64 | E4.' + PIN['19'] | BZ.+ | yellow | GPIO19 → + |  |
| 65 | S3.J42.4 | R4.1 | yellow | AO → R4 |  |
| 66 | R4.2 | E4.' + PIN['35'] | yellow | จุดกลาง → GPIO35 |  |
| 67 | R4.2 | R5.1 | yellow | R4 → R5 |  |

สายเบอร์ 60–77 ในหน้า 5 และสายแจกไฟ (+12 V, +5 V, GND) ในหน้า 4–5 เป็นป้ายปลายสาย ต่อไปที่ราง/ขาไฟตามชื่อ (ดูภาพ)
