"""Minimal KiCad schematic writer used to generate the first aquaPCB schematic draft.

Symbols are copied from the installed KiCad libraries and embedded into the
schematic. Every pin gets a short wire stub ending in a power symbol, a net label
or a no-connect flag, so connectivity is defined purely by net names and can be
checked with `kicad-cli sch erc`.

Files are written in KiCad 8 syntax (version 20231120); run
`kicad-cli sch upgrade` afterwards to convert to the installed version.
"""
import math
import re
import uuid as _uuid

SYMDIR = '/usr/share/kicad/symbols'
GRID = 1.27
STUB = 2.54
FONT = 1.27
POWER_NETS = {'GND': 'power:GND', '+5V': 'power:+5V', '+3V3': 'power:+3V3', 'VIN': 'power:+VDC'}
NC = None   # net value for "no connect"

_TOK = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')


def parse(txt):
    stack = [[]]
    for m in _TOK.finditer(txt):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            e = stack.pop()
            stack[-1].append(e)
        else:
            stack[-1].append(t)
    return stack[0][0]


def unq(s):
    return s[1:-1].replace('\\"', '"').replace('\\\\', '\\') if isinstance(s, str) and s.startswith('"') else s


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def dump(e, ind=0):
    if not isinstance(e, list):
        return e
    head = []
    for x in e:
        if isinstance(x, list):
            break
        head.append(x)
    s = '(' + ' '.join(head)
    for x in e[len(head):]:
        s += ('\n' + '\t' * (ind + 1) + dump(x, ind + 1)) if isinstance(x, list) else ' ' + x
    return s + ')'


def uid():
    return str(_uuid.uuid4())


def snap(v):
    return round(v / GRID) * GRID


