"""eeg_afe_core: the whole front-end in Tiny Tapeout tile coordinates (0..161 x 0..225.76 um).

Left column : OTA (top), bias (middle), feedback parts PR1/PR2, SW1/SW2, C2/C2' (x 49..65), CREF (bottom)
Gutter      : metal3 trunks inn (66.2), inp (67.2), vout (68.2), z (68.95)
Right column: C1 (3x3 MIM, bottom, near ua[0]), C1' (3x3 MIM), Cc (2x1 MIM, top)
Power       : vdd trunk (metal3, x = 2) under the VDPWR stripe, vss trunk (x = 5) under VGND
Ports (LVS against eeg_afe_top): ua0 ua1 rst vdd vss
"""
from lay import Cell, Placed
from route import *
import blk_ota, blk_bias, blk_pseudo_r

TILE_W, TILE_H = 161.0, 225.76
X_INN, X_INP, X_VOUT, X_Z = 66.2, 67.2, 68.2, 68.95
X_VDD, X_VSS = 2.0, 5.0
X_VREF, X_RST = 48.2, 62.5
UA0_X, UA1_X, RST_PIN_X = 152.26, 132.94, 138.46
Y_PIN_TOP = 224.76

def mim_bars(c, mim, x0, x1):
    """Return the m4 top-plate column rects and the m3 extent of a placed MIM array."""
    tops = [mim.tb(b[1]) for k, v in mim.g.terms.items() if k.startswith('C1') for b in v]
    return tops

