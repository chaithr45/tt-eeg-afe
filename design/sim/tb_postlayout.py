"""Post-layout simulation: the extracted core (Magic, with parasitic capacitances) against the
schematic, both in the same test environment (500 ohm + 5 pF pad paths, 15 pF || 1 MOhm load) and
both with the on-chip bias generator.

  python3 tb_postlayout.py                    # tt / 27 C, schematic vs layout, AC + noise
  python3 tb_postlayout.py --corners          # + ss ff sf fs at 27 C and tt at 0 / 50 C
  python3 tb_postlayout.py --tran             # + 10 Hz tone transient with the MOS pseudo-resistors
  python3 tb_postlayout.py --reset            # + output step when rst is released (2 us steps)
  SKY130_LIB=combined python3 tb_postlayout.py ...

Netlist: mag/eeg_afe_core_pex.spice, made by layout/lay.py (extract_tcl(..., pex=True)).
As in the schematic runs, MIM capacitors are simulated as ideal capacitors of the same value and,
for AC/noise, the pseudo-resistors are replaced by their small-signal 1.3e13 ohm equivalent.
Parent-level capacitors on child-internal nets (no DC path, a fraction of a fF) are removed; the
extractor's negative correction capacitors (parent wiring over child cells) are kept.
Results: ../results/postlayout.json (postlayout_combined.json for the continuous models)."""
import json, os, re, sys
import numpy as np
import spice

_trapz = getattr(np, 'trapezoid', None) or np.trapz
PEX = os.path.join(spice.SIM_DIR, '..', '..', 'mag', 'eeg_afe_core_pex.spice')
RESULTS = os.path.join(spice.SIM_DIR, '..', 'results')

# internal node names of the two netlists (ngspice flattens X instances as xcore.<...>)
NODES = {
    'layout':    dict(cell='eeg_afe_core', inn='xcore.xsw1/d', inp='xcore.xsw2/d', vref='xcore.xsw2/s'),
    'schematic': dict(cell='eeg_afe_top', inn='xcore.xafe.inn', inp='xcore.xafe.inp', vref='xcore.vref'),
}

def _drop_dangling_caps(t):
    """Hierarchical extraction can leave a parent-level coupling capacitor on a net that lives
    inside a child cell and is not one of its ports. In SPICE that becomes a separate node with
    only capacitors on it (no DC path, singular matrix). Such capacitors (fractions of a fF)
    are dropped."""
    out, block = [], []
    def flush():
        used = set()
        for l in block:
            w = l.split()
            if not w or w[0].startswith('*'):
                continue
            if w[0].lower() == '.subckt':
                used.update(w[2:])
            elif w[0][0] in 'XxMmRr':
                used.update(x for x in w[1:] if '=' not in x)
        for l in block:
            w = l.split()
            if w and w[0][0] in 'Cc' and not w[0].startswith('Cmim') and not (w[1] in used and w[2] in used):
                continue
            out.append(l)
        block.clear()
    for l in t.splitlines():
        block.append(l)
        if l.lower().startswith('.ends'):
            flush()
    flush()
    return '\n'.join(out)

def prepare_layout(small_signal=True):
    t = open(PEX).read()
    t = re.sub(r'^\.end\s*$', '', t, flags=re.M)
    # MIM -> ideal C (same fit as spice._mim_to_ideal)
    def mim(m):
        name, a, b, l, w = m.group(1), m.group(2), m.group(3), float(m.group(4)), float(m.group(5))
        return f'Cmim{name} {a} {b} {(2.0 * w * l + 0.168 * 2 * (w + l)) * 1e-15:.6g}'
    t = re.sub(r'^X(\S+) (\S+) (\S+) sky130_fd_pr__cap_mim_m3_1 l=([\d.]+) w=([\d.]+).*$', mim, t, flags=re.M)
    # capacitors on child-internal nets have no DC path: drop them. Negative capacitors are kept:
    # they are the extractor's corrections for parent wiring over child cells (the totals stay positive).
    t = _drop_dangling_caps(t)
    if small_signal:
        hdr = re.search(r'^\.subckt pseudo_r (.*)$', t, re.M).group(1).split()
        # internal series nodes of the extracted pseudo-resistor have no DC path in the linear
        # model: tie them to `a` so the operating point stays well defined
        inner = [n for n in hdr if n not in ('a', 'b', 'rst', 'vss')]
        ties = ''.join(f'Rt{i} {n} a 1e9\n' for i, n in enumerate(inner))
        lin = f'.subckt pseudo_r_lin {" ".join(hdr)}\nRpr a b 1.3e13\n{ties}.ends pseudo_r_lin\n'
        t = re.sub(r'(^X\S+(?:\s+\S+)+?)\s+pseudo_r\s*$', r'\1 pseudo_r_lin', t, flags=re.M)
        t += '\n' + lin
    fn = 'pex_ss.spice' if small_signal else 'pex.spice'
    open(spice.path(fn), 'w').write(t + '\n')
    return fn

