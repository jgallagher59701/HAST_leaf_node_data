#!/usr/bin/env python3

import csv
import sys
from datetime import datetime

def clean_csv(input_file, output_file):
    """
    Processes a raw CSV file from the 'three nodes in the backyard' test/experiment
    and produces a cleaned CSV file ready for analysis.

    Args:
        input_file (str): Path to the input raw CSV file.
        output_file (str): Path to save the cleaned CSV file.
    """
    
    # Lines to elide
    lines_to_elide = ["# Start Log", "Node, Message, Time, Battery V, Last TX Dur ms, Temp C, Hum %, Status"]

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write header for the cleaned file
        writer.writerow(["Node", "Message", "Time UTC", "Battery V", "Last TX Dur ms", "Temp C", "Hum %", "Status", "Notes"])

        for line in reader:
            # Skip lines that need to be elided
            if any(elide_line in line for elide_line in lines_to_elide):
                continue

            # Skip lines that start with 'time request'
            if line and line[0].startswith("time request"):
                continue

            # Process valid data lines
            if len(line) == 8:
                try:
                    node = int(line[0])
                    message = int(line[1])
                    timestamp = datetime.fromtimestamp(int(line[2])).isoformat()
                    battery_v = int(line[3]) / 100.0
                    last_tx_dur_ms = int(line[4]) / 100.0
                    temp_c = int(line[5]) / 100.0
                    hum_percent = round(int(line[6]) / 100)  # Convert to integer percent
                    status = int(line[7], 16)  # Convert hex string to integer

                    # Decode status as bitmask
                    status_notes = []
                    if status & 0x01:
                        status_notes.append("RFM95_SEND_ERROR")
                    if status & 0x02:
                        status_notes.append("RFM95_NO_REPLY")
                    if status & 0x04:
                        status_notes.append("SD_FILE_ENTRY_WRITE_ERROR")
                    if status & 0x08:
                        status_notes.append("SD_CARD_WAKEUP_ERROR")
                    if status & 0x10:
                        status_notes.append("SD_NO_MORE_NAMES")
                    if status & 0x20:
                        status_notes.append("SD_CARD_INIT_ERROR")
                    if status & 0x40:
                        status_notes.append("RFM95_INIT_ERROR")
                    if status & 0x80:
                        status_notes.append("SHT_31_INIT_ERROR")

                    notes = ", ".join(status_notes)
                    writer.writerow([node, message, timestamp, battery_v, last_tx_dur_ms, temp_c, hum_percent, hex(status), notes])
                except ValueError as e:
                    # Skip malformed lines
                    print(f"Skipping malformed line: {line}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./clean_csv.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    clean_csv(input_file, output_file)
