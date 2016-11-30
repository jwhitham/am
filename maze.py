
import aimee_maze
from aimee_maze import CONNECTED, START, WALL, FINISH
from PIL import Image

FLAGGED1 = ':'
FLAGGED2 = 'p'
ARROW = Image.open("images/arrow.png")

class Maze:
	def __init__(self, rows, columns, seed):
		self.rows = rows
		self.columns = columns
		self.seed = seed
		self.maze_map = aimee_maze.make_maze(rows, columns, seed)
		self.test_maze_find_start_finish()

	def print_maze(self):
		aimee_maze.print_maze(self.rows, self.columns, self.maze_map)

	def overlay(self, img, (bx1, by1, bx2, by2), border_size):
		(_, _, orig_width, orig_height) = img.getbbox()

		x1 = int(bx1 * orig_width)
		x2 = int(bx2 * orig_width)
		y1 = int(by1 * orig_height)
		y2 = int(by2 * orig_height)

		width = x2 - x1
		height = y2 - y1
		xsize = width / self.columns
		ysize = height / self.rows
		size = min(xsize, ysize)
		xsize = ysize = size
		xoff = x1 + int((width / 2) - ((xsize * self.columns) / 2))
		yoff = y1 + int((height / 2) - ((ysize * self.rows) / 2))

		white = (255, 255, 255)
		black = (0, 0, 0)
		arrow = ARROW.copy()
		arrow = arrow.resize((size, size), Image.BICUBIC)

		for y in range(self.rows):
			for x in range(self.columns):
				value = self.maze_map[x, y]
				if value == WALL:
					continue

				x0 = xoff + (x * size)
				y0 = yoff + (y * size)
				u = d = l = r = border_size

				if self.maze_map.get((x - 1, y), CONNECTED) != WALL: l = 0
				if self.maze_map.get((x + 1, y), CONNECTED) != WALL: r = 0
				if self.maze_map.get((x, y - 1), CONNECTED) != WALL: u = 0
				if self.maze_map.get((x, y + 1), CONNECTED) != WALL: d = 0

				img.paste(black, (x0, y0, x0 + size, y0 + size))
				img.paste(white, (x0 + l, y0 + u, x0 + size - r, y0 + size - d))

				if x == 0:
					img.paste(black, (0, y0, x0, y0 + size))
					img.paste(white, (0, y0 + u, x0, y0 + size - d))
				if x == self.columns - 1:
					img.paste(black, (x0, y0, orig_width, y0 + size))
					img.paste(white, (x0, y0 + u, orig_width, y0 + size - d))
				if y == 0:
					img.paste(black, (x0, 0, x0 + size, y0))
					img.paste(white, (x0 + l, 0, x0 + size - r, y0))
				if y == self.rows - 1:
					img.paste(black, (x0, y0, x0 + size, orig_height))
					img.paste(white, (x0 + l, y0, x0 + size - r, orig_height))

				if value in (START, FINISH):
					img.paste(arrow, (x0, y0, x0 + size, y0 + size), arrow)

	def test_maze_find_start_finish(self):
		# deep copy of maze map (as we modify it)
		maze_map = dict(self.maze_map.items())
		rows = self.rows
		columns = self.columns

		# check maze contents
		start = finish = None
		for y in range(rows):
			for x in range(columns):
				assert maze_map[x, y] in (CONNECTED, START, WALL, FINISH), (
					"at least one square in maze is not connected, start or wall")

				if maze_map[x, y] == START:
					assert start == None, "more than one start point in maze"
					start = (x, y)
				if maze_map[x, y] == FINISH:
					assert finish == None, "more than one finish point in maze"
					finish = (x, y)

		assert start != None, "no start point in maze"
		assert finish != None, "no finish point in maze"
		visited = set()
		ok = [-1]

		# enforce surrounding wall
		for y in range(rows):
			maze_map[0, y] = WALL
			maze_map[columns - 1, y] = WALL
		for x in range(columns):
			maze_map[x, 0] = WALL
			maze_map[x, rows - 1] = WALL

		def recurse(x, y, number_of_steps):
			if (x, y) in visited:
				# Been here before
				return False

			assert maze_map[x, y] != WALL
			visited.add((x, y))
			found = False

			if x < 2 or y < 2 or x >= (columns - 2) or y >= (rows - 2):
				# Reached the exit
				found = True
				ok[0] = number_of_steps

			number_of_steps += 1
			x -= 1
			if maze_map[x, y] != WALL:
				found = recurse(x, y, number_of_steps) or found
			x += 2
			if maze_map[x, y] != WALL:
				found = recurse(x, y, number_of_steps) or found
			x -= 1
			y -= 1
			if maze_map[x, y] != WALL:
				found = recurse(x, y, number_of_steps) or found
			y += 2
			if maze_map[x, y] != WALL:
				found = recurse(x, y, number_of_steps) or found
			y -= 1

			if found:
				maze_map[x, y] = FLAGGED2 # on the path
			else:
				maze_map[x, y] = FLAGGED1 # not on the path

			return found
		
		(x, y) = start	
		recurse(x, y, 0)
		assert ok[0] > 0, "did not reach exit"

		self.start = start
		self.finish = finish 
		self.number_of_steps = ok[0]

		self.number_of_choices = 0
		(x, y) = start
		while (x, y) != finish:
			choice = False
			assert maze_map[x, y] != CONNECTED
			assert maze_map[x, y] != WALL
			assert maze_map[x, y] != FLAGGED1
			assert maze_map[x, y] == FLAGGED2 # on path
			maze_map[x, y] = CONNECTED # visited

			if maze_map[x - 1, y] == FLAGGED1: choice = True
			elif maze_map[x + 1, y] == FLAGGED1: choice = True
			elif maze_map[x, y - 1] == FLAGGED1: choice = True
			elif maze_map[x, y + 1] == FLAGGED1: choice = True

			if maze_map[x - 1, y] == FLAGGED2: x -= 1
			elif maze_map[x + 1, y] == FLAGGED2: x += 1
			elif maze_map[x, y - 1] == FLAGGED2: y -= 1
			elif maze_map[x, y + 1] == FLAGGED2: y += 1

			if choice:
				self.number_of_choices += 1

