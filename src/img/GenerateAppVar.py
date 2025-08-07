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
OnCalcName = OnCalcName.upper()

with open(f"./src/img/{sys.argv[1]}", "rb") as file:
	Data = file.read()

if len(Data) > 0xFFFF:
	print("File is too large! Max file size is 64KB")
	quit()
if len(OnCalcName) > 8:
	print("OnCalcName is too large! (Max 8 characters)")
	quit()






OutputFilePath: str = f"./src/img/{OnCalcName}.8xv"

with open(OutputFilePath, "wb") as file:
	# DISCLAIMER: Some bytes are duplicated throughout the the file,
	# this python script is not wrong, it is what it is ¯\_(ツ)_/¯

	# If you don't know what this code does, READ ALL OF IT(including the comments),
	# THEN and ONLY THEN, can you read it again and interpret what is actually is doing...
	# just trust me...
	
	# Because of the b in "wb", it can only write bytes to the file,
	# so strings has to be encoded to a byte string

	# Magic Number + 42 bytes(for a comment padded with 0s but I'm putting no comment)
	file.write(f"**TI83F*\x1A\x0A\x00{"\x00"*42}".encode())

	# Data length + VarEntryData(17) + 2 bytes containing the length of the data
	ByteStr = (len(Data) + 17).to_bytes(2, "little")
	file.write(ByteStr)	

	# Used to calculate the Checksum
	VarData = (
		# Entry Signature
		b'\x0D\x00' +
		# Var Data Length
		len(Data).to_bytes(2, "little") +
		# Tells TI-Connect that It's an AppVar
		b'\x15' +
		# Name of the AppVar on the calculator(8 bytes of ASCII padded with 0s)
		OnCalcName.encode("ascii") + b'\x00'*(8 - len(OnCalcName)) + 
		# Version and Flag
		b'\x00\x00' + 
		# Var Data Length (again)
		len(Data).to_bytes(2, "little") +
		# Your Data 
		Data)
	file.write(VarData)

	
	# Calculate the Checksum for the end of the file
	tempSum: int = 0
	for byte in VarData:
		# byte is an int for some reason, but that makes
		# it easier for me so im not complaining
		tempSum += byte
		tempSum &= 0xFFFF

	Checksum: bytes = tempSum.to_bytes(2, 'little')

	# Checksum to verify that the data wasn't corrupted during the transfer
	file.write(Checksum)


# https://merthsoft.com/linkguide/ti83+/packet.html#varheader

# File Structure:

# | Section             | Offset | Size     | Notes                     |
# | ------------------- | ------ | -------- | ------------------------- |
# | File Signature1     | 0x00   | 8 bytes  | **TI83F*                  |
# | File Signature2     | 0x08   | 3 bytes  | 1A 0A 00                  |
# | Comment             | 0x0B   | 42 bytes | Optional, fill with 0x00  |
# | Data Section Length | 0x35   | 2 bytes  | File size(in bytes) - 57  |
# | Data Section        | 0x37   | n bytes  | Contains 1 or more entries|
# | Checksum            | END    | 2 bytes  | Sum from 0x37 to data end |


# Type IDs
# | Name                                    | ID     |
# | ----------------------------------------| ------ |
# | AppVar                                  | 0x15   |
# | Real Number								| 0x00   |
# | Real List								| 0x01   |
# | Matrix									| 0x02   |
# | Y-Variable								| 0x03   |
# | String									| 0x04   |
# | Program									| 0x05   |
# | Edit-locked Program						| 0x06   |
# | Picture									| 0x07   |
# | GDB										| 0x08   |
# | Window Settings							| 0x0B   |
# | Complex Number							| 0x0C   |
# | Complex List							| 0x0D   |
# | Window Settings							| 0x0F   |
# | Saved Window Settings					| 0x10   |
# | Table Setup								| 0x11   |
# | Backup									| 0x13   |
# | Used to delete a FLASH application		| 0x14   |
# | Application Variable					| 0x15   |
# | Group Variable							| 0x17   |
# | Directory								| 0x19   |
# | FLASH Operating System					| 0x23   |
# | FLASH Application						| 0x24   |
# | ID list									| 0x26   |
# | Get Certificate							| 0x27   |
# | Clock									| 0x29   |





# Entry Structure:
# For the Entry Signature, if you use 0B, there will(apparently) be no Version,
# and no Flag. For simplicity, I will just use 0D.

# | Section             | Offset | Size     | Notes                     |
# | ------------------- | ------ | -------- | ------------------------- |
# | Entry Signature     | 0x00   | 2 bytes  | 0Bh or 0Dh                |
# | Var Data Length     | 0x02   | 2 bytes  | Byte length of var data   |
# | Type ID             | 0x04   | 1 bytes  | See Type ID table above   |
# | Var Name            | 0x05   | 8 bytes  | Pad with NULL on right    |
# | Version             | 0x0D   | 1 bytes  | Can just be 0             |
# | Flag                | 0x0E   | 1 bytes  | 80h=Archived, 0=other     |
# | Var Data Length     | 0x0F   | 2 bytes  | Same as at offset 0x02    |
# | Var Data            | 0x11   | n bytes  | Your Data                 