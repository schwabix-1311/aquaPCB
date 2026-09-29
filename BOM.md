# aquaPCB – Bill of Materials (v1 draft)

Prices and stock checked 2026-09-29 (LCSC/JLCPCB parts API, reichelt.de product pages).
Quantities per board, taken from the schematic (`kicad-cli sch export bom`).
The ADS1115 address solder jumper JP4 is a PCB feature, no part.

Sourcing rule:
- **SMD → JLCPCB assembly.** JLC can only place parts from its own LCSC stock, so all SMD
  parts carry LCSC numbers and arrive already soldered. No separate LCSC order needed.
- **THT and large hand-soldered parts → Reichelt** (LCSC number as fallback where useful).

JLC "extended" parts cost a one-time loading fee per unique part and order (currently
about $3 each); "basic" parts don't. Prices below: LCSC USD at qty 1–49, excl. VAT;
Reichelt EUR incl. 19 % VAT.

## SMD, assembled by JLCPCB

| Qty | Function | Part | Package | LCSC | Lib | Stock | $/pc |
|---:|---|---|---|---|---|---:|---:|
| 1 | 5 V buck, 60 V, 3.5 A (non-synchronous) | TI TPS54360BDDAR | SOIC-8-EP | C524806 | ext | 59 416 | 0.75 |
| 1 | buck inductor 10 µH, 4.8 A, 20 mΩ | TDK SLF12565T-100M4R8-PF | 12.5×12.5 mm | C138303 | ext | 880 | 0.47 |
| 7 | freewheel Q1–Q6 + buck catch diode, 40 V 5 A | SS54 | SMA | C22452 | **basic** | 2.4 M | 0.04 |
| 6 | power switch Q1–Q6, 40 V, 7 mΩ@10 V | AOS AOD4184A | TO-252 | C99124 | ext | 12 730 | 0.35 |
| 1 | reverse-polarity P-FET, −40 V | AOS AOD4185 | TO-252 | C400894 | ext | 43 789 | 0.42 |
| 1 | P-FET gate clamp 15 V | BZT52C15 | SOD-123 | C173427 | ext | 224 233 | 0.02 |
| 1 | input TVS 33 V, 600 W | SMBJ33A | SMB | C78419 | ext | 12 040 | 0.07 |
| 1 | gate buffer 3.3 V → 5 V, 8 ch | Nexperia 74HCT244D,653 | SOIC-20 | C5978 | ext | 14 361 | 0.44 |
| 1 | SSR driver S1–S4 (+4 spare), 50 V 500 mA | onsemi ULN2803ADWMRG | SOIC-18W | C2977078 | ext | 14 917 | 0.20 |
| 1 | ADC 16 bit, 4 ch, I²C | TI ADS1115IDGSR | VSSOP-10 | C37593 | ext | 28 590 | 1.38 |
| 1 | pH buffer, dual CMOS, 0.5 pA bias, 1.8–5.5 V | TI TLV9062IDR | SOIC-8 | C398355 | ext | 171 837 | 0.12 |
| 1 | pH bias reference 2.495 V, ±0.5 % (TI DBZ pinout; not TL432) | TI TL431BCDBZR | SOT-23 | C6971 | ext | 6 717 | 0.13 |
| 7 | input/1-Wire/ADC clamps | BAT54S | SOT-23 | C12765 | ext | 211 230 | 0.01 |
| 1 | 3.3 V LDO 1 A | AMS1117-3.3 | SOT-223 | C6186 | basic | 759 785 | 0.21 |
| 11 | status LEDs Q1–Q6, S1–S4, 3V3 (green) | KT-0805G | 0805 | C2297 | basic | 1.08 M | 0.02 |
| 1 | power LED (red, V_IN) | NCD0805R1 | 0805 | C84256 | basic | 4.9 M | 0.01 |
| 22 | 10 kΩ pull-downs/-ups, pH bias divider, pH filters, LED | 0805 1 % | 0805 | C17414 | basic | 60 M | 0.004 |
| 12 | 1 kΩ input series, AIN3 filter, Q/3V3 LEDs | 0805 1 % | 0805 | C17513 | basic | 31 M | 0.004 |
| 5 | 4.7 kΩ 1-Wire pull-up, SSR LEDs | 0805 1 % | 0805 | C17673 | basic | 5.2 M | 0.005 |
| 6 | gate resistors 100 Ω | 0805 1 % | 0805 | C17408 | basic | 9.5 M | 0.004 |
| 7 | 100 nF 50 V decoupling, boot, filters | X7R | 0805 | C49678 | basic | 17 M | 0.02 |
| 2 | buck input 4.7 µF 50 V | X7R | 1206 | C29823 | basic | 619 131 | 0.17 |
| 2 | buck output 47 µF 10 V | X5R | 1206 | C96123 | basic | 316 224 | 0.26 |
| 4 | 10 µF 25 V: LDO in/out, pH low-pass AIN0/AIN2 | X5R | 0805 | C15850 | basic | 5.2 M | 0.08 |
| 1 | buck RT 150 kΩ (644 kHz) | 0805 1 % | 0805 | C17470 | basic | – | 0.004 |
| 2 | buck FB top 12 kΩ, COMP 12 kΩ | 0805 1 % | 0805 | C17444 | basic | – | 0.004 |
| 1 | buck FB bottom 2.2 kΩ (5.16 V) | 0805 1 % | 0805 | C17520 | basic | – | 0.004 |
| 1 | pH input series 220 kΩ | 0805 1 % | 0805 | C17556 | basic | – | 0.004 |
| 1 | TL431 feed 470 Ω | 0805 1 % | 0805 | C17710 | basic | – | 0.004 |
| 1 | buck COMP 10 nF | X7R | 0805 | C1710 | basic | – | 0.01 |
| 1 | buck COMP 47 pF | C0G | 0805 | C14857 | basic | – | 0.01 |