def build(name='eeg_afe_core'):
    c = Cell(name)
    # ---------------------------------------------------------------- blocks
    OTA_O, BIAS_O = (37.0, 98.0), (19.0, 67.0)
    PR1_O, PR2_O = (50.5, 86.0), (50.5, 77.0)
    ota = blk_ota.build(); bias = blk_bias.build(); prb = blk_pseudo_r.build()
    c.place('ota', 'XA1', *OTA_O)
    c.place('bias', 'XBIAS', *BIAS_O)
    c.place('pseudo_r', 'XPR1', *PR1_O)
    c.place('pseudo_r', 'XPR2', *PR2_O)
    po, pb, pp = ota.ports, bias.ports, prb.ports
    A = lambda o, x, y: (o[0] + x, o[1] + y)

    # MIM capacitors.  Bottom plates are reached through the generator's metal4 strips (C2_x);
    # top plates are the metal4 columns (C1_x).  Metal3 and via stacks stay >= 1.34 um from capm.
    xm = 70.9 + 44.97                                   # MIM column: x 70.9 .. 160.84
    C1 = c.place('mim_256_3x3', 'XC1', xm, 5.0 + 41.4)
    C1p = c.place('mim_256_3x3', 'XC1p', xm, 90.75 + 41.4)
    Cc = c.place('mim_2225_2x1', 'XCc', 70.9 + 26.075, 176.55 + 11.325)
    CREF = c.place('mim_2225_2x1', 'XCREF', 34.0, 21.0)
    C2 = c.place('mim_86', 'XC2', 55.0, 64.0, 'h')
    C2p = c.place('mim_86', 'XC2p', 55.0, 53.0, 'h')
    SW1 = c.place('n042_015', 'XSW1', 63.0, 64.0)
    SW2 = c.place('n042_015', 'XSW2', 63.0, 53.0)

    def plates(m, kind):           # kind 'C1' = top-plate columns, 'C2' = bottom-plate strips
        return [m.tb(v[0][1]) for k, v in m.g.terms.items() if k.startswith(kind)]

    def bar(m, kind, side, y1, y2, x1=None, x2=None):
        """Extend the plates of `kind` to a metal4 bar between y1 and y2 below/above the array."""
        ps = plates(m, kind)
        for p in ps:
            if side == 'below':
                c.rect('metal4', p[0], y1, p[2], p[1] + 0.05)
            else:
                c.rect('metal4', p[0], p[3] - 0.05, p[2], y2)
        c.rect('metal4', min([p[0] for p in ps] + ([x1] if x1 is not None else [])), y1,
               max([p[2] for p in ps] + ([x2] if x2 is not None else [])), y2)

    # C1: vin = bottom plates (bar below, straight onto the ua[0] pin), inn = top plates (bar above)
    bar(C1, 'C2', 'below', 3.9, 4.4)
    c.rect('metal4', UA0_X - 0.45, 0.9, UA0_X + 0.45, 4.4)
    bar(C1, 'C1', 'above', 88.3, 88.8, x1=69.5)
    c.via3(69.75, 88.55); c.via2(69.75, 88.55)
    c.wire('metal2', [(69.75, 88.55), (X_INN, 88.55)], W2); c.via2(X_INN, 88.55)
    # C1': vss = bottom plates (bar below), inp = top plates (bar above)
    bar(C1p, 'C2', 'below', 89.4, 89.9, x1=68.8)
    y_vb = 89.65
    c.via3(69.05, y_vb); c.via2(69.05, y_vb)
    c.wire('metal2', [(69.05, y_vb), (X_VSS, y_vb)], W2); c.via2(X_VSS, y_vb)
    bar(C1p, 'C1', 'above', 174.05, 174.55, x1=69.5)
    y_inp = 174.3
    c.via3(69.75, y_inp); c.via2(69.75, y_inp)
    c.wire('metal2', [(69.75, y_inp), (69.75, y_inp - 2.0), (X_INP, y_inp - 2.0)], W2)
    c.via2(X_INP, y_inp - 2.0)
    # Cc: z = top plates (bar below), vout = bottom plates (bar above, onto the vout trunk)
    bar(Cc, 'C1', 'below', 175.55, 176.05, x1=69.35)
    y_z = 175.8
    c.via3(69.6, y_z)
    zx, zy = A(OTA_O, *po['z'])
    c.wire('metal3', [(69.6, y_z), (X_Z, y_z), (X_Z, zy)], W3)
    c.rect('metal3', X_Z - 0.2, y_z - 0.25, 69.85, y_z + 0.25)          # fill the corner (no notch)
    c.via2(X_Z, zy)
    c.wire('metal2', [(zx, zy), (X_Z, zy)], W2)                      # the OTA already has a via1 on Rz
    bar(Cc, 'C2', 'above', 199.7, 200.2, x1=67.95)
    c.via3(X_VOUT, 199.95)
    # CREF: vss = bottom plates (bar below, to the vss trunk), vref = top plates (bar above)
    bar(CREF, 'C2', 'below', 8.675, 9.175, x1=X_VSS - 0.25)
    c.via3(X_VSS, 8.925)
    bar(CREF, 'C1', 'above', 32.825, 33.325, x2=X_VREF + 0.25)
    c.rect('metal4', X_VREF - 0.25, 33.0, X_VREF + 0.25, 34.85)
    c.via3(X_VREF, 34.6)
    y_cr = 34.6

    # ---------------------------------------------------------------- trunks
    ota_inn_x, ota_inn_y0 = OTA_O[0] + po['inn'][0], OTA_O[1] + po['inn'][1]
    ota_inp_y0 = OTA_O[1] + po['inp'][1]
    ota_out_y0 = OTA_O[1] + po['out'][1]
    riser(c, X_INN, 63.6, ota_inn_y0)
    riser(c, X_INP, 52.0, ota_inp_y0)
    riser(c, X_VOUT, 1.6, ota_out_y0)
    riser(c, X_VREF, y_cr, 79.0)

    # vout -> ua[1] along the bottom (metal2 under C1)
    c.via2(X_VOUT, 1.6)
    c.wire('metal2', [(X_VOUT, 1.6), (UA1_X, 1.6), (UA1_X, 0.5)], W2)
    c.via2(UA1_X, 0.5); c.via3(UA1_X, 0.5)

    # ---------------------------------------------------------------- feedback parts
    # PR1: a -> inn (extend its a bus to the inn trunk), b -> vout (metal2 hop over inn/inp)
    ax, ay = A(PR1_O, *pp['a'])
    c.wire('metal2', [(ax, ay), (X_INN, ay)], W2); c.via2(X_INN, ay)
    bx, by = A(PR1_O, *pp['b'])
    c.wire('metal1', [(bx, by), (65.5, by)], W1)
    c.via1(65.5, by)
    c.wire('metal2', [(65.5, by), (X_VOUT, by)], W2); c.via2(X_VOUT, by)
    # PR2: a -> inp, b -> vref (metal2 over the top of PR2 to the vref trunk)
    ax, ay = A(PR2_O, *pp['a'])
    c.wire('metal2', [(ax, ay), (X_INP, ay)], W2); c.via2(X_INP, ay)
    bx, by = A(PR2_O, *pp['b'])
    c.wire('metal1', [(bx, by), (65.2, by)], W1)
    c.via1(65.2, by)
    c.wire('metal2', [(65.2, by), (65.2, 79.0), (X_VREF, 79.0)], W2); c.via2(X_VREF, 79.0)
    # rst bars of PR1/PR2 -> rst trunk
    for o in (PR1_O, PR2_O):
        x0, x1, yg = pp['rst_span']
        c.wire('metal3', [(o[0] + x1, o[1] + yg), (X_RST, o[1] + yg)], W3)

    # C2 ('h'): bottom plate (m3) = vout from the right; top plate (m4 pad, right side) = inn
    b = C2.bbox
    c.via2(b[2] + 0.22, b[1] + 1.0)
    c.wire('metal2', [(b[2] + 0.22, b[1] + 1.0), (X_VOUT, b[1] + 1.0)], W2); c.via2(X_VOUT, b[1] + 1.0)
    t = C2.tb(C2.g.terms['C1'][0][1])
    yt = b[3] - 2.0
    c.rect('metal4', t[0] + 1.0, yt - 0.3, X_INN + 0.25, yt + 0.3)
    c.via3(X_INN, yt)
    # C2' ('h'): bottom = vref from the vref trunk (m3 touching the plate), top = inp
    b = C2p.bbox
    c.wire('metal3', [(X_VREF, b[1] + 4.5), (b[0] + 0.2, b[1] + 4.5)], W3)
    t = C2p.tb(C2p.g.terms['C1'][0][1])
    yt = b[3] - 1.6
    c.rect('metal4', t[0] + 1.0, yt - 0.3, X_INP + 0.25, yt + 0.3)
    c.via3(X_INP, yt)

    # SW1: D (left) = inn, S (right) = vout, G = rst ; SW2: D = inp, S = vref, G = rst
    for sw, xd_net, xs_net, dy in ((SW1, X_INN, X_VOUT, 1.6), (SW2, X_INP, None, 1.6)):
        d, s_, g = sw.term('D'), sw.term('S'), sw.term('G')
        y0 = sw.y
        c.wire('metal1', [(cx(d), y0), (61.9, y0)], W1); c.via1(61.9, y0)
        c.wire('metal2', [(61.9, y0), (61.9, y0 + dy), (xd_net, y0 + dy)], W2); c.via2(xd_net, y0 + dy)
        c.wire('metal1', [(cx(s_), y0), (64.6, y0)], W1); c.via1(64.6, y0)
        if xs_net is not None:
            c.wire('metal2', [(64.6, y0), (64.6, y0 - 1.0), (xs_net, y0 - 1.0)], W2); c.via2(xs_net, y0 - 1.0)
        else:   # vref: down and left under C2' to its bottom plate edge
            c.wire('metal2', [(64.6, y0), (64.6, y0 - 1.0), (C2p.bbox[2] + 0.22, y0 - 1.0)], W2)
            c.via2(C2p.bbox[2] + 0.22, y0 - 1.0)
        # gate -> rst trunk.  SW1 uses its bottom gate pad, SW2 its top pad (SW2's vref route runs
        # left along the bottom).  No mcon on the guard ring: the ring reaches vss through the substrate.
        gb = (g[0], 2 * sw.y - g[3], g[2], 2 * sw.y - g[1])
        if sw is SW1:
            c.rect('metal1', gb[0], gb[1] - 0.4, gb[2], gb[3])
            yv = gb[1] - 0.3
            c.rect('metal1', g[0], g[1], g[2], g[3] + 0.08)             # unused top pad: min area
        else:
            c.rect('metal1', g[0], g[1], g[2], g[3] + 0.46)
            yv = g[3] + 0.3
            c.rect('metal1', gb[0], gb[1] - 0.08, gb[2], gb[3])          # unused bottom pad: min area
        c.via1(cx(gb), yv)
        c.wire('metal2', [(cx(gb), yv), (X_RST, yv)], W2)
        c.via2(X_RST, yv)
        c.rect('metal2', X_RST - 0.21, yv - 0.21, cx(gb) + 0.16, yv + 0.21)   # no notch between the pads
    riser(c, X_RST, SW2.y - 1.6, 91.0)

    # ---------------------------------------------------------------- rst from ui_in[0] (metal2 under the MIMs)
    y_rt = 91.0
    c.via2(X_RST, y_rt)
    c.wire('metal2', [(X_RST, y_rt), (RST_PIN_X, y_rt), (RST_PIN_X, Y_PIN_TOP - 0.45)], W2)
    c.via2(RST_PIN_X, Y_PIN_TOP - 0.45); c.via3(RST_PIN_X, Y_PIN_TOP - 0.45)
    c.rect('metal4', RST_PIN_X - 0.15, Y_PIN_TOP - 0.75, RST_PIN_X + 0.15, Y_PIN_TOP + 0.2)

    # ---------------------------------------------------------------- bias <-> OTA, power
    # vbp: bias vbp metal3 extended left, then up along x = 7.4 to the OTA vbp riser
    vbx, vby = A(BIAS_O, *pb['vbp'])
    x_vbp = OTA_O[0] + po['vbp'][0]
    c.wire('metal3', [(BIAS_O[0] - 1.15, vby), (x_vbp, vby), (x_vbp, OTA_O[1] + po['vbp'][1])], W3)
    # vref: bias vref metal3 extended right to the vref trunk
    rfx, rfy = A(BIAS_O, *pb['vref'])
    c.wire('metal3', [(rfx, rfy), (X_VREF, rfy)], W3)
    # vdd: OTA vdd riser and bias vdd -> vdd trunk (metal2 hops over vbp / vss)
    x_ovdd = OTA_O[0] + po['vdd'][0]; y_ovdd = OTA_O[1] + po['vdd'][2] - 0.6
    c.via2(x_ovdd, y_ovdd)
    c.wire('metal2', [(x_ovdd, y_ovdd), (X_VDD, y_ovdd)], W2); c.via2(X_VDD, y_ovdd)
    bvx, bvy = A(BIAS_O, *pb['vdd'])
    c.wire('metal3', [(bvx, bvy), (bvx, 90.75)], W3); c.via2(bvx, 90.75)
    c.wire('metal2', [(bvx, 90.75), (X_VDD, 90.75)], W2); c.via2(X_VDD, 90.75)
    riser(c, X_VDD, 90.75, y_ovdd)
    # vss: OTA, bias, CREF, C1' -> vss trunk
    ovx, ovy = A(OTA_O, *po['vss'])
    c.wire('metal2', [(ovx, ovy), (X_VSS, ovy)], W2); c.via2(X_VSS, ovy)
    bsx, bsy = A(BIAS_O, *pb['vss'])
    c.wire('metal2', [(bsx, bsy), (X_VSS, bsy)], W2); c.via2(X_VSS, bsy)
    riser(c, X_VSS, 8.925, Y_PIN_TOP - 1.46)
    # via3 stacks onto the power stripes (drawn in the Tiny Tapeout top cell)
    for y in (100.0, 150.0, 200.0):
        c.via3(X_VDD, y); c.via3(X_VSS, y)
    c.via3(X_VSS, 30.0); c.via3(X_VSS, 60.0)

    # ---------------------------------------------------------------- ports
    c.label('ua0', 'metal4', UA0_X - 0.2, 2.0, UA0_X + 0.2, 2.4, port=1)
    c.label('ua1', 'metal2', UA1_X - 0.15, 1.45, UA1_X + 0.15, 1.75, port=2)
    c.label('rst', 'metal2', RST_PIN_X - 0.15, 150.0, RST_PIN_X + 0.15, 150.3, port=3)
    c.label('vdd', 'metal3', X_VDD - 0.2, 120.0, X_VDD + 0.2, 120.4, port=4)
    c.label('vss', 'metal3', X_VSS - 0.2, 120.0, X_VSS + 0.2, 120.4, port=5)
    return c

if __name__ == '__main__':
    import lay, re
    c = build()
    out = lay.run_magic(c.save_tcl(), 'build_core')
    print('\n'.join(l for l in out.splitlines() if 'rror' in l)[:1500])
    n, whys = lay.drc('eeg_afe_core')
    print('DRC', n); print('\n'.join(whys[:60]))
