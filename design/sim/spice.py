"""Small helper to run ngspice in batch mode from Python.

Model library selection (first match wins):
  1. environment variable SKY130_LIB (path to an ngspice .lib file)
  2. $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice  (IIC-OSIC-TOOLS / open_pdks install)
  3. the trimmed library used during development (/home/claude/pdk/mini/sky130_mini.lib.spice)
Process corners: tt, ss, ff, sf, fs.

All generated netlists and data files go to sim/work/ so the source folder stays clean.
"""
import os, re, subprocess
import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('EEG_WORK', os.path.join(SIM_DIR, 'work'))   # separate work dirs allow parallel runs
os.makedirs(WORK, exist_ok=True)

DEV_LIBS = {'ngspice': '/home/claude/pdk/mini/sky130_mini.lib.spice',            # dev-machine copies
            'combined': '/home/claude/pdk/mini_combined/sky130.lib.spice'}

def lib_path(choice):
    """'ngspice' (original binned models) or 'combined' (newer continuous models) -> sky130.lib.spice path.
    Any other value is taken as a path."""
    if choice not in ('ngspice', 'combined'):
        return choice
    pdk_root = os.environ.get('PDK_ROOT')
    if pdk_root:
        p = os.path.join(pdk_root, 'sky130A', 'libs.tech', choice, 'sky130.lib.spice')
        if os.path.exists(p):
            return p
    return DEV_LIBS[choice]

def _default_lib():
    """SKY130_LIB = a full path, or 'ngspice' (default) / 'combined' for the two model sets in the PDK:
    libs.tech/ngspice (used for the design) and libs.tech/combined (newer set; Xschem's SKY130 default)."""
    return lib_path(os.environ.get('SKY130_LIB', 'ngspice'))

LIB = _default_lib()

def path(fn):
    """Location of a generated file inside sim/work/."""
    return os.path.join(WORK, fn)

def _resolve(fn):
    for d in (SIM_DIR, WORK):
        p = os.path.join(d, fn)
        if os.path.exists(p):
            return p
    return fn

def run(body, corner='tt', temp=27, name='run', quiet=False, lib=None):
    """Run a netlist body (with its own .control block) at a corner and temperature."""
    body = re.sub(r'\.include\s+"?([\w.\-]+\.spice)"?', lambda m: f'.include "{_resolve(m.group(1))}"', body)
    net = f'* {name}\n.lib "{lib or LIB}" {corner}\n.temp {temp}\n' + body + '\n.end\n'
    fn = path(f'{name}.spice')
    with open(fn, 'w') as f:
        f.write(net)
    r = subprocess.run(['ngspice', '-b', fn], capture_output=True, text=True, timeout=3600, cwd=WORK)
    if not quiet:
        errs = [l for l in (r.stdout + r.stderr).splitlines() if 'rror' in l]
        if errs:
            print('ngspice:', errs[:5])
    return r

def load(fn):
    return np.loadtxt(path(fn))

# ------------------------------------------------------------------ design netlist
# EEG_DESIGN=xschem (default): netlist exported from the Xschem schematics (../xschem/netlist/)
# EEG_DESIGN=reference       : the hand-written netlists in sim/reference/ used for the first sizing
DESIGN = os.environ.get('EEG_DESIGN', 'xschem')
XSCHEM_NETLIST = os.path.join(SIM_DIR, '..', 'xschem', 'netlist', 'eeg_afe_top.spice')

PSEUDO_R_LIN = """
* Small-signal equivalent of pseudo_r: at zero bias a subthreshold MOS pseudo-resistor is a
* linear conductance with thermal (4kT/R) noise. R = 1.3e13 ohm from the MOS model at 27 C.
.subckt pseudo_r_lin a b rst vss
Rpr a b 1.3e13
.ends pseudo_r_lin
"""

def _mim_to_ideal(text):
    """Replace cap_mim_m3_1 instances by ideal capacitors of the same value.
    C = MF*(2.0 fF/um^2 * W*L + 0.168 fF/um * 2*(W+L)), fitted to the PDK model (<0.1 % error).
    The PDK model's milliohm series resistors make the 1e13-ohm nodes ill-conditioned in DC."""
    def rep(m):
        name, n1, n2, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        kv = dict(re.findall(r'(\w+)=([\d.eE+-]+)', rest))
        W, L, MF = float(kv['W']), float(kv['L']), float(kv.get('MF', 1))
        c = MF * (2.0 * W * L + 0.168 * 2 * (W + L)) * 1e-15
        return f'C{name[1:]} {n1} {n2} {c:.6g}'
    return re.sub(r'^(X\S+)\s+(\S+)\s+(\S+)\s+sky130_fd_pr__cap_mim_m3_1\s+(.*)$', rep, text, flags=re.M)

def prepare_design(small_signal=False, ideal_mim=True):
    """Write the design subcircuits (ota, pseudo_r, afe, bias, eeg_afe_top) to work/ and return the file name.
    small_signal=True swaps the MOS pseudo-resistors for pseudo_r_lin (AC / noise / PSRR runs)."""
    if DESIGN == 'reference':
        ref = os.path.join(SIM_DIR, 'reference')
        text = ''.join(open(os.path.join(ref, f)).read() + '\n' for f in ('ota.sub.spice', 'afe.sub.spice', 'bias.sub.spice', 'top.sub.spice'))
    else:
        text = open(XSCHEM_NETLIST).read()
        text = '\n'.join(l for l in text.splitlines() if not l.strip().lower().startswith(('.end', '** sch_path')) or l.strip().lower().startswith('.ends'))
        text += PSEUDO_R_LIN
        if ideal_mim:
            text = _mim_to_ideal(text)
    if small_signal:
        text = re.sub(r'(^X\S+(?:\s+\S+){4})\s+pseudo_r\s*$', r'\1 pseudo_r_lin', text, flags=re.M)
    fn = 'design_ss.spice' if small_signal else 'design.spice'
    open(path(fn), 'w').write(text + '\n')
    return fn
