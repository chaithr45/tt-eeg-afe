"""Minimal parser for Magic .mag files (sky130A, magscale 1 2 -> 1 unit = 0.005 um)."""
import re
from collections import defaultdict

UNIT = 0.005  # um per internal unit

class Mag:
    def __init__(self, path):
        self.rects = defaultdict(list)   # layer -> [(x1,y1,x2,y2)] in internal units
        self.labels = []                 # (layer, x1, y1, x2, y2, text)
        self.uses = []
        layer = None
        for line in open(path):
            line = line.rstrip('\n')
            m = re.match(r'^<< (\S+) >>', line)
            if m:
                layer = m.group(1); continue
            if line.startswith('rect ') and layer not in (None, 'labels', 'properties', 'checkpaint'):
                x1, y1, x2, y2 = map(int, line.split()[1:5])
                self.rects[layer].append((x1, y1, x2, y2))
            elif line.startswith(('rlabel', 'flabel')):
                p = line.split()
                if p[0] == 'rlabel':
                    lay, x1, y1, x2, y2, text = p[1], *map(int, p[2:6]), p[7]
                else:   # flabel layer s x1 y1 x2 y2 rot font size ... text
                    lay, x1, y1, x2, y2, text = p[1], *map(int, p[3:7]), p[-1]
                self.labels.append((lay, x1, y1, x2, y2, text))
            elif line.startswith('use '):
                self.uses.append(line)

    def bbox(self, layers=None):
        xs = [r for l, rs in self.rects.items() if (layers is None or l in layers) for r in rs]
        return (min(r[0] for r in xs), min(r[1] for r in xs), max(r[2] for r in xs), max(r[3] for r in xs))

    def um(self, b):
        return tuple(round(v * UNIT, 3) for v in b)

    def label(self, name):
        return [l for l in self.labels if l[5] == name]

    def containing(self, layer, x, y):
        return [r for r in self.rects.get(layer, []) if r[0] <= x <= r[2] and r[1] <= y <= r[3]]


M1COV = ('metal1', 'viali', 'via1')          # layers that contain metal1 in Magic's sky130 tech
M2COV = ('metal2', 'via1', 'via2')
LICOV = ('locali', 'viali', 'ndiffc', 'pdiffc', 'polycont', 'nsubdiffcont', 'psubdiffcont', 'xpolycontact')

def _touch(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]

def region(mag, layers, x, y):
    """All rects (of `layers`) connected to the point (x, y)."""
    pool = [r for l in layers for r in mag.rects.get(l, [])]
    seed = [r for r in pool if r[0] <= x <= r[2] and r[1] <= y <= r[3]]
    reg, front = set(seed), list(seed)
    while front:
        a = front.pop()
        for b in pool:
            if b not in reg and _touch(a, b):
                reg.add(b); front.append(b)
    return sorted(reg)

def bbox_of(rects):
    return (min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects))
