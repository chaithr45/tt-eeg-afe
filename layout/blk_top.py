"""tt_um_saichaithr_eeg_afe: Tiny Tapeout 1x2 analog tile.

Pins come from the official template (mag/tt_analog_1x2.def). Power: VDPWR stripe x 1..3 um,
VGND stripe x 4..6 um (metal4, y 5..220.76). The core (eeg_afe_core) is drawn in tile coordinates and
already lands on ua[0], ua[1], ui_in[0] and on the stripes. Unused digital outputs (uo_out, uio_out,
uio_oe) are tied to VGND through a metal3 bus at y = 223.3 um.
Writes gds/<top>.gds and lef/<top>.lef.
"""
import os, re
import lay

TOP = 'tt_um_saichaithr_eeg_afe'
DEF = os.path.join(lay.MAGDIR, 'tt_analog_1x2.def')
Y_TIE = 223.3

def output_pins():
    txt = open(DEF).read()
    pins = re.findall(r'- (\S+) \+ NET \S+ \+ DIRECTION (\S+).*?\+ LAYER (\S+) \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \).*?\+ PLACED \( (-?\d+) (-?\d+) \)', txt, re.S)
    out = []
    for n, d, l, x1, y1, x2, y2, px, py in pins:
        if n.startswith(('uo_out', 'uio_out', 'uio_oe')):
            out.append((n, (int(px) + int(x1)) / 1000, (int(px) + int(x2)) / 1000, (int(py) + int(y1)) / 1000))
    return out

def build():
    q = lay.q
    t = [f'cellname delete {TOP}', 'snap internal',
         f'def read {DEF}', f'cellname rename tt_um_template {TOP}', f'load {TOP}', 'snap internal']
    # power stripes
    for name, x in (('VDPWR', 1.0), ('VGND', 4.0)):
        t += [f'box {q(x)} {q(5.0)} {q(x + 2.0)} {q(220.76)}', 'paint metal4',
              f'label {name} FreeSans {q(0.25)} 0 0 0 c metal4', 'port make',
              f'port use {"ground" if name == "VGND" else "power"}', 'port class bidirectional']
    # the core
    t += [f'box 0 0 0 0', 'getcell eeg_afe_core child 0 0', 'identify XCORE']
    # unused outputs -> VGND (metal4 stub, via3, metal3 bus to the VGND stripe)
    pins = output_pins()
    xmax = max(p[2] for p in pins)
    def rect(layer, x1, y1, x2, y2):
        t.append(f'box {q(x1)} {q(y1)} {q(x2)} {q(y2)}; paint {layer}')
    rect('metal3', 4.8, Y_TIE - 0.25, xmax + 0.1, Y_TIE + 0.25)
    for n, x1, x2, y1 in pins:
        xc = (x1 + x2) / 2
        rect('metal4', x1, Y_TIE - 0.25, x2, y1 + 0.5)
        rect('metal4', xc - 0.25, Y_TIE - 0.25, xc + 0.25, Y_TIE + 0.25)
        rect('metal3', xc - 0.25, Y_TIE - 0.25, xc + 0.25, Y_TIE + 0.25)
        rect('via3', xc - 0.16, Y_TIE - 0.16, xc + 0.16, Y_TIE + 0.16)
    # the bus meets the core's vss trunk (x = 5) which carries via3s onto the VGND stripe
    t += ['select top cell', f'save {TOP}',
          'file mkdir ../gds', f'gds write ../gds/{TOP}.gds',
          'file mkdir ../lef', f'lef write ../lef/{TOP}.lef -hide -pinonly']
    return '\n'.join(t)

if __name__ == '__main__':
    out = lay.run_magic(build(), 'build_top')
    print('\n'.join(l for l in out.splitlines() if re.search('rror|arning', l))[:2000])
    n, whys = lay.drc(TOP)
    print('DRC', n); print('\n'.join(w for w in whys if w.startswith('DRC_WHY'))[:3000])
