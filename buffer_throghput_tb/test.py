import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

W_CLOCK_PERIOD = 1
R_CLOCK_PERIOD = 1

class WriteDriver():
  """_summary_
    Module adhering to a specific set of write parameters
    generates fifo write enable signals no matter if the fifo is full
    because then we can tell if Write Bandwidth vs Read Bandwidth vs Fifo size is good enough
  """
  def __init__(self) -> None:
    pass

class ReadDriver():
  """_summary_
    Module adhering to a specific set of read parameters
    generates fifo read enable signals(taking into consideration if fifo is empty)
    because then we can tell if Write Bandwidth vs Read Bandwidth vs Fifo size is good enough
  """
  def __init__(self) -> None:
    pass

class Tb:
  """_summary_
    Holds tools necessary to check/test that FIFO size is good enough
    to handle read and write bandwidths
  """
  def __init__(self, dut):
    self.dut = dut
    self.clk_w = dut.clk_w_i
    self.write_drv = WriteDriver()
    self.read_drv =  ReadDriver()
    self.dut.re_i.value = 0
    self.dut.we_i.value = 0

  async def reset(self, reset_time=10, polarity=False):
    self.dut.rst_ni.value = polarity
    await ClockCycles(self.clk_w, reset_time)
    self.dut.rst_ni.value = not polarity
    await ClockCycles(self.clk_w, reset_time)

@cocotb.test()
async def test(dut):
  d = dut
  cocotb.start_soon(Clock(d.clk_r_i, R_CLOCK_PERIOD, units="ns").start(start_high=False))
  cocotb.start_soon(Clock(d.clk_w_i, W_CLOCK_PERIOD, units="ns").start(start_high=False))

  tb = Tb(dut)
  await tb.reset()

