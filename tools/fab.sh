#!/usr/bin/env bash
# Build JLCPCB fabrication outputs for aquaPCB into fab/ (needs kicad-cli 10 and python3).
# usage: tools/fab.sh            -> fab/gerbers/*, fab/aquaPCB-gerbers.zip, fab/aquaPCB-bom-jlc.csv,
#                                   fab/aquaPCB-cpl-jlc.csv, fab/aquaPCB-print-1to1.pdf
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); K="$ROOT/kicad"; OUT="$ROOT/fab"; PCB="$K/aquaPCB.kicad_pcb"; SCH="$K/aquaPCB.kicad_sch"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
rm -rf "$OUT"; mkdir -p "$OUT/gerbers"

# 1) checks: ERC and DRC must be free of errors (warnings are reported, not fatal)
kicad-cli sch erc --severity-error --exit-code-violations -o "$TMP/erc.rpt" "$SCH" >/dev/null || { echo "ERC errors, see $TMP/erc.rpt"; cat "$TMP/erc.rpt"; exit 1; }
kicad-cli pcb drc --refill-zones --schematic-parity --severity-error --exit-code-violations -o "$TMP/drc.rpt" "$PCB" >/dev/null \
  || { echo "DRC errors:"; cat "$TMP/drc.rpt"; exit 1; }

# 2) Gerbers (JLCPCB: Protel extensions, no X2/netlist, soldermask subtracted from silkscreen) + Excellon drill
kicad-cli pcb export gerbers --check-zones --no-x2 --no-netlist --subtract-soldermask \
  --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts -o "$OUT/gerbers/" "$PCB" >/dev/null
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-zeros-format decimal \
  --excellon-oval-format alternate --excellon-separate-th --generate-map --map-format pdf -o "$OUT/gerbers/" "$PCB" >/dev/null
(cd "$OUT/gerbers" && zip -q -j "$OUT/aquaPCB-gerbers.zip" ./*.g?? ./*.gm1 ./*.drl)

# 3) assembly: CPL (SMD only, no DNP) and the matching JLC BOM
kicad-cli pcb export pos --format csv --units mm --side front --smd-only --exclude-dnp -o "$TMP/pos.csv" "$PCB" >/dev/null
kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC' --group-by '' -o "$TMP/bom.csv" "$SCH" >/dev/null
python3 - "$TMP/pos.csv" "$TMP/bom.csv" "$OUT" <<'PY'
import csv, sys, collections
pos, bom, out = sys.argv[1:4]
P = list(csv.DictReader(open(pos)))
fields = {r['Reference']: r for r in csv.DictReader(open(bom))}
with open(f'{out}/aquaPCB-cpl-jlc.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in P: w.writerow([r['Ref'], f"{float(r['PosX']):.4f}mm", f"{float(r['PosY']):.4f}mm", 'Top' if r['Side'] == 'top' else 'Bottom', f"{float(r['Rot']):.1f}"])
groups = collections.OrderedDict(); missing = []
for r in P:
    fr = fields.get(r['Ref'])
    if fr is None or not fr['LCSC']: missing.append(r['Ref']); continue
    key = (fr['Value'], fr['Footprint'].split(':')[-1], fr['LCSC']); groups.setdefault(key, []).append(r['Ref'])
with open(f'{out}/aquaPCB-bom-jlc.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    for (val, fp, lc), refs in groups.items(): w.writerow([val, ','.join(sorted(refs, key=lambda s: (s.rstrip('0123456789'), int(s[len(s.rstrip('0123456789')):] or 0)))), fp, lc])
print(f'CPL {len(P)} parts, BOM {len(groups)} lines' + (f', WITHOUT LCSC: {missing}' if missing else ''))
if missing: sys.exit(1)
PY

# 4) 1:1 print for the footprint check (copper, silk, fab, outline, real drill sizes)
kicad-cli pcb export pdf --layers F.Cu,F.SilkS,F.Fab,Edge.Cuts --mode-single --scale 1 --drill-shape-opt 2 \
  --black-and-white -o "$OUT/aquaPCB-print-1to1.pdf" "$PCB" >/dev/null
echo "fab outputs in $OUT"