def fmt(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.')


# ---------------------------------------------------------------- symbol library

_libs = {}


def _lib(name):
    if name not in _libs:
        with open(f'{SYMDIR}/{name}.kicad_sym', encoding='utf-8') as f:
            _libs[name] = parse(f.read())
    return _libs[name]


def _raw_symbol(lib, name):
    for e in _lib(lib):
        if isinstance(e, list) and e[0] == 'symbol' and unq(e[1]) == name:
            return e
    raise KeyError(f'{lib}:{name}')


class LibSymbol:
    """A library symbol, flattened (no `extends`), ready to embed."""
    _cache = {}

    @classmethod
    def get(cls, lib_id):
        if lib_id not in cls._cache:
            cls._cache[lib_id] = cls(lib_id)
        return cls._cache[lib_id]

    def __init__(self, lib_id):
        self.lib_id = lib_id
        lib, name = lib_id.split(':')
        sym = _raw_symbol(lib, name)
        ext = [x for x in sym if isinstance(x, list) and x[0] == 'extends']
        if ext:
            parent_name = unq(ext[0][1])
            parent = _raw_symbol(lib, parent_name)
            child_props = {unq(x[1]): x for x in sym if isinstance(x, list) and x[0] == 'property'}
            body = []
            for x in parent[2:]:
                if isinstance(x, list) and x[0] == 'property' and unq(x[1]) in child_props:
                    body.append(child_props.pop(unq(x[1])))
                elif isinstance(x, list) and x[0] == 'symbol':
                    body.append(self._rename(x, parent_name, name))
                else:
                    body.append(x)
            body[1:1] = list(child_props.values())
            sym = ['symbol', q(name)] + body
        self.expr = ['symbol', q(lib_id)] + [x for x in sym[2:] if not (isinstance(x, list) and x[0] == 'extends')]
        self.props = {unq(x[1]): unq(x[2]) for x in self.expr if isinstance(x, list) and x[0] == 'property'}
        self.is_power = any(x == ['power'] or (isinstance(x, list) and x[:1] == ['power']) for x in self.expr)
        self.pins = []
        self._collect(self.expr, 0)
        self.units = sorted({p['unit'] for p in self.pins if p['unit']}) or [1]

    @staticmethod
    def _rename(e, old, new):
        e = list(e)
        e[1] = q(unq(e[1]).replace(old + '_', new + '_', 1))
        return e

    def _collect(self, e, unit):
        for x in e:
            if not isinstance(x, list):
                continue
            if x[0] == 'symbol':
                m = re.search(r'_(\d+)_(\d+)$', unq(x[1]))
                self._collect(x, int(m.group(1)) if m else unit)
            elif x[0] == 'pin':
                at = next(y for y in x if isinstance(y, list) and y[0] == 'at')
                ln = next(y for y in x if isinstance(y, list) and y[0] == 'length')
                nm = next(y for y in x if isinstance(y, list) and y[0] == 'name')
                nu = next(y for y in x if isinstance(y, list) and y[0] == 'number')
                self.pins.append(dict(unit=unit, type=x[1], num=unq(nu[1]), name=unq(nm[1]),
                                      x=float(at[1]), y=float(at[2]), rot=float(at[3]), len=float(ln[1])))

    def unit_pins(self, unit):
        return [p for p in self.pins if p['unit'] in (0, unit)]


# ---------------------------------------------------------------- geometry

def xform(x, y, rot):
    """library coordinates (y up) -> schematic offset (y down), rotated CCW by rot."""
    vx, vy = x, -y
    a = math.radians(rot)
    c, s = round(math.cos(a)), round(math.sin(a))
    return vx * c + vy * s, -vx * s + vy * c


def pin_geometry(p, rot):
    """connection point offset and outward unit vector of a pin."""
    px, py = xform(p['x'], p['y'], rot)
    a = math.radians(p['rot'])
    ix, iy = xform(math.cos(a), math.sin(a), rot)   # direction towards the body
    return (px, py), (-round(ix), -round(iy))


# ---------------------------------------------------------------- schematic

class Project:
    def __init__(self, name):
        self.name = name
        self.root_uuid = uid()
        self.sheets = []
        self.counters = {}
        self.pwr_count = 0

    def next_ref(self, prefix):
        self.counters[prefix] = self.counters.get(prefix, 0) + 1
        return f'{prefix}{self.counters[prefix]}'

    def next_pwr(self):
        self.pwr_count += 1
        return f'#PWR{self.pwr_count:03d}'

    def sheet(self, name, filename, title):
        s = Sheet(self, name, filename, title)
        self.sheets.append(s)
        return s

    def net_sheets(self):
        use = {}
        for s in self.sheets:
            for n in s.nets:
                use.setdefault(n, set()).add(s.name)
        return use

    def write(self, outdir, title, rev, date):
        use = self.net_sheets()
        for s in self.sheets:
            s.write(f'{outdir}/{s.filename}', use, title, rev, date)
        self._write_root(f'{outdir}/{self.name}.kicad_sch', title, rev, date)

    def _write_root(self, path, title, rev, date):
        items = []
        x0, y0, w, h = 30.48, 38.1, 55.88, 17.78
        for i, s in enumerate(self.sheets):
            x = x0 + (i % 3) * (w + 20.32)
            y = y0 + (i // 3) * (h + 20.32)
            items.append(['sheet', ['at', fmt(x), fmt(y)], ['size', fmt(w), fmt(h)], ['fields_autoplaced', 'yes'],
                          ['stroke', ['width', '0.1524'], ['type', 'solid']], ['fill', ['color', '0', '0', '0', '0.0000']],
                          ['uuid', q(s.uuid)],
                          ['property', q('Sheetname'), q(s.title), ['at', fmt(x), fmt(y - 0.7116), '0'],
                           ['effects', ['font', ['size', '1.27', '1.27']], ['justify', 'left', 'bottom']]],
                          ['property', q('Sheetfile'), q(s.filename), ['at', fmt(x), fmt(y + h + 0.5884), '0'],
                           ['effects', ['font', ['size', '1.27', '1.27']], ['justify', 'left', 'top']]],
                          ['instances', ['project', q(self.name),
                                         ['path', q('/' + self.root_uuid), ['page', q(str(i + 2))]]]]])
        doc = ['kicad_sch', ['version', '20231120'], ['generator', q('eeschema')], ['generator_version', q('8.0')],
               ['uuid', q(self.root_uuid)], ['paper', q('A4')], _title_block(title, rev, date, 'Overview'),
               ['lib_symbols']] + items + [
            ['text', q('aquaPCB – Raspberry Pi base board for aquaPi\n'
                       'Draft generated by tools/gen_schematic.py; once edited in eeschema, the\n'
                       '.kicad_sch files are the source of truth.'),
             ['exclude_from_sim', 'no'], ['at', '30.48', '25.4', '0'],
             ['effects', ['font', ['size', '2', '2']], ['justify', 'left', 'bottom']], ['uuid', q(uid())]],
            ['sheet_instances', ['path', q('/'), ['page', q('1')]]]]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(dump(doc) + '\n')


def _title_block(title, rev, date, sheet_title):
    return ['title_block', ['title', q(f'{title} – {sheet_title}')], ['date', q(date)], ['rev', q(rev)],
            ['company', q('aquaPi project')],
            ['comment', '1', q('CERN-OHL-S-2.0')]]


class Part:
    def __init__(self, sheet, lib_id, ref, value, nets, fp='', lcsc='', rot=0, fields=None, units=None):
        self.sheet = sheet
        self.sym = LibSymbol.get(lib_id)
        self.lib_id = lib_id
        self.ref = ref
        self.value = value
        self.nets = nets            # pin number -> net name, or NC
        self.fp = fp or self.sym.props.get('Footprint', '')
        self.fields = dict(fields or {})
        if lcsc:
            self.fields['LCSC'] = lcsc
        self.rot = rot
        self.units = units or self.sym.units
        missing = [p['num'] for p in self.sym.pins if p['unit'] in [0] + list(self.units) and p['num'] not in nets]
        if missing:
            raise ValueError(f'{ref} ({lib_id}): unassigned pins {missing}')
        extra = set(nets) - {p['num'] for p in self.sym.pins}
        if extra:
            raise ValueError(f'{ref} ({lib_id}): unknown pins {sorted(extra)}')

    def unit_extent(self, unit):
        """bounding box (relative) incl. stubs and label text."""
        xs, ys = [0.0], [0.0]
        for p in self.sym.unit_pins(unit):
            (px, py), (dx, dy) = pin_geometry(p, self.rot)
            net = self.nets[p['num']]
            ln = STUB + (len(net) * 0.85 * FONT + 2.54 if net and net not in POWER_NETS else 5.08)
            xs += [px, px + dx * ln]
            ys += [py, py + dy * ln]
            ix, iy = -dx, -dy
            xs.append(px + ix * p['len'] + ix * 2.54)
            ys.append(py + iy * p['len'] + iy * 2.54)
        return min(xs), min(ys), max(xs), max(ys)


class Sheet:
    def __init__(self, project, name, filename, title):
        self.project = project
        self.name = name
        self.filename = filename
        self.title = title
        self.uuid = uid()
        self.file_uuid = uid()
        self.placed = []            # (part, unit, x, y)
        self.texts = []
        self.nets = set()
        self.flags = []             # nets that get a PWR_FLAG
        self.cursor_y = 30.48
        self.left = 25.4

    # -- placement helpers
    def part(self, lib_id, prefix, value, nets, **kw):
        ref = kw.pop('ref', None) or self.project.next_ref(prefix)
        return Part(self, lib_id, ref, value, nets, **kw)

    def row(self, items, gap=7.62, heading=None):
        """place a row of parts (or (part, unit) tuples) left to right."""
        if heading:
            self.note(heading, 1.8)
        boxes = []
        for it in items:
            part, unit = it if isinstance(it, tuple) else (it, None)
            for u in ([unit] if unit else part.units):
                boxes.append((part, u, part.unit_extent(u)))
        height = max(b[2][3] - b[2][1] for b in boxes)
        top = self.cursor_y
        x = self.left
        for part, u, (x0, y0, x1, y1) in boxes:
            ox = snap(x - x0)
            oy = snap(top - y0 + (height - (y1 - y0)) / 2)
            self.placed.append((part, u, ox, oy))
            for p in part.sym.unit_pins(u):
                n = part.nets[p['num']]
                if n:
                    self.nets.add(n)
            x = ox + x1 + gap
        self.cursor_y = snap(top + height + 7.62)

    def note(self, text, size=1.27):
        """text block, top-left anchored at the cursor; advances the cursor below it."""
        self.texts.append((text, self.left, self.cursor_y, size))
        self.cursor_y = snap(self.cursor_y + size * 1.7 * (text.count('\n') + 1) + 3.81)

    def pwr_flag(self, net):
        self.flags.append(net)
        self.nets.add(net)

    # -- output
    def write(self, path, net_use, title, rev, date):
        proj = self.project
        items = []
        lib_ids = {}

        def need(lib_id):
            lib_ids[lib_id] = LibSymbol.get(lib_id)

        def inst_path():
            return q(f'/{proj.root_uuid}/{self.uuid}')

        def power_symbol(net, x, y, d):
            lib_id = POWER_NETS[net]
            need(lib_id)
            sym = LibSymbol.get(lib_id)
            # power symbols point "up" (body above pin) except GND (body below)
            natural = (0, 1) if net == 'GND' else (0, -1)
            rot = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}
            r = (rot[d] - rot[natural]) % 360
            ref = proj.next_pwr()
            items.append(_symbol_instance(sym, lib_id, ref, net, x, y, r, 1, '', {}, inst_path(), proj.name,
                                          hide_ref=True))

        def pin_end(net, x, y, d):
            ex, ey = x + d[0] * STUB, y + d[1] * STUB
            items.append(['wire', ['pts', ['xy', fmt(x), fmt(y)], ['xy', fmt(ex), fmt(ey)]],
                          ['stroke', ['width', '0'], ['type', 'default']], ['uuid', q(uid())]])
            if net in POWER_NETS:
                power_symbol(net, ex, ey, d)
            else:
                angle = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[d]
                glob = len(net_use.get(net, ())) > 1
                just = 'right' if angle in (180, 270) else 'left'
                if glob:
                    items.append(['global_label', q(net), ['shape', 'bidirectional'],
                                  ['at', fmt(ex), fmt(ey), str(angle)], ['fields_autoplaced', 'yes'],
                                  ['effects', ['font', ['size', '1.27', '1.27']], ['justify', just]],
                                  ['uuid', q(uid())],
                                  ['property', q('Intersheetrefs'), q('${INTERSHEET_REFS}'),
                                   ['at', fmt(ex), fmt(ey), '0'],
                                   ['effects', ['font', ['size', '1.27', '1.27']], ['hide', 'yes']]]])
                else:
                    items.append(['label', q(net), ['at', fmt(ex), fmt(ey), str(angle)], ['fields_autoplaced', 'yes'],
                                  ['effects', ['font', ['size', '1.27', '1.27']], ['justify', just, 'bottom']],
                                  ['uuid', q(uid())]])

        for part, unit, ox, oy in self.placed:
            need(part.lib_id)
            items.append(_symbol_instance(part.sym, part.lib_id, part.ref, part.value, ox, oy, part.rot, unit,
                                          part.fp, part.fields, inst_path(), proj.name))
            for p in part.sym.unit_pins(unit):
                (px, py), d = pin_geometry(p, part.rot)
                x, y = ox + px, oy + py
                net = part.nets[p['num']]
                if net is NC:
                    items.append(['no_connect', ['at', fmt(x), fmt(y)], ['uuid', q(uid())]])
                else:
                    pin_end(net, x, y, d)

        fx = self.left
        fy = self.cursor_y + 5.08
        for net in self.flags:
            need('power:PWR_FLAG')
            sym = LibSymbol.get('power:PWR_FLAG')
            ref = f'#FLG{proj.next_pwr()[4:]}'
            items.append(_symbol_instance(sym, 'power:PWR_FLAG', ref, 'PWR_FLAG', fx, fy, 0, 1, '', {}, inst_path(),
                                          proj.name, hide_ref=True))
            pin_end(net, fx, fy, (0, 1))
            fx += 15.24

        for text, x, y, size in self.texts:
            items.append(['text', q(text), ['exclude_from_sim', 'no'], ['at', fmt(x), fmt(y), '0'],
                          ['effects', ['font', ['size', fmt(size), fmt(size)]], ['justify', 'left', 'top']],
                          ['uuid', q(uid())]])

        doc = ['kicad_sch', ['version', '20231120'], ['generator', q('eeschema')], ['generator_version', q('8.0')],
               ['uuid', q(self.file_uuid)], ['paper', q('A3')], _title_block(title, rev, date, self.title),
               ['lib_symbols'] + [s.expr for s in lib_ids.values()]] + items
        with open(path, 'w', encoding='utf-8') as f:
            f.write(dump(doc) + '\n')


def _symbol_instance(sym, lib_id, ref, value, x, y, rot, unit, fp, fields, path, project, hide_ref=False):
    xs = [xform(p['x'], p['y'], rot) for p in sym.unit_pins(unit)] or [(0, 0)]
    top = min(p[1] for p in xs) - 2.54
    bottom = max(p[1] for p in xs) + 2.54
    cx = x + (min(p[0] for p in xs) + max(p[0] for p in xs)) / 2

    def prop(name, val, px, py, hide=False, just=None):
        eff = ['effects', ['font', ['size', '1.27', '1.27']]]
        if just:
            eff.append(['justify', just])
        if hide:
            eff.append(['hide', 'yes'])
        return ['property', q(name), q(val), ['at', fmt(px), fmt(py), '0'], eff]

    e = ['symbol', ['lib_id', q(lib_id)], ['at', fmt(x), fmt(y), fmt(rot)], ['unit', str(unit)],
         ['exclude_from_sim', 'no'], ['in_bom', 'no' if ref.startswith('#') else 'yes'],
         ['on_board', 'no' if ref.startswith('#') else 'yes'], ['dnp', 'no'], ['uuid', q(uid())],
         prop('Reference', ref, cx, y + top, hide=hide_ref),
         prop('Value', value, cx, y + bottom),
         prop('Footprint', fp, x, y, hide=True),
         prop('Datasheet', sym.props.get('Datasheet', ''), x, y, hide=True),
         prop('Description', sym.props.get('Description', ''), x, y, hide=True)]
    for k, v in fields.items():
        e.append(prop(k, v, x, y, hide=True))
    for p in sym.unit_pins(unit):
        e.append(['pin', q(p['num']), ['uuid', q(uid())]])
    e.append(['instances', ['project', q(project), ['path', path, ['reference', q(ref)], ['unit', str(unit)]]]])
    return e
