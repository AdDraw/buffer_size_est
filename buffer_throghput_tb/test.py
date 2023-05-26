import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, FallingEdge, ReadOnly, ReadWrite
from cocotb.regression import TestSuccess

class Interface:
    def __init__(self, clk, rst) -> None:
        self.clk = clk
        self.rst = rst

    async def redge(self, ro=False):
        await RisingEdge(self.clk)
        if ro:
          await ReadOnly()

    async def fedge(self, ro=False):
        await FallingEdge(self.clk)
        if ro:
          await ReadOnly()

    async def reset(self, cycles: int = 5, active_high: bool = False):
        self.rst.setimmediatevalue(active_high)
        await ClockCycles(self.clk, cycles)
        self.rst.setimmediatevalue(not active_high)

class WriteInterface(Interface):
    def __init__(self, dut) -> None:
        self.we = dut.we_i
        self.wrdy = dut.wrdy_o
        super().__init__(dut.clk_w_i, dut.rst_ni)

class ReadInterface(Interface):
    def __init__(self, dut) -> None:
        self.re = dut.re_i
        self.rrdy = dut.rrdy_o
        super().__init__(dut.clk_r_i, dut.rst_ni)

class Driver:
    def __init__(self, wif: WriteInterface, burst_size, idle_cyc_between_bursts, number_of_bursts) -> None:
        self._if = wif
        self.bs = burst_size
        self.idle_bb = idle_cyc_between_bursts
        self.bn = number_of_bursts

    async def write_constantly(self):
        """_summary_
          Start writing as soon as wrdy has been asserted, after this point don't care about
          wrdy, write data as fast as required, but write with a given bandwidth
        """
        while True:
          # WAIT FOR FIFO WRITABLE
          while not self._if.wrdy.value:
              await self._if.redge(ro=True)
          # START ISSUING WRITES(as many as requested)
          for burst_id in range(self.bn):
            for i in range(self.bs): # BURST WRITE
              await self._if.redge()
              self._if.we.setimmediatevalue(1)
            for i in range(self.idle_bb): # IDLE CYCLES BETWEEN BURSTS
              await self._if.redge()
              self._if.we.setimmediatevalue(0)
          break

class Receiver:
    def __init__(self, rif: ReadInterface, burst_size, idle_cyc_between_bursts) -> None:
        self._if = rif
        self.bs = burst_size
        self.idle_bb = idle_cyc_between_bursts
        self.received = []

    async def read_constantly(self):
        """_summary_
          Read data from the FIFO as soon as it is available
          using a burst read functionality
          read data in a burst, then stop for a set number of cycles
          and then continue reading
        """
        while True:
            # wait untill not empty
            while not self._if.rrdy.value:
                await self._if.redge(ro=True)
            # Start reading in bursts
            while True:
              for i in range(self.bs): # BURST WRITE
                await self._if.redge()
                self._if.re.setimmediatevalue(1)
              for i in range(self.idle_bb): # IDLE CYCLES BETWEEN BURSTS
                await self._if.redge()
                self._if.re.setimmediatevalue(0)

class TB:
    def __init__(self, dut) -> None:
        self.dut = dut
        wbs = dut.WRITE_BURST_SIZE.value
        wbi = dut.WRITE_IDLE_CYCLES_BETWEEN_BURSTS.value
        wbn = dut.WRITE_NUMBER_OF_BURSTS.value
        rbs = dut.READ_BURST_SIZE.value
        rbi = dut.READ_IDLE_CYCLES_BETWEEN_BURSTS.value
        self.wif = WriteInterface(dut)
        self.rif = ReadInterface(dut)
        self.driver = Driver(self.wif, burst_size=wbs, idle_cyc_between_bursts=wbi, number_of_bursts=wbn)
        self.reader = Receiver(self.rif, burst_size=rbs, idle_cyc_between_bursts=rbi)
        self.init_ports()

    def init_ports(self):
        # self.dut.cA_din_i.setimmediatevalue(0)
        self.dut.we_i.setimmediatevalue(0)
        self.dut.re_i.setimmediatevalue(0)
        self.dut.rst_ni.setimmediatevalue(1)

    async def check(self):
      while self.dut.wrdy_o.value:
        await self.wif.redge(ro=True)

        # Count how many values in the FIFO

      await self.wif.redge()
      raise ValueError("Fifo got full!!, Wrong FIFO size")

@cocotb.test()
async def test(dut):
  d = dut
  # Frequency
  w_freq = dut.WRITE_FREQ.value
  r_freq = dut.READ_FREQ.value
  W_CLOCK_PERIOD = 1/w_freq * 1e9 # normalize to ns
  R_CLOCK_PERIOD = 1/r_freq * 1e9 # normalize to ns

  cocotb.log.info(f"Write Freq: {w_freq}Hz Period: {W_CLOCK_PERIOD}ns")
  cocotb.log.info(f"Read Freq: {r_freq}Hz Period: {R_CLOCK_PERIOD}ns")

  # Clocks
  cocotb.start_soon(Clock(d.clk_r_i, R_CLOCK_PERIOD, units="ns").start(start_high=False))
  cocotb.start_soon(Clock(d.clk_w_i, W_CLOCK_PERIOD, units="ns").start(start_high=False))

  tb = TB(dut)
  await tb.wif.reset()

  cocotb.start_soon(tb.check())
  cocotb.start_soon(tb.reader.read_constantly())
  await tb.driver.write_constantly()

  await ClockCycles(dut.clk_w_i, 5) # wait for eventual FULL assertion

  raise TestSuccess



