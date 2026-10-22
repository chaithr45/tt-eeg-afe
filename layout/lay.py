"""Scripted Magic layout for the neonatal EEG front-end (SKY130, Tiny Tapeout 1x2 analog tile).

Coordinates in the Python code are in micrometres; Magic's internal unit is 0.005 um
(magscale 1 2), so every coordinate is rounded to the 5 nm grid.

Workflow (see build.py):
  1. gen_devices(): the SKY130 device generator (open_pdks) draws every transistor, resistor
     and MIM capacitor as its own cell (guard rings included); cells are saved in mag/.
  2. Python reads the generated cells (magparse.py), knows where every terminal's metal is,
     and writes a Tcl script that places the devices and draws the wiring for each block.
  3. Magic runs DRC and extraction; Netgen compares the extracted netlist with the
     Xschem schematic netlist (LVS).
"""
import os, re, subprocess
from magparse import Mag, region, bbox_of, M1COV, LICOV

HERE = os.path.dirname(os.path.abspath(__file__))
MAGDIR = os.path.join(HERE, '..', 'mag')
PDK_ROOT = os.environ.get('PDK_ROOT', '/home/claude/pdks')
MAGICRC = os.path.join(PDK_ROOT, 'sky130A', 'libs.tech', 'magic', 'sky130A.magicrc')
MAGIC = os.environ.get('MAGIC', 'magic')
U = 200                       # internal units per um

def q(v):
    """um -> internal units (integer, 5 nm grid)."""
    return int(round(v * U))

def run_magic(tcl, name='run', cwd=None):
    cwd = cwd or MAGDIR
    fn = os.path.join(cwd, f'_{name}.tcl')
    open(fn, 'w').write(tcl + '\nquit -noprompt\n')
    r = subprocess.run([MAGIC, '-dnull', '-noconsole', '-rcfile', MAGICRC, fn],
                       capture_output=True, text=True, cwd=cwd, timeout=3600)
    open(os.path.join(cwd, f'_{name}.log'), 'w').write(r.stdout + r.stderr)
    return r.stdout + r.stderr

# ------------------------------------------------------------------ devices
DEVICES = {}   # name -> (generator, params)

def device(name, gen, **params):
    DEVICES[name] = (gen, params)
    return name

def gen_devices(names=None):
    """Draw the listed devices with the SKY130 generator and save them as mag/<name>.mag."""
    lines = []
    for name, (gen, params) in DEVICES.items():
        if names and name not in names:
            continue
        args = ' '.join(f'{k} {v}' for k, v in params.items())
        lines.append(f'set g [magic::gencell_makecell sky130::sky130_fd_pr__{gen} {args}]')
        lines.append(f'cellname rename $g {name}')
        if gen.startswith('res_xhigh_po'):
            # The generated URPM implant is only 0.75 um wide for a 0.35 um resistor (rule rpm.1
            # wants >= 1.27 um): widen it with a mask hint covering body + contacts.
            ylen = params['l'] / 2 + 2.16 + 0.2
            lines.append(f'load {name}')
            lines.append(f'property MASKHINTS_URPM "{-130} {-q(ylen)} {130} {q(ylen)}"')
    lines.append('writeall force')
    return run_magic('\n'.join(lines), 'gen_devices')

