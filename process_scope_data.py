"""
Process data stored in csv files saved by an oscilloscope.

Probably need to run these data through a low pass filter since the
'calc' function seems to have the time

James Gallagher <jgallagher@opendap.org> 8/15/21
"""

import argparse
from datetime import datetime
import numpy as np
from scipy.signal import butter, filtfilt, sosfilt
import plotly.graph_objects as go


# For the 23dBm file, -d 000005 and -o 0.0; for the 13dBm file, -d 0.00001 -o 0.0765
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", help="read every Xth value, ignored for 'filter'", default=1000, type=int)
    parser.add_argument("-z", "--zero", help="Any value < this is zero", default=0.0, type=float)
    parser.add_argument("-s", "--skip", help="skip the first N lines", default=12, type=int)
    parser.add_argument("-r", "--resistance", help="Resistance used in measurement", default=2.2, type=float)
    parser.add_argument("-d", "--delta_t", help="Delta time for samples", default=0.000005, type=float)
    parser.add_argument("-o", "--offset", help="Vertical offset", default=0.0, type=float)
    parser.add_argument("-w", "--what", help="Do what: calc mAs; print data, filter data", default='calc')
    parser.add_argument("-p", "--plot", help="Plot the raw and filtered data", default=False, type=bool)
    parser.add_argument('data_file', help='Read from this file')
    args = parser.parse_args()

    if args.what == 'calc':
        calc_values_from_siglent_csv(args.data_file, args.zero, args.skip, args.resistance, args.delta_t)
    elif args.what == 'print':
        print_values_from_siglent_csv(args.data_file, args.zero, args.skip, args.interval)
    elif args.what == 'filter':
        # Filter requirements.
        # T = 14.0  # Sample Period, seconds
        fs = 100000.0  # sample rate, Hz
        cutoff = 1000.0  # desired cutoff frequency of the filter, Hz
        # nyq = 0.5 * fs  # Nyquist Frequency
        order = 4
        # n = int(T * fs)  # total number of samples

        # data_file could be '/Users/jimg/src/opendap/HAST_leaf_node_data/Current_measurement/LN_Current_13dBm_23dBm/13dBm_current.csv'

        data = np.genfromtxt(args.data_file, delimiter=',', skip_header=args.skip)

        # slice so we have only the voltage values. 'data_file' holds both the sample time
        # and the voltage as CSV data.
        data = data[...,1] + args.offset    # * 1000 / args.resistance

        y = butter_lowpass_filter(data, cutoff, fs, order)

        if (args.plot):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=data[::100],
                line=dict(shape='spline'),
                name='signal with noise'
            ))
            fig.add_trace(go.Scatter(
                y=y[::100],
                line=dict(shape='spline'),
                name='filtered signal'
            ))
            fig.show()

        # data[...,0] slices just the time info
        calc_values_from_filtered_data(y, args.zero, args.delta_t, args.resistance)
    else:
        args.usage()


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs  # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients - second order sections
    sos = butter(order, normal_cutoff, btype='low', analog=False, output='sos')
    y = sosfilt(sos, data)
    return y


def print_values_from_siglent_csv(data_file, zero_value, skip, sample_interval):
    print("Seconds, Volts")
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


def calc_values_from_filtered_data(data, zero_value, delta_t, resistance):
    """
    @param data is corrected mV for a time slice
    @param zero_value is the value to call 'zero mA'
    @param delta_t is the duration of each sample
    @param resistance Used to convert mV to mA
    """
    volts_samples = 0.0
    samples = 0
    start_time = 0.0
    end_time = 0.0
    sample = 0

    for volts in data:
        if volts > zero_value:
            if start_time == 0.0:
                start_time = sample * delta_t
            end_time = sample
            samples += 1         # count the samples, divide once outside of loop
            volts_samples += volts     # As above, factor out '* delta_t'
        sample += 1

    # Complete calculations and print the results
    end_time *= delta_t
    total_time = samples * delta_t
    # volts_samples / samples: average voltage/sample; * delta_t is avg voltage/second
    # delta_t is seconds/sample --> avg voltage / sample * delta_t is voltage/second
    # voltage/second / resistance is  Amps/ econd; * 1000 --> mA/s
    # mA/s * total_time is mAs
    mAs = (volts_samples / samples) / resistance * 1000

    print(f"Start time: {start_time}, End time: {end_time}, Total time: {total_time}, mAs: {mAs}\n")


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
