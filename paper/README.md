# Paper: electrode-to-alarm hardware for neonatal seizure detection

`eeg_seizure_system.pdf` is a 6-page IEEE conference paper (IEEEtran) that combines the two halves of the project:

- the SKY130 EEG analog front end in this repository (Tiny Tapeout tile, post-layout results), and
- the FPGA seizure detector (hardware-exact gradient-boosted trees on the AMD Kria KV260).

It also adds the interface analysis between them (digital re-referencing, noise in the detector band, CMRR from gain mismatch, ADC and anti-aliasing).

## Build

```
cd paper
latexmk -pdf eeg_seizure_system.tex
```

Needs a TeX Live with `IEEEtran`, `tikz`, `subfig` and `booktabs` (Debian/Ubuntu: `texlive-publishers texlive-pictures texlive-latex-extra`).

## Figures (`figs/`)

| File | Made by | Source data |
|---|---|---|
| `afe_top.pdf`, `afe_ota.pdf` | `python3 draw_schematic_paper.py .` | copy of `design/docs/draw_schematic.py` without titles and notes, smaller scale |
| `layout_annotated.pdf` | `klayout -b -r render_layout.py -rd gds=../../gds/tt_um_saichaithr_eeg_afe.gds -rd lyp=$PDK_ROOT/sky130A/libs.tech/klayout/tech/sky130A.lyp -rd out=.` then `python3 layout_annotated.py` | the tile GDS; block boxes from `layout_boxes.json` and `ota_boxes.py` |
| `postlayout.pdf` | `python3 postlayout_fig.py ../../design/results` | `design/results/postlayout*_curves.json` |

Figure 1 (system block diagram) is TikZ inside the `.tex` file.

## Where the numbers come from

- AFE: `design/results/postlayout.json`, `postlayout_combined.json`, `montecarlo.json`, `summary.json` and `design/README.md` (§1, §9).
- NEF ≈ 10: output noise integrated over the whole band and referred to the input (10.2 µVrms, `postlayout_curves.json`), 15.7 µA total current, f_H = 22.4 kHz, NEF = V_in · sqrt(2 I_tot / (π · U_T · 4kT · BW)).
- Detector: the detector paper and its evaluation logs (not in this repository).
