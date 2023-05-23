`timescale 1ns/1ps
`default_nettype none
module tb_top #(
  parameter integer FIFO_DEPTH = 10,
  parameter integer WRITE_FREQ = 1,
  parameter integer READ_FREQ = 1
)(
  input  wire clk_w_i,
  input  wire clk_r_i,
  input  wire we_i,
  input  wire re_i,
  output wire fifo_empty_o,
  output wire fifo_full_o
);

  generate
    if (WRITE_FREQ == READ_FREQ ) begin
      // Sync FIFO since read and write frequencies are identical
      circ_fifo #() fifo_inst ( );
    end
    else begin
      // Async FIFO since read and write frequencies differ
      cdc_fifo #() fifo_inst ();
    end
  endgenerate

endmodule
`default_nettype wire