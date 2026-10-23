"""Column-width post-layout figure: gain and input-referred noise, schematic vs extracted layout."""
import json, numpy as np, matplotlib, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = sys.argv[1]
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['TeX Gyre Termes', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 7, 'axes.linewidth': 0.5,
                     'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'xtick.minor.width': 0.4,
                     'ytick.minor.width': 0.4, 'legend.fontsize': 6.3})
cl = json.load(open(R + '/postlayout_curves.json'))
co = json.load(open(R + '/postlayout_combined_curves.json'))
fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.55))
series = ((cl['schematic'], '#1f4e9c', '-', 'Schematic (classic)'),
          (cl['layout'], '#d9622b', '--', 'Layout (classic)'),
          (co['layout'], '#2a9d55', ':', 'Layout (continuous)'))
for d, c, ls, lab in series:
    axs[0].semilogx(d['f'], d['g'], color=c, lw=1.0, ls=ls, label=lab)
    axs[1].loglog(d['fn'], np.array(d['vin']) * 1e9, color=c, lw=1.0, ls=ls, label=lab)
for ax in axs:
    ax.axvspan(0.5, 20, color='#7aa6c2', alpha=.18, lw=0)
    ax.set_xlabel('Frequency (Hz)', labelpad=1)
    ax.grid(True, which='major', lw=0.3, color='#cccccc')
    ax.tick_params(pad=1.5, length=2.5)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
axs[0].set_xlim(0.01, 1e6); axs[0].set_ylim(0, 42); axs[0].set_ylabel('Gain (dB)', labelpad=1)
axs[0].set_xticks([1e-2, 1, 1e2, 1e4, 1e6])
axs[1].set_xlim(0.05, 1e5); axs[1].set_ylabel(r'Input noise (nV/$\sqrt{\mathrm{Hz}}$)', labelpad=1)
axs[1].set_xticks([0.1, 10, 1e3, 1e5])
axs[0].legend(frameon=False, loc='lower center', handlelength=2.2, borderaxespad=0.1, labelspacing=0.2)
fig.tight_layout(pad=0.2, w_pad=0.6)
fig.savefig('postlayout.pdf'); fig.savefig('postlayout.png', dpi=300)
print('ok')
