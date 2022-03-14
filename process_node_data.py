"""
Process data stored in the SD cards and logs from the main node from the leaf nodes.

James Gallagher <jgallagher@opendap.org> 4/24/21

7/25/21 Hacked the code for the 'main node' CSV data files to match the newer format.
The sample interval option is no longer useful except for old data files since the
leaf node now longer samples multiple times per minute. By default (--sample-interval=0)
prints every line of data in the CSV file.

Added RSSI output.
"""

import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Read CSV data from the leaf node (SD card or as saved by the main node)")
    parser.add_argument("-f", "--file", help="data file to process", default='node_2_backyard_03.2021.csv')
    parser.add_argument("-i", "--interval", help="sample interval (0-60 minutes) - use with multiple samples/min", type=int, default=0)
    parser.add_argument("-H", "--hourly", help="print one row per hour", type=bool, default=True)
    parser.add_argument("-s", "--source", help="data source: sd or main", choices=['sd', 'main'], default='main')
    args = parser.parse_args()

    if args.source == 'main':
        print_values_from_main(args.file, args.interval)
    elif args.hourly:
        print_values_from_sd_hourly(args.file)
    else:
        print_values_from_sd(args.file, args.interval)


def print_values_from_main(data_file, sample_interval):
    """
    Print values received by a 'main' node and written to a log file.
    :param data_file: Read raw data from this file
    :param sample_interval: Sample the data to yield values at this interval; 0 == print every data row
    :return: Nothing; writes to stdout
    """

    print("Node, Msg #, Msg time, Msg Time (Unix), Tx time (ms), Bat V, Temp C, Rel H %, Node Status, RSSI")
    value_written = False
    with open(data_file, "r") as in_file:
        while True:
            line = in_file.readline()
            if not line:
                break  # This is the loop exit

            # There are 9 fields per csv row
            #
            # "Hello", node, message num, message time, tx time, bat v, temp, hum, status
            # Sample row:
            # ['Hello', 'node 2', 'message 270209', 'msg time 1604995280', 'tx time 403 ms',
            # 'battery 331 v', 'temp 110 C', 'humidity 9913 %', 'status 0x00']
            #
            # parse the line by spaces to access the numeric data more easily. This will
            # yield 22 fields.
            #
            # The new main has X fields when parsed:
            # process_node_data.py:60

            fields = line.strip().replace(',', '').split()

            if len(fields) < 31:
                continue  # if this row is not a data row, ignore it

            node = fields[2]
            msg_num = fields[4]
            # Extract the Unix time value and convert to human-readable
            msg_ux_time = fields[6]  # Unix time
            # if you encounter a "year is out of range" error, the timestamp
            # may be in milliseconds, try `ts /= 1000` in that case
            msg_time = datetime.utcfromtimestamp(int(msg_ux_time)).strftime('%Y-%m-%d %H:%M:%S')

            # Old: only print data on sample_interval minute intervals. Since there are ~3 samples per min,
            # only print the first one for each of the 5 minute intervals.
            # New: The leaf node now samples once every 5 minutes. Use sample_interval == 0
            # to print every line. jhrg 7/25/21
            msg_minute = datetime.utcfromtimestamp(int(msg_ux_time)).strftime('%M')
            if sample_interval == 0 or int(msg_minute) % sample_interval == 0:
                if sample_interval == 0 or not value_written:
                    tx_time = fields[12]  # ms
                    bat = int(fields[8]) / 100  # volts
                    temp = int(fields[15]) / 100  # deg C
                    hum = int(fields[18]) / 100  # % rel hum
                    status = fields[21]  # status in hex
                    rssi = fields[23] # RSSI in dBm (?)
                    print(f"{node},{msg_num},{msg_time},{msg_ux_time},{tx_time},{bat},{temp},{hum},{status},{rssi}")
                    value_written = True
                else:
                    continue
            else:
                value_written = False
                continue


