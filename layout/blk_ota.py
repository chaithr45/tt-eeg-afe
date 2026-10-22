"""OTA (two-stage Miller, PMOS input) without its compensation capacitor Cc (placed with the MIMs).

From bottom to top:
  M6 (5/2 x4) and Rz (xhigh_po 0.35 x 3.3)
  current mirror: three rows, M3a-c left / M4a-c right (7/20 each, series stacks)
  input pair: ten rows of 6-finger 5/8 PMOS, A = M1 (inn -> d1), B = M2 (inp -> y),
              rows A B B A A B A B B A (centroids 4.4 / 4.6)
  M7 (two 10-finger 4/2 PMOS) and M5 (8-finger 4/2 PMOS)
Vertical metal3 risers carry t (left), vdd, vbp (far left) and d1, y, inn, inp, out (right); the
track between inp and out (X_SHIELD) is left free for a vss shield drawn by the core cell.
A metal1 line on t between the top input row and M7 shields inn from vdd / vbp.
Parasitic-driven choices (from post-layout simulation): inp is kept away from out (closed-loop gain),
and the input pair is spaced from M7 / M5 (supply rejection).
Ports: inn inp out vdd vss vbp z
"""
from lay import Cell
from route import *

X_T, X_VDD, X_VBP = -27.2, -28.4, -29.6
X_D1, X_Y, X_INN, X_INP, X_OUT = 26.2, 27.2, 28.2, 29.2, 31.2
X_SHIELD = 30.2                 # vss shield track between inp and out (drawn by the core cell)
GAP7 = 1.5                      # extra space between the input pair and M7 / M5 (less vdd / vbp on inn)
PAIR = 'ABBAABABBA'

