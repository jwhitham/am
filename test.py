
from maze import Maze

if __name__ == "__main__":
	m = Maze(31, 31, 1)
	m.print_maze()
	m.block_drawing(0xfa)
	i = m.to_img(1)
	i.save("test.bmp")

