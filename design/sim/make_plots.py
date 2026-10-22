"""Make the result figures from saved simulation data (results/)."""
import json, os, sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = '../results/'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, GRID, ENV = '#0b0b0b', '#52514e', '#e6e5e1', '#c9c8c2'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': 'white'})
cur = json.load(open(R + 'ac_noise_curves.json'))
tt = cur['tt_27']

# Fig 1: closed-loop gain
fig, ax = plt.subplots(figsize=(7, 3.6))
G = np.array([cur[k]['g'] for k in cur]); f = np.array(tt['f'])
ax.fill_between(f, G.min(0), G.max(0), color=ENV, alpha=.6, lw=0, label='All corners (5 process × 0/27/37 °C; curves overlap)')
ax.semilogx(f, tt['g'], color=BLUE, lw=2, label='Typical, 27 °C')
ax.axvspan(0.5, 100, color=AQUA, alpha=.08, lw=0)
ax.text(7, 40.5, 'EEG band 0.5–100 Hz', color=INK2, ha='center', fontsize=9)
ax.set_xlim(0.01, 1e6); ax.set_ylim(0, 44)
ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Gain (dB)')
ax.set_title('Closed-loop gain: 37.8 dB (77 V/V), −3 dB band 0.09 Hz to 22 kHz', loc='left', fontsize=11, color=INK)
ax.legend(frameon=False, loc='lower center', fontsize=9, bbox_to_anchor=(0.55, 0.05))
fig.tight_layout(); fig.savefig(R + 'fig1_gain.png', dpi=150); plt.close(fig)

# Fig 2: input-referred noise density
fig, ax = plt.subplots(figsize=(7, 3.6))
N = np.array([cur[k]['vin'] for k in cur]) * 1e9; fn = np.array(tt['fn'])
ax.fill_between(fn, N.min(0), N.max(0), color=ENV, alpha=.6, lw=0, label='All corners (5 process × 0/27/37 °C; nearly overlap)')
ax.loglog(fn, np.array(tt['vin']) * 1e9, color=BLUE, lw=2, label='Typical, 27 °C')
ax.axvspan(0.5, 100, color=AQUA, alpha=.08, lw=0)
ax.set_xlim(0.05, 1e5); ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Input-referred noise (nV/√Hz)')
lo, hi = min(cur[k]['noise'] for k in cur), max(cur[k]['noise'] for k in cur)
ax.set_title(f'Input-referred noise: {tt["noise"]:.2f} µVrms over 0.5–100 Hz (corners {lo:.2f}–{hi:.2f})', loc='left', fontsize=11, color=INK)
ax.legend(frameon=False, loc='upper right', fontsize=9)
fig.tight_layout(); fig.savefig(R + 'fig2_noise.png', dpi=150); plt.close(fig)

# Fig 5: post-layout (extracted parasitics) against the schematic, typical / 27 C
if os.path.exists(R + 'postlayout_curves.json'):
    pc = json.load(open(R + 'postlayout_curves.json'))
    pl = json.load(open(R + 'postlayout.json'))['ac']
    s, l = pl['tt_27_schematic'], pl['tt_27_layout']
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6))
    for k, col, ls, lab in (('schematic', BLUE, '-', 'Schematic'), ('layout', ORANGE, '--', 'Layout (extracted)')):
        axs[0].semilogx(pc[k]['f'], pc[k]['g'], color=col, lw=2, ls=ls, label=lab)
        axs[1].loglog(pc[k]['fn'], np.array(pc[k]['vin']) * 1e9, color=col, lw=2, ls=ls, label=lab)
    for ax in axs:
        ax.axvspan(0.5, 100, color=AQUA, alpha=.08, lw=0)
        ax.set_xlabel('Frequency (Hz)')
        ax.legend(frameon=False, fontsize=9, loc='lower center' if ax is axs[0] else 'upper right')
    axs[0].set_xlim(0.01, 1e6); axs[0].set_ylim(0, 44); axs[0].set_ylabel('Gain (dB)')
    axs[0].set_title(f'Gain: {s["gain_db"]:.2f} dB schematic, {l["gain_db"]:.2f} dB layout; '
                     f'−3 dB at {l["f_hi_khz"]:.1f} kHz', loc='left', fontsize=10, color=INK)
    axs[1].set_xlim(0.05, 1e5); axs[1].set_ylabel('Input-referred noise (nV/√Hz)')
    axs[1].set_title(f'Noise 0.5–100 Hz: {s["noise_uvrms"]:.2f} µVrms schematic, {l["noise_uvrms"]:.2f} layout',
                     loc='left', fontsize=10, color=INK)
    fig.tight_layout(); fig.savefig(R + 'fig5_postlayout.png', dpi=150); plt.close(fig)

# Fig 3: transients (small multiples, shared style); needs the saved waveforms (not kept in the git repository)
if not os.path.exists(R + 'tran_sine.npy'):
    print('fig3 skipped: results/tran_sine.npy and tran_artifact.npy not present'); sys.exit(0)
s = np.load(R + 'tran_sine.npy'); a = np.load(R + 'tran_artifact.npy')
fig, axs = plt.subplots(1, 3, figsize=(12, 3.4))
m = (s[:, 0] > 1.5) & (s[:, 0] < 1.7)
axs[0].plot((s[m, 0] - 1.5) * 1e3, (s[m, 1] - s[m, 1].mean()) * 1e3, color=BLUE, lw=2, label='Output (mV)')
axs[0].plot((s[m, 0] - 1.5) * 1e3, s[m, 2] * 1e6 / 10, color=ORANGE, lw=1.5, ls='--', label='Input (µV ÷ 10)')
axs[0].set_xlabel('Time (ms)'); axs[0].set_title('100 µV, 10 Hz tone → 7.7 mV out', loc='left', fontsize=10)
axs[0].set_ylim(-11, 15); axs[0].legend(frameon=False, fontsize=8, loc='upper center', ncol=2)
axs[1].plot(a[:, 0] * 1e3, a[:, 1], color=BLUE, lw=2)
axs[1].set_xlim(0, 40); axs[1].set_xlabel('Time (ms)'); axs[1].set_ylabel('Output (V)')
axs[1].axvspan(0.06, 10, color=AQUA, alpha=.12, lw=0); axs[1].text(5, 0.2, 'reset\nheld', ha='center', color=INK2, fontsize=9)
axs[1].set_ylim(-0.05, 1.9); axs[1].set_title('Power-up with 10 ms reset', loc='left', fontsize=10)
axs[2].plot(a[:, 0] * 1e3, a[:, 1], color=BLUE, lw=2)
axs[2].set_xlim(30, 250); axs[2].set_ylim(-0.05, 1.9); axs[2].set_xlabel('Time (ms)'); axs[2].set_ylabel('Output (V)')
axs[2].axvspan(100, 110, color=AQUA, alpha=.18, lw=0)
axs[2].text(33, 1.5, '20 mV artifact at 50 ms\n→ output saturates', fontsize=8.5, color=INK2)
axs[2].text(116, 0.75, '10 ms reset pulse\n→ back to 0.45 V', fontsize=9, color=INK2)
axs[2].set_title('Artifact recovery with reset pin', loc='left', fontsize=10)
fig.tight_layout(); fig.savefig(R + 'fig3_transient.png', dpi=150); plt.close(fig)
print('plots written')
