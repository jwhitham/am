
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
	clock = pygame.time.Clock()

	m = maze.Maze(21, 21, 1)
	player_x = player_y = 0

	for maze_row in range(m.rows):
		for maze_column in range(m.columns):
			if m.maze_map.get((maze_column, maze_row), 0) == maze.START:
				player_x = maze_column + 0.5
				player_y = maze_row + 0.5
				break

	#for maze_row in range(2, m.rows - 2):
	#	for maze_column in range(2, m.columns - 2):
	#		m.maze_map[(maze_column, maze_row)] = maze.CONNECTED

	texture_width = m.columns
	texture_height = m.rows
	key = None

	while True:
		s.fill((0, 0, 0))
		for screen_x in range(-HALF_WIDTH, HALF_WIDTH, 1):
			#ray_angle = (screen_x * math.pi * 0.25) / HALF_WIDTH
			ray_vector_x = 1.0
			ray_vector_y = (0.99 * screen_x) / HALF_WIDTH
			viewer_x = player_x
			viewer_y = player_y

			#assert 0.70 <= ray_vector_x, (ray_angle, ray_vector_x)
			#assert abs(ray_vector_y) <= 0.71, (ray_angle, ray_vector_y)

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

					texture_x = int(math.floor(i2y * texture_width))
					texture_x %= texture_width
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
						texture_x = int(math.floor(i1x * texture_width))
						texture_x %= texture_width
					else:
						maze_y += 1
						assert maze_y == int(math.floor(viewer_y))
						texture_x = int(math.floor(i1x * texture_width))
						texture_x = texture_width - (texture_x % texture_width) - 1



				if (m.maze_map.get((maze_x, maze_y), 0) == maze.WALL):
					# reached wall
					dist = viewer_x - player_x
					height = (2 * (HALF_HEIGHT - 1)) / dist
					h = maze_x + maze_y
					h = (h % 7) + 1
					r = 255 * (h & 1)
					g = 255 * ((h & 2) / 2)
					b = 255 * ((h & 4) / 4)
					if SHOW_MAP:
						pygame.draw.line(s, (r, g, b),
							(int(viewer_x * MU) + HALF_WIDTH, int(viewer_y * MU) + HALF_HEIGHT),
							(int(player_x * MU) + HALF_WIDTH, int(player_y * MU) + HALF_HEIGHT))
					#pygame.draw.line(s, (r, g, b),
					#	(screen_x + HALF_WIDTH, HALF_HEIGHT - height),
					#	(screen_x + HALF_WIDTH, HALF_HEIGHT + height))

					maze_x = int(math.floor(player_x))
					maze_y = int(math.floor(player_y))
					save_pos = (maze_x, maze_y)
					save_val = m.maze_map[save_pos]
					m.maze_map[save_pos] = '*'

					tmp_y0 = tmp_y1 = HALF_HEIGHT - (height / 2)
					tmp_x = screen_x + HALF_WIDTH
					for texture_y in range(texture_height):
						tmp_y2 = (((texture_y + 1) * height) / texture_height) + tmp_y0
						v = m.maze_map.get((texture_x, texture_y), 0)
						if v == maze.WALL:
							h = ((texture_x + texture_y) % 9)
							r = g = b = 127 + (h * 16)
							if ((texture_x == 0) or (texture_y == 0)
							or (texture_x == (texture_width - 1))
							or (texture_y == (texture_height - 1))):
								r /= 4
								g = b = 0
						elif v == '*':
							r = g = 0
							b = 255
						else:
							r = g = b = 0
						pygame.draw.line(s, (r, g, b), (tmp_x, tmp_y1), (tmp_x, tmp_y2))
						tmp_y1 = tmp_y2

					m.maze_map[save_pos] = save_val
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
		new_player_x = player_x
		new_player_y = player_y
		e = pygame.event.poll()
		while e.type != NOEVENT:
			if e.type == QUIT:
				key = K_ESCAPE
				break
			if e.type == KEYDOWN:
				key = e.key
			if e.type == KEYUP:
				key = None
			e = pygame.event.poll()

		if key == K_LEFT:
			new_player_y -= 0.1
		if key == K_RIGHT:
			new_player_y += 0.1
		if key == K_DOWN:
			new_player_x -= 0.1
		if key == K_UP:
			new_player_x += 0.1
		if key == K_ESCAPE:
			break

		# detect collision
		collide = False
		for x in range(-1, 2, 2):
			maze_x = int(math.floor(new_player_x - (x * 0.1)))
			for y in range(-1, 2, 2):
				maze_y = int(math.floor(new_player_y + (y * 0.1)))
				if m.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
					collide = True

		if not collide:
			player_x = new_player_x
			player_y = new_player_y
			maze_x = int(math.floor(new_player_x))
			maze_y = int(math.floor(new_player_y))
			if m.maze_map.get((maze_x, maze_y), maze.WALL) == maze.FINISH:
				print ("You win!")
				break
				
		pygame.time.wait(40)

	pygame.quit()

if __name__ == "__main__":
	main()

