
import aimee_maze, test_maze

rows = 31
columns = 31
max_score = -1
best_seed = 1
for seed in range(1, 100):
	maze_map = aimee_maze.make_maze(rows, columns, seed)
	score = test_maze.test_maze(rows, columns, maze_map)
	if score > max_score:
		max_score = score
		best_seed = seed

seed = best_seed
maze_map = aimee_maze.make_maze(rows, columns, seed)
aimee_maze.print_maze(rows, columns, maze_map)
score = test_maze.test_maze(rows, columns, maze_map)
print (score, seed)
