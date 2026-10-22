"""Monte Carlo mismatch analysis of the complete front-end (bias + VREF + amplifier).

Uses the continuous ("combined") SKY130 models: they apply mismatch per device
(AGAUSS(...)/sqrt(W*L*mult) inside every transistor, resistor and MIM capacitor), and each
sample gets its own `.option seed`, so runs are independent and reproducible.

Per sample: DC operating point + gain at 10 Hz (closed loop, pads and load included).
  gain          |v(pad)/v(src)| at 10 Hz (C1/C2 matching + finite loop gain)
  out_offset    v(vout) - v(vref): OTA offset plus leakage mismatch, i.e. the output DC error
  vref, iunit   VREF and the bias unit current (diode M11)
  m5_margin     saturation margin |Vds|-|Vdsat| of the tail source M5 (the tightest device, README section 5)

Run:  python3 tb_mc.py            (200 samples tt/27 C/1.8 V + 100 samples ss/0 C/1.71 V, ~10-20 min)
      python3 tb_mc.py 50         (quicker: 50 + 25 samples)
Writes results/montecarlo.json and results/fig4_montecarlo.png."""
import json, os, re, shutil, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import spice

LIB = spice.lib_path(os.environ.get('SKY130_LIB', 'combined'))
P5 = '@m.xafe.xa1.xm5.msky130_fd_pr__pfet_01v8'

def _design():
    """Design netlist for MC: linear pseudo-resistors, real MIM capacitors (they carry mismatch here)."""
    fn = spice.prepare_design(small_signal=True, ideal_mim=('combined' not in LIB))
    shutil.copy(spice.path(fn), spice.path('design_mc.spice'))
    return 'design_mc.spice'

def sample(seed, corner='tt', temp=27, vdd=1.8):
    name = f'mc_{corner}_{temp}_{seed}'
    body = f'''
.option seed={seed}
.option abstol=1e-15 gmin=1e-15
.include design_mc.spice
Vdd vdd 0 {vdd}
XB vdd 0 vbp vref bias
Vin src 0 dc 0 ac 1
Rsw1 src vin 500
Cp1 vin 0 5p
Vrst rst 0 0
XAFE vin vout vdd 0 vbp vref rst afe
Rsw2 vout pad 500
Cp2 pad 0 15p
RL pad 0 1meg
.nodeset v(xafe.inn)=0.45 v(xafe.inp)=0.45 v(vout)=0.45
.control
op
print v(vout) v(vref) v(xafe.inn) i(vdd) @m.xb.xm11.msky130_fd_pr__pfet_01v8[id] {P5}[vds] {P5}[vdsat]
ac lin 1 10 10
print mag(v(pad))
.endc'''
    r = spice.run(body, corner=f'{corner}_mm', temp=temp, name=name, quiet=True, lib=LIB)
    v = {}
    for l in r.stdout.splitlines():
        m = re.match(r'\s*(\S+)\s*=\s*([-+0-9.eE]+)\s*$', l)
        if m:
            v[m.group(1).lower()] = float(m.group(2))
    for ext in ('.spice',):
        try: os.remove(spice.path(name + ext))
        except OSError: pass
    need = ('v(vout)', 'v(vref)', 'mag(v(pad))')
    if not all(k in v for k in need):
        return None
    return dict(seed=seed, gain=v['mag(v(pad))'], out_offset_mv=(v['v(vout)'] - v['v(vref)']) * 1e3,
                vref=v['v(vref)'], vinn=v.get('v(xafe.inn)', np.nan), idd_ua=-v.get('i(vdd)', np.nan) * 1e6,
                iunit_ua=abs(v.get(f'@m.xb.xm11.msky130_fd_pr__pfet_01v8[id]', np.nan)) * 1e6,
                m5_margin=abs(v.get(f'{P5.lower()}[vds]', np.nan)) - abs(v.get(f'{P5.lower()}[vdsat]', np.nan)))

def run_mc(n, corner='tt', temp=27, vdd=1.8):
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
        res = list(ex.map(lambda s: sample(s, corner, temp, vdd), range(1, n + 1)))
    ok = [r for r in res if r]
    return ok, n - len(ok)

def stats(rows, key):
    x = np.array([r[key] for r in rows], float)
    return dict(mean=float(np.nanmean(x)), sigma=float(np.nanstd(x)), min=float(np.nanmin(x)), max=float(np.nanmax(x)))

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    print('model library:', LIB)
    _design()
    out = {'model_library': LIB}
    keys = ('gain', 'out_offset_mv', 'vref', 'iunit_ua', 'idd_ua', 'm5_margin')
    for corner, temp, vdd, nn in (('tt', 27, 1.8, n), ('ss', 0, 1.71, max(n // 2, 10))):
        rows, failed = run_mc(nn, corner, temp, vdd)
        tag = f'{corner}_{temp}C_{vdd}V'
        out[tag] = dict(n=len(rows), failed=failed, stats={k: stats(rows, k) for k in keys}, samples=rows)
        print(f'\n{tag}: {len(rows)} samples ({failed} failed)')
        print(f'  {"":14s} {"mean":>9s} {"sigma":>9s} {"min":>9s} {"max":>9s}')
        for k in keys:
            s = out[tag]['stats'][k]
            print(f'  {k:14s} {s["mean"]:9.4f} {s["sigma"]:9.4f} {s["min"]:9.4f} {s["max"]:9.4f}')
    res_dir = os.path.join(spice.SIM_DIR, '..', 'results')
    json.dump(out, open(os.path.join(res_dir, 'montecarlo.json'), 'w'), indent=1)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        rows = out['tt_27C_1.8V']['samples']
        fig, ax = plt.subplots(1, 4, figsize=(16, 3.6))
        for a, (k, lab) in zip(ax, (('gain', 'Gain at 10 Hz (V/V)'), ('out_offset_mv', 'Output DC offset vs VREF (mV)'),
                                    ('vref', 'VREF (V)'), ('iunit_ua', 'Bias unit current (uA)'))):
            a.hist([r[k] for r in rows], bins=25, color='#3b6ea5', edgecolor='white')
            s = out['tt_27C_1.8V']['stats'][k]
            a.set_title(f'{lab}\nmean {s["mean"]:.4g}, sigma {s["sigma"]:.3g}', fontsize=10); a.set_yticks([])
        fig.suptitle(f'Monte Carlo mismatch, tt 27 C 1.8 V, {len(rows)} samples (SKY130 continuous models)', fontsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(res_dir, 'fig4_montecarlo.png'), dpi=130)
    except Exception as e:
        print('plot skipped:', e)
    print('\nwrote results/montecarlo.json and results/fig4_montecarlo.png; done in %.0f s' % (time.time() - t0))
