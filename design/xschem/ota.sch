v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Two-stage Miller OTA (PMOS input)} -260 -620 0 0 0.6 0.6 {}
T {M3/M4: three 7/20 um NMOS in series (effective L = 60 um) for low 1/f noise.} -260 -580 0 0 0.3 0.3 {}
T {Current sources use the 4/2 um PMOS unit cell matched to the bias diode (0.5 uA per unit).} -260 -555 0 0 0.3 0.3 {}
T {Rz = res_xhigh_po_0p35 L = 3.3 um (about 20 kOhm). Cc = 2 pF = 2 x (22.25 um)^2 MIM (max MIM side is 30 um); bottom plate (met3) on node out.} -260 -530 0 0 0.3 0.3 {}
C {ipin.sym} -240 -400 0 0 {name=p1 lab=inn}
C {ipin.sym} -240 -360 0 0 {name=p2 lab=inp}
C {opin.sym} -240 -320 0 0 {name=p3 lab=out}
C {iopin.sym} -240 -280 0 0 {name=p4 lab=vdd}
C {iopin.sym} -240 -240 0 0 {name=p5 lab=vss}
C {ipin.sym} -240 -200 0 0 {name=p6 lab=vbp}
C {sky130_fd_pr/pfet_01v8.sym} 300 -300 0 0 {name=M5 W=4 L=2 nf=1 mult=8 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 320 -270 0 1 {name=l1 sig_type=std_logic lab=t}
C {lab_pin.sym} 280 -300 0 0 {name=l2 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 320 -330 0 1 {name=l3 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 320 -300 0 1 {name=l4 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 150 -150 0 0 {name=M1 W=5 L=8 nf=1 mult=30 ad=1.45 as=1.45 pd=10.58 ps=10.58 nrd=0.058 nrs=0.058 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -120 0 1 {name=l5 sig_type=std_logic lab=d1}
C {lab_pin.sym} 130 -150 0 0 {name=l6 sig_type=std_logic lab=inn}
C {lab_pin.sym} 170 -180 0 1 {name=l7 sig_type=std_logic lab=t}
C {lab_pin.sym} 170 -150 0 1 {name=l8 sig_type=std_logic lab=t}
C {sky130_fd_pr/pfet_01v8.sym} 450 -150 0 0 {name=M2 W=5 L=8 nf=1 mult=30 ad=1.45 as=1.45 pd=10.58 ps=10.58 nrd=0.058 nrs=0.058 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 -120 0 1 {name=l9 sig_type=std_logic lab=y}
C {lab_pin.sym} 430 -150 0 0 {name=l10 sig_type=std_logic lab=inp}
C {lab_pin.sym} 470 -180 0 1 {name=l11 sig_type=std_logic lab=t}
C {lab_pin.sym} 470 -150 0 1 {name=l12 sig_type=std_logic lab=t}
C {sky130_fd_pr/nfet_01v8.sym} 150 0 0 0 {name=M3a W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -30 0 1 {name=l13 sig_type=std_logic lab=d1}
C {lab_pin.sym} 130 0 0 0 {name=l14 sig_type=std_logic lab=d1}
C {lab_pin.sym} 170 30 0 1 {name=l15 sig_type=std_logic lab=s3}
C {lab_pin.sym} 170 0 0 1 {name=l16 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 150 150 0 0 {name=M3b W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 120 0 1 {name=l17 sig_type=std_logic lab=s3}
C {lab_pin.sym} 130 150 0 0 {name=l18 sig_type=std_logic lab=d1}
C {lab_pin.sym} 170 180 0 1 {name=l19 sig_type=std_logic lab=s3c}
C {lab_pin.sym} 170 150 0 1 {name=l20 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 150 300 0 0 {name=M3c W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 270 0 1 {name=l21 sig_type=std_logic lab=s3c}
C {lab_pin.sym} 130 300 0 0 {name=l22 sig_type=std_logic lab=d1}
C {lab_pin.sym} 170 330 0 1 {name=l23 sig_type=std_logic lab=vss}
C {lab_pin.sym} 170 300 0 1 {name=l24 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 450 0 0 0 {name=M4a W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 -30 0 1 {name=l25 sig_type=std_logic lab=y}
C {lab_pin.sym} 430 0 0 0 {name=l26 sig_type=std_logic lab=d1}
C {lab_pin.sym} 470 30 0 1 {name=l27 sig_type=std_logic lab=s4}
C {lab_pin.sym} 470 0 0 1 {name=l28 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 450 150 0 0 {name=M4b W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 120 0 1 {name=l29 sig_type=std_logic lab=s4}
C {lab_pin.sym} 430 150 0 0 {name=l30 sig_type=std_logic lab=d1}
C {lab_pin.sym} 470 180 0 1 {name=l31 sig_type=std_logic lab=s4c}
C {lab_pin.sym} 470 150 0 1 {name=l32 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 450 300 0 0 {name=M4c W=7 L=20 nf=1 mult=1 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 270 0 1 {name=l33 sig_type=std_logic lab=s4c}
C {lab_pin.sym} 430 300 0 0 {name=l34 sig_type=std_logic lab=d1}
C {lab_pin.sym} 470 330 0 1 {name=l35 sig_type=std_logic lab=vss}
C {lab_pin.sym} 470 300 0 1 {name=l36 sig_type=std_logic lab=vss}
C {sky130_fd_pr/pfet_01v8.sym} 950 -300 0 0 {name=M7 W=4 L=2 nf=1 mult=20 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 970 -270 0 1 {name=l37 sig_type=std_logic lab=out}
C {lab_pin.sym} 930 -300 0 0 {name=l38 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 970 -330 0 1 {name=l39 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 970 -300 0 1 {name=l40 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/nfet_01v8.sym} 950 150 0 0 {name=M6 W=5 L=2 nf=1 mult=4 ad=1.45 as=1.45 pd=10.58 ps=10.58 nrd=0.058 nrs=0.058 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 970 120 0 1 {name=l41 sig_type=std_logic lab=out}
C {lab_pin.sym} 930 150 0 0 {name=l42 sig_type=std_logic lab=y}
C {lab_pin.sym} 970 180 0 1 {name=l43 sig_type=std_logic lab=vss}
C {lab_pin.sym} 970 150 0 1 {name=l44 sig_type=std_logic lab=vss}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 680 -40 0 0 {name=Rz L=3.3 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {lab_pin.sym} 680 -70 0 1 {name=l45 sig_type=std_logic lab=y}
C {lab_pin.sym} 680 -10 0 1 {name=l46 sig_type=std_logic lab=z}
C {lab_pin.sym} 660 -40 0 0 {name=l47 sig_type=std_logic lab=vss}
C {sky130_fd_pr/cap_mim_m3_1.sym} 800 -40 0 0 {name=Cc model=tcleval($::MIM_MODEL) W=22.25 L=22.25 MF=2 spiceprefix=X}
C {lab_pin.sym} 800 -70 0 1 {name=l48 sig_type=std_logic lab=z}
C {lab_pin.sym} 800 -10 0 1 {name=l49 sig_type=std_logic lab=out}