def netlist(which, small_signal):
    if which == 'layout':
        return prepare_layout(small_signal)
    return spice.prepare_design(small_signal=small_signal, ideal_mim=True)

ENV = '''
Rsw1 src ua0 500
Cp1 ua0 0 5p
XCORE ua0 ua1 rst vdd 0 {cell}
Rsw2 ua1 pad 500
Cp2 pad 0 15p
RL pad 0 1meg
'''

def ac(which='layout', corner='tt', temp=27, vdd=1.8):
    n = NODES[which]
    fn = netlist(which, True)
    name = f'{which}_ac'
    body = f'''
.option abstol=1e-15 gmin=1e-15 sparse
.include {fn}
Vdd vdd 0 {vdd}
Vin src 0 dc 0 ac 1
Vrst rst 0 0
{ENV.format(cell=n['cell'])}
.nodeset v({n['inn']})=0.45 v({n['inp']})=0.45 v(ua1)=0.45 v({n['vref']})=0.45
.control
op
print v(ua1) i(Vdd) v({n['inn']}) v({n['inp']}) v({n['vref']})
ac dec 20 0.01 1meg
let g = db(v(pad))
wrdata {name}_g.txt g
noise v(pad) Vin dec 20 0.05 100k
setplot noise1
wrdata {name}_n.txt inoise_spectrum
.endc'''
    r = spice.run(body, corner=corner, temp=temp, name=name)
    op = {}
    for l in r.stdout.splitlines():
        m = re.match(r'\s*(\S+)\s*=\s*([-+0-9.eE]+)\s*$', l)
        if m:
            op[m.group(1)] = float(m.group(2))
    if any(k in r.stdout + r.stderr for k in ('singular matrix', 'Transient op')):
        print(f'  warning: {which} {corner} {temp} C operating point needed fall-back steps')
    d = spice.load(f'{name}_g.txt'); f, g = d[:, 0], d[:, 1]
    band = np.where(g > g.max() - 3)[0]
    nz = spice.load(f'{name}_n.txt'); fn_, vin = nz[:, 0], nz[:, 1]
    m = (fn_ >= 0.5) & (fn_ <= 100)
    return dict(gain_db=round(float(g.max()), 3), f_lo_hz=round(float(f[band[0]]), 4),
                f_hi_khz=round(float(f[band[-1]]) / 1e3, 2),
                noise_uvrms=round(float(np.sqrt(_trapz(vin[m] ** 2, fn_[m])) * 1e6), 3),
                idd_ua=round(-op.get('i(vdd)', np.nan) * 1e6, 3), vout_v=round(op.get('v(ua1)', np.nan), 4),
                vref_v=round(op.get(f'v({n["vref"]})', np.nan), 4),
                _curves=dict(f=f.tolist(), g=g.tolist(), fn=fn_.tolist(), vin=vin.tolist()))

def psrr(which='layout', corner='tt', temp=27, vdd=1.8, f=50):
    """Supply-to-output gain at f (dB); PSRR = signal gain - this."""
    n = NODES[which]
    fn = netlist(which, True)
    name = f'{which}_psr'
    body = f'''
.option abstol=1e-15 gmin=1e-15 sparse
.include {fn}
Vdd vdd 0 dc {vdd} ac 1
Vin src 0 0
Vrst rst 0 0
{ENV.format(cell=n['cell'])}
.nodeset v({n['inn']})=0.45 v({n['inp']})=0.45 v(ua1)=0.45 v({n['vref']})=0.45
.control
op
ac lin 1 {f} {f}
wrdata {name}.txt db(v(pad))
.endc'''
    spice.run(body, corner=corner, temp=temp, name=name)
    return float(spice.load(f'{name}.txt')[1])

def tran(which='layout', corner='tt', temp=27, amp=100e-6, freq=10, tstop=2.0, tsig=1.0, trst=0.5, tmax='50u'):
    """Same stimulus as tb_tran.py: supply ramp, rst high until trst, then a sine from tsig."""
    n = NODES[which]
    fn = netlist(which, False)
    name = f'{which}_tran'
    body = f'''
.option gmin=1e-15 abstol=1e-15 klu
.include {fn}
Vdd vdd 0 PWL(0 0 100u 1.8)
Vin src 0 SIN(0 {amp} {freq} {tsig})
Vrst rst 0 PWL(0 0 50u 0 60u 1.8 {trst} 1.8 {trst + 10e-6} 0)
{ENV.format(cell=n['cell'])}
.ic v({n['inn']})=0.45 v({n['inp']})=0.45 v(ua1)=0.45
.control
tran 1u {tstop} 0 {tmax} uic
wrdata {name}.txt v(pad) v(src) i(Vdd)
.endc'''
    spice.run(body, corner=corner, temp=temp, name=name)
    d = spice.load(f'{name}.txt')
    t, vo, vi, idd = d[:, 0], d[:, 1], d[:, 3], -d[:, 5]
    # gain at `freq` from a least-squares sine fit over the last 5 periods
    w = t > tstop - 5.0 / freq
    A = np.column_stack([np.sin(2 * np.pi * freq * t[w]), np.cos(2 * np.pi * freq * t[w]), np.ones(w.sum()), t[w]])
    co, *_ = np.linalg.lstsq(A, vo[w], rcond=None)
    ci, *_ = np.linalg.lstsq(A, vi[w], rcond=None)
    # (the output DC level is not reported here: with 50 us steps the reset edge is not resolved and the
    #  simulator adds a false step; reset_release() measures it with 2 us steps)
    return dict(gain_vv=round(float(np.hypot(co[0], co[1]) / np.hypot(ci[0], ci[1])), 2),
                idd_ua=round(float(np.mean(idd[w])) * 1e6, 3)), (t, vo)

