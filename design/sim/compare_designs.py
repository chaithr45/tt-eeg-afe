"""Check that the Xschem-exported netlist behaves like the reference netlist used for sizing."""
import importlib, os, sys
import numpy as np

def run(design):
    os.environ['EEG_DESIGN'] = design
    import spice; importlib.reload(spice)
    import tb_ac, tb_bias, tb_tran
    for m in (tb_ac, tb_bias, tb_tran): importlib.reload(m)
    out = {}
    r = tb_ac.frontend_ac(bias=tb_ac.REAL_BIAS, quiet=True)
    out.update(gain_db=r['gain_db'], f_lo=r['f_lo'], f_hi=r['f_hi'], noise_uv=r['n_05_100'], idd_ua=r['idd'], vout=r['op'].get('v(vout)'))
    b = tb_bias.bias_op('tt', 27, 1.8)
    out.update(iunit_ua=b.get('i(vp)', np.nan) * 1e6, vref=b.get('v(vref)'))
    t, o, *_ = tb_tran.tran(tstop=2.0, tsig=1.0, trst=0.5, amp=1e-3, name='cmp_tone')
    a, thd = tb_tran.fit_tone(t, o, 10, 1.5)
    out.update(tone_gain=a / 1e-3, thd_pct=thd)
    return out

if __name__ == '__main__':
    ref = run('reference'); xs = run('xschem')
    print(f'{"metric":10s} {"reference":>12s} {"xschem":>12s} {"diff %":>8s}')
    ok = True
    for k in ref:
        d = 100 * (xs[k] - ref[k]) / ref[k] if ref[k] else 0
        print(f'{k:10s} {ref[k]:12.4f} {xs[k]:12.4f} {d:8.2f}')
    sys.exit(0)
