# 3D maze, ray casting prototype
# Use arrow keys to navigate to the exit

import pygame
from pygame.locals import *
import math
import maze
HALF_WIDTH = 320
HALF_HEIGHT = 240
FIXED_POINT = 256
X_OFFSET = FIXED_POINT * 3
MU = 24
SHOW_MAP = False

def main():
	pygame.init()
	s = pygame.display.set_mode((HALF_WIDTH * 2, HALF_HEIGHT * 2))
	clock = pygame.time.Clock()

	# generate maze
	original_maze = maze.Maze(15, 15, 2)
	player_x = player_y = 0

	for maze_row in range(original_maze.rows):
		for maze_column in range(original_maze.columns):
			if original_maze.maze_map.get((maze_column, maze_row), 0) == maze.START:
				player_x = (maze_column * FIXED_POINT) + (FIXED_POINT / 2)
				player_y = (maze_row * FIXED_POINT) + (FIXED_POINT / 2)
				break

	#for maze_row in range(2, original_maze.rows - 2):
	#	for maze_column in range(2, original_maze.columns - 2):
	#		original_maze.maze_map[(maze_column, maze_row)] = maze.CONNECTED

	texture_width = original_maze.columns
	texture_height = original_maze.rows
	key = None
	player_x -= X_OFFSET

	while True:
		s.fill((0, 0, 0))

		line_x = (player_x + X_OFFSET) / FIXED_POINT

		# vector along the line that the player faces
		camera_vector_x = FIXED_POINT
		camera_vector_y = 0

		# normal to the camera vector (projection plane for view)
		plane_vector_x = -camera_vector_y
		plane_vector_y = camera_vector_x

		for screen_x in range(-HALF_WIDTH, HALF_WIDTH, 1):

			# vector for this screen X (the ray being cast)
			ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH)
			ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH)
			viewer_x = player_x
			viewer_y = player_y

			#assert 0.70 <= ray_vector_x, (ray_angle, ray_vector_x)
			#assert abs(ray_vector_y) <= 0.71, (ray_angle, ray_vector_y)

			maze_x = viewer_x / FIXED_POINT
			maze_y = viewer_y / FIXED_POINT
			previous_is_space = True
			previous_y = (HALF_HEIGHT * 2) - 1
			previous_colour = (64, 64, 64)

			while (maze_x < original_maze.columns) and (0 <= maze_y < original_maze.rows):
				sub_x = viewer_x - (maze_x * FIXED_POINT)
				sub_y = viewer_y - (maze_y * FIXED_POINT)
				assert 0 <= sub_x <= FIXED_POINT
				assert 0 <= sub_y <= FIXED_POINT

				# find first intersection with horizontal line
				i1x = i1y = None
				if ray_vector_y < 0:
					# above (left hand side)
					i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)))
					i1y = maze_y * FIXED_POINT
				elif ray_vector_y > 0:
					# below (right hand side)
					i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)))
					i1y = (maze_y + 1) * FIXED_POINT
			
				# find first intersection with vertical line
				i2x = i2y = None
				if ray_vector_x > 0:
					i2x = (maze_x + 1) * FIXED_POINT
					i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x))

				if (i1x == None) or ((i2x < i1x) and (i2x != None)):
					# crosses vertical line first
					maze_x += 1
					viewer_x = i2x
					viewer_y = i2y
					assert maze_x == (viewer_x / FIXED_POINT)

					texture_x = (i2y * texture_width) / FIXED_POINT
					texture_x %= texture_width
				else:
					# crosses horizontal line first
					if i2x == i1x:
						# special case: crosses both lines at once
						i2y = i1y
						assert i2y == i1y
						maze_x += 1

					viewer_x = i1x
					viewer_y = i1y
					assert maze_x == (viewer_x / FIXED_POINT)
					if ray_vector_y < 0:
						assert maze_y == (viewer_y / FIXED_POINT)
						maze_y -= 1
						texture_x = (i1x * texture_width) / FIXED_POINT
						texture_x %= texture_width
					else:
						maze_y += 1
						assert maze_y == (viewer_y / FIXED_POINT)
						texture_x = (i1x * texture_width) / FIXED_POINT
						texture_x = texture_width - (texture_x % texture_width) - 1



				height = ((2 * FIXED_POINT * (HALF_HEIGHT - 1)) / (viewer_x - player_x))

				h = maze_x + maze_y
				h = (h % 7) + 1
				r = 255 * (h & 1)
				g = 255 * ((h & 2) / 2)
				b = 255 * ((h & 4) / 4)
				if SHOW_MAP:
					pygame.draw.line(s, (r, g, b),
						((int(viewer_x * MU) / FIXED_POINT), (int(viewer_y * MU) / FIXED_POINT)),
						((int(player_x * MU) / FIXED_POINT), (int(player_y * MU) / FIXED_POINT)))

				next_is_space = not (original_maze.maze_map.get((maze_x, maze_y), 0) == maze.WALL)

				tmp_x = screen_x + HALF_WIDTH
				blank = (0, 0, 0)
				if abs(screen_x) <= 2:
					blank = (255, 255, 0)

				dist = viewer_x - player_x
				if dist > 0:
					base_y = height
					top_y = base_y - (height / 4)
				else:
					base_y = previous_y
					top_y = previous_y

				if previous_is_space:
					if next_is_space:
						# all blank
						pass
					else:
						# draw to base of wall (blank)
						if previous_y > base_y:
							pygame.draw.line(s, blank, (tmp_x, previous_y), (tmp_x, base_y))
							previous_y = base_y
						# draw wall
						if previous_y > top_y:
							pygame.draw.line(s, (r / 2, g / 2, b / 2), (tmp_x, previous_y), (tmp_x, top_y))
							previous_y = top_y
				else:
					# draw top of previous wall
					if previous_y > top_y:
						pygame.draw.line(s, previous_colour, (tmp_x, previous_y), (tmp_x, top_y))
						previous_y = top_y

				previous_colour = (r, g, b)
				previous_is_space = next_is_space

				if abs(screen_x) <= 2:
					if maze_x >= line_x:
						pygame.draw.line(s, blank, (tmp_x, previous_y), (tmp_x, 0))
						break

		if SHOW_MAP:
			for x in range(original_maze.columns):
				pygame.draw.line(s, (255, 255, 255),
					(int(x * MU), 0),
					(int(x * MU), HALF_HEIGHT * 2))
			for y in range(original_maze.rows):
				pygame.draw.line(s, (255, 255, 255),
					(0, int(y * MU)),
					(HALF_WIDTH * 2, int(y * MU)))
			for y in range(original_maze.rows):
				for x in range(original_maze.columns):
					if (original_maze.maze_map.get((x, y), 0) == maze.WALL):
						pygame.draw.rect(s, (100, 100, 100),
							(int(x * MU), int(y * MU), MU, MU))


		pygame.display.flip()
		new_player_x = player_x
		new_player_y = player_y

		e = pygame.event.poll()
		while e.type != NOEVENT:
			if e.type == QUIT:
				key = K_ESCAPE
			if e.type == KEYDOWN:
				key = e.key
			if e.type == KEYUP:
				key = None
			e = pygame.event.poll()

		if key == K_LEFT:
			new_player_y -= FIXED_POINT / 10
		if key == K_RIGHT:
			new_player_y += FIXED_POINT / 10
		if key == K_DOWN:
			new_player_x -= FIXED_POINT / 10
		if key == K_UP:
			new_player_x += FIXED_POINT / 10
		if key == K_ESCAPE:
			break

		# detect collision
		maze_y = new_player_y / FIXED_POINT
		maze_x = (new_player_x + X_OFFSET - (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_x = player_x
		maze_x = (new_player_x + X_OFFSET + (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_x = player_x

		maze_x = (new_player_x + X_OFFSET) / FIXED_POINT
		maze_y = (new_player_y - (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_y = player_y
		maze_y = (new_player_y + (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_y = player_y

		player_x = new_player_x
		player_y = new_player_y
		maze_x = player_x / FIXED_POINT
		maze_y = player_y / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.FINISH:
			print ("You win!")
			break
				
		pygame.time.wait(40)

	pygame.quit()

if __name__ == "__main__":
	main()

