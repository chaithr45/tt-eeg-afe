"""LVS of the complete core (eeg_afe_core) against the Xschem schematic.

The layout keeps Cc and CREF next to the other MIM capacitors, outside the ota and bias cells, so the
schematic netlist is regrouped the same way (Cc / CREF moved one level up, netlists otherwise unchanged)."""
import re, sys
import lay

SRC = '../design/xschem/netlist/lvs/eeg_afe_top.spice'

def sub(txt, name):
    return re.search(rf'\.subckt {name} .*?\.ends', txt, re.S).group(0)

def regroup():
    t = open(SRC).read()
    pr = sub(t, 'pseudo_r')
    ota = sub(t, 'ota'); bias = sub(t, 'bias'); afe = sub(t, 'afe')
    cc = [l for l in ota.splitlines() if l.startswith('XCc')][0]
    cref = [l for l in bias.splitlines() if l.startswith('XCREF')][0]
    ota = '\n'.join(l for l in ota.splitlines() if not l.startswith('XCc')).replace(
        '.subckt ota inn inp out vdd vss vbp', '.subckt ota inn inp out vdd vss vbp z')
    bias = '\n'.join(l for l in bias.splitlines() if not l.startswith('XCREF'))
    body = [l for l in afe.splitlines()[1:-1] if not l.startswith('*')]
    m = {'vin': 'ua0', 'vout': 'ua1'}
    def ren(l):
        return ' '.join(m.get(w, w) for w in l.split())
    core = ['.subckt eeg_afe_core ua0 ua1 rst vdd vss', 'XBIAS vdd vss vbp vref bias']
    for l in body:
        l = ren(l)
        if l.startswith('XA1'):
            l = 'XA1 inn inp ua1 vdd vss vbp z ota'
        core.append(l)
    core.append(cc.replace('XCc z out', 'XCc z ua1'))
    core.append(cref)
    core.append('.ends')
    out = '\n\n'.join([pr, ota, bias, '\n'.join(core)]) + '\n'
    open('../mag/eeg_afe_core_schem.spice', 'w').write(out)
    return out

if __name__ == '__main__':
    print(regroup().split('.subckt eeg_afe_core')[1][:1200])
    ok, txt = lay.lvs('eeg_afe_core', 'eeg_afe_core_schem.spice', 'eeg_afe_core')
    print('LVS', 'OK' if ok else 'FAIL')
    print('\n'.join(l for l in txt.splitlines() if re.search('Mismatch|Number of|Final|match uniquely|failed', l))[:4000])
