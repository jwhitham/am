
from maze import Maze

if __name__ == "__main__":
	m = Maze(11, 11, 1)
	m.print_maze()
	i = m.to_img()
	i.save("test.bmp")

