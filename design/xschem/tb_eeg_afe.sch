v {xschem version=3.4.4 file_version=1.2}

G {}
K {}
V {}
S {}
E {}
T {Testbench: power-up, reset, 100 uV / 10 Hz tone} -260 -620 0 0 0.6 0.6 {}
T {Simulation > Netlist, then Simulate. Waveforms: Waves > Load (tb_eeg_afe.raw) or the ngspice plot.} -260 -580 0 0 0.3 0.3 {}
T {Pads: the Tiny Tapeout analog path is modelled as 500 Ohm + 5 pF per pin. Load: 15 pF || 1 MOhm (scope probe / ADC).} -260 -555 0 0 0.3 0.3 {}
T {rst (ui_in[0]) is high for the first 10 ms; the tone starts at 20 ms. Expect gain = 77 V/V and VREF = 0.45 V.} -260 -530 0 0 0.3 0.3 {}
T {Corner: edit the CORNER instance (tt, ss, ff, sf, fs). Temperature: .temp line in the code block.} -260 -505 0 0 0.3 0.3 {}
C {eeg_afe_top.sym} 700 -150 0 0 {name=XTOP}
C {lab_pin.sym} 580 -180 0 0 {name=l1 sig_type=std_logic lab=ua0}
C {lab_pin.sym} 820 -150 0 1 {name=l2 sig_type=std_logic lab=ua1}
C {lab_pin.sym} 580 -120 0 0 {name=l3 sig_type=std_logic lab=rst}
C {lab_pin.sym} 700 -250 0 0 {name=l4 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 700 -50 0 0 {name=l5 sig_type=std_logic lab=0}
C {vsource.sym} 1100 -400 0 0 {name=VDD value="PWL(0 0 100u 1.8)" m=1 savecurrent=false}
C {lab_pin.sym} 1100 -430 0 1 {name=l6 sig_type=std_logic lab=vdd}
C {lab_pin.sym} 1100 -370 0 1 {name=l7 sig_type=std_logic lab=0}
C {vsource.sym} 0 -150 0 0 {name=VIN value="SIN(0 100u 10 20m)" m=1 savecurrent=false}
C {lab_pin.sym} 0 -180 0 1 {name=l8 sig_type=std_logic lab=src}
C {lab_pin.sym} 0 -120 0 1 {name=l9 sig_type=std_logic lab=0}
C {res.sym} 200 -150 0 0 {name=RSW1 value="500" m=1 savecurrent=false}
C {lab_pin.sym} 200 -180 0 1 {name=l10 sig_type=std_logic lab=src}
C {lab_pin.sym} 200 -120 0 1 {name=l11 sig_type=std_logic lab=ua0}
C {capa.sym} 350 -50 0 0 {name=CP1 value="5p" m=1 savecurrent=false}
C {lab_pin.sym} 350 -80 0 1 {name=l12 sig_type=std_logic lab=ua0}
C {lab_pin.sym} 350 -20 0 1 {name=l13 sig_type=std_logic lab=0}
C {vsource.sym} 0 100 0 0 {name=VRST value="PWL(0 0 50u 0 60u 1.8 10m 1.8 10.01m 0)" m=1 savecurrent=false}
C {lab_pin.sym} 0 70 0 1 {name=l14 sig_type=std_logic lab=rst}
C {lab_pin.sym} 0 130 0 1 {name=l15 sig_type=std_logic lab=0}
C {res.sym} 1100 -150 0 0 {name=RSW2 value="500" m=1 savecurrent=false}
C {lab_pin.sym} 1100 -180 0 1 {name=l16 sig_type=std_logic lab=ua1}
C {lab_pin.sym} 1100 -120 0 1 {name=l17 sig_type=std_logic lab=pad}
C {capa.sym} 1250 -50 0 0 {name=CL value="15p" m=1 savecurrent=false}
C {lab_pin.sym} 1250 -80 0 1 {name=l18 sig_type=std_logic lab=pad}
C {lab_pin.sym} 1250 -20 0 1 {name=l19 sig_type=std_logic lab=0}
C {res.sym} 1400 -50 0 0 {name=RL value="1meg" m=1 savecurrent=false}
C {lab_pin.sym} 1400 -80 0 1 {name=l20 sig_type=std_logic lab=pad}
C {lab_pin.sym} 1400 -20 0 1 {name=l21 sig_type=std_logic lab=0}
C {sky130_fd_pr/corner.sym} 0 300 0 0 {name=CORNER only_toplevel=false corner=tt}
C {code_shown.sym} 300 250 0 0 {name=MIM_IDEAL only_toplevel=false value="tcleval(* MIM capacitors: ideal C fitted to the PDK model (<0.1 % error), [set ::MIM_MODEL cap_mim_m3_1_ideal]
* The PDK model's milliohm series resistors make transient runs ~200x slower. LVS netlists use the PDK model.
.subckt sky130_fd_pr__cap_mim_m3_1_ideal c0 c1 w=1 l=1 mf=1
C1 c0 c1 \{2.0e-15*w*l + 0.336e-15*(w+l)\}
.ends
)"}
C {code_shown.sym} 700 250 0 0 {name=CONTROL only_toplevel=false value="* gmin/abstol: the default gmin=1e-12 adds ~1 Tohm of fake leakage at the 1e13-ohm nodes
.option gmin=1e-15 abstol=1e-15 klu
.temp 27
.ic v(xtop.xafe.inn)=0.45 v(xtop.xafe.inp)=0.45 v(ua1)=0.45
.control
  save v(ua0) v(ua1) v(pad) v(rst) v(vdd) v(xtop.vref) v(xtop.vbp) i(vdd)
  * tmax = 2 us: coarser steps give a false output jump when rst is released
  tran 1u 0.25 0 2u uic
  write tb_eeg_afe.raw
  meas tran vref_dc avg v(xtop.vref) from=0.15 to=0.25
  meas tran iddq avg i(vdd) from=0.15 to=0.25
  meas tran vpp_out pp v(pad) from=0.15 to=0.25
  meas tran vpp_in pp v(ua0) from=0.15 to=0.25
  let gain = vpp_out / vpp_in
  print gain
  plot v(pad) v(xtop.vref)
.endc"}
