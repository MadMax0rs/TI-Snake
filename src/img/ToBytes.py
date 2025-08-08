#####################
#	   Made by		#
#	  MadMax0rs		#
#####################

# Takes in the Tileset Image and converts it into useable data
# that can be written to the TI-84 Plus CE Python screen

import sys
from PIL import Image
import numpy as np

DB = False
FILL = True

# Tile atlas/tilemap image is 4x4 tiles, 16 tiles total
ATLAS_SIZE = 4
# Each tile is 16x16
TILE_SIZE = 16

# Converts from the traditional RGB888 color codes where R, G, and B are
# each 8-bits to RGB565 where R is 5-bit, G as 6-bit, and B as 5-bit, then shifts
# them to fit into one uint16 and splits it into 2 uint8s.
# This is how the calculator screen buffer is formatted in memory.
#  
# DISCLAIMER: Yes, this is somewhat lossy, but I have no other choice,
# the screen simply can't display anything better, plus, wait till you play the game,
# it doesnt actualy make very much difference
def RGB888To565(col888) -> list[np.uint8]:

	# Convert from RRGB888 to RGB565
	R: int = round((float(col888[0]) / 0b11111111) * 0b11111)
	G: int = round((float(col888[1]) / 0b11111111) * 0b111111)
	B: int = round((float(col888[2]) / 0b11111111) * 0b11111)

	# Shift into uint16 
	num: np.uint16 = np.uint16( (R << 11) | (G << 5) | B)

	# Split into 2 uint8s (number's low-order 8-bits are truncated,
	# so the 2nd uint8 needs to be right-shifted by 8-bits)
	num0: np.uint8 = np.uint8(num)
	num1: np.uint8 = np.uint8(num >> 8)

	return [num0, num1]


LastInstruction: bool = FILL
# Picks whether to use .db or .fill to make the data as small as possible
def PickInstruction(currentByte: np.uint8, numBytes: int, currentStr: str) -> str:
	global LastInstruction
	if numBytes < 2:
		# Allows for multiple different bytes to be condensed into 1 instruction
		# ex. ".db 0\n.db 1\n.db 2\n.db 3\n" -> ".db 0, 1, 2, 3\n"
		currentStr += f", {currentByte}" if LastInstruction == DB else f"\n\t.db {currentByte}"
		LastInstruction = DB
	else:
		# Allows for multiple of the same bytes to be condensed into 1 instruction 
		# ex. ".db 0, 0, 0, 0, 0, 0, 0, 0" -> ".fill 8, 0"
		currentStr += f"\n\t.fill {numBytes}, {currentByte}\n"
		LastInstruction = FILL
	
	return currentStr

# Store 
OutStrs: str = ""
AppVarStr: str = ""

Atlas = Image.open("D:\\TI-84PlusCE\\Games\\MyGames\\ASM\\Snake\\src\\img\\tileset.png")

# Put the RGBA data into a 3-dimensional array.
# ex. pixelData[pixelX, pixelY, ColorChannel]
PixelData = np.asarray(Atlas)


# Enumerate through every tile (use the atlas and tile sizes so we dont enumerate every pixel)
for x in range(0, TILE_SIZE * ATLAS_SIZE, TILE_SIZE):
	for y in range(0, TILE_SIZE * ATLAS_SIZE, TILE_SIZE):
		# Get the pixel data for the current tile's R, G, and B, but not A,
		# and reshape it so it has all the pixels on the 1st axis,
		# and the individual RGB values on the 2nd axis 
		data = PixelData[x:x + TILE_SIZE, y:y + TILE_SIZE,0:3].reshape(-1, 3)

		# Variable to hold the 2 bytes of RGB565 values for each pixel,
		# flattened into 1 dimension.
		# This means that this array will be double the size of the current tile
		flatData: list[np.uint8] = []

		# Add 2 RGB565 bytes to flatData for each pixel of the current tile
		for i in range(data.shape[0]):
			obj: list[np.uint8] = RGB888To565(data[i])
			flatData.append(obj[0])
			flatData.append(obj[1])

		# Add a label for the current tile to allow for easy memory access in asm.
		# To get the tile number, I can either divide here only, or multiply for
		# every use of x and y... I went with the former.
		# Ex. If x and y represented the x and y location of the tile int the atlas
		# instead of the pixel coordinates, this would be "int(x*ATLAS_SIZE + y)"
		# This effectively flattens the 2 coordinates into 1
		OutStrs += f"\nTile{int(x*ATLAS_SIZE/TILE_SIZE + y/TILE_SIZE)}:"

		# Holds the previous byte to allow for compacting the asm instructions 
		# Default the current byte to the first byte in the tile data,
		# I don't want to explain, just think about it after reading the rest of the code
		currentByte: np.uint8 = flatData[0]

		# Holds the number of times the currentByte has been seen consecutively
		numBytes: int = 0

		# Loop over each byte in flatData and add it to the both outputs
		# in each of their corrisponding formats
		for i in range(len(flatData)):
			# The AppVar just wants the raw bytes
			AppVarStr += chr(int(flatData[i]))

			# The asm code needs instructions like .db and .fill.
			# With .db you can specify 1 or more bytes individually,
			# while with .fill can specify 1 byte, and the number of
			# times that byte should be repeated (.fill can only take
			# base 10 numbers, no hex unfortunately)
			if flatData[i] == currentByte:
				numBytes += 1
			else:
				# Write the next instruction to the output and
				# account for the current byte being different
				OutStrs += PickInstruction(currentByte, numBytes, OutStrs[-1])
				currentByte = flatData[i]
				numBytes = 1

		# Make sure that the last byte of each file gets printed, as the
		# loop will always exit without handling the final byte
		OutStrs += PickInstruction(currentByte, numBytes, OutStrs[-1])


# Output to a bin file to be converted to an AppVar
with open("src/img/SNKSKN.bin", "w") as file:
	file.write(AppVarStr)


# DEPRICATED
# Output the eZ80 spasm instructions to be used in Snake.ez80
with open("src/img/bitMap.txt", "w") as file:
								# Format the array so that it's just the instructions. no "[]", "''", or ", "
	file.write(str(OutStrs))	#.replace("\\n", "\n").replace("', ", "").replace("'", "").replace("\\t", "\t").replace("[", "").replace("]", ""))


