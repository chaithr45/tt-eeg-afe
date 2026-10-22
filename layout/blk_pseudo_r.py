"""pseudo_r: two back-to-back PMOS pairs (0.42/1 um, each in its own n-well) + three reset switches.

Row 1 (PMOS, mirrored so shared nets sit next to each other):
    Ma1(h) [a | m1]   Mb1 [m1 | n1]   Ma2(h) [n1 | m2]   Mb2 [m2 | b]
Row 2 (NMOS switches under the matching PMOS nets):  S1 (m1->a)  S2 (n1->a)  S3 (m2->a), gates = rst.
Each PMOS bulk (guard ring) is tied to its source, as in the schematic.
Ports: a, b (metal2), rst (metal3), vss (metal1 on the switch guard ring).
"""
from lay import Cell

W1 = 0.23        # metal1 wire width
W2 = 0.3         # metal2 wire width
cx = lambda b: (b[0] + b[2]) / 2
cy = lambda b: (b[1] + b[3]) / 2

def ring_side(dev, side):
    """li segment of a device guard ring on 'l' / 'r' / 't' / 'b' (cell coordinates)."""
    rs = dev.guard()
    if side == 'l':  return min(rs, key=lambda r: r[0])
    if side == 'r':  return max(rs, key=lambda r: r[2])
    if side == 'b':  return min(rs, key=lambda r: r[1])
    return max(rs, key=lambda r: r[3])

def ring_tap(c, dev, side, at):
    """mcon on the guard ring side at coordinate `at` (y for l/r, x for t/b); returns its centre."""
    r = ring_side(dev, side)
    x, y = ((r[0] + r[2]) / 2, at) if side in 'lr' else (at, (r[1] + r[3]) / 2)
    c.mcon(x, y)
    return x, y

