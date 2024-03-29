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
        super().__init__(dut.clk_w_o, dut.rst_ni)
        # stats
        self.enable = 0
        self.idle = 0

    async def stats(self):
      while True:
        await self.redge()
        if (self.we.value.integer == 1):
          self.enable += 1
        else:
          self.idle += 1

    def print_stats(self):
      print(f"WIF STATS: EN {self.enable}: IDLE: {self.idle} RATIO: {self.enable/(self.enable+self.idle)}")

class ReadInterface(Interface):
    def __init__(self, dut) -> None:
        self.re = dut.re_i
        self.rrdy = dut.rrdy_o
        super().__init__(dut.clk_r_o, dut.rst_ni)
        # stats
        self.enable = 0
        self.idle = 0

    async def stats(self):
      while True:
        await self.redge()
        if (self.re.value.integer == 1):
          self.enable += 1
        else:
          self.idle += 1

    def print_stats(self):
      print(f"RIF STATS: EN {self.enable}: IDLE: {self.idle} RATIO: {self.enable/(self.enable+self.idle)}")


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
        self._if.we.setimmediatevalue(0)
        while True:
          # WAIT FOR FIFO WRITABLE
          while not self._if.wrdy.value:
              await self._if.redge(ro=True)
          # START ISSUING WRITES(as many as requested)
          cocotb.start_soon(self._if.stats())
          for burst_id in range(self.bn):
            for i in range(self.bs): # BURST WRITE
              await self._if.redge()
              self._if.we.setimmediatevalue(1)
            for i in range(self.idle_bb): # IDLE CYCLES BETWEEN BURSTS
              await self._if.redge()
              self._if.we.setimmediatevalue(0)
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
            cocotb.start_soon(self._if.stats())
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
        self.max_size_required = 0
        wbs = dut.WRITE_BURST_SIZE.value
        wbi = dut.WRITE_IDLE_CYCLES_BETWEEN_BURSTS.value
        wbn = dut.WRITE_NUMBER_OF_BURSTS.value
        rbs = dut.READ_BURST_SIZE.value
        rbi = dut.READ_IDLE_CYCLES_BETWEEN_BURSTS.value
        self.min_fifo_size = self.dut.MIN_FIFO_SIZE.value
        self._async = True if (dut.WRITE_PERIOD.value != dut.READ_PERIOD.value) else False
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
      fifo_inst = self.dut.genblk1.fifo_inst
      words_in_fifo = fifo_inst.a_words_in_fifo if self._async else fifo_inst.words_in_fifo

      while True:
        await self.wif.redge(ro=False)
        if words_in_fifo.value.integer > self.max_size_required:
          self.max_size_required = words_in_fifo.value.integer
        if (words_in_fifo.value.integer > self.min_fifo_size):
          # if at any point the number of words left in the FIFO goes over the MIN_FIFO_SIZE, it means
          # that in a realistic implementation writer would be writing to a full FIFO
          break

        # Count how many values in the FIFO
      fifo_word_left_count = words_in_fifo.value.integer
      await self.wif.redge(ro=True)

      self.wif.print_stats()
      self.rif.print_stats()
      print(self.max_size_required)
      raise ValueError(f"Minimal FIFO size estimated({self.min_fifo_size}) was not enough! TB terminated at {fifo_word_left_count} words in FIFO")

@cocotb.test()
async def test(dut):
  d = dut
  # Frequency
  w_period = d.WRITE_PERIOD.value # in ns
  r_period = d.READ_PERIOD.value # in ns
  w_freq = (1/w_period) * 1e9 # normalize to Hz
  r_freq = (1/r_period) * 1e9 # normalize to Hz
  cocotb.log.info(f"Write Freq: {w_freq}Hz Period: {w_period}ns")
  cocotb.log.info(f"Read Freq: {r_freq}Hz Period: {r_period}ns")

  tb = TB(dut)
  await tb.wif.reset()

  cocotb.start_soon(tb.check())
  cocotb.start_soon(tb.reader.read_constantly())
  await tb.driver.write_constantly()

  await ClockCycles(dut.clk_w_o, 5) # wait for eventual FULL assertion

  if (tb.max_size_required == tb.min_fifo_size):
    raise TestSuccess
  else:
    raise ValueError(f"Noted a different number of words written to the fifo at peak than min_fifo_size suggests, expected: {tb.min_fifo_size}, received: {tb.max_size_required}")

