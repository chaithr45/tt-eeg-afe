"""Small routing helpers shared by the block generators."""

W1 = 0.23        # metal1 wire
W2 = 0.3         # metal2 wire
W3 = 0.4         # metal3 wire

cx = lambda b: (b[0] + b[2]) / 2
cy = lambda b: (b[1] + b[3]) / 2

def ring_side(dev, side):
    """Full-length li segment of a device guard ring on 'l' / 'r' / 't' / 'b' (cell coordinates)."""
    rs = dev.guard()
    x1 = min(r[0] for r in rs); y1 = min(r[1] for r in rs)
    x2 = max(r[2] for r in rs); y2 = max(r[3] for r in rs)
    if side == 'l':
        t = min(r[2] - r[0] for r in rs if abs(r[0] - x1) < 1e-6); return (x1, y1, x1 + t, y2)
    if side == 'r':
        t = min(r[2] - r[0] for r in rs if abs(r[2] - x2) < 1e-6); return (x2 - t, y1, x2, y2)
    if side == 'b':
        t = min(r[3] - r[1] for r in rs if abs(r[1] - y1) < 1e-6); return (x1, y1, x2, y1 + t)
    t = min(r[3] - r[1] for r in rs if abs(r[3] - y2) < 1e-6); return (x1, y2 - t, x2, y2)

def ring_tap(c, dev, side, at):
    """mcon on a guard-ring side at `at` (y for l/r, x for t/b); returns the centre."""
    r = ring_side(dev, side)
    x, y = ((r[0] + r[2]) / 2, at) if side in 'lr' else (at, (r[1] + r[3]) / 2)
    c.mcon(x, y)
    return x, y

def col_strap(c, dev, kind, yrel, x_to=None, x_from=None):
    """via1 on every `kind` ('D'/'S') column of dev at dev.y + yrel and a metal2 strap through them,
    extended to x_to / x_from if given. Returns the strap y."""
    cols = dev.cols(kind)
    y = dev.y + yrel
    xs = [cx(b) for b in cols]
    for x in xs:
        c.via1(x, y)
    a, b = min(xs), max(xs)
    if x_to is not None:
        a, b = min(a, x_to), max(b, x_to)
    if x_from is not None:
        a, b = min(a, x_from), max(b, x_from)
    c.wire('metal2', [(a, y), (b, y)], W2)
    return y

def gate_bar(dev):
    return dev.term('G')

def m1_to(c, x1, x2, y):
    c.wire('metal1', [(x1, y), (x2, y)], W1)

def riser(c, x, y1, y2, layer='metal3', w=W3):
    c.wire(layer, [(x, y1), (x, y2)], w)
