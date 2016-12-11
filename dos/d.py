
ROWS = 27
COLUMNS = 41

fd = open("d.bin", "wb")
for y in range(ROWS):
	for x in range(COLUMNS):
		if x <= 1:
			fd.write("X")
		elif y <= 1:
			fd.write("Y")
		elif x >= (COLUMNS - 2):
			fd.write("x")
		elif y >= (ROWS - 2):
			fd.write("y")
		else:
			fd.write(".")
fd.close()

