
from maze import Maze
import subprocess

m = None
page_number = 0
fd = None

def output(inv):
	global m, fd, page_number

	page_number += 1
	m.to_img(inv).save("page%u.png" % page_number)
	width = 1.0 * m.columns
	if width > 18.0:
		width = 18.0

	fd.write("\n")
	fd.write(r"\includegraphics[width=%1.1fcm]{page%u.png}" % (width, page_number))
	fd.write(r"\newline")
	fd.write(r"~~")
	fd.write(r"\newline")
	fd.write(r"~~")
	fd.write(r"\vspace{1cm}")
	fd.write(r"%u rows and %u columns (seed = %u)" % (m.rows, m.columns, m.seed))
	fd.write(r"\newpage")

def main():
	global m, fd, page_number
	fd = open("book.tex", "wt")
	fd.write(r"""
\documentclass[11pt,a4paper]{book}
\usepackage[pdftex,dvips]{graphicx}
\usepackage{times} 
\begin{document}
\begin{center}
""")
	book()
	fd.write(r"""
\end{center}
\end{document}
""")
	fd.close()
	rc = subprocess.call(["pdflatex", "book.tex"])
	assert rc == 0


def book():
	global m, fd, page_number

	# intro mazes
	m = Maze(11, 11, 900)
	m.block_drawing(0xdb)
	output(0)

	m = Maze(11, 13, 901)
	m.block_drawing(0x01)
	output(0)

	m = Maze(13, 11, 902)
	m.block_drawing(0xf9)
	output(1)
	return

	m = Maze(11, 13, 903)
	m.block_drawing(0x07)
	output(1)

	m = Maze(13, 13, 904)
	m.block_drawing(0x23)
	output(1)

	# small mazes	
	m = Maze(15, 15, 1000)
	m.block_drawing(0xb0)
	output(0)

	m = Maze(19, 15, 1001)
	m.block_drawing(0xb1)
	output(0)

	m = Maze(17, 15, 1002)
	m.block_drawing(0xf9)
	output(1)

	m = Maze(21, 15, 1003)
	m.block_drawing(0x03)
	output(1)

	m = Maze(17, 15, 1004)
	m.block_drawing(0x07)
	output(1)

	# bigger mazes	
	m = Maze(29, 29, 1100)
	m.box_drawing(0)
	output(0)

	m = Maze(29, 29, 1101)
	m.box_drawing(1)
	output(0)

	m = Maze(29, 29, 1102)
	m.box_drawing(2)
	output(0)

	m = Maze(29, 29, 1103)
	m.box_drawing(3)
	output(0)

	m = Maze(29, 29, 1104)
	m.block_drawing(0x2f)
	output(1)

	# bigger again
	m = Maze(43, 33, 1200)
	m.block_drawing(0xb0)
	output(0)

	m = Maze(43, 33, 1201)
	m.block_drawing(0xb1)
	output(0)

	m = Maze(43, 33, 1202)
	m.block_drawing(0xb2)
	output(0)

	m = Maze(43, 33, 1203)
	m.block_drawing(0xdb)
	output(0)

	m = Maze(43, 33, 1204)
	m.block_drawing(0xec)
	output(1)

	# huge mazes
	m = Maze(63, 43, 1300)
	m.box_drawing(3)
	output(0)

	m = Maze(63, 43, 1301)
	m.box_drawing(2)
	output(0)

	m = Maze(63, 43, 1302)
	m.box_drawing(1)
	output(0)

	m = Maze(63, 43, 1303)
	m.box_drawing(0)
	output(0)

	m = Maze(63, 43, 1304)
	m.block_drawing(0x09)
	output(1)

	# final mega mazes
	m = Maze(121, 91, 1401)
	m.box_drawing(1)
	output(0)

	m = Maze(121, 91, 1402)
	m.box_drawing(2)
	output(0)

	m = Maze(121, 91, 1403)
	m.box_drawing(3)
	output(0)

	m = Maze(121, 91, 1404)
	m.box_drawing(2)
	output(0)

	m = Maze(121, 91, 1405)
	m.box_drawing(1)
	output(0)


if __name__ == "__main__":
	main()