SMD parts ≈ **$9 per board**. Extended parts: **12 unique** → ≈ $36 loading fees per order.

## THT and hand-soldered, Reichelt

| Qty | Function | Reichelt Art.-Nr. | Description | €/pc |
|---:|---|---|---|---:|
| 11 | V_IN, Q1–Q6, S1–S4 terminals | AKL 101-02 | terminal 2-pole, 5.08 mm, 13 A | 0.26 |
| 9 | IN1–4, 1-Wire ×3, pH module, AIN3 terminals | AKL 101-03 | terminal 3-pole, 5.08 mm | 0.39 |
| 1 | input fuse, holder incl. 10 A fuse | LITT 0154010.DR | Littelfuse OMNI-BLOK SMD holder + 10 A Nano2 fuse, 125 V (large SMD, hand-soldered) | 2.99 |
| 1 | bulk capacitor 470 µF 50 V | RAD FR 470/50 | Panasonic FR, low ESR, 105 °C | 0.60 |
| 1 | pH input filter across the probe, low leakage | STYROFLEX 2,2N | polystyrene 2.2 nF 2 % 160 V, axial Ø5.8×11.5 mm (47 pF..6.8 nF available) | 0.75 |
| 1 | pH probe connector | UG 1094PL | BNC PCB jack, straight, 50 Ω | 1.99 |
| 1 | Pi connector, variant Zero (plug-on) | MPE 094-2-040 | female header 2×20, 2.54 mm | 1.10 |
| (1) | Pi connector, variant Pi 3/4 (ribbon) | WSL 40G | box header 40-pole, straight | 0.23 |
| 1 | UART, I²C ×2, display, ULN spare, JP1–3 (38 pins) | ECON SL40G1 | pin header 1×40, 2.54 mm (cut to length) | 0.75 |
| 3 | JP1 5V→Pi, JP2 SSR supply, JP3 backlight | JUMPER 2,54 SW | shunt, 2.54 mm | 0.02 |
| 4 | Pi Zero standoffs | – | M2.5 × 11 mm, any Pi mounting kit | – |

THT parts ≈ **€13.50 per board**. Reichelt shipping within Germany: €5.95 (shown on
reichelt.de at the time of the check).

LCSC fallback: the OMNI-BLOK holder 0154010.DR is also stocked at LCSC (C206921), so JLC
could place it instead of hand-soldering.

## Rejected during the check

- 74HCT541 (SOIC): no stock at LCSC (C2675527, C3753686) → 74HCT244D, same function,
  different pinout.
- TI ULN2803ADWR (C9683): $6.27 → onsemi ULN2803ADWMRG.
- TLC2272: needs ≥ 4.4 V supply, output could exceed the 3.3 V ADS1115 input range →
  TLV9062 on 3.3 V.
- Generic SOT-23 TL431 clones (C181103 etc.): cheaper, but SOT-23 pinouts differ between makers →
  TI TL431BCDBZR, pinout checked against TI datasheet SLVS543S.
- LMC6482 / LMP7702: little or no stock, $2–7.
- 5×20 mm PCB fuse holders at Reichelt (MTA 501100, ESKA 503400, Stelvio): rated 6.3 A only.
- MTA 370000 blade-fuse holder: 20 A, but panel snap-in with spade tabs, not PCB.
