"""Generate the Xschem schematics (.sch) and symbols (.sym) for the neonatal EEG front-end.

Connectivity is made with net labels placed directly on device pins (no hand-drawn wires),
so every schematic is correct by construction. Devices are placed in the same arrangement
as the PDF schematic sheets so they are easy to read; drag them around freely in Xschem.

Run:  python3 gen_schematics.py      (writes *.sch and *.sym next to this script)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VER = 'v {xschem version=3.4.4 file_version=1.2}\n'

# SKY130 primitive symbols and their pin offsets (from xschem_sky130 / open_pdks symbols)
PRIM = {
    'nfet': ('sky130_fd_pr/nfet_01v8.sym', {'D': (20, -30), 'G': (-20, 0), 'S': (20, 30), 'B': (20, 0)}, 'nfet_01v8'),
    'pfet': ('sky130_fd_pr/pfet_01v8.sym', {'D': (20, 30), 'G': (-20, 0), 'S': (20, -30), 'B': (20, 0)}, 'pfet_01v8'),
    'mim':  ('sky130_fd_pr/cap_mim_m3_1.sym', {'c0': (0, -30), 'c1': (0, 30)}, 'cap_mim_m3_1'),
    'rxh':  ('sky130_fd_pr/res_xhigh_po_0p35.sym', {'P': (0, -30), 'M': (0, 30), 'B': (-20, 0)}, 'res_xhigh_po_0p35'),
}

def fmt(v):
    return ('%.6g' % v) if isinstance(v, float) else str(v)

class Cell:
    def __init__(self, name, ports, title, notes=()):
        self.name, self.ports, self.title, self.notes = name, ports, title, list(notes)
        self.lines, self.nlab = [], 0
        self.syms = {}          # hierarchical symbol name -> pin offsets

    def label(self, x, y, net, right):
        self.nlab += 1
        self.lines.append(f'C {{lab_pin.sym}} {fmt(x)} {fmt(y)} 0 {1 if right else 0} {{name=l{self.nlab} sig_type=std_logic lab={net}}}')

    def mos(self, kind, name, x, y, d, g, s, b, W, L, mult=1):
        sym, pins, model = PRIM[kind]
        ad = W * 0.29; pd = 2 * (W + 0.29); nr = 0.29 / W
        attrs = (f'name={name} W={fmt(W)} L={fmt(L)} nf=1 mult={mult} ad={fmt(ad)} as={fmt(ad)} '
                 f'pd={fmt(pd)} ps={fmt(pd)} nrd={fmt(nr)} nrs={fmt(nr)} sa=0 sb=0 sd=0 model={model} spiceprefix=X')
        self.lines.append(f'C {{{sym}}} {x} {y} 0 0 {{{attrs}}}')
        for pin, net in (('D', d), ('G', g), ('S', s), ('B', b)):
            px, py = pins[pin]; self.label(x + px, y + py, net, right=(pin != 'G'))

    def mim(self, name, x, y, c0, c1, W, L, MF=1):
        sym, pins, model = PRIM['mim']
        # model name comes from the tcl variable MIM_MODEL (xschemrc: cap_mim_m3_1 = PDK model, used for LVS;
        # the testbench switches it to cap_mim_m3_1_ideal, an ideal C of the same value, 200x faster in transient)
        self.lines.append(f'C {{{sym}}} {x} {y} 0 0 {{name={name} model=tcleval($::MIM_MODEL) W={fmt(W)} L={fmt(L)} MF={MF} spiceprefix=X}}')
        for pin, net in (('c0', c0), ('c1', c1)):
            px, py = pins[pin]; self.label(x + px, y + py, net, right=True)

    def rxh(self, name, x, y, p, m, b, L, mult=1):
        sym, pins, model = PRIM['rxh']
        self.lines.append(f'C {{{sym}}} {x} {y} 0 0 {{name={name} L={fmt(L)} model={model} spiceprefix=X mult={mult}}}')
        for pin, net in (('P', p), ('M', m), ('B', b)):
            px, py = pins[pin]; self.label(x + px, y + py, net, right=(pin != 'B'))

    def sub(self, symname, name, x, y, conn):
        pins = SUBSYM[symname]['pins']
        self.lines.append(f'C {{{symname}.sym}} {x} {y} 0 0 {{name={name}}}')
        for pin, net in conn.items():
            side, px, py = pins[pin]; self.label(x + px, y + py, net, right=(side == 'R'))

    def text(self, s, x, y, size=0.4):
        s = s.replace('{', '(').replace('}', ')')
        self.lines.append(f'T {{{s}}} {x} {y} 0 0 {size} {size} {{}}')

    def write(self):
        out = [VER, 'G {}', 'K {}', 'V {}', 'S {}', 'E {}']
        y = -620
        out.append(f'T {{{self.title}}} -260 {y} 0 0 0.6 0.6 {{}}')
        for i, n in enumerate(self.notes):
            out.append(f'T {{{n}}} -260 {y + 40 + 25 * i} 0 0 0.3 0.3 {{}}')
        for i, (p, d) in enumerate(self.ports):
            sym = {'in': 'ipin.sym', 'out': 'opin.sym', 'io': 'iopin.sym'}[d]
            out.append(f'C {{{sym}}} -240 {-400 + 40 * i} 0 0 {{name=p{i+1} lab={p}}}')
        out += self.lines
        open(os.path.join(HERE, self.name + '.sch'), 'w').write('\n'.join(out) + '\n')

# ---------------------------------------------------------------- hierarchical symbols
SUBSYM = {}
def make_symbol(name, pins, w=160, h=160, label=None):
    """pins: list of (pin, side, dir) in .subckt order; side L/R/T/B."""
    hw, hh = w // 2, h // 2
    sides = {s: [p for p in pins if p[1] == s] for s in 'LRTB'}
    pos = {}
    for s, plist in sides.items():
        n = len(plist)
        for i, (p, _, d) in enumerate(plist):
            k = (i + 1) * (2 * (hh if s in 'LR' else hw)) // (n + 1) - (hh if s in 'LR' else hw)
            k = int(round(k / 10.0)) * 10
            pos[p] = {'L': ('L', -hw - 20, k), 'R': ('R', hw + 20, k), 'T': ('T', k, -hh - 20), 'B': ('B', k, hh + 20)}[s]
    SUBSYM[name] = {'pins': pos}
    L = [VER, 'G {}', 'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}', 'V {}', 'S {}', 'E {}',
         f'L 4 {-hw} {-hh} {hw} {-hh} {{}}', f'L 4 {hw} {-hh} {hw} {hh} {{}}', f'L 4 {hw} {hh} {-hw} {hh} {{}}', f'L 4 {-hw} {hh} {-hw} {-hh} {{}}']
    for p, side, d in pins:
        s, x, y = pos[p]
        ex, ey = {'L': (-hw, y), 'R': (hw, y), 'T': (x, -hh), 'B': (x, hh)}[s]
        L.append(f'L 7 {x} {y} {ex} {ey} {{}}')
        L.append(f'B 5 {x - 2.5} {y - 2.5} {x + 2.5} {y + 2.5} {{name={p} dir={d}}}')
        tx, ty, hj = {'L': (ex + 5, y - 8, 0), 'R': (ex - 5, y - 8, 1), 'T': (x + 4, ey + 4, 0), 'B': (x + 4, ey - 20, 0)}[s]
        L.append(f'T {{{p}}} {tx} {ty} 0 {hj} 0.25 0.25 {{}}')
    L.append(f'T {{{label or name}}} {-hw + 10} {-12} 0 0 0.35 0.35 {{}}')
    L.append(f'T {{@name}} {-hw} {-hh - 24} 0 0 0.25 0.25 {{}}')
    open(os.path.join(HERE, name + '.sym'), 'w').write('\n'.join(L) + '\n')

make_symbol('ota', [('inn', 'L', 'in'), ('inp', 'L', 'in'), ('out', 'R', 'out'), ('vdd', 'T', 'inout'),
                    ('vss', 'B', 'inout'), ('vbp', 'L', 'in')], label='OTA')
make_symbol('pseudo_r', [('a', 'L', 'inout'), ('b', 'R', 'inout'), ('rst', 'T', 'in'), ('vss', 'B', 'inout')],
            w=120, h=80, label='PR')
make_symbol('afe', [('vin', 'L', 'in'), ('vout', 'R', 'out'), ('vdd', 'T', 'inout'), ('vss', 'B', 'inout'),
                    ('vbp', 'L', 'in'), ('vref', 'L', 'in'), ('rst', 'L', 'in')], w=180, h=200, label='AFE core')
make_symbol('bias', [('vdd', 'T', 'inout'), ('vss', 'B', 'inout'), ('vbp', 'R', 'out'), ('vref', 'R', 'out')],
            w=140, h=140, label='Bias + VREF')
make_symbol('eeg_afe_top', [('ua0', 'L', 'inout'), ('ua1', 'R', 'inout'), ('rst', 'L', 'in'), ('vdd', 'T', 'inout'),
                            ('vss', 'B', 'inout')], w=200, h=160, label='EEG front-end')

# ---------------------------------------------------------------- OTA
c = Cell('ota', [('inn', 'in'), ('inp', 'in'), ('out', 'out'), ('vdd', 'io'), ('vss', 'io'), ('vbp', 'in')],
         'Two-stage Miller OTA (PMOS input)',
         ['M3/M4: three 7/20 um NMOS in series (effective L = 60 um) for low 1/f noise.',
          'Current sources use the 4/2 um PMOS unit cell matched to the bias diode (0.5 uA per unit).',
          'Rz = res_xhigh_po_0p35 L = 3.3 um (about 20 kOhm). Cc = 2 pF = 2 x (22.25 um)^2 MIM (max MIM side is 30 um); bottom plate (met3) on node out.'])
c.mos('pfet', 'M5', 300, -300, 't', 'vbp', 'vdd', 'vdd', 4, 2, 8)
c.mos('pfet', 'M1', 150, -150, 'd1', 'inn', 't', 't', 5, 8, 30)
c.mos('pfet', 'M2', 450, -150, 'y', 'inp', 't', 't', 5, 8, 30)
for i, (sd, ss) in enumerate((('d1', 's3'), ('s3', 's3c'), ('s3c', 'vss'))):
    c.mos('nfet', 'M3' + 'abc'[i], 150, 0 + 150 * i, sd, 'd1', ss, 'vss', 7, 20)
for i, (sd, ss) in enumerate((('y', 's4'), ('s4', 's4c'), ('s4c', 'vss'))):
    c.mos('nfet', 'M4' + 'abc'[i], 450, 0 + 150 * i, sd, 'd1', ss, 'vss', 7, 20)
c.mos('pfet', 'M7', 950, -300, 'out', 'vbp', 'vdd', 'vdd', 4, 2, 20)
c.mos('nfet', 'M6', 950, 150, 'out', 'y', 'vss', 'vss', 5, 2, 4)
c.rxh('Rz', 680, -40, 'y', 'z', 'vss', 3.3)
c.mim('Cc', 800, -40, 'z', 'out', 22.25, 22.25, 2)
c.write()

# ---------------------------------------------------------------- pseudo-resistor
c = Cell('pseudo_r', [('a', 'io'), ('b', 'io'), ('rst', 'in'), ('vss', 'io')],
         'Pseudo-resistor (two back-to-back PMOS pairs in series)',
         ['About 1.3e13 Ohm at zero bias (27 C). Each PMOS 0.42/1 um in its own n-well, bulk tied to its outer node.',
          'Reset: when rst is high, XS1-XS3 tie the internal nodes to a so the chain restarts at zero bias.'])
c.mos('pfet', 'Ma1', 150, -300, 'm1', 'm1', 'a', 'a', 0.42, 1)
c.mos('pfet', 'Mb1', 150, -150, 'm1', 'm1', 'n1', 'n1', 0.42, 1)
c.mos('pfet', 'Ma2', 150, 0, 'm2', 'm2', 'n1', 'n1', 0.42, 1)
c.mos('pfet', 'Mb2', 150, 150, 'm2', 'm2', 'b', 'b', 0.42, 1)
c.mos('nfet', 'S1', 500, -300, 'm1', 'rst', 'a', 'vss', 0.42, 0.15)
c.mos('nfet', 'S2', 500, -150, 'n1', 'rst', 'a', 'vss', 0.42, 0.15)
c.mos('nfet', 'S3', 500, 0, 'm2', 'rst', 'a', 'vss', 0.42, 0.15)
c.write()

# ---------------------------------------------------------------- AFE core
c = Cell('afe', [('vin', 'in'), ('vout', 'out'), ('vdd', 'io'), ('vss', 'io'), ('vbp', 'in'), ('vref', 'in'), ('rst', 'in')],
         'Capacitive-feedback EEG amplifier core',
         ['Gain = C1/C2 = 77.8 V/V. C1, C1p: 9 x (25.6 um)^2 MIM units = 11.95 pF. C2, C2p: 8.6 um square = 154 fF.',
          'MIM pins: c0 = top plate (capm/met4), c1 = bottom plate (met3, on the low-impedance node): vin, vss, vout, vref.',
          'SW1/SW2: reset switches driven by rst (ui_in[0]).'])
c.mim('C1', 150, -250, 'inn', 'vin', 25.6, 25.6, 9)
c.mim('C2', 400, -400, 'inn', 'vout', 8.6, 8.6)
c.sub('pseudo_r', 'XPR1', 650, -400, {'a': 'inn', 'b': 'vout', 'rst': 'rst', 'vss': 'vss'})
c.mos('nfet', 'SW1', 950, -400, 'inn', 'rst', 'vout', 'vss', 0.42, 0.15)
c.sub('ota', 'XA1', 500, -120, {'inn': 'inn', 'inp': 'inp', 'out': 'vout', 'vdd': 'vdd', 'vss': 'vss', 'vbp': 'vbp'})
c.mim('C1p', 150, 150, 'inp', 'vss', 25.6, 25.6, 9)
c.mim('C2p', 400, 200, 'inp', 'vref', 8.6, 8.6)
c.sub('pseudo_r', 'XPR2', 650, 200, {'a': 'inp', 'b': 'vref', 'rst': 'rst', 'vss': 'vss'})
c.mos('nfet', 'SW2', 950, 200, 'inp', 'rst', 'vref', 'vss', 0.42, 0.15)
c.write()

# ---------------------------------------------------------------- bias
c = Cell('bias', [('vdd', 'io'), ('vss', 'io'), ('vbp', 'out'), ('vref', 'out')],
         'Bias generator, start-up and VREF',
         ['Subthreshold beta-multiplier: I = n*UT*ln(K)/Rs = 0.5 uA (K = 4, Rs = 92 kOhm xhigh_po, L = 16 um).',
          'Start-up: MS1 (6 x 0.6/20 PMOS in series) pulls x high when no current flows; MS3 then pulls vbp low; MS2 releases it.',
          'MS1 is 0.6 um wide: the 0.42/20 um PMOS bin of the SKY130 continuous (combined) models fails in the ss corner (Pclm < 0).',
          'VREF = Vgs of MR2 (6 x 7/1 NMOS) at one 0.5 uA unit, about 0.45 V. CREF = 2 x (22.25 um)^2 MIM = 2 pF, bottom plate on vss.'])
c.mos('pfet', 'M11', 150, -300, 'vbp', 'vbp', 'vdd', 'vdd', 4, 2)
c.mos('pfet', 'M12', 450, -300, 'vbn', 'vbp', 'vdd', 'vdd', 4, 2)
c.mos('nfet', 'M9', 150, -100, 'vbp', 'vbn', 'rs', 'vss', 7, 1, 8)
c.mos('nfet', 'M10', 450, -100, 'vbn', 'vbn', 'vss', 'vss', 7, 1, 2)
c.rxh('RS', 170, 60, 'rs', 'vss', 'vss', 16)
chain = ['x', 's1a', 's1b', 's1c', 's1d', 's1e', 'vdd']
for i in range(6):
    c.mos('pfet', 'MS1' + 'abcdef'[i], 700 + 200 * (i // 3), 120 - 150 * (i % 3), chain[i], 'vss', chain[i + 1], 'vdd', 0.6, 20)
c.mos('nfet', 'MS2', 750, 300, 'x', 'vbn', 'vss', 'vss', 7, 1, 2)
c.mos('nfet', 'MS3', 1130, 150, 'vbp', 'x', 'vss', 'vss', 0.42, 2)
c.mos('pfet', 'MR1', 1350, -300, 'vref', 'vbp', 'vdd', 'vdd', 4, 2)
c.mos('nfet', 'MR2', 1350, -100, 'vref', 'vref', 'vss', 'vss', 7, 1, 6)
c.mim('CREF', 1600, -150, 'vref', 'vss', 22.25, 22.25, 2)
c.write()

# ---------------------------------------------------------------- top
c = Cell('eeg_afe_top', [('ua0', 'io'), ('ua1', 'io'), ('rst', 'in'), ('vdd', 'io'), ('vss', 'io')],
         'Neonatal EEG front-end: Tiny Tapeout analog core',
         ['ua0 = EEG input (ua[0]), ua1 = output (ua[1]), rst = ui_in[0] (active high), vdd = VDPWR, vss = VGND.',
          'The Tiny Tapeout wrapper (tt_um_...) adds the remaining template pins and ties uo_out, uio_out, uio_oe to VGND in layout.'])
c.sub('bias', 'XBIAS', 200, 0, {'vdd': 'vdd', 'vss': 'vss', 'vbp': 'vbp', 'vref': 'vref'})
c.sub('afe', 'XAFE', 650, 0, {'vin': 'ua0', 'vout': 'ua1', 'vdd': 'vdd', 'vss': 'vss', 'vbp': 'vbp', 'vref': 'vref', 'rst': 'rst'})
# when this is the top schematic (LVS netlist), use the PDK MIM model; a testbench above it may select the ideal one
c.lines.append('C {code_shown.sym} 200 300 0 0 {name=MIM_PDK only_toplevel=true value="tcleval(* MIM model: sky130_fd_pr__[set ::MIM_MODEL [lindex [list [set ::MIM_MODEL] cap_mim_m3_1] [expr [xschem get currsch] == 0]]] (PDK model when this is the top, for LVS))"}')
c.write()
# ---------------------------------------------------------------- testbench (open this one to simulate)
DEV2 = {'vsource': 'vsource.sym', 'res': 'res.sym', 'capa': 'capa.sym'}

def two(cell, kind, name, x, y, p, m, value):
    cell.lines.append(f'C {{{DEV2[kind]}}} {x} {y} 0 0 {{name={name} value="{value}" m=1 savecurrent=false}}')
    cell.label(x, y - 30, p, right=True)
    cell.label(x, y + 30, m, right=True)

def code(cell, name, x, y, text):
    text = text.strip('\n').replace('"', '\\"')
    cell.lines.append(f'C {{code_shown.sym}} {x} {y} 0 0 {{name={name} only_toplevel=false value="{text}"}}')

# Netlisted before the sub-schematics, so setting MIM_MODEL here affects every MIM capacitor below.
TB_MIM = """tcleval(* MIM capacitors: ideal C fitted to the PDK model (<0.1 % error), [set ::MIM_MODEL cap_mim_m3_1_ideal]
* The PDK model's milliohm series resistors make transient runs ~200x slower. LVS netlists use the PDK model.
.subckt sky130_fd_pr__cap_mim_m3_1_ideal c0 c1 w=1 l=1 mf=1
C1 c0 c1 \\{2.0e-15*w*l + 0.336e-15*(w+l)\\}
.ends
)"""

TB_CONTROL = """
* gmin/abstol: the default gmin=1e-12 adds ~1 Tohm of fake leakage at the 1e13-ohm nodes
.option gmin=1e-15 abstol=1e-15 klu
.temp 27
.ic v(xtop.xafe.inn)=0.45 v(xtop.xafe.inp)=0.45 v(ua1)=0.45
.control
  save v(ua0) v(ua1) v(pad) v(rst) v(vdd) v(xtop.vref) v(xtop.vbp) i(vdd)
  * tmax = 2 us: coarser steps give a false output jump when rst is released
  tran 1u 0.25 0 2u uic
  write tb_eeg_afe.raw
  meas tran vref_dc avg v(xtop.vref) from=0.15 to=0.25
  meas tran iddq avg i(vdd) from=0.15 to=0.25
  meas tran vpp_out pp v(pad) from=0.15 to=0.25
  meas tran vpp_in pp v(ua0) from=0.15 to=0.25
  let gain = vpp_out / vpp_in
  print gain
  plot v(pad) v(xtop.vref)
