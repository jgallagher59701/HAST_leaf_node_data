#!/usr/bin/env python3
import csv
import sys


def split_csv_by_node(input_filename):
    # Define the node values to split on and the corresponding output filenames.
    node_files = {
        '3': 'node3.csv',
        '5': 'node5.csv',
        '10': 'node10.csv'
    }

    # Open output files and create CSV writers.
    writers = {}
    output_fhs = {}
    for node, out_filename in node_files.items():
        fh = open(out_filename, 'w', newline='')
        output_fhs[node] = fh
        writers[node] = csv.writer(fh)

    try:
        with open(input_filename, 'r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Read the header row.

            # Write the header to each output file.
            for writer in writers.values():
                writer.writerow(header)

            # Process each row in the input file.
            for row in reader:
                if not row:  # Skip empty rows.
                    continue
                node = row[0].strip()  # The node value is assumed to be in the first column.
                if node in writers:
                    writers[node].writerow(row)
    finally:
        # Always close all output files.
        for fh in output_fhs.values():
            fh.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 split_csv.py <input_csv_file>")
        sys.exit(1)
    input_filename = sys.argv[1]
    split_csv_by_node(input_filename)
    print("CSV file has been split into node3.csv, node5.csv, and node10.csv.")


if __name__ == "__main__":
    main()
