"""Rebuild the whole layout from scratch and check it, in order:

  devices.py      SKY130 generator -> one Magic cell per device (mag/*.mag)
  blk_pseudo_r.py pseudo-resistor block           DRC + LVS
  blk_ota.py      OTA block                       DRC
  blk_bias.py     bias block                      DRC + LVS
  blk_core.py     eeg_afe_core in tile coordinates DRC
  lvs_core.py     core LVS against the Xschem netlist
  blk_top.py      Tiny Tapeout cell, GDS + LEF    DRC
  lvs_top.py      LVS of the Tiny Tapeout cell
  then the parasitic extraction of the core (mag/eeg_afe_core_pex.spice) for
  design/sim/tb_postlayout.py.

Run inside the IIC-OSIC-TOOLS container (magic and netgen on PATH, PDK_ROOT set):
  cd layout && python3 build.py
Stops at the first step that reports DRC errors or an LVS mismatch."""
import re, subprocess, sys
import lay

STEPS = ['devices.py', 'blk_pseudo_r.py', 'blk_ota.py', 'blk_bias.py', 'blk_core.py',
         'lvs_core.py', 'blk_top.py', 'lvs_top.py']

def main():
    for s in STEPS:
        r = subprocess.run([sys.executable, s], capture_output=True, text=True)
        out = r.stdout + r.stderr
        keep = [l for l in out.splitlines() if re.match(r'(DRC|LVS|devices)', l)]
        print(f'{s:16s}', ' | '.join(keep) or '(no report)', flush=True)
        bad = r.returncode != 0 or any(re.match(r'DRC [1-9]', l) or 'FAIL' in l for l in keep)
        if bad:
            print(out[-3000:])
            sys.exit(f'stopped at {s}')
    lay.run_magic(lay.extract_tcl('eeg_afe_core', pex=True), 'pex_core')
    print('extraction       mag/eeg_afe_core_pex.spice written')

if __name__ == '__main__':
    main()