.endc
"""

c = Cell('tb_eeg_afe', [], 'Testbench: power-up, reset, 100 uV / 10 Hz tone',
         ['Simulation > Netlist, then Simulate. Waveforms: Waves > Load (tb_eeg_afe.raw) or the ngspice plot.',
          'Pads: the Tiny Tapeout analog path is modelled as 500 Ohm + 5 pF per pin. Load: 15 pF || 1 MOhm (scope probe / ADC).',
          'rst (ui_in[0]) is high for the first 10 ms; the tone starts at 20 ms. Expect gain = 77 V/V and VREF = 0.45 V.',
          'Corner: edit the CORNER instance (tt, ss, ff, sf, fs). Temperature: .temp line in the code block.'])
c.sub('eeg_afe_top', 'XTOP', 700, -150, {'ua0': 'ua0', 'ua1': 'ua1', 'rst': 'rst', 'vdd': 'vdd', 'vss': '0'})
two(c, 'vsource', 'VDD', 1100, -400, 'vdd', '0', 'PWL(0 0 100u 1.8)')
two(c, 'vsource', 'VIN', 0, -150, 'src', '0', 'SIN(0 100u 10 20m)')
two(c, 'res', 'RSW1', 200, -150, 'src', 'ua0', '500')
two(c, 'capa', 'CP1', 350, -50, 'ua0', '0', '5p')
two(c, 'vsource', 'VRST', 0, 100, 'rst', '0', 'PWL(0 0 50u 0 60u 1.8 10m 1.8 10.01m 0)')
two(c, 'res', 'RSW2', 1100, -150, 'ua1', 'pad', '500')
two(c, 'capa', 'CL', 1250, -50, 'pad', '0', '15p')
two(c, 'res', 'RL', 1400, -50, 'pad', '0', '1meg')
c.lines.append('C {sky130_fd_pr/corner.sym} 0 300 0 0 {name=CORNER only_toplevel=false corner=tt}')
code(c, 'MIM_IDEAL', 300, 250, TB_MIM)
code(c, 'CONTROL', 700, 250, TB_CONTROL)
c.write()

print('wrote', sorted(f for f in os.listdir(HERE) if f.endswith(('.sch', '.sym'))))