def reset_release(which='layout', corner='tt', temp=27, trst=10e-3, tstop=20e-3, tmax='2u'):
    """Output step caused by releasing rst (charge injection and rst coupling), finely resolved:
    rst high from 60 us to trst, output read just before the falling edge and 5 / 10 ms after it."""
    n = NODES[which]
    fn = netlist(which, False)
    name = f'{which}_rst'
    body = f'''
.option gmin=1e-15 abstol=1e-15 klu
.include {fn}
Vdd vdd 0 PWL(0 0 50u 1.8)
Vin src 0 0
Vrst rst 0 PWL(0 0 50u 0 60u 1.8 {trst} 1.8 {trst + 10e-6} 0)
{ENV.format(cell=n['cell'])}
.ic v({n['inn']})=0.45 v({n['inp']})=0.45 v(ua1)=0.45
.control
tran 1u {tstop} 0 {tmax} uic
wrdata {name}.txt v(ua1)
.endc'''
    spice.run(body, corner=corner, temp=temp, name=name)
    d = spice.load(f'{name}.txt')
    t, v = d[:, 0], d[:, 1]
    before = float(np.interp(trst - 0.5e-3, t, v))
    return dict(vout_before_v=round(before, 4),
                step_mv=round((float(np.interp(tstop - 1e-3, t, v)) - before) * 1e3, 2))

def _fmt(r):
    return ('gain %.2f dB | band %.3f Hz - %.1f kHz | noise %.2f uVrms | Idd %.2f uA | vout %.3f V | PSRR(50 Hz) %.1f dB' %
            (r['gain_db'], r['f_lo_hz'], r['f_hi_khz'], r['noise_uvrms'], r['idd_ua'], r['vout_v'], r['psrr_50hz_db']))

if __name__ == '__main__':
    lib = os.path.basename(os.path.dirname(spice.LIB))
    print('model library:', spice.LIB)
    res = dict(models=lib, ac={}, tran={})
    curves = {}
    points = [('tt', 27)]
    if '--corners' in sys.argv:
        points += [('ss', 27), ('ff', 27), ('sf', 27), ('fs', 27), ('tt', 0), ('tt', 50)]
    for c, temp in points:
        for which in ('schematic', 'layout'):
            r = ac(which, c, temp)
            cv = r.pop('_curves')
            r['psrr_50hz_db'] = round(r['gain_db'] - psrr(which, c, temp), 1)
            if (c, temp) == ('tt', 27):
                curves[which] = cv
            res['ac'][f'{c}_{temp}_{which}'] = r
            print(f'{c} {temp:2d} C {which:9s}: {_fmt(r)}', flush=True)
    if '--reset' in sys.argv:
        for which in ('schematic', 'layout'):
            r = reset_release(which)
            res.setdefault('reset', {})[which] = r
            print(f'reset release tt 27 C {which:9s}: output {r["vout_before_v"]:.4f} V before, step {r["step_mv"]:+.2f} mV', flush=True)
    if '--tran' in sys.argv:
        for which in ('schematic', 'layout'):
            r, _ = tran(which)
            res['tran'][which] = r
            print(f'tran tt 27 C {which:9s}: 100 uV / 10 Hz -> gain {r["gain_vv"]:.1f} V/V, '
                  f'Idd {r["idd_ua"]:.2f} uA', flush=True)
    os.makedirs(RESULTS, exist_ok=True)
    out = os.path.join(RESULTS, 'postlayout.json' if lib == 'ngspice' else f'postlayout_{lib}.json')
    old = json.load(open(out)) if os.path.exists(out) else {}
    for k in ('ac', 'tran', 'reset'):
        old.setdefault(k, {}).update(res.get(k, {}))
    old['models'] = lib
    json.dump(old, open(out, 'w'), indent=1)
    if curves:     # gain and noise curves at tt / 27 C for make_plots.py (fig5)
        json.dump(curves, open(out.replace('.json', '_curves.json'), 'w'))
    print('wrote', os.path.relpath(out))
