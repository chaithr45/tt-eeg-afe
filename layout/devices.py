"""Every primitive device of the design, drawn by the SKY130 device generator (guard rings included).
Names: <type>_<W>_<L>[_nf<N>]; sizes match the Xschem schematic (design/xschem)."""
from lay import device

# pseudo-resistors and reset switches
device('p042_1',    'pfet_01v8', w=0.42, l=1,    nf=1)
device('n042_015',  'nfet_01v8', w=0.42, l=0.15, nf=1, gbc=0)   # gate contact on top only
# OTA
device('p5_8_nf6',  'pfet_01v8', w=5,    l=8,    nf=6,  conn_gates=1)     # M1/M2: 5 per side (30 fingers)
device('n7_20',     'nfet_01v8', w=7,    l=20,   nf=1)                     # M3a-c, M4a-c
device('p4_2_nf8',  'pfet_01v8', w=4,    l=2,    nf=8,  conn_gates=1)     # M5
device('p4_2_nf10', 'pfet_01v8', w=4,    l=2,    nf=10, conn_gates=1)     # M7: 2 of these
device('n5_2_nf4',  'nfet_01v8', w=5,    l=2,    nf=4,  conn_gates=1)     # M6
device('rxh_3p3',   'res_xhigh_po_0p35', l=3.3)                            # Rz
# bias
device('p4_2',      'pfet_01v8', w=4,    l=2,    nf=1)                     # M11, M12, MR1
device('n7_1_nf8',  'nfet_01v8', w=7,    l=1,    nf=8,  conn_gates=1)     # M9
device('n7_1_nf2',  'nfet_01v8', w=7,    l=1,    nf=2,  conn_gates=1)     # M10, MS2
device('n7_1_nf6',  'nfet_01v8', w=7,    l=1,    nf=6,  conn_gates=1)     # MR2
device('p06_20',    'pfet_01v8', w=0.6,  l=20,   nf=1)                     # MS1a-f
device('n042_2',    'nfet_01v8', w=0.42, l=2,    nf=1)                     # MS3
device('rxh_16',    'res_xhigh_po_0p35', l=16)                             # RS
# MIM capacitors
device('mim_256_3x3', 'cap_mim_m3_1', w=25.6, l=25.6, nx=3, ny=3)         # C1, C1'
device('mim_86',      'cap_mim_m3_1', w=8.6,  l=8.6)                       # C2, C2'
device('mim_2225_2x1', 'cap_mim_m3_1', w=22.25, l=22.25, nx=2, ny=1)      # Cc, CREF

if __name__ == '__main__':
    import lay
    out = lay.gen_devices()
    print('\n'.join(l for l in out.splitlines() if 'rror' in l) or 'devices generated')