def build(name='pseudo_r'):
    c = Cell(name)
    pitch = 2.96 + 1.4                       # n-well spacing between wells of different potential >= 1.27
    y_p, y_n = 0.0, -4.2
    Ma1 = c.place('p042_1', 'Ma1', 0 * pitch, y_p, 'h')
    Mb1 = c.place('p042_1', 'Mb1', 1 * pitch, y_p)
    Ma2 = c.place('p042_1', 'Ma2', 2 * pitch, y_p, 'h')
    Mb2 = c.place('p042_1', 'Mb2', 3 * pitch, y_p)
    S1 = c.place('n042_015', 'S1', 0.5 * pitch, y_n)
    S2 = c.place('n042_015', 'S2', 1.5 * pitch, y_n)
    S3 = c.place('n042_015', 'S3', 2.5 * pitch, y_n)

    # gate-drain ties (diode-connected PMOS): bridge from the gate pad to the drain column
    for d in (Ma1, Mb1, Ma2, Mb2):
        g, dr = d.term('G'), d.term('D')
        if cx(dr) > cx(g):
            c.rect('metal1', g[2] - 0.05, g[1], dr[2], g[3])
        else:
            c.rect('metal1', dr[0], g[1], g[0] + 0.05, g[3])
        c.rect('metal1', dr[0], dr[1], dr[2], g[3])

    # horizontal m1 links between adjacent columns of the same net (row centre)
    def link(t1, t2):
        a, b = sorted((t1, t2))
        c.rect('metal1', a[0], cy(a) - W1 / 2, b[2], cy(a) + W1 / 2)
    link(Ma1.term('D'), Mb1.term('D'))       # m1
    link(Mb1.term('S'), Ma2.term('S'))       # n1
    link(Ma2.term('D'), Mb2.term('D'))       # m2

    # bulk = source: tap the guard ring next to the source column and join with m1
    for dev, side in ((Ma1, 'l'), (Mb1, 'r'), (Ma2, 'l'), (Mb2, 'r')):
        s = dev.term('S')
        x, y = ring_tap(c, dev, side, cy(s))
        c.rect('metal1', min(x, s[0]), cy(s) - W1 / 2, max(x, s[2]), cy(s) + W1 / 2)

    # switches: drain out to the left, source out to the right (m1 on the device centre line,
    # clear of the top and bottom gate contacts), then metal2
    nets_top = {'m1': (Ma1.term('D'), Mb1.term('D')), 'n1': (Mb1.term('S'), Ma2.term('S')),
                'm2': (Ma2.term('D'), Mb2.term('D'))}
    yj = y_n + 2.2                           # drain jog track between the rows
    ybus = y_n - 1.9                         # net a bus below the switches
    for sw, net in ((S1, 'm1'), (S2, 'n1'), (S3, 'm2')):
        t1, t2 = nets_top[net]
        xm, ym = (cx(t1) + cx(t2)) / 2, cy(t1)
        d, s_ = sw.term('D'), sw.term('S')
        yd = cy(d)
        xo, xs = sw.x - 1.45, sw.x + 1.45
        c.rect('metal1', xo, yd - W1 / 2, d[2], yd + W1 / 2)
        c.via1(xo, yd)
        c.via1(xm, ym)
        c.wire('metal2', [(xo, yd), (xo, yj), (xm, yj), (xm, ym)], W2)
        c.rect('metal1', s_[0], yd - W1 / 2, xs, yd + W1 / 2)
        c.via1(xs, yd)
        c.wire('metal2', [(xs, yd), (xs, ybus)], W2)

    # net a also comes from Ma1 (source + bulk), through its left guard-ring tap
    sa = Ma1.term('S')
    xl = cx(ring_side(Ma1, 'l'))
    c.via1(xl, cy(sa))
    c.wire('metal2', [(xl, cy(sa)), (xl, ybus), (S3.x + 1.45, ybus)], W2)

    # switch gates -> rst: gate pad up, via1 + via2, metal3 bar
    yg = y_n + 1.45
    for sw in (S1, S2, S3):
        g = sw.term('G')
        c.rect('metal1', cx(g) - 0.115, g[1], cx(g) + 0.115, yg + 0.16)
        c.via1(cx(g), yg)
        c.via2(cx(g), yg)
        # the generator's bottom gate contact is below metal1 minimum area on its own: enlarge it
        c.rect('metal1', g[0], 2 * sw.y - g[3] - 0.08, g[2], 2 * sw.y - g[1])
    xg0, xg1 = cx(S1.term('G')), cx(S3.term('G'))
    c.wire('metal3', [(xg0, yg), (xg1, yg)], 0.5)

    # vss: mcon on each switch guard ring (bottom side), joined by metal1
    yb = cy(ring_side(S1, 'b'))
    for sw in (S1, S2, S3):
        c.mcon(sw.x, yb)
    c.wire('metal1', [(S1.x, yb), (S3.x, yb)], W1)

    sb = Mb2.term('S')
    c.label('a', 'metal2', xl - 0.15, ybus - 0.15, xl + 0.15, ybus + 0.15, port=1)
    c.label('b', 'metal1', sb[0], cy(sb) - 0.1, sb[2], cy(sb) + 0.1, port=2)
    c.label('rst', 'metal3', xg0 - 0.2, yg - 0.2, xg0 + 0.2, yg + 0.2, port=3)
    c.label('vss', 'metal1', S1.x - 0.1, yb - 0.1, S1.x + 0.1, yb + 0.1, port=4)
    c.ports = dict(a=(xl, ybus), b=(cx(sb), cy(sb)), b_m1=sb, rst=(xg0, yg), rst_span=(xg0, xg1, yg), vss=(S1.x, yb),
                   vss_span=(S1.x, S3.x, yb))
    return c

if __name__ == '__main__':
    import lay, re
    c = build()
    lay.run_magic(c.save_tcl(), 'build_pseudo_r')
    n, whys = lay.drc('pseudo_r')
    print('DRC', n); print('\n'.join(whys[:30]))
    ok, txt = lay.lvs('pseudo_r', '../design/xschem/netlist/lvs/eeg_afe_top.spice', 'pseudo_r')
    print('LVS', 'OK' if ok else 'FAIL')
    if not ok:
        print('\n'.join(l for l in txt.splitlines() if re.search('Mismatch|Number of|Final', l)))
