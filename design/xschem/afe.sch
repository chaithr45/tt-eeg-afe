v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Capacitive-feedback EEG amplifier core} -260 -620 0 0 0.6 0.6 {}
T {Gain = C1/C2 = 77.8 V/V. C1, C1p: 9 x (25.6 um)^2 MIM units = 11.95 pF. C2, C2p: 8.6 um square = 154 fF.} -260 -580 0 0 0.3 0.3 {}
T {MIM bottom plate (met3) goes on the low-impedance side: vin for C1, vss for C1p, vout for C2, vref for C2p.} -260 -555 0 0 0.3 0.3 {}
T {SW1/SW2: reset switches driven by rst (ui_in[0]).} -260 -530 0 0 0.3 0.3 {}
C {ipin.sym} -240 -400 0 0 {name=p1 lab=vin}
C {opin.sym} -240 -360 0 0 {name=p2 lab=vout}
C {iopin.sym} -240 -320 0 0 {name=p3 lab=vdd}
C {iopin.sym} -240 -280 0 0 {name=p4 lab=vss}
C {ipin.sym} -240 -240 0 0 {name=p5 lab=vbp}
C {ipin.sym} -240 -200 0 0 {name=p6 lab=vref}
C {ipin.sym} -240 -160 0 0 {name=p7 lab=rst}
C {sky130_fd_pr/cap_mim_m3_1.sym} 150 -250 0 0 {name=C1 model=tcleval($::MIM_MODEL) W=25.6 L=25.6 MF=9 spiceprefix=X}
C {lab_pin.sym} 150 -280 0 1 {name=l1 sig_type=std_logic lab=vin}
C {lab_pin.sym} 150 -220 0 1 {name=l2 sig_type=std_logic lab=inn}
C {sky130_fd_pr/cap_mim_m3_1.sym} 400 -400 0 0 {name=C2 model=tcleval($::MIM_MODEL) W=8.6 L=8.6 MF=1 spiceprefix=X}
C {lab_pin.sym} 400 -430 0 1 {name=l3 sig_type=std_logic lab=inn}
C {lab_pin.sym} 400 -370 0 1 {name=l4 sig_type=std_logic lab=vout}
C {pseudo_r.sym} 650 -400 0 0 {name=XPR1}
C {lab_pin.sym} 570 -400 0 0 {name=l5 sig_type=std_logic lab=inn}
C {lab_pin.sym} 730 -400 0 1 {name=l6 sig_type=std_logic lab=vout}
C {lab_pin.sym} 650 -460 0 0 {name=l7 sig_type=std_logic lab=rst}
C {lab_pin.sym} 650 -340 0 0 {name=l8 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 950 -400 0 0 {name=SW1 W=0.42 L=0.15 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 970 -430 0 1 {name=l9 sig_type=std_logic lab=inn}
C {lab_pin.sym} 930 -400 0 0 {name=l10 sig_type=std_logic lab=rst}
C {lab_pin.sym} 970 -370 0 1 {name=l11 sig_type=std_logic lab=vout}
C {lab_pin.sym} 970 -400 0 1 {name=l12 sig_type=std_logic lab=vss}
C {ota.sym} 500 -120 0 0 {name=XA1}
C {lab_pin.sym} 400 -160 0 0 {name=l13 sig_type=std_logic lab=inn}
C {lab_pin.sym} 400 -120 0 0 {name=l14 sig_type=std_logic lab=inp}
C {lab_pin.sym} 600 -120 0 1 {name=l15 sig_type=std_logic lab=vout}
C {lab_pin.sym} 500 -220 0 0 {name=l16 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 500 -20 0 0 {name=l17 sig_type=std_logic lab=vss}
C {lab_pin.sym} 400 -80 0 0 {name=l18 sig_type=std_logic lab=vbp}
C {sky130_fd_pr/cap_mim_m3_1.sym} 150 150 0 0 {name=C1p model=tcleval($::MIM_MODEL) W=25.6 L=25.6 MF=9 spiceprefix=X}
C {lab_pin.sym} 150 120 0 1 {name=l19 sig_type=std_logic lab=vss}
C {lab_pin.sym} 150 180 0 1 {name=l20 sig_type=std_logic lab=inp}
C {sky130_fd_pr/cap_mim_m3_1.sym} 400 200 0 0 {name=C2p model=tcleval($::MIM_MODEL) W=8.6 L=8.6 MF=1 spiceprefix=X}
C {lab_pin.sym} 400 170 0 1 {name=l21 sig_type=std_logic lab=inp}
C {lab_pin.sym} 400 230 0 1 {name=l22 sig_type=std_logic lab=vref}
C {pseudo_r.sym} 650 200 0 0 {name=XPR2}
C {lab_pin.sym} 570 200 0 0 {name=l23 sig_type=std_logic lab=inp}
C {lab_pin.sym} 730 200 0 1 {name=l24 sig_type=std_logic lab=vref}
C {lab_pin.sym} 650 140 0 0 {name=l25 sig_type=std_logic lab=rst}
C {lab_pin.sym} 650 260 0 0 {name=l26 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 950 200 0 0 {name=SW2 W=0.42 L=0.15 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 970 170 0 1 {name=l27 sig_type=std_logic lab=inp}
C {lab_pin.sym} 930 200 0 0 {name=l28 sig_type=std_logic lab=rst}
C {lab_pin.sym} 970 230 0 1 {name=l29 sig_type=std_logic lab=vref}
C {lab_pin.sym} 970 200 0 1 {name=l30 sig_type=std_logic lab=vss}
