/*
 * Copyright (c) 2026 Sai Chaithr Aravapalli
 * SPDX-License-Identifier: Apache-2.0
 *
 * Black-box stub for the analog layout (GDS/LEF are produced in Magic/KLayout).
 */

`default_nettype none

module tt_um_saichaithr_eeg_afe (
    input  wire       VGND,
    input  wire       VDPWR,    // 1.8 V supply
    input  wire [7:0] ui_in,    // ui_in[0] = rst (reset / fast settle, active high)
    output wire [7:0] uo_out,   // unused, tied to VGND in layout
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,  // unused, tied to VGND in layout
    output wire [7:0] uio_oe,   // unused, tied to VGND in layout
    inout  wire [7:0] ua,       // ua[0] = EEG input, ua[1] = amplified output
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

endmodule
