
import pygame
from pygame.locals import *

import maze
HALF_WIDTH = 320
HALF_HEIGHT = 240

def translator(wx, wy, wz):
	sx = sy = 0
	if wx <= 0:
		# behind camera
		return None
	if wy > wx:
		# off RHS
		return None
	if wy < -wx:
		# off LHS
		return None

	sx = ((wy * (HALF_WIDTH - 1)) / wx) + HALF_WIDTH - 1
	sy = ((wz * (HALF_HEIGHT - 1)) / wx) + HALF_HEIGHT - 1
	#assert 0 <= sx < (HALF_WIDTH * 2), (sx, wx, wy)
	#assert 0 <= sy < (HALF_HEIGHT * 2), (sy, wx, wy)
	return (sx, sy)


def main():
	pygame.init()
	s = pygame.display.set_mode((HALF_WIDTH * 2, HALF_HEIGHT * 2))

	m = maze.Maze(21, 21, 1)
	player_x = player_y = 0

	for maze_row in range(m.rows):
		for maze_column in range(m.columns):
			if m.maze_map.get((maze_column, maze_row), 0) == maze.START:
				player_x = maze_column
				player_y = maze_row
				break

	while True:
		s.fill((0, 0, 0))
		for maze_row in range(m.rows):
			for maze_column in range(m.columns - 1, 0, -1):
				wx = ((maze_column - player_x) * 2) + 1
				wy = ((maze_row - player_y) * 2) - 1
				if m.maze_map.get((maze_column, maze_row), 0) == maze.WALL:
					for i in range(2):
						r = [translator(wx, wy, 1),
							translator(wx + 2, wy, 1),
							translator(wx + 2, wy, -1),
							translator(wx, wy, -1)]
						if not (None in r):
							pygame.draw.polygon(s, (255, 255, 255), r)
						wy += 2

					wy -= 4

					r = [translator(wx, wy, 1),
						translator(wx, wy + 2, 1),
						translator(wx, wy + 2, -1),
						translator(wx, wy, -1)]
					if not (None in r):
						pygame.draw.polygon(s, (255, 255, 255), r)
			
		pygame.display.flip()
		e = pygame.event.wait()
		if e.type == KEYDOWN:
			if e.key == K_LEFT:
				player_y -= 1
			if e.key == K_RIGHT:
				player_y += 1
			if e.key == K_DOWN:
				player_x -= 1
			if e.key == K_UP:
				player_x += 1
			if e.key == K_ESCAPE:
				break
		if e.type == QUIT:
			break

	pygame.quit()

if __name__ == "__main__":
	main()

