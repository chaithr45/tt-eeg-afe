# KLayout batch script: render the tile and dump child-cell bounding boxes of eeg_afe_core.
# usage: klayout -b -r render_layout.py -rd gds=... -rd lyp=... -rd out=...
import pya, json
lv = pya.LayoutView()
lv.load_layout(gds, True)
lv.load_layer_props(lyp)
lv.max_hier()
lv.set_config('background-color', '#ffffff')
lv.set_config('grid-visible', 'false')
lv.set_config('text-visible', 'false')
lv.set_config('cell-box-visible', 'false')
W, H = 161.0, 225.76
lv.zoom_box(pya.DBox(0, 0, W, H))
lv.save_image(out + '/layout_raw.png', 1610, 2258)
ly = lv.cellview(0).layout()
core = ly.cell('eeg_afe_core')
boxes = []
for inst in core.each_inst():
    b = inst.dbbox()
    boxes.append([ly.cell(inst.cell_index).name, b.left, b.bottom, b.right, b.top])
top = ly.top_cell()
boxes.append(['__top__', top.dbbox().left, top.dbbox().bottom, top.dbbox().right, top.dbbox().top])
json.dump(boxes, open(out + '/layout_boxes.json', 'w'), indent=0)
