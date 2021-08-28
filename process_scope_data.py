"""
Process data stored in csv files saved by an oscilloscope.

Probably need to run these data through a low pass filter since the
'calc' function seems to have the time

James Gallagher <jgallagher@opendap.org> 8/15/21
"""

import argparse
from datetime import datetime
import numpy as np
from scipy.signal import butter, filtfilt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", help="read every Xth value", default=1000, type=int)
    parser.add_argument("-z", "--zero", help="Any value < this is zero", default=0.03, type=float)
    parser.add_argument("-s", "--skip", help="skip the first N lines", default=12, type=int)
    parser.add_argument("-r", "--resistance", help="Resistance used in measurement", default=2.2, type=float)
    parser.add_argument("-d", "--delta_t", help="Delta time for samples", default=0.000005, type=float)
    parser.add_argument("-w", "--what", help="Do what: Calc mAs; Print data", default='calc')
    parser.add_argument('data_file', help='Read from this file')
    args = parser.parse_args()

    if args.what == 'calc':
        calc_values_from_siglent_csv(args.data_file, args.zero, args.skip, args.resistance, args.delta_t)
    elif args.what == 'print':
        print_values_from_siglent_csv(args.data_file, args.zero, args.skip, args.interval)
    elif args.what == 'filter':
        # Filter requirements.
        T = 7.0  # Sample Period, seconds
        fs = 200.0  # sample rate, Hz
        cutoff = 10  # desired cutoff frequency of the filter, Hz
        nyq = 0.5 * fs  # Nyquist Frequency
        order = 2
        n = int(T * fs)  # total number of samples

        y = butter_lowpass_filter(data, cutoff, fs, order)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=data,
            line=dict(shape='spline'),
            name='signal with noise'
        ))
        fig.add_trace(go.Scatter(
            y=y,
            line=dict(shape='spline'),
            name='filtered signal'
        ))
        fig.show()
    else:
        parser.usage()


# WIP
def butter_lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y


def print_values_from_siglent_csv(data_file, zero_value, skip, sample_interval):
    print("Second, Volt")
    with open(data_file, "r") as in_file:
        i = 0
        line = in_file.readline()
        while line and (i < skip):
            line = in_file.readline()
            i += 1
        while line:
            if i % sample_interval == 0:
                fields = line.strip().replace(',', ' ').split()
                (time, volts) = fields
                if float(volts) <= zero_value:
                    volts = 0
                print(f"{time},{volts}", end='\n')
            line = in_file.readline()
            i += 1


def calc_values_from_siglent_csv(data_file, zero_value, skip, resistance, delta_t):
    with open(data_file, "r") as in_file:
        i = 0
        amp_samples = 0.0
        total_time = 0.0
        start_time = 0.0
        end_time = 0.0

        line = in_file.readline()
        while line and (i < skip):
            line = in_file.readline()
            i += 1

        while line:
            fields = line.strip().replace(',', ' ').split()
            (time, volts) = fields
            volts = float(volts)
            if volts > zero_value:
                if start_time == 0.0:
                    start_time = time
                end_time = time
                total_time += 1     # count the samples, divide once outside of loop
                amp_samples += (volts / resistance)     # As above, factor out '* delta_t'

            line = in_file.readline()
            i += 1

        # Complete calculations and print the results
        mAs = amp_samples * delta_t * 1000
        total_time = total_time * delta_t
        print(f"Start time: {start_time}, End time: {end_time}, Total time: {total_time}, mAs: {mAs}\n")

if __name__ == "__main__":
    main()
