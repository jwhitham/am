
from maze import Maze
import subprocess
from PIL import Image

m = None
page_number = 0
fd = None

def output(background, rows = 21, columns = 41, cropping = (0.0, 0.0, 1.0, 1.0), maze_box = (0.0, 0.5, 1.0, 1.0), seed = None):
	global m, fd, page_number

	page_number += 1

	if seed == None:
		seed = page_number

	img = Image.open(background)
	(_, _, orig_width, orig_height) = img.getbbox()

	(bx1, by1, bx2, by2) = cropping
	x1 = int(bx1 * orig_width)
	y1 = int(by1 * orig_height)
	x2 = int(bx2 * orig_width)
	y2 = int(by2 * orig_height)
	img = img.crop((x1, y1, x2, y2))

	m = Maze(rows, columns, seed)
	m.overlay(img, maze_box)
	img.save("page%u.png" % page_number)

	(_, _, width, height) = img.getbbox()
	img_ratio = float(width) / height
	paper_width = (29.7 - 2.0 - 2.0) 
	paper_height = (21.0 - 2.0 - 4.0 - 1.0)
	paper_ratio = paper_width / paper_height
	if img_ratio > paper_ratio:
		# img is too wide, white bars will appear at bottom and top
		size = r"width=%1.2fcm" % paper_width
	else:
		# img is too tall, white bars will appear at bottom and top
		size = r"height=%1.2fcm" % paper_height

	fd.write("\n")
	fd.write(r"\centering\includegraphics[%s]{page%u.png}" % (size, page_number))
	fd.write(r"\newline\vspace{0.2cm}")
	fd.write(r"{\tt\small\centering make\_maze(rows = %u, columns = %u, seed = %u)}" % (m.rows, m.columns, m.seed))
	fd.write(r"\newpage")

def main():
	global m, fd, page_number
	fd = open("book.tex", "wt")
	fd.write(r"""
\documentclass[12pt]{book}
\usepackage[pdftex,dvips]{graphicx}
\usepackage{times} 
\usepackage[paperwidth=29.7cm,paperheight=21cm,inner=2.0cm,outer=2.0cm,top=4.0cm,bottom=2.0cm]{geometry}
\begin{document}
\begin{center}
\pagenumbering{roman}
\pagestyle{empty}
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

	output("Ja7TP76P.jpeg")
	return

	# intro mazes
	m = Maze(15, 31, 802)
	output(0)
	return

	m = Maze(11, 13, 901)
	m.block_drawing(0x01)
	output(0)

	m = Maze(13, 11, 902)
	m.block_drawing(0xf9)
	output(1)

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

