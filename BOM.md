# aquaPCB – Bill of Materials (v2)

Prices and stock for LCSC/JLCPCB parts checked 2026-10-23 (JLCPCB parts API); Reichelt prices from
the v1 check (2026-09-29) unless marked otherwise. Quantities per board, taken from the v2 schematic
(`kicad-cli sch export bom`). The ADS1115 address solder jumper JP4 is a PCB feature, no part.
The v1 BOM is in the git history (tag `v1.0.1`, branch `release/v1`).

Sourcing rule:
- **SMD → JLCPCB assembly.** JLC can only place parts from its own LCSC stock, so all SMD
  parts carry LCSC numbers (also in the schematic's `LCSC` field) and arrive already soldered.
- **THT → LCSC with the board order** (JLC can fit them or ship them loose), except the few
  parts LCSC doesn't stock well, which come from **Reichelt**.

JLC "extended" parts cost a one-time loading fee per unique part and order (currently
about $3 each); "basic" parts don't. Prices below: LCSC USD at qty 1–49, excl. VAT;
Reichelt EUR incl. 19 % VAT.

## SMD, assembled by JLCPCB

| Qty | Function | Part | Package | LCSC | Lib | Stock | $/pc |
|---:|---|---|---|---|---|---:|---:|
| 1 | 5 V buck, 60 V, 3.5 A (non-synchronous) | TI TPS54360BDDAR | SOIC-8-EP | C524806 | ext | 60 810 | 0.76 |
| 1 | buck inductor 10 µH, 4.8 A, 20 mΩ | TDK SLF12565T-100M4R8-PF | 12.5×12.5 mm | C138303 | ext | 1 538 | 0.52 |
| 7 | freewheel Q1–Q6 + buck catch diode, 40 V 5 A | SS54 | SMA | C22452 | **basic** | 2 M | 0.044 |
| 6 | power switch Q1–Q6, 40 V, 7 mΩ@10 V | AOS AOD4184A | TO-252 | C99124 | ext | 15 834 | 0.35 |
| 1 | reverse-polarity P-FET, −40 V, 9.9 mΩ | Diodes Inc. DMP4010SK3Q-13 | TO-252 | C5359358 | ext | 10 739 | 0.63 |
| 1 | P-FET gate clamp 15 V | BZT52C15 | SOD-123 | C173427 | ext | 157 271 | 0.016 |
| 1 | input TVS 33 V, 600 W | SMBJ33A | SMB | C78419 | ext | 12 780 | 0.074 |
| 1 | gate buffer Q1–Q6, 3.3 V → 5 V | Nexperia 74HCT244D,653 | SOIC-20 | C5978 | ext | 14 023 | 0.39 |
| 2 | PWM expander 16 ch, I²C (#1 DC/LED + Q2/Q3/Q5/Q6, #2 power bars) | NXP PCA9685PW,118 | TSSOP-28 | C2678753 | ext | 5 569 | 3.33 |
| 2 | 0-5 V buffers for the 14 DC/LED port channels | Nexperia 74HCT244PW,118 | TSSOP-20 | C131088 | ext | 24 143 | 0.25 |
| 8 | series resistors, 14 DC/LED + 16 power bar lines | 4×100 Ω array | 0603×4 | C25506 | ext | 162 715 | 0.008 |
| 1 | ADC 16 bit, 4 ch, I²C | TI ADS1115IDGSR | VSSOP-10 | C37593 | ext | 4 397 | 1.51 |
| 11 | clamps: 6 sensor inputs, 4 analog sockets, 1-Wire | BAT54S | SOT-23 | C12765 | ext | 242 564 | 0.014 |
| 2 | 3.3 V LDO 1 A (+3V3, +3V3_EXT for the feeder) | AMS1117-3.3 | SOT-223 | C6186 | basic | 1.5 M | 0.20 |
| 1 | PTC +5V_EXT (sensors, analog, 1-Wire, feeder via +3V3_EXT), hold 1.1 A, trip 2.2 A | nSMD110 | 1206 | C71465 | ext | 10 134 | 0.044 |
| 7 | status LEDs Q1–Q6, 3V3 (green) | KT-0805G | 0805 | C2297 | basic | 2.4 M | 0.016 |
| 1 | power LED (red, V_IN) | NCD0805R1 | 0805 | C84256 | basic | 3.1 M | 0.013 |
| 18 | 10 kΩ pull-downs/-ups, dividers, filters | 0805 1 % | 0805 | C17414 | basic | 54.4 M | 0.003 |
| 2 | 10 kΩ float input pull-downs | 0603 1 % | 0603 | C25804 | basic | 36.2 M | 0.002 |
| 13 | 1 kΩ sensor input series, LED resistors, filters | 0805 1 % | 0805 | C17513 | basic | 43.2 M | 0.004 |
| 4 | 20 kΩ analog dividers (0-5 V → 0-3.33 V) | 0805 1 % | 0805 | C4328 | basic | 2 M | 0.004 |
| 1 | 4.7 kΩ 1-Wire pull-up | 0805 1 % | 0805 | C17673 | basic | 4.9 M | 0.005 |
| 6 | gate resistors 100 Ω | 0805 1 % | 0805 | C17408 | basic | 8.2 M | 0.004 |
| 8 | 100 nF 50 V decoupling, boot, filters | X7R | 0805 | C49678 | basic | 22.7 M | 0.021 |
| 2 | buck input 4.7 µF 50 V | X7R | 1206 | C29823 | basic | 759 194 | 0.08 |
| 2 | buck output 47 µF 10 V | X5R | 1206 | C96123 | basic | 361 868 | 0.16 |
| 8 | 10 µF 25 V: LDO in/out, analog low-pass | X5R | 0805 | C15850 | basic | 9.2 M | 0.043 |
| 1 | buck RT 150 kΩ (644 kHz) | 0805 1 % | 0805 | C17470 | basic | 813 965 | 0.005 |
| 2 | buck FB top 12 kΩ, COMP 12 kΩ | 0805 1 % | 0805 | C17444 | basic | 699 960 | 0.003 |
| 1 | buck FB bottom 2.2 kΩ (5.16 V) | 0805 1 % | 0805 | C17520 | basic | 3.6 M | 0.005 |
| 1 | buck COMP 10 nF | X7R | 0805 | C1710 | basic | 1.4 M | 0.009 |
| 1 | buck COMP 47 pF | C0G | 0805 | C14857 | basic | 103 426 | 0.008 |

SMD parts ≈ **$15.41 per board**; the two PCA9685 alone are $6.67. Extended parts:
**13 unique** → ≈ $39 loading fees per order.

PCA9685PW stock is the tightest of the assembled parts (5 569 at LCSC); the automotive
variant PCA9685PW/Q900,118 (C92206) is a drop-in fallback at a slightly higher price.

## THT and hand-soldered, LCSC

| Qty | Function | Part | LCSC | Stock | $/pc |
|---:|---|---|---|---:|---:|
| 7 | V_IN, Q1–Q6 terminals: push-in spring, 2-pole, 3.5 mm, 8 A | Ningbo Kangnex WJ250B-3.5-02P-11-00A | C8454 | 22 733 | 0.12 |
| 3 | DC, LED, sensor ports: box header 2×4, 2.54 mm, keyed | DC3-2.54-8PAS | C5156664 | 536 | 0.068 |
| 2 | power bar ports: box header 2×5, 2.54 mm, keyed | DC3-2.54-10PAS | C2977596 | 57 | 0.083 |
| 1 | input fuse, OMNI-BLOK holder incl. 10 A Nano2 fuse (large SMD) | Littelfuse 0154010.DR | C206921 | 3 408 | 1.76 |
| (2) | alternative 2×5 box header, grey, more stock | DC3-2.54-10PAS-Grey | C49261191 | 236 | 0.12 |

LCSC through-hole parts ≈ **$2.94 per board**. The 2×5 box header has low stock at LCSC;
Reichelt's WSL 10G (below) fits the same footprint. Terminal footprints and wiring notes as in v1:
`aquaPCB:TerminalBlock_Kangnex_WJ250B-3.5-02P_P3.50mm_Staggered` has a hole in both pin rows for every
pole, so Kangnex and MAX MX250-B terminals fit; rating 8 A (IEC) / 7 A (UL) per contact, which sets the
board's total current.

## THT, Reichelt

| Qty | Function | Reichelt Art.-Nr. | Description | €/pc |
|---:|---|---|---|---:|
| 1 | bulk capacitor 470 µF 50 V (C1) | RAD FR 470/50 | Panasonic FR, low ESR, 105 °C | 0.60 |
| 1 | Pi connector, variant Zero (plug-on) | MPE 094-2-040 | female header 2×20, 2.54 mm | 1.10 |
| (1) | Pi connector, variant Pi 3/4 (ribbon) | WSL 40G | box header 40-pole, straight | 0.23 |
| 1 | 1-Wire, 4 analog sockets, floats, I²C 1, JP1 (25 pins; +16 for the optional headers below) | ECON SL40G1 | pin header 1×40, 2.54 mm (cut to length) | 0.75 |
| 3 | JP1 5V→Pi (Pi Zero 2 W / Pi 3; open for a Pi 4/5 with its own supply); bridges for unused float inputs J30/J31 (+1 for optional JP3) | JUMPER 2,54 SW | shunt, 2.54 mm | 0.02 |
| (2) | alternative to the LCSC 2×5 box headers | WSL 10G | box header 10-pole, straight (price checked 2026-10-23) | 0.15 |
| 2 | Pi Zero standoffs (H5/H6, Zero variant only) | – | M2.5 × 11 mm, any Pi mounting kit | – |

Optional, marked DNP (not in the exported BOM / placement file; pads are on the board):
J23 second I²C header (4), J24 display header (10), JP3 backlight jumper (2 + shunt) – a second
pin header strip covers them.

Reichelt parts ≈ **€2.50 per board** (Zero variant). Reichelt has no 2×4 box header, so the DC, LED
and sensor port headers come from LCSC.

## Changes from v1

- Added: 2× PCA9685PW, 2× 74HCT244PW, 8× 4×100 Ω arrays, second AMS1117-3.3 (+3V3_EXT for the
  feeder), PTC for +5V_EXT, 4 more BAT54S, box headers 2×4 (3) and 2×5 (2), pin headers for 1-Wire,
  analog sockets and floats.
- Dropped: ULN2803A (S1–S4), TLV9062 and the on-board pH front end (BNC, styroflex 6.8 nF, 10 MΩ,
  1 MΩ – now on the pH/ORP add-ons), the four S1–S4 LEDs, the 3-pole terminals (IN1–IN4, 1-Wire,
  module input, AIN3), SSR supply jumper JP2.
- Count changes: 2-pole terminals 11 → 7, green LEDs 11 → 7, 10 µF 4 → 8, 100 nF 7 → 8,
  4.7 kΩ 5 → 1.

## Rejected during the check

- Plain 2×4 / 2×5 pin headers (e.g. A2541WV-2x4P C225519, 254PZ-2x4P-V C53055679): cheaper and better
  stocked, but not keyed – the ports use keyed box headers so a module cable can't be plugged in
  reversed.
- Plain 2×5 pin header with one pin pulled and a coding insert in the cable socket (instead of the
  box headers): blocks a reversed plug, but not a socket pushed on offset by one column or row, and
  the DC/LED/sensor ports use all 8 pins of their 2×4, so they would grow to 2×5 (re-layout) and need
  extra coding parts on the cable side. Fallback if the 2×4 box header ever runs out: a 2×5 box
  header (e.g. Reichelt WSL 10G) on those ports with pins 9/10 unconnected – same pinout, keyed, one
  part type for all five ports; costs the same footprint change and re-layout.
- PCA9685PW,112 (C2688894): no stock; PCA9685BS (HVQFN-28): different footprint, low stock.
- PTC nSMD050 (0.5 A hold, C69688): replaced 2026-10-25 by nSMD110 (1.1 A hold) - the feeder (up to
  500 mA) shares the PTC with the sensors, analog sockets and 1-Wire. 6 V rating is enough on the 5 V
  rail; SMD1206P110TF (C20801) and 1206L110THYR (C126818) are drop-in alternatives.
- AOD4185 (C400894, 15 mΩ) as reverse-polarity FET: replaced 2026-10-25 by DMP4010SK3Q-13 (9.9 mΩ, same DPAK
  pinout G-D-S) to cut its loss by a third; SUD50P04-08-GE3 (C506582, 8.1 mΩ) would save another ~5 °C but
  costs $1.45 and has less stock.
- 8 A fuse (0154008.DR, C206919): replaced by the 10 A insert of the same holder - Littelfuse recommends at
  most ~75 % of the rating as continuous current (8 A -> 6 A); the 8 A continuous limit is set by the terminals.
- From the v1 check, still valid: 74HCT541 (no stock) → 74HCT244; 5×20 mm PCB fuse holders (6.3 A
  only); screw terminals and lever terminals (price) → push-in spring terminals.
