
import aimee_maze
from aimee_maze import CONNECTED, START, WALL, FINISH
from PIL import Image

FLAGGED = ':'
PAGE_409_TABLE = {
	# Box drawing characters
	"wasd" : [250, 250, 250, 250],
	"wasD" : [196, 205, 205, 196],
	"waSd" : [179, 186, 179, 186],
	"waSD" : [218, 201, 213, 214],
	"wAsd" : [196, 205, 205, 196],
	"wAsD" : [196, 205, 205, 196],
	"wASd" : [191, 187, 184, 183],
	"wASD" : [194, 203, 209, 210],
	"Wasd" : [179, 186, 179, 186],
	"WasD" : [192, 200, 212, 211],
	"WaSd" : [179, 186, 179, 186],
	"WaSD" : [195, 204, 198, 199],
	"WAsd" : [217, 188, 190, 189],
	"WAsD" : [193, 202, 207, 208],
	"WASd" : [180, 185, 181, 182],
	"WASD" : [197, 206, 216, 215],
}

class Maze:
	def __init__(self, rows, columns, seed):
		self.rows = rows
		self.columns = columns
		self.seed = seed
		self.maze_map = aimee_maze.make_maze(rows, columns, seed)
		self.test_maze_find_start_finish()

		# no surrounding wall
		self.substitute_3x3(self.start, WALL, FLAGGED)
		self.substitute_3x3(self.finish, WALL, FLAGGED)

		for y in range(rows):
			self.substitute_1x1((0, y), WALL, CONNECTED)
			self.substitute_1x1((columns - 1, y), WALL, CONNECTED)

		for x in range(columns):
			self.substitute_1x1((x, 0), WALL, CONNECTED)
			self.substitute_1x1((x, rows - 1), WALL, CONNECTED)

		self.substitute_3x3(self.start, FLAGGED, WALL)
		self.substitute_3x3(self.finish, FLAGGED, WALL)

	def box_drawing(self, number):
		assert 0 <= number <= 3
		maze_map = dict()
		rows = self.rows
		columns = self.columns
		for y in range(rows):
			for x in range(columns):
				if self.maze_map[x, y] == WALL:
					key = ["w", "a", "s", "d"]
					if self.maze_map.get((x - 1, y), WALL) == WALL: key[1] = "A"
					if self.maze_map.get((x + 1, y), WALL) == WALL: key[3] = "D"
					if self.maze_map.get((x, y - 1), WALL) == WALL: key[0] = "W"
					if self.maze_map.get((x, y + 1), WALL) == WALL: key[2] = "S"
					key = ''.join(key)

					maze_map[x, y] = chr(PAGE_409_TABLE[key][number])
				else:
					maze_map[x, y] = self.maze_map[x, y]
	
		self.maze_map = maze_map

	def block_drawing(self, value):
		value = chr(value)
		rows = self.rows
		columns = self.columns
		for y in range(rows):
			for x in range(columns):
				if self.maze_map[x, y] == WALL:
					self.maze_map[x, y] = value

	def print_maze(self):
		aimee_maze.print_maze(self.rows, self.columns, self.maze_map)

	def to_img(self, flip):
		char_width = 8
		char_height = 8

		maze_map = self.maze_map
		rows = self.rows
		columns = self.columns
		img = Image.new("1", (char_width * columns, char_height * rows), 1)
		font_data = open("cp437-8x8", "rb").read()

		for y in range(rows):
			for x in range(columns):
				value = maze_map[x, y]
				inv = 0xff
				if value in (START, FINISH):
					value = chr(26)
				elif value == CONNECTED:
					pass
				elif flip:
					inv = 0x00

				offset = ord(value) * char_height
				y0 = y * char_height

				for y1 in range(8):
					font = ord(font_data[offset]) ^ inv
					x0 = x * char_width
					for x1 in range(8):
						if (font & 128) == 0:
							img.putpixel((x0, y0), 0)
						x0 += 1
						font = font << 1
					y0 += 1
					offset += 1

		return img

	def substitute_1x1(self, xy, before, after):
		if self.maze_map[xy] == before:
			self.maze_map[xy] = after

	def substitute_3x3(self, (x, y), before, after):
		for y1 in range(y - 1, y + 2, 1):
			for x1 in range(x - 1, x + 2, 1):
				self.substitute_1x1((x1, y1), before, after)

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
				maze_map[x, y] = '%d' % (number_of_steps % 10)
			else:
				maze_map[x, y] = FLAGGED

			return found
		
		(x, y) = start	
		recurse(x, y, 0)
		maze_map[x, y] = START
		assert ok[0] > 0, "did not reach exit"

		self.start = start
		self.finish = finish 
		self.number_of_steps = ok[0]

