import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows = [
 ('Front-end (sheet 1)', None),
 ('C1, C1′', 'cap_mim_m3_1', '77 × 77 µm (11.9 pF)', 'Input coupling'),
 ('C2, C2′', 'cap_mim_m3_1', '8.6 × 8.6 µm (154 fF)', 'Feedback; gain = C1/C2 = 77.5 V/V'),
 ('PR1, PR2', 'pfet_01v8 ×4 each', '0.42 / 1', 'Two pairs in series, ≈1.3×10¹³ Ω'),
 ('S1, S2 + 3 per PR', 'nfet_01v8', '0.42 / 0.15', 'Reset switches, gate = rst (ui_in[0])'),
 ('A1 OTA (sheet 2)', None),
 ('M1, M2', 'pfet_01v8', '5 / 8 × 30 fingers', '2 µA each; W = 150 µm total'),
 ('M3, M4', 'nfet_01v8', '7 / 20, 3 in series', 'Mirror load, effective L = 60 µm'),
 ('M5', 'pfet_01v8', '4 / 2 × 8 units', '4 µA tail'),
 ('M6', 'nfet_01v8', '5 / 2 × 4', '10 µA second stage'),
 ('M7', 'pfet_01v8', '4 / 2 × 20 units', '10 µA load'),
 ('Cc, Rz', 'MIM / xhigh_po', '2 pF, 20 kΩ', 'Miller compensation (ideal in sim)'),
 ('Bias, start-up, VREF (sheet 3)', None),
 ('M11, M12, MR1', 'pfet_01v8', '4 / 2', 'Unit cell, 0.5 µA'),
 ('M10 / M9', 'nfet_01v8', '7 / 1 × 2  /  × 8', 'K = 4'),
 ('Rs', 'res_xhigh_po_0p35', 'L = 16 µm (92 / 118 kΩ)*', 'Sets I_REF'),
 ('MS1 / MS2 / MS3', 'pfet / nfet / nfet', '6×0.6/20 · 7/1×2 · 0.42/2', 'Start-up'),
 ('MR2', 'nfet_01v8', '7 / 1 × 6', 'VREF diode → 0.45 V'),
 ('CREF', 'cap_mim_m3_1', '2 pF', 'VREF decoupling (ideal in sim)'),
]
fig = plt.figure(figsize=(13, 13), dpi=170)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0.03, 0.975, 'Sheet 4 of 4 — Device sizes (SKY130 1.8 V devices, W / L in µm)', fontsize=17, va='top')
ax.text(0.03, 0.948, 'Simulated in ngspice with SKY130 models: 5 process corners × 0/27/37 °C × 1.71/1.8/1.89 V, classic and continuous models; specified 0–50 °C. Pre-layout.',
        fontsize=11.5, color='#555555', va='top')
cols = [0.03, 0.22, 0.42, 0.64]
y = 0.905
for c, h in zip(cols, ['Device', 'SKY130 primitive', 'Size', 'Role']):
    ax.text(c, y, h, fontsize=12.5, fontweight='bold', va='center')
ax.plot([0.03, 0.97], [y - 0.014, y - 0.014], color='black', lw=1)
y -= 0.033
for r in rows:
    if r[1] is None:
        y -= 0.006; ax.text(0.03, y, r[0], fontsize=12.5, fontweight='bold', color='#1a5276', va='center'); y -= 0.029; continue
    for c, v in zip(cols, r):
        ax.text(c, y, v, fontsize=11.3, va='center')
    y -= 0.027
y -= 0.012
ax.plot([0.03, 0.97], [y + 0.012, y + 0.012], color='#999999', lw=0.8)
notes = [
 'Supply current 15.7 µA typical (13–17 µA over corners, 0–37 °C) → about 28 µW at 1.8 V. *Rs = 92 kΩ in the classic',
 '   SKY130 models, 118 kΩ in the continuous (combined) models → 0.50 / 0.39 µA unit current, 15.7 / 12.2 µA supply.',
 'MIM total ≈ 28 pF ≈ 14,000 µm², about 40% of the 160 × 225 µm 1x2 tile. MIM uses met3/met4: keep it clear of',
 '   Tiny Tapeout’s met4 power stripes; met5 is not allowed.',
 'All transistors stay inside the SKY130 model bins (finger W ≤ 7 µm, L ≤ 20 µm); wide devices use parallel fingers.',
 'Next: enter in Xschem, re-simulate, then layout (Magic/KLayout), DRC, LVS, extraction and post-layout simulation.',
]
for n in notes:
    ax.text(0.03, y, n, fontsize=11.2, va='center'); y -= 0.026
fig.savefig('sheet4.png', dpi=170, facecolor='white')
