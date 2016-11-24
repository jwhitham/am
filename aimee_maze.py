
import random

WALL = '#'
UNCONNECTED = '.'
START = '>'
FINISH = '<'
CONNECTED = ' '

def make_maze(rows, columns, seed):
	# Input requirements
	assert rows > 3,			"must have more than 3 rows"
	assert columns > 3,			"must have more than 3 columns"
	assert (rows % 2) == 1,		"must have an odd number of rows"
	assert (columns % 2) == 1,	"must have an odd number of columns"

	# Begin creating the maze
	r = random.Random(seed)
	maze_map = dict()
	todo = []

	# Fill the maze area with walls
	for y in range(rows):
		for x in range(columns):
			maze_map[x, y] = WALL

	# Remove spaces between walls
	for y in range(2, rows - 1, 2):
		for x in range(2, columns - 1, 2):
			maze_map[x, y] = UNCONNECTED

	# Pick player start point (left side)
	y = r.randrange(2, rows - 1, 2)
	maze_map[1, y] = START
	maze_map[0, y] = CONNECTED

	# Pick player finish point (right side)
	x = columns - 2
	y = r.randrange(2, rows - 1, 2)
	maze_map[x, y] = FINISH 
	x += 1
	maze_map[x, y] = CONNECTED

	# Choose centre of the maze
	x = r.randrange(2, columns - 1, 2)
	y = r.randrange(2, rows - 1, 2)
	maze_map[x, y] = CONNECTED
	todo.append((x, y))

	# Repeatedly remove walls to make the maze
	while len(todo) > 0:
		# find some connected place within the maze
		(x, y) = todo.pop(r.randrange(0, len(todo)))

		# look at the walls around it, can any be removed?
		walls = []
		if maze_map[x - 2, y] == UNCONNECTED:
			walls.append((- 1, 0))
		if maze_map[x + 2, y] == UNCONNECTED:
			walls.append((+ 1, 0))
		if maze_map[x, y - 2] == UNCONNECTED:
			walls.append((0, - 1))
		if maze_map[x, y + 2] == UNCONNECTED:
			walls.append((0, + 1))

		if len(walls) > 1:
			# revisit (x, y) as walls remain
			todo.append((x, y))

		if len(walls) > 0:
			# pick a wall
			(dx, dy) = r.choice(walls)
			# remove that wall
			x += dx
			y += dy
			maze_map[x, y] = CONNECTED
			# connect up new space
			x += dx
			y += dy
			maze_map[x, y] = CONNECTED
			# new space joins todo list
			todo.append((x, y))

	# Maze is finished
	return maze_map

def print_maze(rows, columns, maze_map):
	for y in range(rows):
		line = ""
		for x in range(columns):
			line += maze_map[x, y]
		print (line)

