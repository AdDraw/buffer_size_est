import math
import tabulate as tab
import argparse

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
  args = parser.parse_args()

  write_burst_size = args.wbs
  read_burst_size = args.rbs
  write_idle_cycle = args.wbi
  read_idle_cycle = args.rbi
  frequency_write = args.fw
  frequency_read = args.fr
  number_of_write_bursts = args.wbn

  min_fifo_size = main(write_burst_size,
                       read_burst_size,
                       write_idle_cycle,
                       read_idle_cycle,
                       frequency_write,
                       frequency_read,
                       number_of_write_bursts
                       )