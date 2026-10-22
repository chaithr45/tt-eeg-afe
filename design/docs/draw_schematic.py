import schemdraw, schemdraw.elements as elm
schemdraw.use('matplotlib')
FS = 11

def L(d, pts, **kw):
    for a, b in zip(pts[:-1], pts[1:]):
        d.add(elm.Line().endpoints(a, b))

def dot(d, p, open_=False):
    d.add(elm.Dot(open=open_).at(p))

def text(d, p, s, ha='left', va='center', fs=FS, color='black'):
    d.add(elm.Label().at(p).label(s, halign=ha, valign=va, fontsize=fs, color=color))

def fet(d, kind, x, ytop, gate='right', name=None):
    e = (elm.PFet() if kind == 'p' else elm.NFet()).right()
    if gate == 'left':
        e = e.reverse()
    d.add(e.at((x, ytop)))
    if name:
        if gate == 'right':
            text(d, (x - 0.25, ytop - 0.75), name, ha='right')
        else:
            text(d, (x + 0.25, ytop - 0.75), name, ha='left')
    gx = x + 1.37 if gate == 'right' else x - 1.37
    return (gx, ytop - 0.75), (x, ytop - 1.5)

def title(d, p, s, sub):
    text(d, p, s, fs=15)
    text(d, (p[0], p[1] - 0.7), sub, fs=10, color='#555555')

# ---------------- Sheet 1: system ----------------
def sheet1():
    d = schemdraw.Drawing(show=False); d.config(fontsize=FS)
    title(d, (0.5, 8.6), 'Sheet 1 of 4 — Neonatal EEG front-end (top level, simulated design v1)',
          'Capacitive-feedback amplifier · SKY130 · Tiny Tapeout 1x2 tile · ua[0] in, ua[1] out, ui_in[0] = rst')
    a1 = d.add(elm.Opamp(leads=True).at((8, 0)))
    dot(d, (1.5, 0.62), open_=True)
    text(d, (1.2, 0.62), 'ua[0]\nVIN (electrode)', ha='right')
    L(d, [(1.5, 0.62), (3.5, 0.62)])
    d.add(elm.Capacitor().endpoints((3.5, 0.62), (6.0, 0.62)).label('C1  11.9 pF', loc='top'))
    L(d, [(6.0, 0.62), (8.0, 0.62)])
    dot(d, (7.0, 0.62)); text(d, (6.9, 1.0), 'inn', ha='right', fs=9)
    L(d, [(7.0, 0.62), (7.0, 5.4)])
    dot(d, (7.0, 2.6)); dot(d, (7.0, 4.0))
    d.add(elm.Capacitor().endpoints((7.0, 2.6), (12.5, 2.6)).label('C2  154 fF', loc='top'))
    d.add(elm.ResistorIEC().endpoints((7.0, 4.0), (12.5, 4.0)).label('PR1  pseudo-resistor (sheet 3)', loc='top'))
    d.add(elm.Switch().endpoints((7.0, 5.4), (12.5, 5.4)).label('S1  reset (rst)', loc='top'))
    L(d, [(12.5, 5.4), (12.5, 0.0)])
    dot(d, (12.5, 2.6)); dot(d, (12.5, 4.0))
    L(d, [(11.42, 0.0), (15.5, 0.0)])
    dot(d, (12.5, 0.0))
    dot(d, (15.5, 0.0), open_=True)
    text(d, (15.8, 0.0), 'ua[1]\nVOUT (to ADC / scope)')
    text(d, (9.6, -1.9), 'A1  two-stage OTA (sheet 2)', ha='center', fs=10)
    L(d, [(8.0, -0.62), (7.0, -0.62), (7.0, -6.4)])
    text(d, (6.9, -1.0), 'inp', ha='right', fs=9)
    dot(d, (7.0, -2.4)); dot(d, (7.0, -3.6)); dot(d, (7.0, -5.0))
    d.add(elm.Capacitor().endpoints((7.0, -2.4), (4.5, -2.4)).label('C1′  11.9 pF', loc='bottom'))
    L(d, [(4.5, -2.4), (4.5, -3.0)])
    d.add(elm.Ground().at((4.5, -3.0)))
    d.add(elm.Capacitor().endpoints((7.0, -3.6), (10.5, -3.6)).label('C2′  154 fF', loc='top'))
    d.add(elm.ResistorIEC().endpoints((7.0, -5.0), (10.5, -5.0)).label('PR2', loc='top'))
    d.add(elm.Switch().endpoints((7.0, -6.4), (10.5, -6.4)).label('S2  reset (rst)', loc='bottom'))
    L(d, [(10.5, -3.6), (10.5, -6.4)])
    dot(d, (10.5, -3.6)); dot(d, (10.5, -5.0))
    L(d, [(10.5, -5.0), (11.6, -5.0)])
    text(d, (11.7, -5.0), 'VREF ≈ 0.45 V (sheet 3)')
    notes = [
        'Midband gain = C1/C2 = 77.5 V/V (37.8 dB). High-pass f_L = 1/(2π·R_PR·C2) ≈ 0.09 Hz; low-pass ≈ 22 kHz (set by OTA bandwidth).',
        'C1′ goes to ground: VREF noise reaches VOUT with gain ≈ 1, not 78, so a simple on-chip VREF is good enough.',
        'S1/S2 are minimum NMOS switches (0.42/0.15 µm) driven by rst = ui_in[0]. Holding rst high forces VOUT = VREF:',
        '     use it for ~10 ms at power-up and after electrode artifacts (pseudo-resistor recovery alone takes seconds).',
        'MIM capacitors: C1/C1′ = cap_mim_m3_1 77×77 µm, C2/C2′ = 8.6×8.6 µm. Unused digital outputs are tied to VGND (not drawn).',
    ]
    for i, n in enumerate(notes):
        text(d, (0.5, -8.0 - 0.6 * i), n, fs=10)
    return d

