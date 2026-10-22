"""Closed-loop AC + noise testbench for the front-end.

The pseudo-resistors are replaced by their small-signal equivalent (pseudo_r_lin, a linear
1.3e13 ohm resistor with thermal noise) for these runs; the full MOS pseudo-resistor is
used in the transient testbench (tb_tran.py)."""
import numpy as np
import spice

REAL_BIAS = 'XB vdd 0 vbp vref bias'
IDEAL_BIAS = '''XMB vbp vbp vdd vdd sky130_fd_pr__pfet_01v8 L=2 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 mult=1 m=1
Ib vbp 0 0.5u
Vref vref 0 {vref}'''

def frontend_ac(corner='tt', temp=27, vdd=1.8, vref=0.5, bias=None, quiet=False, cload=15):
    design = spice.prepare_design(small_signal=True)
    biasnet = (bias or IDEAL_BIAS).format(vref=vref)
    body = f'''
.option abstol=1e-15 gmin=1e-15 sparse
.include {design}
Vdd vdd 0 {vdd}
{biasnet}
* source -> Tiny Tapeout analog path (approx. 500 ohm, 5 pF) -> ua[0]
Vin src 0 dc 0 ac 1
Rsw1 src vin 500
Cp1 vin 0 5p
Vrst rst 0 0
XAFE vin vout vdd 0 vbp vref rst afe
* ua[1] -> analog path -> scope / ADC input
Rsw2 vout pad 500
Cp2 pad 0 {cload}p
RL pad 0 1meg
.nodeset v(xafe.inn)={vref} v(xafe.inp)={vref} v(vout)={vref}
.control
op
print v(vout) v(xafe.inn) v(xafe.inp) v(vref) v(vbp) i(Vdd) v(xafe.xa1.t) v(xafe.xa1.d1) v(xafe.xa1.y)
print @m.xafe.xa1.xm5.msky130_fd_pr__pfet_01v8[vds] @m.xafe.xa1.xm5.msky130_fd_pr__pfet_01v8[vdsat] @m.xafe.xa1.xm2.msky130_fd_pr__pfet_01v8[vds] @m.xafe.xa1.xm2.msky130_fd_pr__pfet_01v8[vdsat] @m.xafe.xa1.xm4a.msky130_fd_pr__nfet_01v8[vds] @m.xafe.xa1.xm4a.msky130_fd_pr__nfet_01v8[vdsat] @m.xafe.xa1.xm7.msky130_fd_pr__pfet_01v8[vds] @m.xafe.xa1.xm7.msky130_fd_pr__pfet_01v8[vdsat] @m.xafe.xa1.xm6.msky130_fd_pr__nfet_01v8[vds] @m.xafe.xa1.xm6.msky130_fd_pr__nfet_01v8[vdsat]
ac dec 20 0.01 1meg
let g = db(v(pad))
let ph = 180/pi*cph(v(pad))
wrdata cl.txt g ph
noise v(pad) Vin dec 20 0.05 100k
setplot noise1
wrdata nz.txt inoise_spectrum onoise_spectrum
.endc'''
    r = spice.run(body, corner=corner, temp=temp, name='afe_ac')
    op = {}
    for l in r.stdout.splitlines():
        if '=' in l and ('v(' in l or 'i(' in l or '[' in l):
            try:
                op[l.split('=')[0].strip()] = float(l.split('=')[1])
            except ValueError:
                pass
    d = spice.load('cl.txt'); f = d[:, 0]; g = d[:, 1]; ph = d[:, 3]
    gm = g.max(); band = np.where(g > gm - 3)[0]
    n = spice.load('nz.txt'); fn = n[:, 0]; vin = n[:, 1]
    def integ(a, b):
        m = (fn >= a) & (fn <= b)
        return np.sqrt(np.trapezoid(vin[m] ** 2, fn[m]))
    res = dict(gain_db=gm, f_lo=f[band[0]], f_hi=f[band[-1]], n_05_100=integ(0.5, 100) * 1e6,
               n_05_70=integ(0.5, 70) * 1e6, d10=vin[np.argmin(abs(fn - 10))] * 1e9,
               idd=-op.get('i(vdd)', np.nan) * 1e6, op=op, f=f, g=g, ph=ph, fn=fn, vin=vin)
    if not quiet:
        print('gain %.2f dB (%.1f V/V) | band %.3f Hz - %.2f kHz | noise 0.5-100 Hz %.2f uVrms | %.0f nV/rtHz@10Hz | Idd %.2f uA | vout %.3f V' % (
            gm, 10 ** (gm / 20), res['f_lo'], res['f_hi'] / 1e3, res['n_05_100'], res['d10'], res['idd'], op.get('v(vout)', np.nan)))
    return res

def margin(op, dev, typ):
    """Saturation margin |Vds| - |Vdsat| of an OTA device (V)."""
    k = f'@m.xafe.xa1.{dev}.msky130_fd_pr__{typ}_01v8'
    return abs(op.get(k + '[vds]', np.nan)) - abs(op.get(k + '[vdsat]', np.nan))

if __name__ == '__main__':
    print('ideal bias:'); frontend_ac()
    print('on-chip bias:'); frontend_ac(bias=REAL_BIAS)
