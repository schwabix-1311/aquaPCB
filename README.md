# aquaPCB

Raspberry Pi base board for [aquaPi](https://github.com/schwabix-1311/aquaPI), the
modular aquarium controller. One board with a 12 V supply input, power outputs for
LED lamps and fans, control outputs for external SSRs/relays, digital inputs, 1-Wire,
an on-board ADS1115 with pH front end, and headers for a small display and I²C add-ons.

aquaPi needs no special support: every channel is a plain GPIO, hardware PWM, 1-Wire or
I²C port that aquaPi discovers by itself and offers in its Wiring editor.

> Status: **v1 layout complete** (tag `v1.0.1`, branch `release/v1`): schematic ERC clean,
> board fully routed, DRC clean; no prototypes built yet. Fabrication is on hold while
> the [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit) is checked for budget and
> sense - if v2 is dropped, v1 continues with fab outputs and a 1:1 print check.
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

Footprint to confirm on the 1:1 print: 470 µF capacitor C1 diameter (D10 assumed).
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
  driver for it (see aquaPi's ROADMAP.md). v2 puts two PCA9685s on the board, see
  [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit).
- **Robo-Tank compatibility and 0..10 V lamp dimming**: planned for v2, see
  [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit).
- **Mains switching**: stays in external SSRs / relay modules by design.

## Recommended improvements (v2 candidates)

From the comparison with Robo-Tank and Leviathan ([COMPARISON.md](COMPARISON.md)) and
the most frequent complaint about Pi aquarium controllers - hard wiring and port
selection:

- **Silkscreen labels = aquaPi board profile.** aquaPi plans board profiles that show
  connector labels instead of GPIO numbers in its port dropdown (aquaPi ROADMAP,
  "Board support"). aquaPCB can be the first profile because its pin map is already
  documented; keep the silk labels (Q1..Q6, S1..S4, IN1..IN4, ...) and the profile names
  identical. (v2 replaces S1..S4 with power bar outputs, see [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit).)
- **ID EEPROM on GPIO 0/1.** The pins are already reserved. With an EEPROM fitted, aquaPi
  could recognise the board and pick its profile without asking.
- **Pluggable wiring.** RJ45 for module cables like Robo-Tank v3, so a controller can be
  swapped without rewiring - see [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit).
- **0-10 V / PCA9685**: PCA9685s on board, 0-10 V as an optional add-on module - see
  [v2 plan](#v2-plan-robo-tank-v3-compatible-head-unit).
- **Isolated pH as a build option.** Not needed for the proven hand-built setup, but a
  point buyers compare (Robo-Tank sells one for $54.95) - decided: pH/ORP amplifiers move to
  add-on modules, one of them isolated, see
  [pH / ORP amplifiers: add-on modules](#ph--orp-amplifiers-add-on-modules).
- **Ready-to-use offer.** Assembled boards and a wiring guide with photos make more
  difference for beginners than extra channels.

## v2 plan: Robo-Tank v3 compatible head unit

*Decided 2026-10-10. Spec only - no schematic yet. v1 (tag `v1.0.1`, branch `release/v1`)
stays the restart point if v2 is abandoned; v1-only fixes go to `release/v1` and are merged
into `main`.*

### Goal

A Robo-Tank v3 owner replaces only the head unit with aquaPCB v2 and keeps every module,
cable and power bar. Compatibility is **cables only**: plugs and pinouts match, while
the GPIO numbers and the software configuration may differ and are explained by the
mapping table below. The board runs reef-pi or aquaPi. Owners of older Robo-Tank
controllers (v1 Rev A/B+, about 10 v2 boards) get the mapping table only.

Reference: Robo-Tank manual "Controller and its ports" (v3, last updated 2021-12-28),
linked from robo-tank.ca/reef-pi_Related_User_Manuals. Pin positions below are read from
its photos - verify with a meter on a real v3 module or cable before layout.

### Robo-Tank v3 ports to match

```
Port            Connector       Pins (as documented)                      Driven by (v3)
DC Ports        RJ45            1 GND, 2..8 = 0-5 V PWM 9,6,7,4,3,2,1     PCA9685 ch 9,6,7,4,3,2,1
LED Ports       RJ45            1 GND, 2..8 = 0-5 V PWM 15,14,13,12,11,10,8   PCA9685 ch 15..10, 8
Sensors         RJ45            1 GND, 2..7 = inputs 6..1, 8 = +5 V       GPIO 23,27,18,17,15,14
Power Bar 1, 2  DB9 female      1..4 = Ch1..4, 5 = GND, 6..9 = Ch8..5     GPIO direct (3.3 V)
                (straight-through cable to the bar's DB9 male; a null-modem cable shorts Ch1)
Backup floats   2x 2-pole       float in series with bar 1 outlet 2 (AC1) and outlet 1 (AC2)
Feeder          3-pole          +3.3 V / Signal (switched GND) / GND, < 500 mA   PCA9685 ch 0
Temp 1, 2       3-pole each     +5 V / Data / GND                         GPIO 4, GPIO 22
I2C             4-pin header    +5 V / SCL / SDA / GND (5 V side of a level converter)
pH              BNC
Power in        5.5/2.1 barrel  centre +, 12-24 V, >= 1 A; powers the Pi
```

### aquaPCB v2 connectors

```
Port            Connector              Source on aquaPCB v2
DC              RJ45, v3 pinout        PCA #1 ch 1,2,3,4,6,7,9 -> 5 V buffer (0-5 V PWM)
LED             RJ45, v3 pinout        PCA #1 ch 8,10..15      -> 5 V buffer (0-5 V PWM)
Sensors         RJ45, v3 pinout        6 GPIO inputs, 5 V tolerant, +5 V supply pin (fused)
Power Bar 1, 2  2x5 box header each    PCA #2 ch 0..15, push-pull at 3.3 V like Pi GPIO
                + adapter cable        10-wire ribbon with crimped IDC DB9 female
Backup floats   2x 2-pole terminal     in series with bar 1 outlets 1/2, pull-down -> OFF
Feeder          3-pole terminal        PCA #1 ch 0 -> small low-side MOSFET
Temp            1x 3-pole terminal     1-Wire on GPIO 4, +5 V / Data / GND order as v3;
                                       one bus, both probes into the same terminal
I2C             3.3 V header (as v1)   + optional 5 V header behind a PCA9306 level shifter
Analog / pH     4x 3-pole socket       one per ADS1115 input AIN0..AIN3, all identical,
                (+5 V / SIG / GND)     0-5 V each; pH/ORP amplifiers sit on add-on
                                       modules (see below), no reference input
Power in        push-in terminal (J1)  12-24 V, 8 A as v1 - no barrel socket (rated for
                                       far less current than the board's 8 A)
Power outputs   push-in terminals      Q1..Q6, 5 A low-side as v1: Q1/Q4 on the Pi's
                                       hardware PWM0/1, Q2/Q3/Q5/Q6 on PCA #1 ch 15,14,13,12
                                       (shared with LED ports 1..4, dimmable)
SSR outputs     -                      S1..S4 and the ULN2803 dropped: SSRs and relay coils
                                       go on the Q outputs
```

Design rules behind this table:

- **PCA #1 uses Robo-Tank's channel numbers** (feeder 0, DC 1..4/6/7/9, LED 8/10..15,
  ch 5 spare). A reef-pi DC/LED configuration then carries over unchanged, provided the
  I²C address matches - still to confirm.
- **Q1/Q4 stay on the Pi's hardware PWM.** It is much smoother than the PCA9685
  (about 1.5 kHz, 12 bit), which matters when dimming lamps at low levels.
- **Q2/Q3/Q5/Q6 share PCA #1's LED channels 15, 14, 13, 12** (decided 2026-10-10). The
  Q outputs are a power stage (they switch V_IN to ground), the LED RJ45 pins are 0-5 V logic
  signals, so a Q output can't stand in for an RJ45 pin - but it can share its PCA channel:
  the same signal drives the RJ45 pin and, through the 74HCT244 gate buffer, the MOSFET.
  A new user gets four dimmable 12-24 V / 5 A outputs (LED strips, DC pumps), a Robo-Tank
  owner keeps the LED RJ45. Caveat: a shared pair always switches together - whoever uses
  LED port 1..4 for a Robo-Tank module leaves Q2/Q3/Q5/Q6 unconnected. This frees GPIO 12,
  13, 16, 26. Boot safety unchanged: the PCA9685 starts with all outputs off, /OE holds
  them off until software takes over, the gate buffer's pull-downs stay.
- **PCA #2 drives the 16 power bar outputs.** They start up off, and /OE holds them off until
  software takes over, so nothing switches while the Pi boots - unlike v3, where the bar pins
  are raw GPIOs including boot-time pull-ups. Second address (e.g. 0x41); keep the PCA9685
  All-Call address (0x70) in mind for other I²C devices.
- **Power bar adapter.** A crimped IDC DB9 maps ribbon wires 1..9 to DB9 pins
  1,6,2,7,3,8,4,9,5; wire 10 stays unconnected. Box header pinout:
  `1 Ch1, 2 Ch8, 3 Ch2, 4 Ch7, 5 Ch3, 6 Ch6, 7 Ch4, 8 Ch5, 9 GND, 10 spare` - verify on
  the first sample.
- **Logic levels.** The PCA9685s run on 3.3 V like the Pi's I²C bus, so no level shifter
  is needed; the DC/LED channels reach 5 V through 74HCT buffers (the v1 gate-driver
  approach).
- **No jumpers on inputs.** Sensor inputs must be safe for optical, non-contact and float
  sensors without configuration - on Robo-Tank a wrong jumper permanently damages an
  optical sensor.
- **Push-in terminals anywhere on the board** (decided 2026-10-11; replaces v1's "all
  terminals on the board edges"), except in the Raspberry Pi area: the Zero's footprint
  plus room for its SD card and cooling, or the Pi 3/4 box header plus its ribbon exit.
  Edge positions can keep v1's side-entry WJ250B; inside the board the wire has to come
  from above, so those positions need **top-entry (vertical) push-in terminals** - part
  still to choose, ideally the same 3.5 mm pitch and the same 8 A rating for the power
  terminals. Wires must not run across the Pi area. Keep V_IN and the Q1..Q6 terminals
  close to the power path and the analog sockets away from the switching outputs, as on
  v1. The freed edge length is what should let v2 stay at 100 x 100 mm despite the RJ45
  jacks and box headers.
- **Top-entry RJ45 allowed too** (decided 2026-10-11), under the same rule: outside the Pi
  area, cable and latch reachable from above. Price checked 2026-10-11: plain side-entry
  RJ45 ~$0.40 at LCSC; vertical/top-entry ~€0.60..0.95 (HSM 260E-8P8C) up to $1.72..2.67
  (TE 5556416-1) - so about €0.50..2 more per jack, €1.50..6 for all three. Use them only
  where an edge position doesn't fit; mixing both kinds is fine.
- **24 V** must be validated (parts are rated 40 V, v1 was only specified at 12 V).
- **S1..S4 and the ULN2803 are dropped** (decided 2026-10-10). The 74HCT244 can't replace
  the ULN2803 (±6 mA specified, ±35 mA abs. max per pin, ±70 mA per package, 5 V push-pull,
  vs. 500 mA open collector up to 50 V: fine for SSRs and opto relay modules, not for bare
  relay coils) - but neither is needed: the Q outputs (5 A low-side to V_IN, freewheel
  diodes fitted) take SSRs (+ to V_IN, − to the Q terminal), 12 V relay coils and solenoid
  valves better, and Robo-Tank's power bars run on 3.3 V logic straight from PCA #2, as v3
  drives them from raw GPIOs. Frees GPIO 17, 22, 23, 27.

### 0-10 V dimming: optional add-on module

The v3 LED port carries plain 0-5 V PWM into Robo-Tank's own extension modules, which make
0-10 V. v3 owners already have that, so aquaPCB v2 keeps the LED RJ45 at exactly 0-5 V PWM
and puts 0-10 V on a **separate, optional module** for new users whose lamps need it:

- RJ45 input from the LED port (7 channels + GND), own 12-24 V input (the v3 LED RJ45 has
  no supply pin).
- Per channel, DIP-switch selected: 0-5 V PWM, 0-10 V PWM, 0-5 V analog, 0-10 V analog
  (one rail-to-rail op-amp half, bypassable 2-pole filter, gain 1 or 2, protected output).
- Main board: no extra cost or area. Module: estimated €6..10 at batch 5 including PCB and
  assembly setup, enclosure extra.
- Chosen over on-board alternatives (2026-10-10): a separate on-board RJ45 would cost about
  €2.50..3.50 per board plus about 6 cm² and 16 mm of edge; selectable outputs on the LED
  RJ45 itself could damage a v3 extension if set to 10 V.

### pH / ORP amplifiers: add-on modules

**Decided 2026-10-10:** the v2 main board has **no pH front end**. It keeps the ADS1115 and
offers 3-pole add-on sockets (+5 V / SIG / GND) on its inputs; the electrode amplifier,
with BNC, buffer, bias and the guarded high-impedance layout, lives on a small add-on
module. Only the buffered, low-impedance signal crosses the connector. Everyone picks the
variant they need, and the main board gets simpler and cheaper.

```
add-on                       measures       isolation   1 MΩ ground-loop resistor
pH/ORP, non-isolated         pH, ORP        no          yes (moved here from v1's board)
pH/ORP, isolated (AMC3311)   pH, ORP        yes         no - not needed
EC (conductivity)            -              not covered by these modules, see below
```

- **Non-isolated variant** = the proven v1 front end moved onto a module: TLV9062 buffer,
  biased reference ("biased ground"), 10 MΩ / styroflex input RC, guard ring, and the 1 MΩ
  between PH_REF and the BNC shell that limits a ground-loop current to ~µA. A cheap
  PH-4502C-type board still works on the same socket, but has no such protection.
- **Isolated variant** for several probes in the same water (pH + ORP/EC) or equipment with
  leakage current, where a ground loop disturbs the reading - details below. Its input side
  floats, so no DC loop current can flow through the reference electrode; the 1 MΩ is not
  needed there.
- **ORP uses the same modules, unchanged.** An ORP electrode is also a high-impedance
  voltage source. Unlike pH (centred on 0 mV: 0 mV at pH 7, ±59 mV/pH), aquarium ORP is
  mostly positive, typically +150..+450 mV - but one bias fits both: with the AMC3311's
  −0.1..2 V input and the pH bias of 1.2 V the isolated module measures −1.3..+0.8 V
  (the non-isolated one, biased at 1.65 V, about ±1.65 V). Only ORP above +800 mV is out
  of range, which doesn't occur in an aquarium. No bias option, no second variant; only the
  calibration differs: pH needs 2 points (offset and slope), ORP only an offset from one
  test solution (e.g. 225 mV or 470 mV), no temperature compensation. aquaPi's ScaleAux
  handles both.
- **EC is a different circuit.** A conductivity cell is not a voltage source: it needs AC
  excitation (DC polarises the electrodes), a measuring/rectifying stage, temperature
  compensation and a cell constant. Use a bought EC module; isolating its output (like
  DFRobot's Gravity isolator) would exceed the AMC3311's 4 mA high-side budget and needs
  its own isolated DC/DC.
- **Four identical analog sockets, no reference input** (decided 2026-10-10). v1's AIN1
  measured PH_REF, the bias of the on-board amplifier, as a monitor and as the second half
  of a later AIN0−AIN1 differential reading. On v2 the reference lives on the add-on (the
  isolated module's is not even visible to the main board), and the ADS1115 has its own
  internal reference, so that input has no purpose any more. Instead every input gets the
  same socket:

  ```
  pin  signal  path
  1    +5 V    for the module; one shared PTC/fuse for all four sockets
  2    SIG     10k/20k divider -> 1k/100nF -> clamp -> AINx
  3    GND
  ```

  The divider is needed on every socket: the ADS1115 runs on 3.3 V (to match the Pi's I²C
  bus) and its inputs must stay below ~3.6 V, so each socket accepts 0..5 V - a PH-4502C,
  other 5 V modules, and the pH/ORP add-ons (0.8..2 V) alike. It costs a factor 1.5 in
  resolution, still ~0.003 pH per step, below the noise. Any sensor can go on any socket;
  v1's split into pH input, module input and 0..3.3 V input disappears. About
  €0.30..0.50 per socket, against ~€1.50 for v1's on-board pH amplifier.
- A later differential add-on uses two adjacent sockets as a pair (AIN0-1 or AIN2-3, the
  pairs the ADS1115 supports).
- The sockets' +5 V and GND are the main board's, so only the add-ons decide about
  isolation: the non-isolated module carries the 1 MΩ ground-loop resistor, a bought
  PH-4502C has none.

#### Isolated variant (AMC3311)

```
isolated side (AMC3311 HLDO_OUT, 3.2 V)       | low side (main board +5 V)
BNC -> 10M / styroflex RC -> TLV9062 buffer   | AMC3311 OUTP/OUTN
       -> AMC3311 IN                          |   -> difference amp (op-amp, 4x 0.1 % R)
BNC shell <- LM4040-1.2 bias                  |   -> SIG -> main board add-on socket
```

Based on the AMC3311 data sheet (TI SBASAQ5A) and TLV9062 data sheet, checked 2026-10-10:

- **The AMC3311's integrated isolated DC/DC powers the whole isolated side** via HLDO_OUT
  (3.0..3.4 V): max 4 mA external, non-switching load with VDD 3.6..5.5 V, but only 1 mA
  with VDD below 3.6 V - so run the AMC3311 from **+5 V**. Load: TLV9062 dual 538 µA typ /
  800 µA max per amplifier (up to 1.6 mA) plus the LM4040 (~0.1 mA) - well inside 4 mA.
- **The buffer is mandatory.** AMC3311 input: 1 GΩ, bias current 3.5 nA typ / ±15 nA max -
  directly on a 100 MΩ..1 GΩ electrode that would be volts of error. The TLV9062 (pA bias)
  stays in front, with the v1 input RC and guard layout.
- **Bias from a reference, not a divider.** Linear input range is −0.1..2 V, so the BNC
  shell sits at ~1.2 V (LM4040-1.2); pH 0..14 then spans about 0.8..1.6 V. A divider from
  HLDO_OUT would carry its ±0.2 V tolerance and drift into the reading.
- **The difference amplifier sits on the low side** (AMC3311 outputs are referenced to the
  main board's ground, common mode 1.39..1.49 V) and is powered from +5 V, not from the
  isolated supply. Gain 1 gives a single-ended 0.8..1.6 V on one ADS1115 input.
- **Accuracy is plenty for ~0.1 pH:** offset ±1 mV and gain ±0.2 % are removed by aquaPi's
  2-point calibration; nonlinearity ±0.02 %; drift ±10 µV/°C offset, ±40 ppm/°C gain
  (about 0.004 pH over 25 °C); output noise 250 µVrms in 100 kHz, far less behind the RC
  filter and the ADS1115's slow sampling.
- **Risk to measure on the prototype:** the AMC3311's DC/DC switches inside the package next
  to a 1 GΩ source - check the reading's noise with the probe in buffer solution before
  committing to the design.
- **Alternative later:** once aquaPi supports differential ADC ports, OUTP/OUTN could go
  straight into an ADS1115 input pair - no difference amp, but two inputs per probe.
- Cost (isolated variant): AMC3311 price still to check (the AMC1311, without integrated DC/DC, is about $1.20
  at LCSC); BNC, TLV9062, LM4040, op-amp, 0.1 % resistors about €3 more. Compare: DFRobot
  Gravity isolator ~$20, Atlas EZO pH + isolated carrier ~$79, Robo-Tank isolated pH $54.95.

### Robo-Tank v3 -> aquaPCB v2 mapping

```
Robo-Tank v3            aquaPCB v2              reef-pi setting on aquaPCB v2
DC Ports RJ45           DC RJ45                 PCA9685 ch as on v3 (address TBD)
LED Ports RJ45          LED RJ45                PCA9685 ch as on v3 (address TBD);
                                                LED 1..4 also drive Q2/Q3/Q5/Q6
Sensors RJ45            Sensors RJ45            GPIO 5,6,20,21,22,23 (suggested)
Power Bar 1/2 (DB9)     header + DB9 adapter    PCA9685 #2 ch 0..7 / 8..15
AC1/AC2 backup floats   float terminals         hardware only
Feeder                  Feeder terminal         PCA9685 ch 0
Temp 1/2                one Temp terminal       1-Wire GPIO 4, both probes on one bus
I2C                     5 V I2C header          bus 1
pH BNC                  pH/ORP add-on module    ADS1115 input (aquaPi; reef-pi: TBD)
Power in (barrel plug)  J1 push-in terminal     barrel-to-terminal adapter (<€1)
```

### v1 -> v2 changes

Ports with their aquaPi IoRegistry names. Existing names as aquaPi reports them today
(`GPIO 17 out`, `PWM 0`, `DS1820 #1`, `ADC #1 in 0`); the PCA9685 names don't exist yet
and follow the same pattern. **[S]** = suggestion, not yet decided.

```
function          v1: GPIO / aquaPi port             v2: GPIO / aquaPi port
------------------------------------------------------------------------------------------
Q1 power out      GPIO 18, PWM0 -> "PWM 0"           unchanged
Q4 power out      GPIO 19, PWM1 -> "PWM 1"           unchanged
Q2,Q3,Q5,Q6       GPIO 12,13,16,26 -> "GPIO n out"   PCA9685 #1 ch 15,14,13,12, shared with
                                                     LED ports 1..4 -> [S] "PCA9685 #1 ch n"
S1..S4 SSR out    GPIO 17,22,23,27 -> "GPIO n out"   dropped (SSRs go on Q outputs)
IN1..IN4          GPIO 5,6,20,21 -> "GPIO n in"      replaced by sensor RJ45 (6 inputs):
                                                     [S] GPIO 5,6,20,21,22,23 -> "GPIO n in"
1-Wire temp       1 terminal, GPIO 4 -> "DS1820 #n"  unchanged: 1 terminal, GPIO 4, one bus for
                                                     all probes -> "DS1820 #n"
DC ports (7)      -                                  PCA9685 #1 ch 1,2,3,4,6,7,9 (0-5 V PWM)
                                                     -> [S] "PCA9685 #1 ch n"
LED ports (7)     -                                  PCA9685 #1 ch 8,10..15 -> [S] same pattern
feeder            -                                  PCA9685 #1 ch 0 -> small MOSFET
spare             -                                  PCA9685 #1 ch 5
power bar 1, 2    -                                  PCA9685 #2 ch 0..7, 8..15, 3.3 V logic
                                                     -> [S] "PCA9685 #2 ch n"
backup floats     -                                  hardware only, no port
AIN0              on-board pH amp -> "ADC #1 in 0"   socket 1, 0-5 V -> "ADC #1 in 0"
AIN1              PH_REF monitor -> "ADC #1 in 1"    socket 2, 0-5 V -> "ADC #1 in 1"
AIN2              module input 0-5 V                 socket 3, 0-5 V -> "ADC #1 in 2"
AIN3              general 0-3.3 V                    socket 4, 0-5 V -> "ADC #1 in 3"
(later)           -                                  differential pairs [S] "ADC #1 in 0-1"/"2-3"
I2C               3.3 V header, GPIO 2/3             + optional 5 V header (PCA9306)
I2C addresses     ADS1115 0x48                       + PCA9685 #1 0x40 (TBD: match Robo-Tank),
                                                     #2 [S] 0x41; keep 0x70 (All-Call) free
display SPI       GPIO 7..11, 24, 25                 open: not decided for v2
GPIO 0/1, 14/15   ID EEPROM reserved / unused        unchanged
free GPIOs        -                                  12,13,16,17,26,27 (after [S] sensor pins)
```

Active parts on the main board:

```
DROPPED
  ULN2803A (S1..S4 SSR driver)          SSRs/relay coils go on the Q outputs
  TLV9062 (pH buffer)                   moves to the pH/ORP add-ons
  BAT54S clamps of IN1..IN4             replaced by the sensor-input protection below
  (passives, for completeness: BNC, styroflex 6.8n, 10 MΩ, 1 MΩ -> add-ons)

ADDED
  2x PCA9685 (16 ch, 12 bit PWM, I²C)   #1 DC/LED/feeder + Q2/Q3/Q5/Q6, #2 power bars
  74HCT buffers for 14x 0-5 V PWM       DC + LED RJ45 -> [S] 2x 74HCT244
  PCA9306 (I²C level shifter)           optional 5 V I²C header
  small N-MOSFET (feeder, low side)     [S] e.g. AO3400, SOT-23
  sensor-input protection, 6 inputs     5 V tolerant, no jumpers -> [S] series R + BAT54S
  BAT54S clamps, 4 analog sockets       after the 10k/20k divider + RC
  PTC/fuse for +5 V                     sensor RJ45 and analog sockets

UNCHANGED
  TPS54360B 5 V buck (check the budget: sensors, add-ons, 2x PCA9685 now on 5 V/3.3 V),
  AMS1117-3.3, ADS1115, 74HCT244 gate buffer (Q1..Q6), 6x AOD4184A + SS54,
  AOD4185 reverse-polarity FET + zener, SMBJ33A TVS, LEDs

ON ADD-ON BOARDS
  pH/ORP non-isolated: TLV9062 (+ v1 passives incl. 1 MΩ)
  pH/ORP isolated:     AMC3311, TLV9062, LM4040-1.2, op-amp (difference amp)
  0-10 V module:       rail-to-rail op-amps, one half per channel
```

### Open questions (asked to Robo-Tank, or measure)

- Does the 2021-12-28 manual still match the kit sold today (product code FullDv3Ra)?
- Power bar input: current per channel, active high/low, state with the line open; which
  DB9 pin carries the optional +5 V / +12 V mentioned on the product page?
- PCA9685 I²C address and PWM frequency on the v3 controller; input type of the DC and
  LED modules (accepted PWM frequency range, input current).
- Sensor module: does it need pull-ups/pull-downs from the controller?

## Roadmap

1. Specification (this file), BOM with LCSC / Reichelt part numbers ([BOM.md](BOM.md)) – done
2. Schematic in KiCad, ERC clean – done
3. Layout, DRC clean – done
4. Gerbers, JLC BOM/CPL, 1:1 print check (terminals, BNC, Pi header), order 5 prototypes
   – on hold until the v2 go/no-go below
5. Bring-up at 12 V: rails without Pi, then with Pi Zero 2 W, boot with loads attached
   (no output may toggle), all channels from the aquaPi dashboard, 5 A thermal test
6. Validate 24 V operation

v2 ([Robo-Tank v3 compatible head unit](#v2-plan-robo-tank-v3-compatible-head-unit)):

1. Spec – done
2. Answers from Robo-Tank, or measure a v3 module and cable (open questions in the v2 plan)
   – questions sent to info@robo-tank.ca 2026-10-10, waiting for the reply
3. Budget and sense check → go/no-go; on no-go, continue with v1 step 4
4. aquaPi PCA9685 driver (needed for the DC/LED ports and power bars)
5. Schematic and layout, starting from the v1 design
6. 0-10 V add-on module

## Licence

Copyright Markus Kuhn 2026.

This source describes Open Hardware and is licensed under the CERN-OHL-S v2
(`SPDX-License-Identifier: CERN-OHL-S-2.0`), see [LICENSE](LICENSE).

You may redistribute and modify this source and make products using it under the terms
of the CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt). This source is distributed
WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY
QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable
conditions.

Source location: https://github.com/schwabix-1311/aquaPCB. As per CERN-OHL-S v2
section 4, should you produce hardware based on this source, you must where practicable
maintain the Source Location visible on the external case or other product you make.
