
# What's here

This directory contains CSV data recorded by the 'main node' (i.e.,
the receiving node) from HAST nodes 3, 5, and 10 using LORA.

Sensor/node 3 data starts on Sat Oct 28 2023 18:02:35 GMT+0000 (UNIX time 1698516155)
Sensor/node 5 data starts on Sat Oct 28 2023 17:29:17 GMT+0000 (UNIX time 1698514157)
Sensor/node 10 data starts on Sat Oct 28 2023 17:36:27 GMT+0000 (UNIX Time 1698514587)

Nodes 3 and 5 are in trees.
Node 10 is buried 1cm deep in dirt

## What data have been uploaded to Monitor My Watershed (MMW)?

In 'data\_2025', the data in
'Sensor\_data\_three\_nodes_\processed.csv' are the starting point for
getting this information to MMW.

## The actual data files are in sub directories

### The sub-directory 'data\_2024'

The sub-directory 'data\_2024' holds the raw data file from the 'main'
From Sun Oct 01 2023 17:32:40 GMT+0000 to Sat Jan 27 2024 11:02:35
GMT+0000. The file 'Sensor\_data.cs'v is the raw data file from the main
node. File Sensor\_data\_three\_sensors.numbers (for the Mac spreadsheet program
'numbers') has those same data processed a bit to start from Sat Oct
14 2023 11:39:00 GMT+0000 to Sat Jan 27 2024 11:02:35 GMT+0000.

### The sub-directory 'data\_2025'

The sub-directory 'data\_2025' has 'Sensor\_data.csv' (the raw data file
from the main node) from Sun Oct 01 2023 17:32:40 GMT+0000 to Mon Jan
20 2025 18:02:35 GMT+0000. Also in this directory are
'whole\_file\_processed.csv' which is the whole Sensor\_data.csv file
processed using a python script (clean_csv.py) so that values are not sensor counts
but floating point numbers, lines of data are uniform and not
intersperced with 'notes' left by the main node to simplify
troubleshooting, et cetera. Here's an example of the cleaning:

The raw data:
```
# Start Log
# Node, Message, Time, Battery V, Last TX Dur ms, Temp C, Hum %, Status
10, 1, 1696181572, 447, 0, 2358, 3225, 0x20
# Start Log
# Node, Message, Time, Battery V, Last TX Dur ms, Temp C, Hum %, Status
10, 1, 1696181560, 447, 0, 2449, 3086, 0x00
10, 2, 1696852606, 416, 386, 2541, 2917, 0x02
```

The 'clean' data:
```
Node,Message,Time UTC,Battery V,Last TX Dur ms,Temp C,Hum %,Status,Notes
10,1,2023-10-01T11:32:52,4.47,0.0,23.58,32,0x20,SD_CARD_INIT_ERROR
10,1,2023-10-01T11:32:40,4.47,0.0,24.49,31,0x0,
10,2,2023-10-09T05:56:46,4.16,3.86,25.41,29,0x2,RFM95_NO_REPLY
```

Most importantly, also in 'data\_2025' are
'Sensor\_data\_3\_nodes\_only.csv' and
'Sensor\_data\_three\_nodes_\processed.csv' The raw and processed
(clean) data for covering the period of time when all three sensors
were (they are still) running and sampling at one hour intervals. 

## The raw data files contents and how to decode them

The raw data file contains many lines from just sensor #10 sampling at
a 30s interval. When the other two nodes were added (Sat Oct 28 2023
17:02:35 GMT+0000) the frequency drops to once an hour.

The CSV data file holds the following information:

Node, Message, Time, Battery V, Last TX Dur ms, Temp C, Hum %, Status

Node, integer,  always 3, 5, or 10
Message, integer, 1, 2, ... N
Time, integer, UNIX time - seconds since 1.1.1970
Batter V, integer that is 100 time the voltage, divide by 100 to get a float value
Last TX Duration, ms, integer that is 100 times the value, divide ...
Temperature in Degrees C, integer times 100, divide ...
Hum %, 
Status, hex status code, 0x00 - no errors, 0x02 - handshake error



  
