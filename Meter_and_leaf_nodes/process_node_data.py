
import argparse
from datetime import datetime


def main():
    data_file = "node_2_backyard_03.2021.csv"
    sample_interval = 60  # in minutes; 60 == hourly samples

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file to process")
    parser.add_argument("-i", "--interval", help="sample interval (0-60 seconds)", type=int)
    args = parser.parse_args()

    if args.interval:
        sample_interval = args.interval
    if args.file:
        data_file = args.file

    print_values(data_file, sample_interval)


def print_values(data_file, sample_interval):
    print("Node, Msg #, Msg time, Msg Time (Unix), Tx time (ms), Bat V, Temp C, Rel H %, Node Status")
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
            fields = line.strip().replace(',', '').split()

            if len(fields) < 22:
                continue  # if this row is not a data row, ignore it

            node = fields[2]
            msg_num = fields[4]
            # Extract the Unix time value and convert to human-readable
            msg_ux_time = fields[7]  # Unix time
            # if you encounter a "year is out of range" error, the timestamp
            # may be in milliseconds, try `ts /= 1000` in that case
            msg_time = datetime.utcfromtimestamp(int(msg_ux_time)).strftime('%Y-%m-%d %H:%M:%S')

            # only print data on sample_interval minute intervals. Since there are ~3 samples per min,
            # only print the first one for each of the 5 minute intervals.
            msg_minute = datetime.utcfromtimestamp(int(msg_ux_time)).strftime('%M')
            if int(msg_minute) % sample_interval == 0:
                if not value_written:
                    tx_time = fields[10]  # ms
                    bat = int(fields[13]) / 100  # volts
                    temp = int(fields[16]) / 100  # deg C
                    hum = int(fields[19]) / 100  # % rel hum
                    status = fields[22]  # status in hex

                    print(f"{node},{msg_num},{msg_time},{msg_ux_time},{tx_time},{bat},{temp},{hum},{status}")
                    value_written = True
                else:
                    continue
            else:
                value_written = False
                continue


if __name__ == "__main__":
    main()
