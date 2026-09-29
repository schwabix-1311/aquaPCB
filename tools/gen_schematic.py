#!/usr/bin/env python3
"""Generate the aquaPCB schematic draft (hierarchical, KiCad).

    python3 tools/gen_schematic.py   (then upgrade + ERC, see README, section "Schematic")

Pin map, parts and values follow README.md / BOM.md. Nets are connected by name
(power symbols, local and global labels), so the drawing is a readable netlist, not a
hand-routed schematic. Once the schematic has been edited in eeschema, the .kicad_sch
files are the source of truth and this script must not be re-run over them.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schgen import Project, NC   # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), '..', 'kicad')

# ---------------------------------------------------------------- footprints / sourcing
R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
LED0805 = 'LED_SMD:LED_0805_2012Metric'
SMA = 'Diode_SMD:D_SMA'
SMB = 'Diode_SMD:D_SMB'
SOD123 = 'Diode_SMD:D_SOD-123'
SOT23 = 'Package_TO_SOT_SMD:SOT-23'
TO252 = 'Package_TO_SOT_SMD:TO-252-2'
TERM2 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
TERM3 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal'


def hdr(n):
    return f'Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical'


RES = {'10k': 'C17414', '1k': 'C17513', '4k7': 'C17673', '100': 'C17408', '12k': 'C17444',
       '2k2': 'C17520', '150k': 'C17470', '220k': 'C17556'}
CAP = {'100n': ('C49678', C0805), '10n': ('C1710', C0805), '47p': ('C14857', C0805),
       '10u': ('C15850', C0805), '47u': ('C96123', C1206), '4u7/50V': ('C29823', C1206)}
REICHELT = 'Reichelt'

p = Project('aquaPCB')


def R(sh, value, n1, n2, rot=90):
    return sh.part('Device:R', 'R', value, {'1': n1, '2': n2}, fp=R0805, lcsc=RES[value], rot=rot)


def C(sh, value, n1, n2, rot=0):
    lcsc, fp = CAP[value]
    return sh.part('Device:C', 'C', value.replace('/', ' '), {'1': n1, '2': n2}, fp=fp, lcsc=lcsc, rot=rot)


def LED(sh, color, anode, cathode):
    lcsc = {'green': 'C2297', 'red': 'C84256'}[color]
    return sh.part('Device:LED', 'D', f'LED {color}', {'2': anode, '1': cathode}, fp=LED0805, lcsc=lcsc)


def clamp(sh, net):
    """BAT54S: signal clamped to GND and +3V3."""
    return sh.part('Diode:BAT54S', 'D', 'BAT54S', {'1': 'GND', '2': '+3V3', '3': net}, fp=SOT23, lcsc='C12765')


def term(sh, nets, value):
    n = len(nets)
    lib = 'Connector:Screw_Terminal_01x%02d' % n
    return sh.part(lib, 'J', value, {str(i + 1): net for i, net in enumerate(nets)},
                   fp=TERM2 if n == 2 else TERM3, fields={REICHELT: 'AKL 101-%02d' % n})


def header(sh, nets, value):
    n = len(nets)
    return sh.part('Connector_Generic:Conn_01x%02d' % n, 'J', value,
                   {str(i + 1): net for i, net in enumerate(nets)}, fp=hdr(n),
                   fields={REICHELT: 'ECON SL40G1 (cut)'})


# ================================================================ Power
sh = p.sheet('power', 'power.kicad_sch', 'Power supply')
sh.note('12 V input (24 V ready): fuse, reverse-polarity P-FET, TVS, bulk', 2)
j = term(sh, ['VIN_RAW', 'GND'], '12V IN')
f = sh.part('Device:Fuse', 'F', '10A', {'1': 'VIN_RAW', '2': 'VIN_F'},
            fp='aquaPCB:Littelfuse_OMNI-BLOK_154', fields={REICHELT: 'LITT 0154010.DR'})
qp = sh.part('Transistor_FET:Q_PMOS_GDS', 'Q', 'AOD4185', {'1': 'PFET_G', '2': 'VIN_F', '3': 'VIN'},
             fp=TO252, lcsc='C400894', ref='Q10')
rg = R(sh, '10k', 'PFET_G', 'GND')
dz = sh.part('Device:D_Zener', 'D', 'BZT52C15', {'1': 'VIN', '2': 'PFET_G'}, fp=SOD123, lcsc='C173427')
sh.row([j, f, qp, rg, dz])
tvs = sh.part('Device:D_Zener', 'D', 'SMBJ33A', {'1': 'VIN', '2': 'GND'}, fp=SMB, lcsc='C78419')
cb = sh.part('Device:C_Polarized', 'C', '470u 50V', {'1': 'VIN', '2': 'GND'},
             fp='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', fields={REICHELT: 'RAD FR 470/50'})
rl = R(sh, '10k', 'VIN', 'LED_PWR')
dl = LED(sh, 'red', 'LED_PWR', 'GND')
sh.row([tvs, cb, rl, dl])
sh.note('Q10 body diode conducts first, then the channel turns on (V_GS = -V_IN, clamped to -15 V by the\n'
        'zener for 24 V operation). Reversed input: Q10 stays off.')

sh.note('5 V / 3 A buck, TPS54360B (TI datasheet SNVSB93 Fig. 32, values moved to JLC basic parts)', 2)
u = sh.part('Regulator_Switching:TPS54360DDA', 'U', 'TPS54360B',
            {'1': 'BOOT', '2': 'VIN', '3': NC, '4': 'RT', '5': 'FB', '6': 'COMP', '7': 'GND', '8': 'SW',
             '9': 'GND'}, lcsc='C524806')
cin1 = C(sh, '4u7/50V', 'VIN', 'GND')
cin2 = C(sh, '4u7/50V', 'VIN', 'GND')
cin3 = C(sh, '100n', 'VIN', 'GND')
sh.row([cin1, cin2, cin3, u])
cboot = C(sh, '100n', 'BOOT', 'SW')
rt = R(sh, '150k', 'RT', 'GND')
rc = R(sh, '12k', 'COMP', 'COMP_RC')
cc = C(sh, '10n', 'COMP_RC', 'GND')
chf = C(sh, '47p', 'COMP', 'GND')
sh.row([cboot, rt, rc, cc, chf])
l1 = sh.part('Device:L', 'L', '10uH 4.8A', {'1': 'SW', '2': '+5V'}, fp='Inductor_SMD:L_TDK_SLF12565',
             lcsc='C138303', rot=90)
dcatch = sh.part('Device:D_Schottky', 'D', 'SS54', {'1': 'SW', '2': 'GND'}, fp=SMA, lcsc='C22452')
co1 = C(sh, '47u', '+5V', 'GND')
co2 = C(sh, '47u', '+5V', 'GND')
rfb1 = R(sh, '12k', '+5V', 'FB')
rfb2 = R(sh, '2k2', 'FB', 'GND')
sh.row([l1, dcatch, co1, co2, rfb1, rfb2])
sh.note('f_sw = 644 kHz (RT 150k). V_OUT = 0.8 V x (1 + 12k/2.2k) = 5.16 V. EN open = enabled, internal\n'
        'UVLO 4.3 V. Catch diode SS54: ~1 W at 3 A / 12 V in, give it copper.')

sh.note('3.3 V for ADC, sensors, inputs, display (not connected to the Pi\'s own 3V3)', 2)
ldo = sh.part('Regulator_Linear:AMS1117-3.3', 'U', 'AMS1117-3.3', {'1': 'GND', '2': '+3V3', '3': '+5V'},
              lcsc='C6186')
c1 = C(sh, '10u', '+5V', 'GND')
c2 = C(sh, '10u', '+3V3', 'GND')
r3 = R(sh, '1k', '+3V3', 'LED_3V3')
d3 = LED(sh, 'green', 'LED_3V3', 'GND')
jp = sh.part('Jumper:Jumper_2_Open', 'JP', '5V→Pi', {'1': '+5V', '2': '5V_PI'}, fp=hdr(2),
             fields={REICHELT: 'ECON SL40G1 (cut) + JUMPER 2,54 SW'})
sh.row([ldo, c1, c2, r3, d3, jp])
sh.note('JP "5V→Pi": close to power the Pi from this board. Leave OPEN when the Pi has its own USB supply\n'
        '(always for Pi 5).')
for n in ('VIN', 'GND', '+5V'):
    sh.pwr_flag(n)

# ================================================================ Raspberry Pi
sh = p.sheet('pi', 'pi.kicad_sch', 'Raspberry Pi connector')
sh.note('40-pin Pi header, normal (not mirrored) numbering. Fit 2x20 socket (Pi Zero 2 W face-up, header\n'
        'soldered on its underside) or 40-pin box header (Pi 3/4 via IDC ribbon).', 2)
pi_pins = {
    1: NC, 2: '5V_PI', 3: 'GPIO2_SDA', 4: '5V_PI', 5: 'GPIO3_SCL', 6: 'GND', 7: 'GPIO4_1W', 8: 'GPIO14_TXD',
    9: 'GND', 10: 'GPIO15_RXD', 11: 'GPIO17_S1', 12: 'GPIO18_Q1', 13: 'GPIO27_S4', 14: 'GND',
    15: 'GPIO22_S2', 16: 'GPIO23_S3', 17: NC, 18: 'GPIO24_DISP_RST', 19: 'GPIO10_MOSI', 20: 'GND',
    21: 'GPIO9_MISO', 22: 'GPIO25_DISP_DC', 23: 'GPIO11_SCLK', 24: 'GPIO8_CE0', 25: 'GND', 26: 'GPIO7_CE1',
    27: NC, 28: NC, 29: 'GPIO5_IN1', 30: 'GND', 31: 'GPIO6_IN2', 32: 'GPIO12_Q3', 33: 'GPIO13_Q4', 34: 'GND',
    35: 'GPIO19_Q2', 36: 'GPIO16_Q5', 37: 'GPIO26_Q6', 38: 'GPIO20_IN3', 39: 'GND', 40: 'GPIO21_IN4'}
jpi = sh.part('Connector_Generic:Conn_02x20_Odd_Even', 'J', 'Raspberry Pi',
              {str(k): v for k, v in pi_pins.items()}, fp='Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical',
              fields={REICHELT: 'MPE 094-2-040 (socket) or WSL 40G (box header)'})
uart = header(sh, ['GND', 'GPIO14_TXD', 'GPIO15_RXD'], 'UART console')
sh.row([jpi, uart])
sh.note('Pins 1/17 (Pi 3V3) stay unconnected: this board has its own 3.3 V regulator.\n'
        'Pins 27/28 (ID EEPROM) unused. GPIO 14/15 only go to the UART console header.')
holes = [sh.part('Mechanical:MountingHole', 'H', 'M3', {}, fp='MountingHole:MountingHole_3.2mm_M3')
         for _ in range(4)]
holes += [sh.part('Mechanical:MountingHole', 'H', 'M2.5 Pi Zero', {}, fp='MountingHole:MountingHole_2.7mm_M2.5')
          for _ in range(4)]
sh.row(holes, gap=12.7)

# ================================================================ Power outputs
sh = p.sheet('outputs', 'outputs.kicad_sch', 'Power outputs Q1..Q6')
sh.note('74HCT244 shifts 3.3 V GPIO to 5 V gate drive and isolates the Pi from the power stage.', 2)
gpio_q = ['GPIO18_Q1', 'GPIO19_Q2', 'GPIO12_Q3', 'GPIO13_Q4', 'GPIO16_Q5', 'GPIO26_Q6']
buf = sh.part('74xx:74HCT244', 'U', '74HCT244D', {
    '1': 'GND', '19': 'GND', '20': '+5V', '10': 'GND',
    '2': gpio_q[0], '4': gpio_q[1], '6': gpio_q[2], '8': gpio_q[3],
    '17': gpio_q[4], '15': gpio_q[5], '13': 'GND', '11': 'GND',
    '18': 'Q1_DRV', '16': 'Q2_DRV', '14': 'Q3_DRV', '12': 'Q4_DRV',
    '3': 'Q5_DRV', '5': 'Q6_DRV', '7': NC, '9': NC},
    fp='Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm', lcsc='C5978')
cbuf = C(sh, '100n', '+5V', 'GND')
pulldowns = [R(sh, '10k', g, 'GND') for g in gpio_q]
sh.row([buf, cbuf] + pulldowns[:3])
sh.row(pulldowns[3:])
sh.note('Per channel: 100R gate resistor, 10k gate pull-down (off while the Pi boots or is absent),\n'
        'AOD4184A 40 V low-side switch, SS54 freewheel diode to VIN, status LED on the 5 V drive signal.\n'
        'Q1/Q2 = hardware PWM (light, fan). Terminal: pin 1 = +VIN, pin 2 = switched OUT (load between).')
for n in range(1, 7):
    drv, g, out = f'Q{n}_DRV', f'Q{n}_G', f'Q{n}_OUT'
    rgate = R(sh, '100', drv, g)
    rpd = R(sh, '10k', g, 'GND')
    q = sh.part('Transistor_FET:Q_NMOS_GDS', 'Q', 'AOD4184A', {'1': g, '2': out, '3': 'GND'},
                fp=TO252, lcsc='C99124', ref=f'Q{n}', rot=90)
    dfw = sh.part('Device:D_Schottky', 'D', 'SS54', {'1': 'VIN', '2': out}, fp=SMA, lcsc='C22452')
    rled = R(sh, '1k', drv, f'Q{n}_LED')
    dled = LED(sh, 'green', f'Q{n}_LED', 'GND')
    t = term(sh, ['VIN', out], f'OUT Q{n}')
    sh.row([rgate, rpd, q, dfw, rled, dled, t])

# ================================================================ SSR outputs
sh = p.sheet('ssr', 'ssr.kicad_sch', 'SSR / relay control outputs S1..S4')
sh.note('ULN2803A open-collector sinks for external SSRs (3..32 V DC input) or relay modules.\n'
        'No mains voltage on this board.', 2)
uln = sh.part('Transistor_Array:ULN2803A', 'U', 'ULN2803A', {
    '1': 'GPIO17_S1', '2': 'GPIO22_S2', '3': 'GPIO23_S3', '4': 'GPIO27_S4',
    '5': 'SPARE_I5', '6': 'SPARE_I6', '7': 'SPARE_I7', '8': 'SPARE_I8',
    '9': 'GND', '10': 'SSR_V',
    '18': 'S1_OUT', '17': 'S2_OUT', '16': 'S3_OUT', '15': 'S4_OUT',
    '14': 'SPARE_O5', '13': 'SPARE_O6', '12': 'SPARE_O7', '11': 'SPARE_O8'},
    fp='Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm', lcsc='C2977078')
jsel = sh.part('Jumper:Jumper_3_Open', 'JP', 'SSR supply', {'1': '+5V', '2': 'SSR_V', '3': 'VIN'}, fp=hdr(3),
               fields={REICHELT: 'ECON SL40G1 (cut) + JUMPER 2,54 SW'})
spare = header(sh, ['SPARE_I5', 'SPARE_I6', 'SPARE_I7', 'SPARE_I8',
                    'SPARE_O5', 'SPARE_O6', 'SPARE_O7', 'SPARE_O8', 'SSR_V', 'GND'], 'ULN spare')
sh.row([uln, jsel, spare])
sh.note('JP "SSR supply": 1-2 = +5 V, 2-3 = VIN for SSR/relay coil supply (terminal pin 1).\n'
        'Terminal: pin 1 = SSR_V (+), pin 2 = OUT (sinks to GND when on).')
for n in range(1, 5):
    out = f'S{n}_OUT'
    rled = R(sh, '4k7', 'SSR_V', f'S{n}_LED')
    dled = LED(sh, 'green', f'S{n}_LED', out)
    t = term(sh, ['SSR_V', out], f'SSR S{n}')
    sh.row([rled, dled, t])

# ================================================================ Inputs, 1-Wire, display
sh = p.sheet('io', 'io.kicad_sch', 'Inputs, 1-Wire, I2C and display headers')
sh.note('Digital inputs IN1..IN4 (float/level switches, buttons). Terminal: 3V3 / IN / GND.', 2)
for n, g in enumerate(['GPIO5_IN1', 'GPIO6_IN2', 'GPIO20_IN3', 'GPIO21_IN4'], 1):
    t = term(sh, ['+3V3', f'IN{n}_T', 'GND'], f'IN{n}')
    rs = R(sh, '1k', f'IN{n}_T', g)
    rp = R(sh, '10k', '+3V3', g)
    sh.row([t, rs, rp, clamp(sh, g)])
sh.note('1-Wire (DS18B20), GPIO4, 4.7k pull-up. Terminal: GND / DQ / 3V3; parasitic sensors use GND + DQ.', 2)
r1w = R(sh, '4k7', '+3V3', 'GPIO4_1W')
terms = [term(sh, ['GND', 'GPIO4_1W', '+3V3'], f'1-Wire {i}') for i in range(1, 4)]
sh.row([r1w, clamp(sh, 'GPIO4_1W')] + terms)
sh.note('I2C expansion (OLED, PCA9685, ...), SSD1306 pin order. Pull-ups are on the Pi (1.8k).', 2)
i2c = [header(sh, ['GND', '+3V3', 'GPIO3_SCL', 'GPIO2_SDA'], f'I2C {i}') for i in (1, 2)]
sh.row(i2c)
sh.note('SPI display (ST7735 / ILI9341). Backlight to 3V3 via jumper.', 2)
disp = header(sh, ['GND', '+3V3', 'GPIO11_SCLK', 'GPIO10_MOSI', 'GPIO9_MISO', 'GPIO8_CE0', 'GPIO7_CE1',
                   'GPIO25_DISP_DC', 'GPIO24_DISP_RST', 'DISP_BL'], 'Display')
jbl = sh.part('Jumper:Jumper_2_Open', 'JP', 'Backlight', {'1': '+3V3', '2': 'DISP_BL'}, fp=hdr(2),
              fields={REICHELT: 'ECON SL40G1 (cut) + JUMPER 2,54 SW'})
sh.row([disp, jbl])

# ================================================================ ADC and pH
sh = p.sheet('analog', 'analog.kicad_sch', 'ADS1115 ADC and pH front end')
sh.note('ADS1115 on 3.3 V, I2C address 0x48 (JP 1-2, default) or 0x49 (2-3). ALERT/RDY unused.', 2)
adc = sh.part('Analog_ADC:ADS1115IDGS', 'U', 'ADS1115IDGSR', {
    '1': 'ADS_ADDR', '2': NC, '3': 'GND', '4': 'PH_SIG', '5': 'PH_REF', '6': 'AIN2', '7': 'AIN3',
    '8': '+3V3', '9': 'GPIO2_SDA', '10': 'GPIO3_SCL'}, lcsc='C37593')
cadc = C(sh, '100n', '+3V3', 'GND')
jaddr = sh.part('Jumper:SolderJumper_3_Bridged12', 'JP', 'ADDR', {'1': 'GND', '2': 'ADS_ADDR', '3': '+3V3'},
                fp='Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm')
sh.row([adc, cadc, jaddr])
sh.note('pH probe: glass electrode on BNC centre, reference on BNC shell. The shell sits at PH_REF\n'
        '(1.65 V), NOT at GND - BNC shell pads must stay on net PH_REF. Read AIN0-AIN1 differentially.', 2)
opa = sh.part('Amplifier_Operational:TLV9062xD', 'U', 'TLV9062IDR', {
    '3': 'PH_IN', '2': 'PH_SIG', '1': 'PH_SIG',
    '5': 'PH_MID', '6': 'PH_REF', '7': 'PH_REF',
    '8': '+3V3', '4': 'GND'}, lcsc='C398355')
bnc = sh.part('Connector:Conn_Coaxial', 'J', 'pH probe', {'1': 'PH_BNC', '2': 'PH_REF'},
              fp='Connector_Coaxial:BNC_Amphenol_031-5539_Vertical', fields={REICHELT: 'UG 1094PL'})
rin = R(sh, '220k', 'PH_BNC', 'PH_IN')
sh.row([bnc, rin, (opa, 1)])
rm1 = R(sh, '10k', '+3V3', 'PH_MID')
rm2 = R(sh, '10k', 'PH_MID', 'GND')
cm = C(sh, '100n', 'PH_MID', 'GND')
copa = C(sh, '100n', '+3V3', 'GND')
sh.row([rm1, rm2, cm, (opa, 2), (opa, 3), copa])
sh.note('AIN2/AIN3: general 0..3.3 V inputs, 1k + 100n low-pass, clamped. Terminal: AIN2 / AIN3 / GND.', 2)
tain = term(sh, ['AIN2_T', 'AIN3_T', 'GND'], 'AIN')
ra2 = R(sh, '1k', 'AIN2_T', 'AIN2')
ra3 = R(sh, '1k', 'AIN3_T', 'AIN3')
ca2 = C(sh, '100n', 'AIN2', 'GND')
ca3 = C(sh, '100n', 'AIN3', 'GND')
sh.row([tain, ra2, ca2, clamp(sh, 'AIN2'), ra3, ca3, clamp(sh, 'AIN3')])

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    p.write(OUT, 'aquaPCB', 'v1 draft', '2026-09-29')
    print('written to', os.path.normpath(OUT))
