#####################
#	   Made by		#
#	  MadMax0rs		#
#####################

# File/Header structure can be found at the bottom of the file
# (for those who'd like to know)

import sys
import numpy as np
from pathlib import Path


if len(sys.argv) < 3 or sys.argv[1] in ("-h", "-?"):
	print(
	"""
	This generator was written for the TI-84 Plus CE Python.
	It is not garunteed to work for any other device

	Syntax:
	GenerateAppVar.py <FilePath> <OnCalcName>   
	""")
	quit()

FilePath = sys.argv[1]
# Name of the AppVar of the calculator
OnCalcName = sys.argv[2]

with open(sys.argv[1]) as file:
	Data = file.read()

if len(Data) > 0xFFFF:
	print("File is too large! Max file size is 64KB")
	quit()

# The whole point of the checksum is that it should overflow,
# so temporarily disable the warning
np.seterr(over='ignore')

# Calculate the Checksum for the end of the file
tempSum: np.uint16 = np.uint16(0)
for byte in [np.uint16(ord(c)) for c in Data]:
	tempSum += byte

# If something else overflows, it's an error, so tell it to warn again
np.seterr(over='warn')

# Idk if the numpy uint16.tobytes() function works
# how I want it and im too lazy to test
Checksum: bytes = int(tempSum).to_bytes(2, 'little')




OutputFilePath: str = f"{Path(FilePath).parent}\\{OnCalcName}.8xv"

with open(OutputFilePath, "wb") as file:
	# DISCLAIMER: Some bytes are duplicated throughout the the file,
	# this python script is not wrong, it is what it is ¯\_(ツ)_/¯

	# If you don't know what this code does, READ ALL OF IT(including the comments),
	# THEN and ONLY THEN, can you read it again and interpret what is actually is doing...
	# just trust me...
	
	# Because of the b in "wb", it can only write bytes to the file,
	# so strings has to be encoded to a byte string

	# Magic Number + 42 bytes(for a comment padded with 0s but I'm putting no comment)
	file.write(f"**TI83F*{"\x00"*42}".encode())

	# Data length + VarEntryData(17) + 2 bytes containing the length of the data
	ByteStr = (len(Data) + 17 + 2).to_bytes(2, "little")
	file.write(ByteStr)
	file.write(ByteStr)

	# Tells TI-Connect that It's an AppVar
	file.write(b'\0x15')

	# Name of the AppVar on the calculator(ASCII padded with 0s)
	file.write(OnCalcName.encode("ascii"))

	# Data length + 2 bytes containing the length of the data
	ByteStr = (len(Data) + 2).to_bytes(2, "little")
	file.write(ByteStr)

	# Legnth of the actual data
	ByteStr = (len(Data)).to_bytes(2, "little")
	file.write(ByteStr)

	# 2 bytes containing the length of the data (referenced a couple
	# times earlier in the code, now yk what im talking about)
	ByteStr = (len(Data)).to_bytes(2, "little")
	file.write(ByteStr)

	# Your data
	file.write(Data.encode())

	# Checksum to verify that the data wasn't corrupted during the transfer
	file.write(Checksum)



# File Structure:

# | Section             | Offset | Size     | Notes                     |
# | ------------------- | ------ | -------- | ------------------------- |
# | File Magic          | 0x00   | 8 bytes  | **TI83F*                  |
# | Comment             | 0x08   | 42 bytes | Optional, fill with 0x00  |
# | Entry Length        | 0x32   | 2 bytes  | 17 + (data length + 2)    |
# | Entry Length (copy) | 0x34   | 2 bytes  | Same as above             |
# | Var Type            | 0x36   | 1 byte   | 0x15 for AppVar           |
# | Var Name            | 0x37   | 8 bytes  | ASCII, padded with 0x00   |
# | Data Size + 2       | 0x3F   | 2 bytes  | length + 2                |
# | Data Size           | 0x41   | 2 bytes  | length                    |
# | Prefix              | 0x43   | 2 bytes  | Little-endian length      |
# | Data                | 0x45   | N bytes  | Your actual data          |
# | Checksum            | END    | 2 bytes  | Sum from 0x37 to data end |
