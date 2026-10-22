"""Pseudo-resistor characterisation: I-V of one pseudo_r (rst low) with node a held at VREF and a voltage
dV applied across it (a at 0 V so the solver gmin carries no current). Gives the small-signal resistance at zero bias, R0 (the pseudo-resistor is strongly temperature dependent).
The AC/noise testbenches use a fixed linear 1.3e13 ohm model; this script shows how far that holds vs temperature:
f_L = 1 / (2 pi R C2), C2 = 154 fF."""
import numpy as np
import spice

C2 = 154e-15

def pr_iv(corner='tt', temp=27, va=0.0, name='pr_iv'):
    design = spice.prepare_design(small_signal=False)
    spice.run(f'''
.option gmin=1e-15 abstol=1e-18
.include {design}
Va a 0 {va}
Vb b a 0
Vrst rst 0 0
XPR a b rst 0 pseudo_r
.control
dc Vb -0.3 0.3 0.002
wrdata {name}.txt i(Vb)
.endc''', corner=corner, temp=temp, name=name)
    d = spice.load(f'{name}.txt')
    return d[:, 0], -d[:, 1]          # dV, current flowing a <- b through the pseudo-resistor

def r_at(dv, i, i_bias=0.0):
    """Small-signal resistance where the DC current equals i_bias."""
    g = np.gradient(i, dv)
    k = np.argmin(abs(i - i_bias))
    return 1 / g[k], dv[k]

if __name__ == '__main__':
    print('corner temp | R0 (ohm)   f_L = 1/(2 pi R0 C2) (Hz)')
    for c in ('tt', 'ss', 'ff', 'sf', 'fs'):
        for t in (0, 27, 37, 50, 55, 70):
            dv, i = pr_iv(c, t)
            r0, _ = r_at(dv, i, 0)
            print(f'{c:3s} {t:3d} | {r0:9.2e}  {1 / (2 * np.pi * r0 * C2):6.3f}', flush=True)
