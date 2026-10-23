"""Annotated, rotated (90 deg clockwise) picture of the Tiny Tapeout tile for the paper.
Input: layout_raw.png and layout_boxes.json from render_layout.py (KLayout)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['TeX Gyre Termes', 'DejaVu Serif'], 'mathtext.fontset': 'stix',
                     'font.size': 7})
W, H = 161.0, 225.76
img = plt.imread('layout_raw.png')
rot = np.rot90(img, k=-1)                     # clockwise: (x, y) -> (y, W - x)
T = lambda x, y: (y, W - x)

def box(x0, y0, x1, y1):
    a, b = T(x0, y0), T(x1, y1)
    return min(a[0], b[0]), min(a[1], b[1]), abs(a[0] - b[0]), abs(a[1] - b[1])

fig = plt.figure(figsize=(3.45, 2.48))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.imshow(rot, extent=[0, H, 0, W], interpolation='lanczos')
ax.set_xlim(-1, H + 1); ax.set_ylim(-1, W + 1); ax.axis('off')
regions = [  # tile coordinates (um), label, label anchor ('c' centre)
    ((70.9, 5.0, 160.84, 87.8), 'C1 11.9 pF'),
    ((70.9, 90.75, 160.84, 173.55), "C1$'$ 11.9 pF"),
    ((70.9, 176.55, 123.05, 199.2), 'Cc'),
    ((7.9, 9.7, 60.1, 32.3), 'CREF'),
    ((7.85, 47.1, 47.4, 88.9), 'bias,\nstart-up,\nVREF'),
    ((49.0, 48.5, 65.1, 87.3), 'C2, C2$\'$\nPR, S'),
    ((14.1, 103.0, 59.9, 130.4), 'M3/M4\nmirror'),
    ((11.3, 131.9, 62.7, 203.9), 'M1/M2\ninput pair'),
    ((12.1, 206.9, 61.9, 219.3), 'M5,M7'),
]
for (x0, y0, x1, y1), lab in regions:
    bx, by, bw, bh = box(x0, y0, x1, y1)
    ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, ec='black', lw=0.7, ls=(0, (3, 1.5))))
    ax.text(bx + bw / 2, by + bh / 2, lab, ha='center', va='center', fontsize=7,
                        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))
# pins (bottom edge of the tile -> left edge here)
for name, x in (('ua[0] in', 152.26), ('ua[1] out', 132.94)):
    px, py = T(x, 0.0)
    ax.annotate(name, xy=(px + 1, py), xytext=(px + 9, py), fontsize=7, va='center',
                arrowprops=dict(arrowstyle='-', lw=0.6),
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.85))
fig.savefig('layout_annotated.pdf'); fig.savefig('layout_annotated.png', dpi=300)
print('ok')
