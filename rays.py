
import pygame
from pygame.locals import *
import math
import maze
HALF_WIDTH = 320
HALF_HEIGHT = 240
MU = 24
SHOW_MAP = False

def main():
	pygame.init()
	s = pygame.display.set_mode((HALF_WIDTH * 2, HALF_HEIGHT * 2))

	m = maze.Maze(21, 21, 1)
	player_x = player_y = 0

	for maze_row in range(m.rows):
		for maze_column in range(m.columns):
			if m.maze_map.get((maze_column, maze_row), 0) == maze.START:
				player_x = maze_column + 0.5
				player_y = maze_row + 0.5
				break

	while True:
		s.fill((0, 0, 0))
		for screen_x in range(-HALF_WIDTH, HALF_WIDTH, 1):
			ray_angle = (screen_x * math.pi * 0.25) / HALF_WIDTH
			ray_vector_x = math.cos(ray_angle)
			ray_vector_y = math.sin(ray_angle)
			viewer_x = player_x
			viewer_y = player_y

			assert 0.70 <= ray_vector_x, (ray_angle, ray_vector_x)
			assert abs(ray_vector_y) <= 0.71, (ray_angle, ray_vector_y)

			maze_x = int(math.floor(viewer_x))
			maze_y = int(math.floor(viewer_y))

			while (maze_x < m.columns) and (abs(maze_y) < m.columns):
				sub_x = viewer_x - maze_x
				sub_y = viewer_y - maze_y
				assert 0 <= sub_x <= 1.0
				assert 0 <= sub_y <= 1.0

				# find first intersection with horizontal line
				i1x = i1y = None
				if ray_vector_y < 0.0:
					# above (left hand side)
					i1x = viewer_x + ((ray_vector_x * sub_y) / (- ray_vector_y))
					i1y = maze_y + 0.0
				elif ray_vector_y > 0.0:
					# below (right hand side)
					i1x = viewer_x + ((ray_vector_x * (1.0 - sub_y)) / (ray_vector_y))
					i1y = maze_y + 1.0
			
				# find first intersection with vertical line
				i2x = maze_x + 1.0
				i2y = viewer_y + (((1.0 - sub_x) * ray_vector_y) / ray_vector_x)

				if (i1x == None) or (i2x < i1x):
					# crosses vertical line first
					maze_x += 1
					viewer_x = i2x
					viewer_y = i2y
					assert maze_x == int(math.floor(viewer_x))
					assert maze_y == int(math.floor(viewer_y))
				else:
					# crosses horizontal line first
					if i2x == i1x:
						# special case: crosses both lines at once
						assert i2y == i1y
						maze_x += 1

					viewer_x = i1x
					viewer_y = i1y
					assert maze_x == int(math.floor(viewer_x)), (maze_x, viewer_x)
					if ray_vector_y < 0.0:
						assert maze_y == int(math.floor(viewer_y))
						maze_y -= 1
					else:
						maze_y += 1
						assert maze_y == int(math.floor(viewer_y))


				if (m.maze_map.get((maze_x, maze_y), 0) == maze.WALL):
					# reached wall
					dist = viewer_x - player_x
					height = min(HALF_HEIGHT - 1, (HALF_HEIGHT - 1) / dist)
					h = maze_x + maze_y
					h = (h % 7) + 1
					r = 255 * (h & 1)
					g = 255 * ((h & 2) / 2)
					b = 255 * ((h & 4) / 4)
					if SHOW_MAP:
						pygame.draw.line(s, (r, g, b),
							(int(viewer_x * MU) + HALF_WIDTH, int(viewer_y * MU) + HALF_HEIGHT),
							(int(player_x * MU) + HALF_WIDTH, int(player_y * MU) + HALF_HEIGHT))
					pygame.draw.line(s, (r, g, b),
						(screen_x + HALF_WIDTH, HALF_HEIGHT - height),
						(screen_x + HALF_WIDTH, HALF_HEIGHT + height))
					break

		if SHOW_MAP:
			for x in range(m.columns):
				pygame.draw.line(s, (255, 255, 255),
					(int(x * MU) + HALF_WIDTH, 0),
					(int(x * MU) + HALF_WIDTH, HALF_HEIGHT * 2))
			for y in range(m.rows):
				pygame.draw.line(s, (255, 255, 255),
					(0, int(y * MU) + HALF_HEIGHT),
					(HALF_WIDTH * 2, int(y * MU) + HALF_HEIGHT))
			for y in range(m.rows):
				for x in range(m.columns):
					if (m.maze_map.get((x, y), 0) == maze.WALL):
						pygame.draw.rect(s, (100, 100, 100),
							(int(x * MU) + HALF_WIDTH, int(y * MU) + HALF_HEIGHT, MU, MU))


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

