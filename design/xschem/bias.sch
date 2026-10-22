v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Bias generator, start-up and VREF} -260 -620 0 0 0.6 0.6 {}
T {Subthreshold beta-multiplier: I = n*UT*ln(K)/Rs = 0.5 uA (K = 4, Rs = 92 kOhm xhigh_po, L = 16 um).} -260 -580 0 0 0.3 0.3 {}
T {Start-up: MS1 (6 x 0.6/20 PMOS in series) pulls x high when no current flows; MS3 then pulls vbp low; MS2 releases it.} -260 -555 0 0 0.3 0.3 {}
T {MS1 is 0.6 um wide: the 0.42/20 um PMOS bin of the SKY130 continuous (combined) models fails in the ss corner (Pclm < 0).} -260 -530 0 0 0.3 0.3 {}
T {VREF = Vgs of MR2 (6 x 7/1 NMOS) at one 0.5 uA unit, about 0.45 V. CREF = 2 x (22.25 um)^2 MIM = 2 pF, bottom plate on vss.} -260 -505 0 0 0.3 0.3 {}
C {iopin.sym} -240 -400 0 0 {name=p1 lab=vdd}
C {iopin.sym} -240 -360 0 0 {name=p2 lab=vss}
C {opin.sym} -240 -320 0 0 {name=p3 lab=vbp}
C {opin.sym} -240 -280 0 0 {name=p4 lab=vref}
C {sky130_fd_pr/pfet_01v8.sym} 150 -300 0 0 {name=M11 W=4 L=2 nf=1 mult=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -270 0 1 {name=l1 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 130 -300 0 0 {name=l2 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 170 -330 0 1 {name=l3 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 170 -300 0 1 {name=l4 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 450 -300 0 0 {name=M12 W=4 L=2 nf=1 mult=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 -270 0 1 {name=l5 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 430 -300 0 0 {name=l6 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 470 -330 0 1 {name=l7 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 470 -300 0 1 {name=l8 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/nfet_01v8.sym} 150 -100 0 0 {name=M9 W=7 L=1 nf=1 mult=8 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 170 -130 0 1 {name=l9 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 130 -100 0 0 {name=l10 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 170 -70 0 1 {name=l11 sig_type=std_logic lab=rs}
C {lab_pin.sym} 170 -100 0 1 {name=l12 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 450 -100 0 0 {name=M10 W=7 L=1 nf=1 mult=2 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 470 -130 0 1 {name=l13 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 430 -100 0 0 {name=l14 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 470 -70 0 1 {name=l15 sig_type=std_logic lab=vss}
C {lab_pin.sym} 470 -100 0 1 {name=l16 sig_type=std_logic lab=vss}
C {sky130_fd_pr/res_xhigh_po_0p35.sym} 170 60 0 0 {name=RS L=16 model=res_xhigh_po_0p35 spiceprefix=X mult=1}
C {lab_pin.sym} 170 30 0 1 {name=l17 sig_type=std_logic lab=rs}
C {lab_pin.sym} 170 90 0 1 {name=l18 sig_type=std_logic lab=vss}
C {lab_pin.sym} 150 60 0 0 {name=l19 sig_type=std_logic lab=vss}
C {sky130_fd_pr/pfet_01v8.sym} 700 120 0 0 {name=MS1a W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 720 150 0 1 {name=l20 sig_type=std_logic lab=x}
C {lab_pin.sym} 680 120 0 0 {name=l21 sig_type=std_logic lab=vss}
C {lab_pin.sym} 720 90 0 1 {name=l22 sig_type=std_logic lab=s1a}
C {lab_pin.sym} 720 120 0 1 {name=l23 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 700 -30 0 0 {name=MS1b W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 720 0 0 1 {name=l24 sig_type=std_logic lab=s1a}
C {lab_pin.sym} 680 -30 0 0 {name=l25 sig_type=std_logic lab=vss}
C {lab_pin.sym} 720 -60 0 1 {name=l26 sig_type=std_logic lab=s1b}
C {lab_pin.sym} 720 -30 0 1 {name=l27 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 700 -180 0 0 {name=MS1c W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 720 -150 0 1 {name=l28 sig_type=std_logic lab=s1b}
C {lab_pin.sym} 680 -180 0 0 {name=l29 sig_type=std_logic lab=vss}
C {lab_pin.sym} 720 -210 0 1 {name=l30 sig_type=std_logic lab=s1c}
C {lab_pin.sym} 720 -180 0 1 {name=l31 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 900 120 0 0 {name=MS1d W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 920 150 0 1 {name=l32 sig_type=std_logic lab=s1c}
C {lab_pin.sym} 880 120 0 0 {name=l33 sig_type=std_logic lab=vss}
C {lab_pin.sym} 920 90 0 1 {name=l34 sig_type=std_logic lab=s1d}
C {lab_pin.sym} 920 120 0 1 {name=l35 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 900 -30 0 0 {name=MS1e W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 920 0 0 1 {name=l36 sig_type=std_logic lab=s1d}
C {lab_pin.sym} 880 -30 0 0 {name=l37 sig_type=std_logic lab=vss}
C {lab_pin.sym} 920 -60 0 1 {name=l38 sig_type=std_logic lab=s1e}
C {lab_pin.sym} 920 -30 0 1 {name=l39 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 900 -180 0 0 {name=MS1f W=0.6 L=20 nf=1 mult=1 ad=0.174 as=0.174 pd=1.78 ps=1.78 nrd=0.483333 nrs=0.483333 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 920 -150 0 1 {name=l40 sig_type=std_logic lab=s1e}
C {lab_pin.sym} 880 -180 0 0 {name=l41 sig_type=std_logic lab=vss}
C {lab_pin.sym} 920 -210 0 1 {name=l42 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 920 -180 0 1 {name=l43 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/nfet_01v8.sym} 750 300 0 0 {name=MS2 W=7 L=1 nf=1 mult=2 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 770 270 0 1 {name=l44 sig_type=std_logic lab=x}
C {lab_pin.sym} 730 300 0 0 {name=l45 sig_type=std_logic lab=vbn}
C {lab_pin.sym} 770 330 0 1 {name=l46 sig_type=std_logic lab=vss}
C {lab_pin.sym} 770 300 0 1 {name=l47 sig_type=std_logic lab=vss}
C {sky130_fd_pr/nfet_01v8.sym} 1130 150 0 0 {name=MS3 W=0.42 L=2 nf=1 mult=1 ad=0.1218 as=0.1218 pd=1.42 ps=1.42 nrd=0.690476 nrs=0.690476 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 1150 120 0 1 {name=l48 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 1110 150 0 0 {name=l49 sig_type=std_logic lab=x}
C {lab_pin.sym} 1150 180 0 1 {name=l50 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1150 150 0 1 {name=l51 sig_type=std_logic lab=vss}
C {sky130_fd_pr/pfet_01v8.sym} 1350 -300 0 0 {name=MR1 W=4 L=2 nf=1 mult=1 ad=1.16 as=1.16 pd=8.58 ps=8.58 nrd=0.0725 nrs=0.0725 sa=0 sb=0 sd=0 model=pfet_01v8 spiceprefix=X}
C {lab_pin.sym} 1370 -270 0 1 {name=l52 sig_type=std_logic lab=vref}
C {lab_pin.sym} 1330 -300 0 0 {name=l53 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 1370 -330 0 1 {name=l54 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1370 -300 0 1 {name=l55 sig_type=std_logic lab=vdd}
C {sky130_fd_pr/nfet_01v8.sym} 1350 -100 0 0 {name=MR2 W=7 L=1 nf=1 mult=6 ad=2.03 as=2.03 pd=14.58 ps=14.58 nrd=0.0414286 nrs=0.0414286 sa=0 sb=0 sd=0 model=nfet_01v8 spiceprefix=X}
C {lab_pin.sym} 1370 -130 0 1 {name=l56 sig_type=std_logic lab=vref}
C {lab_pin.sym} 1330 -100 0 0 {name=l57 sig_type=std_logic lab=vref}
C {lab_pin.sym} 1370 -70 0 1 {name=l58 sig_type=std_logic lab=vss}
C {lab_pin.sym} 1370 -100 0 1 {name=l59 sig_type=std_logic lab=vss}
C {sky130_fd_pr/cap_mim_m3_1.sym} 1600 -150 0 0 {name=CREF model=tcleval($::MIM_MODEL) W=22.25 L=22.25 MF=2 spiceprefix=X}
C {lab_pin.sym} 1600 -180 0 1 {name=l60 sig_type=std_logic lab=vref}
C {lab_pin.sym} 1600 -120 0 1 {name=l61 sig_type=std_logic lab=vss}
