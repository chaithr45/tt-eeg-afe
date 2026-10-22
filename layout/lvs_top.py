"""LVS of the whole Tiny Tapeout cell (tt_um_saichaithr_eeg_afe): the core on ua[0], ua[1], ui_in[0],
VDPWR, VGND. Unused digital outputs are tied to VGND in the layout, so the extractor merges them into
VGND and they do not appear as separate ports. Run after blk_top.py and lvs_core.py."""
import re
import lay

TOP = 'tt_um_saichaithr_eeg_afe'

if __name__ == '__main__':
    lay.run_magic(lay.extract_tcl(TOP), 'ext_top')
    ext = open(f'{lay.MAGDIR}/{TOP}_lvs.spice').read()
    hdr = re.search(rf'^\.subckt {TOP}((?:.*\n\+.*)*.*)$', ext, re.M).group(1)
    ports = hdr.replace('\n+', ' ').split()
    core = open(f'{lay.MAGDIR}/eeg_afe_core_schem.spice').read()
    open(f'{lay.MAGDIR}/tt_top_schem.spice', 'w').write(
        core + f'\n.subckt {TOP} ' + ' '.join(ports) +
        '\nXCORE ua[0] ua[1] ui_in[0] VDPWR VGND eeg_afe_core\n.ends\n')
    ok, txt = lay.lvs(TOP, 'tt_top_schem.spice', TOP)
    print('ports in layout:', ' '.join(ports))
    print('LVS', 'OK (circuits match uniquely)' if ok else 'FAIL')
    if not ok:
        print('\n'.join(l for l in txt.splitlines() if re.search('Mismatch|Number of|Final', l)))
