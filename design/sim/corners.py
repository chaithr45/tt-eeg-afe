"""Run the front-end AC/noise testbench over process, temperature and supply corners."""
import json, os
import tb_ac, spice
from tb_ac import REAL_BIAS, margin

def run_corners(corners=('tt', 'ss', 'ff', 'sf', 'fs'), temps=(0, 27, 37, 70), vdds=(1.71, 1.8, 1.89), out=None):
    if out is None:
        out = '../results/corners_combined.json' if 'combined' in spice.LIB else '../results/corners.json'
    rows = []
    print(f'{"corner":6s} {"T":>3s} {"VDD":>4s} | {"gain":>6s} {"f_lo":>6s} {"f_hi":>7s} {"noise":>6s} {"Idd":>6s} {"vout":>5s} | sat. margin (V): M5 M2 M4a M6 M7')
    for c in corners:
        for t in temps:
            for v in vdds:
                r = tb_ac.frontend_ac(corner=c, temp=t, vdd=v, bias=REAL_BIAS, quiet=True)
                op = r['op']
                m = [margin(op, 'xm5', 'pfet'), margin(op, 'xm2', 'pfet'), margin(op, 'xm4a', 'nfet'), margin(op, 'xm6', 'nfet'), margin(op, 'xm7', 'pfet')]
                rows.append(dict(corner=c, temp=t, vdd=v, gain_db=r['gain_db'], f_lo=r['f_lo'], f_hi=r['f_hi'],
                                 noise=r['n_05_100'], idd=r['idd'], vout=op.get('v(vout)'), margins=m))
                print(f'{c:6s} {t:3d} {v:4.2f} | {r["gain_db"]:6.2f} {r["f_lo"]:6.3f} {r["f_hi"]/1e3:6.1f}k {r["n_05_100"]:6.2f} {r["idd"]:6.2f} {op.get("v(vout)", 0):5.3f} | '
                      + ' '.join(f'{x:+.2f}' for x in m), flush=True)
    if out:
        json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), out), 'w'), indent=1)
    return rows

if __name__ == '__main__':
    run_corners()
