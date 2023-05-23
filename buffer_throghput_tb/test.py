import cocotb
from cocotb.clock import Clock

W_CLOCK_PERIOD = 1
R_CLOCK_PERIOD = 1
async def test(dut):
  d = dut
  cocotb.start_soon(Clock(d.clk_r_i, R_CLOCK_PERIOD).start(start_high=False))
  cocotb.start_soon(Clock(d.clk_w_i, W_CLOCK_PERIOD).start(start_high=False))


