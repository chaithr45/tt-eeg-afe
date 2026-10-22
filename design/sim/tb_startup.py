"""Start-up check of the bias generator: supply ramps 0 -> VDD in `tramp`, the bias must reach its
operating point (unit current ~0.4-0.6 uA, start-up node X back near 0 V) within a few ms.
A DC operating point cannot show this (the solver finds the 'on' state by itself); only a transient can."""
import numpy as np
import spice

def startup(corner='tt', temp=27, vdd=1.8, tramp='100u', tstop='5m', name='startup'):
    design = spice.prepare_design(small_signal=True)
    spice.run(f'''
.option gmin=1e-15 abstol=1e-15
.include {design}
Vdd vdd 0 PWL(0 0 {tramp} {vdd})
XB vdd 0 vbp vref bias
XMP pr vbp vdd vdd sky130_fd_pr__pfet_01v8 L=2 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 mult=1 m=1
Vp pr 0 0.9
.control
tran 1u {tstop} 0 5u uic
wrdata {name}.txt i(Vp) v(xb.x) v(vref)
.endc''', corner=corner, temp=temp, name=name)
    d = spice.load(f'{name}.txt')
    t, ip, x, vref = d[:, 0], d[:, 1], d[:, 3], d[:, 5]
    # settling time: last moment the unit current is more than 10 % away from its final value
    off = np.abs(ip - ip[-1]) > 0.1 * abs(ip[-1])
    t_settle = t[np.where(off)[0][-1]] if off.any() else 0.0
    return dict(iunit_ua=abs(ip[-1]) * 1e6, x_end=x[-1], vref=vref[-1], t_settle_ms=t_settle * 1e3)

if __name__ == '__main__':
    print('corner temp vdd | Iunit(uA) X_end(V) VREF(V) t_settle(ms)')
    for c in ('tt', 'ss', 'ff', 'sf', 'fs'):
        for t in (0, 27, 70):
            for v in (1.71, 1.89):
                r = startup(c, t, v)
                print(f'{c:6s} {t:3d} {v:.2f} | {r["iunit_ua"]:6.3f} {r["x_end"]:6.3f} {r["vref"]:6.3f} {r["t_settle_ms"]:6.3f}', flush=True)
