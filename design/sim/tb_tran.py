"""Transient testbench with the real (MOS) pseudo-resistors and the on-chip bias.

The supply ramps from 0 V, rst (ui_in[0]) is held high until `trst`, then a test signal
starts at `tsig`: a sine (amp, freq) or, if `step` is given, an input step of that size.

Numerical note: keep tmax <= 2 us whenever a reset edge must be resolved; coarser steps
produce false output jumps at reset release (checked: 20 us -> -94 mV, 2 us and 0.5 us -> -0.8 mV)."""
import numpy as np
import spice

def tran(corner='tt', temp=27, amp=100e-6, freq=10, tstop=3.0, tsig=1.0, step=None, name='tran',
         trst=0.5, vdd=1.8, tmax='50u', rst_pwl=None, src_pwl=None, ideal_mim=True):
    if src_pwl:
        src = f'PWL({src_pwl})'
    elif step is not None:
        src = f'PWL(0 0 {tsig} 0 {tsig + 1e-4} {step})'
    else:
        src = f'SIN(0 {amp} {freq} {tsig})'
    rst = rst_pwl or f'0 0 50u 0 60u 1.8 {trst} 1.8 {trst + 10e-6} 0'
    design = spice.prepare_design(small_signal=False, ideal_mim=ideal_mim)
    body = f'''
.option gmin=1e-15 abstol=1e-15 klu
.include {design}
Vdd vdd 0 PWL(0 0 100u {vdd})
Vin src 0 {src}
Rsw1 src ua0 500
Cp1 ua0 0 5p
Vrst rst 0 PWL({rst})
XTOP ua0 ua1 rst vdd 0 eeg_afe_top
Rsw2 ua1 pad 500
Cp2 pad 0 15p
RL pad 0 1meg
.ic v(xtop.xafe.inn)=0.45 v(xtop.xafe.inp)=0.45 v(ua1)=0.45
.control
tran 1u {tstop} 0 {tmax} uic
wrdata {name}.txt v(pad) v(src) v(xtop.vref) i(Vdd)
.endc'''
    spice.run(body, corner=corner, temp=temp, name=name)
    d = spice.load(f'{name}.txt')
    return d[:, 0], d[:, 1], d[:, 3], d[:, 5], -d[:, 7]

def fit_tone(t, y, f0, t0, harmonics=5):
    """Least-squares fit of a tone (+ offset and drift); returns amplitude and THD (%)."""
    m = t > t0; tt = t[m]; yy = y[m]
    cols = [np.ones_like(tt), tt - tt.mean()]
    for h in range(1, harmonics + 1):
        cols += [np.sin(2 * np.pi * h * f0 * tt), np.cos(2 * np.pi * h * f0 * tt)]
    c, *_ = np.linalg.lstsq(np.column_stack(cols), yy, rcond=None)
    a = [np.hypot(c[2 + 2 * k], c[3 + 2 * k]) for k in range(harmonics)]
    return a[0], np.sqrt(sum(x * x for x in a[1:])) / a[0] * 100

if __name__ == '__main__':
    t, out, vin, vref, idd = tran(tstop=2.0, tsig=1.0, trst=0.5)
    a, thd = fit_tone(t, out, 10, 1.5)
    print(f'100 uV, 10 Hz in -> {a*1e3:.3f} mV out ({a/100e-6:.1f} V/V), THD {thd:.3f} %, VREF {vref[-1]:.4f} V, Idd {idd[-1]*1e6:.2f} uA')
