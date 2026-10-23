import pya, json, collections
ly = pya.Layout(); ly.read(gds)
for name in ['ota', 'bias']:
    c = ly.cell(name); o = None
    # placement of the cell in eeg_afe_core
    core = ly.cell('eeg_afe_core')
    for inst in core.each_inst():
        if inst.cell_index == c.cell_index():
            o = inst.dcplx_trans
    agg = collections.defaultdict(list)
    for inst in c.each_inst():
        b = inst.dbbox().transformed(o)
        agg[ly.cell(inst.cell_index).name].append([round(b.left,2), round(b.bottom,2), round(b.right,2), round(b.top,2)])
    print(name)
    for k, v in agg.items():
        xs = [r[0] for r in v]+[r[2] for r in v]; ys=[r[1] for r in v]+[r[3] for r in v]
        print(f'  {k:28s} n={len(v):3d} x {min(xs):6.1f}..{max(xs):6.1f}  y {min(ys):6.1f}..{max(ys):6.1f}')
