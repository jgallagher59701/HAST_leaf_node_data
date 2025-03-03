#!/usr/bin/env python3
import csv
import sys

def reformat_csv(input_filename, output_filename):
    """
    Reads the input CSV file, reformat each row by:
      - Dropping the first element (Node)
      - Moving the time field (originally the third column) to the beginning
      - Replacing the 'T' in the time field with a space
    Writes the reformatted rows to the output CSV file.
    """
    with open(input_filename, 'r', newline='') as infile, \
         open(output_filename, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read and reformat the header.
        header = next(reader)
        # Expected header: [Node, Message, Time UTC, Battery V, Last TX Dur ms, Temp C, Hum %, Status, Notes]
        # We want the new order: [Time, Message, Battery V, Last TX Dur ms, Temp C, Hum %, Status, Notes]
        # Optionally, rename the time header if desired.
        new_header = ["Time"] + [header[1]] + header[3:]
        writer.writerow(new_header)

        # Process each data row.
        for row in reader:
            if not row:
                continue
            # Extract and modify the time field (column index 2).
            time_field = row[2].replace('T', ' ')
            # Reorder: time, then Message (col index 1), Battery V (col index 3), Last TX Dur ms (col index 4),
            # Temp C (col index 5), Hum % (col index 6), Status (col index 7), and Notes (col index 8).
            new_row = [time_field, row[1], row[3], row[4], row[5], row[6], row[7], row[8]]
            writer.writerow(new_row)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 reformat_csv.py <input_csv_file> <output_csv_file>")
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    reformat_csv(input_filename, output_filename)
    print(f"File '{input_filename}' has been reformatted and saved as '{output_filename}'.")

if __name__ == "__main__":
    main()
