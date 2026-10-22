v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Neonatal EEG front-end: Tiny Tapeout analog core} -260 -620 0 0 0.6 0.6 {}
T {ua0 = EEG input (ua[0]), ua1 = output (ua[1]), rst = ui_in[0] (active high), vdd = VDPWR, vss = VGND.} -260 -580 0 0 0.3 0.3 {}
T {The Tiny Tapeout wrapper (tt_um_...) adds the remaining template pins and ties uo_out, uio_out, uio_oe to VGND in layout.} -260 -555 0 0 0.3 0.3 {}
C {iopin.sym} -240 -400 0 0 {name=p1 lab=ua0}
C {iopin.sym} -240 -360 0 0 {name=p2 lab=ua1}
C {ipin.sym} -240 -320 0 0 {name=p3 lab=rst}
C {iopin.sym} -240 -280 0 0 {name=p4 lab=vdd}
C {iopin.sym} -240 -240 0 0 {name=p5 lab=vss}
C {bias.sym} 200 0 0 0 {name=XBIAS}
C {lab_pin.sym} 200 -90 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 200 90 0 0 {name=l2 sig_type=std_logic lab=vss}
C {lab_pin.sym} 290 -20 0 1 {name=l3 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 290 20 0 1 {name=l4 sig_type=std_logic lab=vref}
C {afe.sym} 650 0 0 0 {name=XAFE}
C {lab_pin.sym} 540 -60 0 0 {name=l5 sig_type=std_logic lab=ua0}
C {lab_pin.sym} 760 0 0 1 {name=l6 sig_type=std_logic lab=ua1}
C {lab_pin.sym} 650 -120 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 650 120 0 0 {name=l8 sig_type=std_logic lab=vss}
C {lab_pin.sym} 540 -20 0 0 {name=l9 sig_type=std_logic lab=vbp}
C {lab_pin.sym} 540 20 0 0 {name=l10 sig_type=std_logic lab=vref}
C {lab_pin.sym} 540 60 0 0 {name=l11 sig_type=std_logic lab=rst}
C {code_shown.sym} 200 300 0 0 {name=MIM_PDK only_toplevel=true value="tcleval(* MIM model: sky130_fd_pr__[set ::MIM_MODEL [lindex [list [set ::MIM_MODEL] cap_mim_m3_1] [expr [xschem get currsch] == 0]]] (PDK model when this is the top, for LVS))"}
