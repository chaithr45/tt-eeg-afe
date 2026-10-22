"""Operating point of the bias generator (unit current, VBP, VREF, start-up node X)."""
import spice, numpy as np
def bias_op(corner='tt', temp=27, vdd=1.8, args=''):
    design = spice.prepare_design(small_signal=True)
    r=spice.run(f'''
.include {design}
Vdd vdd 0 {vdd}
XB vdd 0 vbp vref bias {args}
* probe: one unit current source into a 0.9 V node
XMP pr vbp vdd vdd sky130_fd_pr__pfet_01v8 L=2 W=4 nf=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 mult=1 m=1
Vp pr 0 0.9
* probe: the bias resistor RS on its own (xhigh_po, L = 16 um), 0.1 V across it
XRT rt 0 0 sky130_fd_pr__res_xhigh_po_0p35 L=16 mult=1 m=1
Vrt rt 0 0.1
.control
op
print i(Vp) v(vbp) v(vref) v(xb.x) v(xb.vbn) i(Vdd) i(Vrt)
.endc''', name='bias_op', corner=corner, temp=temp)
    op={}
    for l in r.stdout.splitlines():
        if '=' in l:
            try: op[l.split('=')[0].strip()]=float(l.split('=')[1])
            except ValueError: pass
    return op
if __name__=='__main__':
    print('corner temp vdd | Iunit(uA) VBP VREF X(startup) Ibias_total(uA)')
    extra = ('tt_rl', 'tt_rh') if 'mini' in spice.LIB else ()   # resistor corners exist only in the dev library
    for c in ('tt','ss','ff','sf','fs') + extra:
        for t in (0,27,70):
            for v in (1.71,1.8,1.89):
                if (t!=27 or v!=1.8) and c not in ('tt','ss','ff'): continue
                o=bias_op(c,t,v)
                print(f'{c:6s} {t:3d} {v:.2f} | {o.get("i(vp)",0)*1e6:5.3f} {o.get("v(vbp)",0):.3f} {o.get("v(vref)",0):.3f} {o.get("v(xb.x)",0):.3f} {-o.get("i(vdd)",0)*1e6:5.2f}')