class DevGeom:
    """Terminal geometry of a generated device cell (device-local um)."""
    def __init__(self, name):
        self.name = name
        self.mag = Mag(os.path.join(MAGDIR, name + '.mag'))
        b = self.mag.bbox()
        self.bbox = tuple(v / U for v in b)
        self.terms = {}            # label -> list of bbox (um) of the connected metal1 (or li) region
        for lay, x1, y1, x2, y2, text in self.mag.labels:
            reg = region(self.mag, M1COV, x1, y1)
            kind = 'm1'
            if not reg:
                reg = region(self.mag, LICOV, x1, y1); kind = 'li'
            if not reg and lay in ('metal3', 'via3', 'metal4', 'mimcapcontact'):
                reg = region(self.mag, ('metal4', 'mimcapcontact', 'via3'), x1, y1); kind = 'm4'
            bb = tuple(v / U for v in bbox_of(reg)) if reg else (x1 / U, y1 / U, x2 / U, y2 / U)
            self.terms.setdefault(text, []).append((kind, bb, [tuple(v / U for v in r) for r in reg]))

    def sd_cols(self):
        """All source/drain contact columns (metal1 bbox), sorted left to right. Column 0 is a
        drain, then they alternate D, S, D, ... (the generator's D0, S1, D2 ... labels)."""
        cols = {}
        for lay in ('ndiffc', 'pdiffc'):
            for r in self.mag.rects.get(lay, []):
                reg = region(self.mag, M1COV, (r[0] + r[2]) // 2, (r[1] + r[3]) // 2)
                if reg:
                    bb = bbox_of(reg)
                    cols[bb] = tuple(v / U for v in bb)
        return sorted(cols.values())

    def cols(self, kind):
        """'D' (even columns) or 'S' (odd columns)."""
        c = self.sd_cols()
        return c[0::2] if kind == 'D' else c[1::2]

# ------------------------------------------------------------------ cells
class Cell:
    def __init__(self, name):
        self.name = name
        self.tcl = [f'cellname delete {name}', f'cellname create {name}', f'edit', f'load {name}', 'snap internal',
                    'box 0 0 0 0']
        self.insts = {}

    def rect(self, layer, x1, y1, x2, y2):
        a, b, c, d = q(min(x1, x2)), q(min(y1, y2)), q(max(x1, x2)), q(max(y1, y2))
        if c <= a or d <= b:
            return
        self.tcl.append(f'box {a} {b} {c} {d}; paint {layer}')

    def erase(self, layer, x1, y1, x2, y2):
        self.tcl.append(f'box {q(x1)} {q(y1)} {q(x2)} {q(y2)}; erase {layer}')

    def place(self, cellname, inst, x, y, orient=''):
        """Place a cell with its origin at (x, y). orient: '' | 'h' (mirror x) | 'v' (mirror y) | '180'."""
        o = {'': '', 'h': 'h', 'v': 'v', '180': '180'}[orient]
        self.tcl.append(f'box {q(x)} {q(y)} {q(x)} {q(y)}; getcell {cellname} {o} child 0 0; identify {inst}')
        self.insts[inst] = (cellname, x, y, orient)
        return Placed(cellname, x, y, orient)

    def label(self, name, layer, x1, y1, x2=None, y2=None, port=None, use=None):
        x2 = x1 if x2 is None else x2; y2 = y1 if y2 is None else y2
        self.tcl.append(f'box {q(x1)} {q(y1)} {q(x2)} {q(y2)}; label {name} FreeSans {q(0.2)} 0 0 0 c {layer}')
        if port is not None:
            self.tcl.append(f'port make {port}')
            if use:
                self.tcl.append(f'port use {use}')

    # --- wiring primitives (sizes chosen for SKY130 rules, checked by Magic DRC)
    def via1(self, x, y):           # metal1 <-> metal2
        self.rect('metal1', x - .16, y - .16, x + .16, y + .16)
        self.rect('metal2', x - .16, y - .16, x + .16, y + .16)
        self.rect('via1', x - .13, y - .13, x + .13, y + .13)

    def via2(self, x, y):           # metal2 <-> metal3
        self.rect('metal2', x - .21, y - .21, x + .21, y + .21)
        self.rect('metal3', x - .25, y - .25, x + .25, y + .25)
        self.rect('via2', x - .16, y - .16, x + .16, y + .16)

    def via3(self, x, y):           # metal3 <-> metal4
        self.rect('metal3', x - .25, y - .25, x + .25, y + .25)
        self.rect('metal4', x - .25, y - .25, x + .25, y + .25)
        self.rect('via3', x - .16, y - .16, x + .16, y + .16)

    def mcon(self, x, y):           # li <-> metal1
        self.rect('locali', x - .125, y - .125, x + .125, y + .125)
        self.rect('metal1', x - .145, y - .145, x + .145, y + .145)
        self.rect('viali', x - .085, y - .085, x + .085, y + .085)

    def stack(self, x, y, frm, to):
        """Via stack between layers named 'li','m1','m2','m3','m4'."""
        order = ['li', 'm1', 'm2', 'm3', 'm4']
        a, b = sorted((order.index(frm), order.index(to)))
        for i in range(a, b):
            [self.mcon, self.via1, self.via2, self.via3][i](x, y)

    def wire(self, layer, pts, w):
        """Manhattan wire through points (x, y), width w (um); segment ends extended by w/2."""
        h = w / 2
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if abs(x1 - x2) > 1e-9 and abs(y1 - y2) > 1e-9:
                raise ValueError(f'non-Manhattan segment {(x1, y1)} -> {(x2, y2)}')
            self.rect(layer, min(x1, x2) - h, min(y1, y2) - h, max(x1, x2) + h, max(y1, y2) + h)

    def save_tcl(self):
        return '\n'.join(self.tcl + ['select top cell', 'save ' + self.name])


class Placed:
    """A placed device: transforms device-local terminal geometry to cell coordinates."""
    def __init__(self, cellname, x, y, orient):
        self.cellname, self.x, self.y, self.o = cellname, x, y, orient
        self.g = DevGeom(cellname)

    def tb(self, b):
        x1, y1, x2, y2 = b
        if self.o == 'h':
            x1, x2 = -x2, -x1
        elif self.o == 'v':
            y1, y2 = -y2, -y1
        elif self.o == '180':
            x1, y1, x2, y2 = -x2, -y2, -x1, -y1
        return (x1 + self.x, y1 + self.y, x2 + self.x, y2 + self.y)

    def term(self, label, i=0):
        return self.tb(self.g.terms[label][i][1])

    def cols(self, prefix):
        return sorted(self.tb(b) for b in self.g.cols(prefix))

    @property
    def bbox(self):
        return self.tb(self.g.bbox)

    def guard(self):
        """Guard-ring (bulk) li ring rects in cell coordinates."""
        return [self.tb(r) for r in self.g.terms['B'][0][2]]


def drc_tcl(cell):
    return '\n'.join([f'load {cell}', 'select top cell', 'drc euclidean on', 'drc style drc(full)', 'drc check', 'drc catchup',
                      'set n [drc list count total]', 'puts "DRC_TOTAL $n"',
                      'foreach {why boxes} [drc listall why] { puts "DRC_WHY [llength $boxes] $why : [lrange $boxes 0 2]"; foreach b $boxes { puts "DRC_BOX $why : $b" } }'])

def extract_tcl(cell, pex=False):
    lines = [f'load {cell}', 'select top cell', 'extract do local', 'extract all']
    if pex:
        lines += ['ext2spice lvs', 'ext2spice cthresh 0', 'ext2spice rthresh 0', f'ext2spice -o {cell}_pex.spice']
    else:
        lines += ['ext2spice lvs', f'ext2spice -o {cell}_lvs.spice']
    return '\n'.join(lines)

def drc(cell):
    out = run_magic(drc_tcl(cell), f'drc_{cell}')
    n = re.search(r'DRC_TOTAL (\d+)', out)
    whys = [l for l in out.splitlines() if l.startswith('DRC_WHY')]
    return (int(n.group(1)) if n else -1), whys

def lvs(cell, schem_netlist, schem_cell=None):
    run_magic(extract_tcl(cell), f'ext_{cell}')
    setup = os.path.join(PDK_ROOT, 'sky130A', 'libs.tech', 'netgen', 'sky130A_setup.tcl')
    log = os.path.join(MAGDIR, f'lvs_{cell}.log')
    r = subprocess.run(['netgen', '-batch', 'lvs', f'{cell}_lvs.spice {cell}', f'{schem_netlist} {schem_cell or cell}',
                        setup, log], capture_output=True, text=True, cwd=MAGDIR, timeout=3600)
    txt = open(log).read() if os.path.exists(log) else r.stdout
    ok = 'Circuits match uniquely' in txt and 'Final result: Circuits match uniquely' in txt or \
         re.search(r'Final result:\s+Circuits match uniquely', txt) is not None
    return ok, txt


def cell_bbox(cells):
    """Bounding boxes (um) of saved cells, measured by Magic."""
    lines = []
    for c in cells:
        lines += [f'load {c}', 'select top cell', f'puts "BBOX {c} [box values]"']
    out = run_magic('\n'.join(lines), 'bbox')
    res = {}
    for l in out.splitlines():
        if l.startswith('BBOX'):
            p = l.split()
            res[p[1]] = tuple(int(v) / U for v in p[2:6])
    return res