# ---------------- Sheet 2: OTA ----------------
def sheet2():
    d = schemdraw.Drawing(show=False); d.config(fontsize=FS)
    title(d, (-1.5, 2.6), 'Sheet 2 of 4 — A1: two-stage Miller OTA',
          'PMOS input pair, NMOS mirror load (3-device stacks for low 1/f noise), NMOS common-source 2nd stage, Rz–Cc compensation')
    L(d, [(0.5, 0), (13.5, 0)]); text(d, (0.3, 0), 'VDD 1.8 V', ha='right')
    L(d, [(0.5, -9.5), (13.5, -9.5)]); text(d, (0.3, -9.5), 'VGND', ha='right')
    # M5 tail
    L(d, [(4, 0), (4, -0.5)])
    g5, b5 = fet(d, 'p', 4, -0.5, gate='left', name='M5')
    L(d, [g5, (1.9, -1.25)]); text(d, (1.8, -1.25), 'VBP', ha='right')
    L(d, [b5, (4, -2.5)]); dot(d, (4, -2.5)); text(d, (4.15, -2.85), 'T', fs=10)
    L(d, [(2, -2.5), (6, -2.5)])
    L(d, [(2, -2.5), (2, -3)]); L(d, [(6, -2.5), (6, -3)])
    g1, b1 = fet(d, 'p', 2, -3, gate='left', name='M1')
    L(d, [g1, (0.2, -3.75)]); text(d, (0.1, -3.75), 'IN−', ha='right')
    g2, b2 = fet(d, 'p', 6, -3, gate='right', name='M2')
    L(d, [g2, (8.0, -3.75)]); text(d, (8.1, -3.75), 'IN+')
    L(d, [b1, (2, -6)]); L(d, [b2, (6, -6)])
    g3, b3 = fet(d, 'n', 2, -6, gate='right', name='M3 (3-stack)')
    g4, b4 = fet(d, 'n', 6, -6, gate='left', name='M4 (3-stack)')
    L(d, [g3, g4]); dot(d, (4, -6.75))
    L(d, [(4, -6.75), (4, -5.5), (2, -5.5)]); dot(d, (2, -5.5))
    L(d, [b3, (2, -9.5)]); L(d, [b4, (6, -9.5)])
    # Y node -> second stage + compensation
    dot(d, (6, -5.25)); text(d, (5.85, -5.0), 'Y', ha='right', fs=10)
    L(d, [(6, -5.25), (9, -5.25)]); dot(d, (9, -5.25))
    L(d, [(9, -5.25), (9, -6.75), (10.63, -6.75)])
    L(d, [(12, 0), (12, -0.5)])
    g7, b7 = fet(d, 'p', 12, -0.5, gate='left', name='M7')
    L(d, [g7, (9.9, -1.25)]); text(d, (9.8, -1.25), 'VBP', ha='right')
    g6, b6 = fet(d, 'n', 12, -6, gate='left', name='M6')
    L(d, [b7, (12, -6)]); dot(d, (12, -4))
    L(d, [b6, (12, -9.5)])
    L(d, [(9, -5.25), (9, -4)])
    d.add(elm.Resistor().endpoints((9, -4), (10.5, -4)).label('Rz', loc='top'))
    d.add(elm.Capacitor().endpoints((10.5, -4), (12, -4)).label('Cc', loc='top'))
    L(d, [(12, -4), (14, -4)]); text(d, (14.1, -4), 'OUT')
    notes = [
        'IN− = gate of M1 (inverting), IN+ = gate of M2 (non-inverting).',
        'Bulks: M1/M2 tied to tail node T (own n-well); other PMOS to VDD; all NMOS to VGND.',
        'M3 and M4 are each three 7/20 µm NMOS in series (effective L = 60 µm); long L lowers the mirror\'s input-referred 1/f noise.',
        'VBP comes from the bias generator on sheet 3 (0.5 µA per PMOS unit cell 4/2 µm). Sizes on sheet 4.',
    ]
    for i, n in enumerate(notes):
        text(d, (-1.5, -10.6 - 0.6 * i), n, fs=10)
    return d

