`default_nettype none
module tb_top #(
  parameter integer FIFO_DEPTH_W = 2,
  parameter integer MIN_FIFO_SIZE = 2,
  // For easy cocotb access
  parameter integer WRITE_BURST_SIZE = 10,
  parameter integer WRITE_IDLE_CYCLES_BETWEEN_BURSTS = 10,
  parameter integer WRITE_NUMBER_OF_BURSTS = 10,
  parameter integer READ_BURST_SIZE = 10,
  parameter integer READ_IDLE_CYCLES_BETWEEN_BURSTS = 10,
  // CLOCKS
  parameter real WRITE_PERIOD = 20,
  parameter real READ_PERIOD  = 20
)(
  input  wire rst_ni,
  // Write
  output  wire clk_w_o, // clk just for ext sampling
  input  wire we_i,
  output wire wrdy_o,
  // Read Port
  output  wire clk_r_o, // clk just for ext sampling
  input  wire re_i,
  output wire rrdy_o
);
  reg clk_r = 1'b0;
  reg clk_w = 1'b0;
  initial begin
    $display("WRITE_PERIOD: %0fns, half: %0fns", WRITE_PERIOD, WRITE_PERIOD/2);
    $display("READ_PERIOD : %0fns, half: %0fns", READ_PERIOD, READ_PERIOD/2);
  end
  always #(READ_PERIOD/2) clk_r <= ~clk_r;
  always #(WRITE_PERIOD/2) clk_w <= ~clk_w;

  localparam integer DATA_W = 1;
  generate
    if (READ_PERIOD == WRITE_PERIOD ) begin
      // Sync FIFO since read and write frequencies are identical
      wire rdata;
      wire full;
      wire empty;
      circ_fifo #(
        .DATA_W       (DATA_W),
        .FIFO_DEPTH_W (FIFO_DEPTH_W),
        .ID           (0)
      ) fifo_inst (
        .clk_i       (clk_w),
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
        .BUFFER_DEPTH_POWER (FIFO_DEPTH_W)
      ) fifo_inst (
        .clk_a_i  (clk_w),
        .a_rst_ni (rst_ni),
        .a_we_i   (we_i),
        .a_din_i  (1'b1),
        .a_wrdy_o (wrdy_o),
        .clk_b_i  (clk_r),
        .b_rst_ni (rst_ni),
        .b_re_i   (re_i),
        .b_dout_o (rdata),
        .b_rrdy_o (rrdy_o)
      );
    end
  endgenerate

  assign clk_w_o = clk_w;
  assign clk_r_o = clk_r;

  initial begin
    $dumpvars(0);
    #1;
  end

endmodule
`default_nettype wire