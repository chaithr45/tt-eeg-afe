"""Re-run the key simulations and write results/summary.json.

Usage (inside IIC-OSIC-TOOLS):  cd sim && python3 run_all.py [--quick]
--quick skips the 45-point corner sweep."""
import json, os, sys, time
import numpy as np
import spice, tb_ac, tb_tran, tb_bias, corners

t0 = time.time()
print('model library:', spice.LIB)
S = {'model_library': spice.LIB, 'design_source': spice.DESIGN}

# 1. Small-signal: gain, bandwidth, noise, current (typical, on-chip bias)
r = tb_ac.frontend_ac(bias=tb_ac.REAL_BIAS, quiet=True)
S['typical'] = dict(gain_db=r['gain_db'], gain_vv=10 ** (r['gain_db'] / 20), f_lo_hz=r['f_lo'], f_hi_hz=r['f_hi'],
                    noise_uvrms_0p5_100hz=r['n_05_100'], noise_density_10hz_nv=r['d10'], idd_ua=r['idd'],
                    vout_dc=r['op'].get('v(vout)'))
print('typical:', {k: round(v, 3) for k, v in S['typical'].items()})

# 2. Bias generator over corners
b = {}
for c in ('tt', 'ss', 'ff', 'sf', 'fs'):
    for t in (0, 27, 70):
        for v in (1.71, 1.8, 1.89):
            o = tb_bias.bias_op(c, t, v)
            if 'i(vp)' not in o:
                print(f'bias {c} {t} C {v} V: ngspice failed, skipped'); continue
            b[f'{c}_{t}_{v}'] = dict(iunit_ua=o['i(vp)'] * 1e6, vref=o.get('v(vref)'), x=o.get('v(xb.x)'),
                                     rs_kohm=(0.1 / o['i(vrt)'] / 1e3) if o.get('i(vrt)') else np.nan)
iu = [x['iunit_ua'] for x in b.values()]; vr = [x['vref'] for x in b.values()]; xs = [x['x'] for x in b.values()]
tt = b.get('tt_27_1.8', {})
S['bias'] = dict(iunit_ua_tt=tt.get('iunit_ua', np.nan), rs_kohm_tt=abs(tt.get('rs_kohm', np.nan)),
                 iunit_ua_min=min(iu), iunit_ua_max=max(iu), vref_min=min(vr), vref_max=max(vr), startup_x_max=max(xs))
print('bias:', {k: round(v, 3) for k, v in S['bias'].items()})

# 3. PSRR (supply-to-output vs signal gain) at 50 Hz
design = spice.prepare_design(small_signal=True)
spice.run(f'''
.option abstol=1e-15 gmin=1e-15 sparse
.include {design}
Vdd vdd 0 dc 1.8 ac 1
XB vdd 0 vbp vref bias
Vin src 0 0
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
ac lin 1 50 50
wrdata psr.txt db(v(pad))
.endc''', name='psrr')
S['psrr_50hz_db'] = S['typical']['gain_db'] - float(spice.load('psr.txt')[1])
print('PSRR @50 Hz: %.1f dB' % S['psrr_50hz_db'])

# 4. Transient: 100 uV tone gain, distortion at 1/3/5 mV
S['tran'] = {}
for amp in (100e-6, 1e-3, 3e-3, 5e-3):
    t, out, vin, vref, idd = tb_tran.tran(tstop=2.5, tsig=1.0, trst=0.5, amp=amp, name='tone')
    a, thd = tb_tran.fit_tone(t, out, 10, 1.5)
    S['tran'][f'{amp*1e6:.0f}uV'] = dict(out_mv=a * 1e3, gain_vv=a / amp, thd_pct=thd)
    print(f'tone {amp*1e3:.1f} mV: out {a*1e3:.2f} mV, gain {a/amp:.1f}, THD {thd:.3f} %')

# 5. Artifact recovery with a 10 ms reset pulse (fine time step around the reset edges)
t, out, *_ = tb_tran.tran(tstop=0.25, name='artifact', tmax='2u',
                          rst_pwl='0 0 50u 0 60u 1.8 10m 1.8 10.01m 0 100m 0 100.01m 1.8 110m 1.8 110.01m 0',
                          src_pwl='0 0 50m 0 50.1m 20m')
k = lambda x: out[np.argmin(abs(t - x))]
S['artifact'] = dict(before=k(0.049), saturated=k(0.099), after_reset=k(0.13), end=k(0.249))
print('artifact recovery:', {kk: round(v, 4) for kk, v in S['artifact'].items()})

# 6. Corners (optional, ~3 minutes)
if '--quick' not in sys.argv:
    rows = corners.run_corners()
    g = [x['gain_db'] for x in rows]; n = [x['noise'] for x in rows if x['temp'] <= 37]; i = [x['idd'] for x in rows]
    m = np.array([x['margins'] for x in rows])
    S['corners'] = dict(n=len(rows), gain_db_min=min(g), gain_db_max=max(g), noise_uv_max_le37C=max(n) if n else None,
                        noise_uv_max_all=max(x['noise'] for x in rows), idd_ua_min=min(i), idd_ua_max=max(i),
                        min_sat_margin_v=dict(zip(['M5', 'M2', 'M4a', 'M6', 'M7'], m.min(axis=0).tolist())))
    print('corners:', S['corners'])

out = 'summary_combined.json' if 'combined' in spice.LIB else 'summary.json'
json.dump(S, open(os.path.join(spice.SIM_DIR, '..', 'results', out), 'w'), indent=1)
print('wrote results/' + out)
print('done in %.0f s' % (time.time() - t0))
