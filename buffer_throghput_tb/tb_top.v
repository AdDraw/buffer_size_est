`timescale 1ns/1ps
`default_nettype none
module tb_top #(
  parameter integer FIFO_DEPTH_W = 2,
  parameter integer WRITE_FREQ   = 1,
  parameter integer READ_FREQ    = 1,
  // For easy cocotb access
  parameter integer WRITE_BURST_SIZE = 10,
  parameter integer WRITE_IDLE_CYCLES_BETWEEN_BURSTS = 10,
  parameter integer WRITE_NUMBER_OF_BURSTS = 10,
  parameter integer READ_BURST_SIZE = 10,
  parameter integer READ_IDLE_CYCLES_BETWEEN_BURSTS = 10
)(
  input  wire rst_ni,
  // Write
  input  wire clk_w_i,
  input  wire we_i,
  output wire wrdy_o,
  // Read Port
  input  wire clk_r_i,
  input  wire re_i,
  output wire rrdy_o
);
  localparam integer DATA_W = 1;
  generate
    if (WRITE_FREQ == READ_FREQ ) begin
      // Sync FIFO since read and write frequencies are identical
      wire rdata;
      wire full;
      wire empty;
      circ_fifo #(
        .DATA_W       (DATA_W),
        .FIFO_DEPTH_W (FIFO_DEPTH_W),
        .ID           (0)
      ) fifo_inst (
        .clk_i       (clk_w_i),
        .rst_ni      (rst_ni),
        .wr_en_i     (we_i),
        .rd_en_i     (re_i),
        .data_i      (1'b1),
        .data_o      (rdata),
        .full_o      (full),
        .empty_o     (empty),
        .overflow_o  (),
        .underflow_o ()
      );
      assign wrdy_o = ~full;
      assign rrdy_o = ~empty;
    end
    else begin
      wire rdata;
      // Async FIFO since read and write frequencies differ
      async_fifo_Ndeep #(
        .DATA_WIDTH         (DATA_W),
        .BUFFER_DEPTH_POWER (FIFO_DEPTH_W )
      ) fifo_inst (
        .clk_a_i  (clk_w_i),
        .a_rst_ni (rst_ni),
        .a_we_i   (we_i),
        .a_din_i  (1'b1),
        .a_wrdy_o (wrdy_o),
        .clk_b_i  (clk_r_i),
        .b_rst_ni (rst_ni),
        .b_re_i   (re_i),
        .b_dout_o (rdata),
        .b_rrdy_o (rrdy_o)
      );
    end
  endgenerate

  initial begin
    $dumpvars(0);
  end

endmodule
`default_nettype wire