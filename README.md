# aquaPCB

Raspberry Pi base board for [aquaPi](https://github.com/schwabix-1311/aquaPI), the
modular aquarium controller. One board with a 12 V supply input, power outputs for
LED lamps and fans, control outputs for external SSRs/relays, digital inputs, 1-Wire,
an on-board ADS1115 with pH front end, and headers for a small display and I²C add-ons.

aquaPi needs no special support: every channel is a plain GPIO, hardware PWM, 1-Wire or
I²C port that aquaPi discovers by itself and offers in its Wiring editor.

> Status: **schematic draft (v1)**, ERC clean. No layout yet.
> Not a beginner kit: SMD parts are assembled by the PCB fab (JLCPCB economic PCBA);
> only through-hole connectors are hand-soldered.

## Key figures

```
Supply          12 V DC, 8 A max total (parts rated >= 40 V; 24 V operation planned, not yet validated)
Pi              Zero 2 W plugged on face-up; Pi 3/4 via 40-pin ribbon (Pi 5: own PSU)
Power outputs   6x low-side MOSFET, 5 A each, 2 with hardware PWM (Q1..Q6)
SSR outputs     4x open-collector sink, ULN2803A, for SSR / relay modules (S1..S4)
Inputs          4x protected 3.3 V digital inputs (IN1..IN4)
1-Wire          GPIO4, 1 sensor terminal (bus: several sensors per terminal), parasitic power supported
Analog          ADS1115, 16 bit, 4 channels single-ended: on-board pH amplifier (BNC),
                module input 0..5 V (e.g. PH-4502C, ORP board), general 0..3.3 V input
Expansion       I2C header (OLED, PCA9685, ...); optional: 2nd I2C header, SPI display header
Board           100 x 100 mm, 2 layers, 1 oz Cu, 4x M3
```

No mains voltage on this board. Mains loads (heater, pumps) are switched by external
SSRs or relay modules driven from S1..S4.

## Block diagram

```
 12 V in ──[fuse 8A]───[rev.pol. P-FET]──┬──[TVS]── V_IN rail ─────────────┐
                                         │                                  │
                                    [buck 5V/3A]──┬── jumper "5V→Pi" ──> Pi 5V
                                                  │                         │
                                             [LDO 3V3]── ADC, sensors, display
                                                                            │
   Pi GPIO ──> [74HCT244, 5V] ──> gate ──> Q1..Q6 MOSFET ──> terminals (+V_IN / OUT)
   Pi GPIO ──> [ULN2803A] ─────────────> S1..S4 ──> terminals (+5V|+V_IN / OUT)
   IN1..IN4 terminals ──[1k + clamp, 10k pull-up]──> Pi GPIO
   1-Wire terminals ──[4k7 pull-up, ESD]──> GPIO4
   I2C (GPIO2/3) ──> 2x I2C header
                └──> ADS1115 ──< pH buffer ──< BNC ;  module input (0..5 V) ;  AIN3 terminal
   SPI0 + DC/RST ──> display header
```

## Pin map (BCM numbering)

Outputs sit on GPIO 9 and above only: those pins default to pull-down at boot, so no load
switches on while the Pi boots. GPIO 0..8 default to pull-up and are used for inputs and
buses only.

```
GPIO  function            GPIO  function
 0    reserved (ID EEPROM) 14    unused (not connected)
 1    reserved (ID EEPROM) 15    unused (not connected)
 2    I2C SDA              16    Q5  power out
 3    I2C SCL              17    S1  SSR out
 4    1-Wire               18    Q1  power out, PWM0 (light)
 5    IN1                  19    Q4  power out, PWM1 (fan)
 6    IN2                  20    IN3
 7    SPI CE1              21    IN4
 8    SPI CE0              22    S2  SSR out
 9    SPI MISO             23    S3  SSR out
10    SPI MOSI             24    display RST
11    SPI SCLK             25    display DC
12    Q2  power out        26    Q6  power out
13    Q3  power out        27    S4  SSR out
```

All GPIOs except 14/15 are in use (14/15 stay free: no UART console, customers rarely
have a USB-serial adapter). Further expansion goes over I²C (e.g. PCA9685 PWM breakout,
MCP23017 IO expander).

Raspberry Pi OS settings: `dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2`,
`dtoverlay=w1-gpio,gpiopin=4`, `dtparam=i2c_arm=on`, `dtparam=spi=on` (display only).

## Circuit blocks

### Power input
- 2-pin push-in terminal, 8 A fuse in a Littelfuse OMNI-BLOK holder (replaceable Nano2
  fuse; common 5x20 mm PCB holders are only rated 6.3 A). 8 A is the board's total current
  limit, set by the terminals' rating (8 A IEC per contact).
- Reverse-polarity protection: P-channel MOSFET in the positive line, gate via resistor
  to GND with a 15 V zener clamp (needed only above ~18 V, kept for 24 V readiness).
- TVS SMBJ33A across V_IN, bulk electrolytic 470 µF / 50 V.

### 5 V and 3.3 V
- Buck converter TPS54360B (60 V input, 3.5 A), non-synchronous with SS54 catch diode and
  10 µH / 4.8 A inductor, set to 5 V / 3 A. 3 A covers Pi Zero 2 W through Pi 4.
  Based on TI's 5 V design example (datasheet SNVSB93, fig. 32), values moved to JLC basic
  parts: RT 150 k (644 kHz), feedback 12 k / 2.2 k (5.16 V), compensation 12 k + 10 nF,
  47 pF, 2x 47 µF output. EN left open (internal 4.3 V UVLO).
- Jumper "5V→Pi" feeds the Pi through its GPIO header 5 V pins. Leave it **open** when the
  Pi has its own USB power supply (always for Pi 5).
- 3.3 V LDO (AMS1117-3.3) from 5 V for ADC, 1-Wire, inputs and display, so peripherals
  don't load the Pi's own regulator.

### Power outputs Q1..Q6
Identical low-side switches, terminal pair +V_IN / OUT per channel, 5 A each (8 A in total
for the whole board).
- 74HCT244 on 5 V as gate driver: accepts 3.3 V logic (V_IH 2.0 V), drives gates at 5 V,
  and keeps the Pi's GPIOs isolated from the power stage.
- 100 Ω gate resistor, 10 kΩ gate pull-down (output stays off when the Pi is absent or
  booting), logic-level N-MOSFET, 40 V, DPAK (e.g. AOD4184A, ~9 mΩ at V_GS 4.5 V).
- SS54 Schottky freewheel diode OUT → +V_IN for fans, pumps, solenoids.
- Status LED per channel.
- Q1/Q4 on hardware PWM (GPIO18/19) for dimming LED lamps and 2-wire fans. 4-wire PC-fan
  PWM input is not supported. The GPIO order Q1 18, Q2 12, Q3 13, Q4 19 follows the Pi
  header, so the GPIO → 74HCT244 → gate lines route without crossings.

Why not drive the MOSFET directly from the GPIO (e.g. IRLB8721)? It works with typical
parts, but R_DS(on) is only specified from V_GS 4.5 V while V_th may reach 2.35 V, so a
worst-case part runs half-on at 3.3 V and heats up; the gate floats during boot; a
gate-drain short puts the load supply onto the Pi; and 30 V V_DS leaves no margin for 24 V.
The buffer costs about €0.60 per board.

### SSR outputs S1..S4
- ULN2803A (SOIC-18), open-collector sink with built-in flyback diodes.
- Terminal pair per channel: supply (+5 V or +V_IN, selected by jumper) and OUT.
- Drives SSRs with 3..32 V DC control input or relay modules.
- The four unused ULN2803A channels stay unconnected (inputs open; the internal resistors keep
  them off).

### Digital inputs IN1..IN4
3-pin terminal 3V3 / IN / GND for float switches, level sensors, push buttons.
1 kΩ series resistor, 10 kΩ pull-up to 3.3 V, BAT54S clamp to 3.3 V and GND.

### 1-Wire
GPIO4 with 4.7 kΩ pull-up to 3.3 V; one 3-pin terminal (GND / DQ / 3V3), so both
3-wire and parasitic-powered (GND / DQ only) DS18B20 sensors work. ESD protection diode.

### ADS1115 and pH
- ADS1115 on 3.3 V directly on the Pi's I²C bus (matching logic levels, no level shifter),
  address 0x48 by default, 0x49 by solder jumper.
- All inputs are read **single-ended**, as aquaPi's ADS1115 driver does today.
- Requirements behind this design: good probe lifetime; ~0.1 pH stability is enough, since
  aquaPi's ScaleAux calibration removes offset and slope. Derived from the hand-built
  controller (PH-4502C amplifier with 10 MΩ / 4.7 nF styroflex input filter, probe life > 2
  years).
- AIN0: on-board pH amplifier, like the PH-4502C but with a low-leakage input. Right-angle BNC
  jack at the left board edge (see Mechanical),
  10 MΩ in series, styroflex capacitor to the probe reference, TLV9062 CMOS buffer on 3.3 V
  (0.5 pA input bias). The probe reference (BNC shell) sits at PH_REF = 1.65 V (3.3 V / 2,
  buffered by the second op-amp half), so AIN0 reads 1.65 V ± 59 mV/pH.
- Probe load: only the op-amp input (0.5 pA typical, ≈ 10¹² Ω or more) and the leakage of
  the polystyrene capacitor. No ceramic capacitor or clamp on the high-impedance input:
  MLCC leakage (only specified to ~10 GΩ) would dominate.
- 50 Hz suppression (filter pumps), two stages: 10 MΩ / 6.8 nF styroflex at the input
  (68 ms; together with the electrode's 100 MΩ..1 GΩ: 0.7..7 s), then 10 k / 10 µF after the
  buffer (1.6 Hz, about −30 dB at 50 Hz). Styroflex values 47 pF..6.8 nF are available.
- Ground-loop insurance: 1 MΩ between the PH_REF buffer and the BNC shell. Nothing in the
  tank is grounded today; if that ever changes (a grounded sensor), the DC current through
  the reference electrode stays below ~1.7 µA instead of mA. The reading goes visibly wrong,
  the probe survives. In normal operation only pA flow through it. (A fully isolated pH
  stage was designed and dropped: ~€3 per board for a case that doesn't occur.)
- Layout of the high-impedance node (PH_BNC / PH_IN: BNC centre, 10 MΩ, styroflex lead,
  op-amp pin 3), replacing the point-to-point "air wiring" of the hand-built version:
  - guard ring on both layers around all of it, on net PH_BUF (the buffer output follows
    the input within the op-amp offset, so input-to-guard leakage is ~1.6 mV / R_leak:
    femtoamps on a clean board); stray leakage from other nets ends in the guard;
  - non-plated milled slots between the BNC centre pad and the shell pads, and around the
    input pads, to cut surface leakage paths;
  - shortest possible node, solder mask on, no silkscreen inside the guard, flux washed off
    (and the board dried) after hand-soldering; optional conformal coating of the pH corner.
- AIN1: PH_REF, as a monitor and for a later AIN0−AIN1 differential reading if the driver
  gets support for it.
- AIN2: module input for 5 V amplifier boards (e.g. the PH-4502C from probe kits, ORP or
  conductivity boards), terminal +5 V / SIG / GND. Divider 10 k / 20 k, fitted by default,
  maps 0..5 V to 0..3.33 V (leave the 20 k off for 1:1 up to 3.3 V); with 10 µF a 2.4 Hz
  low-pass; clamped to 0..3.3 V.
- AIN3: terminal 3V3 / AIN3 / GND for other 0..3.3 V sensors, 1 k / 100 nF, clamped.

### Display and I²C expansion
- 2x 4-pin I²C header, pin order GND / VCC / SCL / SDA (common SSD1306 OLED modules).
- 8-pin SPI header for ST7735 / ILI9341 TFTs: CE0, CE1, MOSI, MISO, SCLK, DC, RST,
  backlight to 3.3 V via jumper.

## Schematic

KiCad 10 project in [kicad/](kicad): root sheet `aquaPCB.kicad_sch` with six sub-sheets
(power, Pi connector, power outputs, SSR outputs, inputs/1-Wire/display, ADC/pH) and a
project footprint library `aquaPCB.pretty` (Littelfuse OMNI-BLOK fuse holder).

The first draft was generated by `tools/gen_schematic.py` from the pin map and BOM:
every pin ends in a short stub with a net label or power symbol, so the drawing is a
readable netlist rather than a hand-routed schematic. Once the schematic is edited in
eeschema, the `.kicad_sch` files are the source of truth; the generator is **retired**
and refuses to overwrite existing schematics (`--force` only for a fresh draft).

```
python3 tools/gen_schematic.py                        # (re)generate the draft
for f in kicad/*.kicad_sch; do kicad-cli sch upgrade "$f"; done
kicad-cli sch erc --severity-all kicad/aquaPCB.kicad_sch
```

Placeholder footprint to check at layout time: 470 µF capacitor diameter (D10 assumed).
The BNC footprint (`aquaPCB.pretty`) is made from the LCSC/EasyEDA pad data and the maker drawing.

## Build options

Optional parts carry KiCad's **DNP** (Do Not Populate) flag: their footprints stay on the board,
but they are left out of the BOM and the pick-and-place file. They are all through-hole pin
headers, so they can be soldered in later if needed.

```
J23   second I2C header
J24   SPI display header
JP3   display backlight jumper
```

Export for JLCPCB without them: `kicad-cli sch export bom --exclude-dnp ...` and
`kicad-cli pcb export pos --exclude-dnp ...`. Further options (e.g. on-board pH amplifier vs.
external amplifier board on AIN2, Pi Zero socket vs. Pi 3/4 box header) can become KiCad 10
design variants once they are needed.

## Mechanical

- 100 x 100 mm, 4x M3 mounting holes.
- One 2x20 footprint with normal (not mirrored) pin numbering, fitted with either
  - a 2x20 female socket: Pi Zero 2 W sits **face-up** on it, with its 2x20 pin header
    soldered on the Zero's underside (pins pointing down; use a Zero 2 W without
    pre-soldered header, not the WH). The header side is held by the plug connection, the
    opposite side by two M2.5 x 11 mm standoffs in the Zero's outer mounting holes (H5/H6,
    58 mm apart). No holes next to the header, so the larger box header fits as well.
    Face-up keeps SoC cooling, SD card and LED accessible; or
  - a 40-pin box header: Pi 3/4 connect through a standard IDC ribbon cable.
  A face-down Zero would need a mirrored footprint and could not share it with the ribbon.
- pH BNC: right-angle jack HanElectricity BNC-Q9-50KWE at the left board edge. Its body front face is
  flush with the edge; nut and barrel (d 9.5 mm, thread 1/2-28UNEF) protrude 21.4 mm, enclosure cutout
  d 12.9 mm. The whole shell (pin and both legs) is the probe reference PH_SHELL, not GND: in a metal
  enclosure it must be insulated from the wall (plastic enclosure or insulating bushing). Its insulation
  resistance is only specified at ≥ 5 GΩ (POM insulator); with a 1 GΩ electrode that is a worst-case
  gain error of ~17 % (typical parts are far better and ScaleAux calibrates the slope), but humidity can
  change it - a PTFE-insulated BNC would be the upgrade if readings drift.
- All terminals are push-in spring terminals (Kangnex WJ250B, 3.5 mm pitch, staggered pins) on the
  board edges, wire entry facing outwards: wires up to 1.5 mm² / 16 AWG, strip 9–10 mm; solid wire
  or ferrules push in, the button releases.
  The footprints have a hole in both staggered pin rows for every pole, so the MAX MX250-B
  (LCSC C7470116 / C7470117) fits as a drop-in alternative; when routing, join both holes of
  each pole.
- All terminals on the board edges; power path along one edge; the analog/pH corner away
  from the switching outputs.

## Current budget and copper

```
Path                      current   trace width, 1 oz, 10 °C rise (IPC-2221)
V_IN input + GND return    8 A      5.3 mm  -> copper pour / bottom GND plane
one power output Q        5 A       2.8 mm
buck input                ~1.5 A    0.7 mm
5 V to Pi                 3 A       1.4 mm
signals                   < 0.1 A   0.25 mm
```

1 oz copper with pours is sufficient; 2 oz would halve the widths but costs noticeably more.

## Cost estimate

Based on the checked part prices in [BOM.md](BOM.md) (2026-09-29). Fab fees and shipping
are estimates.

```
per board                                     batch 5    batch 10
  PCB 100x100, 2 layers                         ~ €2       ~ €1.5
  SMD parts (LCSC, checked)                     ~ €8       ~ €7.5
  PCBA setup + 11 extended-part fees, share     ~ €7.5     ~ €3.75
  THT parts (LCSC: terminals, fuse, BNC;
            Reichelt: rest)                     ~ €8       ~ €8
  shipping JLC + Reichelt, share                ~ €5       ~ €2.5
  EU import VAT 19 % + €3 duty/category (JLC)   ~ €4       ~ €3.5
  -----------------------------------------------------------------
                                                ~ €35      ~ €27
```

Target limit **≤ €40 per board** at batch 5 is met with margin (about €35) after dropping the UART
header and two 1-Wire terminals, moving the BNC to LCSC and switching to LCSC push-in terminals.
The on-board pH amplifier costs about €1.50 (BNC, TLV9062, styroflex). Levers: order 10 boards
(~€27 each), or leave the on-board pH amplifier unpopulated when an external amplifier board is
used on AIN2.

## Not on v1

- **PCA9685 PWM expander**: plug a breakout into an I²C header once aquaPi has a
  driver for it (see aquaPi's ROADMAP.md).
- **Robo-Tank / Leviathan compatibility and 0..10 V lamp dimming**: possible later add-on
  board on the I²C header (PCA9685 + op-amp outputs 0..5 V / 0..10 V + RJ45 jacks),
  estimated €12..15. Needs the Robo-Tank RJ45 pinouts from their manuals first.
- **Mains switching**: stays in external SSRs / relay modules by design.

## Roadmap

1. Specification (this file), BOM with LCSC / Reichelt part numbers ([BOM.md](BOM.md)) – done
2. Schematic in KiCad, ERC clean – draft done, needs review
3. Layout, DRC clean
4. Gerbers, JLC BOM/CPL, order 5 prototypes
5. Bring-up at 12 V: rails without Pi, then with Pi Zero 2 W, boot with loads attached
   (no output may toggle), all channels from the aquaPi dashboard, 5 A thermal test
6. Validate 24 V operation

## Licence

Copyright Markus Kuhn 2026.

This source describes Open Hardware and is licensed under the CERN-OHL-S v2
(`SPDX-License-Identifier: CERN-OHL-S-2.0`), see [LICENSE](LICENSE).

You may redistribute and modify this source and make products using it under the terms
of the CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt). This source is distributed
WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY
QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable
conditions.

Source location: to be added once the GitHub repository exists. As per CERN-OHL-S v2
section 4, should you produce hardware based on this source, you must where practicable
maintain the Source Location visible on the external case or other product you make.
