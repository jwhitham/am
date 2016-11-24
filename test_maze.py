
from aimee_maze import CONNECTED, START, WALL, FINISH

def test_maze(rows, columns, maze_map):
	start = None

	for y in range(rows):
		for x in range(columns):
			assert maze_map[x, y] in (CONNECTED, START, WALL, FINISH), (
				"at least one square in maze is not connected, start or wall")

			if maze_map[x, y] == START:
				assert start == None, "more than one start point in maze"
				start = (x, y)

	assert start != None, "no start point in maze"
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
			maze_map[x, y] = ':'

		return found
	
	(x, y) = start	
	recurse(x, y, 0)
	maze_map[x, y] = START
	assert ok[0] > 0, "did not reach exit"
	return ok[0]

