"""
Process data stored in csv files saved by an oscilloscope.

Probably need to run these data through a low pass filter since the
'calc' function seems to have the time

James Gallagher <jgallagher@opendap.org> 8/15/21

This is old has been replaced by a Jupyter notebook.
"""

import argparse
import numpy as np
from scipy.signal import butter, sosfilt
import plotly.graph_objects as go
import plotly.express as px

# For the 23dBm file, -d 000005 and -o 0.0; for the 13dBm file, -d 0.00001 -o 0.0765
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", help="read every Xth value, ignored for 'filter'", default=1000, type=int)
    parser.add_argument("-z", "--zero", help="Any value < this is zero", default=0.00015, type=float)
    parser.add_argument("-s", "--skip", help="skip the first N lines", default=12, type=int)
    parser.add_argument("-r", "--resistance", help="Resistance used in measurement", default=2.2, type=float)
    parser.add_argument("-d", "--delta_t", help="Sample time period", default=0.000005, type=float)
    parser.add_argument("-o", "--offset", help="Voltage offset", default=0.0, type=float)
    parser.add_argument("-w", "--what", help="Do what: print or filter data", default='print')
    parser.add_argument("-p", "--plot", help="Plot the raw and filtered data", default=False, type=bool)
    parser.add_argument("-R", "--raw", help="Plot raw data too", default=False, type=bool)
    parser.add_argument('data_file', help='Read from this file')
    args = parser.parse_args()

    if args.what == 'print':
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
        voltages = data[..., 1] + args.offset    # * 1000 / args.resistance

        filtered_volts = butter_lowpass_filter(voltages, cutoff, fs, order)

        # Threshold post filtering.
        # y is derived from 'data' which is a numpy array, so this works to set
        # all the values of 'y' less than args.zero to 0.0.
        filtered_volts[filtered_volts < args.zero] = 0.0

        mA = voltages / args.resistance * 1000.0
        filtered_mA = filtered_volts / args.resistance * 1000.0

        fig1 = px.line(x=data[::100, 0],
                       y=filtered_mA[::100],
                       line_shape='linear',
                       title="Leaf Node Current Profile During the Wake State, LoRa Tx at 23dBm")

        fig1.update_xaxes(title_text="time (s)")
        fig1.update_yaxes(title_text="current (mA)")

        fig1.show()

        fig1.write_image("Current_measurement/figures/fig1.png")

        if args.plot:
            fig = go.Figure()
            if args.raw:
                fig.add_trace(go.Scatter(
                    x0=data[0, 0],
                    dx=args.delta_t * 100,  # Scale delta_t but 100 since we sample 'filtered_volts'
                    y=mA[::100],  # print every 100 values
                    line=dict(shape='spline'),
                    name='signal with noise'
                ))
            fig.add_trace(go.Scatter(
                x0=data[0, 0],
                dx=args.delta_t * 100,      # Scale delta_t but 100 since we sample 'filtered_volts'
                y=filtered_mA[::100],
                line=dict(shape='spline'),
                name='filtered signal'
            ))
            fig.update_xaxes(title_text="time (s)")
            fig.update_yaxes(title_text="current (mA)")

            fig.show(title="Leaf node current use during the operating phase")

        calc_values_from_filtered_data(filtered_volts, args.zero, args.delta_t, args.resistance)
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
    @param data is corrected voltage for a time slice
    @param zero_value is the value to call 'zero volts' FIXME Remove
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


if __name__ == "__main__":
    main()
