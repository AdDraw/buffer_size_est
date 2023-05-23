import math
import tabulate as tab

def main():
  number_of_bursts = 10
  write_burst_size = 1024
  write_idle_cycle = 3
  read_burst = 2
  read_idle_cycle = 1

  print("1. Burst data:")
  print(tab.tabulate([["write", write_burst_size, write_idle_cycle, number_of_bursts,number_of_bursts*write_burst_size],
                      ["read", read_burst, read_idle_cycle]],
                     headers=["type", "Burst Size[words]", "Cycles between bursts[cyc]", "Number of write bursts", "Total data to write"]))
  print()

  frequency_write = 100
  period_write = 1/ frequency_write
  frequency_read = 10
  period_read = 1/ frequency_read

  print("2. Frequency:")
  print(tab.tabulate([["write", frequency_write, period_write], ["read", frequency_read, period_read]], headers=["type", "freq[Hz]", "period[s]"]))
  print()

  time_to_write_burst_cycle = write_burst_size + write_idle_cycle
  time_to_write_n_bursts_cycle = number_of_bursts * (write_burst_size + write_idle_cycle)
  time_to_write_burst_period = time_to_write_burst_cycle * period_write
  time_to_write_n_bursts_period = time_to_write_burst_period * number_of_bursts
  time_to_read_burst_cycle = read_burst + read_idle_cycle
  time_to_read_burst_period = time_to_read_burst_cycle * period_read
  read_per_second = read_burst / time_to_read_burst_period

  print(f"3. Time required to process bursts:")
  print(tab.tabulate([["single write", time_to_write_burst_cycle, time_to_write_burst_period],
                      ["multiple writes", time_to_write_n_bursts_cycle, time_to_write_n_bursts_period],
                      ["single read", time_to_read_burst_cycle, time_to_read_burst_period]],
                     headers=["type", "Time to process[cycles]", "Time to process[s]"]))
  print()

  read_in_time_to_write_burst = math.floor(time_to_write_n_bursts_period * read_per_second)

  print("Results:")
  print(f"- In the time to write the {number_of_bursts} burst/bursts({number_of_bursts*write_burst_size} words, {time_to_write_n_bursts_period}s) {read_in_time_to_write_burst} words can be read")
  min_fifo_size_any = (write_burst_size * number_of_bursts) - read_in_time_to_write_burst
  min_fifo_size = min_fifo_size_any if (min_fifo_size_any > 0) else 0

  print(f"\nMinimum FIFO BUFFER WORD SIZE({write_burst_size*number_of_bursts} - {read_in_time_to_write_burst}): {min_fifo_size}")

  return min_fifo_size

if __name__ == "__main__":
  min_fifo_size = main()