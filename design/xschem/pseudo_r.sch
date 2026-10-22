v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Pseudo-resistor (two back-to-back PMOS pairs in series)} -260 -620 0 0 0.6 0.6 {}
T {About 1.3e13 Ohm at zero bias (27 C). Each PMOS 0.42/1 um in its own n-well, bulk tied to its outer node.} -260 -580 0 0 0.3 0.3 {}
T {Reset: when rst is high, XS1-XS3 tie the internal nodes to a so the chain restarts at zero bias.} -260 -555 0 0 0.3 0.3 {}
C {iopin.sym} -240 -400 0 0 {name=p1 lab=a}
C {iopin.sym} -240 -360 0 0 {name=p2 lab=b}
C {ipin.sym} -240 -320 0 0 {name=p3 lab=rst}
C {iopin.sym} -240 -280 0 0 {name=p4 lab=vss}
C {sky130_fd_pr/pfet_01v8.sym} 150 -300 0 0 {name=Ma1 W=0.42 L=1 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -270 0 1 {name=l1 sig_type=std_logic lab=m1}
C {lab_pin.sym} 130 -300 0 0 {name=l2 sig_type=std_logic lab=m1}
C {lab_pin.sym} 170 -330 0 1 {name=l3 sig_type=std_logic lab=a}
C {lab_pin.sym} 170 -300 0 1 {name=l4 sig_type=std_logic lab=a}
C {sky130_fd_pr/pfet_01v8.sym} 150 -150 0 0 {name=Mb1 W=0.42 L=1 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -120 0 1 {name=l5 sig_type=std_logic lab=m1}
C {lab_pin.sym} 130 -150 0 0 {name=l6 sig_type=std_logic lab=m1}
C {lab_pin.sym} 170 -180 0 1 {name=l7 sig_type=std_logic lab=n1}
C {lab_pin.sym} 170 -150 0 1 {name=l8 sig_type=std_logic lab=n1}
C {sky130_fd_pr/pfet_01v8.sym} 150 0 0 0 {name=Ma2 W=0.42 L=1 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 30 0 1 {name=l9 sig_type=std_logic lab=m2}
C {lab_pin.sym} 130 0 0 0 {name=l10 sig_type=std_logic lab=m2}
C {lab_pin.sym} 170 -30 0 1 {name=l11 sig_type=std_logic lab=n1}
C {lab_pin.sym} 170 0 0 1 {name=l12 sig_type=std_logic lab=n1}
C {sky130_fd_pr/pfet_01v8.sym} 150 150 0 0 {name=Mb2 W=0.42 L=1 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 180 0 1 {name=l13 sig_type=std_logic lab=m2}
C {lab_pin.sym} 130 150 0 0 {name=l14 sig_type=std_logic lab=m2}
C {lab_pin.sym} 170 120 0 1 {name=l15 sig_type=std_logic lab=b}
C {lab_pin.sym} 170 150 0 1 {name=l16 sig_type=std_logic lab=b}
C {sky130_fd_pr/nfet_01v8.sym} 500 -300 0 0 {name=S1 W=0.42 L=0.15 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 520 -330 0 1 {name=l17 sig_type=std_logic lab=m1}
C {lab_pin.sym} 480 -300 0 0 {name=l18 sig_type=std_logic lab=rst}
C {lab_pin.sym} 520 -270 0 1 {name=l19 sig_type=std_logic lab=a}
C {lab_pin.sym} 520 -300 0 1 {name=l20 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 500 -150 0 0 {name=S2 W=0.42 L=0.15 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 520 -180 0 1 {name=l21 sig_type=std_logic lab=n1}
C {lab_pin.sym} 480 -150 0 0 {name=l22 sig_type=std_logic lab=rst}
C {lab_pin.sym} 520 -120 0 1 {name=l23 sig_type=std_logic lab=a}
C {lab_pin.sym} 520 -150 0 1 {name=l24 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 500 0 0 0 {name=S3 W=0.42 L=0.15 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 520 -30 0 1 {name=l25 sig_type=std_logic lab=m2}
C {lab_pin.sym} 480 0 0 0 {name=l26 sig_type=std_logic lab=rst}
C {lab_pin.sym} 520 30 0 1 {name=l27 sig_type=std_logic lab=a}
C {lab_pin.sym} 520 0 0 1 {name=l28 sig_type=std_logic lab=vss}