def print_values_from_sd_hourly(data_file):
    """
    Print values from the leaf node's SD card.

    TODO Hack this for files where there are several samples per hour but
    gaps of several minutes between the samples.

    :param data_file:
    :param sample_interval:
    :return: Writes to stdout
    """

    print("Node, Msg #, Msg time, Msg Time (Unix), Tx time (ms), Bat V, Temp C, Rel H %, Node Status")
    hour_last_written = -1      # print the very first row
    with open(data_file, "r") as in_file:
        while True:
            line = in_file.readline()
            if not line:
                break  # This is the loop exit

            # There are 8 fields per csv row
            #
            # Sample row: 2, 1, 1612714606, 425, 0, 1904, 3480, 0x00
            # node, message num, message time, bat v, tx time, temp, hum, status
            fields = line.strip().replace(',', '').split()

            if len(fields) < 8:
                continue  # if this row is not a data row, ignore it

            (node, msg_num, msg_ux_time, bat, tx_time, temp, hum, status) = fields

            # if you encounter a "year is out of range" error, the timestamp
            # may be in milliseconds, try `ts /= 1000` in that case
            msg_ux_time = int(msg_ux_time)
            msg_time = datetime.utcfromtimestamp(msg_ux_time).strftime('%Y-%m-%d %H:%M:%S')

            # only print data on sample_interval minute intervals. Since there are ~3 samples per min,
            # only print the first one for each of the sample_interval minute intervals.
            msg_hour = datetime.utcfromtimestamp(msg_ux_time).strftime('%H')
            if int(msg_hour) != hour_last_written:
                hour_last_written = int(msg_hour)
                bat = int(bat) / 100  # volts
                temp = int(temp) / 100  # deg C
                hum = int(hum) / 100  # % rel hum

                print(f"{node},{msg_num},{msg_time},{msg_ux_time},{tx_time},{bat},{temp},{hum},{status}")


def print_values_from_sd(data_file, sample_interval):
    """
    Print values from the leaf node's SD card.

    This version of print_values... is for files where there are several samples
    per minute.

    :param data_file:
    :param sample_interval:
    :return: Writes to stdout
    """

    print("Node, Msg #, Msg time, Msg Time (Unix), Tx time (ms), Bat V, Temp C, Rel H %, Node Status")
    value_written = False
    with open(data_file, "r") as in_file:
        while True:
            line = in_file.readline()
            if not line:
                break  # This is the loop exit

            # There are 8 fields per csv row
            #
            # Sample row: 2, 1, 1612714606, 425, 0, 1904, 3480, 0x00
            # node, message num, message time, bat v, tx time, temp, hum, status
            fields = line.strip().replace(',', '').split()

            if len(fields) < 8:
                continue  # if this row is not a data row, ignore it

            (node, msg_num, msg_ux_time, bat, tx_time, temp, hum, status) = fields

            # if you encounter a "year is out of range" error, the timestamp
            # may be in milliseconds, try `ts /= 1000` in that case
            msg_ux_time = int(msg_ux_time)
            msg_time = datetime.utcfromtimestamp(msg_ux_time).strftime('%Y-%m-%d %H:%M:%S')

            # only print data on sample_interval minute intervals. Since there are ~3 samples per min,
            # only print the first one for each of the sample_interval minute intervals.
            msg_minute = datetime.utcfromtimestamp(msg_ux_time).strftime('%M')
            if int(msg_minute) % sample_interval == 0:
                if not value_written:
                    bat = int(bat) / 100  # volts
                    temp = int(temp) / 100  # deg C
                    hum = int(hum) / 100  # % rel hum

                    print(f"{node},{msg_num},{msg_time},{msg_ux_time},{tx_time},{bat},{temp},{hum},{status}")
                    value_written = True
                else:
                    continue
            else:
                value_written = False
                continue


if __name__ == "__main__":
    main()
