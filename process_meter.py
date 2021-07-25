
"""
Process data from the METER logger

James Gallagher <jgallagher@opendap.org> 4/24/21
"""


import argparse
from datetime import datetime, timedelta


def main():
    """
    Hack the data collected by the Meter data logger.

    We failed to correctly set the time on the logger, so this code reads the time stamp and
    adds an offset, based on our notes and recollection of the time of day we deployed and
    collected the logger. The processing also modified the header lines, so both the original
    and corrected times are in the output. Lastly, the code can sample the data so that only
    hourly measurements are output, making plotting using Google, Excel, etc., sane.

    :return: Lines of CSV data
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="data file to process", default='EM40647_Data.csv')
    parser.add_argument("-i", "--interval", help="sample interval (0-60 seconds)", type=int, default=60)
    parser.add_argument("-o", "--offset", help="time offset in seconds", type=int, default=354049200)
    args = parser.parse_args()

    process_values(args.file, args.offset, args.interval)


def process_values(data_file, offset, sample_interval):
    """
    Process the METER data.

    The first three lines are header information and should be echoed to the output. The rest of
    the lines are csv data lines. The lines look like:
    8/31/2009 11:40 PM,0.136,3.4,0.00,0.097,5.2,0.01,0.137,2.6,0.01,0.091,6.9,0.00,0.036,5.3,0.00
    where, after the date there are 15 values, five groups of three measurements of
    m³/m³ VWC, °C Temp, mS/cm EC Bulk

    The timestamps are off on some of the data, so there are two timestamps in the output. The
    first is the original and the seconds is the result of applying the offset to that time.
    """

    line_num = 0
    with open(data_file, "r") as in_file:
        while True:
            line = in_file.readline()
            line_num += 1
            if not line:
                break  # This is the loop exit

            if line_num == 1 or line_num == 2:
                print('blank', line, end='', sep=',')
                continue
            elif line_num == 3:
                print('Original Time', line, end='', sep=',')
                continue

            fields = line.strip().split(",")

            msg_time = fields[0]  # parsed time
            time = msg_time.replace('/', ' ').replace(':', ' ').split()
            if len(time) != 6:
                print(f"Failed to parse date for line {line_num}")

            hours = int(time[3])
            minutes = int(time[4])
            if minutes % sample_interval == 0:
                if time[5] == "PM":             # 12 PM == 12, 1 PM == 13
                    if hours < 12:
                        hours = (hours + 12) % 24
                else:
                    hours = hours % 12          # 1 AM == 1, 2 AM == 2, ... 12 AM == 0

                time_obj = datetime(int(time[2]), int(time[0]), int(time[1]), hours, minutes)
                time_offset = timedelta(seconds=offset)
                new_time = time_obj + time_offset
                # print(f"Old time: {msg_time}, new time: {new_time}")
                print(fields[0], new_time, sep=',', end=',')        # ,{fields[1:]}")
                print(*fields[1:], sep=",")


if __name__ == "__main__":
    main()
