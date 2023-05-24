import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

W_CLOCK_PERIOD = 1
R_CLOCK_PERIOD = 1

@cocotb.test()
async def test(dut):
  d = dut
  cocotb.start_soon(Clock(d.clk_r_i, R_CLOCK_PERIOD, units="ns").start(start_high=False))
  cocotb.start_soon(Clock(d.clk_w_i, W_CLOCK_PERIOD, units="ns").start(start_high=False))

  d.re_i.value = 0
  d.we_i.value = 0
  d.rst_ni.value = 0
  await ClockCycles(d.clk_w_i, 10)
  d.rst_ni.value = 1
  await ClockCycles(d.clk_w_i, 10)
