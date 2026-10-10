# aquaPCB compared to other Raspberry Pi aquarium boards

*As of October 2026. Prices are shop listings found at that time and change;
aquaPCB has no prototype yet, so its figures are design values.*

aquaPCB is a base board for running [aquaPi](https://github.com/schwabix-1311/aquaPI)
on a Raspberry Pi. The closest alternatives are boards made for
[reef-pi](https://reef-pi.github.io/), the open-source reef controller software:
Robo-Tank and Leviathan. Commercial all-in-one controllers are listed at the end
for scale.

## Overview

| | aquaPCB v1 | Robo-Tank Deluxe | Leviathan | reef-pi HAT (cadlab) |
|---|---|---|---|---|
| Status | layout done, no prototype | selling (robo-tank.ca) | sold on Tindie | open design |
| Price | ~€35/board at batch 5, ~€27 at 10 (self-built) | $209.95 complete kit, $129.95 DIY kit | older Kickstarter: board from $14, kits from $117 | parts only |
| Assembly | SMD by PCB fab, THT hand-soldered | assembled or DIY kit | assembled / bare "Kraken" | DIY |
| Pi | Zero 2 W on board, Pi 3/4 via ribbon | any 40-pin Pi as a shield | external, via header | HAT |
| Load outputs | 6x 5 A MOSFET, 12 V direct, 2 with HW PWM | 7 DC + 7 LED PWM (0-5 V), PCA9685 | 4 light + 4 dosing (12 V) | 12 PWM via PCA9685 |
| Mains | external SSRs via 4 sink outputs | 2x DB9 power bar ports, 16 outlets | 12 GPIO outlets via relay boards | 8 relay drivers (ULN2803) |
| 0-10 V dimming | planned add-on | yes (Equipment Extension, 8 ports) | no | no |
| pH | on-board, non-isolated, ADS1115 | isolated pH circuit ($54.95) | external interface over I²C | 2 I²C pH ports |
| Temperature | 1-Wire terminal (several sensors) | 2x DS18B20 ports | 3 channels | 3x DS18B20 |
| Inputs | 4 protected digital | 6 sensor ports (RJ45) | 2 float + 2 optical level | 2 ATO |
| RTC | no | battery-backed | no | no |
| Connectors | push-in terminals | RJ45 / DB9 plug-in cables | JST + headers | various |
| Software | aquaPi (all ports auto-detected) | reef-pi + Robo-Tank web app | reef-pi | reef-pi |
| Pinout published | yes (README) | no | no | yes (design files) |
| Licence | open hardware, CERN-OHL-S v2 | closed | closed | open |

## What aquaPi needs to run on the others

Robo-Tank and Leviathan are plain GPIO/I²C/1-Wire hardware, so aquaPi detects
most of it already: outlets, sensor inputs and DS18B20 work today. What's
missing is a **PCA9685 driver**; without it the lights and DC pumps on both
boards can't be driven. Robo-Tank's pH circuit and RTC still need checking.
Neither manufacturer publishes a pinout - get it from their manuals or by
measuring a board, never by guessing.

## Where aquaPCB is stronger

- **Cost.** About €35 per board at batch 5, against $130-210 for a Robo-Tank kit.
- **Drives 12 V loads directly.** Six 5 A MOSFET outputs for LED lamps, fans and
  DC pumps, no extra driver board.
- **Safe boot.** Outputs sit on GPIOs that default to pull-down, so nothing
  switches on while the Pi boots.
- **Open.** Pin map in the README, design files under CERN-OHL-S v2.
- **No cloud, no subscription.** Like aquaPi itself, everything runs locally.

## Where the others are stronger

- **Available now.** Robo-Tank is shipping; aquaPCB has no prototype yet.
- **Plug-in wiring.** Robo-Tank uses RJ45 and DB9 cables and ready-made power
  bars - less screwdriver work than push-in terminals.
- **0-10 V dimming** for commercial lamps (Robo-Tank Equipment Extension);
  aquaPCB plans it as an add-on board.
- **Isolated pH.** Robo-Tank sells an isolated pH circuit. aquaPCB's pH input is
  deliberately non-isolated, matching a hand-built setup whose probe lasted
  over two years, but it is a point buyers compare.
- **Real-time clock.** Robo-Tank keeps the time after a reboot without internet;
  aquaPCB relies on network time.
- **Accessory ecosystem.** Power bars, sensor extensions and cables from the
  same shop.

## Two ways to grow aquaPi's user base

- **aquaPi on existing boards** - easiest for people who already own a
  Robo-Tank or Leviathan and use reef-pi: needs the PCA9685 driver and a board
  profile per board (see aquaPi's ROADMAP.md, "Board support").
- **aquaPCB for new users** - a cheap, open board with a documented pin map,
  so aquaPi can ship a ready-made profile for it.

## Commercial controllers for scale

Neptune Apex A3 Pro ~1,100-1,250 CAD (system), GHL ProfiLux 4.1 ~620 EUR (base
unit), Hydros Control X4 ~450 USD (starter pack), JBL ProFlora CO2 Control
~275-300 EUR (CO2 only). Details and sources in aquaPi's
[COMPARISON.md](https://github.com/schwabix-1311/aquaPI/blob/main/COMPARISON.md).

## Sources

- [Robo-Tank shop](https://www.robo-tank.ca/)
- [Robo-Tank Deluxe Complete Kit](https://www.robo-tank.ca/Reef-pi-Deluxe-Aquarium-Controller-Complete-Kit)
- [Robo-Tank DIY kits](https://www.robo-tank.ca/Reef-pi-DIY-Hardware)
- [reef2reef: Robo-Tank, adding other I²C sensors](https://www.reef2reef.com/threads/robo-tank-w-reefpi-adding-other-i2c-sensors.834813/)
- [Leviathan board on Tindie](https://www.tindie.com/products/schreiber/leviathan-aquarium-automation-reef-pi-board-2)
- [Leviathan, reefs.com](https://reefs.com/leviathan-affordable-aquarium-automation/)
- [Open reef-pi HAT on cadlab.io](https://cadlab.io/project/1832/master/files/v2)
- [reef-pi drivers](https://github.com/reef-pi/drivers)
