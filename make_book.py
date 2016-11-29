
from maze import Maze
import subprocess, os
from PIL import Image

m = None
page_number = 0
fd = None

def output(background, rows = 21, columns = 41, crop = (0.0, 0.0, 1.0, 1.0),
				border_size = 1, maze_box = (0.0, 0.0, 1.0, 1.0), seed = None,
				portrait = False):
	global m, fd, page_number

	page_number += 1

	if seed == None:
		seed = page_number

	print ("page %u image %s: load" % (page_number, background))
	img = Image.open("images/" + background)

	(_, _, orig_width, orig_height) = img.getbbox()

	(bx1, by1, bx2, by2) = crop
	x1 = int(bx1 * orig_width)
	y1 = int(by1 * orig_height)
	x2 = int(bx2 * orig_width)
	y2 = int(by2 * orig_height)
	print ("crop")
	img = img.crop((x1, y1, x2, y2))

	print ("make maze")
	m = Maze(rows, columns, seed)

	print ("print maze")
	m.overlay(img, maze_box, border_size)

	if portrait:
		print ("rotate")
		img = img.rotate(270)

	print ("save image")
	img.save("output/page%u.png" % page_number)

	(_, _, width, height) = img.getbbox()
	img_ratio = float(width) / height
	paper_width = (29.7 - 1.0 - 1.0)
	paper_height = (21.0 - 1.0 - 3.0 - 1.0)
	paper_ratio = paper_width / paper_height
	if img_ratio > paper_ratio:
		# img is too wide, white bars will appear at bottom and top
		size = r"width=%1.2fcm" % paper_width
	else:
		# img is too tall, white bars will appear at bottom and top
		size = r"height=%1.2fcm" % paper_height

	fd.write("\n")
	fd.write(r"\begin{figure}[p]\centering\includegraphics[%s]{page%u.png}" % (size, page_number))
	fd.write(r"\caption{make\_maze(rows = %u, columns = %u, seed = %u)}" % (m.rows, m.columns, m.seed))
	fd.write(r"\end{figure}")

def main():
	global m, fd, page_number
	fd = open("output/book.tex", "wt")
	fd.write(r"""
\documentclass[12pt]{book}
\usepackage[pdftex,dvips]{graphicx}
\usepackage{times} 
\usepackage{color} 
\usepackage{morefloats} 
\usepackage[paperwidth=29.7cm,paperheight=21cm,inner=1.0cm,outer=1.0cm,top=3.0cm,bottom=1.0cm]{geometry}
\usepackage[labelformat=empty]{caption}
\begin{document}
\pagestyle{empty}
\pagenumbering{gobble}
\title{Book of Mazes}
\maketitle
""")
	book()
	fd.write(r"""
\end{document}
""")
	fd.close()
	os.chdir("output")
	rc = subprocess.call(["pdflatex", "book.tex"])
	assert rc == 0


# 62266-frozen-elsa-and-anna-on-mountains.jpg
# 91686-frozen-elsa.jpg
# bestmoviewalls_Frozen_16_2560x1600.jpg
# Disney_Frozen_Concept_Art_01.jpg
# disney-frozen_elsa-wide.jpg
# frozen1.jpg
# frozen_2013_movie-wide.jpg
# Frozen-Elsa.jpg
# frozen_elsa_snow_queen_palace-wide.jpg
# frozen-fever-1.jpg
# frozen-fever-poster.jpg
# Frozen-frozen-34532690-1600-900.jpg
# Frozen-image-frozen-36065993-2560-1600.jpg
# frozen.jpg
# Frozen-Movie-Winter_Arendelle-HD-Wallpaper1.jpg
# Frozen-Wallpaper-olaf-and-sven-37883401-2880-1800.jpg
# Ja7TP76P.jpeg
# Kristoff-and-Sven-in-Frozen-Movie-HD-Wallpapers.jpg

def book():
	output("91686-frozen-elsa.jpg", rows = 21, columns = 21, maze_box = (0.0, 0.4, 1.0, 1.0), crop = (0.3, 0.0, 0.7, 1.0), portrait = True)
	output("62266-frozen-elsa-and-anna-on-mountains.jpg")
	output("Kristoff-and-Sven-in-Frozen-Movie-HD-Wallpapers.jpg", maze_box = (0.0, 0.0, 0.5, 1.0), columns = 31, rows = 31)
	output("Ja7TP76P.jpeg", columns = 31, rows = 31, crop = (0.2, 0.0, 0.8, 1.0), portrait = True, maze_box = (0.0, 0.4, 1.0, 1.0))
	output("Frozen-Wallpaper-olaf-and-sven-37883401-2880-1800.jpg", maze_box = (0.0, 0.35, 1.0, 1.0), columns = 121, rows = 41)
	output("Frozen-Movie-Winter_Arendelle-HD-Wallpaper1.jpg")
	output("frozen.jpg", maze_box = (0.0, 0.3, 1.0, 1.0))
	output("Frozen-image-frozen-36065993-2560-1600.jpg")
	output("Frozen-frozen-34532690-1600-900.jpg", rows = 31, columns = 51, maze_box = (0.0, 0.0, 1.0, 0.5), crop = (0.35, 0.0, 1.0, 1.0))
	output("Disney_Frozen_Concept_Art_01.jpg", rows = 31, columns = 71, maze_box = (0.0, 0.0, 1.0, 0.8), crop = (0.1, 0.0, 0.9, 1.0))
	output("frozen-fever-poster.jpg", crop = (0.0, 0.25, 1.0, 0.9), rows = 31, columns = 51, maze_box = (0.0, 0.3, 1.0, 1.0))
	output("91686-frozen-elsa.jpg", rows = 21, columns = 21, maze_box = (0.0, 0.0, 0.5, 1.0), crop = (0.0, 0.0, 0.9, 1.0))
	output("frozen-fever-1.jpg", crop = (0.2, 0.0, 1.0, 1.0), rows = 51, columns = 51, maze_box = (0.5, 0.0, 1.0, 1.0))
	output("frozen_elsa_snow_queen_palace-wide.jpg", rows = 31, columns = 71, maze_box = (0.0, 0.0, 1.0, 0.7))
	output("Frozen-Elsa.jpg", rows = 41, columns = 41, maze_box = (0.0, 0.4, 1.0, 1.0), portrait = True)
	output("frozen_2013_movie-wide.jpg", rows = 31, columns = 71, maze_box = (0.1, 0.4, 1.0, 1.0))
	output("frozen1.jpg", rows = 51, columns = 51, maze_box = (0.0, 0.0, 0.7, 1.0))
	output("disney-frozen_elsa-wide.jpg", rows = 31, columns = 61, maze_box = (0.0, 0.4, 1.0, 1.0), crop = (0.2, 0.0, 1.0, 1.0))
	output("bestmoviewalls_Frozen_16_2560x1600.jpg", rows = 41, columns = 61)



if __name__ == "__main__":
	main()

