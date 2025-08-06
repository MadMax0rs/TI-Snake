import sys
from PIL import Image
import numpy as np


def RGB888To565(col888) -> list[np.uint8]:
	R: int = round((float(col888[0]) / 0b11111111) * 0b11111)
	G: int = round((float(col888[1]) / 0b11111111) * 0b111111)
	B: int = round((float(col888[2]) / 0b11111111) * 0b11111)

	num: np.uint16 = np.uint16( (R << 11) | (G << 5) | B)

	num0: np.uint8 = np.uint8(num)
	num1: np.uint8 = np.uint8(num >> 8)

	return [num0, num1]

outStrs: list[str] = []
AppVarStr: str = ""

img = Image.open("D:\\TI-84 plus CE\\Games\\MyGames\\ASM\\Snake\\src\\img\\tileset.png")
pixelData = np.asarray(img)


for x in range(0, 64, 16):
	for y in range(0, 64, 16):
		data = pixelData[x:x+16,y:y+16,0:3].reshape(-1, 3)
		flatData: list[np.uint8] = []

		for i in range(data.shape[0]):
			obj = RGB888To565(data[i])
			flatData.append(obj[0])
			flatData.append(obj[1])

		outStrs.append(f"Tile{int(y/16+x/4)}:\n")
		currentByte: np.uint8 = flatData[0]
		numBytes: int = 0

		for i in range(len(flatData)):
			AppVarStr += chr(int(flatData[i]))
			if flatData[i] == currentByte:
				numBytes += 1
			else:
				if numBytes < 2:
					outStrs[-1] += f"\t.db {currentByte}\n"
				else:
					outStrs[-1] += f"\t.fill {numBytes}, {currentByte}\n"
				currentByte = flatData[i]
				numBytes = 1

		if numBytes < 2:
			outStrs[-1] += f"\t.db {currentByte}\n"
		else:
			outStrs[-1] += f"\t.fill {numBytes}, {currentByte}\n"

		
with open("src/img/bitMap.txt", "w") as file:
	file.write(str(outStrs).replace("\\n", "\n").replace("', ", "").replace("'", "").replace("\\t", "\t").replace("[", "").replace("]", ""))


with open("src/img/SNKSKNDF.bin", "w") as file:
	file.write(AppVarStr)


