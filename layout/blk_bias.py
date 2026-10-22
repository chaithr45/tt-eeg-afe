"""bias: beta-multiplier current reference, start-up and VREF (CREF sits with the MIM capacitors).

  MS1a-f  start-up pull-up, six 0.6/20 PMOS in series (alternating orientation so each source
          meets the next drain on the same side)                         rows above
  M11 M12 MR1   4/2 PMOS unit cells (vbp mirror)                         PMOS row (y = 0)
  RS | M9 (7/1 x8) | M10 (x2) | MS2 (x2) | MR2 (x6) | MS3 (0.42/2)        NMOS row (y = -9)
Ports: vdd vss vbp vref
"""
from lay import Cell
from route import *

def build(name='bias'):
    c = Cell(name)
    yP, yN = 0.0, -9.0
    M11 = c.place('p4_2', 'M11', 0.0, yP)
    M12 = c.place('p4_2', 'M12', 4.2, yP)
    MR1 = c.place('p4_2', 'MR1', 8.4, yP)
    RS = c.place('rxh_16', 'RS', -9.0, yN)
    M9 = c.place('n7_1_nf8', 'M9', -1.0, yN)
    M10 = c.place('n7_1_nf2', 'M10', 7.4, yN)
    MS2 = c.place('n7_1_nf2', 'MS2', 12.2, yN)
    MR2 = c.place('n7_1_nf6', 'MR2', 19.4, yN)
    MS3 = c.place('n042_2', 'MS3', 26.5, yN)
    xs, ys0, pit = 4.2, 6.0, 2.9
    MS1 = [c.place('p06_20', f'MS1{k}', xs, ys0 + i * pit, 'h' if i % 2 == 0 else '')
           for i, k in enumerate('abcdef')]
    # one n-well (vdd) under the PMOS row and the start-up stack
    c.rect('nwell', min(M11.bbox[0], MS1[0].bbox[0]), M11.bbox[1], max(MR1.bbox[2], MS1[0].bbox[2]), MS1[-1].bbox[3])

    # ---------------------------------------------------------------- PMOS row
    gb = [d.term('G') for d in (M11, M12, MR1)]
    m1_to(c, gb[0][0] + 0.1, gb[-1][2] - 0.1, cy(gb[0]))           # all gates = vbp
    d11 = M11.term('D')                                            # M11 diode (D = G): bridge at
    c.rect('metal1', d11[0], gb[0][1], gb[0][0] + 0.05, gb[0][3])  # gate level + drain column up
    c.rect('metal1', d11[0], d11[1], d11[2], gb[0][3])
    for d in (M11, M12, MR1):                                      # sources = vdd
        c.via1(cx(d.term('S')), d.y + 1.0)
    c.wire('metal2', [(cx(M11.term('S')), 1.0), (cx(MR1.term('S')), 1.0)], W2)
    xr, _ = ring_tap(c, MR1, 'r', 1.0); c.via1(xr, 1.0)
    c.wire('metal2', [(cx(MR1.term('S')), 1.0), (xr, 1.0)], W2)
    for d in (M11, M12, MR1):
        c.via1(cx(d.term('D')), d.y - 1.0)

    # ---------------------------------------------------------------- NMOS row
    # gates of M9, M10, MS2 = vbn (one metal1 bar); M10 is the vbn diode
    g9, g10, g2 = M9.term('G'), M10.term('G'), MS2.term('G')
    m1_to(c, g9[0] + 0.1, g2[2] - 0.1, cy(g9))
    for col in M10.cols('D'):
        c.rect('metal1', col[0] - 0.2, col[3] - 0.01, col[2] + 0.2, g10[3])   # covers both gate pads
    # MR2 diode: drains = gate = vref
    gR2 = MR2.term('G')
    for col in MR2.cols('D'):
        c.rect('metal1', col[0] - 0.2, col[3] - 0.01, col[2] + 0.2, gR2[3])
    # M9 drains = vbp, sources = rs
    yD9 = col_strap(c, M9, 'D', +1.75)
    yS9 = col_strap(c, M9, 'S', -1.75)
    # vbp: M11 drain down to the M9 drain strap
    xv = cx(M11.term('D'))
    c.wire('metal2', [(xv, -1.0), (xv, yD9)], W2)
    # vbn: M12 drain down onto the vbn gate bar
    xn = cx(M12.term('D'))
    xgv = (cx(M9.cols('D')[3]) + cx(M9.cols('S')[3])) / 2       # via on a finger's gate-contact pad
    c.wire('metal2', [(xn, -1.0), (xn, cy(g9)), (xgv, cy(g9))], W2)
    c.via1(xgv, cy(g9))
    # vref: MR1 drain down, across, onto MR2's gate bar
    xrf = cx(MR1.term('D'))
    yjog = yN + 5.5
    c.wire('metal2', [(xrf, -1.0), (xrf, yjog)], W2)
    c.via2(xrf, yjog); c.via2(MR2.x, yjog)
    c.wire('metal3', [(xrf, yjog), (MR2.x, yjog)], W3)                 # crosses the x net in metal3
    xgr = (cx(MR2.cols('S')[1]) + cx(MR2.cols('D')[2])) / 2
    c.wire('metal2', [(MR2.x, yjog), (xgr, yjog), (xgr, cy(gR2))], W2)
    c.via1(xgr, cy(gR2))
    # x: MS2 drains -> MS3 gate and MS1a drain
    yX = col_strap(c, MS2, 'D', +1.75)
    gS3 = MS3.term('G')
    xg3 = MS3.x + 0.6
    c.wire('metal2', [(cx(MS2.cols('D')[-1]), yX), (xg3, yX), (xg3, cy(gS3))], W2)
    c.via1(xg3, cy(gS3))
    dA = MS1[0].term('D')                                  # MS1a ('h'): drain on the right
    xX = cx(MS2.cols('D')[-1])
    c.wire('metal2', [(xX, yX), (xX, MS1[0].y), (cx(dA), MS1[0].y)], W2)
    c.via1(cx(dA), MS1[0].y)
    # vbp also to MS3 drain: metal3 from the M9 drain strap
    dS3 = MS3.term('D')
    c.via2(xv, yD9)
    c.wire('metal3', [(xv, yD9), (xv, yN - 3.0), (cx(dS3), yN - 3.0), (cx(dS3), cy(dS3))], W3)
    c.via2(cx(dS3), cy(dS3)); c.via1(cx(dS3), cy(dS3))
    # vss: sources of M10, MS2, MR2, MS3 on one metal2 strap; ring taps
    yV = yN - 1.75
    for d in (M10, MS2, MR2):
        for col in d.cols('S'):
            c.via1(cx(col), yV)
    sS3 = MS3.term('S')
    c.via1(cx(sS3), cy(sS3))
    c.wire('metal2', [(cx(sS3), cy(sS3)), (cx(sS3), yV)], W2)
    x_vss0 = cx(M10.cols('S')[0])
    c.wire('metal2', [(x_vss0, yV), (cx(sS3), yV)], W2)
    for d in (M9, M10, MS2, MR2, MS3, RS):
        ring_tap(c, d, 'b', d.x)
    xt, yt = ring_tap(c, M10, 'b', M10.x + 0.9)
    c.via1(xt, yt)
    c.wire('metal2', [(xt, yt), (xt, yV)], W2)

    # rs: RS top terminal -> M9 source strap
    r1, r2 = RS.term('R1'), RS.term('R2')
    c.via1(cx(r1), cy(r1))
    c.wire('metal2', [(cx(r1), cy(r1)), (cx(r1), yS9), (cx(M9.cols('S')[0]), yS9)], W2)
    # RS bottom (vss) -> vss strap, along the bottom
    yB = cy(r2)
    c.via1(cx(r2), yB)
    c.wire('metal2', [(cx(r2), yB), (x_vss0, yB), (x_vss0, yV)], W2)

    # ---------------------------------------------------------------- start-up stack
    x_out_l, x_out_r = xs - 11.4, xs + 11.4
    for i, (up, dn) in enumerate(zip(MS1, MS1[1:])):
        s, d = up.term('S'), dn.term('D')
        right = cx(s) > xs
        xo = x_out_r if right else x_out_l
        c.wire('metal1', [(cx(s), up.y), (xo, up.y), (xo, dn.y), (cx(d), dn.y)], W1)
    # MS1f source = vdd: out to the right, metal3 down to the PMOS vdd strap
    sF = MS1[-1].term('S')
    c.wire('metal1', [(cx(sF), MS1[-1].y), (x_out_r, MS1[-1].y)], W1)
    c.via1(x_out_r, MS1[-1].y); c.via2(x_out_r, MS1[-1].y)
    c.wire('metal3', [(x_out_r, MS1[-1].y), (x_out_r, 1.0), (cx(MR1.term('S')), 1.0)], W3)
    c.via2(cx(MR1.term('S')), 1.0)
    # gates = vss: via1 on each gate bar near its left end, metal2 out to a spine at the far left
    xg, xsp = xs - 9.7, RS.x - 2.0
    for d in MS1:
        g = d.term('G')
        c.via1(xg, cy(g))
        c.wire('metal2', [(xg, cy(g)), (xsp, cy(g))], W2)
    c.wire('metal2', [(xsp, cy(MS1[-1].term('G'))), (xsp, yB), (cx(r2), yB)], W2)

    # ---------------------------------------------------------------- ports
    c.label('vdd', 'metal3', x_out_r - 0.2, MS1[-1].y - 0.2, x_out_r + 0.2, MS1[-1].y + 0.2, port=1)
    c.label('vss', 'metal2', xsp - 0.15, yB - 0.15, xsp + 0.15, yB + 0.15, port=2)
    c.label('vbp', 'metal3', cx(dS3) - 0.2, yN - 3.2, cx(dS3) + 0.2, yN - 2.8, port=3)
    c.label('vref', 'metal2', MR2.x - 0.15, yjog - 0.15, MR2.x + 0.15, yjog + 0.15, port=4)
    c.ports = dict(vdd=(x_out_r, MS1[-1].y), vss=(xsp, yB), vbp=(cx(dS3), yN - 3.0), vref=(MR2.x, yjog),
                   vref_m3=(xrf, MR2.x, yjog))
    return c

if __name__ == '__main__':
    import lay, re
    c = build()
    lay.run_magic(c.save_tcl(), 'build_bias')
    n, whys = lay.drc('bias')
    print('DRC', n); print('\n'.join(whys[:40]))
    txt = open('../design/xschem/netlist/lvs/eeg_afe_top.spice').read()
    blk = re.search(r'\.subckt bias .*?\.ends', txt, re.S).group(0)
    blk = '\n'.join(l for l in blk.splitlines() if not l.startswith('XCREF'))
    open('../mag/bias_noCREF.spice', 'w').write(blk + '\n')
    ok, txt = lay.lvs('bias', 'bias_noCREF.spice', 'bias')
    print('LVS', 'OK' if ok else 'FAIL')
    if not ok:
        print('\n'.join(l for l in txt.splitlines() if re.search('Mismatch|Number of|Final', l)))