# ---------------- Sheet 3: bias, VREF, pseudo-resistor ----------------
def sheet3():
    d = schemdraw.Drawing(show=False); d.config(fontsize=FS)
    title(d, (-1.0, 2.6), 'Sheet 3 of 4 — Bias generator, start-up, VREF and pseudo-resistor',
          'Subthreshold beta-multiplier: I_REF ≈ n·U_T·ln(K) / Rs = 0.50 µA at 27 °C (0.43–0.62 µA over corners)  · K = 4, Rs = 92 kΩ')
    L(d, [(0.8, 0), (21.5, 0)]); text(d, (0.6, 0), 'VDD', ha='right')
    L(d, [(0.8, -8.5), (21.5, -8.5)]); text(d, (0.6, -8.5), 'VGND', ha='right')
    text(d, (4, 1.0), 'Beta-multiplier', ha='center', fs=10, color='#555555')
    text(d, (11.8, 1.0), 'Start-up', ha='center', fs=10, color='#555555')
    text(d, (17.5, 1.0), 'VREF', ha='center', fs=10, color='#555555')
    text(d, (25.0, 1.0), 'Pseudo-resistor pair (×2 in series)', ha='center', fs=10, color='#555555')
    # PMOS mirror
    L(d, [(2, 0), (2, -0.5)]); L(d, [(6, 0), (6, -0.5)])
    g11, b11 = fet(d, 'p', 2, -0.5, gate='right', name='M11')
    g12, b12 = fet(d, 'p', 6, -0.5, gate='left', name='M12')
    L(d, [g11, g12]); dot(d, (4, -1.25))
    L(d, [(4, -1.25), (4, -2.6), (2, -2.6)]); dot(d, (2, -2.6))
    L(d, [(2, -2.6), (0.2, -2.6)]); text(d, (0.1, -2.6), 'VBP', ha='right')
    L(d, [b11, (2, -4)]); L(d, [b12, (6, -4)])
    g9, b9 = fet(d, 'n', 2, -4, gate='right', name='M9 (×K)')
    g10, b10 = fet(d, 'n', 6, -4, gate='left', name='M10')
    L(d, [g9, g10]); dot(d, (4, -4.75))
    L(d, [(4, -4.75), (4, -3.4), (6, -3.4)]); dot(d, (6, -3.4))
    L(d, [(4, -4.75), (4, -6.0)]); text(d, (4, -6.4), 'VBN', ha='center')
    d.add(elm.Resistor().endpoints(b9, (2, -7.5)).label('Rs', loc='bottom'))
    L(d, [(2, -7.5), (2, -8.5)])
    L(d, [b10, (6, -8.5)])
    # start-up
    L(d, [(10, 0), (10, -0.5)])
    gs1, bs1 = fet(d, 'p', 10, -0.5, gate='right', name='MS1 (6-stack)')
    L(d, [gs1, (12, -1.25), (12, -1.6)]); d.add(elm.Ground().at((12, -1.6)))
    L(d, [bs1, (10, -4)]); dot(d, (10, -3)); text(d, (9.85, -2.7), 'X', ha='right', fs=10)
    gs2, bs2 = fet(d, 'n', 10, -4, gate='left', name='MS2')
    L(d, [gs2, (8.0, -4.75)]); text(d, (7.9, -4.75), 'VBN', ha='right')
    L(d, [bs2, (10, -8.5)])
    gs3, bs3 = fet(d, 'n', 14, -4, gate='left', name='MS3')
    L(d, [(10, -3), (12, -3), (12, -4.75), gs3])
    L(d, [(14, -4), (14, -3)]); text(d, (14, -2.65), 'VBP', ha='center')
    L(d, [bs3, (14, -8.5)])
    # VREF: one PMOS unit current into an NMOS diode
    L(d, [(18, 0), (18, -0.5)])
    gr1, br1 = fet(d, 'p', 18, -0.5, gate='left', name='MR1 (unit)')
    L(d, [gr1, (15.9, -1.25)]); text(d, (15.8, -1.25), 'VBP', ha='right')
    L(d, [br1, (18, -4)]); dot(d, (18, -3.0))
    gr2, br2 = fet(d, 'n', 18, -4, gate='left', name='MR2')
    L(d, [gr2, (16.4, -4.75), (16.4, -3.0), (18, -3.0)]); dot(d, (16.4, -3.0))
    L(d, [br2, (18, -8.5)])
    L(d, [(18, -3.0), (19.8, -3.0)]); dot(d, (19.8, -3.0))
    text(d, (19.8, -2.6), 'VREF', ha='center')
    d.add(elm.Capacitor().endpoints((19.8, -3.0), (19.8, -5.2)))
    text(d, (20.15, -4.1), 'CREF 2 pF', ha='left')
    L(d, [(19.8, -5.2), (19.8, -8.5)])
    # pseudo-resistor detail
    dot(d, (24.5, -0.8), open_=True); text(d, (24.2, -0.8), 'A', ha='right')
    L(d, [(24.5, -0.8), (24.5, -1.3)])
    ga, ba = fet(d, 'p', 24.5, -1.3, gate='right', name='Ma')
    L(d, [ba, (24.5, -3.8)])
    mb = d.add(elm.PFet().left().reverse().at((24.5, -5.3)))
    text(d, (24.25, -4.55), 'Mb', ha='right')
    gb = (25.87, -4.55)
    L(d, [ga, (25.87, -3.3)]); L(d, [gb, (25.87, -3.3)])
    L(d, [(25.87, -3.3), (24.5, -3.3)]); dot(d, (24.5, -3.3)); dot(d, (25.87, -3.3))
    L(d, [(24.5, -5.3), (24.5, -5.8)])
    dot(d, (24.5, -5.8), open_=True); text(d, (24.2, -5.8), 'B', ha='right')
    notes = [
        'Start-up: if no current flows, VBN = 0 → MS2 off → MS1 pulls X high → MS3 pulls VBP down and starts the loop.',
        '              Once running, VBN rises → MS2 pulls X low → MS3 turns off.',
        'MS1 is six 0.6/20 µm PMOS in series (weak pull-up). Simulated: X < 20 mV once started, all corners, both model sets.',
        'VREF = Vgs of a weak-inversion NMOS diode at 0.5 µA → 0.45 V typical (0.39–0.50 V over corners, 0–70 °C).',
        'Pseudo-resistor = two Ma/Mb pairs in series (≈1.3×10¹³ Ω at 27 °C). Each PMOS 0.42/1 µm, own n-well, bulk to outer node.',
        '              Reset switches (0.42/0.15 µm NMOS, gate = rst) tie the internal nodes to A so the chain restarts at zero bias.',
    ]
    for i, n in enumerate(notes):
        text(d, (-1.0, -9.6 - 0.6 * i), n, fs=10)
    return d

for i, f in enumerate([sheet1, sheet2, sheet3], 1):
    f().save(f'sheet{i}.png', dpi=170)
print('ok')
