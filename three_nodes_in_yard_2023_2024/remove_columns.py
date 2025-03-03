#!/usr/bin/env python3
import csv
import sys


def remove_unwanted_columns(input_filename, output_filename):
    """
    Processes a CSV file with extra metadata at the beginning.
    It finds the header row starting with "Date and Time in UTC"
    and then writes only the desired columns to the output file.

    The input header is:
      Date and Time in UTC,SampleNumber,Battery,TXDuration,Temperature,Humidity,NodeStatus,MainNodeNotes

    The desired output contains only the columns:
      Date and Time in UTC,SampleNumber,Battery,Temperature,Humidity
    """
    # The indices for the desired columns (0-based):
    # 0: Date and Time in UTC, 1: SampleNumber, 2: Battery, 4: Temperature, 5: Humidity
    desired_indices = [0, 1, 2, 4, 5]

    header_found = False

    with open(input_filename, 'r', newline='') as infile, \
            open(output_filename, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            # Skip empty rows
            if not row or all(cell.strip() == "" for cell in row):
                continue

            # Look for the header row (first cell equals "Date and Time in UTC")
            if not header_found:
                if row[0].strip() == "Date and Time in UTC":
                    header_found = True
                    # Write the new header with only the desired columns.
                    new_header = [row[i] for i in desired_indices]
                    writer.writerow(new_header)
                # Skip rows until header is found.
                continue

            # Process data rows once the header has been found.
            # Write only the desired columns.
            # We assume that all data rows have at least 6 columns.
            new_row = [row[i] for i in desired_indices]
            writer.writerow(new_row)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 remove_columns.py <input_csv_file> <output_csv_file>")
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    remove_unwanted_columns(input_filename, output_filename)
    print(f"Processed '{input_filename}' and saved output to '{output_filename}'.")


if __name__ == "__main__":
    main()