def build(name='ota'):
    c = Cell(name)
    # ---------------------------------------------------------------- placement
    y_m6 = 0.0
    M6 = c.place('n5_2_nf4', 'M6', 14.0, y_m6)
    Rz = c.place('rxh_3p3', 'Rz', 25.0, y_m6 - 0.5)
    yr = [27.9, 18.7, 9.5]                      # mirror rows a, b, c
    M3 = [c.place('n7_20', f'M3{k}', -12.0, yr[i]) for i, k in enumerate('abc')]
    M4 = [c.place('n7_20', f'M4{k}', 12.0, yr[i], 'h') for i, k in enumerate('abc')]
    yp = [37.5 + 7.2 * k for k in range(10)]
    P = []
    na = nb = 0
    for k, ab in enumerate(PAIR):
        if ab == 'A':
            P.append(('A', c.place('p5_8_nf6', f'M1_{na}', 0.0, yp[k]))); na += 1
        else:
            P.append(('B', c.place('p5_8_nf6', f'M2_{nb}', 0.0, yp[k]))); nb += 1
    y7 = yp[-1] + 3.6 + 1.5 + 3.1 + GAP7  # n-well (t) to n-well (vdd) >= 1.27
    M7a = c.place('p4_2_nf10', 'M7_0', -12.6, y7)
    M7b = c.place('p4_2_nf10', 'M7_1', 12.6, y7)
    y5 = y7 + 6.2                          # M5 n-well abuts M7's (both vdd)
    M5 = c.place('p4_2_nf8', 'M5', 0.0, y5)

    # one continuous n-well (net t) under the ten input-pair rows
    c.rect('nwell', P[0][1].bbox[0], P[0][1].bbox[1], P[0][1].bbox[2], P[-1][1].bbox[3])
    # one continuous vdd n-well under M7a, M7b and M5
    c.rect('nwell', M7a.bbox[0], M7a.bbox[1], M7b.bbox[2], M5.bbox[3])

    # ---------------------------------------------------------------- input pair
    for ab, d in P:
        xd = X_D1 if ab == 'A' else X_Y
        xg = X_INN if ab == 'A' else X_INP
        yD = col_strap(c, d, 'D', +1.25, x_to=xd)
        c.via2(xd, yD)
        yS = col_strap(c, d, 'S', -1.25, x_to=X_T)
        c.via2(X_T, yS)
        g = d.term('G')
        m1_to(c, g[2] - 0.1, xg, cy(g))
        c.via1(xg, cy(g)); c.via2(xg, cy(g))
        # bulk ring -> t (left side)
        xr, yr_ = ring_tap(c, d, 'l', d.y)
        m1_to(c, X_T, xr, d.y)
        c.via1(X_T, d.y); c.via2(X_T, d.y)

    # t shield (metal1) between the top input row (an inn row) and the M7 row, so that vdd and vbp
    # (which carries supply ripple) do not couple onto inn only
    top = P[-1][1]
    y_sh = (top.bbox[3] + M7a.bbox[1]) / 2
    m1_to(c, X_T, top.bbox[2], y_sh)
    c.via1(X_T, y_sh); c.via2(X_T, y_sh)

    # ---------------------------------------------------------------- M7, M5 (vdd sources, gate vbp)
    for d in (M7a, M7b, M5):
        yS = col_strap(c, d, 'S', -1.0, x_to=X_VDD)
        c.via2(X_VDD, yS)
        xr, _ = ring_tap(c, d, 'l', yS)
        c.via1(xr, yS)
        g = d.term('G')
        m1_to(c, X_VBP, g[0] + 0.1, cy(g))
        c.via1(X_VBP, cy(g)); c.via2(X_VBP, cy(g))
    # M7 drains -> out (strap across both devices to the out riser)
    yD7 = M7a.y + 1.0
    for d in (M7a, M7b):
        col_strap(c, d, 'D', +1.0, x_to=X_OUT)
    c.via2(X_OUT, yD7)
    # M5 drain -> t
    yD5 = col_strap(c, M5, 'D', +1.0, x_to=X_T)
    c.via2(X_T, yD5)

    # ---------------------------------------------------------------- mirror
    # gates: bridge left/right gate bars in each row, metal2 spine at x = 0
    for a, b in zip(M3, M4):
        ga, gb = a.term('G'), b.term('G')
        m1_to(c, ga[2] - 0.1, gb[0] + 0.1, cy(ga))
        c.via1(0.0, cy(ga))
    ytop_g, ybot_g = cy(M3[0].term('G')), cy(M3[2].term('G'))
    riser(c, 0.0, ybot_g, ytop_g, 'metal2', W2)
    # d1: riser down to mirror row a, across to M3a drain; the gate spine joins it
    y_d1 = yr[0] + 2.0
    riser(c, X_D1, y_d1, yp[-1] + 1.25)
    c.wire('metal3', [(X_D1, y_d1), (cx(M3[0].term('D')), y_d1)], W3)
    c.via2(cx(M3[0].term('D')), y_d1); c.via1(cx(M3[0].term('D')), y_d1)
    c.via2(0.0, y_d1)
    # y: riser down to M6's gate; branch to M4a's drain
    y_y = yr[0] + 1.0
    g6 = M6.term('G')
    riser(c, X_Y, min(cy(g6), cy(Rz.term('R1'))), yp[-1] + 1.25)
    c.wire('metal3', [(X_Y, y_y), (cx(M4[0].term('D')), y_y)], W3)
    c.via2(cx(M4[0].term('D')), y_y); c.via1(cx(M4[0].term('D')), y_y)
    m1_to(c, g6[2] - 0.1, X_Y, cy(g6))
    c.via1(X_Y, cy(g6)); c.via2(X_Y, cy(g6))
    # series connections a -> b -> c on both sides (source column of the upper device to the
    # drain column of the lower device, metal2 jog between the rows)
    for side in (M3, M4):
        for up, dn in zip(side, side[1:]):
            s, d = up.term('S'), dn.term('D')
            ym = (up.y + dn.y) / 2
            c.via1(cx(s), up.y - 2.5); c.via1(cx(d), dn.y + 2.5)
            c.wire('metal2', [(cx(s), up.y - 2.5), (cx(s), ym), (cx(d), ym), (cx(d), dn.y + 2.5)], W2)
    # vss: M3c / M4c sources, M6 sources, guard rings
    y_vss = yr[2] - 2.5
    sL, sR = M3[2].term('S'), M4[2].term('S')
    c.via1(cx(sL), y_vss); c.via1(cx(sR), y_vss)
    c.wire('metal2', [(cx(sL), y_vss), (cx(sR), y_vss)], W2)
    yS6 = col_strap(c, M6, 'S', -1.25, x_from=-2.0)
    c.wire('metal2', [(cx(sR), y_vss), (cx(sR), yS6), (-2.0, yS6)], W2)
    for d in M3 + M4 + [M6]:
        xr, yt = ring_tap(c, d, 'b', d.x)
    # one ring tap joined to the vss wire (left mirror device c, bottom ring)
    xr, yt = cx(ring_side(M3[2], 'b')) - 3.0, cy(ring_side(M3[2], 'b'))
    c.mcon(xr, yt); c.via1(xr, yt)
    c.wire('metal2', [(xr, yt), (xr, yS6), (-2.0, yS6)], W2)

    # ---------------------------------------------------------------- M6 drain -> out, Rz y -> z
    yD6 = col_strap(c, M6, 'D', +1.25, x_to=X_OUT)
    c.via2(X_OUT, yD6)
    riser(c, X_OUT, yD6, yD7)
    r1, r2 = Rz.term('R1'), Rz.term('R2')
    # R1 (top) -> y riser
    c.via1(cx(r1), cy(r1))
    c.wire('metal2', [(cx(r1), cy(r1)), (X_Y, cy(r1))], W2)
    c.via2(X_Y, cy(r1))
    # fill between the two via2 landing pads on the y riser (avoids a metal3 notch)
    c.wire('metal3', [(X_Y, cy(r1)), (X_Y, cy(M6.term('G')))], 0.5)
    # Rz guard ring (vss)
    ring_tap(c, Rz, 'b', Rz.x)

    # ---------------------------------------------------------------- risers + ports
    riser(c, X_T, yD5, yp[0] - 1.25)
    riser(c, X_INN, min(cy(d.term('G')) for ab, d in P if ab == 'A'), max(cy(d.term('G')) for ab, d in P if ab == 'A') + 0.8)
    riser(c, X_INP, min(cy(d.term('G')) for ab, d in P if ab == 'B'), max(cy(d.term('G')) for ab, d in P if ab == 'B') + 0.8)
    riser(c, X_VDD, M7a.y - 1.0, M5.y + 2.0)
    riser(c, X_VBP, cy(M7a.term('G')), cy(M5.term('G')) + 2.0)
    ytop = M5.y + 2.0
    yinn = max(cy(d.term('G')) for ab, d in P if ab == 'A') + 0.8
    yinp = max(cy(d.term('G')) for ab, d in P if ab == 'B') + 0.8
    c.label('inn', 'metal3', X_INN - 0.2, yinn - 0.4, X_INN + 0.2, yinn, port=1)
    c.label('inp', 'metal3', X_INP - 0.2, yinp - 0.4, X_INP + 0.2, yinp, port=2)
    c.label('out', 'metal3', X_OUT - 0.2, yD7 - 0.2, X_OUT + 0.2, yD7 + 0.2, port=3)
    c.label('vdd', 'metal3', X_VDD - 0.2, ytop - 0.4, X_VDD + 0.2, ytop, port=4)
    c.label('vss', 'metal2', -2.15, yS6 - 0.15, -1.85, yS6 + 0.15, port=5)
    c.label('vbp', 'metal3', X_VBP - 0.2, ytop - 0.4, X_VBP + 0.2, ytop, port=6)
    c.via1(cx(r2), cy(r2))
    c.label('z', 'metal1', cx(r2) - 0.1, cy(r2) - 0.1, cx(r2) + 0.1, cy(r2) + 0.1, port=7)
    gA = [cy(d.term('G')) for ab, d in P if ab == 'A']
    gB = [cy(d.term('G')) for ab, d in P if ab == 'B']
    c.ports = dict(inn=(X_INN, min(gA), yinn), inp=(X_INP, min(gB), yinp), out=(X_OUT, yD6, yD7),
                   vdd=(X_VDD, M7a.y - 1.0, M5.y + 2.0), vbp=(X_VBP, cy(M7a.term('G')), cy(M5.term('G')) + 2.0),
                   vss=(-2.0, yS6), z=(cx(r2), cy(r2)), z_m1=r2)
    return c

if __name__ == '__main__':
    import lay, re, sys
    c = build()
    out = lay.run_magic(c.save_tcl(), 'build_ota')
    errs = [l for l in out.splitlines() if 'rror' in l or 'annot' in l]
    print('\n'.join(errs[:10]))
    n, whys = lay.drc('ota')
    print('DRC', n); print('\n'.join(whys[:40]))
