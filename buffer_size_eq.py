import math
import tabulate as tab
import argparse

import subprocess as subp

def main(write_burst_size, read_burst_size, write_idle_cycle, read_idle_cycle, frequency_write, frequency_read, number_of_bursts):
  period_write = 1 / frequency_write
  period_read = 1 / frequency_read
  time_to_write_burst_cycle = write_burst_size + write_idle_cycle
  time_to_write_n_bursts_cycle = number_of_bursts * (write_burst_size + write_idle_cycle)
  time_to_write_burst_period = time_to_write_burst_cycle * period_write
  time_to_write_n_bursts_period = time_to_write_burst_period * number_of_bursts
  time_to_read_burst_cycle = read_burst_size + read_idle_cycle
  time_to_read_burst_period = time_to_read_burst_cycle * period_read
  read_per_second = read_burst_size / time_to_read_burst_period
  read_per_cycle = read_burst_size / time_to_read_burst_cycle
  write_per_second = write_burst_size / time_to_write_burst_period
  write_per_cycle = write_burst_size / time_to_write_burst_cycle
  read_in_time_to_write_burst = math.floor(time_to_write_n_bursts_period * read_per_second)
  min_fifo_size_any = (write_burst_size * number_of_bursts) - read_in_time_to_write_burst
  min_fifo_size = min_fifo_size_any if (min_fifo_size_any > 0) else 0


  print("1. Burst data:")
  print(tab.tabulate([["write", write_burst_size, write_idle_cycle, number_of_bursts,number_of_bursts*write_burst_size],
                      ["read", read_burst_size, read_idle_cycle]],
                     headers=["type", "Burst Size[words]", "Cycles between bursts[cyc]", "Number of write bursts", "Total data to write"]))
  print()
  print("2. Frequency:")
  print(tab.tabulate([["write", frequency_write, period_write], ["read", frequency_read, period_read]], headers=["type", "freq[Hz]", "period[s]"]))
  print()
  print(f"3. Time required to process bursts:")
  print(tab.tabulate([["single write", time_to_write_burst_cycle, time_to_write_burst_period, write_per_cycle, write_per_second],
                      ["multiple writes", time_to_write_n_bursts_cycle, time_to_write_n_bursts_period],
                      ["single read", time_to_read_burst_cycle, time_to_read_burst_period, read_per_cycle, read_per_second]],
                     headers=["type", "Time to process[cycles]", "Time to process[s]", "words per cycle", "Words per second"]))
  print()


  if (min_fifo_size_any < 0):
    print(f"!!! In the time to write all bursts({time_to_write_n_bursts_period}s) {read_in_time_to_write_burst} words can be read")
    print(f"!!! {read_in_time_to_write_burst} words is higher than {write_burst_size*number_of_bursts} words written in this time period thus")
    print("!!! Read Bandwidth is good enough that FIFO is not required!")

  else:
    print(f"In the time to write the {number_of_bursts} burst/bursts({number_of_bursts*write_burst_size} words, {time_to_write_n_bursts_period}s) {read_in_time_to_write_burst} words can be read")
    print(f"\nMinimum FIFO BUFFER WORD SIZE({write_burst_size*number_of_bursts} - {read_in_time_to_write_burst}): {min_fifo_size}")

  return min_fifo_size

if __name__ == "__main__":
  parser = argparse.ArgumentParser(add_help=True, usage="Use to calculate the minimum FIFO word size required to handle a given read and write bandwidth")
  parser.add_argument("--wbs", type=int, default=1024, help="Write Burst Size, how many words in a bursts are written into the FIFO, def=1024")
  parser.add_argument("--rbs", type=int, default=10, help="Read Burst Size, how many words in a bursts are read from the FIFO, def=10")
  parser.add_argument("--wbi", type=int, default=1, help="Write Burst Idle Cycles, how many cycles is there between 2 write bursts, def=1")
  parser.add_argument("--rbi", type=int, default=1, help="Read Burst Idle Cycles, how many cycles is there between 2 read bursts, def=1")
  parser.add_argument("--fw", type=int, default=1, help="Write Frequency in Hz, def=1")
  parser.add_argument("--fr", type=int, default=1, help="Read Frequency in Hz, def=1")
  parser.add_argument("--wbn", type=int, default=1, help="How many write bursts in a sequence is there to process, def=1")
  parser.add_argument("--testbench-check", default=False, action="store_true", help="Runs testbench check after calculations")
  args = parser.parse_args()

  write_burst_size = args.wbs
  read_burst_size = args.rbs
  write_idle_cycle = args.wbi
  read_idle_cycle = args.rbi
  frequency_write = args.fw
  frequency_read = args.fr
  number_of_write_bursts = args.wbn
  testbench_check = args.testbench_check

  min_fifo_size = main(write_burst_size,
                       read_burst_size,
                       write_idle_cycle,
                       read_idle_cycle,
                       frequency_write,
                       frequency_read,
                       number_of_write_bursts
                       )

  if testbench_check:
    # Testbench now only deals in FIFO size equal to powers of 2
    # we have to take the fifo size and generate a ceil(log())
    fifo_depth_w = math.ceil(math.log2(min_fifo_size))
    print(f"Adjusted minimum FIFO SIZE {fifo_depth_w}, because {pow(2, fifo_depth_w)} >= {min_fifo_size}")

    print("-----------------------------------")
    print("-- Testbench check in progress... -")
    print("-----------------------------------")

    shell_cmd = f"make" \
                f" WRITE_BURST_SIZE={write_burst_size}" \
                f" WRITE_IDLE_CYCLES_BETWEEN_BURSTS={write_idle_cycle}" \
                f" WRITE_NUMBER_OF_BURSTS={number_of_write_bursts}" \
                f" READ_BURST_SIZE={read_burst_size}" \
                f" READ_IDLE_CYCLES_BETWEEN_BURSTS={read_idle_cycle}" \
                f" FIFO_DEPTH_W={fifo_depth_w}" \
                f" MIN_FIFO_SIZE={min_fifo_size}" \
                f" WRITE_FREQ={frequency_write}" \
                f" READ_FREQ={frequency_read}"


    import os
    cdw = os.getcwd()

    shell_cmd = shell_cmd.split(" ")

    print(shell_cmd)

    subp.Popen(args="make clean".split(" "), shell=False, cwd=f"{cdw}/buffer_throghput_tb/", stdout=subp.PIPE, stderr=subp.STDOUT)

    make_proc = subp.Popen(args=shell_cmd, shell=False, cwd=f"{cdw}/buffer_throghput_tb/", stdout=subp.PIPE, stderr=subp.STDOUT)
    stdout, stderr = make_proc.communicate()

    stdout = stdout.decode()
    if stderr is not None:
      stderr = stderr.decode()
    return_code = make_proc.returncode

    print(f"stdout: {stdout}")
    print(f"stderr: {stderr}")
    print(f"return_code: {return_code}")